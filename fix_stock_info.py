#!/usr/bin/env python3
"""
修复股票信息缺失问题
"""

import sqlite3
import pandas as pd
import akshare as ak
import time
from datetime import datetime

def fix_stock_info():
    """修复股票信息缺失"""
    
    print('🔧 开始修复股票信息缺失问题...')
    
    # 连接数据库
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 1. 检查缺失的股票信息
        print('\n📊 检查缺失的股票信息...')
        missing_stocks = pd.read_sql('''
            SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at
            FROM stock_info 
            WHERE (name IS NULL OR name = '' OR name = 'None')
               OR (industry IS NULL OR industry = '' OR industry = 'None')
               OR (market_cap IS NULL OR market_cap = 0)
               OR (close IS NULL OR close = 0)
            ORDER BY symbol
        ''', conn)
        
        print(f'发现 {len(missing_stocks)} 条缺失信息的股票记录')
        
        if len(missing_stocks) > 0:
            print('\n📋 缺失信息示例：')
            print(missing_stocks.head(10).to_string(index=False))
        
        # 2. 获取完整的股票列表信息
        print('\n🔄 获取完整的股票列表信息...')
        try:
            # 获取A股股票列表
            stock_list_df = ak.stock_info_a_code_name()
            
            if stock_list_df is not None and len(stock_list_df) > 0:
                # 重命名列以匹配数据库
                stock_list_df = stock_list_df.rename(columns={
                    'code': 'symbol',
                    'name': 'name'
                })
                
                # 获取行业信息
                print('\n🔄 获取行业信息...')
                industry_map = {}
                
                # 分批获取行业信息，避免API限制
                batch_size = 50
                symbols = stock_list_df['symbol'].tolist()
                
                for i in range(0, len(symbols), batch_size):
                    batch_symbols = symbols[i:i+batch_size]
                    
                    for symbol in batch_symbols:
                        try:
                            # 获取个股信息
                            stock_info = ak.stock_individual_info_em(symbol=symbol)
                            if stock_info is not None and len(stock_info) > 0:
                                industry = stock_info.loc[stock_info['item'] == '行业', 'value'].iloc[0] if '行业' in stock_info['item'].values else ''
                                industry_map[symbol] = industry
                        except Exception as e:
                            print(f'获取 {symbol} 行业信息失败: {e}')
                        
                        # 添加延迟避免API限制
                        time.sleep(0.1)
                    
                    if i % 500 == 0:
                        print(f'已处理 {i}/{len(symbols)} 只股票...')
                
                # 3. 更新数据库
                print('\n🔄 更新数据库...')
                updated_count = 0
                
                for _, row in stock_list_df.iterrows():
                    symbol = str(row['symbol']).zfill(6)
                    name = str(row['name'])
                    industry = industry_map.get(symbol, '其他')
                    
                    # 更新股票信息
                    cursor.execute('''
                        UPDATE stock_info 
                        SET name = ?, industry = ?, updated_at = ?
                        WHERE symbol = ? AND (name IS NULL OR name = '' OR name = 'None')
                    ''', (name, industry, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                    
                    if updated_count % 100 == 0:
                        print(f'已更新 {updated_count} 条记录...')
                
                conn.commit()
                print(f'✅ 成功更新 {updated_count} 条股票信息')
                
                # 4. 验证修复结果
                print('\n📊 验证修复结果...')
                after_fix = pd.read_sql('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN name IS NULL OR name = '' OR name = 'None' THEN 1 ELSE 0 END) as missing_name,
                        SUM(CASE WHEN industry IS NULL OR industry = '' OR industry = 'None' THEN 1 ELSE 0 END) as missing_industry,
                        SUM(CASE WHEN market_cap IS NULL OR market_cap = 0 THEN 1 ELSE 0 END) as missing_market_cap
                    FROM stock_info
                ''', conn)
                
                print('修复后统计：')
                print(after_fix.to_string(index=False))
                
            else:
                print('❌ 无法获取股票列表信息')
                
        except Exception as e:
            print(f'❌ 获取股票信息时出错: {e}')
            # 使用备用方法获取部分信息
            print('尝试使用备用方法...')
            
            # 获取股票基本信息
            try:
                basic_info = ak.stock_info_a_code_name()
                if basic_info is not None and len(basic_info) > 0:
                    basic_info = basic_info.rename(columns={'code': 'symbol', 'name': 'name'})
                    
                    updated_count = 0
                    for _, row in basic_info.iterrows():
                        symbol = str(row['symbol']).zfill(6)
                        name = str(row['name'])
                        
                        cursor.execute('''
                            UPDATE stock_info 
                            SET name = ?, industry = '其他', updated_at = ?
                            WHERE symbol = ? AND (name IS NULL OR name = '' OR name = 'None')
                        ''', (name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                    
                    conn.commit()
                    print(f'✅ 使用备用方法更新 {updated_count} 条记录')
                    
            except Exception as e2:
                print(f'❌ 备用方法也失败: {e2}')
        
    except Exception as e:
        print(f'❌ 修复过程出错: {e}')
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_stock_info()