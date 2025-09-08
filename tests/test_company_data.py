#!/usr/bin/env python3
"""
测试公司分析页面数据获取
"""
import requests
import json

# 服务器地址
BASE_URL = "http://localhost:5000"

# 测试用户凭据
USERNAME = "admin"
PASSWORD = "admin123"

def test_company_data():
    """测试公司数据获取"""
    session = requests.Session()
    
    # 1. 登录
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    print("1. 正在登录...")
    login_response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"✅ 登录成功: {login_result.get('message')}")
    else:
        print(f"❌ 登录失败: {login_response.status_code}")
        return False
    
    # 2. 获取公司数据
    print("\n2. 获取公司数据...")
    company_response = session.get(f"{BASE_URL}/api/company/000001/data")
    
    if company_response.status_code == 200:
        try:
            data = company_response.json()
            print(f"✅ 数据获取成功")
            print(f"- 股票代码: {data.get('data', {}).get('company', {}).get('symbol', 'N/A')}")
            print(f"- 公司名称: {data.get('data', {}).get('company', {}).get('name', 'N/A')}")
            print(f"- 价格数据条数: {len(data.get('data', {}).get('prices', []))}")
            print(f"- 指标数据条数: {len(data.get('data', {}).get('indicators', []))}")
            
            # 打印完整数据结构
            print("\n📊 数据结构:")
            if 'data' in data and 'company' in data['data']:
                company = data['data']['company']
                for key, value in company.items():
                    print(f"  {key}: {value}")
            
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            print(f"响应内容: {company_response.text[:200]}...")
            return False
    else:
        print(f"❌ 获取数据失败: {company_response.status_code}")
        print(f"响应内容: {company_response.text[:200]}...")
        return False

if __name__ == "__main__":
    print("🔍 测试公司分析页面数据获取")
    print("=" * 50)
    test_company_data()