#!/usr/bin/env python3
"""
测试股票列表同步功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.stock_sync import StockDataSynchronizer
from utils.logger import logger

def test_sync_stock_list():
    """测试同步股票列表功能"""
    print("🔍 开始测试股票列表同步功能...")
    
    try:
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 同步股票列表
        print("🔄 正在同步股票列表...")
        count = synchronizer.sync_stock_list()
        
        print(f"✅ 股票列表同步完成，共同步 {count} 只股票")
        
        # 验证同步结果
        print("🔍 验证同步结果...")
        from core.storage import db_manager
        import sqlite3
        
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM stock_info")
            total_count = cursor.fetchone()[0]
            
            # 显示前10只股票
            cursor = conn.execute("SELECT symbol, name FROM stock_info LIMIT 10")
            stocks = cursor.fetchall()
            
        print(f"📊 数据库中股票总数: {total_count}")
        print("📋 前10只股票:")
        for symbol, name in stocks:
            print(f"   {symbol} - {name}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error(f"股票列表同步测试失败: {e}")
        raise

if __name__ == "__main__":
    test_sync_stock_list()