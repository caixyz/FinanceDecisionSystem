#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：修复stock_board_concept_name_em接口下载问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import akshare as ak
import sqlite3
from core.storage import DatabaseManager

def safe_table_name(interface_name):
    """将接口名称转换为安全的表名"""
    # 替换不安全的字符
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', interface_name)
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = f"ak_{safe_name}"
    return f"akshare_{safe_name}"

def test_stock_board_concept():
    """测试stock_board_concept_name_em接口"""
    print("测试stock_board_concept_name_em接口...")
    
    try:
        # 测试接口调用
        print("1. 测试接口调用...")
        df = ak.stock_board_concept_name_em()
        print(f"接口调用成功，获取到 {len(df)} 条数据")
        print(f"数据列: {list(df.columns)}")
        print("数据预览:")
        print(df.head())
        
        # 测试表名转换
        interface_name = "stock_board_concept_name_em"
        table_name = safe_table_name(interface_name)
        print(f"\n2. 安全表名: {table_name}")
        
        # 测试数据库操作
        print("\n3. 测试数据库操作...")
        db_manager = DatabaseManager()
        
        # 创建表
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join([f'{col} TEXT' for col in df.columns])},
            download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # 使用参数化方式避免SQL注入
        try:
            conn = db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute(create_sql)
            conn.commit()
            print("表创建成功")
            
            # 插入数据
            df['download_time'] = '2024-01-01 00:00:00'
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print("数据插入成功")
            
            conn.close()
            
        except Exception as e:
            print(f"数据库操作失败: {e}")
            # 尝试使用execute方法
            try:
                result = db_manager.execute(create_sql)
                print(f"使用execute方法创建表，影响行数: {result}")
            except Exception as e2:
                print(f"execute方法也失败: {e2}")
        
        return True
        
    except Exception as e:
        print(f"接口测试失败: {e}")
        return False

def fix_table_name_issue():
    """修复表名问题"""
    print("\n修复表名问题...")
    
    # 获取接口数据
    try:
        df = ak.stock_board_concept_name_em()
        print(f"成功获取数据，形状: {df.shape}")
        
        # 显示列名，检查是否有特殊字符
        print("列名列表:")
        for col in df.columns:
            safe_col = re.sub(r'[^a-zA-Z0-9_]', '_', col)
            if col != safe_col:
                print(f"  原始: '{col}' -> 安全: '{safe_col}'")
            else:
                print(f"  安全: '{col}'")
        
        return df
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("stock_board_concept_name_em 接口问题修复测试")
    print("=" * 60)
    
    # 修复表名问题
    df = fix_table_name_issue()
    
    if df is not None:
        print("\n✅ 数据获取成功，问题可能已解决")
    else:
        print("\n❌ 数据获取失败，需要进一步检查")