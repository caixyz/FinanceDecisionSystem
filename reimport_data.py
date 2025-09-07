#!/usr/bin/env python3
"""
重新导入AKShare接口数据
"""

import sqlite3
import pandas as pd
import os

def clear_and_reimport():
    """清空并重新导入数据"""
    db_path = os.path.join('data', 'finance_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 清空现有数据（保留表结构）
        tables = [
            'akshare_interface_tag_relations',
            'akshare_interface_tags',
            'akshare_interface_stats',
            'akshare_interface_errors',
            'akshare_interface_examples',
            'akshare_interface_returns',
            'akshare_interface_params',
            'akshare_interfaces'
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        conn.commit()
        print("✅ 已清空现有数据")
        
        # 重新导入股票接口数据
        stock_csv = os.path.join('docs', 'akshare_stock_interfaces_with_chinese.csv')
        stock_df = pd.read_csv(stock_csv)
        
        print(f"正在导入股票接口数据: {len(stock_df)} 条记录")
        
        for _, row in stock_df.iterrows():
            cursor.execute("""
                INSERT INTO akshare_interfaces 
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
            tag = str(row['类型']).replace('股票相关', '股票')
            cursor.execute("INSERT OR IGNORE INTO akshare_interface_tags (tag_name) VALUES (?)", (tag,))
            cursor.execute("SELECT id FROM akshare_interface_tags WHERE tag_name = ?", (tag,))
            tag_result = cursor.fetchone()
            if tag_result:
                tag_id = tag_result[0]
                cursor.execute("""
                    INSERT INTO akshare_interface_tag_relations (interface_id, tag_id) 
                    VALUES (?, ?)
                """, (interface_id, tag_id))
        
        # 重新导入市场接口数据
        market_csv = os.path.join('docs', 'akshare_market_interfaces_with_chinese.csv')
        market_df = pd.read_csv(market_csv)
        
        print(f"正在导入市场接口数据: {len(market_df)} 条记录")
        
        for _, row in market_df.iterrows():
            cursor.execute("""
                INSERT INTO akshare_interfaces 
                (interface_name, interface_name_cn, interface_description, category_level1, category_level2, 
                 module_name, function_type, status, create_time, update_time)
                VALUES (?, ?, ?, ?, ?, 'akshare', '数据获取', 'active', datetime('now'), datetime('now'))
            """, [
                row['接口名称'], 
                row['中文描述'], 
                row['主要功能'], 
                row['类型'].replace('相关', ''),
                row['类型'].replace('相关', '')
            ])
            
            interface_id = cursor.lastrowid
            
            # 插入标签
            tag = str(row['类型']).replace('相关', '')
            cursor.execute("INSERT OR IGNORE INTO akshare_interface_tags (tag_name) VALUES (?)", (tag,))
            cursor.execute("SELECT id FROM akshare_interface_tags WHERE tag_name = ?", (tag,))
            tag_result = cursor.fetchone()
            if tag_result:
                tag_id = tag_result[0]
                cursor.execute("""
                    INSERT INTO akshare_interface_tag_relations (interface_id, tag_id) 
                    VALUES (?, ?)
                """, (interface_id, tag_id))
        
        conn.commit()
        print("✅ 数据重新导入完成")
        
        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM akshare_interfaces")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT category_level1, COUNT(*) FROM akshare_interfaces GROUP BY category_level1")
        categories = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM akshare_interface_tags")
        tags = cursor.fetchone()[0]
        
        print(f"\n📊 导入结果:")
        print(f"总接口数量: {total}")
        print(f"标签数量: {tags}")
        print("按分类统计:")
        for cat, count in categories:
            print(f"  {cat}: {count} 个接口")
        
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_and_reimport()