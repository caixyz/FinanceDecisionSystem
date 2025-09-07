#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
寻找被低估的优质公司分析工具
基于长期持有价值评估框架，筛选当前估值合理的优质股票
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

class UndervaluedStockFinder:
    """寻找被低估的优质公司"""
    
    def __init__(self, db_path="data/finance_data.db"):
        self.db_path = db_path
        self.conn = None
        self.connect_db()
        
    def connect_db(self):
        """连接数据库"""
        try:
            db_full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.db_path)
            self.conn = sqlite3.connect(db_full_path)
        except Exception as e:
            print(f"数据库连接失败: {e}")
            self.conn = None
    
    def get_stock_basics(self):
        """获取股票基本信息"""
        try:
            query = """
            SELECT code, name, industry, area, pe, pb, roe, net_profit_ratio, gross_profit_rate
            FROM stock_basics 
            WHERE pe IS NOT NULL AND pe > 0 AND pb IS NOT NULL AND pb > 0
            """
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()
    
    def get_financial_indicators(self):
        """获取财务指标"""
        try:
            query = """
            SELECT 
                code,
                roe,
                net_profit_ratio,
                gross_profit_rate,
                netprofit_yoy,
                esp_yoy,
                mb_revenue_yoy,
                debt_asset_ratio
            FROM financial_indicators
            WHERE roe IS NOT NULL
            """
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"获取财务指标失败: {e}")
            return pd.DataFrame()
    
    def calculate_valuation_score(self, df):
        """计算估值评分"""
        df = df.copy()
        
        # PE估值评分 (越低越好)
        df['pe_score'] = 100 - (df['pe'] / 50 * 100)
        df['pe_score'] = df['pe_score'].clip(0, 100)
        
        # PB估值评分 (越低越好)
        df['pb_score'] = 100 - (df['pb'] / 5 * 100)
        df['pb_score'] = df['pb_score'].clip(0, 100)
        
        # PEG估值评分 (考虑成长性)
        df['peg'] = df['pe'] / abs(df['netprofit_yoy'].replace(0, np.nan))
        df['peg_score'] = 100 - (df['peg'] / 2 * 100)
        df['peg_score'] = df['peg_score'].clip(0, 100)
        
        # 综合估值评分
        df['valuation_score'] = (df['pe_score'] * 0.4 + df['pb_score'] * 0.3 + df['peg_score'] * 0.3)
        
        return df
    
    def calculate_quality_score(self, df):
        """计算质量评分"""
        df = df.copy()
        
        # ROE评分
        df['roe_score'] = (df['roe'] / 20 * 100).clip(0, 100)
        
        # 净利润率评分
        df['profit_score'] = (df['net_profit_ratio'] / 20 * 100).clip(0, 100)
        
        # 毛利率评分
        df['margin_score'] = (df['gross_profit_rate'] / 50 * 100).clip(0, 100)
        
        # 成长性评分
        df['growth_score'] = (df['netprofit_yoy'] / 30 * 100).clip(-50, 100)
        
        # 财务稳健性评分
        df['debt_score'] = 100 - (df['debt_asset_ratio'] / 70 * 100)
        df['debt_score'] = df['debt_score'].clip(0, 100)
        
        # 综合质量评分
        df['quality_score'] = (
            df['roe_score'] * 0.3 + 
            df['profit_score'] * 0.2 + 
            df['margin_score'] * 0.2 + 
            df['growth_score'] * 0.15 + 
            df['debt_score'] * 0.15
        )
        
        return df
    
    def find_undervalued_stocks(self, min_quality_score=70, max_valuation_score=50):
        """寻找被低估的优质公司"""
        
        # 获取数据
        basics_df = self.get_stock_basics()
        financial_df = self.get_financial_indicators()
        
        if basics_df.empty or financial_df.empty:
            print("数据库中没有足够的数据，使用模拟数据演示...")
            return self.get_demo_undervalued_stocks()
        
        # 合并数据
        merged_df = pd.merge(basics_df, financial_df, on='code', how='inner')
        
        # 计算评分
        merged_df = self.calculate_valuation_score(merged_df)
        merged_df = self.calculate_quality_score(merged_df)
        
        # 综合评分
        merged_df['total_score'] = merged_df['quality_score'] * 0.6 + merged_df['valuation_score'] * 0.4
        
        # 筛选条件
        undervalued = merged_df[
            (merged_df['quality_score'] >= min_quality_score) &
            (merged_df['valuation_score'] <= max_valuation_score) &
            (merged_df['roe'] >= 15) &
            (merged_df['netprofit_yoy'] >= 10)
        ]
        
        # 排序
        undervalued = undervalued.sort_values('total_score', ascending=False)
        
        return undervalued.head(10)
    
    def get_demo_undervalued_stocks(self):
        """获取演示用的被低估股票"""
        demo_stocks = [
            {
                'code': '000858',
                'name': '五粮液',
                'industry': '白酒',
                'pe': 18.5,
                'pb': 3.2,
                'roe': 27.9,
                'net_profit_ratio': 36.5,
                'gross_profit_rate': 75.2,
                'netprofit_yoy': 22.6,
                'debt_asset_ratio': 25.3,
                'valuation_score': 75,
                'quality_score': 95,
                'total_score': 87
            },
            {
                'code': '600519',
                'name': '贵州茅台',
                'industry': '白酒',
                'pe': 25.8,
                'pb': 8.5,
                'roe': 31.2,
                'net_profit_ratio': 52.8,
                'gross_profit_rate': 91.5,
                'netprofit_yoy': 19.2,
                'debt_asset_ratio': 12.4,
                'valuation_score': 65,
                'quality_score': 98,
                'total_score': 84.8
            },
            {
                'code': '000333',
                'name': '美的集团',
                'industry': '家电',
                'pe': 12.3,
                'pb': 2.1,
                'roe': 24.8,
                'net_profit_ratio': 9.2,
                'gross_profit_rate': 25.1,
                'netprofit_yoy': 14.1,
                'debt_asset_ratio': 64.2,
                'valuation_score': 85,
                'quality_score': 78,
                'total_score': 81.2
            },
            {
                'code': '600036',
                'name': '招商银行',
                'industry': '银行',
                'pe': 6.8,
                'pb': 0.9,
                'roe': 16.5,
                'net_profit_ratio': 38.2,
                'gross_profit_rate': 45.8,
                'netprofit_yoy': 11.2,
                'debt_asset_ratio': 92.1,
                'valuation_score': 92,
                'quality_score': 72,
                'total_score': 80.0
            },
            {
                'code': '000651',
                'name': '格力电器',
                'industry': '家电',
                'pe': 8.9,
                'pb': 1.8,
                'roe': 25.6,
                'net_profit_ratio': 12.8,
                'gross_profit_rate': 30.5,
                'netprofit_yoy': 16.7,
                'debt_asset_ratio': 58.9,
                'valuation_score': 88,
                'quality_score': 82,
                'total_score': 84.6
            }
        ]
        
        return pd.DataFrame(demo_stocks)
    
    def format_analysis_report(self, stocks_df):
        """格式化分析报告"""
        if stocks_df.empty:
            return "没有找到符合条件的被低估优质公司。"
        
        report = []
        report.append("📊 当前被低估的优质公司分析")
        report.append("=" * 50)
        
        for idx, stock in stocks_df.iterrows():
            report.append(f"\n🏆 {stock['name']} ({stock['code']})")
            report.append(f"行业：{stock['industry']}")
            report.append(f"估值评分：{stock['valuation_score']:.1f}/100")
            report.append(f"质量评分：{stock['quality_score']:.1f}/100")
            report.append(f"综合评分：{stock['total_score']:.1f}/100")
            
            report.append(f"\n💰 估值指标：")
            report.append(f"  PE：{stock['pe']:.1f}倍")
            report.append(f"  PB：{stock['pb']:.1f}倍")
            report.append(f"  ROE：{stock['roe']:.1f}%")
            
            report.append(f"\n📈 财务指标：")
            report.append(f"  净利润率：{stock['net_profit_ratio']:.1f}%")
            report.append(f"  毛利率：{stock['gross_profit_rate']:.1f}%")
            report.append(f"  净利润增长：{stock['netprofit_yoy']:.1f}%")
            report.append(f"  负债率：{stock['debt_asset_ratio']:.1f}%")
            
            # 投资建议
            if stock['total_score'] >= 85:
                recommendation = "🟢 强烈推荐"
            elif stock['total_score'] >= 75:
                recommendation = "🟡 推荐"
            else:
                recommendation = "🟠 观望"
            
            report.append(f"\n🎯 投资建议：{recommendation}")
            report.append("-" * 30)
        
        return "\n".join(report)
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

def main():
    """主函数"""
    print("🔍 正在扫描被低估的优质公司...")
    
    finder = UndervaluedStockFinder()
    
    try:
        undervalued_stocks = finder.find_undervalued_stocks()
        report = finder.format_analysis_report(undervalued_stocks)
        print(report)
        
        # 保存结果
        if not undervalued_stocks.empty:
            output_file = "undervalued_stocks_analysis.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n💾 分析结果已保存到：{output_file}")
    
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
    
    finally:
        finder.close()

if __name__ == "__main__":
    main()
