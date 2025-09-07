#!/usr/bin/env python3
"""
检查股票数据缺失情况
"""

import sqlite3
import pandas as pd

def check_data_missing():
    """检查数据缺失情况"""
    
    # 连接数据库
    conn = sqlite3.connect('data/finance_data.db')
    
    print('📊 stock_info表数据完整性检查：')
    print('=' * 50)
    
    # 获取总记录数
    total = pd.read_sql('SELECT COUNT(*) as total FROM stock_info', conn).iloc[0]['total']
    print(f'总记录数: {total:,}')
    
    # 检查各字段缺失情况
    fields = ['name', 'industry', 'market_cap', 'pe_ratio', 'pb_ratio', 'close']
    for field in fields:
        missing = pd.read_sql(f"SELECT COUNT(*) as missing FROM stock_info WHERE {field} IS NULL OR {field} = '' OR {field} = 0", conn).iloc[0]['missing']
        pct = (missing / total) * 100
        print(f'{field}: 缺失 {missing:,} 条 ({pct:.1f}%)')
    
    print('\n🔍 数据质量分析：')
    print('=' * 50)
    
    # 检查完全缺失的记录
    complete_missing = pd.read_sql('''
        SELECT COUNT(*) as count 
        FROM stock_info 
        WHERE (name IS NULL OR name = '') 
           OR (industry IS NULL OR industry = '')
           OR (market_cap IS NULL OR market_cap = 0)
           OR (close IS NULL OR close = 0)
    ''', conn).iloc[0]['count']
    print(f'关键字段完全缺失: {complete_missing:,} 条 ({(complete_missing/total)*100:.1f}%)')
    
    # 检查最近更新的数据
    print('\n📅 最近更新的数据：')
    recent_data = pd.read_sql('''
        SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at 
        FROM stock_info 
        WHERE updated_at IS NOT NULL
        ORDER BY updated_at DESC 
        LIMIT 10
    ''', conn)
    print(recent_data.to_string(index=False))
    
    # 检查未分类的股票
    print('\n🗂️  未分类股票示例：')
    uncategorized = pd.read_sql('''
        SELECT symbol, name, industry, market_cap, close, updated_at 
        FROM stock_info 
        WHERE industry IS NULL OR industry = '' 
        LIMIT 10
    ''', conn)
    print(uncategorized.to_string(index=False))
    
    # 检查是否有重复数据
    print('\n🔄 重复数据检查：')
    duplicates = pd.read_sql('''
        SELECT symbol, COUNT(*) as count
        FROM stock_info 
        GROUP BY symbol 
        HAVING COUNT(*) > 1
    ''', conn)
    if len(duplicates) > 0:
        print(f'发现重复股票代码: {len(duplicates)} 个')
        print(duplicates.to_string(index=False))
    else:
        print('未发现重复数据')
    
    conn.close()

if __name__ == "__main__":
    check_data_missing()