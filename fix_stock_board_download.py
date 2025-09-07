#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复stock_board_concept_name_em接口下载问题的完整解决方案
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import re
import sqlite3
import pandas as pd
from datetime import datetime
from core.storage import DatabaseManager

def safe_table_name(interface_name):
    """生成安全的表名"""
    # 替换所有不安全字符为下划线
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', str(interface_name))
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = f'_{safe_name}'
    return f"akshare_{safe_name}"

def safe_column_name(column_name, index=None):
    """生成安全的列名"""
    # 移除或替换特殊字符，但保留部分中文特征
    safe_name = str(column_name)
    
    # 替换常见特殊字符
    safe_name = safe_name.replace('-', '_dash_')
    safe_name = safe_name.replace(' ', '_')
    safe_name = safe_name.replace('(', '_')
    safe_name = safe_name.replace(')', '_')
    safe_name = safe_name.replace('/', '_')
    safe_name = safe_name.replace('\\', '_')
    safe_name = safe_name.replace('%', '_pct_')
    
    # 使用拼音或英文缩写映射
    mapping = {
        '排名': 'rank',
        '板块名称': 'board_name',
        '板块代码': 'board_code', 
        '最新价': 'latest_price',
        '涨跌额': 'change_amount',
        '涨跌幅': 'change_percent',
        '总市值': 'total_market_cap',
        '换手率': 'turnover_rate',
        '上涨家数': 'up_count',
        '下跌家数': 'down_count',
        '领涨股票': 'leading_stock',
        '领涨股票-涨跌幅': 'leading_stock_change'
    }
    
    if safe_name in mapping:
        return mapping[safe_name]
    
    # 如果没有映射，使用索引确保唯一性
    if index is not None:
        return f"col_{index}"
    
    # 最后的清理
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)
    if not safe_name or safe_name[0].isdigit():
        safe_name = f'col_{safe_name}'
    
    return safe_name

def download_stock_board_concept():
    """下载并存储stock_board_concept_name_em数据"""
    print("开始下载stock_board_concept_name_em数据...")
    
    try:
        import akshare as ak
        
        # 获取数据
        print("1. 获取接口数据...")
        df = ak.stock_board_concept_name_em()
        print(f"获取到 {len(df)} 条数据，{len(df.columns)} 列")
        
        # 显示原始列名
        print("原始列名:")
        for i, col in enumerate(df.columns):
            print(f"  {i+1}. '{col}'")
        
        # 创建安全列名映射
        column_mapping = {}
        safe_columns = []
        for i, col in enumerate(df.columns):
            safe_col = safe_column_name(col, i)
            column_mapping[col] = safe_col
            safe_columns.append(safe_col)
        
        print("\n安全列名映射:")
        for original, safe in column_mapping.items():
            print(f"  '{original}' -> '{safe}'")
        
        # 重命名DataFrame列
        df_renamed = df.rename(columns=column_mapping)
        
        # 生成安全表名
        interface_name = "stock_board_concept_name_em"
        table_name = safe_table_name(interface_name)
        print(f"\n2. 表名: {table_name}")
        
        # 连接数据库
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()
        
        # 添加下载时间
        df_renamed['download_time'] = datetime.now()
        
        # 使用pandas的to_sql方法（自动处理列名问题）
        print("3. 存储到数据库...")
        df_renamed.to_sql(
            table_name, 
            conn, 
            if_exists='replace', 
            index=False,
            method='multi'
        )
        
        # 验证数据存储
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()[0]
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        print(f"\n4. 验证结果:")
        print(f"   存储记录数: {count}")
        print(f"   表列数: {len(columns_info)}")
        print("   存储列名:")
        for col in columns_info:
            print(f"     {col[1]} ({col[2]})")
        
        conn.close()
        
        print(f"\n✅ 数据下载和存储成功！")
        print(f"表名: {table_name}")
        print(f"记录数: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_safe_naming():
    """测试安全命名函数"""
    print("测试安全命名函数...")
    
    test_cases = [
        "stock_board_concept_name_em",
        "排名",
        "板块名称",
        "板块代码",
        "最新价",
        "涨跌额",
        "涨跌幅",
        "总市值",
        "换手率",
        "上涨家数",
        "下跌家数",
        "领涨股票",
        "领涨股票-涨跌幅"
    ]
    
    print("表名测试:")
    for name in test_cases:
        safe = safe_table_name(name)
        print(f"  {name} -> {safe}")
    
    print("\n列名测试:")
    for name in test_cases:
        safe = safe_column_name(name)
        print(f"  '{name}' -> '{safe}'")

if __name__ == "__main__":
    print("=" * 70)
    print("stock_board_concept_name_em 接口问题修复")
    print("=" * 70)
    
    # 测试命名函数
    test_safe_naming()
    
    print("\n" + "=" * 70)
    
    # 执行下载
    success = download_stock_board_concept()
    
    if success:
        print("\n🎉 修复完成！数据已成功下载并存储到数据库")
    else:
        print("\n💥 修复失败，请检查错误信息")