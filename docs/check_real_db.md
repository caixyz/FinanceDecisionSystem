import sqlite3
import os
import pandas as pd

def check_real_database():
    """检查真实的数据库情况"""
    
    # 确保data目录存在
    os.makedirs('data', exist_ok=True)
    
    # 检查正确的数据库路径
    db_path = 'data/finance_data.db'
    print(f"=== 检查数据库: {db_path} ===")
    
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✅ 数据库文件存在，大小: {size} bytes")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"\n📊 数据库中的表 ({len(tables)}个):")
            
            for table in tables:
                table_name = table[0]
                print(f"\n📋 表: {table_name}")
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print("  字段结构:")
                for col in columns:
                    print(f"    {col[1]} ({col[2]})")
                
                # 获取数据量
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  数据量: {count} 条记录")
                
                # 获取数据样本
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    print("  数据样本:")
                    for row in rows:
                        print(f"    {row}")
            
            # 特别检查stock_info表的关键字段
            if 'stock_info' in [t[0] for t in tables]:
                print("\n=== 股票信息详情 ===")
                
                # 检查缺失字段
                cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE name IS NULL OR name = '' LIMIT 5")
                missing_names = cursor.fetchall()
                if missing_names:
                    print(f"❌ 缺失名称的股票: {len(missing_names)} 只")
                
                cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE industry IS NULL OR industry = '' OR industry = '未知' LIMIT 5")
                missing_industry = cursor.fetchall()
                if missing_industry:
                    print(f"❌ 缺失行业的股票: {len(missing_industry)} 只")
                
                # 检查数据完整性
                cursor.execute("SELECT COUNT(*) FROM stock_info WHERE close IS NULL OR close = 0")
                missing_close = cursor.fetchone()[0]
                print(f"❌ 缺失最新股价的股票: {missing_close} 只")
                
                cursor.execute("SELECT COUNT(*) FROM stock_info WHERE pe_ratio IS NULL OR pe_ratio = 0")
                missing_pe = cursor.fetchone()[0]
                print(f"❌ 缺失市盈率的股票: {missing_pe} 只")
                
                cursor.execute("SELECT COUNT(*) FROM stock_info WHERE pb_ratio IS NULL OR pb_ratio = 0")
                missing_pb = cursor.fetchone()[0]
                print(f"❌ 缺失市净率的股票: {missing_pb} 只")
                
                # 显示一些正常数据
                cursor.execute("SELECT symbol, name, industry, close, pe_ratio, pb_ratio, market_cap FROM stock_info WHERE close > 0 AND industry != '未知' LIMIT 5")
                good_data = cursor.fetchall()
                if good_data:
                    print("\n✅ 正常数据样本:")
                    for row in good_data:
                        print(f"  {row[0]} | {row[1]} | {row[2]} | 股价: {row[3]} | PE: {row[4]} | PB: {row[5]} | 市值: {row[6]}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
    else:
        print("❌ 数据库文件不存在，需要初始化")
        return False
    
    return True

if __name__ == "__main__":
    check_real_database()