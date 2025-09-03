#!/usr/bin/env python3
"""
测试登录功能
"""
import requests
import json

def test_login_system():
    base_url = "http://localhost:5000"
    
    print("🔍 测试金融决策系统登录功能\n")
    
    # 测试未登录时访问受保护的资源
    print("1. 测试未登录访问受保护资源...")
    try:
        response = requests.get(f"{base_url}/api/stocks/list")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ 正确拒绝未授权访问")
        else:
            print("   ❌ 未正确保护资源")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试登录
    print("\n2. 测试用户登录...")
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    session = requests.Session()
    
    try:
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        result = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {result['message']}")
        
        if response.status_code == 200:
            print("   ✅ 登录成功")
            user_info = result['data']['user']
            print(f"   用户信息: {user_info['username']} ({user_info['real_name']})")
        else:
            print("   ❌ 登录失败")
            return
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
        return
    
    # 测试登录后访问受保护资源
    print("\n3. 测试登录后访问受保护资源...")
    try:
        response = session.get(f"{base_url}/api/auth/user")
        result = response.json()
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 成功访问用户信息")
            print(f"   用户: {result['data']['username']}")
        else:
            print("   ❌ 访问失败")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试获取股票列表
    print("\n4. 测试获取股票列表...")
    try:
        response = session.get(f"{base_url}/api/stocks/list")
        result = response.json()
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 成功获取股票列表")
            stock_count = len(result['data'])
            print(f"   股票数量: {stock_count}")
        else:
            print(f"   ❌ 获取失败: {result['message']}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试用户统计信息
    print("\n5. 测试用户统计信息...")
    try:
        response = session.get(f"{base_url}/api/user/statistics")
        result = response.json()
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 成功获取统计信息")
            stats = result['data']
            print(f"   统计数据: {stats}")
        else:
            print(f"   ❌ 获取失败: {result['message']}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试用户活动记录
    print("\n6. 测试用户活动记录...")
    try:
        response = session.get(f"{base_url}/api/user/activities")
        result = response.json()
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 成功获取活动记录")
            activities = result['data']
            print(f"   活动数量: {len(activities)}")
        else:
            print(f"   ❌ 获取失败: {result['message']}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试退出登录
    print("\n7. 测试退出登录...")
    try:
        response = session.post(f"{base_url}/api/auth/logout")
        result = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {result['message']}")
        
        if response.status_code == 200:
            print("   ✅ 退出登录成功")
        else:
            print("   ❌ 退出登录失败")
    except Exception as e:
        print(f"   ❌ 退出请求失败: {e}")
    
    # 测试退出登录后再次访问受保护资源
    print("\n8. 测试退出登录后访问受保护资源...")
    try:
        response = session.get(f"{base_url}/api/auth/user")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ 正确拒绝访问")
        else:
            print("   ❌ 未正确处理注销状态")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    print("\n🎉 登录系统测试完成！")

if __name__ == "__main__":
    test_login_system()