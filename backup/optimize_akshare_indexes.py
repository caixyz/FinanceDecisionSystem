#!/usr/bin/env python3
"""
AKShare接口表索引优化脚本
为AKShare接口表添加性能优化索引
"""

import sqlite3
import os

def create_optimized_indexes():
    """为AKShare接口表创建优化索引"""
    
    db_path = os.path.join('data', 'finance_data.db')
    
    # 索引创建SQL语句
    index_sql = """
    -- 接口表索引
    CREATE INDEX IF NOT EXISTS idx_interfaces_category ON akshare_interfaces(category1, category2, category3);
    CREATE INDEX IF NOT EXISTS idx_interfaces_name ON akshare_interfaces(interface_name);
    CREATE INDEX IF NOT EXISTS idx_interfaces_status ON akshare_interfaces(status);
    CREATE INDEX IF NOT EXISTS idx_interfaces_update ON akshare_interfaces(update_time);
    
    -- 参数表索引
    CREATE INDEX IF NOT EXISTS idx_params_interface ON akshare_interface_params(interface_id);
    CREATE INDEX IF NOT EXISTS idx_params_name ON akshare_interface_params(param_name);
    CREATE INDEX IF NOT EXISTS idx_params_required ON akshare_interface_params(is_required);
    
    -- 返回字段索引
    CREATE INDEX IF NOT EXISTS idx_returns_interface ON akshare_interface_returns(interface_id);
    CREATE INDEX IF NOT EXISTS idx_returns_field ON akshare_interface_returns(field_name);
    
    -- 示例表索引
    CREATE INDEX IF NOT EXISTS idx_examples_interface ON akshare_interface_examples(interface_id);
    
    -- 错误码索引
    CREATE INDEX IF NOT EXISTS idx_errors_interface ON akshare_interface_errors(interface_id);
    CREATE INDEX IF NOT EXISTS idx_errors_code ON akshare_interface_errors(error_code);
    
    -- 标签关联索引
    CREATE INDEX IF NOT EXISTS idx_tag_rel_interface ON akshare_interface_tag_relations(interface_id);
    CREATE INDEX IF NOT EXISTS idx_tag_rel_tag ON akshare_interface_tag_relations(tag_id);
    
    -- 统计表索引
    CREATE INDEX IF NOT EXISTS idx_stats_interface ON akshare_interface_stats(interface_id);
    CREATE INDEX IF NOT EXISTS idx_stats_date ON akshare_interface_stats(last_call_date);
    """
    
    print("正在创建优化索引...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行索引创建
        cursor.executescript(index_sql)
        conn.commit()
        
        print("✅ 索引创建完成")
        
        # 验证索引创建
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_akshare_%'")
        indexes = cursor.fetchall()
        
        print(f"创建的AKShare索引数量: {len(indexes)}")
        for index in indexes:
            print(f"  - {index[0]}")
            
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
        
    finally:
        if conn:
            conn.close()

def analyze_database():
    """分析数据库状态"""
    db_path = os.path.join('data', 'finance_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表统计信息
        cursor.execute("""
            SELECT name, sql 
            FROM sqlite_master 
            WHERE type='table' AND name LIKE 'akshare_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        print("\n📊 数据库表结构分析:")
        for table_name, sql in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  📋 {table_name}: {count} 条记录")
        
        # 获取索引信息
        cursor.execute("""
            SELECT name, tbl_name, sql
            FROM sqlite_master 
            WHERE type='index' AND tbl_name LIKE 'akshare_%'
            ORDER BY tbl_name, name
        """)
        indexes = cursor.fetchall()
        
        print(f"\n🔍 数据库索引统计:")
        current_table = ""
        for index_name, table_name, sql in indexes:
            if table_name != current_table:
                print(f"  📊 {table_name}:")
                current_table = table_name
            print(f"    🔑 {index_name}")
        
    except Exception as e:
        print(f"❌ 分析错误: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_optimized_indexes()
    analyze_database()