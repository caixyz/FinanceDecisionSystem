#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复股票行业信息
使用AKShare获取真实行业分类并更新数据库
"""

import sys
import sqlite3
import pandas as pd
import akshare as ak
import time
from typing import Dict, Optional

sys.path.append('.')

class IndustryFixer:
    def __init__(self):
        self.db_path = 'data/finance_data.db'
        self.conn = sqlite3.connect(self.db_path)
        
    def get_real_industry_info(self, symbol: str) -> Optional[str]:
        """获取股票真实行业信息"""
        try:
            # 使用ak.stock_individual_info_em获取详细信息
            stock_info = ak.stock_individual_info_em(symbol=symbol)
            
            if not stock_info.empty:
                # 查找行业相关字段
                industry_col = None
                for col in stock_info['item']:
                    if '行业' in str(col) or 'industry' in str(col).lower():
                        industry_col = col
                        break
                
                if industry_col:
                    industry_value = stock_info[stock_info['item'] == industry_col]['value'].iloc[0]
                    return str(industry_value) if industry_value else None
                    
            return None
            
        except Exception as e:
            print(f"获取{symbol}行业信息失败: {e}")
            return None
    
    def update_industry_data(self, limit: int = None):
        """更新数据库中的行业信息"""
        try:
            # 获取当前股票列表
            if limit:
                query = f"SELECT symbol, name, industry FROM stock_info LIMIT {limit}"
            else:
                query = "SELECT symbol, name, industry FROM stock_info"
                
            df = pd.read_sql_query(query, self.conn)
            
            print(f"需要更新行业信息的股票数: {len(df)}")
            
            updated_count = 0
            
            for idx, row in df.iterrows():
                symbol = str(row['symbol']).zfill(6)
                current_industry = row['industry']
                
                # 获取真实行业信息
                real_industry = self.get_real_industry_info(symbol)
                
                if real_industry and real_industry != current_industry:
                    # 更新数据库
                    cursor = self.conn.cursor()
                    cursor.execute(
                        "UPDATE stock_info SET industry = ? WHERE symbol = ?",
                        (real_industry, symbol)
                    )
                    self.conn.commit()
                    
                    updated_count += 1
                    print(f"更新 {symbol} ({row['name']}) 行业: {current_industry} -> {real_industry}")
                    
                    # 避免请求过快
                    time.sleep(0.1)
                    
                elif updated_count % 100 == 0:
                    print(f"已处理 {idx+1}/{len(df)} 只股票...")
            
            print(f"完成！共更新 {updated_count} 只股票的行业信息")
            
        except Exception as e:
            print(f"更新行业信息失败: {e}")
            
    def check_industry_distribution(self):
        """检查行业分布"""
        try:
            query = "SELECT industry, COUNT(*) as count FROM stock_info GROUP BY industry ORDER BY count DESC"
            df = pd.read_sql_query(query, self.conn)
            
            print("\n行业分布统计:")
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"检查行业分布失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

if __name__ == "__main__":
    fixer = IndustryFixer()
    
    print("开始修复股票行业信息...")
    
    # 先检查当前行业分布
    fixer.check_industry_distribution()
    
    # 更新行业信息（先测试前10条）
    fixer.update_industry_data(limit=10)
    
    # 再次检查行业分布
    fixer.check_industry_distribution()
    
    fixer.close()
    print("修复完成！")