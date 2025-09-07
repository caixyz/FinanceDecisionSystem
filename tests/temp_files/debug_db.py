import sqlite3
import os

# 检查数据库文件是否存在
if os.path.exists('finance_data.db'):
    print("数据库文件存在")
else:
    print("数据库文件不存在")
    exit(1)

# 连接数据库
conn = sqlite3.connect('finance_data.db')
cursor = conn.cursor()

# 检查所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\n数据库表:")
for table in tables:
    print(f"  {table[0]}")

# 如果stock_info表存在，检查其结构
if any('stock_info' in str(table) for table in tables):
    print("\nstock_info表结构:")
    cursor.execute("PRAGMA table_info(stock_info)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]}: {col[2]}")
    
    print("\n前5条股票数据:")
    cursor.execute("SELECT symbol, name, industry FROM stock_info LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]} - {row[1]}: {row[2]}")
else:
    print("\nstock_info表不存在")

conn.close()