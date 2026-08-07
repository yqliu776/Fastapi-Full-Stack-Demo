import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.middleware.bot_detection_middleware import BotDetectionMiddleware


class _DummyApp:
    pass


@pytest.fixture(scope="module")
def middleware():
    return BotDetectionMiddleware(_DummyApp())


class TestHoneypotTrap:
    """L-04: 蜜罐路径精确匹配，避免误伤正常路径"""

    def test_exact_trap_paths_trigger(self, middleware):
        for path in ["/admin.php", "/wp-admin", "/.env", "/phpmyadmin", "/.git"]:
            assert middleware.check_honeypot_trap(path) is True, f"应触发: {path}"

    def test_dev_paths_no_longer_trap(self, middleware):
        """/test、/dev、/staging、/api/private 已被移除，不应误伤"""
        for path in ["/test", "/dev", "/staging", "/api/private", "/old"]:
            assert middleware.check_honeypot_trap(path) is False, f"不应触发: {path}"

    def test_substring_not_triggered(self, middleware):
        """路径包含陷阱子串但并非精确匹配时不应触发（修复 startswith/子串误伤）"""
        assert middleware.check_honeypot_trap("/test/admin.php") is False
        assert middleware.check_honeypot_trap("/api/private/backup") is False
        assert middleware.check_honeypot_trap("/static/.env.example") is False


class TestAnalyzePatterns:
    """H-07: 行为模式分析纯函数"""

    def test_benign_requests_not_flagged(self, middleware):
        current_time = 1000.0
        # 两个间隔 5 秒的请求，无任何可疑特征
        timestamps = [995.0, 1000.0]
        result = middleware.analyze_patterns(timestamps, current_time)
        assert result["is_automated"] is False
        assert result["score"] == 0

    def test_regular_fast_requests_flagged(self, middleware):
        current_time = 1000.0
        # 20 个间隔恒为 50ms 的请求，全部落在最近 1 秒内
        timestamps = [current_time - i * 0.05 for i in range(19, -1, -1)]
        result = middleware.analyze_patterns(timestamps, current_time)
        assert result["is_automated"] is True
        assert result["score"] >= 10
        assert result["recent_second_requests"] == 20

    def test_single_request_returns_zero_score(self, middleware):
        current_time = 1000.0
        result = middleware.analyze_patterns([1000.0], current_time)
        assert result["is_automated"] is False
        assert result["score"] == 0
