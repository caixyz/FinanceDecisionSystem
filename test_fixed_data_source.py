#!/usr/bin/env python3
"""
测试修复后的数据源模块
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fixed_data_source():
    """测试修复后的数据获取"""
    print("🔧 测试修复后的数据源模块")
    print("=" * 60)
    
    try:
        # 重新导入模块以确保使用最新代码
        import importlib
        if 'core.data_source' in sys.modules:
            importlib.reload(sys.modules['core.data_source'])
        
        from core.data_source import DataSource
        from utils.logger import logger
        
        print("1. 创建数据源实例...")
        data_source = DataSource()
        print("   ✅ 数据源初始化成功")
        
        print("\n2. 测试获取股票数据...")
        symbol = "000001"
        print(f"   正在获取 {symbol} 的30天数据...")
        
        try:
            stock_data = data_source.get_stock_data(symbol, days=30)
            
            if not stock_data.empty:
                print(f"   ✅ 成功获取 {len(stock_data)} 条记录")
                print(f"   数据列名: {list(stock_data.columns)}")
                print(f"   数据形状: {stock_data.shape}")
                print(f"   最新价格: {stock_data['close'].iloc[-1]:.2f}")
                print(f"   日期范围: {stock_data.index[0]} 到 {stock_data.index[-1]}")
                
                # 检查必要的列
                required_cols = ['open', 'high', 'low', 'close', 'volume']
                missing_cols = [col for col in required_cols if col not in stock_data.columns]
                
                if missing_cols:
                    print(f"   ⚠️  缺少列: {missing_cols}")
                else:
                    print("   ✅ 所有必要列都存在")
                
                return True
                
            else:
                print("   ❌ 获取的数据为空")
                return False
                
        except Exception as e:
            print(f"   ❌ 数据获取失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 模块导入或初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_stocks():
    """测试多个股票的数据获取"""
    print("\n" + "=" * 60)
    print("🔄 测试多个股票数据获取")
    print("=" * 60)
    
    stocks = ["000001", "600519", "000002"]  # 平安银行、贵州茅台、万科A
    names = ["平安银行", "贵州茅台", "万科A"]
    
    try:
        from core.data_source import DataSource
        data_source = DataSource()
        
        success_count = 0
        for i, symbol in enumerate(stocks):
            print(f"\n{i+1}. 测试 {names[i]} ({symbol})")
            try:
                data = data_source.get_stock_data(symbol, days=10)  # 只获取10天数据，快速测试
                if not data.empty:
                    print(f"   ✅ 成功获取 {len(data)} 条记录")
                    print(f"   列数: {len(data.columns)}, 列名: {list(data.columns)}")
                    success_count += 1
                else:
                    print(f"   ❌ 数据为空")
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
        
        print(f"\n📊 测试结果: {success_count}/{len(stocks)} 个股票数据获取成功")
        return success_count == len(stocks)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 修复验证测试")
    print("=" * 60)
    
    # 基础测试
    basic_success = test_fixed_data_source()
    
    # 多股票测试
    multi_success = test_multiple_stocks()
    
    print("\n" + "=" * 60)
    if basic_success and multi_success:
        print("✅ 所有测试通过！修复成功生效！")
        print("🎉 系统可以正常获取和处理AKShare数据")
    else:
        print("❌ 测试失败，需要进一步检查问题")
    print("=" * 60)