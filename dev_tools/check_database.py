#!/usr/bin/env python3
"""
检查 finance_data.db 数据库内容
"""
import sqlite3
import pandas as pd
from pathlib import Path
import os

def check_database():
    # 检查数据库文件是否存在
    db_path = Path("data/finance_data.db")
    
    print(f"检查数据库路径: {db_path.absolute()}")
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        
        # 创建数据库目录和初始化数据库
        db_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已创建数据库目录: {db_path.parent}")
        
        # 尝试初始化数据库
        try:
            from core.storage import DatabaseManager
            db_manager = DatabaseManager()
            print("✅ 数据库已初始化")
        except Exception as e:
            print(f"❌ 初始化数据库失败: {e}")
            return
    else:
        print("✅ 数据库文件存在")
    
    # 连接数据库并检查内容
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if not tables:
                print("📋 数据库中没有表")
                return
            
            print(f"\n📋 数据库中的表 ({len(tables)} 个):")
            
            for (table_name,) in tables:
                print(f"\n🔍 表: {table_name}")
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print("   列结构:")
                for col in columns:
                    print(f"     - {col[1]} ({col[2]})")
                
                # 获取数据数量
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   数据行数: {count}")
                
                # 如果有数据，显示前几行
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                    sample_data = cursor.fetchall()
                    print("   示例数据:")
                    for i, row in enumerate(sample_data):
                        print(f"     {i+1}: {row}")
                    
                    # 对于股票数据表，显示有哪些股票
                    if table_name == 'stock_daily':
                        cursor.execute("SELECT DISTINCT symbol FROM stock_daily;")
                        symbols = cursor.fetchall()
                        print(f"   包含股票: {[s[0] for s in symbols]}")
                        
                        # 显示每个股票的数据范围
                        for (symbol,) in symbols:
                            cursor.execute("""
                                SELECT MIN(date), MAX(date), COUNT(*) 
                                FROM stock_daily WHERE symbol = ?
                            """, (symbol,))
                            min_date, max_date, data_count = cursor.fetchone()
                            print(f"     {symbol}: {min_date} ~ {max_date} ({data_count} 条)")
                    
                    elif table_name == 'stock_info':
                        cursor.execute("SELECT symbol, name FROM stock_info;")
                        stocks = cursor.fetchall()
                        print(f"   股票信息: {stocks}")
                        
                    elif table_name == 'technical_indicators':
                        cursor.execute("SELECT DISTINCT symbol FROM technical_indicators;")
                        symbols = cursor.fetchall()
                        cursor.execute("SELECT DISTINCT indicator_name FROM technical_indicators;")
                        indicators = cursor.fetchall()
                        print(f"   技术指标股票: {[s[0] for s in symbols]}")
                        print(f"   指标类型: {[i[0] for i in indicators]}")
                        
                    elif table_name == 'backtest_results':
                        cursor.execute("SELECT strategy_name, symbol, total_return FROM backtest_results;")
                        results = cursor.fetchall()
                        print("   回测结果:")
                        for result in results:
                            print(f"     策略: {result[0]}, 股票: {result[1]}, 收益率: {result[2]:.2%}")
                            
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")

if __name__ == "__main__":
    print("🔍 检查 finance_data.db 数据库内容\n")
    check_database()