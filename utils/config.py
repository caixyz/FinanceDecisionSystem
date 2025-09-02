"""
配置管理模块
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config.yml"
        
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'DATABASE': {
                'type': 'sqlite',
                'path': 'data/finance_data.db'
            },
            'DATA_SOURCE': {
                'primary': 'akshare',
                'update_interval': 300,
                'retry_times': 3,
                'timeout': 30
            },
            'LOGGING': {
                'level': 'INFO'
            }
        }
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.get('DATABASE', {})
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """获取数据源配置"""
        return self.get('DATA_SOURCE', {})
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web服务配置"""
        return self.get('WEB', {})

# 全局配置实例
config = Config()