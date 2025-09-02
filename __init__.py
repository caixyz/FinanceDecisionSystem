"""
金融决策系统
基于 AKShare 的股票数据分析和策略回测系统
"""

__version__ = "1.0.0"
__author__ = "Finance Decision System"

from .core.data_source import DataSource
from .core.analyzer import TechnicalAnalyzer
from .core.backtest import BacktestEngine

__all__ = [
    "DataSource",
    "TechnicalAnalyzer", 
    "BacktestEngine"
]