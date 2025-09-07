#!/usr/bin/env python3
"""
修复测试股票的演示数据
为常用测试股票添加模拟的最新价格和财务指标
"""
import sqlite3
import pandas as pd
from datetime import datetime
import sys
import os

def fix_test_data():
    """修复测试股票的演示数据"""
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    # 测试股票数据
    test_stocks = {
        '000001': {'name': '平安银行', 'close': 11.25, 'pe_ratio': 6.8, 'pb_ratio': 0.85, 'market_cap': 2180.5, 'industry': '银行'},
        '000002': {'name': '万科A', 'close': 8.92, 'pe_ratio': 12.3, 'pb_ratio': 0.45, 'market_cap': 1056.8, 'industry': '房地产'},
        '000858': {'name': '五粮液', 'close': 145.67, 'pe_ratio': 18.5, 'pb_ratio': 3.2, 'market_cap': 5654.3, 'industry': '白酒'},
        '601398': {'name': '工商银行', 'close': 5.89, 'pe_ratio': 5.2, 'pb_ratio': 0.58, 'market_cap': 21045.6, 'industry': '银行'},
        '600519': {'name': '贵州茅台', 'close': 1625.88, 'pe_ratio': 25.8, 'pb_ratio': 9.5, 'market_cap': 20432.1, 'industry': '白酒'},
        '601288': {'name': '农业银行', 'close': 4.56, 'pe_ratio': 5.1, 'pb_ratio': 0.62, 'market_cap': 15943.2, 'industry': '银行'},
    }
    
    updated_count = 0
    
    for symbol, data in test_stocks.items():
        try:
            # 检查股票是否存在
            cursor.execute('SELECT symbol FROM stock_info WHERE symbol = ?', (symbol,))
            exists = cursor.fetchone()
            
            if exists:
                # 更新现有股票
                cursor.execute('''
                    UPDATE stock_info 
                    SET name = ?, close = ?, pe_ratio = ?, pb_ratio = ?, 
                        market_cap = ?, industry = ?, updated_at = ?
                    WHERE symbol = ?
                ''', (
                    data['name'], data['close'], data['pe_ratio'], 
                    data['pb_ratio'], data['market_cap'], data['industry'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol
                ))
            else:
                # 插入新股票
                cursor.execute('''
                    INSERT INTO stock_info (symbol, name, close, pe_ratio, pb_ratio, 
                                         market_cap, industry, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol, data['name'], data['close'], data['pe_ratio'],
                    data['pb_ratio'], data['market_cap'], data['industry'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
            
            updated_count += 1
            print(f"✅ 已更新 {symbol} - {data['name']}")
            
        except Exception as e:
            print(f"❌ 更新 {symbol} 时出错: {e}")
            continue
    
    conn.commit()
    
    # 显示更新结果
    cursor.execute('''
        SELECT symbol, name, close, pe_ratio, pb_ratio, market_cap, industry
        FROM stock_info 
        WHERE symbol IN ('000001', '000002', '000858', '601398', '600519', '601288')
        ORDER BY symbol
    ''')
    
    print("\n📊 更新后的测试股票数据:")
    print("代码\t名称\t\t收盘价\t市盈率\t市净率\t市值(亿)\t行业")
    print("-" * 80)
    for row in cursor.fetchall():
        symbol, name, close, pe, pb, cap, industry = row
        print(f"{symbol}\t{name}\t\t{close}\t{pe}\t{pb}\t{cap}\t{industry}")
    
    conn.close()
    print(f"\n🎉 共更新 {updated_count} 只测试股票")

if __name__ == "__main__":
    print("🔄 开始修复测试股票数据...")
    fix_test_data()