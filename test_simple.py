#!/usr/bin/env python3
"""
简化的API测试脚本
"""
import requests
import json

# 基础配置
BASE_URL = "http://localhost:5000"

def test_simple_api():
    """测试简化的API接口"""
    print("=== 测试金融决策系统API接口 ===\n")
    
    # 测试股票列表
    try:
        print("1. 测试股票列表API...")
        response = requests.get(f"{BASE_URL}/api/stocks/list")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                if 'data' in data:
                    print(f"   获取到 {len(data['data'])} 只股票")
                    # 显示前3只股票
                    for stock in data['data'][:3]:
                        print(f"   - {stock.get('symbol', 'N/A')}: {stock.get('name', 'N/A')}")
                else:
                    print("   数据格式异常")
            except:
                print("   响应不是JSON格式")
        print()
    except Exception as e:
        print(f"   错误: {e}\n")
    
    # 测试用户登录
    try:
        print("2. 测试用户登录...")
        login_data = {
            "username": "demo",
            "password": "demo123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            login_result = response.json()
            print("   登录成功")
            session_token = response.cookies.get('session')
        else:
            print("   登录失败")
            return
        print()
    except Exception as e:
        print(f"   错误: {e}\n")
        return
    
    # 测试单只股票数据
    test_stocks = ['000002', '000858', '601398']
    
    for symbol in test_stocks:
        try:
            print(f"3. 测试股票 {symbol} 数据...")
            response = requests.get(f"{BASE_URL}/api/company/{symbol}/data?days=30")
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    company = data['data']['company']
                    prices = data['data']['prices']
                    print(f"   股票名称: {company.get('name', 'N/A')}")
                    print(f"   行业: {company.get('industry', 'N/A')}")
                    print(f"   最新价: {company.get('close', 0)}")
                    print(f"   历史数据: {len(prices)} 条")
                    if prices:
                        print(f"   最近日期: {prices[-1].get('date', 'N/A')}")
                        print(f"   最近价格: {prices[-1].get('close', 0)}")
                else:
                    print(f"   错误: {data.get('message', '未知错误')}")
            else:
                print(f"   错误: HTTP {response.status_code}")
            print()
        except Exception as e:
            print(f"   错误: {e}\n")

if __name__ == "__main__":
    test_simple_api()
    print("=== 测试完成 ===")