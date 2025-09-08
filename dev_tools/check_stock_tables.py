#!/usr/bin/env python3
"""
检查股票数据相关表结构
"""

import sqlite3
import os

def check_stock_tables():
    """检查股票数据表"""
    
    # 连接数据库
    db_path = 'data/finance_data.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('📊 股票数据相关表：')
    print('=' * 60)
    
    # 查看所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = cursor.fetchall()
    
    stock_tables = []
    for table in all_tables:
        table_name = table[0]
        if 'stock' in table_name.lower() or 'akshare' in table_name.lower():
            stock_tables.append(table_name)
    
    for table_name in stock_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f'📈 {table_name}: {count:,} 条记录')
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if len(columns) <= 5:
                field_names = [col[1] for col in columns]
                print(f'   字段: {", ".join(field_names)}')
            else:
                field_names = [col[1] for col in columns[:5]]
                print(f'   字段: {", ".join(field_names)}...')
            print()
            
        except Exception as e:
            print(f'❌ {table_name}: 查询错误 - {e}')
    
    # 查看核心表
    print('\n🔍 核心股票数据表详情：')
    print('=' * 60)
    
    core_tables = [
        'stock_info',
        'akshare_stock_zh_a_spot',
        'akshare_stock_zh_a_hist',
        'akshare_stock_individual_info_em'
    ]
    
    for table_name in core_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f'\n📋 {table_name} ({count:,} 条记录):')
            for col in columns:
                col_name, col_type, _, _, _, _ = col
                print(f'   {col_name}: {col_type}')
                
        except Exception as e:
            print(f'❌ {table_name}: 不存在')
    
    conn.close()

if __name__ == "__main__":
    check_stock_tables()