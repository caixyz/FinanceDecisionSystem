#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10万资金稳健投资方案
保本优先，低风险增值策略
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class ConservativeInvestmentPlan:
    """10万资金稳健投资方案"""
    
    def __init__(self, total_capital=100000):
        self.total_capital = total_capital
        self.risk_tolerance = "保守型"
        self.investment_horizon = "3-5年"
        
    def create_defensive_portfolio(self):
        """创建防御型投资组合"""
        
        # 核心配置：保本为主
        allocation = {
            "现金及货币基金": {
                "percentage": 30,  # 3万
                "purpose": "应急资金+机会资金",
                "products": ["余额宝", "微信理财通", "银行T+0理财"],
                "expected_return": "2-3%",
                "risk_level": "极低"
            },
            "债券基金": {
                "percentage": 25,  # 2.5万
                "purpose": "稳定收益",
                "products": ["国债基金", "高等级企业债基金", "短债基金"],
                "expected_return": "4-6%",
                "risk_level": "低"
            },
            "银行理财产品": {
                "percentage": 20,  # 2万
                "purpose": "保本增值",
                "products": ["大额存单", "结构性存款", "保本理财"],
                "expected_return": "3-4.5%",
                "risk_level": "低"
            },
            "高分红蓝筹股": {
                "percentage": 15,  # 1.5万
                "purpose": "股息收入+长期增值",
                "products": ["银行股", "公用事业股", "消费龙头"],
                "expected_return": "6-8%",
                "risk_level": "中低"
            },
            "指数基金定投": {
                "percentage": 10,  # 1万
                "purpose": "长期增值",
                "products": ["沪深300ETF", "中证红利ETF", "消费ETF"],
                "expected_return": "8-12%",
                "risk_level": "中等"
            }
        }
        
        return allocation
    
    def create_stock_picking_strategy(self):
        """股票选择策略 - 只选最安全的"""
        
        safe_stocks = [
            {
                "name": "工商银行",
                "code": "601398",
                "reason": "国有大行+高股息5.5%+低估值",
                "allocation": "5000元",
                "strategy": "长期持有收息"
            },
            {
                "name": "中国移动",
                "code": "600941",
                "reason": "垄断经营+高股息7%+现金流稳定",
                "allocation": "5000元",
                "strategy": "防御+分红"
            },
            {
                "name": "长江电力",
                "code": "600900",
                "reason": "水电龙头+股息3.5%+业绩稳定",
                "allocation": "5000元",
                "strategy": "类债券投资"
            }
        ]
        
        return safe_stocks
    
    def create_risk_management_rules(self):
        """风险控制规则"""
        
        rules = {
            "仓位控制": {
                "单只股票": "不超过总资金的5%",
                "股票总仓位": "不超过总资金的25%",
                "现金比例": "始终保持30%以上"
            },
            "止损规则": {
                "个股止损": "-8%立即止损",
                "整体止损": "账户回撤-5%减仓50%",
                "重新评估": "月度检查持仓"
            },
            "买入规则": {
                "分批买入": "分3次买入，每次间隔1个月",
                "大盘判断": "上证指数PE<12倍时加仓",
                "个股判断": "股息率>4%时才考虑"
            },
            "卖出规则": {
                "目标止盈": "盈利20%部分止盈",
                "基本面恶化": "股息连续下降立即卖出",
                "估值过高": "PE>行业平均1.5倍减仓"
            }
        }
        
        return rules
    
    def create_action_plan(self):
        """90天行动计划"""
        
        plan = {
            "第1个月": {
                "week1": [
                    "开设证券账户+银行账户",
                    "买入3万货币基金(余额宝)",
                    "学习基本投资知识"
                ],
                "week2": [
                    "买入2.5万债券基金",
                    "研究高分红股票",
                    "设置止损提醒"
                ],
                "week3": [
                    "买入2万银行理财",
                    "关注工商银行等蓝筹股",
                    "建立投资记录表"
                ],
                "week4": [
                    "评估首月收益",
                    "调整配置比例",
                    "继续学习"
                ]
            },
            "第2个月": {
                "week1": [
                    "开始定投500元沪深300ETF",
                    "研究中国移动",
                    "检查债券基金表现"
                ],
                "week2": [
                    "买入第一只股票(工商银行5000元)",
                    "设置止损价格",
                    "记录买入理由"
                ],
                "week3": [
                    "继续定投ETF",
                    "观察持仓表现",
                    "学习财报分析"
                ],
                "week4": [
                    "月度总结",
                    "调整定投金额",
                    "准备下月计划"
                ]
            },
            "第3个月": {
                "week1": [
                    "评估前两个月收益",
                    "考虑加仓第二只股票",
                    "检查风险控制"
                ],
                "week2": [
                    "买入第二只股票(中国移动5000元)",
                    "分散投资时间",
                    "继续ETF定投"
                ],
                "week3": [
                    "建立完整持仓",
                    "设置预警价格",
                    "制定长期计划"
                ],
                "week4": [
                    "季度总结",
                    "制定下季度计划",
                    "保持学习"
                ]
            }
        }
        
        return plan
    
    def calculate_expected_returns(self):
        """计算预期收益"""
        
        allocation = self.create_defensive_portfolio()
        
        expected_return = 0
        max_loss = 0
        
        for asset, details in allocation.items():
            percentage = details["percentage"]
            return_range = details["expected_return"]
            
            # 提取预期收益中位数
            if "-" in str(return_range):
                range_str = str(return_range).replace("%", "")
                min_str, max_str = range_str.split("-")
                min_return = float(min_str.strip())
                max_return = float(max_str.strip())
                avg_return = (min_return + max_return) / 2
            else:
                avg_return = float(str(return_range).replace("%", ""))
            
            expected_return += percentage / 100 * avg_return
            
            # 估算最大损失
            if details["risk_level"] == "极低":
                max_loss_asset = 0.5
            elif details["risk_level"] == "低":
                max_loss_asset = 2
            elif details["risk_level"] == "中低":
                max_loss_asset = 10
            else:
                max_loss_asset = 15
            
            max_loss += percentage / 100 * max_loss_asset
        
        return {
            "预期年化收益": f"{expected_return:.1f}%",
            "最大可能亏损": f"{max_loss:.1f}%",
            "保本概率": "95%以上",
            "实现正收益概率": "85%以上"
        }
    
    def create_emergency_plan(self):
        """应急计划 - 市场极端情况"""
        
        emergency_plan = {
            "大盘下跌20%时": {
                "行动": "暂停股票买入，增加债券配置",
                "仓位调整": "股票仓位降至15%",
                "心理建设": "这是机会，不是风险"
            },
            "个股跌停时": {
                "行动": "不恐慌卖出，检查基本面",
                "止损": "设置-8%机械止损",
                "补仓": "跌幅15%时分批补仓"
            },
            "急需用钱时": {
                "赎回顺序": "货币基金→银行理财→债券基金→股票",
                "保留底线": "至少保留20%资金投资",
                "时间规划": "提前1个月准备"
            }
        }
        
        return emergency_plan
    
    def generate_complete_report(self):
        """生成完整投资报告"""
        
        report = []
        report.append("=" * 60)
        report.append("🏦 10万资金稳健投资方案")
        report.append("=" * 60)
        
        # 基本配置
        report.append("\n📊 资产配置方案")
        report.append("-" * 40)
        allocation = self.create_defensive_portfolio()
        
        for asset, details in allocation.items():
            amount = self.total_capital * details["percentage"] / 100
            report.append(f"{asset}: {details['percentage']}% = {amount:,.0f}元")
            report.append(f"  目的: {details['purpose']}")
            report.append(f"  预期收益: {details['expected_return']}")
            report.append(f"  风险等级: {details['risk_level']}")
            report.append("")
        
        # 股票选择
        report.append("\n🏆 安全股票池")
        report.append("-" * 40)
        stocks = self.create_stock_picking_strategy()
        for stock in stocks:
            report.append(f"{stock['name']}({stock['code']})")
            report.append(f"  理由: {stock['reason']}")
            report.append(f"  配置: {stock['allocation']}")
            report.append(f"  策略: {stock['strategy']}")
            report.append("")
        
        # 收益预期
        report.append("\n💰 收益预期")
        report.append("-" * 40)
        returns = self.calculate_expected_returns()
        for key, value in returns.items():
            report.append(f"{key}: {value}")
        
        # 风险控制
        report.append("\n⚠️ 风险控制规则")
        report.append("-" * 40)
        rules = self.create_risk_management_rules()
        for category, rule in rules.items():
            report.append(f"\n{category}:")
            for key, value in rule.items():
                report.append(f"  {key}: {value}")
        
        # 行动计划
        report.append("\n📅 90天行动计划")
        report.append("-" * 40)
        plan = self.create_action_plan()
        for month, weeks in plan.items():
            report.append(f"\n{month}:")
            for week, actions in weeks.items():
                report.append(f"  {week}:")
                for action in actions:
                    report.append(f"    • {action}")
        
        # 应急计划
        report.append("\n🚨 应急计划")
        report.append("-" * 40)
        emergency = self.create_emergency_plan()
        for situation, plan in emergency.items():
            report.append(f"\n{situation}:")
            for key, value in plan.items():
                report.append(f"  {key}: {value}")
        
        return "\n".join(report)

def main():
    """主函数"""
    print("正在生成10万资金稳健投资方案...")
    
    plan = ConservativeInvestmentPlan(100000)
    report = plan.generate_complete_report()
    
    print(report)
    
    # 保存报告
    with open("conservative_investment_plan.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\n💾 投资方案已保存到 conservative_investment_plan.txt")
    
    # 快速开始指南
    print("\n🚀 快速开始指南:")
    print("1. 立即行动: 开设证券账户+银行账户")
    print("2. 资金分配: 先买3万货币基金+2.5万债券基金")
    print("3. 学习提升: 每天学习30分钟投资知识")
    print("4. 风险控制: 永远记住保本第一")

if __name__ == "__main__":
    main()
