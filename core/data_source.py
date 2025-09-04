"""
数据获取模块
基于 AKShare 封装的统一数据接口
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
try:
    from utils.logger import logger
    from utils.config import config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.logger import logger
    from utils.config import config
import time
import functools

class DataFetcher:
    """数据获取器基类"""
    
    def __init__(self):
        self.config = config.get_data_source_config()
        self.retry_times = self.config.get('retry_times', 3)
        self.timeout = self.config.get('timeout', 30)
    
    def _retry_request(self, func, *args, **kwargs):
        """重试请求"""
        last_exception = None
        for attempt in range(self.retry_times):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_times - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"第 {attempt + 1} 次尝试失败: {e}，{wait_time}秒后重试")
                    time.sleep(wait_time)
                else:
                    logger.error(f"所有重试失败: {e}")
        
        raise last_exception


class StockDataFetcher(DataFetcher):
    """股票数据获取器"""
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        def _get_data():
            logger.bind(data_fetch=True).info("开始获取A股股票列表")
            df = ak.stock_zh_a_spot_em()
            logger.bind(data_fetch=True).info(f"成功获取 {len(df)} 只股票信息")
            return df
        
        return self._retry_request(_get_data)
    
    def get_stock_hist(self, 
                      symbol: str, 
                      period: str = "daily",
                      start_date: str = None,
                      end_date: str = None,
                      adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史数据
        
        Args:
            symbol: 股票代码 (如: 000001)
            period: 周期 (daily, weekly, monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq前复权, hfq后复权, 空字符串不复权)
        """
        def _get_data():
            logger.bind(data_fetch=True).info(f"开始获取股票 {symbol} 的 {period} 历史数据")
            
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            # 标准化列名 - 处理中文列名
            if not df.empty:
                # AKShare返回的标准列名（中文）
                column_mapping = {
                    '日期': 'date',
                    '股票代码': 'symbol',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'turnover',
                    '振幅': 'amplitude',
                    '涨跌幅': 'change_pct',
                    '涨跌额': 'change_amount',
                    '换手率': 'turnover_rate'
                }
                
                # 重命名列
                df = df.rename(columns=column_mapping)
                logger.debug(f"列名映射后: {list(df.columns)}")
                
                # 移除不需要的列（如股票代码列）
                if 'symbol' in df.columns:
                    df = df.drop('symbol', axis=1)
                
                # 确保必要的列存在
                required_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    logger.error(f"缺少必要的列: {missing_cols}")
                    return pd.DataFrame()
                
                # 数据类型转换
                numeric_columns = ['open', 'close', 'high', 'low', 'volume', 'turnover', 
                                 'amplitude', 'change_pct', 'change_amount', 'turnover_rate']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # 日期处理
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.bind(data_fetch=True).info(f"成功获取股票 {symbol} 历史数据，共 {len(df)} 条记录")
            return df
        
        return self._retry_request(_get_data)
    
    def get_stock_realtime(self) -> pd.DataFrame:
        """获取股票实时数据"""
        def _get_data():
            logger.bind(data_fetch=True).info("开始获取股票实时数据")
            df = ak.stock_zh_a_spot_em()
            logger.bind(data_fetch=True).info(f"成功获取实时数据，共 {len(df)} 只股票")
            return df
        
        return self._retry_request(_get_data)
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        def _get_data():
            logger.bind(data_fetch=True).info(f"开始获取股票 {symbol} 基本信息")
            
            # 获取股票基本信息
            info = ak.stock_individual_info_em(symbol=symbol)
            
            result = {}
            if not info.empty:
                for _, row in info.iterrows():
                    result[row['item']] = row['value']
            
            logger.bind(data_fetch=True).info(f"成功获取股票 {symbol} 基本信息")
            return result
        
        return self._retry_request(_get_data)
    
    def get_industry_list(self) -> pd.DataFrame:
        """获取行业列表"""
        def _get_data():
            logger.bind(data_fetch=True).info("开始获取行业列表")
            df = ak.stock_board_industry_name_em()
            logger.bind(data_fetch=True).info(f"成功获取 {len(df)} 个行业")
            return df
        
        return self._retry_request(_get_data)
    
    def get_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """获取指定行业的股票列表"""
        def _get_data():
            logger.bind(data_fetch=True).info(f"开始获取行业 {industry_name} 的股票列表")
            df = ak.stock_board_industry_cons_em(symbol=industry_name)
            logger.bind(data_fetch=True).info(f"成功获取行业 {industry_name} 的 {len(df)} 只股票")
            return df
        
        return self._retry_request(_get_data)


class MarketDataFetcher(DataFetcher):
    """市场数据获取器"""
    
    def get_market_index(self, index_code: str = "sh000001") -> pd.DataFrame:
        """获取市场指数数据"""
        def _get_data():
            logger.bind(data_fetch=True).info(f"开始获取指数 {index_code} 数据")
            
            df = ak.stock_zh_index_daily(symbol=index_code)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            
            logger.bind(data_fetch=True).info(f"成功获取指数 {index_code} 数据，共 {len(df)} 条记录")
            return df
        
        return self._retry_request(_get_data)
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪数据"""
        def _get_data():
            logger.bind(data_fetch=True).info("开始获取市场情绪数据")
            
            # 简化版本，避免一些可能出错的接口
            result = {
                'limit_up_count': 0,
                'market_fund_flow': {}
            }
            
            try:
                # 获取涨跌停数据
                limit_data = ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
                result['limit_up_count'] = len(limit_data) if not limit_data.empty else 0
            except:
                pass
            
            logger.bind(data_fetch=True).info("成功获取市场情绪数据")
            return result
        
        return self._retry_request(_get_data)


class DataSource:
    """统一数据源接口"""
    
    def __init__(self):
        self.stock_fetcher = StockDataFetcher()
        self.market_fetcher = MarketDataFetcher()
        logger.info("数据源初始化完成")
    
    def get_stock_data(self, 
                      symbol: str, 
                      period: str = "daily",
                      days: int = None,
                      start_date: str = None,
                      end_date: str = None) -> pd.DataFrame:
        """
        获取股票数据的统一接口
        
        Args:
            symbol: 股票代码
            period: 数据周期
            days: 获取最近多少天的数据
            start_date: 开始日期
            end_date: 结束日期
        """
        if days and not start_date:
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        
        return self.stock_fetcher.get_stock_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        return self.stock_fetcher.get_stock_list()
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        return self.stock_fetcher.get_stock_info(symbol)
    
    def get_market_data(self, index_code: str = "sh000001") -> pd.DataFrame:
        """获取市场指数数据"""
        return self.market_fetcher.get_market_index(index_code)
    
    def get_market_sentiment(self) -> Dict[str, Any]:
        """获取市场情绪"""
        return self.market_fetcher.get_market_sentiment()