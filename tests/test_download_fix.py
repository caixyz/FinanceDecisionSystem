#!/usr/bin/env python3
"""测试下载功能修复"""

import requests
import json

def test_download_interface():
    """测试接口下载功能"""
    
    # 测试服务器是否运行
    try:
        response = requests.get('http://localhost:5000/api/akshare/interfaces')
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print(f"❌ 服务器返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接服务器: {e}")
        return False
    
    # 测试下载正常接口
    test_cases = [
        {
            "interface": "stock_zh_a_spot",
            "description": "A股实时行情"
        },
        {
            "interface": "stock_a_indicator_lg", 
            "description": "A股技术指标（已知问题接口）"
        }
    ]
    
    for case in test_cases:
        print(f"\n🧪 测试 {case['description']} ({case['interface']})...")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/akshare/interfaces/download',
                json={'interface_name': case['interface']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"✅ {case['interface']} 下载成功")
                    print(f"   插入记录: {result['data']['records_inserted']}")
                    print(f"   总记录数: {result['data']['total_records']}")
                else:
                    print(f"⚠️  {case['interface']} 下载完成但有警告: {result.get('message')}")
            else:
                result = response.json()
                print(f"⚠️  {case['interface']} 返回错误: {result.get('message', '未知错误')}")
                
        except Exception as e:
            print(f"❌ {case['interface']} 测试失败: {e}")
    
    return True

if __name__ == "__main__":
    print("开始测试下载功能修复...")
    test_download_interface()
    print("\n测试完成！")