import sqlite3
import os

def check_database():
    # 检查数据库文件是否存在
    db_path = 'data/finance_data.db'
    print('检查数据库:', db_path)
    
    if not os.path.exists(db_path):
        print('数据库文件不存在，需要创建')
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        print('数据库中的表:')
        for table in tables:
            print(f'  - {table}')
        
        # 检查stock_info表
        if 'stock_info' in tables:
            cursor.execute("SELECT COUNT(*) FROM stock_info WHERE symbol='000001'")
            count = cursor.fetchone()[0]
            print(f'\nstock_info表中000001的记录数: {count}')
            
            if count > 0:
                cursor.execute("SELECT symbol, name, industry, close, pe_ratio, pb_ratio FROM stock_info WHERE symbol='000001'")
                row = cursor.fetchone()
                print(f'股票信息: {row}')
            else:
                print('000001在stock_info表中无数据')
        else:
            print('\n⚠️ stock_info表不存在')
        
        # 检查stock_daily表
        if 'stock_daily' in tables:
            cursor.execute("SELECT COUNT(*) FROM stock_daily WHERE symbol='000001'")
            count = cursor.fetchone()[0]
            print(f'stock_daily表中000001的记录数: {count}')
            
            if count > 0:
                cursor.execute("SELECT date, open, high, low, close, volume FROM stock_daily WHERE symbol='000001' ORDER BY date DESC LIMIT 3")
                rows = cursor.fetchall()
                print('最新3条数据:')
                for row in rows:
                    print(f'  {row}')
            else:
                print('000001在stock_daily表中无数据')
        else:
            print('\n⚠️ stock_daily表不存在')
            
        # 检查technical_indicators表
        if 'technical_indicators' in tables:
            cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE symbol='000001'")
            count = cursor.fetchone()[0]
            print(f'technical_indicators表中000001的记录数: {count}')
            
            if count > 0:
                cursor.execute("SELECT date, sma_5, sma_20, rsi, macd FROM technical_indicators WHERE symbol='000001' ORDER BY date DESC LIMIT 3")
                rows = cursor.fetchall()
                print('最新3条技术指标:')
                for row in rows:
                    print(f'  {row}')
            else:
                print('000001在technical_indicators表中无数据')
        else:
            print('\n⚠️ technical_indicators表不存在')
            
        conn.close()
        
    except Exception as e:
        print(f'数据库检查失败: {e}')

if __name__ == '__main__':
    check_database()