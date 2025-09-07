#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库路径和连接
"""
import os
import sqlite3
from pathlib import Path

def check_db_path():
    """检查数据库路径"""
    
    print("🔍 检查数据库路径...")
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 检查数据库文件
    db_path = os.path.join(current_dir, 'finance_data.db')
    print(f"💾 数据库文件路径: {db_path}")
    
    if os.path.exists(db_path):
        print("✅ 数据库文件存在")
        
        # 获取文件大小
        size = os.path.getsize(db_path)
        print(f"📊 文件大小: {size} bytes")
        
        # 检查文件是否为空
        if size == 0:
            print("⚠️  数据库文件为空")
            return False
        
        # 连接数据库
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"📋 数据库中的表 ({len(tables)} 个):")
            for table in tables:
                table_name = table[0]
                print(f"  - {table_name}")
                
                # 获取表结构
                try:
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    print(f"    列数: {len(columns)}")
                except Exception as e:
                    print(f"    ❌ 获取表结构失败: {e}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    else:
        print("❌ 数据库文件不存在")
        return False

def check_relative_paths():
    """检查相对路径"""
    print("\n🔍 检查相对路径...")
    
    # 检查当前目录
    print(f"📁 当前目录内容:")
    files = os.listdir('.')
    db_files = [f for f in files if f.endswith('.db')]
    print(f"  数据库文件: {db_files}")
    
    # 检查上级目录
    parent_dir = os.path.dirname(current_dir)
    if parent_dir != current_dir:
        print(f"📁 上级目录: {parent_dir}")
        parent_files = os.listdir(parent_dir)
        parent_db_files = [f for f in parent_files if f.endswith('.db')]
        print(f"  上级目录数据库文件: {parent_db_files}")

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    success = check_db_path()
    check_relative_paths()
    
    if not success:
        print("\n💡 建议检查:")
        print("1. 数据库文件是否在正确的目录")
        print("2. 是否有其他路径的数据库文件")
        print("3. 数据库是否已正确初始化")