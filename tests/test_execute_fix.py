#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证DatabaseManager.execute()方法修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.storage import DatabaseManager
import sqlite3

def test_execute_method():
    """测试DatabaseManager.execute()方法"""
    print("测试DatabaseManager.execute()方法...")
    
    try:
        db_manager = DatabaseManager()
        
        # 测试1: 创建测试表
        print("测试1: 创建测试表")
        create_sql = """
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value INTEGER DEFAULT 0
        )
        """
        result = db_manager.execute(create_sql)
        print(f"创建表成功，影响行数: {result}")
        
        # 测试2: 插入数据
        print("测试2: 插入数据")
        insert_sql = "INSERT INTO test_table (name, value) VALUES (?, ?)"
        result = db_manager.execute(insert_sql, ("测试1", 100))
        print(f"插入数据成功，影响行数: {result}")
        
        # 测试3: 更新数据
        print("测试3: 更新数据")
        update_sql = "UPDATE test_table SET value = ? WHERE name = ?"
        result = db_manager.execute(update_sql, (200, "测试1"))
        print(f"更新数据成功，影响行数: {result}")
        
        # 测试4: 删除数据
        print("测试4: 删除数据")
        delete_sql = "DELETE FROM test_table WHERE name = ?"
        result = db_manager.execute(delete_sql, ("测试1",))
        print(f"删除数据成功，影响行数: {result}")
        
        # 测试5: 清理测试表
        print("测试5: 清理测试表")
        drop_sql = "DROP TABLE IF EXISTS test_table"
        result = db_manager.execute(drop_sql)
        print(f"删除表成功，影响行数: {result}")
        
        print("所有测试通过！DatabaseManager.execute()方法工作正常")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_connection_method():
    """测试DatabaseManager.get_connection()方法"""
    print("\n测试DatabaseManager.get_connection()方法...")
    
    try:
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        
        # 测试连接是否正常
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("数据库连接测试通过")
            conn.close()
            return True
        else:
            print("数据库连接测试失败")
            conn.close()
            return False
            
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("数据库方法修复验证测试")
    print("=" * 50)
    
    success1 = test_execute_method()
    success2 = test_connection_method()
    
    if success1 and success2:
        print("\n✅ 所有测试通过！数据库方法修复成功")
    else:
        print("\n❌ 测试失败，请检查错误信息")