import requests
import json

def test_api_endpoints():
    """测试API端点是否修复了NaN值问题"""
    
    # 测试股票列表API
    try:
        response = requests.get('http://localhost:5000/api/stocks/list')
        if response.status_code == 200:
            data = response.json()
            print("✅ 股票列表API正常")
            print(f"   返回股票数量: {len(data.get('data', []))}")
        else:
            print(f"❌ 股票列表API错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票列表API异常: {e}")
    
    # 测试股票数据API
    try:
        response = requests.get('http://localhost:5000/api/stocks/000001/data?days=30')
        if response.status_code == 200:
            data = response.json()
            print("✅ 股票数据API正常")
            print(f"   返回数据条数: {len(data.get('data', []))}")
            
            # 检查是否有NaN值
            stock_data = data.get('data', [])
            has_nan = False
            for record in stock_data:
                for key, value in record.items():
                    if str(value) == 'nan' or str(value) == 'NaN':
                        has_nan = True
                        break
            if has_nan:
                print("⚠️  发现NaN值")
            else:
                print("✅ 无NaN值")
        else:
            print(f"❌ 股票数据API错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票数据API异常: {e}")

if __name__ == "__main__":
    test_api_endpoints()