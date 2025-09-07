#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终数据库检查
"""
import sqlite3
import os

def check_db(db_path):
    """检查指定路径的数据库"""
    print(f"\n🔍 检查数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ 文件不存在")
        return False
    
    size = os.path.getsize(db_path)
    print(f"✅ 文件存在, 大小: {size} bytes")
    
    if size == 0:
        print("⚠️  文件为空")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 表数量: {len(tables)}")
        stock_tables = []
        
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 检查是否为股票相关表
            if 'stock' in table_name.lower():
                stock_tables.append(table_name)
                
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print(f"    列数: {len(columns)}")
            
            # 获取数据量
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"    数据量: {count}")
        
        if stock_tables:
            print(f"\n📈 股票相关表: {stock_tables}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return False

if __name__ == "__main__":
    # 检查两个可能的数据库文件
    current_dir = os.getcwd()
    
    # 1. 当前目录的finance_data.db
    db1 = "finance_data.db"
    print("=" * 50)
    print("检查当前目录的数据库")
    check_db(db1)
    
    # 2. data目录的finance_data.db
    db2 = "data/finance_data.db"
    print("=" * 50)
    print("检查data目录的数据库")
    check_db(db2)
    
    print("\n" + "=" * 50)
    print("💡 总结:")
    print("- 配置文件中的路径: data/finance_data.db")
    print("- 实际使用的应该是: data/finance_data.db")
    print("- 当前目录的finance_data.db可能是空的")