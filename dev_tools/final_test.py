"""
最终测试K线图标注功能
"""
import requests
import time

def test_web_chart_with_annotations():
    """测试Web接口的标注功能"""
    base_url = "http://127.0.0.1:5000"
    symbol = "000858"
    days = 30
    
    print("🎯 测试K线图高低点标注功能")
    print("="*50)
    
    # 测试三种模式
    modes = [
        ("global", "全局最高低点"),
        ("local", "局部最高低点"),
        ("none", "不标注")
    ]
    
    for mode, desc in modes:
        print(f"\n测试{desc}模式...")
        
        try:
            url = f"{base_url}/api/stocks/{symbol}/chart?type=candlestick&days={days}&mark_extremes={mode}"
            print(f"请求: {url}")
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    chart_url = result['data']['chart_url']
                    print(f"✅ 成功生成图表: {chart_url}")
                    
                    # 验证文件访问
                    img_url = f"{base_url}{chart_url}"
                    img_response = requests.get(img_url, timeout=10)
                    
                    if img_response.status_code == 200:
                        print(f"✅ 图片可正常访问，大小: {len(img_response.content):,} bytes")
                    else:
                        print(f"❌ 图片访问失败: {img_response.status_code}")
                else:
                    print(f"❌ API错误: {result.get('message')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"💥 请求异常: {e}")
        
        time.sleep(1)  # 避免请求过快
    
    print("\n" + "="*50)
    print("🎉 测试完成！")
    print("\n💡 使用提示:")
    print("1. 打开Web界面: http://127.0.0.1:5000")
    print("2. 输入股票代码: 000858")
    print("3. 选择'高低点标注'模式")
    print("4. 点击'分析股票'后再点击'生成图表'")
    print("5. 查看K线图上的高低点标注")

if __name__ == "__main__":
    test_web_chart_with_annotations()