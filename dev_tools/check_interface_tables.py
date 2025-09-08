#!/usr/bin/env python3
"""
统计所有接口相关表及数据量
"""
import sqlite3
import pandas as pd

def get_interface_tables_info():
    """获取所有接口相关表的信息"""
    
    # 连接到数据库
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = cursor.fetchall()
    
    interface_tables = []
    
    print("=" * 80)
    print("接口相关表统计报告")
    print("=" * 80)
    
    # 统计接口相关表
    for table_name, in all_tables:
        # 判断是否为接口相关表
        is_interface_table = (
            table_name.startswith('akshare_') or 
            table_name in ['akshare_interfaces', 'stock_info', 'stock_daily'] or
            'interface' in table_name.lower()
        )
        
        if is_interface_table:
            # 获取表记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # 获取表结构信息
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_count = len(columns)
            
            # 获取表大小（使用近似方法）
            try:
                cursor.execute(f"SELECT SUM(length(sql) + length(name)) FROM sqlite_master WHERE name='{table_name}'")
                size_kb = 0  # 简单处理，实际大小需要更复杂的计算
            except:
                size_kb = 0
            
            interface_tables.append({
                '表名': table_name,
                '记录数': count,
                '列数': column_count,
                '大小(KB)': "-",
                '说明': get_table_description(table_name)
            })
    
    # 创建DataFrame并排序
    df = pd.DataFrame(interface_tables)
    df = df.sort_values('记录数', ascending=False)
    
    print("\n📊 接口相关表详细信息:")
    print("-" * 80)
    print(df.to_string(index=False))
    
    # 统计汇总
    total_tables = len(interface_tables)
    total_records = df['记录数'].sum()
    
    print("\n📈 统计汇总:")
    print("-" * 80)
    print(f"接口相关表总数: {total_tables}")
    print(f"总记录数: {total_records:,}")
    
    # 按类别分组
    print("\n📋 按类别分组:")
    print("-" * 80)
    
    categories = {
        '接口元数据表': [t for t in interface_tables if 'interface' in t['表名'] and 'meta' not in t['表名']],
        '接口参数表': [t for t in interface_tables if 'param' in t['表名']],
        '接口返回表': [t for t in interface_tables if 'return' in t['表名']],
        '接口示例表': [t for t in interface_tables if 'example' in t['表名']],
        '接口错误表': [t for t in interface_tables if 'error' in t['表名']],
        '接口标签表': [t for t in interface_tables if 'tag' in t['表名']],
        '接口统计表': [t for t in interface_tables if 'stats' in t['表名']],
        '实际数据表': [t for t in interface_tables if t['表名'].startswith('akshare_') and not any(x in t['表名'] for x in ['interface', 'param', 'return', 'example', 'error', 'tag', 'stats'])],
        '股票基础表': [t for t in interface_tables if t['表名'] in ['stock_info', 'stock_daily']]
    }
    
    for category, tables in categories.items():
        if tables:
            total_records_cat = sum(t['记录数'] for t in tables)
            print(f"{category}: {len(tables)}个表, {total_records_cat:,}条记录")
    
    conn.close()
    return df

def get_table_description(table_name):
    """获取表的描述信息"""
    descriptions = {
        'akshare_interfaces': 'AKShare接口主表，包含所有接口的基本信息',
        'akshare_interface_params': '接口参数表，记录每个接口的参数信息',
        'akshare_interface_returns': '接口返回表，记录接口的返回字段信息',
        'akshare_interface_examples': '接口示例表，包含接口的使用示例',
        'akshare_interface_errors': '接口错误表，记录接口可能的错误信息',
        'akshare_interface_tags': '接口标签表，定义接口的分类标签',
        'akshare_interface_tag_relations': '接口标签关联表，关联接口和标签',
        'akshare_interface_stats': '接口统计表，记录接口的统计信息',
        'stock_info': '股票基础信息表',
        'stock_daily': '股票日线数据表'
    }
    
    return descriptions.get(table_name, 'AKShare数据下载表')

def check_recent_downloads():
    """检查最近下载的数据表"""
    print("\n🔄 检查最近下载的数据:")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect('data/finance_data.db')
        cursor = conn.cursor()
        
        # 获取所有以akshare_开头的数据表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'akshare_%' AND name NOT LIKE '%interface%' ORDER BY name")
        data_tables = cursor.fetchall()
        
        if data_tables:
            for table_name, in data_tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()[0]
                
                # 检查是否有download_time列
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'download_time' in columns:
                    cursor.execute(f"SELECT MAX(download_time) as latest FROM {table_name}")
                    latest = cursor.fetchone()[0]
                    print(f"{table_name}: {count:,}条记录，最新下载时间: {latest}")
                else:
                    print(f"{table_name}: {count:,}条记录")
        else:
            print("暂无下载的数据表")
            
        conn.close()
    except Exception as e:
        print(f"检查失败: {e}")

if __name__ == "__main__":
    # 获取接口表统计
    df = get_interface_tables_info()
    
    # 检查最近下载
    check_recent_downloads()
    
    print("\n" + "=" * 80)
    print("统计完成！")
    print("=" * 80)