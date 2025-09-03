#!/usr/bin/env python3
"""
同步所有股票数据的脚本
包括股票列表、历史数据和最新数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stock_sync import StockDataSynchronizer
from utils.logger import logger
import time

def sync_all_stock_data():
    """同步所有股票数据"""
    print("🔍 开始同步所有股票数据...")
    
    try:
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 1. 同步股票列表
        print("🔄 正在同步股票列表...")
        count = synchronizer.sync_stock_list()
        print(f"✅ 股票列表同步完成，共同步 {count} 只股票")
        
        # 等待一段时间避免请求过快
        time.sleep(2)
        
        # 2. 同步所有股票的历史数据（最近365天）
        print("🔄 正在同步所有股票历史数据（最近365天）...")
        result = synchronizer.sync_all_stock_daily_data(days=365, batch_size=20, delay=0.5)
        print(f"✅ 股票历史数据同步完成: {result}")
        
        # 3. 测试同步最新数据功能
        print("🔄 正在测试同步最新数据功能...")
        result = synchronizer.sync_latest_stock_data(days=30, batch_size=20, delay=0.5)
        print(f"✅ 最新数据同步测试完成: {result}")
        
        # 4. 测试搜索功能
        print("🔍 测试股票搜索功能...")
        search_results = synchronizer.search_stocks(keyword="银行", limit=10)
        print(f"✅ 股票搜索完成，找到 {len(search_results)} 条记录")
        for stock in search_results:
            print(f"   {stock['symbol']} - {stock['name']}")
            
        print("\n🎉 所有数据同步任务完成！")
        
    except Exception as e:
        print(f"❌ 数据同步失败: {e}")
        logger.error(f"数据同步失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    sync_all_stock_data()