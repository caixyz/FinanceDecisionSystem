"""
股票数据同步管理器
负责从AKShare获取股票数据并同步到本地数据库
"""
import pandas as pd
import time
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import akshare as ak

from utils.logger import logger
from core.data_source import DataSource
from core.storage import db_manager
from core.analyzer import TechnicalAnalyzer


class StockDataSynchronizer:
    """股票数据同步管理器"""
    
    def __init__(self):
        self.data_source = DataSource()
        self.db_manager = db_manager
        self.analyzer = TechnicalAnalyzer()
        logger.info("股票数据同步管理器初始化完成")
    
    def sync_stock_list(self) -> int:
        """
        同步股票列表到数据库
        Returns:
            int: 成功同步的股票数量
        """
        try:
            logger.info("开始同步股票列表...")
            
            # 获取股票列表
            stock_list_df = self.data_source.get_stock_list()
            
            if stock_list_df.empty:
                logger.warning("未获取到股票列表数据")
                return 0
            
            synced_count = 0
            
            # 遍历股票列表并保存到数据库
            for _, row in stock_list_df.iterrows():
                try:
                    # 提取股票信息
                    symbol = row.get('代码', '')
                    name = row.get('名称', '')
                    
                    if not symbol:
                        continue
                    
                    # 构造股票信息字典
                    stock_info = {
                        '股票简称': name
                    }
                    
                    # 保存到数据库
                    self.db_manager.save_stock_info(symbol, stock_info)
                    synced_count += 1
                    
                except Exception as e:
                    logger.warning(f"同步股票 {row.get('代码', '')} 信息时出错: {e}")
                    continue
            
            logger.info(f"股票列表同步完成，共同步 {synced_count} 只股票")
            return synced_count
            
        except Exception as e:
            logger.error(f"同步股票列表失败: {e}")
            raise
    
    def sync_all_stock_daily_data(self, 
                                 days: int = 365,
                                 batch_size: int = 50,
                                 delay: float = 1.0) -> Dict[str, int]:
        """
        同步所有股票的历史日线数据
        Args:
            days: 获取最近多少天的数据
            batch_size: 批处理大小
            delay: 请求间隔（秒）
        Returns:
            Dict[str, int]: 同步统计信息
        """
        try:
            logger.info(f"开始同步所有股票日线数据（最近{days}天）...")
            
            # 获取数据库中的所有股票代码
            symbols = self._get_all_stock_symbols()
            if not symbols:
                logger.warning("数据库中没有股票信息")
                return {'total': 0, 'success': 0, 'failed': 0}
            
            logger.info(f"共 {len(symbols)} 只股票需要同步")
            
            # 分批处理
            total_count = len(symbols)
            success_count = 0
            failed_count = 0
            
            for i in range(0, total_count, batch_size):
                batch_symbols = symbols[i:i + batch_size]
                logger.info(f"处理批次 {i//batch_size + 1}/{(total_count-1)//batch_size + 1}，共 {len(batch_symbols)} 只股票")
                
                for symbol in batch_symbols:
                    try:
                        # 获取股票历史数据
                        df = self.data_source.get_stock_data(symbol, days=days)
                        
                        if not df.empty:
                            # 保存到数据库
                            self.db_manager.save_stock_daily_data(symbol, df)
                            success_count += 1
                            logger.debug(f"股票 {symbol} 数据同步成功，共 {len(df)} 条记录")
                        else:
                            logger.warning(f"股票 {symbol} 未获取到历史数据")
                            failed_count += 1
                        
                        # 延时避免请求过快
                        time.sleep(delay)
                        
                    except Exception as e:
                        logger.error(f"同步股票 {symbol} 数据时出错: {e}")
                        failed_count += 1
                        continue
                
                # 显示进度
                processed = min(i + batch_size, total_count)
                logger.info(f"进度: {processed}/{total_count} ({processed/total_count*100:.1f}%)")
            
            result = {
                'total': total_count,
                'success': success_count,
                'failed': failed_count
            }
            
            logger.info(f"股票日线数据同步完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"同步所有股票日线数据失败: {e}")
            raise
    
    def sync_latest_stock_data(self, 
                              days: int = 30,
                              batch_size: int = 50,
                              delay: float = 1.0) -> Dict[str, int]:
        """
        同步最新的股票数据（增量更新）
        Args:
            days: 获取最近多少天的数据
            batch_size: 批处理大小
            delay: 请求间隔（秒）
        Returns:
            Dict[str, int]: 同步统计信息
        """
        try:
            logger.info(f"开始同步最新股票数据（最近{days}天）...")
            
            # 获取数据库中的所有股票代码
            symbols = self._get_all_stock_symbols()
            if not symbols:
                logger.warning("数据库中没有股票信息")
                return {'total': 0, 'success': 0, 'failed': 0}
            
            logger.info(f"共 {len(symbols)} 只股票需要同步")
            
            # 分批处理
            total_count = len(symbols)
            success_count = 0
            failed_count = 0
            
            for i in range(0, total_count, batch_size):
                batch_symbols = symbols[i:i + batch_size]
                logger.info(f"处理批次 {i//batch_size + 1}/{(total_count-1)//batch_size + 1}，共 {len(batch_symbols)} 只股票")
                
                for symbol in batch_symbols:
                    try:
                        # 检查数据库中最新的数据日期
                        latest_date = self._get_latest_stock_date(symbol)
                        
                        # 如果数据库中没有数据或数据不是最新的，则获取最近的数据
                        if latest_date is None:
                            # 获取最近days天的数据
                            df = self.data_source.get_stock_data(symbol, days=days)
                        else:
                            # 只获取最新数据
                            start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
                            end_date = datetime.now().strftime("%Y%m%d")
                            
                            if start_date <= end_date:
                                df = self.data_source.get_stock_data(
                                    symbol, 
                                    start_date=start_date, 
                                    end_date=end_date
                                )
                            else:
                                # 数据已经是最新的
                                logger.debug(f"股票 {symbol} 数据已是最新的")
                                success_count += 1
                                continue
                        
                        if not df.empty:
                            # 保存到数据库
                            self.db_manager.save_stock_daily_data(symbol, df)
                            success_count += 1
                            logger.debug(f"股票 {symbol} 最新数据同步成功，共 {len(df)} 条记录")
                        else:
                            logger.warning(f"股票 {symbol} 未获取到最新数据")
                            success_count += 1  # 没有新数据也算成功
                        
                        # 延时避免请求过快
                        time.sleep(delay)
                        
                    except Exception as e:
                        logger.error(f"同步股票 {symbol} 最新数据时出错: {e}")
                        failed_count += 1
                        continue
                
                # 显示进度
                processed = min(i + batch_size, total_count)
                logger.info(f"进度: {processed}/{total_count} ({processed/total_count*100:.1f}%)")
            
            result = {
                'total': total_count,
                'success': success_count,
                'failed': failed_count
            }
            
            logger.info(f"最新股票数据同步完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"同步最新股票数据失败: {e}")
            raise
    
    def search_stocks(self, 
                     keyword: str = None,
                     industry: str = None,
                     min_price: float = None,
                     max_price: float = None,
                     limit: int = 100) -> List[Dict]:
        """
        搜索股票
        Args:
            keyword: 股票代码或名称关键词
            industry: 行业筛选
            min_price: 最低价格
            max_price: 最高价格
            limit: 返回结果数量限制
        Returns:
            List[Dict]: 股票信息列表
        """
        try:
            query = "SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio FROM stock_info WHERE 1=1"
            params = []
            
            if keyword:
                query += " AND (symbol LIKE ? OR name LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if industry:
                query += " AND industry = ?"
                params.append(industry)
            
            if min_price is not None:
                query += " AND close >= ?"
                params.append(min_price)
            
            if max_price is not None:
                query += " AND close <= ?"
                params.append(max_price)
            
            query += " ORDER BY symbol LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            # 转换为字典列表
            result = df.to_dict('records') if not df.empty else []
            
            logger.info(f"股票搜索完成，找到 {len(result)} 条记录")
            return result
            
        except Exception as e:
            logger.error(f"股票搜索失败: {e}")
            raise
    
    def get_stock_data_range(self, symbol: str, days: int = None) -> Tuple[Optional[str], Optional[str]]:
        """
        获取股票数据的时间范围
        Args:
            symbol: 股票代码
            days: 限制天数（可选）
        Returns:
            Tuple[Optional[str], Optional[str]]: (最早日期, 最晚日期)
        """
        try:
            query = "SELECT MIN(date) as min_date, MAX(date) as max_date FROM stock_daily WHERE symbol = ?"
            params = [symbol]
            
            if days:
                min_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
                query += " AND date >= ?"
                params.append(min_date)
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.execute(query, params)
                result = cursor.fetchone()
            
            if result and result[0] and result[1]:
                return result[0], result[1]
            return None, None
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 数据范围失败: {e}")
            return None, None
    
    def _get_all_stock_symbols(self) -> List[str]:
        """获取数据库中所有股票代码"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.execute("SELECT symbol FROM stock_info")
                symbols = [row[0] for row in cursor.fetchall()]
            return symbols
        except Exception as e:
            logger.error(f"获取股票代码列表失败: {e}")
            return []
    
    def _get_latest_stock_date(self, symbol: str) -> Optional[datetime]:
        """获取股票在数据库中的最新数据日期"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.execute(
                    "SELECT MAX(date) FROM stock_daily WHERE symbol = ?", 
                    (symbol,)
                )
                result = cursor.fetchone()
            
            if result and result[0]:
                return datetime.strptime(result[0], "%Y-%m-%d")
            return None
        except Exception as e:
            logger.error(f"获取股票 {symbol} 最新日期失败: {e}")
            return None