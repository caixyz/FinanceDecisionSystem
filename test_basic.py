#!/usr/bin/env python3
"""
简单测试脚本
测试核心功能是否正常工作
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试模块导入"""
    print("🔧 测试模块导入...")
    
    try:
        from utils.config import config
        print("✅ 配置模块导入成功")
        
        from utils.logger import logger
        print("✅ 日志模块导入成功")
        
        from core.data_source import DataSource
        print("✅ 数据源模块导入成功")
        
        from core.analyzer import TechnicalAnalyzer
        print("✅ 分析模块导入成功")
        
        from core.backtest import BacktestEngine, MAStrategy
        print("✅ 回测模块导入成功")
        
        from core.storage import DatabaseManager, CacheManager
        print("✅ 存储模块导入成功")
        
        from core.visualization import ChartPlotter
        print("✅ 可视化模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        # 测试配置
        from utils.config import config
        db_config = config.get_database_config()
        print(f"✅ 配置读取成功: {db_config.get('type', 'unknown')}")
        
        # 测试数据库
        from core.storage import DatabaseManager
        db = DatabaseManager()
        print("✅ 数据库初始化成功")
        
        # 测试分析器
        from core.analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        print("✅ 技术分析器初始化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_data_generation():
    """测试数据生成"""
    print("\n📊 测试数据生成...")
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # 生成测试数据
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        price = 100
        prices = []
        for i in range(100):
            price += np.random.normal(0, 2)
            prices.append(max(price, 10))  # 确保价格为正
        
        test_data = pd.DataFrame({
            'open': [p * (1 + np.random.uniform(-0.02, 0.02)) for p in prices],
            'high': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
            'low': [p * (1 + np.random.uniform(-0.03, 0)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000000, 10000000) for _ in range(100)],
            'turnover': [np.random.uniform(10000000, 100000000) for _ in range(100)]
        }, index=dates)
        
        print(f"✅ 测试数据生成成功: {len(test_data)} 条记录")
        
        # 测试技术分析
        from core.analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        
        # 计算技术指标
        enhanced_data = analyzer.calculate_all_indicators(test_data)
        print(f"✅ 技术指标计算成功: {len(enhanced_data.columns)} 个指标")
        
        # 测试信号生成
        signals = analyzer.get_trading_signals(enhanced_data)
        buy_signals = (signals['Signal'] == 1).sum()
        sell_signals = (signals['Signal'] == -1).sum()
        print(f"✅ 交易信号生成成功: 买入信号 {buy_signals} 个, 卖出信号 {sell_signals} 个")
        
        return True, test_data
        
    except Exception as e:
        print(f"❌ 数据生成测试失败: {e}")
        return False, None

def test_backtest():
    """测试回测功能"""
    print("\n🔄 测试回测功能...")
    
    try:
        success, test_data = test_data_generation()
        if not success:
            return False
        
        from core.backtest import BacktestEngine, MAStrategy
        
        # 初始化回测引擎
        engine = BacktestEngine(initial_capital=1000000)
        strategy = MAStrategy(5, 20)
        
        # 运行回测
        results = engine.run_backtest(strategy, test_data, "TEST")
        
        print(f"✅ 回测完成")
        print(f"   初始资金: {results['initial_capital']:,.0f}")
        print(f"   最终价值: {results['final_value']:,.0f}")
        print(f"   总收益率: {results['total_return']:+.2%}")
        print(f"   交易次数: {results['trade_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 回测测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 金融决策系统 - 功能测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        return
    
    # 测试基本功能
    if not test_basic_functionality():
        return
        
    # 测试数据生成
    if not test_data_generation()[0]:
        return
        
    # 测试回测
    if not test_backtest():
        return
    
    print("\n" + "=" * 50)
    print("✅ 所有测试通过！系统基本功能正常")
    print("=" * 50)
    print("\n📝 接下来您可以:")
    print("1. 运行演示脚本: python demo.py")
    print("2. 启动Web服务: python app.py")
    print("3. 查看README.md了解更多功能")

if __name__ == "__main__":
    main()