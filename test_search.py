import requests
import json

def test_search_stocks():
    """测试股票搜索功能"""
    base_url = "http://localhost:5000"
    
    # 先登录获取session
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        # 登录
        print("正在登录...")
        response = session.post(f"{base_url}/api/auth/login", json=login_data, timeout=10)
        result = response.json()
        print(f"登录结果: {result}")
        
        if result['code'] != 200:
            print("登录失败")
            return
        
        # 搜索股票
        print("开始搜索股票...")
        response = session.get(f"{base_url}/api/stocks/list?keyword=平安", timeout=10)
        print(f"搜索请求状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"搜索结果: {result}")
            
            # 显示前几只股票的信息
            if result['code'] == 200 and result['data']['stocks']:
                print("\n前3只股票的详细信息:")
                for i, stock in enumerate(result['data']['stocks'][:3]):
                    print(f"{i+1}. {stock}")
            else:
                print("未找到股票或返回错误")
        else:
            print(f"请求失败，状态码: {response.status_code}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_search_stocks()