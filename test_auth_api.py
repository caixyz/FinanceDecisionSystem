#!/usr/bin/env python3
"""
带认证的API测试脚本
"""
import requests
import json
import sys

# 配置
BASE_URL = "http://localhost:5000"
USERNAME = "demo"
PASSWORD = "demo123"

def test_login():
    """测试用户登录"""
    print("=== 测试用户登录 ===")
    
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 登录成功")
                session = requests.Session()
                session.cookies.update(response.cookies)
                return session
            else:
                print(f"❌ 登录失败: {data.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return None

def test_stock_list(session):
    """测试股票列表API"""
    print("\n=== 测试股票列表API ===")
    
    try:
        response = session.get(f"{BASE_URL}/api/stocks/list")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stocks = data.get('data', [])
            if data.get('code') == 200 or data.get('message') == '获取股票列表成功':
                print(f"✅ 股票列表获取成功，数量: {len(stocks)}")
                if stocks:
                    print("前3只股票:")
                    for stock in stocks[:3]:
                        print(f"  {stock.get('symbol')} - {stock.get('name')} - {stock.get('industry', 'N/A')}")
                return True
            else:
                print(f"❌ API错误: {data.get('message')} (code: {data.get('code')})")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return False

def test_company_data(session, symbol="000002"):
    """测试公司数据API"""
    print(f"\n=== 测试公司数据API ({symbol}) ===")
    
    try:
        response = session.get(f"{BASE_URL}/api/company/{symbol}/data?days=30")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                company = data['data']['company']
                prices = data['data']['prices']
                indicators = data['data']['indicators']
                
                print(f"✅ 公司数据获取成功")
                print(f"  股票代码: {company.get('symbol')}")
                print(f"  名称: {company.get('name')}")
                print(f"  行业: {company.get('industry', 'N/A')}")
                print(f"  最新价: {company.get('close', 0)}")
                print(f"  历史数据: {len(prices)} 条")
                print(f"  技术指标: {len(indicators)} 条")
                return True
            else:
                print(f"❌ API错误: {data.get('message')} (code: {data.get('code')})")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return False

def main():
    """主测试函数"""
    print("开始测试带认证的API...")
    
    # 1. 测试登录
    session = test_login()
    if not session:
        print("❌ 登录失败，无法继续测试")
        return False
    
    # 2. 测试股票列表
    if not test_stock_list(session):
        print("❌ 股票列表测试失败")
        return False
    
    # 3. 测试公司数据API
    symbols = ["000002", "000858", "601398"]
    for symbol in symbols:
        if not test_company_data(session, symbol):
            print(f"❌ {symbol} 公司数据测试失败")
            return False
    
    print("\n🎉 所有测试通过！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)