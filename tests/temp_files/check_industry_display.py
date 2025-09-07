#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查股票行业信息在前端显示是否正确
"""

import sqlite3
import json
import requests
from datetime import datetime

def check_industry_display():
    """检查行业信息显示"""
    print("=" * 60)
    print("检查股票行业信息在前端显示")
    print("=" * 60)
    
    # 连接数据库
    conn = sqlite3.connect('finance_data.db')
    cursor = conn.cursor()
    
    # 检查主要股票的行业信息
    test_stocks = [
        '601398',  # 工商银行
        '600036',  # 招商银行
        '600519',  # 贵州茅台
        '600030',  # 中信证券
        '000858',  # 五粮液
        '000001',  # 平安银行
    ]
    
    print("\n数据库中的行业信息：")
    print("-" * 40)
    
    for symbol in test_stocks:
        cursor.execute("SELECT symbol, name, industry, updated_at FROM stock_info WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        if result:
            print(f"{result[0]} - {result[1]}: {result[2]} (更新于: {result[3]})")
        else:
            print(f"{symbol}: 未找到")
    
    # 检查行业分布
    print("\n\n行业分布统计：")
    print("-" * 40)
    
    cursor.execute("""
        SELECT industry, COUNT(*) as count 
        FROM stock_info 
        WHERE industry IS NOT NULL AND industry != '' 
        GROUP BY industry 
        ORDER BY count DESC 
        LIMIT 15
    """)
    
    industries = cursor.fetchall()
    for industry, count in industries:
        print(f"{industry}: {count} 只股票")
    
    conn.close()
    
    print("\n\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    check_industry_display()