import sqlite3

def check_stock_info_schema():
    """检查stock_info表的结构"""
    try:
        conn = sqlite3.connect('data/finance_data.db')
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("PRAGMA table_info(stock_info)")
        columns = cursor.fetchall()
        
        print("stock_info表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]}) {('PRIMARY KEY' if col[5] == 1 else '')}")
        
        conn.close()
    except Exception as e:
        print(f"检查表结构失败: {e}")

if __name__ == "__main__":
    check_stock_info_schema()