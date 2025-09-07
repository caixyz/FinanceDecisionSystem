#!/usr/bin/env python3
"""
一键分析公司长期持有价值
使用方法: python analyze_long_term_company.py [股票代码]
"""
import sys
import argparse
from pathlib import Path
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from dev_tools.company_quality_analyzer import CompanyQualityAnalyzer
from dev_tools.long_term_investment_report import LongTermInvestmentReport
from dev_tools.long_term_survival_analysis import LongTermSurvivalAnalyzer

class LongTermCompanyAnalyzer:
    """公司长期持有价值分析器"""
    
    def __init__(self):
        self.analyzer = CompanyQualityAnalyzer()
        self.report_generator = LongTermInvestmentReport()
        self.survival_analyzer = LongTermSurvivalAnalyzer()
    
    def analyze_single_company(self, symbol):
        """分析单个公司的长期持有价值"""
        print(f"\n🔍 正在深度分析 {symbol} 的长期持有价值...")
        
        # 基础信息
        basic_info = self._get_basic_info(symbol)
        
        # 存活年限分析
        survival_analysis = self._analyze_survival(symbol)
        
        # 质量深度分析
        quality_analysis = self.analyzer.analyze_company_quality(symbol)
        
        # 综合评估
        final_assessment = self._generate_final_assessment(
            basic_info, survival_analysis, quality_analysis
        )
        
        return final_assessment
    
    def _get_basic_info(self, symbol):
        """获取公司基础信息"""
        conn = self.survival_analyzer.db_manager.get_connection()
        try:
            query = """
                SELECT s.symbol, s.name, s.industry, s.area,
                       a.totalAssets, a.outstanding, a.esp, a.bvps, a.pb,
                       a.timeToMarket
                FROM stock_info s
                LEFT JOIN stock_basics a ON s.symbol = a.symbol
                WHERE s.symbol = ?
            """
            result = conn.execute(query, [symbol]).fetchone()
            
            if result:
                return dict(zip(['symbol', 'name', 'industry', 'area', 
                               'totalAssets', 'outstanding', 'esp', 'bvps', 'pb', 'timeToMarket'], 
                              result))
            return {}
        finally:
            conn.close()
    
    def _analyze_survival(self, symbol):
        """分析公司存活年限"""
        try:
            # 获取所有股票数据
            all_stocks = self.survival_analyzer.get_all_stocks_with_history()
            if all_stocks.empty:
                return {'survival_years': 0, 'category': '未知'}
            
            # 找到特定股票
            stock_data = all_stocks[all_stocks['symbol'] == symbol]
            if stock_data.empty:
                return {'survival_years': 0, 'category': '新股'}
            
            survival_years = float(stock_data.iloc[0]['survival_years'])
            
            # 分类
            if survival_years >= 20:
                category = "老牌龙头"
            elif survival_years >= 15:
                category = "成熟公司"
            elif survival_years >= 10:
                category = "成长公司"
            else:
                category = "新股/次新股"
            
            return {
                'survival_years': survival_years,
                'category': category,
                'first_trade': str(stock_data.iloc[0]['first_trade_date']) if 'first_trade_date' in stock_data.columns else '未知'
            }
            
        except Exception as e:
            print(f"存活分析出错: {e}")
            return {'survival_years': 0, 'category': '分析失败'}
    
    def _generate_final_assessment(self, basic_info, survival_analysis, quality_analysis):
        """生成最终评估"""
        
        # 计算综合评分
        survival_score = min(100, survival_analysis['survival_years'] * 4)
        quality_score = quality_analysis.get('long_term_score', 0)
        
        # 权重计算
        final_score = (survival_score * 0.3 + quality_score * 0.7)
        
        # 投资建议等级
        if final_score >= 85:
            recommendation = "🏆 强烈推荐长期持有"
            risk_level = "低风险"
            holding_period = "10年以上"
        elif final_score >= 75:
            recommendation = "⭐ 推荐长期持有"
            risk_level = "中低风险"
            holding_period = "7-10年"
        elif final_score >= 65:
            recommendation = "🔍 可以持有，需密切观察"
            risk_level = "中等风险"
            holding_period = "5-7年"
        elif final_score >= 50:
            recommendation = "⚠️ 谨慎持有"
            risk_level = "中高风险"
            holding_period = "3-5年"
        else:
            recommendation = "❌ 不建议长期持有"
            risk_level = "高风险"
            holding_period = "不建议"
        
        return {
            'company': basic_info,
            'survival': survival_analysis,
            'quality': quality_analysis,
            'final_assessment': {
                'overall_score': round(final_score, 2),
                'recommendation': recommendation,
                'risk_level': risk_level,
                'suggested_holding_period': holding_period,
                'key_factors': self._identify_key_factors(quality_analysis)
            }
        }
    
    def _identify_key_factors(self, quality_analysis):
        """识别关键影响因素"""
        factors = []
        
        # 财务健康度
        financial = quality_analysis.get('financial_health', {})
        if financial.get('score', 0) > 70:
            factors.append("✅ 财务健康度优秀")
        elif financial.get('score', 0) > 50:
            factors.append("⚖️ 财务健康度良好")
        else:
            factors.append("⚠️ 财务健康度一般")
        
        # 成长性
        growth = quality_analysis.get('growth_potential', {})
        if growth.get('score', 0) > 70:
            factors.append("📈 成长性优秀")
        elif growth.get('score', 0) > 50:
            factors.append("📊 成长性良好")
        else:
            factors.append("📉 成长性一般")
        
        # 风险水平
        risk = quality_analysis.get('risk_assessment', {})
        if risk.get('risk_level') == 'low':
            factors.append("🛡️ 风险水平较低")
        elif risk.get('risk_level') == 'medium':
            factors.append("⚠️ 风险水平中等")
        else:
            factors.append("🔥 风险水平较高")
        
        return factors
    
    def print_analysis_report(self, analysis_result):
        """打印分析报告"""
        print("\n" + "="*70)
        print("🏆 公司长期持有价值分析报告")
        print("="*70)
        
        # 公司基本信息
        company = analysis_result['company']
        if company:
            print(f"\n📊 公司信息:")
            print(f"   股票代码: {company.get('symbol', 'N/A')}")
            print(f"   公司名称: {company.get('name', 'N/A')}")
            print(f"   所属行业: {company.get('industry', 'N/A')}")
            print(f"   所在地区: {company.get('area', 'N/A')}")
        
        # 存活分析
        survival = analysis_result['survival']
        print(f"\n⏰ 存活分析:")
        print(f"   上市年限: {survival.get('survival_years', 0):.1f}年")
        print(f"   公司类型: {survival.get('category', '未知')}")
        print(f"   首次交易: {survival.get('first_trade', '未知')}")
        
        # 最终评估
        assessment = analysis_result['final_assessment']
        print(f"\n🎯 最终评估:")
        print(f"   综合评分: {assessment['overall_score']}分")
        print(f"   投资建议: {assessment['recommendation']}")
        print(f"   风险等级: {assessment['risk_level']}")
        print(f"   建议持有: {assessment['suggested_holding_period']}")
        
        # 关键因素
        factors = assessment['key_factors']
        if factors:
            print(f"\n🔍 关键影响因素:")
            for factor in factors:
                print(f"   {factor}")
        
        print("\n" + "="*70)
    
    def save_analysis_report(self, analysis_result, filename=None):
        """保存分析报告"""
        if filename is None:
            symbol = analysis_result['company'].get('symbol', 'unknown')
            filename = f"analysis_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path("reports") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n📄 分析报告已保存到: {filepath}")
        return str(filepath)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分析公司长期持有价值')
    parser.add_argument('symbol', nargs='?', help='股票代码，如 000858')
    parser.add_argument('--list', action='store_true', help='列出长期存活股票')
    parser.add_argument('--report', action='store_true', help='生成完整投资策略报告')
    
    args = parser.parse_args()
    
    analyzer = LongTermCompanyAnalyzer()
    
    if args.list:
        print("\n📋 长期存活股票列表 (10年以上):")
        survival_analyzer = LongTermSurvivalAnalyzer()
        long_term_stocks = survival_analyzer.get_top_long_term_stocks(min_years=10, top_n=20)
        
        if not long_term_stocks.empty:
            for _, stock in long_term_stocks.iterrows():
                print(f"   {stock['symbol']} {stock['name']} - {stock['industry']} ({stock['survival_years']:.1f}年)")
        else:
            print("   暂无数据")
    
    elif args.report:
        print("\n🏆 正在生成完整投资策略报告...")
        report_generator = LongTermInvestmentReport()
        report = report_generator.generate_complete_report()
        report_generator.print_summary_report(report)
        
    elif args.symbol:
        # 分析单个公司
        symbol = args.symbol.zfill(6)  # 补零
        result = analyzer.analyze_single_company(symbol)
        analyzer.print_analysis_report(result)
        
        # 保存报告
        save_choice = input("\n是否保存详细报告? (y/n): ").lower()
        if save_choice == 'y':
            analyzer.save_analysis_report(result)
    
    else:
        print("\n🎯 使用方法:")
        print("   python analyze_long_term_company.py 000858      # 分析单个公司")
        print("   python analyze_long_term_company.py --list      # 列出长期存活股票")
        print("   python analyze_long_term_company.py --report    # 生成完整报告")

if __name__ == "__main__":
    main()