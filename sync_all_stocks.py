#!/usr/bin/env python3
"""
同步所有股票数据到数据库
"""
import sys
import os
sys.path.append('core')

from core.data_source import DataSource
from core.storage import DatabaseManager
from core.stock_sync import StockDataSynchronizer
import pandas as pd
import time
from datetime import datetime

def sync_all_stocks():
    """同步所有股票数据"""
    print("=== 开始同步所有股票数据 ===")
    
    # 初始化组件
    ds = DataSource()
    db = DatabaseManager()
    syncer = StockDataSynchronizer()
    
    try:
        # 1. 获取实时股票列表
        print("正在获取实时股票列表...")
        realtime_data = ds.stock_fetcher.get_stock_realtime()
        total_stocks = len(realtime_data)
        print(f"成功获取 {total_stocks} 只股票数据")
        
        # 2. 保存股票列表到数据库
        print("正在保存股票列表到数据库...")
        stocks_added = 0
        stocks_updated = 0
        
        for index, row in realtime_data.iterrows():
            symbol = str(row.get('代码', '')).zfill(6)
            name = str(row.get('名称', ''))
            
            # 构建股票信息
            stock_info = {
                'symbol': symbol,
                'name': name,
                'market_cap': float(row.get('总市值', 0) or 0),
                'close': float(row.get('最新价', 0) or 0),
                'industry': str(row.get('行业', '')) if pd.notna(row.get('行业')) else '未知',
                'pe': float(row.get('市盈率', 0) or 0) if pd.notna(row.get('市盈率')) else 0,
                'pb': float(row.get('市净率', 0) or 0) if pd.notna(row.get('市净率')) else 0,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 保存到数据库
            try:
                db.save_stock_info(stock_info)
                stocks_added += 1
                
                if stocks_added % 100 == 0:
                    print(f"已处理 {stocks_added}/{total_stocks} 只股票...")
                    
            except Exception as e:
                print(f"保存股票 {symbol} 失败: {e}")
                continue
        
        print(f"股票列表同步完成: 新增 {stocks_added} 只")
        
        # 3. 显示同步结果
        final_stock_list = db.get_stock_list()
        print(f"\n=== 同步完成 ===")
        print(f"数据库中股票总数: {len(final_stock_list)}")
        
        if isinstance(final_stock_list, list) and final_stock_list:
            print("前10只股票:")
            for stock in final_stock_list[:10]:
                print(f"  {stock['symbol']} - {stock['name']} - {stock['industry']}")
        elif hasattr(final_stock_list, 'head'):
            print("前10只股票:")
            for _, stock in final_stock_list.head(10).iterrows():
                print(f"  {stock['symbol']} - {stock['name']} - {stock['industry']}")
        
        return True
        
    except Exception as e:
        print(f"同步失败: {e}")
        return False

if __name__ == "__main__":
    sync_all_stocks()