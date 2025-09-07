import requests
import json

def test_sync_stock_list():
    """测试同步股票列表"""
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
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        result = response.json()
        print(f"登录结果: {result}")
        
        if result['code'] != 200:
            print("登录失败")
            return
        
        # 同步股票列表
        print("开始同步股票列表...")
        response = session.post(f"{base_url}/api/stocks/sync/list")
        print(f"同步请求状态码: {response.status_code}")
        result = response.json()
        print(f"同步结果: {result}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_sync_stock_list()