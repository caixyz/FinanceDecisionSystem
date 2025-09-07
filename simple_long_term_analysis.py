#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版公司长期持有价值分析
基于A股历史数据的核心逻辑演示
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class SimpleLongTermAnalyzer:
    """简化版长期持有价值分析器"""
    
    def __init__(self):
        # 模拟一些优质长期公司的数据
        self.demo_companies = {
            '000858': {
                'name': '五粮液',
                'industry': '白酒',
                'listing_date': '1998-04-27',
                'market_cap': 8000,  # 亿元
                'roes': [25.8, 26.1, 28.3, 30.2, 28.9],  # 近5年ROE
                'profit_growth': [15.2, 22.1, 30.5, 25.8, 19.4],  # 净利润增长率
                'dividend_yield': 2.1,
                'debt_ratio': 25.3,
                'gross_margin': 75.2,
                'net_margin': 35.8,
                'description': '浓香型白酒龙头，品牌护城河深厚'
            },
            '600519': {
                'name': '贵州茅台',
                'industry': '白酒',
                'listing_date': '2001-08-27',
                'market_cap': 25000,
                'roes': [32.1, 34.5, 33.8, 35.2, 31.9],
                'profit_growth': [20.5, 30.2, 27.8, 23.1, 19.8],
                'dividend_yield': 1.5,
                'debt_ratio': 15.2,
                'gross_margin': 91.5,
                'net_margin': 52.3,
                'description': '酱香型白酒绝对龙头，具备定价权'
            },
            '000001': {
                'name': '平安银行',
                'industry': '银行',
                'listing_date': '1991-04-03',
                'market_cap': 3000,
                'roes': [11.2, 12.1, 11.8, 10.9, 11.5],
                'profit_growth': [8.5, 12.3, 10.1, 7.8, 13.2],
                'dividend_yield': 4.2,
                'debt_ratio': 92.1,  # 银行特殊
                'gross_margin': 45.8,
                'net_margin': 28.5,
                'description': '零售银行业务领先，数字化转型成功'
            },
            '600036': {
                'name': '招商银行',
                'industry': '银行',
                'listing_date': '2002-04-09',
                'market_cap': 9000,
                'roes': [16.8, 17.2, 16.9, 15.8, 16.1],
                'profit_growth': [13.5, 15.2, 14.8, 12.1, 15.8],
                'dividend_yield': 5.1,
                'debt_ratio': 93.2,
                'gross_margin': 48.2,
                'net_margin': 35.2,
                'description': '零售银行龙头，资产质量优异'
            }
        }
    
    def calculate_survival_years(self, listing_date):
        """计算上市年限"""
        listing = datetime.strptime(listing_date, '%Y-%m-%d')
        return (datetime.now() - listing).days / 365.25
    
    def analyze_financial_health(self, company_data):
        """分析财务健康度"""
        score = 0
        details = {}
        
        # ROE评分 (权重30%)
        avg_roe = np.mean(company_data['roes'])
        roe_score = min(100, max(0, avg_roe * 3))
        details['roe'] = {'value': avg_roe, 'score': roe_score}
        score += roe_score * 0.3
        
        # 盈利增长评分 (权重25%)
        avg_growth = np.mean(company_data['profit_growth'])
        growth_score = min(100, max(0, avg_growth * 2.5))
        details['profit_growth'] = {'value': avg_growth, 'score': growth_score}
        score += growth_score * 0.25
        
        # 毛利率评分 (权重20%)
        margin = company_data['gross_margin']
        margin_score = min(100, max(0, margin * 0.8))
        details['gross_margin'] = {'value': margin, 'score': margin_score}
        score += margin_score * 0.2
        
        # 负债率评分 (权重15%)
        debt = company_data['debt_ratio']
        if company_data['industry'] == '银行':
            debt_score = 70  # 银行特殊处理
        else:
            debt_score = max(0, min(100, 100 - debt))
        details['debt_ratio'] = {'value': debt, 'score': debt_score}
        score += debt_score * 0.15
        
        # 分红率评分 (权重10%)
        dividend = company_data['dividend_yield']
        dividend_score = min(100, max(0, dividend * 15))
        details['dividend_yield'] = {'value': dividend, 'score': dividend_score}
        score += dividend_score * 0.1
        
        return {
            'score': round(score, 2),
            'details': details,
            'level': '优秀' if score >= 80 else '良好' if score >= 70 else '一般' if score >= 60 else '较差'
        }
    
    def assess_moat_strength(self, company_data):
        """评估护城河强度"""
        score = 0
        factors = []
        
        # 行业地位 (权重40%)
        if company_data['industry'] == '白酒':
            score += 85  # 白酒行业护城河强
            factors.append('白酒行业品牌护城河深厚')
        elif company_data['industry'] == '银行':
            score += 75  # 银行业有牌照护城河
            factors.append('银行业准入门槛高')
        
        # 盈利能力持续性 (权重30%)
        roe_std = np.std(company_data['roes'])
        if roe_std < 5:
            score += 80
            factors.append('盈利能力稳定')
        
        # 市场地位 (权重30%)
        if '龙头' in company_data['description'] or '绝对' in company_data['description']:
            score += 90
            factors.append('行业龙头地位稳固')
        
        return {
            'score': round(score, 2),
            'factors': factors,
            'level': '强' if score >= 80 else '中等' if score >= 60 else '弱'
        }
    
    def calculate_valuation_score(self, company_data):
        """计算估值合理性"""
        # 简化的估值评分
        industry = company_data['industry']
        
        if industry == '白酒':
            # 白酒合理PE 25-35倍
            pe_estimate = company_data['market_cap'] / 300  # 假设净利润300亿
            if 25 <= pe_estimate <= 35:
                return {'score': 85, 'pe': pe_estimate, 'assessment': '合理'}
            elif pe_estimate > 35:
                return {'score': 60, 'pe': pe_estimate, 'assessment': '偏高'}
            else:
                return {'score': 75, 'pe': pe_estimate, 'assessment': '偏低'}
        
        elif industry == '银行':
            # 银行合理PE 5-8倍
            pe_estimate = company_data['market_cap'] / 400  # 假设净利润400亿
            if 5 <= pe_estimate <= 8:
                return {'score': 85, 'pe': pe_estimate, 'assessment': '合理'}
            elif pe_estimate > 8:
                return {'score': 55, 'pe': pe_estimate, 'assessment': '偏高'}
            else:
                return {'score': 80, 'pe': pe_estimate, 'assessment': '偏低'}
        
        return {'score': 70, 'pe': 0, 'assessment': '需具体分析'}
    
    def generate_final_report(self, symbol):
        """生成最终分析报告"""
        if symbol not in self.demo_companies:
            return {"error": "股票代码不存在，请使用以下代码：000858, 600519, 000001, 600036"}
        
        company = self.demo_companies[symbol]
        
        # 计算各项评分
        survival_years = self.calculate_survival_years(company['listing_date'])
        financial_health = self.analyze_financial_health(company)
        moat_strength = self.assess_moat_strength(company)
        valuation = self.calculate_valuation_score(company)
        
        # 综合评分
        weights = {
            'survival': 0.15,
            'financial': 0.35,
            'moat': 0.25,
            'valuation': 0.25
        }
        
        final_score = (
            min(100, survival_years * 3) * weights['survival'] +
            financial_health['score'] * weights['financial'] +
            moat_strength['score'] * weights['moat'] +
            valuation['score'] * weights['valuation']
        )
        
        # 投资建议
        if final_score >= 85:
            recommendation = "🏆 强烈推荐长期持有"
            holding_period = "10年以上"
            risk_level = "低风险"
        elif final_score >= 75:
            recommendation = "⭐ 推荐长期持有"
            holding_period = "7-10年"
            risk_level = "中低风险"
        elif final_score >= 65:
            recommendation = "🔍 可以持有，需观察"
            holding_period = "5-7年"
            risk_level = "中等风险"
        elif final_score >= 55:
            recommendation = "⚠️ 谨慎持有"
            holding_period = "3-5年"
            risk_level = "中高风险"
        else:
            recommendation = "❌ 不建议长期持有"
            holding_period = "不建议"
            risk_level = "高风险"
        
        return {
            'company': {
                'symbol': symbol,
                'name': company['name'],
                'industry': company['industry'],
                'survival_years': round(survival_years, 1),
                'market_cap': company['market_cap']
            },
            'analysis': {
                'survival_analysis': {
                    'years': round(survival_years, 1),
                    'category': '老牌公司' if survival_years >= 20 else '成熟公司' if survival_years >= 15 else '成长公司'
                },
                'financial_health': financial_health,
                'moat_strength': moat_strength,
                'valuation': valuation
            },
            'final_assessment': {
                'overall_score': round(final_score, 2),
                'recommendation': recommendation,
                'risk_level': risk_level,
                'holding_period': holding_period,
                'key_strengths': [
                    f"ROE: {np.mean(company['roes']):.1f}%",
                    f"净利润增长: {np.mean(company['profit_growth']):.1f}%",
                    f"毛利率: {company['gross_margin']:.1f}%",
                    f"分红率: {company['dividend_yield']:.1f}%"
                ]
            }
        }
    
    def print_analysis(self, symbol):
        """打印分析报告"""
        result = self.generate_final_report(symbol)
        
        if 'error' in result:
            print(result['error'])
            return
        
        company = result['company']
        assessment = result['final_assessment']
        
        print("\n" + "="*70)
        print("🏆 公司长期持有价值分析报告")
        print("="*70)
        
        print(f"\n📊 公司信息：")
        print(f"   股票代码：{company['symbol']}")
        print(f"   公司名称：{company['name']}")
        print(f"   所属行业：{company['industry']}")
        print(f"   上市年限：{company['survival_years']}年")
        print(f"   市值规模：{company['market_cap']}亿元")
        
        print(f"\n🎯 最终评估：")
        print(f"   综合评分：{assessment['overall_score']}分")
        print(f"   投资建议：{assessment['recommendation']}")
        print(f"   风险等级：{assessment['risk_level']}")
        print(f"   建议持有：{assessment['holding_period']}")
        
        print(f"\n💪 核心优势：")
        for strength in assessment['key_strengths']:
            print(f"   • {strength}")
        
        print("\n" + "="*70)

def main():
    """主函数"""
    analyzer = SimpleLongTermAnalyzer()
    
    print("🎯 长期持有价值分析工具")
    print("="*50)
    print("可用的股票代码：")
    for code, info in analyzer.demo_companies.items():
        print(f"   {code} - {info['name']} ({info['industry']})")
    
    while True:
        symbol = input("\n请输入股票代码（如000858）或输入q退出: ").strip()
        
        if symbol.lower() == 'q':
            break
        
        if symbol in analyzer.demo_companies:
            analyzer.print_analysis(symbol)
        else:
            print("❌ 股票代码不存在，请重新输入")

if __name__ == "__main__":
    main()
