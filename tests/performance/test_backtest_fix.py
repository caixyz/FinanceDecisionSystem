"""
测试回测功能修复
"""
import requests
import json

def test_backtest_api():
    """测试回测API"""
    print("=" * 50)
    print("测试回测功能修复")
    print("=" * 50)
    
    try:
        url = "http://127.0.0.1:5000/api/backtest/run"
        
        # 测试数据
        test_data = {
            "symbol": "000001",
            "strategy": "MA策略",
            "days": 90,
            "initial_capital": 1000000
        }
        
        print(f"正在测试回测API...")
        print(f"请求数据: {test_data}")
        
        response = requests.post(
            url, 
            json=test_data, 
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ JSON解析成功")
                print(f"返回代码: {result.get('code')}")
                print(f"返回消息: {result.get('message')}")
                
                if result.get('code') == 200:
                    data = result.get('data', {})
                    print(f"\n回测结果:")
                    print(f"  策略名称: {data.get('strategy_name')}")
                    print(f"  股票代码: {data.get('symbol')}")
                    print(f"  开始日期: {data.get('start_date')}")
                    print(f"  结束日期: {data.get('end_date')}")
                    print(f"  初始资金: {data.get('initial_capital'):,}")
                    print(f"  最终价值: {data.get('final_value'):,.2f}")
                    print(f"  总收益率: {data.get('total_return'):.2%}")
                    print(f"  年化收益率: {data.get('annual_return'):.2%}")
                    print(f"  最大回撤: {data.get('max_drawdown'):.2%}")
                    print(f"  夏普比率: {data.get('sharpe_ratio'):.2f}")
                    print(f"  交易次数: {data.get('trade_count')}")
                    print(f"  胜率: {data.get('win_rate'):.1%}")
                    
                    # 检查equity_curve是否正确序列化
                    equity_curve = data.get('equity_curve', {})
                    if equity_curve:
                        print(f"  净值曲线数据点: {len(equity_curve)}个")
                        # 显示前几个数据点
                        sample_points = list(equity_curve.items())[:3]
                        print(f"  样本数据点: {sample_points}")
                    
                    print("✅ 回测功能修复成功！")
                    return True
                else:
                    print(f"❌ API返回错误: {result.get('message')}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"响应内容: {response.text[:500]}...")
                return False
        else:
            print(f"❌ HTTP请求失败")
            print(f"响应内容: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    success = test_backtest_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 回测功能修复验证成功！")
        print("现在可以正常使用策略回测功能了")
    else:
        print("💥 回测功能仍有问题，需要进一步调试")
    print("=" * 50)