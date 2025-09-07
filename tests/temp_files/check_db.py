import sqlite3
import pandas as pd

def check_database():
    """检查数据库中的股票信息"""
    try:
        # 连接数据库
        conn = sqlite3.connect('data/finance_data.db')
        
        # 查询股票信息表
        query = "SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio FROM stock_info LIMIT 10"
        df = pd.read_sql_query(query, conn)
        
        print("数据库中的股票信息:")
        print(df)
        
        # 检查是否有完整的字段数据
        print("\n字段数据统计:")
        print(f"总记录数: {len(df)}")
        print(f"有行业信息的记录数: {df['industry'].notna().sum()}")
        print(f"有市值信息的记录数: {df['market_cap'].notna().sum()}")
        print(f"有市盈率信息的记录数: {df['pe_ratio'].notna().sum()}")
        print(f"有市净率信息的记录数: {df['pb_ratio'].notna().sum()}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")

if __name__ == "__main__":
    check_database()