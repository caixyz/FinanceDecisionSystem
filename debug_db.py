import sqlite3
import os
import pandas as pd

def debug_database():
    """调试数据库问题"""
    
    # 检查当前目录的.db文件
    print("=== 数据库文件检查 ===")
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    if db_files:
        for db_file in db_files:
            size = os.path.getsize(db_file)
            print(f"找到数据库文件: {db_file} (大小: {size} bytes)")
    else:
        print("未找到数据库文件")
        return
    
    # 检查finance_data.db
    db_path = 'finance_data.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"\n=== 数据库中的表 ({len(tables)}个) ===")
            for table in tables:
                table_name = table[0]
                print(f"\n表: {table_name}")
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                print("字段:")
                for col in columns:
                    print(f"  {col[1]}: {col[2]}")
                
                # 获取数据样本
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    if rows:
                        print("数据样本:")
                        for row in rows:
                            print(f"  {row}")
                    else:
                        print("该表无数据")
                except Exception as e:
                    print(f"读取数据失败: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"数据库连接失败: {e}")

if __name__ == "__main__":
    debug_database()