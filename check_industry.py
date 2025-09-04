import sys
sys.path.append('.')
import pandas as pd
import akshare as ak

# 检查是否有其他接口可以获取行业信息
print("检查其他行业信息接口...")

# 1. 检查股票基本信息接口
print("\n1. 尝试ak.stock_individual_info_em()...")
try:
    # 用平安银行测试
    info = ak.stock_individual_info_em(symbol="000001")
    print("股票基本信息:")
    print(info)
    print("列名:", list(info.columns) if hasattr(info, 'columns') else "无列名")
except Exception as e:
    print(f"获取股票基本信息失败: {e}")

# 2. 检查股票列表接口
print("\n2. 尝试ak.stock_zh_a_spot()...")
try:
    df2 = ak.stock_zh_a_spot()
    print(f"获取到 {len(df2)} 条股票数据")
    print("列名:", list(df2.columns))
    
    # 检查是否有行业相关列
    industry_cols2 = [col for col in df2.columns if '行业' in str(col) or 'industry' in str(col).lower()]
    print(f"行业相关列: {industry_cols2}")
    
except Exception as e:
    print(f"获取股票列表失败: {e}")

# 3. 检查行业分类接口
print("\n3. 尝试ak.stock_board_industry_name_em()...")
try:
    industry_df = ak.stock_board_industry_name_em()
    print(f"获取到 {len(industry_df)} 个行业")
    print("列名:", list(industry_df.columns))
    print("前5个行业:")
    print(industry_df.head())
except Exception as e:
    print(f"获取行业列表失败: {e}")

# 4. 检查股票行业分类接口
print("\n4. 尝试ak.stock_board_industry_cons_em()...")
try:
    # 用第一个行业测试
    if 'industry_df' in locals() and not industry_df.empty:
        first_industry = industry_df.iloc[0]['板块名称']
        stocks_in_industry = ak.stock_board_industry_cons_em(symbol=first_industry)
        print(f"行业 {first_industry} 包含 {len(stocks_in_industry)} 只股票")
        print("列名:", list(stocks_in_industry.columns))
        print("前3条数据:")
        print(stocks_in_industry.head(3))
except Exception as e:
    print(f"获取行业股票列表失败: {e}")