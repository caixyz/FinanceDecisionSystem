"""
测试Web接口的标注功能
"""
import requests
import time

def test_web_annotations():
    """测试Web接口"""
    base_url = "http://127.0.0.1:5000"
    symbol = "000858"
    days = 30
    
    print("🌐 测试Web接口标注功能")
    print("="*50)
    
    # 测试不同的mark_extremes参数
    test_cases = [
        ("global", "全局标注"),
        ("local", "局部标注"),
        ("none", "无标注"),
        ("", "默认参数")  # 空参数，应该使用默认值
    ]
    
    results = []
    
    for mark_extremes, description in test_cases:
        print(f"\n🧪 测试 {description}")
        
        try:
            # 构建URL
            if mark_extremes:
                url = f"{base_url}/api/stocks/{symbol}/chart?type=candlestick&days={days}&mark_extremes={mark_extremes}"
            else:
                url = f"{base_url}/api/stocks/{symbol}/chart?type=candlestick&days={days}"
            
            print(f"   请求URL: {url}")
            
            # 发起请求
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    chart_url = result['data']['chart_url']
                    print(f"   ✅ API调用成功: {chart_url}")
                    
                    # 检查文件
                    import os
                    local_path = chart_url.replace('/static/charts/', 'static/charts/')
                    if os.path.exists(local_path):
                        size = os.path.getsize(local_path)
                        print(f"   📊 文件大小: {size:,} bytes")
                        results.append((mark_extremes, description, size, chart_url))
                    else:
                        print(f"   ❌ 文件不存在: {local_path}")
                else:
                    print(f"   ❌ API错误: {result.get('message')}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 请求异常: {e}")
        
        time.sleep(1)  # 避免请求过快
    
    # 分析结果
    print(f"\n📊 结果分析:")
    print("="*50)
    
    if len(results) >= 2:
        # 比较文件大小
        global_size = None
        none_size = None
        
        for mark_extremes, description, size, chart_url in results:
            print(f"{description:12s}: {size:8,} bytes - {chart_url}")
            if mark_extremes == "global":
                global_size = size
            elif mark_extremes == "none":
                none_size = size
        
        if global_size and none_size:
            diff = global_size - none_size
            print(f"\n📈 大小差异分析:")
            print(f"   全局标注: {global_size:,} bytes")
            print(f"   无标注  : {none_size:,} bytes")
            print(f"   差异    : {diff:,} bytes")
            
            if diff > 1000:  # 如果差异超过1KB
                print(f"   ✅ 标注可能已生效 (文件更大)")
            elif abs(diff) < 500:  # 差异很小
                print(f"   ⚠️  文件大小相近，标注可能未生效")
            else:
                print(f"   🤔 需要进一步检查")
    
    print(f"\n🎯 建议:")
    print(f"1. 在浏览器中打开: http://127.0.0.1:5000")
    print(f"2. 输入股票代码: {symbol}")
    print(f"3. 选择'全局最高低点'标注模式")
    print(f"4. 生成图表并仔细查看红色和绿色标注")
    
    return results

if __name__ == "__main__":
    results = test_web_annotations()
    print(f"\n✅ 测试完成，共生成 {len(results)} 个图表")