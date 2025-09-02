"""
测试报告生成功能
"""
import requests
import json
import time

def test_report_generation():
    """测试报告生成API"""
    print("=" * 50)
    print("测试报告生成功能")
    print("=" * 50)
    
    try:
        url = "http://127.0.0.1:5000/api/reports/generate"
        
        # 测试数据
        test_data = {
            "symbol": "000001",
            "days": 90
        }
        
        print(f"正在测试报告生成API...")
        print(f"请求URL: {url}")
        print(f"请求数据: {test_data}")
        
        # 发送请求
        print("发送POST请求...")
        response = requests.post(
            url, 
            json=test_data, 
            headers={'Content-Type': 'application/json'},
            timeout=120  # 延长超时时间到120秒
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON解析成功")
                print(f"返回代码: {result.get('code')}")
                print(f"返回消息: {result.get('message')}")
                
                if result.get('code') == 200:
                    data = result.get('data', {})
                    report_url = data.get('report_url')
                    print(f"✅ 报告生成成功!")
                    print(f"报告URL: {report_url}")
                    
                    # 检查文件是否存在
                    import os
                    file_path = report_url.replace('/static/reports/', 'static/reports/')
                    if os.path.exists(file_path):
                        print(f"✅ 报告文件存在: {file_path}")
                        
                        # 检查文件大小
                        file_size = os.path.getsize(file_path)
                        print(f"报告文件大小: {file_size} bytes")
                        
                        return True
                    else:
                        print(f"❌ 报告文件不存在: {file_path}")
                        return False
                else:
                    print(f"❌ API返回错误: {result.get('message')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:1000]}...")
                return False
        else:
            print(f"❌ HTTP请求失败")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout as e:
        print(f"❌ 请求超时: {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_step_by_step():
    """分步测试报告生成过程"""
    print("\n" + "=" * 50)
    print("分步测试报告生成过程")
    print("=" * 50)
    
    try:
        # 1. 测试数据获取
        print("1. 测试数据获取...")
        response = requests.get("http://127.0.0.1:5000/api/stocks/000001/analysis?days=90", timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ 股票数据获取成功")
            else:
                print(f"❌ 股票数据获取失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 股票数据API失败: {response.status_code}")
            return False
        
        # 2. 测试图表生成
        print("2. 测试图表生成...")
        response = requests.get("http://127.0.0.1:5000/api/stocks/000001/chart?type=candlestick&days=90", timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ 图表生成成功")
            else:
                print(f"❌ 图表生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 图表生成API失败: {response.status_code}")
            return False
        
        # 3. 检查报告目录
        print("3. 检查报告目录...")
        import os
        if not os.path.exists("static/reports"):
            os.makedirs("static/reports", exist_ok=True)
            print("✅ 报告目录创建成功")
        else:
            print("✅ 报告目录存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 分步测试失败: {e}")
        return False

if __name__ == "__main__":
    # 先检查前置条件
    step_success = test_report_step_by_step()
    
    if step_success:
        # 再测试报告生成
        success = test_report_generation()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 报告生成功能正常！")
        else:
            print("💥 报告生成功能异常")
    else:
        print("\n💥 前置条件检查失败，无法测试报告生成")
    
    print("=" * 50)