"""
策略回测框架
提供策略开发、回测和性能评估功能
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

from utils.logger import logger
from core.analyzer import TechnicalAnalyzer
from core.storage import db_manager


class Position:
    """持仓信息"""
    
    def __init__(self, symbol: str, quantity: int, entry_price: float, entry_date: datetime):
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.current_price = entry_price
        self.current_date = entry_date
    
    def update_price(self, price: float, date: datetime):
        """更新当前价格"""
        self.current_price = price
        self.current_date = date
    
    @property
    def market_value(self) -> float:
        """市值"""
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return (self.current_price - self.entry_price) * self.quantity
    
    @property
    def unrealized_pnl_pct(self) -> float:
        """未实现盈亏百分比"""
        if self.entry_price == 0:
            return 0
        return (self.current_price - self.entry_price) / self.entry_price


class Trade:
    """交易记录"""
    
    def __init__(self, symbol: str, action: str, quantity: int, price: float, 
                 date: datetime, commission: float = 0):
        self.symbol = symbol
        self.action = action  # 'BUY' or 'SELL'
        self.quantity = quantity
        self.price = price
        self.date = date
        self.commission = commission
        self.amount = quantity * price + commission
    
    def __repr__(self):
        return f"Trade({self.date}, {self.action}, {self.symbol}, {self.quantity}@{self.price})"


class Portfolio:
    """投资组合"""
    
    def __init__(self, initial_capital: float = 1000000, commission_rate: float = 0.0003):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        
        # 历史记录
        self.equity_curve = pd.Series(dtype=float)
        self.daily_returns = pd.Series(dtype=float)
        
    def buy(self, symbol: str, quantity: int, price: float, date: datetime) -> bool:
        """买入股票"""
        try:
            commission = quantity * price * self.commission_rate
            total_cost = quantity * price + commission
            
            if self.cash >= total_cost:
                # 更新持仓
                if symbol in self.positions:
                    # 已有持仓，增加数量
                    old_pos = self.positions[symbol]
                    new_quantity = old_pos.quantity + quantity
                    new_avg_price = (old_pos.quantity * old_pos.entry_price + quantity * price) / new_quantity
                    self.positions[symbol] = Position(symbol, new_quantity, new_avg_price, old_pos.entry_date)
                else:
                    # 新建持仓
                    self.positions[symbol] = Position(symbol, quantity, price, date)
                
                # 更新现金
                self.cash -= total_cost
                
                # 记录交易
                trade = Trade(symbol, 'BUY', quantity, price, date, commission)
                self.trades.append(trade)
                
                logger.debug(f"买入成功: {symbol} {quantity}股 @ {price}")
                return True
            else:
                logger.warning(f"资金不足，无法买入 {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"买入操作失败: {e}")
            return False
    
    def sell(self, symbol: str, quantity: int, price: float, date: datetime) -> bool:
        """卖出股票"""
        try:
            if symbol in self.positions and self.positions[symbol].quantity >= quantity:
                commission = quantity * price * self.commission_rate
                proceeds = quantity * price - commission
                
                # 更新持仓
                pos = self.positions[symbol]
                pos.quantity -= quantity
                
                if pos.quantity == 0:
                    del self.positions[symbol]
                
                # 更新现金
                self.cash += proceeds
                
                # 记录交易
                trade = Trade(symbol, 'SELL', quantity, price, date, commission)
                self.trades.append(trade)
                
                logger.debug(f"卖出成功: {symbol} {quantity}股 @ {price}")
                return True
            else:
                logger.warning(f"持仓不足，无法卖出 {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"卖出操作失败: {e}")
            return False
    
    def update_prices(self, prices: Dict[str, float], date: datetime):
        """更新所有持仓的价格"""
        for symbol, position in self.positions.items():
            if symbol in prices:
                position.update_price(prices[symbol], date)
    
    @property
    def total_value(self) -> float:
        """总资产价值"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    @property
    def total_return(self) -> float:
        """总收益率"""
        if self.initial_capital == 0:
            return 0
        return (self.total_value - self.initial_capital) / self.initial_capital
    
    def get_positions_summary(self) -> pd.DataFrame:
        """获取持仓汇总"""
        if not self.positions:
            return pd.DataFrame()
        
        data = []
        for symbol, pos in self.positions.items():
            data.append({
                'symbol': symbol,
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'market_value': pos.market_value,
                'unrealized_pnl': pos.unrealized_pnl,
                'unrealized_pnl_pct': pos.unrealized_pnl_pct
            })
        
        return pd.DataFrame(data)


class Strategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.analyzer = TechnicalAnalyzer()
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 包含OHLC和技术指标的DataFrame
            
        Returns:
            Series: 交易信号序列，1为买入，-1为卖出，0为持有
        """
        pass
    
    @abstractmethod
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio: Portfolio) -> int:
        """
        计算仓位大小
        
        Args:
            data: 当前市场数据
            signal: 交易信号
            portfolio: 当前投资组合
            
        Returns:
            int: 交易数量
        """
        pass


class MAStrategy(Strategy):
    """移动平均线策略"""
    
    def __init__(self, short_period: int = 5, long_period: int = 20, name: str = "MA策略"):
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成MA交叉信号"""
        df = data.copy()
        
        # 计算移动平均线
        df[f'MA_{self.short_period}'] = df['close'].rolling(self.short_period).mean()
        df[f'MA_{self.long_period}'] = df['close'].rolling(self.long_period).mean()
        
        # 生成信号
        signals = pd.Series(0, index=df.index)
        
        # 金叉买入
        golden_cross = (df[f'MA_{self.short_period}'] > df[f'MA_{self.long_period}']) & \
                      (df[f'MA_{self.short_period}'].shift(1) <= df[f'MA_{self.long_period}'].shift(1))
        signals[golden_cross] = 1
        
        # 死叉卖出
        death_cross = (df[f'MA_{self.short_period}'] < df[f'MA_{self.long_period}']) & \
                     (df[f'MA_{self.short_period}'].shift(1) >= df[f'MA_{self.long_period}'].shift(1))
        signals[death_cross] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio: Portfolio) -> int:
        """计算仓位大小（固定比例）"""
        if signal == 1:  # 买入信号
            # 使用50%资金买入
            target_value = portfolio.cash * 0.5
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100  # 按手数买入
            return quantity
        elif signal == -1:  # 卖出信号
            # 全部卖出
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0


