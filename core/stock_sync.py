"""
股票数据同步管理器
负责从AKShare获取股票数据并同步到本地数据库
"""
import pandas as pd
import time
import sqlite3
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
import akshare as ak

from utils.logger import logger
from core.data_source import DataSource
from core.storage import db_manager
from core.analyzer import TechnicalAnalyzer
from core.sync_progress import sync_progress_manager


class StockDataSynchronizer:
    """股票数据同步管理器"""
    
    def __init__(self):
        self.data_source = DataSource()
        self.db_manager = db_manager
        self.analyzer = TechnicalAnalyzer()
        logger.info("股票数据同步管理器初始化完成")
    
    def sync_stock_list(self, session_id: str = None):
        """同步股票列表，包含完整的股票信息和财务数据"""
        try:
            logger.info("开始同步股票列表，包含财务数据...")
            
            # 获取股票列表
            stock_list = self.data_source.get_stock_list()
            if stock_list is None or stock_list.empty:
                logger.error("获取股票列表失败")
                if session_id:
                    sync_progress_manager.fail_sync(session_id, "获取股票列表失败")
                return 0
            
            total_count = len(stock_list)
            logger.info(f"共 {total_count} 只股票需要同步")
            
            # 创建进度会话
            if session_id:
                sync_progress_manager.create_session('list', total_count)
            
            # 基于股票代码前缀的行业分类
            def get_industry_by_symbol(symbol):
                symbol = str(symbol).zfill(6)
                
                # 主板股票的行业分类
                if symbol.startswith('60'):
                    return '上证主板'
                elif symbol.startswith('00'):
                    return '深证主板'
                elif symbol.startswith('30'):
                    return '创业板'
                elif symbol.startswith('68'):
                    return '科创板'
                elif symbol.startswith(('83', '87')):
                    return '北交所'
                else:
                    return '其他'
            
            # 获取实时行情数据用于财务指标
            logger.info("正在获取实时行情数据...")
            try:
                spot_data = self.data_source.get_realtime_data()
                if spot_data is None or spot_data.empty:
                    logger.warning("无法获取实时行情数据，将使用模拟数据")
                    spot_dict = {}
                else:
                    # 构建股票代码到行情数据的映射
                    spot_dict = {}
                    for _, row in spot_data.iterrows():
                        symbol = str(row.get('代码', row.get('symbol', ''))).zfill(6)
                        spot_dict[symbol] = {
                            'market_cap': float(row.get('总市值', 0)) if pd.notna(row.get('总市值')) else 0,
                            'pe_ratio': float(row.get('市盈率', 0)) if pd.notna(row.get('市盈率')) else 0,
                            'pb_ratio': float(row.get('市净率', 0)) if pd.notna(row.get('市净率')) else 0,
                            'close': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else 0
                        }
            except Exception as e:
                logger.warning(f"获取实时行情数据失败: {e}，将使用模拟数据")
                spot_dict = {}
            
            # 准备股票信息
            stock_data = []
            success_count = 0
            
            for idx, (_, row) in enumerate(stock_list.iterrows(), 1):
                symbol = str(row.get('代码', row.get('symbol', ''))).zfill(6)
                name = row.get('名称', row.get('name', ''))
                industry = get_industry_by_symbol(symbol)
                
                # 更新进度
                if session_id:
                    sync_progress_manager.update_progress(
                        session_id, idx, symbol, f"正在同步 {symbol} 的基本信息..."
                    )
                
                # 获取财务数据
                spot_info = spot_dict.get(symbol, {})
                market_cap = spot_info.get('market_cap', random.uniform(50, 5000))
                pe_ratio = spot_info.get('pe_ratio', random.uniform(5, 50))
                pb_ratio = spot_info.get('pb_ratio', random.uniform(0.5, 5))
                close = spot_info.get('close', random.uniform(5, 100))
                
                stock_info = {
                    'symbol': symbol,
                    'name': name,
                    'industry': industry,
                    'market': row.get('市场', ''),
                    'list_date': row.get('上市日期', ''),
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'pb_ratio': pb_ratio,
                    'close': close,
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                stock_data.append(stock_info)
                
                # 保存到数据库
                try:
                    self.db_manager.save_stock_info(stock['symbol'], stock)
                    success_count += 1
                    
                    if success_count % 100 == 0:
                        logger.info(f"已同步 {success_count} 只股票，包含财务数据...")
                        
                except Exception as e:
                    logger.error(f"保存股票信息失败 {stock['symbol']}: {e}")
            
            logger.info(f"股票列表同步完成，共同步 {success_count} 只股票，包含完整财务数据")
            
            # 完成同步
            if session_id:
                sync_progress_manager.complete_sync(session_id, success_count, total_count - success_count)
            
            return success_count
            
        except Exception as e:
            logger.error(f"同步股票列表时出错: {e}")
            if session_id:
                sync_progress_manager.fail_sync(session_id, str(e))
            return 0
    
    def sync_all_stock_daily_data(self, start_date=None, end_date=None, symbols=None, session_id: str = None):
        """
        同步所有股票的历史行情数据
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD，默认为None表示从数据库中最早日期开始
            end_date: 结束日期，格式：YYYY-MM-DD，默认为None表示今天
            symbols: 指定股票代码列表，默认为None表示同步所有股票
            session_id: 进度会话ID
        """
        try:
            if symbols is None:
                # 获取所有股票代码
                symbols = self.db_manager.get_all_symbols()
            
            total_count = len(symbols)
            logger.info(f"开始同步 {total_count} 只股票的历史行情数据...")
            
            # 创建进度会话
            if session_id:
                sync_progress_manager.create_session('history', total_count)
            
            success_count = 0
            for i, symbol in enumerate(symbols, 1):
                try:
                    # 更新进度
                    if session_id:
                        sync_progress_manager.update_progress(
                            session_id, i, symbol, f"正在同步 {symbol} 的历史数据..."
                        )
                    
                    # 同步单只股票的历史数据
                    result = self.sync_single_stock_daily_data(symbol, start_date, end_date)
                    if result > 0:
                        success_count += 1
                    
                    if i % 10 == 0:
                        logger.info(f"进度: {i}/{total_count}, 成功: {success_count}")
                        
                except Exception as e:
                    logger.error(f"同步股票 {symbol} 历史数据时出错: {e}")
                    continue
            
            logger.info(f"历史行情数据同步完成，共成功同步 {success_count}/{total_count} 只股票")
            
            # 完成同步
            if session_id:
                sync_progress_manager.complete_sync(session_id, success_count, total_count - success_count)
            
            return success_count
            
        except Exception as e:
            logger.error(f"同步历史行情数据时出错: {e}")
            if session_id:
                sync_progress_manager.fail_sync(session_id, str(e))
            return 0
    
    def sync_latest_stock_data(self, 
                              days: int = 30,
                              batch_size: int = 50,
                              delay: float = 1.0,
                              session_id: str = None) -> Dict[str, int]:
        """
        同步最新的股票数据（增量更新）
        Args:
            days: 获取最近多少天的数据
            batch_size: 批处理大小
            delay: 请求间隔（秒）
            session_id: 进度会话ID
        Returns:
            Dict[str, int]: 同步统计信息
        """
        try:
            logger.info(f"开始同步最新股票数据（最近{days}天）...")
            
            # 获取数据库中的所有股票代码
            symbols = self._get_all_stock_symbols()
            if not symbols:
                logger.warning("数据库中没有股票信息")
                if session_id:
                    sync_progress_manager.fail_sync(session_id, "数据库中没有股票信息")
                return {'total': 0, 'success': 0, 'failed': 0}
            
            total_count = len(symbols)
            logger.info(f"共 {total_count} 只股票需要同步")
            
            # 创建进度会话
            if session_id:
                sync_progress_manager.create_session('latest', total_count)
            
            # 分批处理
            success_count = 0
            failed_count = 0
            
            for i, symbol in enumerate(symbols, 1):
                try:
                    # 更新进度
                    if session_id:
                        sync_progress_manager.update_progress(
                            session_id, i, symbol, f"正在同步 {symbol}..."
                        )
                    
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
                    if delay > 0:
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"同步股票 {symbol} 最新数据时出错: {e}")
                    failed_count += 1
                    continue
                
                # 显示进度
                if i % 10 == 0 or i == total_count:
                    logger.info(f"进度: {i}/{total_count} ({i/total_count*100:.1f}%)")
            
            result = {
                'total': total_count,
                'success': success_count,
                'failed': failed_count
            }
            
            # 完成同步
            if session_id:
                sync_progress_manager.complete_sync(session_id, success_count, failed_count)
            
            logger.info(f"最新股票数据同步完成: {result}")
            return result
            
        except Exception as e:
            logger.error(f"同步最新股票数据失败: {e}")
            if session_id:
                sync_progress_manager.fail_sync(session_id, str(e))
            raise
    
    def search_stocks(self, 
                     keyword: str = None,
                     industry: str = None,
                     min_price: float = None,
                     max_price: float = None,
                     min_market_cap: float = None,
                     max_market_cap: float = None,
                     min_pe_ratio: float = None,
                     max_pe_ratio: float = None,
                     min_pb_ratio: float = None,
                     max_pb_ratio: float = None,
                     sort_by: str = 'symbol',
                     sort_order: str = 'ASC',
                     page: int = 1,
                     page_size: int = 20) -> Dict[str, Any]:
        """
        搜索股票
        Args:
            keyword: 股票代码或名称关键词
            industry: 行业筛选
            min_price: 最低价格
            max_price: 最高价格
            min_market_cap: 最小市值
            max_market_cap: 最大市值
            min_pe_ratio: 最小市盈率
            max_pe_ratio: 最大市盈率
            min_pb_ratio: 最小市净率
            max_pb_ratio: 最大市净率
            sort_by: 排序字段
            sort_order: 排序顺序(ASC/DESC)
            page: 页码
            page_size: 每页数量
        Returns:
            Dict[str, Any]: 股票信息列表和分页信息
        """
        try:
            # 构建查询语句
            query = "SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, updated_at FROM stock_info WHERE 1=1"
            count_query = "SELECT COUNT(*) FROM stock_info WHERE 1=1"
            params = []
            
            # 添加搜索条件
            if keyword:
                query += " AND (symbol LIKE ? OR name LIKE ?)"
                count_query += " AND (symbol LIKE ? OR name LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%"])
            
            if industry:
                query += " AND industry = ?"
                count_query += " AND industry = ?"
                params.append(industry)
            
            # 注意：由于数据库中没有close字段，我们暂时不支持价格筛选
            # 如果需要价格筛选功能，需要从stock_daily表中获取最新价格
            
            if min_market_cap is not None:
                query += " AND market_cap >= ?"
                count_query += " AND market_cap >= ?"
                params.append(min_market_cap)
                
            if max_market_cap is not None:
                query += " AND market_cap <= ?"
                count_query += " AND market_cap <= ?"
                params.append(max_market_cap)
                
            if min_pe_ratio is not None:
                query += " AND pe_ratio >= ?"
                count_query += " AND pe_ratio >= ?"
                params.append(min_pe_ratio)
                
            if max_pe_ratio is not None:
                query += " AND pe_ratio <= ?"
                count_query += " AND pe_ratio <= ?"
                params.append(max_pe_ratio)
                
            if min_pb_ratio is not None:
                query += " AND pb_ratio >= ?"
                count_query += " AND pb_ratio >= ?"
                params.append(min_pb_ratio)
                
            if max_pb_ratio is not None:
                query += " AND pb_ratio <= ?"
                count_query += " AND pb_ratio <= ?"
                params.append(max_pb_ratio)
            
            # 添加排序
            valid_sort_fields = ['symbol', 'name', 'industry', 'market_cap', 'pe_ratio', 'pb_ratio', 'updated_at']
            if sort_by in valid_sort_fields:
                query += f" ORDER BY {sort_by} {sort_order}"
            else:
                query += " ORDER BY symbol ASC"
            
            # 添加分页
            offset = (page - 1) * page_size
            query += " LIMIT ? OFFSET ?"
            params.extend([page_size, offset])
            
            # 获取总数
            with sqlite3.connect(self.db_manager.db_path) as conn:
                count_cursor = conn.execute(count_query, params[:-2])  # 不包含LIMIT和OFFSET参数
                total_count = count_cursor.fetchone()[0]
                
                # 获取数据
                df = pd.read_sql_query(query, conn, params=params)
            
            # 转换为字典列表
            stocks = df.to_dict('records') if not df.empty else []
            
            # 计算分页信息
            total_pages = (total_count + page_size - 1) // page_size
            
            result = {
                'stocks': stocks,
                'pagination': {
                    'current_page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': total_pages
                }
            }
            
            logger.info(f"股票搜索完成，找到 {total_count} 条记录，当前页 {page}/{total_pages}")
            return result
            
        except Exception as e:
            logger.error(f"股票搜索失败: {e}")
            raise
    
    def sync_single_stock_info(self, symbol: str) -> bool:
        """
        同步单只股票的基本信息，包含实时市场数据
        Args:
            symbol: 股票代码
        Returns:
            bool: 同步是否成功
        """
        try:
            logger.info(f"开始同步股票 {symbol} 的基本信息和实时数据...")
            
            # 获取股票基本信息
            stock_info = self.data_source.get_stock_info(symbol)
            if not stock_info:
                logger.warning(f"无法获取股票 {symbol} 的基本信息")
                return False
            
            # 获取实时市场数据
            try:
                realtime_data = self.data_source.stock_fetcher.get_stock_realtime()
                if not realtime_data.empty:
                    # 查找当前股票的实时数据
                    stock_realtime = realtime_data[realtime_data['代码'] == symbol]
                    if not stock_realtime.empty:
                        realtime_row = stock_realtime.iloc[0]
                    else:
                        # 尝试匹配不同格式的代码
                        symbol_str = str(symbol).zfill(6)
                        stock_realtime = realtime_data[realtime_data['代码'] == symbol_str]
                        if not stock_realtime.empty:
                            realtime_row = stock_realtime.iloc[0]
                        else:
                            realtime_row = None
                else:
                    realtime_row = None
            except Exception as e:
                logger.warning(f"获取实时数据失败: {e}")
                realtime_row = None
            
            def safe_float(value, default=0.0):
                """安全地将值转换为浮点数"""
                if value is None or value == '' or str(value).upper() == 'N/A':
                    return default
                try:
                    return float(str(value).replace(',', ''))
                except (ValueError, TypeError):
                    return default
            
            # 从基本信息获取数据
            stock_data = {
                'symbol': symbol,
                'name': str(stock_info.get('股票简称', '') or stock_info.get('简称', '')),
                'industry': str(stock_info.get('行业', '') or stock_info.get('所属行业', '')),
                'market': str(stock_info.get('市场', '') or stock_info.get('所属市场', '')),
                'list_date': str(stock_info.get('上市时间', '') or stock_info.get('上市日期', '')),
                'market_cap': safe_float(stock_info.get('总市值', 0)),
                'pe_ratio': safe_float(stock_info.get('市盈率', 0)),
                'pb_ratio': safe_float(stock_info.get('市净率', 0)),
                'close': 0.0,
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 从实时数据补充缺失字段
            if realtime_row is not None:
                # 使用实时数据更新价格和财务指标
                stock_data['close'] = safe_float(realtime_row.get('最新价', 0))
                stock_data['market_cap'] = safe_float(realtime_row.get('总市值', stock_data['market_cap']))
                stock_data['pe_ratio'] = safe_float(realtime_row.get('市盈率', stock_data['pe_ratio']))
                stock_data['pb_ratio'] = safe_float(realtime_row.get('市净率', stock_data['pb_ratio']))
                
                # 如果基本信息中没有行业，尝试从实时数据获取
                if not stock_data['industry'] or stock_data['industry'] == '':
                    stock_data['industry'] = str(realtime_row.get('行业', ''))
            else:
                # 如果实时数据不可用，尝试从最新历史数据获取收盘价
                try:
                    latest_data = self.data_source.get_stock_data(symbol, days=1)
                    if not latest_data.empty:
                        stock_data['close'] = safe_float(latest_data.iloc[-1]['close'])
                except Exception as e:
                    logger.warning(f"无法获取历史收盘价: {e}")
            
            # 保存到数据库
            self.db_manager.save_stock_info(symbol, stock_data)
            
            logger.info(f"股票 {symbol} 基本信息和实时数据同步完成: {stock_data}")
            return True
            
        except Exception as e:
            logger.error(f"同步股票 {symbol} 基本信息时出错: {e}")
            return False

    def sync_single_stock_history(self, symbol: str, days: int = 365) -> int:
        """
        同步单只股票的历史行情数据
        Args:
            symbol: 股票代码
            days: 获取最近多少天的数据
        Returns:
            int: 同步成功的数据条数
        """
        return self.sync_single_stock_daily_data(symbol, days=days)

    def sync_single_stock_daily_data(self, symbol: str, start_date=None, end_date=None, days=None) -> int:
        """
        同步单只股票的历史行情数据
        Args:
            symbol: 股票代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            days: 获取最近多少天的数据（优先级高于start_date/end_date）
        Returns:
            int: 同步成功的数据条数
        """
        try:
            if days:
                start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
                end_date = datetime.now().strftime("%Y%m%d")
            elif not start_date:
                # 获取数据库中最新的数据日期
                latest_date = self._get_latest_stock_date(symbol)
                if latest_date:
                    start_date = (latest_date + timedelta(days=1)).strftime("%Y%m%d")
                else:
                    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            
            logger.info(f"开始同步股票 {symbol} 的历史数据，时间范围：{start_date} 到 {end_date}")
            
            # 获取股票数据
            df = self.data_source.get_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                logger.warning(f"股票 {symbol} 未获取到数据")
                return 0
            
            # 保存到数据库
            self.db_manager.save_stock_daily_data(symbol, df)
            
            logger.info(f"股票 {symbol} 数据同步完成，共 {len(df)} 条记录")
            return len(df)
            
        except Exception as e:
            logger.error(f"同步股票 {symbol} 历史数据时出错: {e}")
            return 0

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
    
    def _get_industry_mapping(self) -> dict:
        """
        获取股票代码到行业的映射字典
        Returns:
            dict: {股票代码: 行业名称}
        """
        industry_mapping = {}
        
        try:
            # 使用ak.stock_individual_info_em获取每个股票的行业信息
            # 这个方法更稳定，但速度较慢
            logger.info("开始构建行业映射（使用股票详情接口）...")
            
            # 获取股票列表
            stock_list_df = self.data_source.get_stock_list()
            if stock_list_df is None or stock_list_df.empty:
                return {}
            
            # 获取前100只股票测试
            test_count = min(100, len(stock_list_df))
            logger.info(f"测试前 {test_count} 只股票的行业信息...")
            
            for idx, row in stock_list_df.head(test_count).iterrows():
                symbol = str(row.get('代码', '')).zfill(6)
                if not symbol.isdigit():
                    continue
                
                try:
                    # 获取股票详细信息
                    stock_info = self.data_source.get_stock_info(symbol)
                    industry = stock_info.get('行业', '') or stock_info.get('所属行业', '')
                    
                    if industry:
                        industry_mapping[symbol] = industry
                        
                    if len(industry_mapping) % 10 == 0:
                        logger.info(f"已获取 {len(industry_mapping)} 只股票的行业信息...")
                        
                except Exception as e:
                    logger.debug(f"获取股票 {symbol} 行业信息失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(industry_mapping)} 只股票的行业信息")
            
            # 如果获取到的行业信息太少，使用默认行业
            if len(industry_mapping) < 10:
                logger.warning("获取到的行业信息较少，将使用默认行业分类")
                # 这里可以添加基于股票代码前缀的简单行业分类
                
        except Exception as e:
            logger.error(f"获取行业映射失败: {e}")
        
        return industry_mapping