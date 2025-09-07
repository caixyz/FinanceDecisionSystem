#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""
import sqlite3
import os

def check_database():
    """检查数据库和表结构"""
    
    # 检查数据库文件
    if not os.path.exists('finance_data.db'):
        print("❌ 数据库文件 finance_data.db 不存在")
        return
    
    print("✅ 数据库文件存在")
    
    # 连接数据库
    conn = sqlite3.connect('finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    {col[1]}: {col[2]}")
            print()
            
            # 获取前3条数据
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                if rows:
                    print(f"    📋 前3条数据:")
                    for row in rows:
                        print(f"      {row}")
                    print()
            except Exception as e:
                print(f"    ❌ 查询数据失败: {e}")
    
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()