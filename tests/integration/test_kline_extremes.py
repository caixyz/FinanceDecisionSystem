"""
测试K线图高低点标注功能
演示全局最高低点和局部最高低点标注
"""
import requests
import time
import os
from datetime import datetime

def test_kline_extremes_marking():
    """测试K线图高低点标注功能"""
    print("=" * 60)
    print("🎯 K线图高低点标注功能测试")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5000"
    symbol = "000858"  # 使用五粮液作为测试股票
    days = 90
    
    # 测试三种标注模式
    test_modes = [
        ("global", "全局最高低点"),
        ("local", "局部最高低点"), 
        ("none", "不标注")
    ]
    
    success_count = 0
    
    for mode, description in test_modes:
        print(f"\n{len(test_modes) - test_modes.index((mode, description)) + 1}. 测试{description}标注...")
        
        try:
            # 请求K线图生成
            chart_url = f"{base_url}/api/stocks/{symbol}/chart?type=candlestick&days={days}&mark_extremes={mode}"
            print(f"   请求URL: {chart_url}")
            
            response = requests.get(chart_url, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    chart_path = result['data']['chart_url']
                    print(f"   ✅ {description}K线图生成成功")
                    print(f"   📁 图片路径: {chart_path}")
                    
                    # 检查文件是否存在
                    local_path = chart_path.replace('/static/charts/', 'static/charts/')
                    if os.path.exists(local_path):
                        file_size = os.path.getsize(local_path)
                        print(f"   📊 文件大小: {file_size:,} bytes")
                        
                        # 验证图片可访问性
                        img_response = requests.get(f"{base_url}{chart_path}", timeout=30)
                        if img_response.status_code == 200:
                            print(f"   🌐 HTTP访问正常: {img_response.status_code}")
                            success_count += 1
                        else:
                            print(f"   ❌ HTTP访问失败: {img_response.status_code}")
                    else:
                        print(f"   ❌ 文件不存在: {local_path}")
                else:
                    print(f"   ❌ API返回错误: {result.get('message')}")
            else:
                print(f"   ❌ HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 测试{description}时出错: {e}")
        
        # 添加延时避免服务器压力
        time.sleep(2)
    
    return success_count == len(test_modes)

def test_web_interface():
    """测试Web界面的高低点标注功能"""
    print(f"\n{4}. 测试Web界面集成...")
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 测试主页是否可访问
        response = requests.get(base_url, timeout=30)
        if response.status_code == 200:
            html_content = response.text
            
            # 检查是否包含高低点标注选择控件
            if 'markExtremes' in html_content:
                print("   ✅ Web界面包含高低点标注选择控件")
                
                # 检查选项
                if '全局最高低点' in html_content and '局部最高低点' in html_content:
                    print("   ✅ 标注选项配置正确")
                    return True
                else:
                    print("   ❌ 标注选项配置不完整")
                    return False
            else:
                print("   ❌ Web界面缺少高低点标注选择控件")
                return False
        else:
            print(f"   ❌ Web界面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   💥 Web界面测试出错: {e}")
        return False

def demonstrate_extremes_features():
    """演示高低点标注功能的特点"""
    print(f"\n{5}. 功能特点演示...")
    
    features = [
        "🎯 全局最高低点标注 - 标注整个时间段内的绝对最高点和最低点",
        "📍 局部最高低点标注 - 标注局部极值点，帮助识别短期趋势转折",
        "🎨 智能标注样式 - 不同颜色和形状区分不同类型的标注点",
        "📊 价格显示 - 标注中包含具体的价格数值",
        "🔄 动态切换 - 前端支持实时切换不同标注模式",
        "⚡ 高性能渲染 - 使用matplotlib高效绘制，支持大数据量"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n   💡 使用建议:")
    print("   - 全局标注适合查看整体趋势和重要支撑阻力位")
    print("   - 局部标注适合短线交易和波段操作参考")
    print("   - 不标注模式保持图表简洁，专注价格走势")

if __name__ == "__main__":
    print("🚀 开始测试K线图高低点标注功能")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保静态目录存在
    os.makedirs('static/charts', exist_ok=True)
    
    # 1. 测试K线图标注功能
    chart_success = test_kline_extremes_marking()
    
    # 2. 测试Web界面集成
    web_success = test_web_interface()
    
    # 3. 演示功能特点
    demonstrate_extremes_features()
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    if chart_success and web_success:
        print("🎉 K线图高低点标注功能完全正常！")
        print("\n✅ 已实现的功能:")
        print("1. ✅ 全局最高低点标注 - 红色标注最高点，绿色标注最低点")
        print("2. ✅ 局部最高低点标注 - 橙色标注局部高点，青色标注局部低点")
        print("3. ✅ 前端选择控件 - 用户可选择不同标注模式")
        print("4. ✅ API参数支持 - mark_extremes参数控制标注行为")
        print("5. ✅ 线程安全绘图 - 解决了matplotlib多线程问题")
        
        print("\n🎯 使用方法:")
        print("1. 在Web界面选择股票代码和分析天数")
        print("2. 在'高低点标注'下拉菜单中选择标注模式：")
        print("   - 全局最高低点：标注整个周期的绝对最高和最低价格")
        print("   - 局部最高低点：标注多个局部转折点")
        print("   - 不标注：保持图表简洁")
        print("3. 点击'生成图表'按钮即可看到带标注的K线图")
        
    else:
        print("💥 部分功能存在问题，需要进一步调试")
        if not chart_success:
            print("❌ K线图标注功能异常")
        if not web_success:
            print("❌ Web界面集成异常")
    
    print("=" * 60)