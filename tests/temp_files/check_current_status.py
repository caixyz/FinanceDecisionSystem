import sqlite3
import os

def check_database():
    db_path = 'data/finance_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_info'")
        if not cursor.fetchone():
            print("stock_info表不存在")
            conn.close()
            return
        
        # 获取股票总数
        cursor.execute('SELECT COUNT(*) FROM stock_info')
        count = cursor.fetchone()[0]
        print(f'数据库中股票总数: {count}')
        
        # 获取有行业信息的股票数
        cursor.execute("SELECT COUNT(*) FROM stock_info WHERE industry IS NOT NULL AND industry != ''")
        industry_count = cursor.fetchone()[0]
        print(f'有行业信息的股票数: {industry_count}')
        
        # 获取前10条数据
        cursor.execute('SELECT symbol, name, industry FROM stock_info LIMIT 10')
        results = cursor.fetchall()
        print('\n前10条数据:')
        for row in results:
            print(f'{row[0]} - {row[1]} - 行业: {row[2]}')
        
        # 显示行业分布
        cursor.execute('SELECT industry, COUNT(*) FROM stock_info WHERE industry IS NOT NULL AND industry != "" GROUP BY industry')
        industries = cursor.fetchall()
        if industries:
            print('\n行业分布:')
            for industry, cnt in industries:
                print(f'{industry}: {cnt}只股票')
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database()