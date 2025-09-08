#!/usr/bin/env python3
"""
检查数据库中的接口名称是否正确
"""
import sqlite3

def check_interface_names():
    """检查接口名称"""
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    # 查找包含lg_indicator的接口
    cursor.execute("SELECT interface_name FROM akshare_interfaces WHERE interface_name LIKE '%lg_indicator%'")
    results = cursor.fetchall()
    print("数据库中的lg_indicator相关接口:")
    for result in results:
        print(f"  {result[0]}")
    
    # 检查错误的接口名
    cursor.execute("SELECT interface_name FROM akshare_interfaces WHERE interface_name='stock_a_lg_indicator'")
    wrong_result = cursor.fetchall()
    print("\n错误的stock_a_lg_indicator:")
    for result in wrong_result:
        print(f"  {result[0]}")
    
    # 检查正确的接口名
    cursor.execute("SELECT interface_name FROM akshare_interfaces WHERE interface_name='stock_a_indicator_lg'")
    correct_result = cursor.fetchall()
    print("\n正确的stock_a_indicator_lg:")
    for result in correct_result:
        print(f"  {result[0]}")
    
    # 检查所有股票相关接口
    cursor.execute("SELECT interface_name, interface_name_cn FROM akshare_interfaces WHERE interface_name LIKE 'stock_%'")
    stock_results = cursor.fetchall()
    print(f"\n股票相关接口总数: {len(stock_results)}")
    print("前10个股票接口:")
    for name, name_cn in stock_results[:10]:
        print(f"  {name} - {name_cn}")
    
    conn.close()

if __name__ == "__main__":
    check_interface_names()