"""
调试K线图标注功能
检查为什么标注没有显示
"""
import os
from core.visualization import ChartPlotter
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer

def debug_chart_generation():
    """调试图表生成过程"""
    print("🔍 开始调试K线图标注功能")
    
    # 1. 初始化组件
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    chart_plotter = ChartPlotter()
    
    # 2. 获取数据
    symbol = "000858"
    days = 60
    print(f"📊 获取股票数据: {symbol}, {days}天")
    
    df = data_source.get_stock_data(symbol, days=days)
    print(f"   数据行数: {len(df)}")
    print(f"   数据列: {list(df.columns)}")
    print(f"   数据范围: {df.index[0]} 到 {df.index[-1]}")
    print(f"   价格范围: 最高{df['high'].max():.2f}, 最低{df['low'].min():.2f}")
    
    # 3. 添加技术指标
    df = analyzer.calculate_all_indicators(df)
    
    # 4. 测试三种标注模式
    test_modes = [
        ("global", "全局最高低点"),
        ("local", "局部最高低点"),
        ("none", "不标注")
    ]
    
    for mode, description in test_modes:
        print(f"\n🎯 测试{description}标注模式: {mode}")
        
        try:
            # 生成图表
            chart_path = chart_plotter.plot_candlestick_chart(
                df, 
                symbol, 
                mark_extremes=mode,
                title=f"{symbol} K线图 - {description}"
            )
            
            print(f"   ✅ 图表生成成功: {chart_path}")
            
            # 检查文件
            if os.path.exists(chart_path):
                file_size = os.path.getsize(chart_path)
                print(f"   📁 文件大小: {file_size:,} bytes")
                
                # 如果是全局标注模式，详细检查
                if mode == "global":
                    print(f"   🎯 全局最高点: 第{df['high'].idxmax()}行, 价格{df['high'].max():.2f}")
                    print(f"   🎯 全局最低点: 第{df['low'].idxmin()}行, 价格{df['low'].min():.2f}")
                    
                elif mode == "local":
                    # 检查局部极值点
                    from scipy.signal import argrelextrema
                    import numpy as np
                    
                    highs = df['high'].values
                    lows = df['low'].values
                    
                    high_peaks = argrelextrema(highs, np.greater, order=5)[0]
                    low_peaks = argrelextrema(lows, np.less, order=5)[0]
                    
                    print(f"   📍 发现局部高点: {len(high_peaks)}个")
                    print(f"   📍 发现局部低点: {len(low_peaks)}个")
                    
                    if len(high_peaks) > 0:
                        print(f"   📍 局部高点价格: {[highs[i] for i in high_peaks[:3]]}")
                    if len(low_peaks) > 0:
                        print(f"   📍 局部低点价格: {[lows[i] for i in low_peaks[:3]]}")
            else:
                print(f"   ❌ 文件不存在: {chart_path}")
                
        except Exception as e:
            print(f"   💥 生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎯 调试完成！请检查生成的图片文件。")

if __name__ == "__main__":
    debug_chart_generation()