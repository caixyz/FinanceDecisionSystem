#!/usr/bin/env python3
"""
测试API接口，验证股票数据是否正确返回
"""
import requests
import json
from urllib.parse import urljoin

# 服务器地址
BASE_URL = 'http://localhost:5000'

# 测试股票代码
test_symbols = ['000001', '000002', '000858', '601398']

def test_api_without_auth():
    """测试无需认证的API接口"""
    print("=== 测试无需认证的API接口 ===")
    
    # 测试股票列表
    url = urljoin(BASE_URL, '/api/stocks/list')
    try:
        response = requests.get(url, timeout=5)
        print(f"股票列表API状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"股票数量: {len(data.get('data', []))}")
        else:
            print(f"响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"错误: {e}")

def test_api_with_auth():
    """测试需要认证的API接口"""
    print("\n=== 测试需要认证的API接口 ===")
    
    # 先登录获取session
    login_url = urljoin(BASE_URL, '/api/auth/login')
    login_data = {
        'username': 'demo',
        'password': 'demo123'
    }
    
    session = requests.Session()
    
    try:
        # 登录
        response = session.post(login_url, json=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("登录成功")
            
            # 测试公司数据API
            for symbol in test_symbols:
                print(f"\n--- 测试股票 {symbol} ---")
                url = urljoin(BASE_URL, f'/api/company/{symbol}/data')
                
                response = session.get(url, params={'days': 30})
                print(f"状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        company = data.get('data', {}).get('company', {})
                        print(f"股票代码: {company.get('symbol')}")
                        print(f"名称: {company.get('name')}")
                        print(f"最新价: {company.get('close')}")
                        print(f"行业: {company.get('industry')}")
                        print(f"市盈率: {company.get('pe_ratio')}")
                        print(f"市净率: {company.get('pb_ratio')}")
                    except Exception as e:
                        print(f"解析JSON失败: {e}")
                        print(f"响应内容: {response.text[:200]}")
                else:
                    print(f"错误响应: {response.text[:200]}")
        else:
            print(f"登录失败: {response.text}")
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    test_api_without_auth()
    test_api_with_auth()