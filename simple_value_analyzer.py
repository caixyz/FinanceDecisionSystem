#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版价值投资分析器
基于A股历史数据的核心逻辑演示
"""
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sqlite3
import os

class SimpleValueAnalyzer:
    """简化版价值投资分析器"""
    
    def __init__(self):
        self.db_path = os.path.join('data', 'finance_data.db')
        
    def get_all_stocks(self, limit=None):
        """获取所有股票数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at 
            FROM stock_info 
            WHERE symbol IS NOT NULL AND name IS NOT NULL
            ORDER BY symbol
            """
            
            if limit:
                query += f" LIMIT {limit}"
                
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # 清理数据
            df['market_cap'] = pd.to_numeric(df['market_cap'], errors='coerce')
            df['pe_ratio'] = pd.to_numeric(df['pe_ratio'], errors='coerce')
            df['pb_ratio'] = pd.to_numeric(df['pb_ratio'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            return pd.DataFrame()
    
    def analyze_stock(self, stock_data):
        """分析单只股票的长期投资价值"""
        try:
            symbol = stock_data.get('symbol', '')
            name = stock_data.get('name', '')
            industry = stock_data.get('industry', '')
            market_cap = float(stock_data.get('market_cap', 0))
            pe_ratio = float(stock_data.get('pe_ratio', 0))
            pb_ratio = float(stock_data.get('pb_ratio', 0))
            current_price = float(stock_data.get('close', 0))
            
            # 基础数据检查
            if not symbol or market_cap <= 0 or current_price <= 0:
                return {'qualified': False, 'error': '数据不完整'}
            
            # 计算各项评分
            score = 0
            score_details = {}
            
            # 1. 市值评分 (20分) - 偏好中等市值公司
            if market_cap >= 100 and market_cap <= 5000:
                score += 20
                score_details['市值评分'] = 20
            elif market_cap > 5000 and market_cap <= 10000:
                score += 15
                score_details['市值评分'] = 15
            elif market_cap > 10000:
                score += 10
                score_details['市值评分'] = 10
            else:
                score += 5
                score_details['市值评分'] = 5
            
            # 2. 市盈率评分 (25分) - 偏好低市盈率
            if pe_ratio > 0 and pe_ratio <= 15:
                score += 25
                score_details['市盈率评分'] = 25
            elif pe_ratio > 15 and pe_ratio <= 25:
                score += 20
                score_details['市盈率评分'] = 20
            elif pe_ratio > 25 and pe_ratio <= 40:
                score += 15
                score_details['市盈率评分'] = 15
            else:
                score += 5
                score_details['市盈率评分'] = 5
            
            # 3. 市净率评分 (25分) - 偏好低市净率
            if pb_ratio > 0 and pb_ratio <= 2:
                score += 25
                score_details['市净率评分'] = 25
            elif pb_ratio > 2 and pb_ratio <= 3:
                score += 20
                score_details['市净率评分'] = 20
            elif pb_ratio > 3 and pb_ratio <= 5:
                score += 15
                score_details['市净率评分'] = 15
            else:
                score += 5
                score_details['市净率评分'] = 5
            
            # 4. 行业评分 (15分) - 偏好稳定增长行业
            good_industries = ['白酒', '医药', '银行', '保险', '食品饮料', '家电']
            medium_industries = ['电力', '公用事业', '交通运输', '房地产']
            
            if any(ind in industry for ind in good_industries):
                score += 15
                score_details['行业评分'] = 15
            elif any(ind in industry for ind in medium_industries):
                score += 10
                score_details['行业评分'] = 10
            else:
                score += 5
                score_details['行业评分'] = 5
            
            # 5. 价格合理性评分 (15分)
            if current_price > 0 and current_price <= 50:
                score += 15
                score_details['价格评分'] = 15
            elif current_price > 50 and current_price <= 100:
                score += 12
                score_details['价格评分'] = 12
            elif current_price > 100 and current_price <= 200:
                score += 10
                score_details['价格评分'] = 10
            else:
                score += 5
                score_details['价格评分'] = 5
            
            # 计算评分百分比
            score_percent = min(int((score / 100) * 100), 100)
            
            # 判断是否合格
            qualified = score >= 60
            
            # 生成推荐等级
            if score >= 85:
                recommendation = '强烈推荐'
                risk_level = '低风险'
            elif score >= 75:
                recommendation = '推荐'
                risk_level = '中低风险'
            elif score >= 65:
                recommendation = '谨慎推荐'
                risk_level = '中等风险'
            else:
                recommendation = '观望'
                risk_level = '中高风险'
            
            # 生成关键指标
            key_metrics = {
                '市值': f'{market_cap:.1f}',
                '市盈率': f'{pe_ratio:.1f}',
                '市净率': f'{pb_ratio:.1f}',
                '当前价': f'{current_price:.2f}',
                '行业': industry
            }
            
            return {
                'symbol': symbol,
                'name': name,
                'industry': industry,
                'score': score,
                'score_percent': score_percent,
                'score_details': score_details,
                'key_metrics': key_metrics,
                'recommendation': recommendation,
                'risk_level': risk_level,
                'qualified': qualified,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'qualified': False, 'error': f'分析错误: {str(e)}'}

if __name__ == "__main__":
    # 测试代码
    analyzer = SimpleValueAnalyzer()
    stocks = analyzer.get_all_stocks(limit=10)
    
    if not stocks.empty:
        for _, stock in stocks.iterrows():
            result = analyzer.analyze_stock(stock.to_dict())
            print(f"股票: {stock['symbol']} - {stock['name']}")
            print(f"评分: {result.get('score', 0)} ({result.get('score_percent', 0)}%)")
            print(f"推荐: {result.get('recommendation', '-')}")
            print("-" * 50)