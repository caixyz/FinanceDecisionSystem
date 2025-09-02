"""
测试修复后的data_source模块
"""
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_source import DataSource
import pandas as pd

def test_data_source():
    """测试DataSource类"""
    print("=" * 50)
    print("测试修复后的 DataSource 模块")
    print("=" * 50)
    
    try:
        # 创建DataSource实例
        print("正在创建DataSource实例...")
        ds = DataSource()
        print("✅ DataSource实例创建成功")
        
        # 测试获取股票数据
        symbol = "000001"
        days = 30
        
        print(f"\n正在获取股票 {symbol} 的 {days} 天数据...")
        data = ds.get_stock_data(symbol, days=days)
        
        if data is not None and not data.empty:
            print(f"✅ 获取数据成功！")
            print(f"数据形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            print(f"数据类型:")
            print(data.dtypes)
            print(f"\n前5行数据:")
            print(data.head())
            print(f"\n最后5行数据:")
            print(data.tail())
            
            # 检查必要的列是否存在
            required_cols = ['open', 'close', 'high', 'low', 'volume']
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if not missing_cols:
                print("✅ 所有必要的列都存在")
                return True
            else:
                print(f"❌ 缺少必要的列: {missing_cols}")
                return False
        else:
            print("❌ 获取数据失败或数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_source()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！数据源模块修复成功！")
    else:
        print("💥 测试失败，需要进一步调试")
    print("=" * 50)