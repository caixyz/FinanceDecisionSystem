#!/usr/bin/env python3
"""
导入AKShare接口数据到数据库
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path

def import_stock_interfaces():
    """导入股票接口数据"""
    db_path = os.path.join('data', 'finance_data.db')
    csv_file = os.path.join('docs', 'akshare_stock_interfaces_with_chinese.csv')
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        print(f"正在导入股票接口数据: {len(df)} 条记录")
        
        # 插入数据
        for _, row in df.iterrows():
            cursor = conn.cursor()
            
            # 插入接口主表
            cursor.execute("""
                INSERT OR REPLACE INTO akshare_interfaces 
                (interface_name, interface_name_cn, interface_description, category_level1, category_level2, 
                 module_name, function_type, status, create_time, update_time)
                VALUES (?, ?, ?, '股票', ?, 'akshare', '数据获取', 'active', datetime('now'), datetime('now'))
            """, [
                row['接口名称'], 
                row['中文描述'], 
                row['主要功能'], 
                row['类型']
            ])
            
            interface_id = cursor.lastrowid
            
            # 插入标签
            if pd.notna(row['标签']):
                tags = str(row['标签']).split(',')
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        # 插入标签（如果不存在）
                        cursor.execute("INSERT OR IGNORE INTO akshare_interface_tags (tag_name) VALUES (?)", (tag,))
                        cursor.execute("SELECT id FROM akshare_interface_tags WHERE tag_name = ?", (tag,))
                        tag_id = cursor.fetchone()[0]
                        
                        # 插入关联
                        cursor.execute("""
                            INSERT OR IGNORE INTO akshare_interface_tag_relations (interface_id, tag_id) 
                            VALUES (?, ?)
                        """, (interface_id, tag_id))
        
        conn.commit()
        print("✅ 股票接口数据导入完成")
        
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        conn.rollback()
    finally:
        conn.close()

def import_market_interfaces():
    """导入市场接口数据"""
    db_path = os.path.join('data', 'finance_data.db')
    csv_file = os.path.join('docs', 'akshare_market_interfaces_with_chinese.csv')
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        print(f"正在导入市场接口数据: {len(df)} 条记录")
        
        # 插入数据
        for _, row in df.iterrows():
            cursor = conn.cursor()
            
            # 插入接口主表
            cursor.execute("""
                INSERT OR REPLACE INTO akshare_interfaces 
                (interface_name, interface_name_cn, interface_description, category_level1, category_level2, 
                 module_name, function_type, status, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, 'akshare', '数据获取', 'active', datetime('now'), datetime('now'))
            """, [
                row['接口名称'], 
                row['中文描述'], 
                row['主要功能'], 
                row['类型'],
                row['类型']  # 使用类型作为二级分类
            ])
            
            interface_id = cursor.lastrowid
            
            # 插入标签（从类型字段提取）
            tag = str(row['类型']).replace('相关', '')
            if tag:
                cursor.execute("INSERT OR IGNORE INTO akshare_interface_tags (tag_name) VALUES (?)", (tag,))
                cursor.execute("SELECT id FROM akshare_interface_tags WHERE tag_name = ?", (tag,))
                tag_result = cursor.fetchone()
                if tag_result:
                    tag_id = tag_result[0]
                    cursor.execute("""
                        INSERT OR IGNORE INTO akshare_interface_tag_relations (interface_id, tag_id) 
                        VALUES (?, ?)
                    """, (interface_id, tag_id))
        
        conn.commit()
        print("✅ 市场接口数据导入完成")
        
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_database_stats():
    """获取数据库统计信息"""
    db_path = os.path.join('data', 'finance_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # 接口总数
        cursor.execute("SELECT COUNT(*) FROM akshare_interfaces")
        stats['total_interfaces'] = cursor.fetchone()[0]
        
        # 按分类统计
        cursor.execute("""
            SELECT category_level1, COUNT(*) 
            FROM akshare_interfaces 
            GROUP BY category_level1
        """)
        stats['by_category'] = cursor.fetchall()
        
        # 按状态统计
        cursor.execute("SELECT status, COUNT(*) FROM akshare_interfaces GROUP BY status")
        stats['by_status'] = cursor.fetchall()
        
        # 标签统计
        cursor.execute("SELECT COUNT(*) FROM akshare_interface_tags")
        stats['total_tags'] = cursor.fetchone()[0]
        
        return stats
        
    except Exception as e:
        print(f"统计错误: {e}")
        return {}
    finally:
        conn.close()

if __name__ == "__main__":
    # 导入数据
    import_stock_interfaces()
    import_market_interfaces()
    
    # 显示统计信息
    stats = get_database_stats()
    print("\n📊 数据库统计信息:")
    print(f"总接口数量: {stats.get('total_interfaces', 0)}")
    print(f"标签数量: {stats.get('total_tags', 0)}")
    
    print("\n按分类统计:")
    for category, count in stats.get('by_category', []):
        print(f"  {category}: {count} 个接口")
    
    print("\n按状态统计:")
    for status, count in stats.get('by_status', []):
        print(f"  {status}: {count} 个接口")