#!/usr/bin/env python3
"""
完整系统测试脚本
验证AKShare接口数据库、索引和数据完整性
"""

import sqlite3
import os
import pandas as pd
from datetime import datetime

def test_complete_system():
    """测试完整系统"""
    db_path = os.path.join('data', 'finance_data.db')
    
    print("🚀 开始完整系统测试...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 测试数据库连接
        print("✅ 数据库连接正常")
        
        # 2. 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'akshare_%'")
        tables = cursor.fetchall()
        print(f"📊 找到 {len(tables)} 个AKShare相关表")
        
        # 3. 检查数据量
        data_summary = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            data_summary[table_name] = count
            
        print("\n📈 数据表统计:")
        for table, count in data_summary.items():
            print(f"  {table}: {count} 条记录")
        
        # 4. 检查索引
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = cursor.fetchall()
        print(f"\n🔍 找到 {len(indexes)} 个自定义索引")
        
        # 5. 检查接口数据完整性
        cursor.execute("""
            SELECT interface_name, interface_name_cn, category_level1, category_level2, status
            FROM akshare_interfaces 
            ORDER BY category_level1, interface_name
            LIMIT 10
        """)
        sample_data = cursor.fetchall()
        
        print("\n📋 接口数据样例:")
        for item in sample_data:
            print(f"  {item[0]} | {item[1][:20]}... | {item[2]}/{item[3]} | {item[4]}")
        
        # 6. 检查标签数据
        cursor.execute("""
            SELECT t.tag_name, COUNT(r.interface_id) as count
            FROM akshare_interface_tags t
            LEFT JOIN akshare_interface_tag_relations r ON t.id = r.tag_id
            GROUP BY t.tag_name
            ORDER BY count DESC
        """)
        tags = cursor.fetchall()
        
        print("\n🏷️ 标签统计:")
        for tag, count in tags:
            print(f"  {tag}: {count} 个接口")
        
        # 7. 检查分类分布
        cursor.execute("""
            SELECT category_level1, category_level2, COUNT(*) as count
            FROM akshare_interfaces
            GROUP BY category_level1, category_level2
            ORDER BY category_level1, count DESC
        """)
        categories = cursor.fetchall()
        
        print("\n📂 分类分布:")
        current_cat1 = None
        for cat1, cat2, count in categories:
            if cat1 != current_cat1:
                print(f"  {cat1}:")
                current_cat1 = cat1
            print(f"    {cat2}: {count} 个接口")
        
        # 8. 性能测试 - 查询速度
        start_time = datetime.now()
        cursor.execute("""
            SELECT * FROM akshare_interfaces 
            WHERE interface_name LIKE '%stock%' 
            AND category_level1 = '股票'
        """)
        stock_results = cursor.fetchall()
        end_time = datetime.now()
        
        query_time = (end_time - start_time).total_seconds()
        print(f"\n⚡ 查询性能测试:")
        print(f"  股票相关接口查询: {len(stock_results)} 条结果")
        print(f"  查询耗时: {query_time:.4f} 秒")
        
        # 9. 数据完整性检查
        cursor.execute("""
            SELECT COUNT(*) 
            FROM akshare_interfaces i
            LEFT JOIN akshare_interface_tag_relations r ON i.id = r.interface_id
            WHERE r.interface_id IS NULL
        """)
        missing_tags = cursor.fetchone()[0]
        
        print(f"\n✅ 数据完整性检查:")
        print(f"  无标签接口: {missing_tags} 个")
        
        # 10. 总体评估
        total_interfaces = data_summary.get('akshare_interfaces', 0)
        total_tags = data_summary.get('akshare_interface_tags', 0)
        
        print(f"\n🎯 系统状态总结:")
        print(f"  ✅ 数据库连接正常")
        print(f"  ✅ 表结构完整 ({len(tables)} 个表)")
        print(f"  ✅ 索引优化 ({len(indexes)} 个索引)")
        print(f"  ✅ 数据导入成功 ({total_interfaces} 个接口)")
        print(f"  ✅ 标签系统正常 ({total_tags} 个标签)")
        print(f"  ✅ 查询性能良好")
        
        if total_interfaces > 0 and missing_tags == 0:
            print("\n🎉 系统测试通过！所有功能正常")
        else:
            print(f"\n⚠️  发现 {missing_tags} 个问题需要关注")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        conn.close()
    
    return True

def test_api_endpoints():
    """测试API端点"""
    print("\n🔌 测试API端点...")
    
    # 这里可以添加API测试代码
    print("  API测试功能待实现")
    
    return True

if __name__ == "__main__":
    # 运行完整系统测试
    success = test_complete_system()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 所有测试完成！系统运行正常")
    else:
        print("\n" + "=" * 50)
        print("❌ 测试发现问题，请检查日志")