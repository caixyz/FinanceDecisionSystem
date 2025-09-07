import requests
import json

def check_stock_data():
    session = requests.Session()
    
    # 登录
    login_response = session.post('http://localhost:5000/api/auth/login', 
                                  json={'username': 'admin', 'password': 'admin123'})
    
    # 测试几个股票的数据
    symbols = ['000001', '000002', '000858', '601398']
    
    for symbol in symbols:
        try:
            response = session.get(f'http://localhost:5000/api/company/{symbol}/data')
            print(f"=== {symbol} ===")
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                company = data['data']['company']
                
                print(f"股票代码: {company.get('symbol', '无')}")
                print(f"股票名称: {company.get('name', '无')}")
                print(f"所属行业: {company.get('industry', '未知')}")
                print(f"最新股价: {company.get('current_price', '无')}")
                print(f"市盈率: {company.get('pe_ratio', '无')}")
                print(f"市净率: {company.get('pb_ratio', '无')}")
                print(f"总市值: {company.get('market_cap', '无')}")
                print(f"财务数据: {company.get('financial_data', {})}")
            else:
                print("获取失败")
            print()
            
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    check_stock_data()