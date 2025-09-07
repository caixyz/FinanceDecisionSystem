import sqlite3

# 连接到数据库
conn = sqlite3.connect('data/finance_data.db')
cursor = conn.cursor()

# 检查总股票数
cursor.execute('SELECT COUNT(*) FROM stock_info')
total = cursor.fetchone()[0]
print(f'总股票数: {total}')

# 检查有行业信息的股票数
cursor.execute("SELECT COUNT(*) FROM stock_info WHERE industry IS NOT NULL AND industry != ''")
with_industry = cursor.fetchone()[0]
print(f'有行业信息的股票数: {with_industry}')

# 查看前5条数据
cursor.execute('SELECT symbol, name, industry FROM stock_info LIMIT 5')
rows = cursor.fetchall()
print('前5条股票数据:')
for row in rows:
    print(f'  {row[0]} - {row[1]} - 行业: {row[2]}')

conn.close()