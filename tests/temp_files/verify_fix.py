#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据修复结果
"""
import sqlite3

def verify_fix():
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    print("🎯 数据修复验证结果:")
    print("=" * 50)
    
    # 1. 验证菜百股份
    print("\n1. 菜百股份验证:")
    cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE symbol = '605599'")
    result = cursor.fetchone()
    if result:
        print(f"   ✅ {result[0]} - {result[1]} - 行业: {result[2]}")
    else:
        print("   ❌ 未找到菜百股份")
    
    # 2. 验证重要股票的行业分类
    print("\n2. 重要股票行业验证:")
    important_stocks = [
        ('601398', '工商银行', '银行'),
        ('600036', '招商银行', '银行'),
        ('600519', '贵州茅台', '酿酒行业'),
        ('600030', '中信证券', '证券'),
        ('601318', '中国平安', '保险'),
    ]
    
    for symbol, name, expected_industry in important_stocks:
        cursor.execute("SELECT industry FROM stock_info WHERE symbol = ?", (symbol,))
        result = cursor.fetchone()
        if result:
            actual_industry = result[0]
            status = "✅" if actual_industry == expected_industry else "❌"
            print(f"   {status} {symbol} - {name}: {actual_industry}")
        else:
            print(f"   ❌ {symbol} - {name}: 未找到")
    
    # 3. 统计行业分布
    print("\n3. 修复后的行业分布:")
    cursor.execute("""
        SELECT industry, COUNT(*) as count
        FROM stock_info 
        WHERE industry NOT IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        AND industry IS NOT NULL AND industry != ''
        GROUP BY industry
        ORDER BY count DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    for industry, count in results:
        print(f"   {industry}: {count}只股票")
    
    # 4. 统计剩余市场板块数据
    print("\n4. 剩余市场板块统计:")
    cursor.execute("""
        SELECT industry, COUNT(*) as count
        FROM stock_info 
        WHERE industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        GROUP BY industry
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    for industry, count in results:
        print(f"   {industry}: {count}只股票 (待修复)")
    
    conn.close()
    print("\n🎉 验证完成！")

if __name__ == "__main__":
    verify_fix()