#!/usr/bin/env python3
"""
数据库验证脚本
验证AKShare接口表是否正确创建和配置
"""

import sqlite3
import os

def verify_database():
    """验证数据库状态"""
    db_path = os.path.join('data', 'finance_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🎯 AKShare接口数据库验证报告")
        print("=" * 50)
        
        # 1. 检查所有AKShare相关表
        print("\n📋 数据表列表:")
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' AND name LIKE 'akshare_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        for table_name, sql in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table_name}: {count} 条记录")
        
        # 2. 检查索引
        print("\n🔍 索引列表:")
        cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master 
            WHERE type='index' AND tbl_name LIKE 'akshare_%'
            ORDER BY tbl_name, name
        """)
        indexes = cursor.fetchall()
        
        index_count = 0
        for index_name, table_name, sql in indexes:
            if not index_name.startswith('sqlite_autoindex_'):
                print(f"  🔑 {table_name}.{index_name}")
                index_count += 1
        
        print(f"\n📊 总计: {len(tables)} 个表, {index_count} 个自定义索引")
        
        # 3. 检查示例数据
        print("\n📈 示例数据:")
        cursor.execute("SELECT interface_name, interface_name_cn, category_level1 FROM akshare_interfaces LIMIT 3")
        samples = cursor.fetchall()
        
        for name, cn_name, category in samples:
            print(f"  📌 {name} ({cn_name}) - {category}")
        
        # 4. 检查表结构完整性
        print("\n🔧 表结构验证:")
        required_tables = [
            'akshare_interfaces',
            'akshare_interface_params', 
            'akshare_interface_returns',
            'akshare_interface_examples',
            'akshare_interface_errors',
            'akshare_interface_tags',
            'akshare_interface_tag_relations',
            'akshare_interface_stats'
        ]
        
        missing_tables = []
        for table in required_tables:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                missing_tables.append(table)
        
        if missing_tables:
            print(f"  ❌ 缺失表: {missing_tables}")
        else:
            print("  ✅ 所有必需表都存在")
        
        # 5. 检查外键关系
        print("\n🔗 外键关系验证:")
        cursor.execute("""
            SELECT interface_name 
            FROM akshare_interfaces 
            WHERE id IN (SELECT DISTINCT interface_id FROM akshare_interface_params LIMIT 3)
        """)
        related_interfaces = cursor.fetchall()
        
        if related_interfaces:
            print("  ✅ 外键关系正常")
            for iface in related_interfaces:
                print(f"    📋 {iface[0]}")
        else:
            print("  ⚠️  暂无关联数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证错误: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_database()