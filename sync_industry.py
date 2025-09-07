#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高效同步所有股票的行业信息
"""

import sys
import sqlite3
import pandas as pd
import akshare as ak
import time
from typing import Dict, Optional
import concurrent.futures
import threading

sys.path.append('.')

class IndustrySyncer:
    def __init__(self):
        self.db_path = 'data/finance_data.db'
        self.conn = sqlite3.connect(self.db_path)
        self.lock = threading.Lock()
        
    def get_industry_by_symbol_batch(self, symbols: list) -> Dict[str, str]:
        """批量获取股票行业信息"""
        industry_map = {}
        
        for symbol in symbols:
            try:
                # 使用个股详情接口获取行业信息
                stock_info = ak.stock_individual_info_em(symbol=symbol)
                
                if not stock_info.empty:
                    # 查找行业字段
                    for _, row in stock_info.iterrows():
                        if '行业' in str(row['item']):
                            industry = str(row['value'])
                            if industry and industry != 'nan':
                                industry_map[symbol] = industry
                                break
                
                # 避免请求过快
                time.sleep(0.1)
                
            except Exception as e:
                print(f"获取{symbol}行业信息失败: {e}")
                continue
                
        return industry_map
    
    def update_industries_efficiently(self):
        """高效更新所有股票的行业信息"""
        try:
            # 获取需要更新的股票列表
            query = """
            SELECT symbol, name, industry 
            FROM stock_info 
            WHERE industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所', '其他')
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            if df.empty:
                print("没有需要更新的股票行业信息")
                return
            
            print(f"需要更新行业信息的股票数: {len(df)}")
            
            # 分批处理，每批50只股票
            batch_size = 50
            total_updated = 0
            
            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i:i+batch_size]
                symbols = [str(row['symbol']).zfill(6) for _, row in batch_df.iterrows()]
                
                print(f"处理第 {i//batch_size + 1} 批，共 {len(symbols)} 只股票...")
                
                # 获取这批股票的行业信息
                industry_map = self.get_industry_by_symbol_batch(symbols)
                
                # 更新数据库
                with self.lock:
                    cursor = self.conn.cursor()
                    for symbol, industry in industry_map.items():
                        cursor.execute(
                            "UPDATE stock_info SET industry = ? WHERE symbol = ?",
                            (industry, symbol.lstrip('0'))
                        )
                    self.conn.commit()
                
                updated_in_batch = len(industry_map)
                total_updated += updated_in_batch
                
                print(f"本批更新 {updated_in_batch} 只股票，总计已更新 {total_updated} 只")
                
                # 批次间暂停
                if i + batch_size < len(df):
                    time.sleep(2)
            
            print(f"完成！共更新 {total_updated} 只股票的行业信息")
            
            # 显示更新后的行业分布
            self.show_industry_distribution()
            
        except Exception as e:
            print(f"更新行业信息失败: {e}")
            
    def show_industry_distribution(self):
        """显示行业分布"""
        try:
            query = """
            SELECT industry, COUNT(*) as count 
            FROM stock_info 
            GROUP BY industry 
            ORDER BY count DESC 
            LIMIT 20
            """
            df = pd.read_sql_query(query, self.conn)
            
            print("\n更新后的行业分布（前20）:")
            print(df.to_string(index=False))
            
            # 统计有真实行业的股票数量
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM stock_info 
                WHERE industry NOT IN ('上证主板', '深证主板', '创业板', '科创板', '北交所', '其他')
                AND industry IS NOT NULL
            """)
            real_industry_count = cursor.fetchone()[0]
            
            print(f"\n拥有真实行业信息的股票数: {real_industry_count}")
            
        except Exception as e:
            print(f"显示行业分布失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

if __name__ == "__main__":
    syncer = IndustrySyncer()
    
    print("开始同步股票真实行业信息...")
    
    # 先显示当前分布
    syncer.show_industry_distribution()
    
    # 开始同步
    syncer.update_industries_efficiently()
    
    syncer.close()
    print("行业信息同步完成！")