#!/usr/bin/env python3
"""
AKShare接口表初始化脚本
将AKShare接口表结构导入到现有数据库中
"""

import sqlite3
import os
from pathlib import Path

def init_akshare_tables():
    """初始化AKShare接口表到现有数据库"""
    
    # 数据库路径
    db_path = os.path.join('data', 'finance_data.db')
    
    # SQL文件路径
    sql_file = os.path.join('docs', 'akshare_interface_schema.sql')
    
    print(f"正在连接到数据库: {db_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("正在执行SQL脚本...")
        
        # 执行SQL脚本
        cursor.executescript(sql_content)
        
        # 提交事务
        conn.commit()
        
        print("✅ AKShare接口表已成功创建到数据库中")
        
        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'akshare_%'")
        tables = cursor.fetchall()
        
        print(f"创建的AKShare相关表数量: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查示例数据
        cursor.execute("SELECT COUNT(*) FROM akshare_interfaces")
        count = cursor.fetchone()[0]
        print(f"已插入的接口数据数量: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_akshare_tables()