#!/usr/bin/env python3
"""
测试股票数据管理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stock_sync import StockDataSynchronizer
from utils.logger import logger

def test_stock_management():
    """测试股票数据管理功能"""
    print("🔍 开始测试股票数据管理功能...")
    
    try:
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 测试同步股票列表
        print("🔄 正在同步股票列表...")
        count = synchronizer.sync_stock_list()
        print(f"✅ 股票列表同步完成，共同步 {count} 只股票")
        
        # 测试搜索功能
        print("🔍 测试股票搜索功能...")
        search_results = synchronizer.search_stocks(keyword="银行", limit=5)
        print(f"✅ 股票搜索完成，找到 {len(search_results)} 条记录")
        for stock in search_results:
            print(f"   {stock['symbol']} - {stock['name']}")
            
        print("\n🎉 股票数据管理功能测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"股票数据管理功能测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_management()