class RSIStrategy(Strategy):
    """RSI策略"""
    
    def __init__(self, rsi_period: int = 14, oversold: float = 30, overbought: float = 70, name: str = "RSI策略"):
        super().__init__(name)
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """生成RSI信号"""
        df = self.analyzer.add_rsi(data.copy(), self.rsi_period)
        
        signals = pd.Series(0, index=df.index)
        
        # RSI超卖买入
        oversold_signal = (df['RSI'] < self.oversold) & (df['RSI'].shift(1) >= self.oversold)
        signals[oversold_signal] = 1
        
        # RSI超买卖出
        overbought_signal = (df['RSI'] > self.overbought) & (df['RSI'].shift(1) <= self.overbought)
        signals[overbought_signal] = -1
        
        return signals
    
    def get_position_size(self, data: pd.DataFrame, signal: int, portfolio: Portfolio) -> int:
        """计算仓位大小"""
        if signal == 1:  # 买入信号
            target_value = portfolio.cash * 0.3  # 使用30%资金
            price = data['close'].iloc[-1]
            quantity = int(target_value / price / 100) * 100
            return quantity
        elif signal == -1:  # 卖出信号
            symbol = data.name if hasattr(data, 'name') else 'default'
            if symbol in portfolio.positions:
                return portfolio.positions[symbol].quantity
        
        return 0


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 1000000, commission_rate: float = 0.0003):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        logger.info("回测引擎初始化完成")
    
    def run_backtest(self, 
                    strategy: Strategy,
                    data: pd.DataFrame,
                    symbol: str,
                    start_date: str = None,
                    end_date: str = None) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            strategy: 交易策略
            data: 股票数据
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        try:
            logger.info(f"开始回测策略: {strategy.name}, 股票: {symbol}")
            
            # 数据预处理
            df = data.copy()
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            # 初始化投资组合
            portfolio = Portfolio(self.initial_capital, self.commission_rate)
            
            # 计算技术指标
            df = strategy.analyzer.calculate_all_indicators(df)
            
            # 生成交易信号
            signals = strategy.generate_signals(df)
            
            # 回测循环
            equity_curve = []
            daily_returns = []
            
            for i, (date, row) in enumerate(df.iterrows()):
                current_price = row['close']
                
                # 更新持仓价格
                portfolio.update_prices({symbol: current_price}, date)
                
                # 记录净值
                portfolio_value = portfolio.total_value
                equity_curve.append(portfolio_value)
                
                # 计算日收益率
                if i > 0:
                    daily_return = (portfolio_value - prev_value) / prev_value
                    daily_returns.append(daily_return)
                else:
                    daily_returns.append(0)
                
                prev_value = portfolio_value
                
                # 执行交易信号
                if i < len(signals) and signals.iloc[i] != 0:
                    signal = signals.iloc[i]
                    quantity = strategy.get_position_size(df.iloc[i:i+1], signal, portfolio)
                    
                    if signal == 1 and quantity > 0:  # 买入
                        portfolio.buy(symbol, quantity, current_price, date)
                    elif signal == -1 and quantity > 0:  # 卖出
                        portfolio.sell(symbol, quantity, current_price, date)
            
            # 计算回测结果
            results = self._calculate_performance_metrics(
                portfolio, equity_curve, daily_returns, df.index, strategy.name, symbol
            )
            
            logger.info(f"回测完成: {strategy.name}")
            return results
            
        except Exception as e:
            logger.error(f"回测运行失败: {e}")
            raise
    
    def _calculate_performance_metrics(self, 
                                     portfolio: Portfolio, 
                                     equity_curve: List[float],
                                     daily_returns: List[float],
                                     dates: pd.DatetimeIndex,
                                     strategy_name: str,
                                     symbol: str) -> Dict[str, Any]:
        """计算回测性能指标"""
        
        # 基本指标
        final_value = portfolio.total_value
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 转换为Series
        equity_series = pd.Series(equity_curve, index=dates)
        returns_series = pd.Series(daily_returns, index=dates)
        
        # 年化收益率
        trading_days = len(equity_curve)
        years = trading_days / 252  # 假设一年252个交易日
        annual_return = (final_value / self.initial_capital) ** (1/years) - 1 if years > 0 else 0
        
        # 最大回撤
        cumulative_max = equity_series.expanding().max()
        drawdown = (equity_series - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        
        # 夏普比率
        if len(returns_series) > 1 and returns_series.std() > 0:
            sharpe_ratio = returns_series.mean() / returns_series.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 交易统计
        trades = portfolio.trades
        total_trades = len(trades)
        
        # 计算盈利交易
        profitable_trades = 0
        if total_trades > 1:
            buy_trades = [t for t in trades if t.action == 'BUY']
            sell_trades = [t for t in trades if t.action == 'SELL']
            
            for sell_trade in sell_trades:
                # 找到对应的买入交易（简化处理，假设FIFO）
                for buy_trade in buy_trades:
                    if buy_trade.symbol == sell_trade.symbol and buy_trade.date <= sell_trade.date:
                        if sell_trade.price > buy_trade.price:
                            profitable_trades += 1
                        break
        
        win_rate = profitable_trades / (total_trades // 2) if total_trades > 1 else 0
        
        results = {
            'strategy_name': strategy_name,
            'symbol': symbol,
            'start_date': dates[0].strftime('%Y-%m-%d'),
            'end_date': dates[-1].strftime('%Y-%m-%d'),
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trade_count': total_trades,
            'win_rate': win_rate,
            'equity_curve': equity_series,
            'daily_returns': returns_series,
            'trades': trades,
            'positions': portfolio.get_positions_summary()
        }
        
        return results
    
    def run_multi_stock_backtest(self, 
                               strategy: Strategy,
                               stock_data: Dict[str, pd.DataFrame],
                               weights: Dict[str, float] = None) -> Dict[str, Any]:
        """
        多股票组合回测
        
        Args:
            strategy: 交易策略
            stock_data: 多只股票数据 {symbol: DataFrame}
            weights: 股票权重 {symbol: weight}
        """
        try:
            logger.info(f"开始多股票回测: {strategy.name}")
            
            if weights is None:
                # 等权重分配
                n_stocks = len(stock_data)
                weights = {symbol: 1.0/n_stocks for symbol in stock_data.keys()}
            
            # 初始化组合投资组合
            portfolio = Portfolio(self.initial_capital, self.commission_rate)
            
            # 获取所有日期的交集
            all_dates = None
            for symbol, data in stock_data.items():
                if all_dates is None:
                    all_dates = set(data.index)
                else:
                    all_dates = all_dates.intersection(set(data.index))
            
            all_dates = sorted(list(all_dates))
            
            # 为每只股票生成信号
            all_signals = {}
            for symbol, data in stock_data.items():
                df = strategy.analyzer.calculate_all_indicators(data)
                all_signals[symbol] = strategy.generate_signals(df)
            
            # 回测循环
            equity_curve = []
            daily_returns = []
            
            for i, date in enumerate(all_dates):
                # 更新所有持仓价格
                current_prices = {}
                for symbol, data in stock_data.items():
                    if date in data.index:
                        current_prices[symbol] = data.loc[date, 'close']
                
                portfolio.update_prices(current_prices, date)
                
                # 记录净值
                portfolio_value = portfolio.total_value
                equity_curve.append(portfolio_value)
                
                # 计算日收益率
                if i > 0:
                    daily_return = (portfolio_value - prev_value) / prev_value
                    daily_returns.append(daily_return)
                else:
                    daily_returns.append(0)
                
                prev_value = portfolio_value
                
                # 执行交易信号
                for symbol in stock_data.keys():
                    if date in all_signals[symbol].index and all_signals[symbol].loc[date] != 0:
                        signal = all_signals[symbol].loc[date]
                        price = current_prices[symbol]
                        
                        # 计算目标仓位
                        target_value = portfolio.total_value * weights[symbol]
                        current_value = portfolio.positions[symbol].market_value if symbol in portfolio.positions else 0
                        
                        if signal == 1:  # 买入信号
                            if current_value < target_value:
                                buy_value = target_value - current_value
                                quantity = int(buy_value / price / 100) * 100
                                if quantity > 0:
                                    portfolio.buy(symbol, quantity, price, date)
                        
                        elif signal == -1:  # 卖出信号
                            if symbol in portfolio.positions:
                                quantity = portfolio.positions[symbol].quantity
                                portfolio.sell(symbol, quantity, price, date)
            
            # 计算回测结果
            results = self._calculate_performance_metrics(
                portfolio, equity_curve, daily_returns, 
                pd.DatetimeIndex(all_dates), strategy.name, "Portfolio"
            )
            
            logger.info(f"多股票回测完成: {strategy.name}")
            return results
            
        except Exception as e:
            logger.error(f"多股票回测失败: {e}")
            raise
    
    def save_backtest_result(self, results: Dict[str, Any]) -> int:
        """保存回测结果到数据库"""
        try:
            return db_manager.save_backtest_result(results)
        except Exception as e:
            logger.error(f"保存回测结果失败: {e}")
            raise