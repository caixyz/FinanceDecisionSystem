#!/usr/bin/env python3
"""
测试AKShare接口下载功能的脚本
"""
import requests
import json
import sqlite3
import pandas as pd
import akshare as ak

# 测试单个接口下载
def test_download_interface():
    """测试下载单个接口数据"""
    print("测试下载股票历史数据接口...")
    
    try:
        # 使用AKShare获取数据
        df = ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="")
        
        if df is not None and not df.empty:
            print(f"✅ 成功获取数据: {len(df)} 条记录")
            print(f"列名: {list(df.columns)}")
            print("前5行数据:")
            print(df.head())
            
            # 创建表名
            table_name = "akshare_stock_zh_a_hist"
            
            # 连接到数据库
            conn = sqlite3.connect('data/finance_data.db')
            
            # 插入数据
            df['download_time'] = pd.Timestamp.now()
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # 验证数据
            result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn)
            print(f"✅ 数据已保存到数据库表: {table_name}")
            print(f"总记录数: {result.iloc[0]['count']}")
            
            conn.close()
            return True
        else:
            print("❌ 获取数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        conn = sqlite3.connect('data/finance_data.db')
        cursor = conn.cursor()
        
        # 检查akshare_interfaces表
        cursor.execute("SELECT COUNT(*) FROM akshare_interfaces")
        count = cursor.fetchone()[0]
        print(f"✅ 数据库连接正常，akshare_interfaces表中有 {count} 条记录")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AKShare接口下载功能测试")
    print("=" * 50)
    
    # 测试数据库连接
    test_database_connection()
    
    print()
    
    # 测试接口下载
    test_download_interface()
    
    print()
    print("测试完成！")