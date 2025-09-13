#!/usr/bin/env python3
"""
基于本地已有数据同步股票信息
"""
import sys
import os
sys.path.append('core')

from core.storage import DatabaseManager
import pandas as pd
from datetime import datetime

def sync_local_stocks():
    """基于已有股票代码同步基本信息"""
    print("=== 开始同步本地股票数据 ===")
    
    db = DatabaseManager()
    
    # 获取当前股票列表
    current_stocks = db.get_stock_list()
    print(f"当前数据库中已有 {len(current_stocks)} 只股票")
    
    # 创建示例股票数据（基于常见的A股股票）
    sample_stocks = [
        {'symbol': '000001', 'name': '平安银行', 'industry': '银行'},
        {'symbol': '000002', 'name': '万科A', 'industry': '房地产'},
        {'symbol': '000858', 'name': '五粮液', 'industry': '白酒'},
        {'symbol': '600519', 'name': '贵州茅台', 'industry': '白酒'},
        {'symbol': '601398', 'name': '工商银行', 'industry': '银行'},
        {'symbol': '601288', 'name': '农业银行', 'industry': '银行'},
        {'symbol': '000333', 'name': '美的集团', 'industry': '家电'},
        {'symbol': '002415', 'name': '海康威视', 'industry': '安防'},
        {'symbol': '600036', 'name': '招商银行', 'industry': '银行'},
        {'symbol': '601318', 'name': '中国平安', 'industry': '保险'},
        {'symbol': '600000', 'name': '浦发银行', 'industry': '银行'},
        {'symbol': '601166', 'name': '兴业银行', 'industry': '银行'},
        {'symbol': '000651', 'name': '格力电器', 'industry': '家电'},
        {'symbol': '002594', 'name': '比亚迪', 'industry': '汽车'},
        {'symbol': '300750', 'name': '宁德时代', 'industry': '新能源'},
        {'symbol': '600031', 'name': '三一重工', 'industry': '工程机械'},
        {'symbol': '600887', 'name': '伊利股份', 'industry': '乳制品'},
        {'symbol': '000063', 'name': '中兴通讯', 'industry': '通信'},
        {'symbol': '600104', 'name': '上汽集团', 'industry': '汽车'},
        {'symbol': '601988', 'name': '中国银行', 'industry': '银行'},
    ]
    
    # 保存示例股票到数据库
    stocks_added = 0
    for stock in sample_stocks:
        try:
            stock_info = {
                'symbol': stock['symbol'],
                'name': stock['name'],
                'market_cap': 100000000000.0,  # 示例市值
                'close': 10.0,  # 示例价格
                'industry': stock['industry'],
                'pe': 15.0,  # 示例PE
                'pb': 1.5,   # 示例PB
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            db.save_stock_info(stock['symbol'], stock_info)
            stocks_added += 1
            print(f"已添加: {stock['symbol']} - {stock['name']} ({stock['industry']})")
            
        except Exception as e:
            print(f"添加 {stock['symbol']} 失败: {e}")
    
    # 显示最终结果
    final_stocks = db.get_stock_list()
    print(f"\n=== 同步完成 ===")
    print(f"成功添加 {stocks_added} 只股票")
    print(f"数据库中股票总数: {len(final_stocks)}")
    
    # 按行业分组显示
    if isinstance(final_stocks, list):
        df = pd.DataFrame(final_stocks)
    else:
        df = final_stocks
    
    if not df.empty and 'industry' in df.columns:
        industry_counts = df['industry'].value_counts()
        print("\n按行业分布:")
        for industry, count in industry_counts.head().items():
            print(f"  {industry}: {count} 只")
    
    return True

if __name__ == "__main__":
    sync_local_stocks()