#!/usr/bin/env python3
"""
简单测试AKShare数据获取的脚本，不依赖我们的模块
"""
import akshare as ak
import pandas as pd

def test_akshare_direct():
    """直接测试AKShare数据获取"""
    print("🧪 直接测试AKShare数据获取")
    print("=" * 50)
    
    try:
        print("1. 测试获取股票历史数据...")
        
        # 直接使用AKShare获取数据
        symbol = "000001"
        print(f"   获取 {symbol} 数据...")
        
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
        
        if not df.empty:
            print(f"   ✅ 成功获取 {len(df)} 条记录")
            print(f"   原始列数: {len(df.columns)}")
            print(f"   原始列名: {list(df.columns)}")
            print(f"   数据样例:")
            print(df.head())
            
            # 测试动态列名映射
            actual_cols = len(df.columns)
            base_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
            extended_cols = ['turnover', 'amplitude', 'change_pct', 'change_amount', 'turnover_rate']
            
            if actual_cols >= 6:
                new_cols = base_cols + extended_cols[:actual_cols-6]
                df.columns = new_cols
                print(f"   ✅ 动态映射后列名: {list(df.columns)}")
            else:
                print(f"   ⚠️  列数不足6列: {actual_cols}")
            
        else:
            print("   ❌ 获取的数据为空")
            
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_akshare_direct()