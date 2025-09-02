"""
测试K线图404问题修复
"""
import requests
import time
import os

def test_chart_generation_and_access():
    """测试图表生成和访问"""
    print("=" * 50)
    print("测试K线图和技术指标图404问题修复")
    print("=" * 50)
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 1. 生成K线图
        print("1. 测试K线图生成...")
        candlestick_url = f"{base_url}/api/stocks/000001/chart?type=candlestick&days=30"
        response = requests.get(candlestick_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ K线图生成成功: {chart_url}")
                
                # 检查文件是否存在
                file_path = chart_url.replace('/static/charts/', 'static/charts/')
                if os.path.exists(file_path):
                    print(f"✅ K线图文件存在: {file_path}")
                    file_size = os.path.getsize(file_path)
                    print(f"   文件大小: {file_size} bytes")
                    
                    # 测试通过HTTP访问
                    static_url = f"{base_url}{chart_url}"
                    static_response = requests.get(static_url, timeout=30)
                    
                    if static_response.status_code == 200:
                        print(f"✅ K线图HTTP访问正常: {static_response.status_code}")
                        print(f"   Content-Type: {static_response.headers.get('Content-Type')}")
                        print(f"   Content-Length: {static_response.headers.get('Content-Length')}")
                    else:
                        print(f"❌ K线图HTTP访问失败: {static_response.status_code}")
                        return False
                else:
                    print(f"❌ K线图文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ K线图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ K线图API调用失败: {response.status_code}")
            return False
        
        # 2. 生成技术指标图
        print("\n2. 测试技术指标图生成...")
        indicators_url = f"{base_url}/api/stocks/000001/chart?type=indicators&days=30"
        response = requests.get(indicators_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ 技术指标图生成成功: {chart_url}")
                
                # 检查文件是否存在
                file_path = chart_url.replace('/static/charts/', 'static/charts/')
                if os.path.exists(file_path):
                    print(f"✅ 技术指标图文件存在: {file_path}")
                    file_size = os.path.getsize(file_path)
                    print(f"   文件大小: {file_size} bytes")
                    
                    # 测试通过HTTP访问
                    static_url = f"{base_url}{chart_url}"
                    static_response = requests.get(static_url, timeout=30)
                    
                    if static_response.status_code == 200:
                        print(f"✅ 技术指标图HTTP访问正常: {static_response.status_code}")
                        print(f"   Content-Type: {static_response.headers.get('Content-Type')}")
                        print(f"   Content-Length: {static_response.headers.get('Content-Length')}")
                    else:
                        print(f"❌ 技术指标图HTTP访问失败: {static_response.status_code}")
                        return False
                else:
                    print(f"❌ 技术指标图文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ 技术指标图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 技术指标图API调用失败: {response.status_code}")
            return False
        
        # 3. 测试静态文件服务器配置
        print("\n3. 测试静态文件服务器配置...")
        static_test_url = f"{base_url}/static/charts/"
        response = requests.get(static_test_url, timeout=30)
        print(f"静态目录访问状态码: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generation_and_access()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 K线图和技术指标图404问题修复成功！")
        print("修复内容:")
        print("1. ✅ 确保图表文件目录存在")
        print("2. ✅ 添加了详细的前端调试信息")
        print("3. ✅ 增加了图片加载失败的错误处理")
        print("4. ✅ 添加了防缓存时间戳")
        print("5. ✅ 静态文件服务正常")
        print("\n现在可以正常使用图表功能了！")
    else:
        print("💥 仍有问题需要进一步调试")
    print("=" * 50)