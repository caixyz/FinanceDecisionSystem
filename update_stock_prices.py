#!/usr/bin/env python3
"""
更新股票最新价格和财务指标
从历史数据中提取最新价格并更新到stock_info表
"""
import sqlite3
import pandas as pd
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_stock_prices():
    """更新股票最新价格到stock_info表"""
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 获取所有股票代码
        cursor.execute('SELECT symbol FROM stock_info')
        symbols = [row[0] for row in cursor.fetchall()]
        
        updated_count = 0
        
        for symbol in symbols:
            try:
                # 从历史数据获取最新价格
                cursor.execute('''
                    SELECT close, volume, date 
                    FROM stock_daily_data 
                    WHERE symbol = ? 
                    ORDER BY date DESC 
                    LIMIT 1
                ''', (symbol,))
                
                latest_data = cursor.fetchone()
                if latest_data:
                    close_price, volume, latest_date = latest_data
                    
                    # 更新stock_info表的最新价格
                    cursor.execute('''
                        UPDATE stock_info 
                        SET close = ?, volume = ?, updated_at = ?
                        WHERE symbol = ?
                    ''', (close_price, volume, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
                    
                    updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f"已更新 {updated_count} 只股票的价格信息...")
                        
            except Exception as e:
                print(f"更新股票 {symbol} 价格时出错: {e}")
                continue
        
        conn.commit()
        print(f"✅ 价格更新完成，共更新 {updated_count} 只股票")
        
        # 显示更新后的样本
        cursor.execute('''
            SELECT symbol, name, close, industry, updated_at 
            FROM stock_info 
            WHERE close IS NOT NULL 
            LIMIT 10
        ''')
        
        print("\n📊 更新后的样本数据:")
        for row in cursor.fetchall():
            print(f"  {row[0]} - {row[1]}: 收盘价 {row[2]}, 行业: {row[3]}")
            
    except Exception as e:
        print(f"❌ 更新过程出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 开始更新股票最新价格信息...")
    update_stock_prices()