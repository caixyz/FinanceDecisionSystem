"""
数据存储模块
提供SQLite数据库操作和数据缓存功能
"""
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import pickle
from utils.logger import logger
from utils.config import config

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = config.get('DATABASE.path', 'data/finance_data.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logger.info(f"数据库管理器初始化完成: {self.db_path}")
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            # 创建股票基础信息表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    symbol TEXT PRIMARY KEY,
                    name TEXT,
                    industry TEXT,
                    market_cap REAL,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建股票历史数据表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_daily (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date DATE,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume BIGINT,
                    turnover REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # 创建技术指标表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS technical_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    date DATE,
                    indicator_name TEXT,
                    indicator_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date, indicator_name)
                )
            ''')
            
            # 创建回测结果表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS backtest_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT,
                    symbol TEXT,
                    start_date DATE,
                    end_date DATE,
                    initial_capital REAL,
                    final_value REAL,
                    total_return REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL,
                    trade_count INTEGER,
                    win_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建交易记录表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backtest_id INTEGER,
                    symbol TEXT,
                    trade_date DATE,
                    action TEXT,
                    price REAL,
                    quantity INTEGER,
                    amount REAL,
                    commission REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (backtest_id) REFERENCES backtest_results (id)
                )
            ''')
            
            # 创建索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_stock_daily_symbol_date ON stock_daily(symbol, date)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_date ON technical_indicators(symbol, date)')
            
            conn.commit()
            logger.info("数据库表结构初始化完成")
    
    def save_stock_daily_data(self, symbol: str, data: pd.DataFrame):
        """保存股票日线数据"""
        try:
            # 准备数据
            df = data.copy()
            df['symbol'] = symbol
            df = df.reset_index()
            
            # 选择需要的列
            columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            df = df[[col for col in columns if col in df.columns]]
            
            with sqlite3.connect(self.db_path) as conn:
                # 使用 REPLACE 来处理重复数据
                df.to_sql('stock_daily', conn, if_exists='append', index=False, method='multi')
                
            logger.info(f"成功保存股票 {symbol} 的 {len(df)} 条日线数据")
            
        except Exception as e:
            logger.error(f"保存股票日线数据失败: {e}")
            raise
    
    def get_stock_daily_data(self, 
                           symbol: str, 
                           start_date: str = None, 
                           end_date: str = None,
                           limit: int = None) -> pd.DataFrame:
        """获取股票日线数据"""
        try:
            query = "SELECT * FROM stock_daily WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                df = df.sort_index()
            
            logger.info(f"从数据库获取股票 {symbol} 数据 {len(df)} 条")
            return df
            
        except Exception as e:
            logger.error(f"获取股票日线数据失败: {e}")
            raise
    
    def save_stock_info(self, symbol: str, info: Dict[str, Any]):
        """保存股票基础信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    REPLACE INTO stock_info (symbol, name, industry, market_cap, pe_ratio, pb_ratio)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    info.get('股票简称', ''),
                    info.get('所属行业', ''),
                    info.get('总市值', 0),
                    info.get('市盈率-动态', 0),
                    info.get('市净率', 0)
                ))
                
            logger.info(f"成功保存股票 {symbol} 基础信息")
            
        except Exception as e:
            logger.error(f"保存股票基础信息失败: {e}")
            raise
    
    def save_technical_indicators(self, symbol: str, date: str, indicators: Dict[str, float]):
        """保存技术指标数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for indicator_name, value in indicators.items():
                    conn.execute('''
                        REPLACE INTO technical_indicators (symbol, date, indicator_name, indicator_value)
                        VALUES (?, ?, ?, ?)
                    ''', (symbol, date, indicator_name, value))
                
            logger.info(f"成功保存股票 {symbol} 在 {date} 的 {len(indicators)} 个技术指标")
            
        except Exception as e:
            logger.error(f"保存技术指标失败: {e}")
            raise
    
    def get_technical_indicators(self, 
                               symbol: str, 
                               start_date: str = None, 
                               end_date: str = None) -> pd.DataFrame:
        """获取技术指标数据"""
        try:
            query = "SELECT * FROM technical_indicators WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
                
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date"
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
            
            if not df.empty:
                # 转换为透视表格式
                df['date'] = pd.to_datetime(df['date'])
                df = df.pivot_table(
                    index='date', 
                    columns='indicator_name', 
                    values='indicator_value'
                ).fillna(method='ffill')
            
            return df
            
        except Exception as e:
            logger.error(f"获取技术指标数据失败: {e}")
            raise
    
    def save_backtest_result(self, result: Dict[str, Any]) -> int:
        """保存回测结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    INSERT INTO backtest_results (
                        strategy_name, symbol, start_date, end_date,
                        initial_capital, final_value, total_return, 
                        max_drawdown, sharpe_ratio, trade_count, win_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.get('strategy_name'),
                    result.get('symbol'),
                    result.get('start_date'),
                    result.get('end_date'),
                    result.get('initial_capital'),
                    result.get('final_value'),
                    result.get('total_return'),
                    result.get('max_drawdown'),
                    result.get('sharpe_ratio'),
                    result.get('trade_count'),
                    result.get('win_rate')
                ))
                
                backtest_id = cursor.lastrowid
                
            logger.info(f"成功保存回测结果，ID: {backtest_id}")
            return backtest_id
            
        except Exception as e:
            logger.error(f"保存回测结果失败: {e}")
            raise


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = config.get('REDIS.cache_ttl', 3600)  # 默认1小时
        logger.info(f"缓存管理器初始化完成: {self.cache_dir}")
    
    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.cache"
    
    def _get_meta_path(self, key: str) -> Path:
        """获取缓存元数据文件路径"""
        return self.cache_dir / f"{key}.meta"
    
    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            # 保存数据
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # 保存元数据
            meta = {
                'created_at': datetime.now().timestamp(),
                'ttl': ttl,
                'expires_at': datetime.now().timestamp() + ttl
            }
            
            with open(meta_path, 'w') as f:
                json.dump(meta, f)
            
            logger.debug(f"缓存已设置: {key}, TTL: {ttl}秒")
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            if not cache_path.exists() or not meta_path.exists():
                return None
            
            # 检查是否过期
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            
            if datetime.now().timestamp() > meta['expires_at']:
                self.delete(key)
                return None
            
            # 读取数据
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            logger.debug(f"缓存命中: {key}")
            return value
            
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def delete(self, key: str):
        """删除缓存"""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            if cache_path.exists():
                cache_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            
            logger.debug(f"缓存已删除: {key}")
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
    
    def clear_expired(self):
        """清理过期缓存"""
        try:
            current_time = datetime.now().timestamp()
            cleared_count = 0
            
            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        meta = json.load(f)
                    
                    if current_time > meta['expires_at']:
                        key = meta_file.stem
                        self.delete(key)
                        cleared_count += 1
                        
                except Exception as e:
                    logger.warning(f"清理缓存文件 {meta_file} 时出错: {e}")
            
            logger.info(f"清理了 {cleared_count} 个过期缓存")
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")


# 全局实例
db_manager = DatabaseManager()
cache_manager = CacheManager()
