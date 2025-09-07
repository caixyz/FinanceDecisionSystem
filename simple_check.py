import sqlite3
import os

# 检查数据库文件
print("检查数据库文件...")
if os.path.exists('finance_data.db'):
    print("✅ finance_data.db 存在")
else:
    print("❌ finance_data.db 不存在")
    exit()

# 连接数据库
conn = sqlite3.connect('finance_data.db')
cursor = conn.cursor()

# 查询所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\n数据库中的表:")
for table in tables:
    print(f"- {table[0]}")

# 检查是否有股票相关的表
stock_tables = [t[0] for t in tables if 'stock' in str(t[0]).lower()]
if stock_tables:
    print(f"\n📊 股票相关表: {stock_tables}")
else:
    print("\n❌ 没有找到股票相关的表")

conn.close()