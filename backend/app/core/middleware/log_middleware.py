from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import iterate_in_threadpool
from fastapi import Request, Response
from time import time
import json

class LoggingMiddleware(BaseHTTPMiddleware):
    """FastAPI 日志中间件，用于记录请求和响应的详细信息。

    该中间件可以记录请求的方法、路径、查询参数、客户端IP、请求头信息，
    以及响应的状态码、响应体和处理时间等信息。支持格式化和非格式化的日志输出。

    Attributes:
        logger_manager: 日志管理器实例
        formatted_output (bool): 是否使用格式化的 JSON 输出
        exclude_paths (list): 不需要记录日志的路径列表
    """

    def __init__(self, app, logger_manager, formatted_output=True):
        """初始化日志中间件。

        Args:
            app: FastAPI 应用实例
            logger_manager: LogTool 日志工具实例
            formatted_output (bool, optional): 是否使用格式化的 JSON 输出。默认为 True。
        """
        super().__init__(app)
        self.logger_manager = logger_manager
        self.logger = logger_manager.get_logger()
        self.formatted_output = formatted_output
        # 定义不需要记录日志的路径
        self.exclude_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico"
        ]

    def should_log(self, path: str) -> bool:
        """判断给定路径是否需要记录日志。

        Args:
            path (str): 请求路径

        Returns:
            bool: 如果需要记录日志返回 True，否则返回 False
        """
        return not any(path.startswith(exclude) for exclude in self.exclude_paths)

    async def dispatch(self, request: Request, call_next):
        """处理请求并记录日志的主要方法。

        Args:
            request (Request): FastAPI 请求对象
            call_next: 处理下一个中间件的可调用对象

        Returns:
            响应对象

        Raises:
            Exception: 当请求处理过程中发生错误时抛出异常
        """
        # 检查是否需要记录日志
        if not self.should_log(request.url.path):
            return await call_next(request)

        start_time = time()

        # 构建结构化日志
        log_data = {
            "request": {
                "method": request.method,
                "path": request.url.path,
                # 只有当查询参数存在时才记录
                "query_params": dict(request.query_params) if request.query_params else None,
                "client_ip": request.client.host,
                # 精简请求头信息，只保留关键头部并精简内容
                "headers": self._get_simplified_headers(dict(request.headers))
            }
        }

        try:
            response = await call_next(request)

            # 获取响应内容
            response_body = [section async for section in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))

            try:
                body = json.loads(response_body[0].decode()) if response_body else None
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = "<non-JSON response>"

            log_data["response"] = body

            if self.formatted_output:
                log_message = f"Request completed\n{json.dumps(log_data, indent=2, ensure_ascii=False)}"
            else:
                log_message = (f"Request completed - Method: {request.method}, Path: {request.url.path}, "
                             f"Time: {time() - start_time:.2f}s")

            self.logger.info(log_message)

            return response

        except Exception as e:
            log_data["error"] = str(e)
            if self.formatted_output:
                error_message = f"Request failed\n{json.dumps(log_data, indent=2, ensure_ascii=False)}"
            else:
                error_message = (f"Request failed - Method: {request.method}, Path: {request.url.path}, "
                               f"Error: {str(e)}")
                
            self.logger.error(error_message)
            raise

    @staticmethod
    def _get_simplified_headers(headers):
        """精简请求头信息，只保留关键头部并缩短内容。

        Args:
            headers (dict): 原始请求头字典

        Returns:
            dict: 精简后的请求头字典
        """
        simplified_headers = {}
        important_headers = ["user-agent", "content-type", "accept", "referer", "origin"]
        
        for k, v in headers.items():
            k_lower = k.lower()
            if k_lower in important_headers:
                # 精简User-Agent，只保留浏览器/系统信息
                if k_lower == "user-agent" and len(v) > 30:
                    # 提取主要浏览器和操作系统信息
                    if "Mozilla" in v and "(" in v and ")" in v:
                        platform_part = v[v.find("("): v.find(")") + 1]
                        browser_part = v.split(" ")[-1] if " " in v else v
                        simplified_headers[k] = f"{browser_part} {platform_part}"
                    else:
                        simplified_headers[k] = v[:30] + "..." if len(v) > 30 else v
                else:
                    # 对其他头部，如果过长则截断
                    simplified_headers[k] = v[:50] + "..." if len(v) > 50 else v
        
        return simplified_headers

