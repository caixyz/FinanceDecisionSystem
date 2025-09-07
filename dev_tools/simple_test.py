#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试标注功能
"""
import matplotlib
matplotlib.use('Agg')

from core.visualization import ChartPlotter
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer

# 初始化
data_source = DataSource()
analyzer = TechnicalAnalyzer()
chart_plotter = ChartPlotter()

# 获取数据
symbol = "000858"
df = data_source.get_stock_data(symbol, days=30)
df = analyzer.calculate_all_indicators(df)

print(f"数据行数: {len(df)}")
print(f"最高价: {df['high'].max():.2f}")
print(f"最低价: {df['low'].min():.2f}")

# 测试全局标注
try:
    chart_path = chart_plotter.plot_candlestick_chart(
        df, symbol, mark_extremes="global"
    )
    print(f"✅ 全局标注成功: {chart_path}")
except Exception as e:
    print(f"❌ 全局标注失败: {e}")

# 测试局部标注
try:
    chart_path = chart_plotter.plot_candlestick_chart(
        df, symbol, mark_extremes="local"
    )
    print(f"✅ 局部标注成功: {chart_path}")
except Exception as e:
    print(f"❌ 局部标注失败: {e}")

print("测试完成")
