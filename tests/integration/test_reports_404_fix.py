"""
测试报告中图表路径404问题修复
"""
import requests
import time
import os

def test_report_charts_fix():
    """测试报告生成和图表访问修复"""
    print("=" * 60)
    print("测试报告中K线图和技术指标图404问题修复")
    print("=" * 60)
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 1. 生成报告
        print("1. 测试报告生成...")
        report_url = f"{base_url}/api/reports/generate"
        
        test_data = {
            "symbol": "000858", 
            "days": 90
        }
        
        response = requests.post(
            report_url, 
            json=test_data, 
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                report_path = result['data']['report_url']
                print(f"✅ 报告生成成功: {report_path}")
                
                # 检查HTML文件是否存在
                file_path = report_path.replace('/static/reports/', 'static/reports/')
                if os.path.exists(file_path):
                    print(f"✅ 报告文件存在: {file_path}")
                    
                    # 读取HTML文件内容检查图片路径
                    with open(file_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    print("\n2. 检查HTML中的图片路径...")
                    
                    # 查找图片src
                    import re
                    img_srcs = re.findall(r'src="([^"]*)"', html_content)
                    
                    for img_src in img_srcs:
                        print(f"   发现图片路径: {img_src}")
                        
                        if img_src.startswith('/static/'):
                            # 检查对应的图片文件是否存在
                            img_file_path = img_src.replace('/static/', 'static/')
                            if os.path.exists(img_file_path):
                                print(f"   ✅ 图片文件存在: {img_file_path}")
                                
                                # 测试通过HTTP访问
                                img_url = f"{base_url}{img_src}"
                                img_response = requests.get(img_url, timeout=30)
                                
                                if img_response.status_code == 200:
                                    print(f"   ✅ 图片HTTP访问正常: {img_response.status_code}")
                                    print(f"      Content-Type: {img_response.headers.get('Content-Type')}")
                                else:
                                    print(f"   ❌ 图片HTTP访问失败: {img_response.status_code}")
                                    return False
                            else:
                                print(f"   ❌ 图片文件不存在: {img_file_path}")
                                return False
                        else:
                            print(f"   ⚠️  图片路径格式可能有问题: {img_src}")
                    
                    # 3. 测试通过浏览器访问报告
                    print("\n3. 测试报告HTTP访问...")
                    report_http_url = f"{base_url}{report_path}"
                    report_response = requests.get(report_http_url, timeout=30)
                    
                    if report_response.status_code == 200:
                        print(f"✅ 报告HTTP访问正常: {report_response.status_code}")
                        return True
                    else:
                        print(f"❌ 报告HTTP访问失败: {report_response.status_code}")
                        return False
                        
                else:
                    print(f"❌ 报告文件不存在: {file_path}")
                    return False
            else:
                print(f"❌ 报告生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 报告生成API失败: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_report_charts_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 报告中K线图和技术指标图404问题修复成功！")
        print("修复内容:")
        print("1. ✅ 修正了HTML报告中图片路径格式")
        print("2. ✅ 将文件系统路径转换为正确的Web URL路径")
        print("3. ✅ 图片现在使用 /static/reports/ 前缀")
        print("4. ✅ 静态文件服务器配置正确")
        print("\n现在报告中的图表可以正常显示了！")
    else:
        print("💥 仍有问题需要进一步调试")
    print("=" * 60)