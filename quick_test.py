"""
快速测试K线图高低点标注功能
"""
import requests

def quick_test():
    """快速测试三种标注模式"""
    base_url = "http://127.0.0.1:5000"
    symbol = "000858"
    days = 60
    
    modes = ["global", "local", "none"]
    
    for mode in modes:
        try:
            url = f"{base_url}/api/stocks/{symbol}/chart?type=candlestick&days={days}&mark_extremes={mode}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"✅ {mode} 模式测试成功: {result['data']['chart_url']}")
                else:
                    print(f"❌ {mode} 模式API错误: {result.get('message')}")
            else:
                print(f"❌ {mode} 模式HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"💥 {mode} 模式异常: {e}")

if __name__ == "__main__":
    print("🎯 K线图高低点标注快速测试")
    quick_test()
    print("✅ 测试完成")