import requests
import json

def test_api_format():
    """测试API返回格式"""
    
    # 测试股票列表API
    try:
        response = requests.get('http://localhost:5000/api/stocks/list')
        if response.status_code == 200:
            data = response.json()
            print("API返回格式:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print(f"\n数据类型: {type(data)}")
            print(f"数据键: {list(data.keys())}")
            if 'data' in data:
                print(f"数据内容类型: {type(data['data'])}")
                if isinstance(data['data'], list):
                    print(f"数据条数: {len(data['data'])}")
                    if data['data']:
                        print(f"第一条数据: {data['data'][0]}")
                elif isinstance(data['data'], dict):
                    print(f"数据键: {list(data['data'].keys())}")
                    if 'stocks' in data['data']:
                        print(f"股票列表类型: {type(data['data']['stocks'])}")
                        print(f"股票列表长度: {len(data['data']['stocks'])}")
        else:
            print(f"❌ 股票列表API错误: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票列表API异常: {e}")

if __name__ == "__main__":
    test_api_format()