#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复主要股票的行业信息
"""

import sqlite3
import akshare as ak
import pandas as pd

# 主要股票代码列表
main_stocks = [
    '601398',  # 工商银行
    '000001',  # 平安银行
    '600036',  # 招商银行
    '601288',  # 农业银行
    '601988',  # 中国银行
    '000858',  # 五粮液
    '600519',  # 贵州茅台
    '000002',  # 万科A
    '600030',  # 中信证券
    '000651',  # 格力电器
]

def fix_industry_for_stock(symbol):
    """修复单个股票的行业信息"""
    try:
        # 获取真实行业信息
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        
        if not stock_info.empty:
            # 查找行业字段
            industry = None
            for _, row in stock_info.iterrows():
                if '行业' in str(row['item']):
                    industry = str(row['value'])
                    if industry and industry != 'nan':
                        break
            
            if industry:
                # 更新数据库
                conn = sqlite3.connect('data/finance_data.db')
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE stock_info SET industry = ? WHERE symbol = ?",
                    (industry, symbol.lstrip('0'))
                )
                conn.commit()
                
                # 获取股票名称
                cursor.execute("SELECT name FROM stock_info WHERE symbol = ?", (symbol.lstrip('0'),))
                name = cursor.fetchone()[0]
                
                conn.close()
                
                print(f"✅ 更新 {symbol} ({name}) 行业: {industry}")
                return True
                
    except Exception as e:
        print(f"❌ 更新{symbol}失败: {e}")
        return False

def main():
    print("开始修复主要股票的行业信息...")
    
    # 先显示当前信息
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    for symbol in main_stocks:
        cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE symbol = ?", (symbol.lstrip('0'),))
        result = cursor.fetchone()
        if result:
            print(f"当前: {result[0]} - {result[1]} - {result[2]}")
    
    conn.close()
    
    print("\n开始更新...")
    
    # 更新行业信息
    updated_count = 0
    for symbol in main_stocks:
        if fix_industry_for_stock(symbol):
            updated_count += 1
    
    print(f"\n完成！共更新 {updated_count} 只股票的行业信息")
    
    # 显示更新后的信息
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    print("\n更新后的信息:")
    for symbol in main_stocks:
        cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE symbol = ?", (symbol.lstrip('0'),))
        result = cursor.fetchone()
        if result:
            print(f"更新后: {result[0]} - {result[1]} - {result[2]}")
    
    conn.close()

if __name__ == "__main__":
    main()