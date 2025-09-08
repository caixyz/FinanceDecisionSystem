#!/usr/bin/env python3
"""
创建AKShare接口表索引
"""

import sqlite3
import os

def create_indexes():
    """创建索引"""
    db_path = os.path.join('data', 'finance_data.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(akshare_interfaces)")
        columns = cursor.fetchall()
        print("akshare_interfaces表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 创建索引
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_interfaces_name ON akshare_interfaces(interface_name)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_category1 ON akshare_interfaces(category_level1)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_category2 ON akshare_interfaces(category_level2)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_category3 ON akshare_interfaces(category_level3)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_status ON akshare_interfaces(status)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_module ON akshare_interfaces(module_name)",
            "CREATE INDEX IF NOT EXISTS idx_interfaces_type ON akshare_interfaces(function_type)",
            "CREATE INDEX IF NOT EXISTS idx_params_interface ON akshare_interface_params(interface_id)",
            "CREATE INDEX IF NOT EXISTS idx_returns_interface ON akshare_interface_returns(interface_id)",
            "CREATE INDEX IF NOT EXISTS idx_examples_interface ON akshare_interface_examples(interface_id)",
            "CREATE INDEX IF NOT EXISTS idx_errors_interface ON akshare_interface_errors(interface_id)",
            "CREATE INDEX IF NOT EXISTS idx_stats_interface ON akshare_interface_stats(interface_id)"
        ]
        
        for sql in indexes:
            try:
                cursor.execute(sql)
                print(f"✅ 创建成功: {sql}")
            except Exception as e:
                print(f"❌ 创建失败: {sql} - {e}")
        
        conn.commit()
        print("索引创建完成")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_indexes()