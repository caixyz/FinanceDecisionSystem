"""
长期存活股票分析演示工具
使用模拟数据演示10年、20年股票分析方法
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import logger

class DemoLongTermAnalyzer:
    """演示长期存活股票分析器"""
    
    def __init__(self, db_path="data/finance_data.db"):
        self.db_path = db_path
    
    def create_demo_data(self):
        """创建演示数据"""
        logger.info("创建长期存活股票演示数据...")
        
        # 创建模拟的长期股票数据
        companies = [
            # 20年以上老牌公司
            {'symbol': '000001', 'name': '平安银行', 'industry': '银行', 'list_year': 1991, 'quality_score': 95},
            {'symbol': '000002', 'name': '万科A', 'industry': '房地产', 'list_year': 1991, 'quality_score': 92},
            {'symbol': '600036', 'name': '招商银行', 'industry': '银行', 'list_year': 1991, 'quality_score': 98},
            {'symbol': '000858', 'name': '五粮液', 'industry': '白酒', 'list_year': 1998, 'quality_score': 96},
            {'symbol': '600519', 'name': '贵州茅台', 'industry': '白酒', 'list_year': 2001, 'quality_score': 100},
            {'symbol': '000651', 'name': '格力电器', 'industry': '家电', 'list_year': 1996, 'quality_score': 94},
            {'symbol': '000333', 'name': '美的集团', 'industry': '家电', 'list_year': 1993, 'quality_score': 93},
            {'symbol': '601318', 'name': '中国平安', 'industry': '保险', 'list_year': 2007, 'quality_score': 97},
            
            # 15-20年成熟公司
            {'symbol': '600031', 'name': '三一重工', 'industry': '工程机械', 'list_year': 2003, 'quality_score': 85},
            {'symbol': '000157', 'name': '中联重科', 'industry': '工程机械', 'list_year': 2000, 'quality_score': 82},
            {'symbol': '600276', 'name': '恒瑞医药', 'industry': '医药', 'list_year': 2000, 'quality_score': 90},
            {'symbol': '600887', 'name': '伊利股份', 'industry': '乳制品', 'list_year': 1996, 'quality_score': 88},
            
            # 10-15年成长公司
            {'symbol': '002415', 'name': '海康威视', 'industry': '安防', 'list_year': 2010, 'quality_score': 91},
            {'symbol': '000725', 'name': '京东方A', 'industry': '面板', 'list_year': 2001, 'quality_score': 75},
            {'symbol': '002594', 'name': '比亚迪', 'industry': '汽车', 'list_year': 2011, 'quality_score': 89},
            {'symbol': '300750', 'name': '宁德时代', 'industry': '新能源', 'list_year': 2018, 'quality_score': 93},
            
            # 5-10年新兴公司
            {'symbol': '688981', 'name': '中芯国际', 'industry': '半导体', 'list_year': 2020, 'quality_score': 78},
            {'symbol': '688036', 'name': '传音控股', 'industry': '手机', 'list_year': 2019, 'quality_score': 83},
        ]
        
        # 计算当前年份
        current_year = datetime.now().year
        
        # 创建DataFrame
        df = pd.DataFrame(companies)
        df['survival_years'] = current_year - df['list_year']
        df['first_trade_date'] = pd.to_datetime(df['list_year'].astype(str) + '-01-01')
        df['last_trade_date'] = pd.to_datetime('2024-12-31')
        df['trading_days'] = (df['survival_years'] * 250).astype(int)  # 假设每年250个交易日
        df['is_active'] = True
        
        # 分类
        def categorize_survival(years):
            if years >= 20:
                return '20年+'
            elif years >= 15:
                return '15-20年'
            elif years >= 10:
                return '10-15年'
            elif years >= 5:
                return '5-10年'
            else:
                return '新股'
        
        df['survival_category'] = df['survival_years'].apply(categorize_survival)
        
        return df
    
    def analyze_demo_data(self):
        """分析演示数据"""
        logger.info("分析演示数据...")
        df = self.create_demo_data()
        
        # 长期存活股票分析
        long_term_10 = df[df['survival_years'] >= 10]
        long_term_20 = df[df['survival_years'] >= 20]
        
        # 生成报告
        report = "A股长期存活股票演示分析报告\n"
        report += "=" * 50 + "\n\n"
        report += "演示数据概况:\n"
        report += f"总股票数: {len(df)}\n"
        report += f"活跃股票: {len(df[df['is_active']])} ({len(df[df['is_active']])/len(df)*100:.1f}%)\n\n"
        report += "存活年限分布:\n"
        report += f"20年+: {len(df[df['survival_years'] >= 20])}只 ({len(df[df['survival_years'] >= 20])/len(df)*100:.1f}%)\n"
        report += f"15-20年: {len(df[(df['survival_years'] >= 15) & (df['survival_years'] < 20)])}只\n"
        report += f"10-15年: {len(df[(df['survival_years'] >= 10) & (df['survival_years'] < 15)])}只\n"
        report += f"5-10年: {len(df[(df['survival_years'] >= 5) & (df['survival_years'] < 10)])}只\n"
        report += f"新股: {len(df[df['survival_years'] < 5])}只\n\n"
        report += f"10年以上优质股票 ({len(long_term_10)}只):\n"
        
        for _, stock in long_term_10.iterrows():
            report += f"{stock['symbol']} {stock['name']} ({stock['industry']}) - {stock['survival_years']}年, 评分{stock['quality_score']}\n"
        
        report += f"\n20年以上老牌股票 ({len(long_term_20)}只):\n"
        for _, stock in long_term_20.iterrows():
            report += f"{stock['symbol']} {stock['name']} ({stock['industry']}) - {stock['survival_years']}年\n"
        
        # 行业分布
        industry_dist = long_term_10['industry'].value_counts()
        report += f"\n长期存活股票行业分布:\n"
        for industry, count in industry_dist.items():
            report += f"{industry}: {count}只\n"
        
        return df, report
    
    def create_investment_strategies(self, df):
        """创建投资策略建议"""
        strategies = {
            '保守型': {
                'description': '专注20年以上老牌公司',
                'stocks': df[df['survival_years'] >= 20],
                'criteria': '存活年限≥20年, 质量评分≥90',
                'allocation': '核心持仓60%',
                'risk_level': '低风险'
            },
            '平衡型': {
                'description': '10-20年成熟公司为主',
                'stocks': df[(df['survival_years'] >= 10) & (df['survival_years'] < 20)],
                'criteria': '存活年限10-20年, 质量评分≥85',
                'allocation': '核心持仓50%, 成长配置30%',
                'risk_level': '中低风险'
            },
            '成长型': {
                'description': '10-15年成长公司',
                'stocks': df[(df['survival_years'] >= 10) & (df['survival_years'] < 15)],
                'criteria': '存活年限10-15年, 质量评分≥80',
                'allocation': '成长配置60%',
                'risk_level': '中等风险'
            }
        }
        
        return strategies
    
    def save_demo_results(self, df, report):
        """保存演示结果"""
        os.makedirs('data', exist_ok=True)
        
        # 保存数据
        df.to_csv('data/demo_long_term_stocks.csv', index=False, encoding='utf-8-sig')
        
        # 保存报告
        with open('data/demo_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 创建投资策略
        strategies = self.create_investment_strategies(df)
        
        strategy_report = "=== 长期投资策略建议 ===\n\n"
        for strategy_name, details in strategies.items():
            strategy_report += f"\n{strategy_name}策略:\n"
            strategy_report += f"描述: {details['description']}\n"
            strategy_report += f"选股标准: {details['criteria']}\n"
            strategy_report += f"资金配置: {details['allocation']}\n"
            strategy_report += f"风险等级: {details['risk_level']}\n"
            strategy_report += f"股票数量: {len(details['stocks'])}只\n"
            if not details['stocks'].empty:
                strategy_report += "主要股票:\n"
                for _, stock in details['stocks'].iterrows():
                    strategy_report += f"  • {stock['symbol']} {stock['name']} - {stock['survival_years']}年\n"
        
        with open('data/demo_investment_strategies.txt', 'w', encoding='utf-8') as f:
            f.write(strategy_report)
        
        print("演示分析结果已保存:")
        print("data/demo_long_term_stocks.csv - 股票数据")
        print("data/demo_analysis_report.txt - 分析报告")
        print("data/demo_investment_strategies.txt - 投资策略")
    
    def run_demo_analysis(self):
        """运行完整的演示分析"""
        logger.info("开始长期存活股票演示分析...")
        
        # 分析数据
        df, report = self.analyze_demo_data()
        
        # 保存结果
        self.save_demo_results(df, report)
        
        # 打印报告
        print(report)
        
        return df

def main():
    """主函数"""
    analyzer = DemoLongTermAnalyzer()
    analyzer.run_demo_analysis()

if __name__ == "__main__":
    main()