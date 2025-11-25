from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re
import hashlib
import time
from collections import defaultdict, deque

from app.core.models import ResponseModel
from app.core.utils import logger
from app.core.settings import settings


class BotDetectionMiddleware(BaseHTTPMiddleware):
    """机器人检测中间件 - 用于检测和阻止爬虫行为"""

    def __init__(self, app):
        """初始化机器人检测中间件"""
        super().__init__(app)

        # 可疑的用户代理模式
        self.suspicious_user_agents = [
            r'bot', r'crawler', r'spider', r'scraper', r'curl', r'wget',
            r'python-requests', r'httpclient', r'java/', r'libwww',
            r'phantomjs', r'selenium', r'headless', r'webdriver',
            r'bingbot', r'googlebot', r'slurp', r'duckduckbot',
            r'baiduspider', r'yandexbot', r'facebookexternalhit'
        ]

        # 合法的用户代理模式（用于反向验证）
        self.legitimate_user_agents = [
            r'chrome', r'firefox', r'safari', r'opera', r'edge',
            r'mobile', r'android', r'iphone', r'ipad'
        ]

        # 请求指纹存储 - 用于检测自动化行为
        self.request_fingerprints = defaultdict(lambda: {
            'timestamps': deque(maxlen=100),
            'patterns': defaultdict(int),
            'suspicious_score': 0
        })

        # 配置参数
        self.config = {
            'max_requests_per_minute': settings.BOT_DETECTION_MAX_REQUESTS_PER_MINUTE,
            'max_requests_per_second': settings.BOT_DETECTION_MAX_REQUESTS_PER_SECOND,
            'min_interval_ms': settings.BOT_DETECTION_MIN_INTERVAL_MS,
            'suspicious_score_threshold': settings.BOT_DETECTION_SUSPICIOUS_SCORE_THRESHOLD,
            'block_duration_seconds': settings.BOT_DETECTION_BLOCK_DURATION,
            'enable_captcha_challenge': settings.BOT_DETECTION_ENABLE_CAPTCHA,
            'honeypot_detection': settings.BOT_DETECTION_ENABLE_HONEYPOT
        }

        # 蜜罐陷阱路径
        self.honeypot_paths = [
            '/admin.php', '/wp-admin', '/config.php', '/.env',
            '/phpmyadmin', '/mysql', '/backup', '/old',
            '/test', '/dev', '/staging', '/api/private',
            '/_debug', '/__debug__', '/.git', '/.svn'
        ]

    def get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        if request.client:
            return request.client.host

        return "unknown"

    def generate_request_fingerprint(self, request: Request) -> str:
        """生成请求指纹"""
        user_agent = request.headers.get("User-Agent", "")
        accept = request.headers.get("Accept", "")
        accept_language = request.headers.get("Accept-Language", "")
        accept_encoding = request.headers.get("Accept-Encoding", "")

        # 创建指纹字符串
        fingerprint_data = f"{user_agent}|{accept}|{accept_language}|{accept_encoding}"

        # 使用MD5生成指纹哈希
        return hashlib.md5(fingerprint_data.encode()).hexdigest()

    def analyze_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """分析用户代理字符串"""
        user_agent_lower = user_agent.lower()

        # 检测可疑的用户代理
        suspicious_matches = []
        for pattern in self.suspicious_user_agents:
            if re.search(pattern, user_agent_lower):
                suspicious_matches.append(pattern)

        # 检测合法的用户代理
        legitimate_matches = []
        for pattern in self.legitimate_user_agents:
            if re.search(pattern, user_agent_lower):
                legitimate_matches.append(pattern)

        # 计算可疑度分数
        suspicious_score = len(suspicious_matches) * 2
        legitimate_score = len(legitimate_matches)

        # 空用户代理或异常短的用户代理
        if not user_agent or len(user_agent) < 10:
            suspicious_score += 3

        return {
            "is_suspicious": suspicious_score > legitimate_score,
            "suspicious_score": suspicious_score,
            "legitimate_score": legitimate_score,
            "suspicious_patterns": suspicious_matches,
            "legitimate_patterns": legitimate_matches,
            "user_agent_length": len(user_agent)
        }

    def detect_automated_behavior(self, client_ip: str, fingerprint: str, current_time: float) -> Dict[str, Any]:
        """检测自动化行为模式"""
        fingerprint_data = self.request_fingerprints[f"{client_ip}:{fingerprint}"]

        # 添加当前时间戳
        fingerprint_data['timestamps'].append(current_time)

        # 分析请求模式
        timestamps = fingerprint_data['timestamps']

        if len(timestamps) < 2:
            return {"is_automated": False, "score": 0}

        # 计算请求间隔
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]) * 1000  # 转换为毫秒
            intervals.append(interval)

        # 检测异常模式
        suspicious_patterns = 0

        # 1. 检测过于规律的请求间隔（机器人特征）
        if len(intervals) >= 3:
            interval_variance = sum(abs(intervals[i] - intervals[i-1]) for i in range(1, len(intervals))) / len(intervals)
            if interval_variance < 50:  # 间隔变化小于50ms，非常可疑
                suspicious_patterns += 3

        # 2. 检测过快的请求（小于最小间隔）
        fast_requests = sum(1 for interval in intervals if interval < self.config['min_interval_ms'])
        if fast_requests > 0:
            suspicious_patterns += min(fast_requests, 5)

        # 3. 检测突发大量请求
        recent_requests = sum(1 for ts in timestamps if current_time - ts < 60)  # 最近1分钟
        if recent_requests > self.config['max_requests_per_minute']:
            suspicious_patterns += 5

        # 4. 检测每秒过多请求
        recent_second_requests = sum(1 for ts in timestamps if current_time - ts < 1)  # 最近1秒
        if recent_second_requests > self.config['max_requests_per_second']:
            suspicious_patterns += 3

        fingerprint_data['suspicious_score'] = suspicious_patterns

        return {
            "is_automated": suspicious_patterns >= self.config['suspicious_score_threshold'],
            "score": suspicious_patterns,
            "intervals": intervals[-5:],  # 返回最近5个间隔
            "recent_requests": recent_requests,
            "recent_second_requests": recent_second_requests
        }

    def check_honeypot_trap(self, path: str) -> bool:
        """检查是否触发了蜜罐陷阱"""
        for honeypot_path in self.honeypot_paths:
            if path.startswith(honeypot_path) or honeypot_path in path:
                return True
        return False

    def should_challenge_with_captcha(self, detection_results: Dict[str, Any]) -> bool:
        """判断是否需要进行验证码挑战"""
        total_score = (
            detection_results.get("user_agent_analysis", {}).get("suspicious_score", 0) +
            detection_results.get("behavior_analysis", {}).get("score", 0)
        )

        return (
            self.config['enable_captcha_challenge'] and
            total_score >= self.config['suspicious_score_threshold']
        )

    async def dispatch(self, request: Request, call_next):
        """处理机器人检测逻辑"""

        # 如果全局禁用机器人检测，直接通过
        if not settings.BOT_DETECTION_ENABLED:
            return await call_next(request)

        # 排除静态资源和API文档路径
        exclude_paths = ['/docs', '/redoc', '/openapi.json', '/favicon.ico', '/static']
        if any(request.url.path.startswith(path) for path in exclude_paths):
            return await call_next(request)

        client_ip = self.get_client_ip(request)
        current_time = time.time()
        path = request.url.path
        user_agent = request.headers.get("User-Agent", "")

        # 生成请求指纹
        fingerprint = self.generate_request_fingerprint(request)

        detection_results = {
            "client_ip": client_ip,
            "path": path,
            "user_agent": user_agent,
            "fingerprint": fingerprint
        }

        try:
            # 1. 用户代理分析
            user_agent_analysis = self.analyze_user_agent(user_agent)
            detection_results["user_agent_analysis"] = user_agent_analysis

            # 2. 行为模式分析
            behavior_analysis = self.detect_automated_behavior(client_ip, fingerprint, current_time)
            detection_results["behavior_analysis"] = behavior_analysis

            # 3. 蜜罐陷阱检测
            honeypot_triggered = self.check_honeypot_trap(path)
            detection_results["honeypot_triggered"] = honeypot_triggered

            # 综合判断
            is_suspicious = (
                user_agent_analysis["is_suspicious"] or
                behavior_analysis["is_automated"] or
                honeypot_triggered
            )

            detection_results["is_suspicious"] = is_suspicious
            detection_results["total_score"] = (
                user_agent_analysis["suspicious_score"] +
                behavior_analysis["score"]
            )

            # 记录可疑行为
            if is_suspicious:
                logger.warning(f"检测到可疑请求: {detection_results}")

            # 如果触发了蜜罐陷阱，直接封禁
            if honeypot_triggered:
                logger.warning(f"蜜罐陷阱被触发: IP={client_ip}, Path={path}")
                response = ResponseModel(
                    code=403,
                    message="访问被拒绝",
                    data={"reason": "suspicious_access", "blocked": True}
                )
                return JSONResponse(
                    status_code=403,
                    content=response.model_dump(),
                    headers={"X-Bot-Detected": "true", "X-Block-Reason": "honeypot"}
                )

            # 如果行为高度可疑，进行验证码挑战或封禁
            if behavior_analysis["is_automated"] and behavior_analysis["score"] >= self.config['suspicious_score_threshold'] + 5:
                logger.warning(f"自动化行为检测: IP={client_ip}, Score={behavior_analysis['score']}")

                if self.should_challenge_with_captcha(detection_results):
                    # 返回验证码挑战响应
                    response = ResponseModel(
                        code=429,
                        message="请完成验证码验证",
                        data={
                            "challenge_type": "captcha",
                            "reason": "suspicious_behavior",
                            "score": behavior_analysis["score"]
                        }
                    )
                    return JSONResponse(
                        status_code=429,
                        content=response.model_dump(),
                        headers={"X-Bot-Detected": "true", "X-Challenge-Required": "captcha"}
                    )

            # 继续处理请求
            response = await call_next(request)

            # 添加检测信息到响应头（调试用）
            if settings.DEBUG:
                response.headers["X-Bot-Score"] = str(detection_results["total_score"])
                response.headers["X-Bot-Suspicious"] = str(is_suspicious).lower()

            return response

        except Exception as e:
            logger.error(f"机器人检测中间件处理失败: {str(e)}")
            # 出现异常时允许请求通过，避免服务不可用
            return await call_next(request)