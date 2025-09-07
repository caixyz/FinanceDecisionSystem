"""
长期存活股票分析工具
分析A股市场中长期存活的公司，识别具有10年、20年历史的优质股票
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

from core.data_source import StockDataFetcher
from core.storage import DatabaseManager
from utils.logger import logger

class LongTermSurvivalAnalyzer:
    """长期存活股票分析器"""
    
    def __init__(self, db_path="data/finance_data.db"):
        self.db_path = db_path
        self.fetcher = StockDataFetcher()
        self.db_manager = DatabaseManager(db_path)
        
    def get_all_stocks_with_history(self):
        """获取所有股票及其历史数据"""
        logger.info("开始获取所有股票历史数据...")
        
        # 从数据库获取股票列表
        conn = sqlite3.connect(self.db_path)
        try:
            # 获取股票基本信息
            stocks_df = pd.read_sql_query("""
                SELECT DISTINCT symbol, name, industry
                FROM stock_info 
                WHERE symbol IS NOT NULL
                ORDER BY symbol
            """, conn)
            
            # 获取历史数据时间范围
            history_df = pd.read_sql_query("""
                SELECT symbol, MIN(date) as first_trade_date, MAX(date) as last_trade_date,
                       COUNT(*) as trading_days
                FROM stock_daily 
                GROUP BY symbol
            """, conn)
            
            # 合并数据
            if not stocks_df.empty and not history_df.empty:
                merged_df = pd.merge(stocks_df, history_df, on='symbol', how='inner')
                return merged_df
            else:
                return pd.DataFrame()
                
        finally:
            conn.close()
    
    def calculate_survival_metrics(self, df):
        """计算存活指标"""
        logger.info("计算存活指标...")
        
        if df.empty:
            return pd.DataFrame()
        
        # 转换日期格式
        df['first_trade_date'] = pd.to_datetime(df['first_trade_date'], errors='coerce')
        df['last_trade_date'] = pd.to_datetime(df['last_trade_date'], errors='coerce')
        
        # 计算当前日期
        current_date = datetime.now()
        
        # 计算存活年限
        df['survival_years'] = (current_date - df['first_trade_date']).dt.days / 365.25
        
        # 计算最近交易活跃度
        df['days_since_last_trade'] = (current_date - df['last_trade_date']).dt.days
        
        # 判断是否为活跃股票
        df['is_active'] = df['days_since_last_trade'] <= 30
        
        # 计算长期存活分类
        df['survival_category'] = df['survival_years'].apply(
            lambda x: '20年+' if x >= 20 else 
                     '15-20年' if x >= 15 else 
                     '10-15年' if x >= 10 else 
                     '5-10年' if x >= 5 else 
                     '1-5年' if x >= 1 else '新股'
        )
        
        return df
    
    def analyze_long_term_survivors(self, min_years=10):
        """分析长期存活股票"""
        logger.info(f"分析{min_years}年以上存活股票...")
        
        # 获取基础数据
        df = self.get_all_stocks_with_history()
        if df.empty:
            logger.warning("未找到股票历史数据")
            return pd.DataFrame()
        
        # 计算指标
        df = self.calculate_survival_metrics(df)
        
        # 筛选长期存活股票
        long_term_df = df[df['survival_years'] >= min_years].copy()
        
        # 排序：按存活年限降序
        long_term_df = long_term_df.sort_values('survival_years', ascending=False)
        
        # 添加质量指标
        long_term_df['quality_score'] = self._calculate_quality_score(long_term_df)
        
        return long_term_df
    
    def _calculate_quality_score(self, df):
        """计算股票质量评分"""
        score = pd.Series(0.0, index=df.index)
        
        # 存活年限权重 (40%)
        score += (df['survival_years'] / df['survival_years'].max()) * 40
        
        # 交易活跃度权重 (30%)
        score += (df['trading_days'] / df['trading_days'].max()) * 30
        
        # 最近交易权重 (30%)
        score += (1 - df['days_since_last_trade'] / 365) * 30
        
        return score.round(2)
    
    def get_top_long_term_stocks(self, min_years=10, top_n=50):
        """获取顶级长期存活股票"""
        df = self.analyze_long_term_survivors(min_years)
        
        if df.empty:
            return pd.DataFrame()
        
        # 选择需要的列
        columns = [
            'symbol', 'name', 'industry', 'survival_years', 
            'first_trade_date', 'last_trade_date', 'trading_days',
            'survival_category', 'quality_score', 'is_active'
        ]
        
        result = df[columns].head(top_n)
        
        # 格式化输出
        result['survival_years'] = result['survival_years'].round(1)
        result['first_trade_date'] = result['first_trade_date'].dt.strftime('%Y-%m-%d')
        result['last_trade_date'] = result['last_trade_date'].dt.strftime('%Y-%m-%d')
        
        return result
    
    def generate_summary_report(self):
        """生成总结报告"""
        logger.info("生成长线股票分析报告...")
        
        # 获取所有数据
        df = self.get_all_stocks_with_history()
        if df.empty:
            return "无可用数据"
        
        df = self.calculate_survival_metrics(df)
        
        # 统计信息
        total_stocks = len(df)
        active_stocks = len(df[df['is_active']])
        
        survival_counts = {
            '20年+': len(df[df['survival_years'] >= 20]),
            '15-20年': len(df[(df['survival_years'] >= 15) & (df['survival_years'] < 20)]),
            '10-15年': len(df[(df['survival_years'] >= 10) & (df['survival_years'] < 15)]),
            '5-10年': len(df[(df['survival_years'] >= 5) & (df['survival_years'] < 10)]),
            '1-5年': len(df[(df['survival_years'] >= 1) & (df['survival_years'] < 5)]),
            '新股': len(df[df['survival_years'] < 1])
        }
        
        # 行业分布
        industry_survival = df[df['survival_years'] >= 10].groupby('industry').size().sort_values(ascending=False)
        
        report = "A股长期存活股票分析报告\n"
        report += "=" * 50 + "\n"
        report += f"总股票数: {total_stocks}\n"
        report += f"活跃股票: {active_stocks} ({active_stocks/total_stocks*100:.1f}%)\n\n"
        report += "存活年限分布:\n"
        
        for category, count in survival_counts.items():
            percentage = count / total_stocks * 100
            report += f"{category}: {count}只 ({percentage:.1f}%)\n"
        
        if not industry_survival.empty:
            report += "\n长期存活股票行业TOP5:\n"
            for industry, count in industry_survival.head(5).items():
                report += f"{industry}: {count}只\n"
        
        return report

def main():
    """主函数"""
    analyzer = LongTermSurvivalAnalyzer()
    
    # 获取10年以上存活股票
    top_stocks = analyzer.get_top_long_term_stocks(min_years=10, top_n=30)
    
    if not top_stocks.empty:
        print("=== 10年以上优质股票TOP30 ===")
        print(top_stocks.to_string(index=False))
        
        # 保存到CSV
        output_file = "data/long_term_survivors.csv"
        os.makedirs("data", exist_ok=True)
        top_stocks.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到: {output_file}")
    
    # 生成报告
    report = analyzer.generate_summary_report()
    print(report)
    
    # 获取20年以上股票
    twenty_year_stocks = analyzer.get_top_long_term_stocks(min_years=20, top_n=20)
    if not twenty_year_stocks.empty:
        print("\n=== 20年以上老牌股票TOP20 ===")
        print(twenty_year_stocks[['symbol', 'name', 'industry', 'survival_years']].to_string(index=False))

if __name__ == "__main__":
    main()