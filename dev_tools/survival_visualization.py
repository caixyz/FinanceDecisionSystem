"""
长期存活股票可视化分析工具
生成图表和交互式报告
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import os
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class SurvivalVisualizer:
    """存活股票可视化分析器"""
    
    def __init__(self, data_file="data/long_term_survivors.csv"):
        self.data_file = data_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        if os.path.exists(self.data_file):
            self.df = pd.read_csv(self.data_file)
            # 转换日期列
            self.df['first_trade_date'] = pd.to_datetime(self.df['first_trade_date'])
            self.df['last_trade_date'] = pd.to_datetime(self.df['last_trade_date'])
        else:
            print(f"数据文件不存在: {self.data_file}")
    
    def create_survival_distribution_chart(self):
        """创建存活年限分布图"""
        if self.df is None:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 存活年限直方图
        ax1.hist(self.df['survival_years'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(x=10, color='red', linestyle='--', linewidth=2, label='10年线')
        ax1.axvline(x=20, color='green', linestyle='--', linewidth=2, label='20年线')
        ax1.set_xlabel('存活年限')
        ax1.set_ylabel('股票数量')
        ax1.set_title('股票存活年限分布')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 存活类别饼图
        category_counts = self.df['survival_category'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        wedges, texts, autotexts = ax2.pie(category_counts.values, 
                                          labels=category_counts.index,
                                          autopct='%1.1f%%',
                                          colors=colors)
        ax2.set_title('股票存活类别分布')
        
        plt.tight_layout()
        plt.savefig('data/survival_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("存活分布图已保存")
    
    def create_industry_analysis_chart(self):
        """创建行业分析图"""
        if self.df is None:
            return
        
        # 长期存活股票行业分布
        long_term_df = self.df[self.df['survival_years'] >= 10]
        
        if long_term_df.empty:
            print("无长期存活股票数据")
            return
        
        industry_counts = long_term_df['industry'].value_counts().head(15)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(industry_counts.index, industry_counts.values, color='lightcoral')
        
        # 添加数值标签
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                   f'{int(width)}', ha='left', va='center')
        
        ax.set_xlabel('股票数量')
        ax.set_title('长期存活股票行业分布TOP15')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig('data/industry_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("行业分布图已保存")
    
    def create_interactive_timeline(self):
        """创建交互式时间线"""
        if self.df is None:
            return
        
        # 创建时间线数据
        timeline_df = self.df[self.df['survival_years'] >= 15].copy()
        
        if timeline_df.empty:
            print("无足够长期数据")
            return
        
        # 按行业分组
        timeline_df = timeline_df.sort_values('first_trade_date')
        
        fig = px.scatter(timeline_df, 
                        x='first_trade_date', 
                        y='survival_years',
                        color='industry',
                        size='quality_score',
                        hover_data=['symbol', 'name', 'survival_years', 'quality_score'],
                        title='长期存活股票时间线分析',
                        labels={
                            'first_trade_date': '上市日期',
                            'survival_years': '存活年限',
                            'industry': '行业',
                            'quality_score': '质量评分'
                        })
        
        fig.update_layout(
            xaxis_title="上市日期",
            yaxis_title="存活年限(年)",
            height=600,
            showlegend=True
        )
        
        fig.write_html('data/survival_timeline.html')
        print("交互式时间线已保存")
    
    def create_quality_heatmap(self):
        """创建质量评分热力图"""
        if self.df is None:
            return
        
        # 创建透视表
        long_term_df = self.df[self.df['survival_years'] >= 10]
        
        if long_term_df.empty:
            print("无长期数据")
            return
        
        # 创建行业-存活类别热力图
        pivot_data = pd.crosstab(long_term_df['industry'], long_term_df['survival_category'])
        
        # 选择前15个行业
        top_industries = long_term_df['industry'].value_counts().head(15).index
        pivot_data = pivot_data.loc[top_industries]
        
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(pivot_data, annot=True, fmt='d', cmap='YlOrRd', ax=ax)
        ax.set_title('行业长期存活股票分布热力图')
        ax.set_xlabel('存活类别')
        ax.set_ylabel('行业')
        
        plt.tight_layout()
        plt.savefig('data/quality_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("质量热力图已保存")
    
    def create_comprehensive_report(self):
        """创建综合报告"""
        if self.df is None:
            return
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('存活年限分布', '行业分布', '质量评分', '活跃状态'),
            specs=[[{"type": "histogram"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # 存活年限分布
        fig.add_trace(
            go.Histogram(x=self.df['survival_years'], name='存活年限'),
            row=1, col=1
        )
        
        # 行业分布TOP10
        industry_counts = self.df[self.df['survival_years'] >= 10]['industry'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=industry_counts.values, y=industry_counts.index, orientation='h', name='行业'),
            row=1, col=2
        )
        
        # 质量评分散点图
        long_term_df = self.df[self.df['survival_years'] >= 10]
        fig.add_trace(
            go.Scatter(x=long_term_df['survival_years'], 
                      y=long_term_df['quality_score'],
                      mode='markers',
                      name='质量评分'),
            row=2, col=1
        )
        
        # 活跃状态饼图
        active_counts = self.df['is_active'].value_counts()
        fig.add_trace(
            go.Pie(labels=['活跃', '不活跃'], values=active_counts.values, name='活跃状态'),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="长期存活股票综合分析报告",
            height=800,
            showlegend=True
        )
        
        fig.write_html('data/comprehensive_report.html')
        print("综合报告已保存")
    
    def generate_all_charts(self):
        """生成所有图表"""
        if self.df is None:
            print("请先运行分析工具获取数据")
            return
        
        print("开始生成可视化图表...")
        
        # 创建数据目录
        os.makedirs('data', exist_ok=True)
        
        # 生成各种图表
        self.create_survival_distribution_chart()
        self.create_industry_analysis_chart()
        self.create_interactive_timeline()
        self.create_quality_heatmap()
        self.create_comprehensive_report()
        
        print("所有图表生成完成！")
        print("文件位置:")
        print("• 存活分布图: data/survival_distribution.png")
        print("• 行业分布图: data/industry_distribution.png")
        print("• 交互式时间线: data/survival_timeline.html")
        print("• 质量热力图: data/quality_heatmap.png")
        print("• 综合报告: data/comprehensive_report.html")

def main():
    """主函数"""
    visualizer = SurvivalVisualizer()
    visualizer.generate_all_charts()

if __name__ == "__main__":
    main()