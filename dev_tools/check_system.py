#!/usr/bin/env python3
"""系统健康检查工具"""

import sqlite3
import os
import sys
from pathlib import Path

def check_database():
    """检查数据库状态"""
    db_path = Path('data/finance_data.db')
    
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("📊 数据库表:", tables)
        
        # 检查股票信息表
        cursor.execute("SELECT COUNT(*) FROM stock_info")
        stock_count = cursor.fetchone()[0]
        print(f"📈 股票总数: {stock_count}")
        
        # 检查日线数据表
        cursor.execute("SELECT COUNT(*) FROM stock_daily")
        daily_count = cursor.fetchone()[0]
        print(f"📅 日线数据条数: {daily_count}")
        
        # 检查数据完整性
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT s.symbol),
                COUNT(DISTINCT d.symbol),
                MIN(d.date),
                MAX(d.date)
            FROM stock_info s
            LEFT JOIN stock_daily d ON s.symbol = d.symbol
        """)
        result = cursor.fetchone()
        print(f"✅ 数据完整性:")
        print(f"   - 有信息的股票: {result[0]}")
        print(f"   - 有数据的股票: {result[1]}")
        print(f"   - 最早数据日期: {result[2]}")
        print(f"   - 最新数据日期: {result[3]}")
        
        # 检查长期分析可行性
        print("🎯 长期分析可行性:")
        print("   - 当前数据时间跨度: 1年 (2024-2025)")
        print("   - ⚠️  需要至少10年历史数据")
        print("   - 💡 解决方案: 使用演示数据或扩展历史数据收集")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def check_long_term_analyzer():
    """检查长期分析器"""
    analyzer_path = Path('dev_tools/long_term_survival_analysis.py')
    
    if not analyzer_path.exists():
        print("❌ 长期分析器不存在")
        return False
    
    try:
        # 检查文件语法
        with open(analyzer_path, 'r', encoding='utf-8') as f:
            code = f.read()
            compile(code, str(analyzer_path), 'exec')
        
        print("✅ 长期分析器语法检查通过")
        
        # 运行测试
        import subprocess
        result = subprocess.run([sys.executable, str(analyzer_path)], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ 长期分析器运行成功")
            print("📊 输出:", result.stdout.strip())
        else:
            print("❌ 长期分析器运行失败")
            print("💥 错误:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 长期分析器检查失败: {e}")
        return False

def check_demo_analyzer():
    """检查演示分析器"""
    demo_path = Path('dev_tools/demo_long_term_analysis.py')
    
    if not demo_path.exists():
        print("❌ 演示分析器不存在")
        return False
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ 演示分析器运行成功")
            
            # 检查输出文件
            output_files = [
                'data/demo_long_term_stocks.csv',
                'data/demo_analysis_report.txt',
                'data/demo_investment_strategies.txt'
            ]
            
            for file_path in output_files:
                if Path(file_path).exists():
                    print(f"✅ {file_path} 已生成")
                else:
                    print(f"❌ {file_path} 未找到")
                    
        else:
            print("❌ 演示分析器运行失败")
            print("💥 错误:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 演示分析器检查失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🚀 开始系统健康检查...")
    print("=" * 50)
    
    # 检查数据库
    print("\n1. 数据库检查")
    db_ok = check_database()
    
    # 检查长期分析器
    print("\n2. 长期分析器检查")
    analyzer_ok = check_long_term_analyzer()
    
    # 检查演示分析器
    print("\n3. 演示分析器检查")
    demo_ok = check_demo_analyzer()
    
    print("\n" + "=" * 50)
    print("📋 检查结果总结:")
    print(f"   数据库: {'✅' if db_ok else '❌'}")
    print(f"   长期分析器: {'✅' if analyzer_ok else '❌'}")
    print(f"   演示分析器: {'✅' if demo_ok else '❌'}")
    
    if all([db_ok, analyzer_ok, demo_ok]):
        print("🎉 系统状态良好！")
    else:
        print("⚠️  发现一些问题，请查看详情")

if __name__ == "__main__":
    main()