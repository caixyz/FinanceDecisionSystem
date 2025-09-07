#!/usr/bin/env python3
import sqlite3

# 检查当前行业信息
conn = sqlite3.connect('data/finance_data.db')
cursor = conn.cursor()

# 检查主要股票的行业信息
cursor.execute("SELECT symbol, name, industry FROM stock_info WHERE symbol IN ('601398', '600036', '600519', '600030')")
results = cursor.fetchall()
print('数据库中的行业信息:')
for row in results:
    print(f'  {row[0]} - {row[1]} - {row[2]}')

# 检查行业分布统计
cursor.execute("SELECT industry, COUNT(*) as count FROM stock_info GROUP BY industry ORDER BY count DESC LIMIT 10")
industry_stats = cursor.fetchall()
print('\n行业分布统计(前10):')
for industry, count in industry_stats:
    print(f'  {industry}: {count}')

conn.close()