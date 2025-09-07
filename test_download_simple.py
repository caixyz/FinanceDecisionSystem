#!/usr/bin/env python3
"""
测试AKShare接口下载功能的脚本 - 使用简单接口
"""
import sqlite3
import pandas as pd
import akshare as ak

def test_simple_interface():
    """测试下载简单接口数据"""
    print("测试下载接口列表数据...")
    
    try:
        # 使用简单的接口测试
        df = ak.stock_zh_a_spot()
        
        if df is not None and not df.empty:
            print(f"✅ 成功获取数据: {len(df)} 条记录")
            print(f"列名: {list(df.columns)}")
            
            # 创建表名
            table_name = "akshare_stock_zh_a_spot"
            
            # 连接到数据库
            conn = sqlite3.connect('data/finance_data.db')
            
            # 插入数据
            df['download_time'] = pd.Timestamp.now()
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # 验证数据
            result = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", conn)
            print(f"✅ 数据已保存到数据库表: {table_name}")
            print(f"总记录数: {result.iloc[0]['count']}")
            
            # 显示表结构
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("表结构:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            conn.close()
            return True
        else:
            print("❌ 获取数据为空")
            return False
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def test_database_tables():
    """测试数据库中的表"""
    try:
        conn = sqlite3.connect('data/finance_data.db')
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  {table[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AKShare接口下载功能测试")
    print("=" * 50)
    
    # 测试数据库
    test_database_tables()
    
    print()
    
    # 测试接口下载
    test_simple_interface()
    
    print()
    print("测试完成！")