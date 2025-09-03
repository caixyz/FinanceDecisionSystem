#!/usr/bin/env python3
"""
测试股票数据同步功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stock_sync import StockDataSynchronizer
from utils.logger import logger

def test_stock_sync():
    """测试股票数据同步功能"""
    print("🔍 开始测试股票数据同步功能...")
    
    try:
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 测试获取股票列表（只获取前5只股票用于测试）
        print("🔍 测试获取股票列表...")
        stock_list_df = synchronizer.data_source.get_stock_list()
        print(f"✅ 成功获取股票列表，共 {len(stock_list_df)} 只股票")
        
        if not stock_list_df.empty:
            print("📋 前5只股票信息:")
            for i, (_, row) in enumerate(stock_list_df.head().iterrows()):
                symbol = row.get('代码', '')
                name = row.get('名称', '')
                print(f"   {i+1}. {symbol} - {name}")
        
        # 测试获取单只股票的历史数据
        if not stock_list_df.empty:
            test_symbol = stock_list_df.iloc[0]['代码']
            print(f"\n🔍 测试获取股票 {test_symbol} 的历史数据...")
            stock_data = synchronizer.data_source.get_stock_data(test_symbol, days=30)
            print(f"✅ 成功获取股票 {test_symbol} 的历史数据，共 {len(stock_data)} 条记录")
            
            if not stock_data.empty:
                print("📋 最近5条数据:")
                print(stock_data.tail())
        
        # 测试搜索功能
        print("\n🔍 测试股票搜索功能...")
        search_results = synchronizer.search_stocks(keyword="平安", limit=5)
        print(f"✅ 股票搜索完成，找到 {len(search_results)} 条记录")
        for stock in search_results:
            print(f"   {stock['symbol']} - {stock['name']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"股票数据同步测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_stock_sync()