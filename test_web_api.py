"""
测试Web API是否正常工作
"""
import requests
import json

def test_api():
    """测试股票分析API"""
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 50)
    print("测试金融决策系统Web API")
    print("=" * 50)
    
    try:
        # 测试股票分析接口
        print("正在测试股票分析接口...")
        url = f"{base_url}/api/stocks/000001/analysis?days=30"
        
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API调用成功!")
            print(f"返回状态码: {data.get('code')}")
            print(f"返回消息: {data.get('message')}")
            
            if data.get('code') == 200:
                analysis_data = data.get('data', {})
                print(f"\n分析结果:")
                print(f"股票代码: {analysis_data.get('symbol')}")
                print(f"当前价格: {analysis_data.get('current_price')}")
                print(f"趋势判断: {analysis_data.get('trend')}")
                print(f"交易信号: {analysis_data.get('trading_signal', {}).get('signal')}")
                print(f"风险等级: {analysis_data.get('risk_assessment', {}).get('risk_level')}")
                
                print("✅ 股票分析功能正常工作!")
                return True
            else:
                print(f"❌ API返回错误: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Web API测试通过！系统正常运行！")
        print("您现在可以通过Web界面使用金融决策系统了")
    else:
        print("💥 Web API测试失败")
    print("=" * 50)