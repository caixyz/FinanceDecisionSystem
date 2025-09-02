"""
调试AKShare数据问题的测试脚本
"""
import akshare as ak
import pandas as pd
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_akshare_data():
    """测试AKShare数据获取"""
    print("=" * 50)
    print("测试 AKShare 数据获取")
    print("=" * 50)
    
    try:
        # 测试获取平安银行数据
        symbol = "000001"
        print(f"正在获取股票 {symbol} 的数据...")
        
        # 获取原始数据
        raw_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="")
        
        print(f"原始数据形状: {raw_data.shape}")
        print(f"原始数据列名: {list(raw_data.columns)}")
        print(f"原始数据列数: {len(raw_data.columns)}")
        print("\n前5行数据:")
        print(raw_data.head())
        
        print("\n数据类型:")
        print(raw_data.dtypes)
        
        return raw_data
        
    except Exception as e:
        print(f"获取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_data_standardization(df):
    """测试数据标准化"""
    print("\n" + "=" * 50)
    print("测试数据标准化")
    print("=" * 50)
    
    if df is None or df.empty:
        print("没有数据可以标准化")
        return None
    
    try:
        # 获取实际列数
        actual_cols = len(df.columns)
        print(f"实际列数: {actual_cols}")
        print(f"实际列名: {list(df.columns)}")
        
        # 基础列名映射
        base_cols = ['date', 'open', 'close', 'high', 'low', 'volume']
        extended_cols = ['turnover', 'amplitude', 'change_pct', 'change_amount', 'turnover_rate']
        
        # 根据实际列数确定列名
        if actual_cols >= 6:
            new_cols = base_cols + extended_cols[:actual_cols-6]
            print(f"计划使用的列名: {new_cols}")
            print(f"新列名数量: {len(new_cols)}")
            
            if len(new_cols) == actual_cols:
                df_copy = df.copy()
                df_copy.columns = new_cols
                print("列名映射成功!")
                print(f"映射后的列名: {list(df_copy.columns)}")
                return df_copy
            else:
                print(f"列名数量不匹配: 需要{actual_cols}个，提供了{len(new_cols)}个")
                return None
        else:
            print(f"列数不足: 至少需要6列，实际只有{actual_cols}列")
            return None
            
    except Exception as e:
        print(f"数据标准化失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_data_source_module():
    """测试data_source模块"""
    print("\n" + "=" * 50)
    print("测试 data_source 模块")
    print("=" * 50)
    
    try:
        from core.data_source import DataSource
        
        ds = DataSource()
        print("DataSource实例创建成功")
        
        # 测试获取股票数据
        symbol = "000001"
        days = 30
        
        print(f"正在获取股票 {symbol} 的 {days} 天数据...")
        data = ds.get_stock_data(symbol, days)
        
        if data is not None and not data.empty:
            print(f"获取数据成功！形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            print("\n前5行:")
            print(data.head())
            return True
        else:
            print("获取数据失败或数据为空")
            return False
            
    except Exception as e:
        print(f"测试data_source模块失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始调试AKShare数据问题...")
    
    # 1. 测试原始AKShare数据
    raw_data = test_akshare_data()
    
    # 2. 测试数据标准化
    if raw_data is not None:
        standardized_data = test_data_standardization(raw_data)
    
    # 3. 测试data_source模块
    success = test_data_source_module()
    
    print("\n" + "=" * 50)
    print("调试完成")
    print("=" * 50)
    
    if success:
        print("✅ 所有测试通过")
    else:
        print("❌ 存在问题，需要进一步修复")