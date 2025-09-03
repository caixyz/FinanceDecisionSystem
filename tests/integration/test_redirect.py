#!/usr/bin/env python3
"""
测试登录跳转修复
"""
import requests
import json

def test_login_redirect():
    base_url = "http://localhost:5000"
    
    print("测试登录跳转修复\n")
    
    # 测试1: 访问根路径是否重定向到登录页
    print("1. 测试根路径重定向...")
    try:
        # 不跟随重定向，检查是否返回302
        response = requests.get(f"{base_url}/", allow_redirects=False)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 302:
            location = response.headers.get('Location', '')
            print(f"   重定向到: {location}")
            if '/login' in location:
                print("   ✅ 正确重定向到登录页面")
            else:
                print("   ❌ 重定向目标错误")
        else:
            print("   ❌ 未产生重定向")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试2: 跟随重定向，确认最终页面是登录页
    print("\n2. 测试重定向后的页面内容...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=True)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if '登录 - 金融决策系统' in content and 'loginForm' in content:
                print("   ✅ 成功显示登录页面")
            else:
                print("   ❌ 页面内容不正确")
        else:
            print("   ❌ 最终页面状态异常")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试3: 直接访问登录页
    print("\n3. 测试直接访问登录页...")
    try:
        response = requests.get(f"{base_url}/login")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if '登录 - 金融决策系统' in content:
                print("   ✅ 登录页面正常")
            else:
                print("   ❌ 登录页面内容异常")
        else:
            print("   ❌ 登录页面无法访问")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试4: 测试登录后的跳转
    print("\n4. 测试登录后的跳转...")
    session = requests.Session()
    
    try:
        # 登录
        login_data = {"username": "demo", "password": "demo123"}
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        result = response.json()
        
        print(f"   登录状态: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 登录成功")
            
            # 登录后访问根路径
            response = session.get(f"{base_url}/", allow_redirects=False)
            print(f"   登录后访问根路径状态: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ 登录后可以访问分析界面")
            else:
                print("   ❌ 登录后访问异常")
                
        else:
            print(f"   ❌ 登录失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"   ❌ 登录测试失败: {e}")
    
    print("\n登录跳转测试完成！")

if __name__ == "__main__":
    test_login_redirect()