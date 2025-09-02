#!/usr/bin/env python3
"""
测试数据获取功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_source import DataSource
from utils.logger import logger

def test_data_fetch():
    """测试数据获取"""
    print("🧪 测试AKShare数据获取功能")
    print("=" * 50)
    
    data_source = DataSource()
    
    # 测试获取股票数据
    print("1. 测试获取股票历史数据...")
    try:
        # 使用平安银行作为测试
        symbol = "000001"
        print(f"   获取 {symbol} 最近30天数据...")
        
        stock_data = data_source.get_stock_data(symbol, days=30)
        
        if not stock_data.empty:
            print(f"   ✅ 成功获取 {len(stock_data)} 条记录")
            print(f"   数据列: {list(stock_data.columns)}")
            print(f"   数据范围: {stock_data.index[0]} 到 {stock_data.index[-1]}")
            print(f"   最新价格: {stock_data['close'].iloc[-1]:.2f}")
            
            # 检查必要的列是否存在
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in stock_data.columns]
            
            if missing_cols:
                print(f"   ⚠️  缺少必要列: {missing_cols}")
            else:
                print("   ✅ 所有必要列都存在")
                
        else:
            print("   ❌ 获取的数据为空")
            
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
        logger.error(f"数据获取测试失败: {e}")
    
    print("\n2. 测试获取股票列表...")
    try:
        stock_list = data_source.get_stock_list()
        if not stock_list.empty:
            print(f"   ✅ 成功获取 {len(stock_list)} 只股票")
            print(f"   列名: {list(stock_list.columns)}")
        else:
            print("   ❌ 股票列表为空")
    except Exception as e:
        print(f"   ❌ 获取股票列表失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    test_data_fetch()