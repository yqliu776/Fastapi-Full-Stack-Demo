import os
import time
import shutil
import schedule
import threading
import datetime
from loguru import logger
from app.core.utils.timezone_util import tzu


class LogUtil:
    """
    日志管理工具类，实现单例模式的日志管理系统。
    
    该类负责管理应用程序的日志记录，包括：
    - 日志文件的创建和配置
    - 按日期组织日志文件
    - 自动归档历史日志
    - 提供统一的日志记录接口
    
    Attributes:
        project_root (str): 项目根目录的绝对路径
        _instance (LogUtil): 单例实例
        _initialized (bool): 初始化标志
        archive_thread (threading.Thread): 归档任务线程
        _should_stop (bool): 控制归档线程停止的标志
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        初始化 LogTool 实例
        """
        # 确保只初始化一次
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._should_stop = False
        self.archive_thread = None
        
        # 获取项目根目录
        current_file_path = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))
        
        # 初始化日志目录相关属性
        self.base_log_dir = os.path.join(self.project_root, 'logs')
        self.current_date = time.strftime("%Y-%m-%d")
        self.daily_log_dir = os.path.join(self.base_log_dir, self.current_date)
        self.archive_dir = os.path.join(self.base_log_dir, 'archives')
        self.log_handler_id = None
        
        # 初始化日志记录器
        self.setup_logger()

    def setup_logger(self, rotation_size="1 MB", retention="1 day"):
        """
        配置日志记录器的核心方法。
        
        Args:
            rotation_size (str): 日志文件轮转大小，默认为1MB
            retention (str): 日志保留期，默认为1天
        
        配置内容包括：
        - 创建日志目录结构
        - 设置日志格式和轮转策略
        - 配置日志保留策略
        """
        # 当天日志目录
        self.current_date = time.strftime("%Y-%m-%d")
        self.daily_log_dir = os.path.join(self.base_log_dir, self.current_date)

        # 创建所需目录
        for dir_path in [self.daily_log_dir, self.archive_dir]:
            os.makedirs(dir_path, exist_ok=True)

        # 添加日志处理
        self.log_handler_id = logger.add(
            os.path.join(self.daily_log_dir, "{time:HH-mm-ss}.log"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
            rotation=rotation_size,
            retention=retention,
            compression=None,
            encoding="utf-8"
        )

        # 添加归档任务
        self.setup_archive_task()

    def setup_archive_task(self):
        """
        设置日志归档任务，实现日志文件的自动归档功能。
            
        功能：
        - 在每天00:00自动执行归档
        - 将前一天的日志文件压缩为zip格式
        - 删除原始日志文件
        - 使用守护线程执行归档任务
        """
        # 停止现有的归档线程（如果有）
        self.stop_archive_thread()
        
        # 设置每天0点执行归档
        schedule.clear()
        schedule.every().day.at("00:00").do(self.archive_logs)

        # 启动调度任务
        self._should_stop = False
        self.archive_thread = threading.Thread(target=self.run_schedule, daemon=True)
        self.archive_thread.start()

    def run_schedule(self):
        """运行调度任务的线程函数"""
        while not self._should_stop:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def stop_archive_thread(self):
        """停止归档线程"""
        if self.archive_thread and self.archive_thread.is_alive():
            self._should_stop = True
            self.archive_thread.join(timeout=3)  # 等待线程安全退出，最多3秒

    def archive_logs(self, target_date=None):
        """
        归档指定日期的日志。
        
        Args:
            target_date (str, optional): 要归档的日期，格式为YYYY-MM-DD。
                                        如果不指定，默认归档前一天的日志。
        
        Returns:
            bool: 归档操作是否成功
        """
        try:
            # 如果未指定日期，使用前一天的日期
            if target_date is None:
                yesterday = tzu.get_now() - datetime.timedelta(days=1)
                target_date = yesterday.strftime("%Y-%m-%d")
            
            target_log_dir = os.path.join(self.base_log_dir, target_date)
            
            # 确保目标日志目录存在
            if not os.path.exists(target_log_dir):
                logger.warning(f"归档目标目录不存在: {target_log_dir}")
                return False
                
            # 确保目录中有文件需要归档
            if not os.listdir(target_log_dir):
                logger.warning(f"归档目标目录为空: {target_log_dir}")
                return False
            
            # 创建归档文件
            archive_name = f"{target_date}.zip"
            archive_path = os.path.join(self.archive_dir, archive_name)
            
            # 执行归档
            logger.info(f"开始归档 {target_date} 的日志...")
            shutil.make_archive(
                os.path.splitext(archive_path)[0],  # 不包含扩展名的路径
                'zip',
                target_log_dir
            )
            
            # 检查归档是否成功
            if os.path.exists(archive_path):
                logger.info(f"成功创建归档文件: {archive_path}")
                
                # 删除原始日志目录
                shutil.rmtree(target_log_dir)
                logger.info(f"已删除原始日志目录: {target_log_dir}")
                return True
            else:
                logger.error(f"归档文件创建失败: {archive_path}")
                return False
                
        except Exception as e:
            logger.exception(f"日志归档过程出错: {str(e)}")
            return False

    def reset_logger(self, rotation_size="1 MB", retention="1 day"):
        """
        重置日志记录器，更新配置参数。
        
        Args:
            rotation_size (str): 新的日志文件轮转大小
            retention (str): 新的日志保留期
            
        当需要更改日志配置时使用此方法。
        """
        # 移除现有的处理器
        if hasattr(self, 'log_handler_id'):
            logger.remove(self.log_handler_id)
            
        # 重新设置日志记录器
        self.setup_logger(rotation_size, retention)
        logger.info(f"已重置日志记录器，轮转大小: {rotation_size}, 保留期: {retention}")

    @staticmethod
    def get_logger():
        """
        获取日志记录器实例。
        
        Returns:
            logger: loguru.logger实例，用于记录日志的统一接口
        """
        return logger
    
    def __del__(self):
        """
        析构函数，确保在对象销毁时停止归档线程
        """
        self.stop_archive_thread()

# 实例化日志管理器
logger_manager = LogUtil()
