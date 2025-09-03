#!/usr/bin/env python3
"""
检查数据库中的股票数据
"""
import sys
import os
import sqlite3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.storage import db_manager

def check_stock_data():
    """检查数据库中的股票数据"""
    print("🔍 检查数据库中的股票数据...")
    
    try:
        # 连接数据库
        with sqlite3.connect(db_manager.db_path) as conn:
            # 检查股票信息表
            cursor = conn.execute("SELECT COUNT(*) FROM stock_info")
            stock_count = cursor.fetchone()[0]
            print(f"📊 股票信息表中共有 {stock_count} 只股票")
            
            # 显示前10只股票
            if stock_count > 0:
                cursor = conn.execute("SELECT symbol, name FROM stock_info LIMIT 10")
                stocks = cursor.fetchall()
                print("📋 前10只股票:")
                for symbol, name in stocks:
                    print(f"   {symbol} - {name}")
            
            # 检查股票日线数据表
            cursor = conn.execute("SELECT COUNT(*) FROM stock_daily")
            daily_count = cursor.fetchone()[0]
            print(f"📊 股票日线数据表中共有 {daily_count} 条记录")
            
            # 显示一些日线数据
            if daily_count > 0:
                cursor = conn.execute("SELECT symbol, date, close FROM stock_daily LIMIT 5")
                daily_data = cursor.fetchall()
                print("📋 部分日线数据:")
                for symbol, date, close in daily_data:
                    print(f"   {symbol} - {date} - 收盘价: {close}")
                    
        print("\n✅ 数据库检查完成！")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_stock_data()