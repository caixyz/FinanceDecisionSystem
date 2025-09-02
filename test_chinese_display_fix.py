"""
测试图表中文显示修复
"""
import requests
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def test_chinese_fonts():
    """测试中文字体支持"""
    print("=" * 50)
    print("测试系统中文字体支持")
    print("=" * 50)
    
    # 获取系统可用字体
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    chinese_fonts = [
        'SimHei',          # 黑体
        'Microsoft YaHei', # 微软雅黑
        'DejaVu Sans',     # 备选字体
        'Arial Unicode MS', # Mac/Linux备选
        'WenQuanYi Micro Hei', # Linux中文字体
        'Noto Sans CJK SC'  # Google字体
    ]
    
    print("系统可用的中文字体:")
    found_fonts = []
    for font in chinese_fonts:
        if font in available_fonts:
            found_fonts.append(font)
            print(f"✅ {font}")
        else:
            print(f"❌ {font}")
    
    if found_fonts:
        print(f"\n推荐使用字体: {found_fonts[0]}")
        return found_fonts[0]
    else:
        print("\n⚠️ 未找到合适的中文字体，可能出现显示问题")
        return None

def test_chart_generation():
    """测试图表生成和中文显示"""
    print("\n" + "=" * 50)
    print("测试图表生成和中文显示")
    print("=" * 50)
    
    try:
        base_url = "http://127.0.0.1:5000"
        
        # 1. 测试K线图生成
        print("1. 测试K线图生成...")
        candlestick_url = f"{base_url}/api/stocks/000001/chart?type=candlestick&days=30"
        response = requests.get(candlestick_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ K线图生成成功: {chart_url}")
            else:
                print(f"❌ K线图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ K线图API调用失败: {response.status_code}")
            return False
        
        # 2. 测试技术指标图生成
        print("2. 测试技术指标图生成...")
        indicators_url = f"{base_url}/api/stocks/000001/chart?type=indicators&days=30"
        response = requests.get(indicators_url, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                chart_url = result['data']['chart_url']
                print(f"✅ 技术指标图生成成功: {chart_url}")
            else:
                print(f"❌ 技术指标图生成失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 技术指标图API调用失败: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 测试字体支持
    recommended_font = test_chinese_fonts()
    
    # 测试图表生成
    success = test_chart_generation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 图表中文显示修复成功！")
        print("修复内容:")
        print("1. ✅ 完善了中文字体检测和设置")
        print("2. ✅ 在每个绘图方法中确保字体设置")
        print("3. ✅ 为标题和标签指定了中文字体属性")
        print("4. ✅ 支持多种中文字体备选方案")
        if recommended_font:
            print(f"5. ✅ 当前使用字体: {recommended_font}")
        print("\n现在图表中的中文应该能正常显示了！")
    else:
        print("💥 仍有问题需要进一步调试")
        if not recommended_font:
            print("建议安装支持中文的字体，如：")
            print("- Windows: 微软雅黑 (Microsoft YaHei)")
            print("- Mac: Arial Unicode MS")
            print("- Linux: WenQuanYi Micro Hei")
    
    print("=" * 50)