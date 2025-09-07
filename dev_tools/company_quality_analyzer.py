"""
优质公司深度分析工具
基于财务数据、行业地位、成长性等多维度评估公司质量
"""
import pandas as pd
import numpy as np
import sqlite3
import json
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from core.data_source import StockDataFetcher
from utils.logger import logger

class CompanyQualityAnalyzer:
    """公司质量分析器"""
    
    def __init__(self, db_path="data/finance_data.db"):
        self.db_path = db_path
        self.fetcher = StockDataFetcher()
        
    def analyze_company_quality(self, symbol):
        """深度分析单家公司质量"""
        logger.info(f"开始分析 {symbol} 的公司质量...")
        
        analysis = {
            'symbol': symbol,
            'basic_info': {},
            'financial_health': {},
            'growth_potential': {},
            'risk_assessment': {},
            'long_term_score': 0,
            'recommendation': ''
        }
        
        try:
            # 获取基础信息
            analysis['basic_info'] = self._get_basic_info(symbol)
            
            # 财务健康度分析
            analysis['financial_health'] = self._analyze_financial_health(symbol)
            
            # 成长性分析
            analysis['growth_potential'] = self._analyze_growth_potential(symbol)
            
            # 风险评估
            analysis['risk_assessment'] = self._assess_risk(symbol)
            
            # 计算综合评分
            analysis['long_term_score'] = self._calculate_long_term_score(analysis)
            
            # 投资建议
            analysis['recommendation'] = self._generate_recommendation(analysis)
            
        except Exception as e:
            logger.error(f"分析 {symbol} 时出错: {e}")
            
        return analysis
    
    def _get_basic_info(self, symbol):
        """获取公司基础信息"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = """
                SELECT s.symbol, s.name, s.industry, s.area, s.market,
                       a.totalAssets, a.outstanding, a.totalAssets, a.liquidAssets,
                       a.fixedAssets, a.reserved, a.reservedPerShare, a.esp,
                       a.bvps, a.pb, a.timeToMarket
                FROM stock_info s
                LEFT JOIN stock_basics a ON s.symbol = a.symbol
                WHERE s.symbol = ?
            """
            df = pd.read_sql_query(query, conn, params=[symbol])
            if not df.empty:
                return df.iloc[0].to_dict()
            return {}
        finally:
            conn.close()
    
    def _analyze_financial_health(self, symbol):
        """分析财务健康度"""
        conn = sqlite3.connect(self.db_path)
        try:
            # 获取最近3年财务数据
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y%m%d')
            
            query = """
                SELECT * FROM financial_data 
                WHERE symbol = ? AND report_date >= ? AND report_date <= ?
                ORDER BY report_date DESC
            """
            df = pd.read_sql_query(query, conn, params=[symbol, start_date, end_date])
            
            if df.empty:
                return {'score': 0, 'details': '无财务数据'}
            
            health_metrics = {}
            
            # 盈利能力
            if 'net_profit_margin' in df.columns:
                npm = df['net_profit_margin'].dropna()
                if not npm.empty:
                    health_metrics['profitability'] = {
                        'avg_margin': npm.mean(),
                        'trend': 'stable' if npm.std() < 5 else 'volatile',
                        'score': min(100, max(0, npm.mean() * 10))
                    }
            
            # 偿债能力
            if 'debt_to_asset_ratio' in df.columns:
                debt_ratio = df['debt_to_asset_ratio'].dropna()
                if not debt_ratio.empty:
                    avg_debt = debt_ratio.mean()
                    health_metrics['solvency'] = {
                        'debt_ratio': avg_debt,
                        'risk_level': 'low' if avg_debt < 0.3 else 'medium' if avg_debt < 0.6 else 'high',
                        'score': max(0, 100 - avg_debt * 100)
                    }
            
            # 运营效率
            if 'roa' in df.columns:
                roa = df['roa'].dropna()
                if not roa.empty:
                    health_metrics['efficiency'] = {
                        'avg_roa': roa.mean(),
                        'score': min(100, max(0, roa.mean() * 100))
                    }
            
            # 综合财务健康评分
            scores = [m.get('score', 0) for m in health_metrics.values()]
            overall_score = np.mean(scores) if scores else 0
            
            return {
                'score': overall_score,
                'details': health_metrics
            }
            
        finally:
            conn.close()
    
    def _analyze_growth_potential(self, symbol):
        """分析成长性"""
        conn = sqlite3.connect(self.db_path)
        try:
            # 获取历史股价数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1825)  # 5年
            
            query = """
                SELECT date, close FROM stock_daily 
                WHERE symbol = ? AND date >= ? AND date <= ?
                ORDER BY date
            """
            df = pd.read_sql_query(query, conn, params=[
                symbol, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            ])
            
            if len(df) < 100:  # 数据不足
                return {'score': 0, 'details': '数据不足'}
            
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 计算增长指标
            initial_price = df.iloc[0]['close']
            current_price = df.iloc[-1]['close']
            
            total_return = (current_price - initial_price) / initial_price * 100
            annual_return = (current_price / initial_price) ** (252 / len(df)) - 1
            
            # 计算波动率
            df['returns'] = df['close'].pct_change()
            volatility = df['returns'].std() * np.sqrt(252) * 100
            
            # 风险调整后收益
            sharpe_ratio = annual_return / (volatility / 100) if volatility > 0 else 0
            
            growth_score = min(100, max(0, 
                annual_return * 50 + sharpe_ratio * 10 + 50
            ))
            
            return {
                'score': growth_score,
                'details': {
                    'total_return': total_return,
                    'annual_return': annual_return * 100,
                    'volatility': volatility,
                    'sharpe_ratio': sharpe_ratio
                }
            }
            
        finally:
            conn.close()
    
    def _assess_risk(self, symbol):
        """风险评估"""
        risk_factors = {
            'price_volatility': self._calculate_price_risk(symbol),
            'financial_risk': self._calculate_financial_risk(symbol),
            'market_risk': self._calculate_market_risk(symbol),
            'sector_risk': self._calculate_sector_risk(symbol)
        }
        
        # 综合风险评分 (0-100, 分数越低风险越高)
        risk_scores = [r['score'] for r in risk_factors.values()]
        overall_risk = np.mean(risk_scores) if risk_scores else 50
        
        return {
            'score': overall_risk,
            'details': risk_factors,
            'risk_level': 'low' if overall_risk > 70 else 'medium' if overall_risk > 40 else 'high'
        }
    
    def _calculate_price_risk(self, symbol):
        """计算价格风险"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = """
                SELECT close FROM stock_daily 
                WHERE symbol = ? AND date >= date('now', '-1 year')
                ORDER BY date
            """
            df = pd.read_sql_query(query, conn, params=[symbol])
            
            if len(df) < 50:
                return {'score': 50, 'details': '数据不足'}
            
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            
            # 波动率评分 (波动率越低分数越高)
            volatility_score = max(0, min(100, 100 - volatility * 100))
            
            return {
                'score': volatility_score,
                'details': {'volatility': volatility * 100}
            }
        finally:
            conn.close()
    
    def _calculate_financial_risk(self, symbol):
        """计算财务风险"""
        # 简化的财务风险评估
        return {'score': 60, 'details': '基础评估'}
    
    def _calculate_market_risk(self, symbol):
        """计算市场风险"""
        # 简化的市场风险评估
        return {'score': 55, 'details': '基础评估'}
    
    def _calculate_sector_risk(self, symbol):
        """计算行业风险"""
        # 简化的行业风险评估
        return {'score': 65, 'details': '基础评估'}
    
    def _calculate_long_term_score(self, analysis):
        """计算长期持有综合评分"""
        weights = {
            'financial_health': 0.3,
            'growth_potential': 0.25,
            'risk_assessment': 0.25,
            'survival_years': 0.2
        }
        
        scores = [
            analysis['financial_health'].get('score', 0) * weights['financial_health'],
            analysis['growth_potential'].get('score', 0) * weights['growth_potential'],
            analysis['risk_assessment'].get('score', 0) * weights['risk_assessment'],
            min(100, analysis['basic_info'].get('survival_years', 0) * 5) * weights['survival_years']
        ]
        
        return sum(scores)
    
    def _generate_recommendation(self, analysis):
        """生成投资建议"""
        score = analysis['long_term_score']
        
        if score >= 80:
            return "强烈推荐长期持有 - 具备优秀基本面和成长潜力"
        elif score >= 70:
            return "推荐持有 - 基本面良好，具备长期价值"
        elif score >= 60:
            return "谨慎持有 - 需要进一步观察关键指标"
        else:
            return "不建议长期持有 - 风险较高或基本面一般"

if __name__ == "__main__":
    analyzer = CompanyQualityAnalyzer()
    
    # 示例分析
    symbols = ['000001', '000858', '600519']  # 平安银行、五粮液、贵州茅台
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"分析 {symbol} 的长期持有价值")
        print('='*50)
        
        result = analyzer.analyze_company_quality(symbol)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))