#!/usr/bin/env python3
"""
金融决策系统使用示例
演示系统的主要功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer
from core.backtest import BacktestEngine, MAStrategy, RSIStrategy
from core.visualization import ChartPlotter, ReportGenerator
from strategies.example_strategies import MACDStrategy, CompositeStrategy
from utils.logger import logger


def demo_data_fetching():
    """演示数据获取功能"""
    print("=" * 60)
    print("📊 数据获取演示")
    print("=" * 60)
    
    data_source = DataSource()
    
    # 获取股票列表
    print("1. 获取A股股票列表...")
    try:
        stock_list = data_source.get_stock_list()
        print(f"   成功获取 {len(stock_list)} 只股票")
        print(f"   前5只股票: {stock_list.head()['名称'].tolist()}")
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
    
    # 获取具体股票数据
    print("\n2. 获取平安银行(000001)历史数据...")
    try:
        stock_data = data_source.get_stock_data("000001", days=30)
        print(f"   成功获取 {len(stock_data)} 条记录")
        print(f"   最新价格: {stock_data['close'].iloc[-1]:.2f}")
        print(f"   期间涨跌: {((stock_data['close'].iloc[-1] / stock_data['close'].iloc[0] - 1) * 100):+.2f}%")
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
    
    print()


def demo_technical_analysis():
    """演示技术分析功能"""
    print("=" * 60)
    print("📈 技术分析演示") 
    print("=" * 60)
    
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    
    try:
        # 获取数据
        print("1. 获取贵州茅台(600519)数据...")
        stock_data = data_source.get_stock_data("600519", days=60)
        print(f"   获取了 {len(stock_data)} 条数据")
        
        # 技术分析
        print("\n2. 进行技术分析...")
        analysis = analyzer.analyze_stock("600519", stock_data)
        
        print(f"   股票代码: {analysis['symbol']}")
        print(f"   当前价格: {analysis['current_price']:.2f}")
        print(f"   趋势判断: {analysis['trend']}")
        
        # 技术指标
        indicators = analysis['technical_indicators']
        print(f"   RSI指标: {indicators['RSI']:.2f}")
        print(f"   MACD: {indicators['MACD']:.4f}")
        print(f"   MA5: {indicators['MA_5']:.2f}")
        print(f"   MA20: {indicators['MA_20']:.2f}")
        
        # 交易信号
        signal = analysis['trading_signal']
        signal_text = {1: "买入", -1: "卖出", 0: "持有"}
        print(f"   交易信号: {signal_text.get(signal['signal'], '未知')}")
        print(f"   信号强度: {signal['strength']}")
        
        # 风险评估
        risk = analysis['risk_assessment']
        print(f"   风险等级: {risk['risk_level']}")
        print(f"   年化波动率: {risk['volatility']:.2%}")
        
    except Exception as e:
        print(f"   ❌ 分析失败: {e}")
    
    print()


def demo_strategy_backtest():
    """演示策略回测功能"""
    print("=" * 60)
    print("🔄 策略回测演示")
    print("=" * 60)
    
    data_source = DataSource()
    backtest_engine = BacktestEngine(initial_capital=1000000)
    
    # 测试多个策略
    strategies = [
        ("MA策略", MAStrategy(5, 20)),
        ("RSI策略", RSIStrategy()),
        ("MACD策略", MACDStrategy()),
        ("综合策略", CompositeStrategy())
    ]
    
    symbol = "000002"  # 万科A
    
    try:
        # 获取数据
        print(f"获取 {symbol} 一年历史数据...")
        stock_data = data_source.get_stock_data(symbol, days=252)
        print(f"获取了 {len(stock_data)} 条数据")
        
        print("\n开始回测各种策略:")
        print("-" * 60)
        
        results = {}
        for strategy_name, strategy in strategies:
            print(f"\n🔄 测试策略: {strategy_name}")
            try:
                result = backtest_engine.run_backtest(strategy, stock_data, symbol)
                results[strategy_name] = result
                
                print(f"   总收益率: {result['total_return']:+.2%}")
                print(f"   年化收益: {result['annual_return']:+.2%}")
                print(f"   最大回撤: {result['max_drawdown']:-.2%}")
                print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
                print(f"   交易次数: {result['trade_count']}")
                print(f"   胜率: {result['win_rate']:.1%}")
                
            except Exception as e:
                print(f"   ❌ 回测失败: {e}")
        
        # 策略比较
        if results:
            print("\n" + "=" * 60)
            print("📊 策略比较")
            print("=" * 60)
            print(f"{'策略名称':<12} {'总收益率':<10} {'夏普比率':<8} {'最大回撤':<10} {'胜率':<8}")
            print("-" * 60)
            
            for name, result in results.items():
                print(f"{name:<12} {result['total_return']:>8.2%} "
                      f"{result['sharpe_ratio']:>8.2f} "
                      f"{result['max_drawdown']:>9.2%} "
                      f"{result['win_rate']:>7.1%}")
        
    except Exception as e:
        print(f"❌ 回测演示失败: {e}")
    
    print()


def demo_visualization():
    """演示可视化功能"""
    print("=" * 60)
    print("📊 可视化演示")
    print("=" * 60)
    
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    chart_plotter = ChartPlotter()
    
    try:
        # 获取数据
        print("1. 获取中国平安(601318)数据...")
        stock_data = data_source.get_stock_data("601318", days=90)
        
        # 添加技术指标
        print("2. 计算技术指标...")
        enhanced_data = analyzer.calculate_all_indicators(stock_data)
        
        # 生成K线图
        print("3. 生成K线图...")
        candlestick_path = chart_plotter.plot_candlestick_chart(
            enhanced_data, 
            "601318",
            title="中国平安(601318) - K线图"
        )
        print(f"   K线图已保存: {candlestick_path}")
        
        # 生成技术指标图
        print("4. 生成技术指标图...")
        indicators_path = chart_plotter.plot_technical_indicators(
            enhanced_data,
            "601318",
            indicators=['RSI', 'MACD', 'KDJ']
        )
        print(f"   技术指标图已保存: {indicators_path}")
        
        # 生成分析报告
        print("5. 生成分析报告...")
        report_generator = ReportGenerator()
        analysis = analyzer.analyze_stock("601318", enhanced_data)
        report_path = report_generator.generate_stock_report("601318", enhanced_data, analysis)
        print(f"   分析报告已保存: {report_path}")
        
    except Exception as e:
        print(f"❌ 可视化演示失败: {e}")
    
    print()


def demo_multi_stock_analysis():
    """演示多股票分析"""
    print("=" * 60)
    print("🏢 多股票分析演示")
    print("=" * 60)
    
    data_source = DataSource()
    analyzer = TechnicalAnalyzer()
    
    # 选择几只代表性股票
    symbols = ["000001", "600036", "600519", "000002"]  # 平安银行, 招商银行, 贵州茅台, 万科A
    names = ["平安银行", "招商银行", "贵州茅台", "万科A"]
    
    try:
        print("分析以下股票:")
        for symbol, name in zip(symbols, names):
            print(f"  {symbol} - {name}")
        
        print("\n获取数据并分析...")
        
        analyses = {}
        for i, symbol in enumerate(symbols):
            try:
                print(f"\n📈 分析 {names[i]} ({symbol})")
                
                # 获取数据
                stock_data = data_source.get_stock_data(symbol, days=60)
                analysis = analyzer.analyze_stock(symbol, stock_data)
                analyses[symbol] = analysis
                
                # 显示关键信息
                print(f"   当前价格: {analysis['current_price']:.2f}")
                print(f"   趋势: {analysis['trend']}")
                
                signal = analysis['trading_signal']['signal']
                signal_text = {1: "买入", -1: "卖出", 0: "持有"}
                print(f"   信号: {signal_text.get(signal, '未知')}")
                print(f"   风险等级: {analysis['risk_assessment']['risk_level']}")
                
            except Exception as e:
                print(f"   ❌ 分析 {names[i]} 失败: {e}")
        
        # 汇总比较
        if analyses:
            print("\n" + "=" * 60)
            print("📊 股票对比")
            print("=" * 60)
            print(f"{'股票':<8} {'当前价格':<10} {'趋势':<8} {'信号':<6} {'风险等级':<8}")
            print("-" * 50)
            
            for i, symbol in enumerate(symbols):
                if symbol in analyses:
                    analysis = analyses[symbol]
                    signal = analysis['trading_signal']['signal']
                    signal_text = {1: "买入", -1: "卖出", 0: "持有"}
                    
                    print(f"{names[i]:<8} {analysis['current_price']:>9.2f} "
                          f"{analysis['trend']:<8} "
                          f"{signal_text.get(signal, '未知'):<6} "
                          f"{analysis['risk_assessment']['risk_level']:<8}")
        
    except Exception as e:
        print(f"❌ 多股票分析失败: {e}")
    
    print()


def main():
    """主演示函数"""
    print("🚀 金融决策系统功能演示")
    print("基于 AKShare 的智能股票分析平台")
    print()
    
    try:
        # 演示各个功能模块
        demo_data_fetching()
        demo_technical_analysis()
        demo_strategy_backtest()
        demo_visualization()
        demo_multi_stock_analysis()
        
        print("=" * 60)
        print("✅ 演示完成！")
        print("=" * 60)
        print()
        print("🌐 启动Web服务:")
        print("   python app.py")
        print()
        print("📖 查看更多功能:")
        print("   - 在Web界面进行交互式分析")
        print("   - 使用API接口集成到其他系统")
        print("   - 开发自定义交易策略")
        print("   - 批量处理多只股票")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  演示被用户中断")
    except Exception as e:
        print(f"\n\n❌ 演示过程中出错: {e}")
        logger.error(f"演示失败: {e}")


if __name__ == "__main__":
    main()