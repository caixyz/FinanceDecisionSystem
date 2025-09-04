#!/usr/bin/env python3
"""
浏览器测试脚本 - 验证NaN值修复效果
"""

import requests
import json
import time

def test_with_login():
    """使用登录测试API"""
    
    # 创建会话
    session = requests.Session()
    
    # 登录
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    try:
        # 登录
        login_response = session.post('http://localhost:5000/api/auth/login', json=login_data)
        print(f"登录状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ 登录成功")
            
            # 测试股票列表API
            list_response = session.get('http://localhost:5000/api/stocks/list')
            print(f"股票列表API状态: {list_response.status_code}")
            
            if list_response.status_code == 200:
                data = list_response.json()
                print(f"✅ 股票列表API正常，返回 {len(data.get('data', []))} 条记录")
                
                # 检查是否有NaN值
                stocks = data.get('data', [])
                has_nan = False
                for stock in stocks[:5]:  # 检查前5条
                    for key, value in stock.items():
                        if str(value).lower() == 'nan' or value is None:
                            print(f"⚠️  发现NaN/None值: {key}={value}")
                            has_nan = True
                
                if not has_nan:
                    print("✅ 无NaN值发现")
            
            # 测试股票数据API
            data_response = session.get('http://localhost:5000/api/stocks/000001/data?days=30')
            print(f"股票数据API状态: {data_response.status_code}")
            
            if data_response.status_code == 200:
                data = data_response.json()
                stock_data = data.get('data', [])
                print(f"✅ 股票数据API正常，返回 {len(stock_data)} 条记录")
                
                # 检查数据中的NaN值
                has_nan = False
                for record in stock_data[:3]:  # 检查前3条
                    for key, value in record.items():
                        if str(value).lower() == 'nan' or value is None:
                            print(f"⚠️  发现NaN/None值: {key}={value}")
                            has_nan = True
                
                if not has_nan:
                    print("✅ 股票数据无NaN值")
            
        else:
            print(f"❌ 登录失败: {login_response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    print("开始测试NaN值修复效果...")
    print("=" * 50)
    
    # 等待应用完全启动
    time.sleep(3)
    
    test_with_login()
    
    print("=" * 50)
    print("测试完成")