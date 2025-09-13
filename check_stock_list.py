#!/usr/bin/env python3
"""
验证股票列表显示
"""
import sys
sys.path.append('core')

from core.storage import DatabaseManager
from collections import Counter

def check_stock_list():
    """检查股票列表"""
    print("=== 股票列表验证 ===")
    
    db = DatabaseManager()
    
    # 获取股票列表
    stocks = db.get_stock_list()
    print(f"数据库中股票总数: {len(stocks)}")
    
    if not stocks:
        print("股票列表为空")
        return
    
    # 显示前20只股票
    print("\n前20只股票列表:")
    for i, stock in enumerate(stocks[:20]):
        print(f"{i+1:2d}. {stock['symbol']} - {stock['name']:<20} - {stock['industry']:<10} - 市值: {stock['market_cap']:>12.0f}")
    
    # 按行业统计
    industries = [s['industry'] for s in stocks if s['industry'] != '未分类']
    industry_count = Counter(industries)
    
    print("\n按行业分布 (前10):")
    for industry, count in industry_count.most_common(10):
        print(f"  {industry}: {count} 只股票")
    
    # 显示完整行业分布
    print(f"\n完整行业分布: {len(industry_count)} 个行业")
    
    return stocks

if __name__ == "__main__":
    check_stock_list()