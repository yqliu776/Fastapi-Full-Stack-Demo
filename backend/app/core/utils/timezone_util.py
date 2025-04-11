from datetime import datetime, timezone, timedelta

from app.core.settings import settings

class TimeZoneUtil:
    """
    时区工具类，支持可配置时区的时间操作
    """
    
    # 预设时区
    CHINA_TIMEZONE = timezone(timedelta(hours=8), 'Asia/Shanghai')
    UTC_TIMEZONE = timezone.utc
    
    def __init__(self, use_china_timezone=True):
        """
        初始化时区工具
        
        Args:
            default_timezone: 默认时区，如果为None则使用中国时区
        """
        if use_china_timezone:
            self.default_timezone = self.CHINA_TIMEZONE
        else:
            self.default_timezone = self.UTC_TIMEZONE
    
    def get_now(self):
        """
        获取当前时间（使用默认时区）
        
        Returns:
            datetime: 当前时间
        """
        return datetime.now(self.default_timezone)
    
    def convert_timezone(self, dt, target_timezone=None):
        """
        转换时间到目标时区
        
        Args:
            dt: 原始datetime对象
            target_timezone: 目标时区，如果为None则使用默认时区
            
        Returns:
            datetime: 转换后的datetime对象
        """
        if target_timezone is None:
            target_timezone = self.default_timezone
            
        # 确保源时间有时区信息
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=self.default_timezone)
            
        return dt.astimezone(target_timezone)

    @staticmethod
    def format_time(dt, format_str="%Y-%m-%d %H:%M:%S"):
        """
        格式化时间为字符串
        
        Args:
            dt: 需要格式化的datetime对象
            format_str: 格式化字符串，默认为'%Y-%m-%d %H:%M:%S'
            
        Returns:
            str: 格式化后的时间字符串
        """
        return dt.strftime(format_str)
    
    def parse_time(self, time_str, format_str="%Y-%m-%d %H:%M:%S", set_timezone=True):
        """
        解析时间字符串为datetime对象
        
        Args:
            time_str: 时间字符串
            format_str: 格式化字符串，默认为'%Y-%m-%d %H:%M:%S'
            set_timezone: 是否设置时区信息，默认为True
            
        Returns:
            datetime: 解析后的datetime对象
        """
        dt = datetime.strptime(time_str, format_str)
        if set_timezone:
            dt = dt.replace(tzinfo=self.default_timezone)
        return dt
    
    def time_diff(self, dt1, dt2):
        """
        计算两个时间的差值
        
        Args:
            dt1: 第一个datetime对象
            dt2: 第二个datetime对象
            
        Returns:
            timedelta: 时间差对象
        """
        # 确保时区一致
        dt1 = self.ensure_timezone(dt1)
        dt2 = self.ensure_timezone(dt2)
        
        if dt1.tzinfo != dt2.tzinfo:
            dt2 = dt2.astimezone(dt1.tzinfo)
            
        return dt1 - dt2
    
    def ensure_timezone(self, dt):
        """
        确保datetime对象有时区信息
        
        Args:
            dt: datetime对象
            
        Returns:
            datetime: 带有时区信息的datetime对象
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.default_timezone)
        return dt
    
    # 工厂方法创建常用时区实例
    @classmethod
    def china_timezone(cls):
        """
        创建中国时区工具实例
        
        Returns:
            TimeZoneUtil: 中国时区工具实例
        """
        return cls.CHINA_TIMEZONE
    
    @classmethod
    def utc_timezone(cls):
        """
        创建UTC时区工具实例
        
        Returns:
            TimeZoneUtil: UTC时区工具实例
        """
        return cls.UTC_TIMEZONE
    

tzu = TimeZoneUtil(settings.USE_CHINA_TIMEZONE)
