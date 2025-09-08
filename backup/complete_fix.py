#!/usr/bin/env python3
"""
完整修复股票信息数据
"""

import sqlite3
import pandas as pd
import akshare as ak
import time
from datetime import datetime

def complete_stock_info_fix():
    """完整修复股票信息数据"""
    
    print('🔄 开始完整修复股票信息数据...')
    
    # 连接数据库
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 1. 清空现有数据
        print('\n🗑️ 清空现有股票信息...')
        cursor.execute('DELETE FROM stock_info')
        conn.commit()
        print('✅ 已清空现有数据')
        
        # 2. 获取股票基本信息
        print('\n📊 获取股票基本信息...')
        stock_list = ak.stock_info_a_code_name()
        print(f'获取到 {len(stock_list)} 只股票')
        
        # 3. 获取股票实时数据
        print('\n📈 获取股票实时数据...')
        stock_spot = ak.stock_zh_a_spot()
        print(f'获取到 {len(stock_spot)} 条实时数据')
        
        # 4. 创建数据映射
        spot_map = {}
        for _, row in stock_spot.iterrows():
            symbol = str(row['代码']).zfill(6)
            try:
                # 转换数值
                market_cap = float(row['总市值']) * 10000 if pd.notna(row['总市值']) else 0
                pe = float(row['市盈率']) if pd.notna(row['市盈率']) and str(row['市盈率']).replace('.', '').replace('-', '').isdigit() else 0
                pb = float(row['市净率']) if pd.notna(row['市净率']) and str(row['市净率']).replace('.', '').replace('-', '').isdigit() else 0
                close = float(row['最新价']) if pd.notna(row['最新价']) else 0
                
                spot_map[symbol] = {
                    'close': close,
                    'market_cap': market_cap,
                    'pe_ratio': pe,
                    'pb_ratio': pb
                }
            except (ValueError, TypeError):
                continue
        
        # 5. 批量插入数据
        print('\n💾 开始批量插入数据...')
        inserted = 0
        
        for _, row in stock_list.iterrows():
            symbol = str(row['code']).zfill(6)
            name = str(row['name'])
            
            # 获取实时数据
            spot_data = spot_map.get(symbol, {
                'close': 0,
                'market_cap': 0,
                'pe_ratio': 0,
                'pb_ratio': 0
            })
            
            # 插入数据
            cursor.execute('''
                INSERT INTO stock_info (symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                name,
                '未分类',
                spot_data['market_cap'],
                spot_data['pe_ratio'],
                spot_data['pb_ratio'],
                spot_data['close'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            inserted += 1
            
            if inserted % 100 == 0:
                print(f'已插入 {inserted} 条记录...')
        
        conn.commit()
        print(f'✅ 成功插入 {inserted} 条完整股票信息')
        
        # 6. 验证结果
        print('\n📊 验证修复结果...')
        
        # 统计信息
        stats = pd.read_sql('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN name IS NOT NULL AND name != '' THEN 1 ELSE 0 END) as has_name,
                SUM(CASE WHEN market_cap > 0 THEN 1 ELSE 0 END) as has_market_cap,
                SUM(CASE WHEN pe_ratio != 0 THEN 1 ELSE 0 END) as has_pe,
                SUM(CASE WHEN pb_ratio != 0 THEN 1 ELSE 0 END) as has_pb
            FROM stock_info
        ''', conn)
        
        print('数据完整性统计：')
        print(stats.to_string(index=False))
        
        # 显示前20条数据
        sample = pd.read_sql('''
            SELECT symbol, name, market_cap, pe_ratio, pb_ratio, close
            FROM stock_info 
            ORDER BY market_cap DESC
            LIMIT 20
        ''', conn)
        
        print('\n💰 市值最大的20只股票：')
        print(sample.to_string(index=False))
        
        # 显示行业分布
        industry_stats = pd.read_sql('''
            SELECT industry, COUNT(*) as count
            FROM stock_info
            GROUP BY industry
            ORDER BY count DESC
        ''', conn)
        
        print('\n📊 行业分布：')
        print(industry_stats.to_string(index=False))
        
    except Exception as e:
        print(f'❌ 修复失败: {e}')
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    complete_stock_info_fix()