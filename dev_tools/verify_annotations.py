"""
验证K线图标注功能是否真的在工作
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer
from core.visualization import ChartPlotter
import os

def verify_annotations():
    """验证标注功能"""
    print("🔍 验证K线图标注功能")
    print("="*50)
    
    # 1. 获取数据
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    chart_plotter = ChartPlotter()
    
    symbol = "000858"
    df = data_source.get_stock_data(symbol, days=30)
    df = analyzer.calculate_all_indicators(df)
    
    print(f"数据信息:")
    print(f"  行数: {len(df)}")
    print(f"  最高价: {df['high'].max():.2f}")
    print(f"  最低价: {df['low'].min():.2f}")
    print(f"  价格范围: {df['high'].max() - df['low'].min():.2f}")
    
    # 2. 手动测试标注逻辑
    print(f"\n手动测试标注逻辑:")
    
    # 获取最高低点位置
    high_idx = df['high'].idxmax()
    low_idx = df['low'].idxmin()
    high_pos = df.index.get_loc(high_idx)
    low_pos = df.index.get_loc(low_idx)
    
    print(f"  全局最高点: 位置{high_pos}, 日期{high_idx}, 价格{df['high'].max():.2f}")
    print(f"  全局最低点: 位置{low_pos}, 日期{low_idx}, 价格{df['low'].min():.2f}")
    
    # 3. 测试标注方法
    print(f"\n测试标注方法:")
    try:
        # 创建简单的测试图
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # 绘制简单的价格线
        dates = pd.to_datetime(df.index)
        ax.plot(dates, df['close'], label='收盘价', linewidth=2)
        
        # 调用标注方法
        chart_plotter._mark_global_extremes(ax, df, dates)
        
        ax.set_title("测试标注功能", fontsize=16)
        ax.set_ylabel("价格")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 保存测试图
        test_path = "static/charts/test_annotations.png"
        plt.savefig(test_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(test_path):
            size = os.path.getsize(test_path)
            print(f"  ✅ 测试图生成成功: {test_path}")
            print(f"  📊 文件大小: {size:,} bytes")
        else:
            print(f"  ❌ 测试图生成失败")
            
    except Exception as e:
        print(f"  💥 标注方法测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 生成完整的K线图
    print(f"\n生成完整K线图:")
    try:
        chart_path = chart_plotter.plot_candlestick_chart(
            df, 
            symbol, 
            mark_extremes="global",
            title=f"{symbol} K线图 - 验证标注"
        )
        
        if os.path.exists(chart_path):
            size = os.path.getsize(chart_path)
            print(f"  ✅ K线图生成成功: {chart_path}")
            print(f"  📊 文件大小: {size:,} bytes")
            
            # 对比无标注的版本
            chart_path_none = chart_plotter.plot_candlestick_chart(
                df, 
                symbol, 
                mark_extremes="none",
                title=f"{symbol} K线图 - 无标注"
            )
            
            if os.path.exists(chart_path_none):
                size_none = os.path.getsize(chart_path_none)
                print(f"  📊 无标注版本: {chart_path_none}")
                print(f"  📊 无标注大小: {size_none:,} bytes")
                print(f"  📊 大小差异: {size - size_none:,} bytes")
                
                if size > size_none:
                    print(f"  ✅ 有标注版本更大，可能包含标注")
                else:
                    print(f"  ⚠️  大小相同，标注可能没有生效")
        else:
            print(f"  ❌ K线图生成失败")
            
    except Exception as e:
        print(f"  💥 K线图生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "="*50)
    print(f"✅ 验证完成")

if __name__ == "__main__":
    verify_annotations()