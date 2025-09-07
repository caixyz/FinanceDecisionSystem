#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看数据库表结构的完整信息
"""

import sqlite3
import os

def check_database_structure():
    """查看数据库中所有表的完整字段结构"""
    
    # 连接数据库
    db_path = os.path.join('data', 'finance_data.db')
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("数据库中没有任何表")
            return
        
        print('=== 数据库中的所有表 ===')
        for i, table in enumerate(tables, 1):
            print(f'{i}. {table[0]}')
        
        print()
        
        # 详细查看每个表的结构
        for table_name in tables:
            table_name = table_name[0]
            print(f'=== 表: {table_name} ===')
            
            # 获取表字段信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if columns:
                print('字段ID | 字段名           | 数据类型     | 是否必填 | 默认值 | 主键')
                print('-' * 75)
                for col in columns:
                    col_id, name, type_, notnull, default, pk = col
                    notnull_str = '是' if notnull else '否'
                    pk_str = '是' if pk else '否'
                    default_str = str(default) if default else 'None'
                    print(f'{col_id:6} | {name:16} | {type_:12} | {notnull_str:8} | {default_str:8} | {pk_str}')
                
                print(f'总字段数: {len(columns)} 个')
                
                # 获取索引信息
                cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = cursor.fetchall()
                if indexes:
                    print('\n索引信息:')
                    for idx in indexes:
                        idx_name, unique_, origin = idx
                        unique_str = '唯一' if unique_ else '非唯一'
                        print(f'  - {idx_name} ({unique_str})')
                
                # 获取数据条数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f'数据条数: {count:,} 条')
                
            else:
                print('该表无字段信息')
            
            print()
    
    except Exception as e:
        print(f"查询数据库时出错: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_structure()