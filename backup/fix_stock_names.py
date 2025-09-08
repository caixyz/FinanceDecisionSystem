#!/usr/bin/env python3
"""
修复股票名称和行业信息
"""

import sqlite3
import pandas as pd
import akshare as ak
import time
from datetime import datetime

def fix_stock_names_and_industries():
    """修复股票名称和行业信息"""
    
    print('🔧 开始修复股票名称和行业信息...')
    
    # 连接数据库
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 1. 获取股票代码列表
        print('\n📊 获取股票代码列表...')
        symbols = pd.read_sql('SELECT symbol FROM stock_info ORDER BY symbol', conn)['symbol'].tolist()
        print(f'需要处理 {len(symbols)} 只股票')
        
        # 2. 获取股票基本信息
        print('\n🔄 获取股票基本信息...')
        
        # 方法1：使用股票列表接口
        try:
            stock_list = ak.stock_info_a_code_name()
            if stock_list is not None and len(stock_list) > 0:
                # 创建股票信息映射
                stock_info_map = {}
                for _, row in stock_list.iterrows():
                    symbol = str(row['code']).zfill(6)
                    name = str(row['name'])
                    stock_info_map[symbol] = name
                
                print(f'成功获取 {len(stock_info_map)} 只股票名称')
                
                # 更新数据库
                updated_count = 0
                for symbol in symbols:
                    if symbol in stock_info_map:
                        name = stock_info_map[symbol]
                        cursor.execute('''
                            UPDATE stock_info 
                            SET name = ?, updated_at = ?
                            WHERE symbol = ?
                        ''', (name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
                        
                        if cursor.rowcount > 0:
                            updated_count += 1
                        
                        if updated_count % 100 == 0:
                            print(f'已更新 {updated_count} 条记录...')
                
                conn.commit()
                print(f'✅ 成功更新 {updated_count} 只股票名称')
                
        except Exception as e:
            print(f'❌ 获取股票名称失败: {e}')
        
        # 3. 更新行业信息（简化版本）
        print('\n🔄 更新行业信息...')
        
        # 使用股票基本信息获取行业
        try:
            # 分批处理，避免API限制
            batch_size = 50
            updated_industry = 0
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i+batch_size]
                
                for symbol in batch:
                    try:
                        # 获取个股基本信息
                        stock_info = ak.stock_individual_info_em(symbol=symbol)
                        if stock_info is not None and len(stock_info) > 0:
                            industry_row = stock_info[stock_info['item'] == '行业']
                            if not industry_row.empty:
                                industry = str(industry_row.iloc[0]['value'])
                                
                                cursor.execute('''
                                    UPDATE stock_info 
                                    SET industry = ?, updated_at = ?
                                    WHERE symbol = ?
                                ''', (industry, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), symbol))
                                
                                if cursor.rowcount > 0:
                                    updated_industry += 1
                    
                    except Exception as e:
                        # 如果个别股票获取失败，跳过继续
                        pass
                    
                    # 添加小延迟避免API限制
                    time.sleep(0.1)
                
                if i % 500 == 0:
                    conn.commit()
                    print(f'已处理 {i}/{len(symbols)} 只股票，更新行业 {updated_industry} 条')
            
            conn.commit()
            print(f'✅ 成功更新 {updated_industry} 只股票行业信息')
            
        except Exception as e:
            print(f'❌ 更新行业信息失败: {e}')
            # 使用默认行业
            cursor.execute('''
                UPDATE stock_info 
                SET industry = CASE 
                    WHEN symbol LIKE '6%' THEN '主板'
                    WHEN symbol LIKE '0%' THEN '中小板'
                    WHEN symbol LIKE '3%' THEN '创业板'
                    WHEN symbol LIKE '688%' THEN '科创板'
                    ELSE '其他'
                END
                WHERE industry IS NULL OR industry = '' OR industry = 'None'
            ''')
            conn.commit()
            print('✅ 使用默认行业分类更新')
        
        # 4. 验证修复结果
        print('\n📊 验证修复结果...')
        
        # 检查更新后的数据
        stats = pd.read_sql('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN name IS NOT NULL AND name != '' AND name != 'None' THEN 1 ELSE 0 END) as has_name,
                SUM(CASE WHEN industry IS NOT NULL AND industry != '' AND industry != 'None' THEN 1 ELSE 0 END) as has_industry,
                SUM(CASE WHEN market_cap > 0 THEN 1 ELSE 0 END) as has_market_cap
            FROM stock_info
        ''', conn)
        
        print('修复后统计：')
        print(stats.to_string(index=False))
        
        # 显示前10条数据
        sample = pd.read_sql('''
            SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at
            FROM stock_info 
            WHERE name IS NOT NULL AND name != '' AND name != 'None'
            ORDER BY symbol
            LIMIT 10
        ''', conn)
        
        print('\n修复后的数据示例：')
        print(sample.to_string(index=False))
        
    except Exception as e:
        print(f'❌ 修复过程出错: {e}')
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    fix_stock_names_and_industries()