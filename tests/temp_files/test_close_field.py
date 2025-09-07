#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证股票列表API是否正确返回包含收盘价的数据
"""

import requests
import json

def test_public_api():
    """测试公开API"""
    print("=== 测试公开股票查看API ===")
    try:
        response = requests.get('http://localhost:5001/api/public/stocks')
        data = response.json()
        
        if data.get('success'):
            stocks = data.get('stocks', [])
            print(f"API返回的股票数量: {len(stocks)}")
            
            if stocks:
                print("\n前3条股票数据:")
                for i, stock in enumerate(stocks[:3]):
                    print(f"  {i+1}. {stock['symbol']} - {stock['name']}")
                    print(f"     行业: {stock['industry']}")
                    print(f"     收盘价: {stock['close']}")
                    print(f"     更新时间: {stock['updated_at']}")
                    print()
                    
                # 检查是否所有股票都有收盘价字段
                missing_close = [s for s in stocks if 'close' not in s]
                if missing_close:
                    print(f"警告: {len(missing_close)} 条记录缺少收盘价字段")
                else:
                    print("✅ 所有股票记录都包含收盘价字段")
                    
        else:
            print(f"API返回错误: {data.get('message')}")
            
    except Exception as e:
        print(f"测试公开API失败: {e}")

def test_main_api():
    """测试主应用API"""
    print("\n=== 测试主应用股票列表API ===")
    try:
        # 注意：主应用需要登录，这里我们检查API结构
        response = requests.get('http://localhost:5000/api/stocks/list')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"响应码: {data.get('code')}")
                print(f"消息: {data.get('message')}")
                if 'data' in data:
                    stocks = data['data']
                    print(f"股票数量: {len(stocks)}")
                    if stocks:
                        print("前2条数据示例:")
                        print(json.dumps(stocks[:2], ensure_ascii=False, indent=2))
        else:
            print(f"需要登录，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"测试主应用API失败: {e}")

if __name__ == "__main__":
    test_public_api()
    test_main_api()