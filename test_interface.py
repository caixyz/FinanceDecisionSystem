#!/usr/bin/env python3
"""测试stock_a_indicator_lg接口"""

import akshare as ak
import json
import sys

def test_stock_a_indicator_lg():
    """测试stock_a_indicator_lg接口"""
    print("正在测试 stock_a_indicator_lg 接口...")
    
    try:
        # 直接调用接口
        df = ak.stock_a_indicator_lg()
        
        if df is None:
            print("❌ 接口返回 None")
            return False
        
        if df.empty:
            print("⚠️  接口返回空数据框")
            return False
        
        print(f"✅ 接口调用成功！返回数据行数: {len(df)}")
        print(f"📊 数据列数: {len(df.columns)}")
        print("📋 列名:", list(df.columns))
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print("💡 这通常表示接口返回空数据或格式错误")
        return False
    
    except Exception as e:
        print(f"❌ 接口调用失败: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_stock_a_indicator_lg()
    sys.exit(0 if success else 1)