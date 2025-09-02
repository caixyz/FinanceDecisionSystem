"""
测试图表功能修复
"""
import requests
import time

def test_stock_analysis_with_charts():
    """测试股票分析和图表生成"""
    print("=" * 50)
    print("测试股票分析和图表生成功能")
    print("=" * 50)
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 1. 测试股票分析API
        print("1. 测试股票分析API...")
        analysis_url = f"{base_url}/api/stocks/000001/analysis?days=30"
        response = requests.get(analysis_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ 股票分析API正常")
                print(f"   股票: {result['data']['symbol']}")
                print(f"   当前价格: {result['data']['current_price']}")
                print(f"   趋势: {result['data']['trend']}")
            else:
                print(f"❌ 股票分析API错误: {result.get('message')}")
                return False
        else:
            print(f"❌ 股票分析API失败: {response.status_code}")
            return False
        
        # 2. 测试K线图生成API
        print("2. 测试K线图生成API...")
        candlestick_url = f"{base_url}/api/stocks/000001/chart?type=candlestick&days=30"
        response = requests.get(candlestick_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ K线图生成成功: {chart_url}")
                
                # 检查图片文件是否存在
                import os
                file_path = chart_url.replace('/static/charts/', 'static/charts/')
                if os.path.exists(file_path):
                    print(f"✅ K线图文件存在: {file_path}")
                else:
                    print(f"❌ K线图文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ K线图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ K线图API失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
        
        # 3. 测试技术指标图生成API
        print("3. 测试技术指标图生成API...")
        indicators_url = f"{base_url}/api/stocks/000001/chart?type=indicators&days=30"
        response = requests.get(indicators_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ 技术指标图生成成功: {chart_url}")
                
                # 检查图片文件是否存在
                import os
                file_path = chart_url.replace('/static/charts/', 'static/charts/')
                if os.path.exists(file_path):
                    print(f"✅ 技术指标图文件存在: {file_path}")
                else:
                    print(f"❌ 技术指标图文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ 技术指标图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 技术指标图API失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
        
        # 4. 测试静态文件访问
        print("4. 测试静态文件访问...")
        static_url = f"{base_url}{chart_url}"
        response = requests.get(static_url, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ 静态文件访问正常: {static_url}")
        else:
            print(f"❌ 静态文件访问失败: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_stock_analysis_with_charts()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 图表功能修复成功！所有测试通过！")
        print("现在可以在Web界面中:")
        print("1. 进行股票分析")
        print("2. 点击'生成图表'按钮")
        print("3. 查看K线图和技术指标图")
    else:
        print("💥 图表功能仍有问题，需要进一步调试")
    print("=" * 50)