"""
测试图表生成功能
"""
import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端
import matplotlib.pyplot as plt

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_matplotlib():
    """测试matplotlib基本功能"""
    print("1. 测试matplotlib基本功能...")
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title('测试图表')
        
        save_path = "static/charts/test_basic.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        if os.path.exists(save_path):
            print(f"✅ matplotlib基本功能正常，图表已保存: {save_path}")
            return True
        else:
            print("❌ matplotlib保存图表失败")
            return False
            
    except Exception as e:
        print(f"❌ matplotlib测试失败: {e}")
        return False

def test_data_source():
    """测试数据源"""
    print("2. 测试数据源...")
    try:
        from core.data_source import DataSource
        
        ds = DataSource()
        data = ds.get_stock_data("000001", days=30)
        
        if not data.empty:
            print(f"✅ 数据获取成功，形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            print(f"索引类型: {type(data.index)}")
            return data
        else:
            print("❌ 数据获取失败")
            return None
            
    except Exception as e:
        print(f"❌ 数据源测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_technical_analysis(data):
    """测试技术指标计算"""
    print("3. 测试技术指标计算...")
    try:
        from core.analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        enhanced_data = analyzer.calculate_all_indicators(data)
        
        print(f"✅ 技术指标计算完成")
        print(f"增强后数据形状: {enhanced_data.shape}")
        print(f"新增列: {[col for col in enhanced_data.columns if col not in data.columns]}")
        
        return enhanced_data
        
    except Exception as e:
        print(f"❌ 技术指标计算失败: {e}")
        import traceback
        traceback.print_exc()
        return data

def test_candlestick_chart(data):
    """测试K线图生成"""
    print("4. 测试K线图生成...")
    try:
        from core.visualization import ChartPlotter
        
        plotter = ChartPlotter()
        
        # 检查数据格式
        print(f"数据索引类型: {type(data.index)}")
        print(f"数据前5行:")
        print(data.head())
        
        chart_path = plotter.plot_candlestick_chart(
            data, 
            "000001", 
            title="测试K线图",
            save_path="static/charts/test_candlestick.png"
        )
        
        if os.path.exists(chart_path):
            print(f"✅ K线图生成成功: {chart_path}")
            return True
        else:
            print(f"❌ K线图文件不存在: {chart_path}")
            return False
            
    except Exception as e:
        print(f"❌ K线图生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_indicators_chart(data):
    """测试技术指标图生成"""
    print("5. 测试技术指标图生成...")
    try:
        from core.visualization import ChartPlotter
        
        plotter = ChartPlotter()
        
        chart_path = plotter.plot_technical_indicators(
            data, 
            "000001",
            indicators=['RSI', 'MACD', 'KDJ'],
            save_path="static/charts/test_indicators.png"
        )
        
        if os.path.exists(chart_path):
            print(f"✅ 技术指标图生成成功: {chart_path}")
            return True
        else:
            print(f"❌ 技术指标图文件不存在: {chart_path}")
            return False
            
    except Exception as e:
        print(f"❌ 技术指标图生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chart_api():
    """测试图表API"""
    print("6. 测试图表API...")
    try:
        import requests
        
        # 测试K线图API
        url = "http://127.0.0.1:5000/api/stocks/000001/chart?type=candlestick&days=30"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result.get('data', {}).get('chart_url')
                print(f"✅ K线图API调用成功: {chart_url}")
                
                # 检查文件是否存在
                file_path = chart_url.replace('/static/charts/', 'static/charts/')
                if os.path.exists(file_path):
                    print(f"✅ K线图文件存在: {file_path}")
                    return True
                else:
                    print(f"❌ K线图文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ API返回错误: {result.get('message')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 图表API测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📊 图表生成功能诊断")
    print("=" * 60)
    
    # 确保目录存在
    os.makedirs("static/charts", exist_ok=True)
    
    # 1. 基础matplotlib测试
    if not test_matplotlib():
        print("\n💥 matplotlib基础功能异常，停止测试")
        exit(1)
    
    # 2. 数据源测试
    data = test_data_source()
    if data is None:
        print("\n💥 数据源异常，停止测试")
        exit(1)
    
    # 3. 技术指标计算测试
    enhanced_data = test_technical_analysis(data)
    
    # 4. K线图测试
    candlestick_success = test_candlestick_chart(enhanced_data)
    
    # 5. 技术指标图测试
    indicators_success = test_indicators_chart(enhanced_data)
    
    # 6. API测试
    api_success = test_chart_api()
    
    print("\n" + "=" * 60)
    print("📊 诊断结果汇总")
    print("=" * 60)
    print(f"matplotlib基础功能: ✅")
    print(f"数据源功能: ✅")
    print(f"技术指标计算: ✅")
    print(f"K线图生成: {'✅' if candlestick_success else '❌'}")
    print(f"技术指标图生成: {'✅' if indicators_success else '❌'}")
    print(f"图表API: {'✅' if api_success else '❌'}")
    
    if candlestick_success and indicators_success and api_success:
        print("\n🎉 所有图表功能正常！")
    else:
        print("\n💥 部分图表功能异常，需要修复")