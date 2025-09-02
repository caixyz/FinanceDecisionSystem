"""
日志管理模块
"""
import os
from loguru import logger
from pathlib import Path
try:
    from utils.config import config
except ImportError:
    from .config import config

class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.setup_logger()
    
    def setup_logger(self):
        """设置日志配置"""
        # 移除默认的控制台处理器
        logger.remove()
        
        # 获取日志配置
        log_level = config.get('LOGGING.level', 'INFO')
        log_format = config.get('LOGGING.format', 
            "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}")
        rotation = config.get('LOGGING.rotation', "1 day")
        retention = config.get('LOGGING.retention', "30 days")
        
        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 添加控制台处理器
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=log_level,
            format=log_format,
            colorize=True
        )
        
        # 添加文件处理器 - 所有日志
        logger.add(
            sink=log_dir / "app.log",
            level=log_level,
            format=log_format,
            rotation=rotation,
            retention=retention,
            encoding="utf-8"
        )
        
        # 添加文件处理器 - 错误日志
        logger.add(
            sink=log_dir / "error.log",
            level="ERROR",
            format=log_format,
            rotation=rotation,
            retention=retention,
            encoding="utf-8"
        )
        
        # 添加文件处理器 - 数据获取日志
        logger.add(
            sink=log_dir / "data_fetch.log",
            level="INFO",
            format=log_format,
            rotation=rotation,
            retention=retention,
            encoding="utf-8",
            filter=lambda record: "data_fetch" in record["extra"]
        )

# 初始化日志管理器
log_manager = LogManager()

# 导出日志器
__all__ = ['logger']