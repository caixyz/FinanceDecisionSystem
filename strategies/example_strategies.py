"""
示例交易策略
"""
from core.backtest import Strategy
import pandas as pd
import numpy as np


class MACDStrategy(Strategy):
    """MACD策略"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, name: str = "MACD策略"):
        super().__init__(name)
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成MACD交叉信号"""
        df = self.analyzer.add_macd(data.copy(), self.fast, self.slow, self.signal)
        
        signals = pd.Series(0, index=df.index)
        
        # MACD金叉买入
        golden_cross = (df['MACD'] > df['MACD_Signal']) & \
                      (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
        signals[golden_cross] = 1
        
        # MACD死叉卖出
        death_cross = (df['MACD'] < df['MACD_Signal']) & \
                     (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
        signals[death_cross] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio) -> int:
        """计算仓位大小"""
        if signal == 1:  # 买入信号
            target_value = portfolio.cash * 0.6  # 使用60%资金
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100
            return quantity
        elif signal == -1:  # 卖出信号
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0


class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self, period: int = 20, std_dev: float = 2, name: str = "布林带策略"):
        super().__init__(name)
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成布林带信号"""
        df = self.analyzer.add_bollinger_bands(data.copy(), self.period, self.std_dev)
        
        signals = pd.Series(0, index=df.index)
        
        # 价格跌破下轨买入
        buy_signal = (df['close'] < df['BB_Lower']) & (df['close'].shift(1) >= df['BB_Lower'].shift(1))
        signals[buy_signal] = 1
        
        # 价格突破上轨卖出
        sell_signal = (df['close'] > df['BB_Upper']) & (df['close'].shift(1) <= df['BB_Upper'].shift(1))
        signals[sell_signal] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio) -> int:
        """计算仓位大小"""
        if signal == 1:  # 买入信号
            target_value = portfolio.cash * 0.4  # 使用40%资金
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100
            return quantity
        elif signal == -1:  # 卖出信号
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0


class CompositeStrategy(Strategy):
    """综合策略（多指标组合）"""
    
    def __init__(self, name: str = "综合策略"):
        super().__init__(name)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成综合信号"""
        df = self.analyzer.calculate_all_indicators(data.copy())
        
        signals = pd.Series(0, index=df.index)
        
        # 多条件买入信号
        buy_conditions = (
            (df['RSI'] < 30) &  # RSI超卖
            (df['close'] < df['BB_Lower']) &  # 价格低于布林带下轨
            (df['MACD'] > df['MACD_Signal']) &  # MACD金叉
            (df['MA_5'] > df['MA_20'])  # 短期均线在长期均线之上
        )
        
        # 多条件卖出信号
        sell_conditions = (
            (df['RSI'] > 70) |  # RSI超买
            (df['close'] > df['BB_Upper']) |  # 价格高于布林带上轨
            (df['MACD'] < df['MACD_Signal'])  # MACD死叉
        )
        
        signals[buy_conditions] = 1
        signals[sell_conditions] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio) -> int:
        """计算仓位大小"""
        if signal == 1:  # 买入信号
            target_value = portfolio.cash * 0.8  # 使用80%资金
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100
            return quantity
        elif signal == -1:  # 卖出信号
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0


class MomentumStrategy(Strategy):
    """动量策略"""
    
    def __init__(self, lookback_period: int = 20, threshold: float = 0.05, name: str = "动量策略"):
        super().__init__(name)
        self.lookback_period = lookback_period
        self.threshold = threshold
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成动量信号"""
        df = data.copy()
        
        # 计算动量指标
        momentum = df['close'].pct_change(self.lookback_period)
        
        signals = pd.Series(0, index=df.index)
        
        # 正动量买入
        buy_signal = momentum > self.threshold
        signals[buy_signal] = 1
        
        # 负动量卖出
        sell_signal = momentum < -self.threshold
        signals[sell_signal] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio) -> int:
        """计算仓位大小"""
        if signal == 1:  # 买入信号
            target_value = portfolio.cash * 0.5  # 使用50%资金
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100
            return quantity
        elif signal == -1:  # 卖出信号
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0