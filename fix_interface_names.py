#!/usr/bin/env python3
"""
修复数据库中的错误接口名称
"""
import sqlite3
import akshare as ak

def fix_wrong_interface_names():
    """修复错误的接口名称"""
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    # 检查stock_a_lg_indicator是否存在
    cursor.execute("SELECT COUNT(*) FROM akshare_interfaces WHERE interface_name='stock_a_lg_indicator'")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print("发现错误的接口名称: stock_a_lg_indicator")
        
        # 检查正确的接口是否存在
        cursor.execute("SELECT COUNT(*) FROM akshare_interfaces WHERE interface_name='stock_a_indicator_lg'")
        correct_count = cursor.fetchone()[0]
        
        if correct_count == 0:
            # 更新错误的接口名称
            cursor.execute("""
                UPDATE akshare_interfaces 
                SET interface_name = 'stock_a_indicator_lg',
                    interface_name_cn = 'A股技术指标'
                WHERE interface_name = 'stock_a_lg_indicator'
            """)
            
            print("已更新接口名称: stock_a_lg_indicator -> stock_a_indicator_lg")
        else:
            # 删除错误的接口
            cursor.execute("DELETE FROM akshare_interfaces WHERE interface_name='stock_a_lg_indicator'")
            print("已删除重复的接口: stock_a_lg_indicator")
    
    # 检查其他可能的错误接口
    cursor.execute("SELECT interface_name FROM akshare_interfaces")
    all_interfaces = cursor.fetchall()
    
    wrong_names = []
    for interface_name, in all_interfaces:
        if not hasattr(ak, interface_name):
            wrong_names.append(interface_name)
    
    if wrong_names:
        print(f"发现{len(wrong_names)}个不存在的接口:")
        for name in wrong_names:
            print(f"  {name}")
            
        # 将这些接口标记为不可用
        for name in wrong_names:
            cursor.execute("""
                UPDATE akshare_interfaces 
                SET status = 'invalid'
                WHERE interface_name = ?
            """, (name,))
        
        print("已将不存在的接口标记为invalid")
    
    conn.commit()
    conn.close()
    
    print("接口名称修复完成")

def verify_interface_names():
    """验证接口名称"""
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT interface_name FROM akshare_interfaces WHERE status='active'")
    active_interfaces = cursor.fetchall()
    
    valid_count = 0
    invalid_count = 0
    
    for interface_name, in active_interfaces:
        if hasattr(ak, interface_name):
            valid_count += 1
        else:
            invalid_count += 1
            print(f"无效接口: {interface_name}")
    
    print(f"验证完成 - 有效接口: {valid_count}, 无效接口: {invalid_count}")
    conn.close()

if __name__ == "__main__":
    fix_wrong_interface_names()
    verify_interface_names()