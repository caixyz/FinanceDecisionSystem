"""
长期投资策略报告生成器
生成基于数据驱动的长期持有投资建议
"""
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from dev_tools.company_quality_analyzer import CompanyQualityAnalyzer
from dev_tools.long_term_survival_analysis import LongTermSurvivalAnalyzer
from utils.logger import logger

class LongTermInvestmentReport:
    """长期投资策略报告"""
    
    def __init__(self, db_path="data/finance_data.db"):
        self.db_path = db_path
        self.survival_analyzer = LongTermSurvivalAnalyzer(db_path)
        self.quality_analyzer = CompanyQualityAnalyzer(db_path)
        
    def generate_complete_report(self):
        """生成完整的投资策略报告"""
        logger.info("开始生成长期投资策略报告...")
        
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_overview': self._analyze_market_overview(),
            'top_recommendations': self._get_top_recommendations(),
            'sector_analysis': self._analyze_sectors(),
            'strategy_recommendations': self._generate_strategy_recommendations(),
            'risk_warnings': self._generate_risk_warnings()
        }
        
        return report
    
    def _analyze_market_overview(self):
        """市场概览分析"""
        # 获取长期存活股票数据
        long_term_stocks = self.survival_analyzer.get_top_long_term_stocks(min_years=10, top_n=200)
        
        if long_term_stocks.empty:
            return {'error': '无可用数据'}
        
        overview = {
            'total_long_term_stocks': len(long_term_stocks),
            'avg_survival_years': long_term_stocks['survival_years'].mean(),
            'industry_distribution': long_term_stocks['industry'].value_counts().head(10).to_dict(),
            'survival_categories': long_term_stocks['survival_category'].value_counts().to_dict()
        }
        
        return overview
    
    def _get_top_recommendations(self, top_n=20):
        """获取顶级推荐股票"""
        # 获取长期存活股票
        long_term_stocks = self.survival_analyzer.get_top_long_term_stocks(min_years=15, top_n=50)
        
        if long_term_stocks.empty:
            return []
        
        recommendations = []
        
        # 分析每个股票的长期价值
        for _, stock in long_term_stocks.head(top_n).iterrows():
            try:
                quality_analysis = self.quality_analyzer.analyze_company_quality(stock['symbol'])
                
                recommendation = {
                    'symbol': stock['symbol'],
                    'name': stock['name'],
                    'industry': stock['industry'],
                    'survival_years': stock['survival_years'],
                    'quality_score': quality_analysis.get('long_term_score', 0),
                    'financial_health': quality_analysis.get('financial_health', {}),
                    'growth_potential': quality_analysis.get('growth_potential', {}),
                    'risk_level': quality_analysis.get('risk_assessment', {}).get('risk_level', 'unknown'),
                    'recommendation': quality_analysis.get('recommendation', '')
                }
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"分析 {stock['symbol']} 时出错: {e}")
                continue
        
        # 按质量评分排序
        recommendations.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _analyze_sectors(self):
        """行业分析"""
        long_term_stocks = self.survival_analyzer.get_top_long_term_stocks(min_years=10, top_n=100)
        
        if long_term_stocks.empty:
            return {}
        
        sector_analysis = {}
        
        for industry in long_term_stocks['industry'].unique():
            industry_stocks = long_term_stocks[long_term_stocks['industry'] == industry]
            
            sector_analysis[industry] = {
                'count': len(industry_stocks),
                'avg_survival_years': industry_stocks['survival_years'].mean(),
                'top_stocks': industry_stocks[['symbol', 'name', 'survival_years']].head(3).to_dict('records')
            }
        
        return sector_analysis
    
    def _generate_strategy_recommendations(self):
        """生成策略建议"""
        recommendations = {
            'portfolio_allocation': {
                'defensive_stocks': {
                    'description': '防御性股票 - 20年以上老牌公司',
                    'allocation': '40%',
                    'characteristics': ['稳定分红', '低波动率', '行业龙头'],
                    'examples': ['银行', '保险', '公用事业']
                },
                'growth_stocks': {
                    'description': '成长型股票 - 10-20年成长公司',
                    'allocation': '35%',
                    'characteristics': ['行业成长', '业绩稳定', '估值合理'],
                    'examples': ['消费龙头', '制造业', '医药']
                },
                'value_stocks': {
                    'description': '价值型股票 - 被低估的优质公司',
                    'allocation': '25%',
                    'characteristics': ['低估值', '高ROE', '现金流好'],
                    'examples': ['周期股', '价值洼地']
                }
            },
            'holding_periods': {
                'short_term': '1-3年 - 观察期，验证投资逻辑',
                'medium_term': '3-7年 - 成长期，享受业绩增长',
                'long_term': '7-15年 - 成熟期，享受复利效应'
            },
            'rebalancing_frequency': {
                'quarterly': '季度检查 - 基本面变化',
                'annually': '年度调整 - 估值重新评估',
                'trigger_based': '触发调整 - 重大事件'
            }
        }
        
        return recommendations
    
    def _generate_risk_warnings(self):
        """生成风险提示"""
        warnings = [
            {
                'type': '市场风险',
                'level': '高',
                'description': '系统性风险可能影响所有股票，建议分批建仓',
                'mitigation': '分散投资，定期定额'
            },
            {
                'type': '行业风险',
                'level': '中',
                'description': '行业周期变化可能影响公司业绩',
                'mitigation': '跨行业配置，关注政策导向'
            },
            {
                'type': '公司风险',
                'level': '中',
                'description': '公司经营恶化或管理层变化',
                'mitigation': '定期跟踪财报，设置止损'
            },
            {
                'type': '流动性风险',
                'level': '低',
                'description': '部分小盘股可能存在流动性问题',
                'mitigation': '优选大盘股，关注成交量'
            },
            {
                'type': '估值风险',
                'level': '中',
                'description': '买入时估值过高可能影响长期收益',
                'mitigation': '等待合理估值，分批建仓'
            }
        ]
        
        return warnings
    
    def save_report(self, report, filename=None):
        """保存报告到文件"""
        if filename is None:
            filename = f"long_term_investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path("reports") / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"报告已保存到: {filepath}")
        return str(filepath)
    
    def print_summary_report(self, report):
        """打印摘要报告"""
        print("\n" + "="*60)
        print("🏆 长期投资策略报告")
        print("="*60)
        print(f"报告日期: {report['report_date']}")
        
        # 市场概览
        overview = report['market_overview']
        if 'error' not in overview:
            print(f"\n📊 市场概览:")
            print(f"   长期存活股票总数: {overview['total_long_term_stocks']}")
            print(f"   平均存活年限: {overview['avg_survival_years']:.1f}年")
            
            print(f"\n🏭 行业分布TOP5:")
            for industry, count in list(overview['industry_distribution'].items())[:5]:
                print(f"   {industry}: {count}只")
        
        # 顶级推荐
        print(f"\n🎯 顶级推荐股票 (前10):")
        for i, rec in enumerate(report['top_recommendations'][:10], 1):
            print(f"   {i:2d}. {rec['symbol']} {rec['name']} ({rec['industry']})")
            print(f"       存活: {rec['survival_years']:.1f}年 | 评分: {rec['quality_score']:.1f} | 风险: {rec['risk_level']}")
        
        # 策略建议
        strategy = report['strategy_recommendations']
        print(f"\n📋 投资组合建议:")
        for category, details in strategy['portfolio_allocation'].items():
            print(f"   {details['allocation']} - {details['description']}")
        
        print(f"\n⚠️  风险提示:")
        for warning in report['risk_warnings'][:3]:
            print(f"   {warning['type']}: {warning['description']}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    report_generator = LongTermInvestmentReport()
    
    # 生成完整报告
    complete_report = report_generator.generate_complete_report()
    
    # 打印摘要
    report_generator.print_summary_report(complete_report)
    
    # 保存报告
    report_file = report_generator.save_report(complete_report)
    print(f"\n完整报告已保存到: {report_file}")