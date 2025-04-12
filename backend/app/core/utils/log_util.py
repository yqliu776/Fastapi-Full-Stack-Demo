from loguru import logger
import threading
import schedule
import datetime
import shutil
import time
import os

from .timezone_util import tzu


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
        _archive_lock (threading.Lock): 归档操作的互斥锁
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        初始化 LogUtil 实例
        """
        # 确保只初始化一次
        self.schedule_initialized = None
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self._should_stop = False
        self.archive_thread = None
        # 添加归档锁，防止重复归档
        self._archive_lock = threading.Lock()
        # 归档日期记录，避免重复归档同一天的日志
        self._archived_dates = set()
        
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

    def setup_logger(self, rotation_size="100 MB", retention="1 day"):
        """
        配置日志记录器的核心方法。
        
        Args:
            rotation_size (str): 日志文件轮转大小，默认为100MB
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
            os.path.join(self.daily_log_dir, "{time:HH-mm}.log"),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
            rotation=rotation_size,
            retention=retention,
            compression=None,
            encoding="utf-8"
        )

        # 添加归档任务 - 仅在初始化时设置一次
        if not hasattr(self, 'schedule_initialized') or not self.schedule_initialized:
            self.setup_archive_task()
            self.schedule_initialized = True

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
        # 将归档任务调整为每天00:01执行
        schedule.every().day.at("00:01").do(self._prepare_for_new_day_logs)

        # 启动调度任务
        self._should_stop = False
        self.archive_thread = threading.Thread(target=self.run_schedule, daemon=True)
        self.archive_thread.start()

    def _prepare_for_new_day_logs(self):
        """
        准备新一天的日志记录，并归档前一天的日志。
        
        此方法确保在处理旧日志前先设置好新日志文件，避免文件占用冲突。
        """
        try:
            # 获取当前日期和昨天日期
            now = tzu.get_now()
            yesterday = now - datetime.timedelta(days=1)
            today_date = now.strftime("%Y-%m-%d")
            yesterday_date = yesterday.strftime("%Y-%m-%d")
            
            # 如果今天的日期与当前记录的日期相同，说明日志已经更新过
            # 这是为了防止一天内多次调用此方法
            if today_date == self.current_date and os.path.exists(os.path.join(self.daily_log_dir, "app.log")):
                logger.debug(f"当前日志已经是最新日期 {today_date}，跳过日志处理器更新")
                
                # 仍然检查是否需要归档昨天的日志
                if yesterday_date not in self._archived_dates and self.archive_logs(yesterday_date):
                    logger.info(f"成功归档 {yesterday_date} 的日志")
                return True
            
            logger.info(f"开始准备 {today_date} 的日志文件")
            
            # 1. 先移除旧的日志处理器
            if self.log_handler_id is not None:
                logger.remove(self.log_handler_id)
                
            # 2. 确保使用新的日期
            self.current_date = today_date
            self.daily_log_dir = os.path.join(self.base_log_dir, self.current_date)
            
            # 3. 确保新日期的目录存在
            os.makedirs(self.daily_log_dir, exist_ok=True)
            
            # 4. 重新添加日志处理器，指向新的日期目录
            self.log_handler_id = logger.add(
                os.path.join(self.daily_log_dir, "{time:HH-mm}.log"),
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
                rotation="100 MB",
                retention="1 day",
                compression=None,
                encoding="utf-8"
            )
            
            logger.info("已创建新的日志文件并更新日志处理器")
            
            # 5. 在创建新日志处理器后，归档昨天的日志(如果尚未归档)
            if yesterday_date not in self._archived_dates and self.archive_logs(yesterday_date):
                logger.info(f"成功归档 {yesterday_date} 的日志")
            
            return True
        except Exception as e:
            logger.exception(f"准备新日志时发生错误: {str(e)}")
            return False

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
        # 使用锁确保同一时间只有一个线程执行归档
        if not self._archive_lock.acquire(blocking=False):
            logger.info(f"另一个归档操作正在进行中，跳过对 {target_date} 的归档")
            return False
            
        try:
            # 如果未指定日期，使用前一天的日期
            if target_date is None:
                yesterday = tzu.get_now() - datetime.timedelta(days=1)
                target_date = yesterday.strftime("%Y-%m-%d")
                
            # 检查是否已经归档过这个日期
            if target_date in self._archived_dates:
                logger.info(f"日期 {target_date} 的日志已归档，跳过")
                return False
                
            # 检查归档文件是否已存在
            archive_name = f"{target_date}.zip"
            archive_path = os.path.join(self.archive_dir, archive_name)
            if os.path.exists(archive_path):
                logger.info(f"归档文件已存在: {archive_path}，标记为已归档")
                self._archived_dates.add(target_date)
                return True
            
            target_log_dir = os.path.join(self.base_log_dir, target_date)
            
            # 确保目标日志目录存在
            if not os.path.exists(target_log_dir):
                logger.warning(f"归档目标目录不存在: {target_log_dir}")
                # 即使目录不存在也标记为已尝试归档
                self._archived_dates.add(target_date)
                return False
                
            # 确保目录中有文件需要归档
            if not os.listdir(target_log_dir):
                logger.warning(f"归档目标目录为空: {target_log_dir}")
                # 即使目录为空也标记为已尝试归档
                self._archived_dates.add(target_date)
                return False
            
            # 创建归档文件
            logger.info(f"开始归档 {target_date} 的日志...")
            shutil.make_archive(
                os.path.splitext(archive_path)[0],  # 不包含扩展名的路径
                'zip',
                target_log_dir
            )
            
            # 检查归档是否成功
            if os.path.exists(archive_path):
                logger.info(f"成功创建归档文件: {archive_path}")
                
                # 删除原始日志目录，使用安全的方式
                self._safe_remove_directory(target_log_dir)
                
                # 记录已归档的日期
                self._archived_dates.add(target_date)
                return True
            else:
                logger.error(f"归档文件创建失败: {archive_path}")
                return False
                
        except Exception as e:
            logger.exception(f"日志归档过程出错: {str(e)}")
            return False
        finally:
            # 释放锁，允许其他归档操作进行
            self._archive_lock.release()

    @staticmethod
    def _safe_remove_directory(directory_path, max_retries=3, retry_delay=2):
        """
        安全地删除目录，处理文件占用的情况。
        
        Args:
            directory_path (str): 要删除的目录路径
            max_retries (int): 最大重试次数
            retry_delay (int): 重试间隔（秒）
            
        Returns:
            bool: 删除操作是否完全成功
        """
        files_not_removed = []
        
        # 尝试删除每个文件
        for root, dirs, files in os.walk(directory_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                removed = False
                
                # 尝试删除文件，有多次重试机会
                for attempt in range(max_retries):
                    try:
                        os.unlink(file_path)
                        removed = True
                        break
                    except PermissionError as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"文件占用，无法删除: {file_path}，将在 {retry_delay} 秒后重试...")
                            time.sleep(retry_delay)
                        else:
                            logger.warning(f"文件占用，跳过删除: {file_path}")
                            files_not_removed.append(file_path)
                    except Exception as e:
                        logger.error(f"删除文件时发生错误: {file_path}, 错误: {str(e)}")
                        files_not_removed.append(file_path)
                        break
            
            # 删除空目录
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if os.path.exists(dir_path) and not os.listdir(dir_path):
                        os.rmdir(dir_path)
                except Exception as e:
                    logger.error(f"删除目录时发生错误: {dir_path}, 错误: {str(e)}")
        
        # 最后尝试删除主目录
        try:
            if os.path.exists(directory_path) and not os.listdir(directory_path):
                os.rmdir(directory_path)
                logger.info(f"已删除原始日志目录: {directory_path}")
            elif files_not_removed:
                logger.warning(f"无法完全删除目录 {directory_path}，{len(files_not_removed)} 个文件被跳过")
        except Exception as e:
            logger.error(f"删除主目录时发生错误: {directory_path}, 错误: {str(e)}")
        
        return len(files_not_removed) == 0

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
