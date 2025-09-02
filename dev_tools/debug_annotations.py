"""
调试标注问题 - 检查标注是否真的被调用
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer
import numpy as np

def test_annotation_directly():
    """直接测试标注功能"""
    print("🔍 直接测试标注功能")
    
    # 获取数据
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    
    symbol = "000858"
    df = data_source.get_stock_data(symbol, days=30)
    df = analyzer.calculate_all_indicators(df)
    
    print(f"数据概况:")
    print(f"  总行数: {len(df)}")
    print(f"  最高价: {df['high'].max():.2f} (第{df['high'].idxmax()}天)")
    print(f"  最低价: {df['low'].min():.2f} (第{df['low'].idxmin()}天)")
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # 准备数据
    dates = pd.to_datetime(df.index)
    
    print(f"\n绘制K线图:")
    
    # 绘制K线图 (简化版)
    for i in range(len(df)):
        date = dates[i]
        open_price = df['open'].iloc[i]
        high_price = df['high'].iloc[i]
        low_price = df['low'].iloc[i]
        close_price = df['close'].iloc[i]
        
        # 绘制影线
        ax.plot([date, date], [low_price, high_price], color='black', linewidth=1)
        
        # 绘制实体
        color = 'red' if close_price >= open_price else 'green'
        body_height = abs(close_price - open_price)
        bottom = min(open_price, close_price)
        ax.bar(date, body_height, bottom=bottom, color=color, alpha=0.8, width=0.6)
    
    print(f"  ✅ K线图绘制完成")
    
    # 手动添加标注
    print(f"\n添加标注:")
    
    # 获取最高低点
    high_idx = df['high'].idxmax()
    low_idx = df['low'].idxmin()
    high_pos = df.index.get_loc(high_idx)
    low_pos = df.index.get_loc(low_idx)
    
    high_date = dates[high_pos]
    high_price = df['high'].iloc[high_pos]
    low_date = dates[low_pos]
    low_price = df['low'].iloc[low_pos]
    
    price_range = high_price - low_price
    
    print(f"  最高点: {high_date.strftime('%Y-%m-%d')}, 价格: {high_price:.2f}")
    print(f"  最低点: {low_date.strftime('%Y-%m-%d')}, 价格: {low_price:.2f}")
    print(f"  价格范围: {price_range:.2f}")
    
    # 添加最高点标注
    annotation_high = ax.annotate(
        f'全局最高\\n{high_price:.2f}', 
        xy=(high_date, high_price), 
        xytext=(high_date, high_price + price_range * 0.08),
        fontsize=12, ha='center', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.8),
        arrowprops=dict(arrowstyle='->', color='red', lw=2)
    )
    print(f"  ✅ 添加最高点标注")
    
    # 添加最低点标注
    annotation_low = ax.annotate(
        f'全局最低\\n{low_price:.2f}', 
        xy=(low_date, low_price), 
        xytext=(low_date, low_price - price_range * 0.08),
        fontsize=12, ha='center', va='top',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8),
        arrowprops=dict(arrowstyle='->', color='green', lw=2)
    )
    print(f"  ✅ 添加最低点标注")
    
    # 设置图表
    ax.set_title(f'{symbol} K线图 - 测试标注', fontsize=16, fontweight='bold')
    ax.set_ylabel('价格', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # 保存图表
    save_path = "static/charts/debug_annotations.png"
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n💾 图表已保存: {save_path}")
    
    # 检查文件
    import os
    if os.path.exists(save_path):
        size = os.path.getsize(save_path)
        print(f"📊 文件大小: {size:,} bytes")
        
        # 验证标注是否真的在图上
        print(f"\n🎯 标注验证:")
        print(f"  标注对象创建成功: annotation_high = {type(annotation_high)}")
        print(f"  标注对象创建成功: annotation_low = {type(annotation_low)}")
        print(f"  标注文本: '{annotation_high.get_text()}'")
        print(f"  标注文本: '{annotation_low.get_text()}'")
        
        return True
    else:
        print(f"❌ 文件保存失败")
        return False

if __name__ == "__main__":
    success = test_annotation_directly()
    if success:
        print(f"\n🎉 标注功能测试成功！")
        print(f"📝 请检查生成的图片 static/charts/debug_annotations.png")
    else:
        print(f"\n💥 标注功能测试失败！")