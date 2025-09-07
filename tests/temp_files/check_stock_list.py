import sys
sys.path.append('.')
import pandas as pd
import akshare as ak

# 检查股票列表数据结构
print("检查ak.stock_zh_a_spot_em()返回的数据结构...")
try:
    df = ak.stock_zh_a_spot_em()
    print(f"获取到 {len(df)} 条股票数据")
    print("列名:", list(df.columns))
    print("\n前3条数据:")
    print(df.head(3))
    
    # 检查是否有行业相关列
    industry_cols = [col for col in df.columns if '行业' in str(col) or 'industry' in str(col).lower()]
    print(f"\n行业相关列: {industry_cols}")
    
    # 检查是否有其他信息列
    info_cols = [col for col in df.columns if col not in ['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低', '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']]
    print(f"其他可能的列: {info_cols}")
    
except Exception as e:
    print(f"获取股票列表失败: {e}")
    import traceback
    traceback.print_exc()