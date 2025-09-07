#!/usr/bin/env python3
import requests
import json

# 测试股票列表API
try:
    response = requests.get('http://localhost:5000/api/stocks/list')
    data = response.json()
    
    if data.get('success'):
        stocks = data.get('data', [])
        print(f'API返回的股票总数: {len(stocks)}')
        
        # 查找工商银行
        icbc = None
        for stock in stocks:
            if stock['symbol'] == '601398':
                icbc = stock
                break
        
        if icbc:
            print(f'\n工商银行信息:')
            print(f'  代码: {icbc["symbol"]}')
            print(f'  名称: {icbc["name"]}')
            print(f'  行业: {icbc["industry"]}')
        else:
            print('\n未找到工商银行信息')
            
        # 显示前5条股票信息
        print('\n前5条股票信息:')
        for i, stock in enumerate(stocks[:5]):
            print(f'  {i+1}. {stock["symbol"]} - {stock["name"]} - {stock["industry"]}')
            
    else:
        print('API返回错误:', data.get('message'))
        
except Exception as e:
    print('测试API失败:', e)