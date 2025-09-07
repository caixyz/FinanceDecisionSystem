#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import akshare as ak

# 检查工商银行信息
conn = sqlite3.connect('data/finance_data.db')
cursor = conn.cursor()

cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE symbol='601398' OR name LIKE '%工商银行%'")
result = cursor.fetchone()
print('工商银行当前信息:', result)

# 获取真实行业信息
symbol = '601398'
try:
    stock_info = ak.stock_individual_info_em(symbol=symbol)
    print("\n工商银行详细信息:")
    for _, row in stock_info.iterrows():
        if '行业' in str(row['item']):
            print(f"{row['item']}: {row['value']}")
            
    # 显示所有信息
    print("\n所有信息:")
    print(stock_info.to_string(index=False))
    
except Exception as e:
    print(f"获取工商银行信息失败: {e}")

conn.close()