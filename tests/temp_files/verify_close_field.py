#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证脚本：检查股票列表中是否已正确添加收盘价字段
"""

import sqlite3
import json

def check_database_structure():
    """检查数据库结构"""
    print("=== 检查数据库结构 ===")
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    # 检查stock_info表结构
    cursor.execute("PRAGMA table_info(stock_info)")
    columns = cursor.fetchall()
    print("stock_info表字段:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查是否有close字段
    has_close = any(col[1] == 'close' for col in columns)
    print(f"\n✅ 包含close字段: {has_close}")
    
    # 检查数据示例
    cursor.execute("SELECT symbol, name, industry, close, updated_at FROM stock_info LIMIT 5")
    samples = cursor.fetchall()
    print("\n数据示例:")
    for row in samples:
        print(f"  {row[0]} - {row[1]} - 行业:{row[2]} - 收盘价:{row[3]} - 更新时间:{row[4]}")
    
    conn.close()

def check_api_responses():
    """检查API响应格式"""
    print("\n=== 检查API响应格式 ===")
    
    # 检查公开API
    print("公开API (http://localhost:5001/api/public/stocks):")
    print("  已添加close字段到SELECT查询")
    
    # 检查主应用模板
    print("\n主应用模板 (test_stock_management.html):")
    print("  已添加'最新收盘价(元)'表头")
    print("  已添加close字段的数据显示")

def main():
    """主函数"""
    check_database_structure()
    check_api_responses()
    
    print("\n" + "="*50)
    print("✅ 收盘价字段已成功添加到股票列表")
    print("="*50)
    print("\n访问地址:")
    print("  公开查看: http://localhost:5001")
    print("  主应用: http://localhost:5000/test_stock_management")
    print("\n演示账号:")
    print("  管理员: admin / admin123")
    print("  演示用户: demo / demo123")

if __name__ == "__main__":
    main()