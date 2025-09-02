"""
技术分析模块
实现常用的技术指标计算
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from utils.logger import logger
import warnings
warnings.filterwarnings('ignore')

class TechnicalAnalyzer:
    """技术分析器"""
    
    def __init__(self):
        logger.info("技术分析器初始化完成")
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        try:
            df = data.copy()
            
            # 移动平均线
            df = self.add_moving_averages(df)
            
            # MACD
            df = self.add_macd(df)
            
            # RSI
            df = self.add_rsi(df)
            
            # 布林带
            df = self.add_bollinger_bands(df)
            
            # KDJ
            df = self.add_kdj(df)
            
            # ATR
            df = self.add_atr(df)
            
            # 成交量指标
            df = self.add_volume_indicators(df)
            
            logger.info("所有技术指标计算完成")
            return df
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            raise
    
    def add_moving_averages(self, data: pd.DataFrame, periods: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """添加移动平均线"""
        df = data.copy()
        
        for period in periods:
            # 简单移动平均线
            df[f'MA_{period}'] = df['close'].rolling(window=period).mean()
            
            # 指数移动平均线
            df[f'EMA_{period}'] = df['close'].ewm(span=period).mean()
        
        logger.debug(f"移动平均线计算完成: {periods}")
        return df
    
    def add_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """添加MACD指标"""
        df = data.copy()
        
        # 计算快慢EMA
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        
        # MACD线
        df['MACD'] = ema_fast - ema_slow
        
        # 信号线
        df['MACD_Signal'] = df['MACD'].ewm(span=signal).mean()
        
        # MACD柱状图
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        logger.debug("MACD指标计算完成")
        return df
    
    def add_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """添加RSI指标"""
        df = data.copy()
        
        # 价格变化
        delta = df['close'].diff()
        
        # 上涨和下跌
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # 平均收益和损失
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        # RS和RSI
        rs = avg_gains / avg_losses
        df['RSI'] = 100 - (100 / (1 + rs))
        
        logger.debug(f"RSI指标计算完成: period={period}")
        return df
    
    def add_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """添加布林带"""
        df = data.copy()
        
        # 中轨（移动平均线）
        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        
        # 标准差
        std = df['close'].rolling(window=period).std()
        
        # 上轨和下轨
        df['BB_Upper'] = df['BB_Middle'] + (std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (std * std_dev)
        
        # 布林带宽度
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        
        # %B指标
        df['BB_Percent'] = (df['close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        logger.debug(f"布林带指标计算完成: period={period}, std_dev={std_dev}")
        return df
    
    def add_kdj(self, data: pd.DataFrame, k_period: int = 9, d_period: int = 3, j_period: int = 3) -> pd.DataFrame:
        """添加KDJ指标"""
        df = data.copy()
        
        # 最高价和最低价
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        
        # RSV
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        
        # K值
        df['KDJ_K'] = rsv.ewm(com=d_period-1).mean()
        
        # D值
        df['KDJ_D'] = df['KDJ_K'].ewm(com=j_period-1).mean()
        
        # J值
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        logger.debug(f"KDJ指标计算完成: K={k_period}, D={d_period}, J={j_period}")
        return df
    
    def add_atr(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """添加ATR（平均真实波幅）"""
        df = data.copy()
        
        # 真实波幅
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # ATR
        df['ATR'] = true_range.rolling(window=period).mean()
        
        logger.debug(f"ATR指标计算完成: period={period}")
        return df
    
    def add_volume_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """添加成交量指标"""
        df = data.copy()
        
        # 成交量移动平均
        df['Volume_MA_5'] = df['volume'].rolling(window=5).mean()
        df['Volume_MA_10'] = df['volume'].rolling(window=10).mean()
        
        # 相对成交量
        df['Volume_Ratio'] = df['volume'] / df['Volume_MA_10']
        
        # OBV (On Balance Volume)
        price_change = df['close'].diff()
        df['OBV'] = (df['volume'] * np.sign(price_change)).cumsum()
        
        # 资金流量指标 MFI
        if 'turnover' in df.columns:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            money_flow = typical_price * df['volume']
            
            positive_flow = money_flow.where(typical_price > typical_price.shift(), 0).rolling(14).sum()
            negative_flow = money_flow.where(typical_price < typical_price.shift(), 0).rolling(14).sum()
            
            mfi_ratio = positive_flow / negative_flow
            df['MFI'] = 100 - (100 / (1 + mfi_ratio))
        
        logger.debug("成交量指标计算完成")
        return df
    
    def calculate_support_resistance(self, data: pd.DataFrame, window: int = 20) -> Tuple[List[float], List[float]]:
        """计算支撑位和阻力位"""
        try:
            df = data.copy()
            
            # 计算局部高点和低点
            highs = df['high'].rolling(window=window, center=True).max()
            lows = df['low'].rolling(window=window, center=True).min()
            
            # 找到支撑位（局部低点）
            support_levels = []
            for i in range(window, len(df) - window):
                if df['low'].iloc[i] == lows.iloc[i]:
                    support_levels.append(df['low'].iloc[i])
            
            # 找到阻力位（局部高点）
            resistance_levels = []
            for i in range(window, len(df) - window):
                if df['high'].iloc[i] == highs.iloc[i]:
                    resistance_levels.append(df['high'].iloc[i])
            
            # 去重并排序
            support_levels = sorted(list(set(support_levels)))
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
            
            logger.debug(f"支撑阻力位计算完成: 支撑位{len(support_levels)}个, 阻力位{len(resistance_levels)}个")
            return support_levels, resistance_levels
            
        except Exception as e:
            logger.error(f"计算支撑阻力位失败: {e}")
            return [], []
    
    def calculate_trend(self, data: pd.DataFrame, period: int = 20) -> str:
        """判断趋势方向"""
        try:
            df = data.copy()
            
            # 使用移动平均线判断趋势
            if f'MA_{period}' not in df.columns:
                df[f'MA_{period}'] = df['close'].rolling(window=period).mean()
            
            current_price = df['close'].iloc[-1]
            current_ma = df[f'MA_{period}'].iloc[-1]
            previous_ma = df[f'MA_{period}'].iloc[-5]  # 5天前的MA
            
            # 判断趋势
            if current_price > current_ma and current_ma > previous_ma:
                trend = "上升趋势"
            elif current_price < current_ma and current_ma < previous_ma:
                trend = "下降趋势"
            else:
                trend = "震荡趋势"
            
            logger.debug(f"趋势判断完成: {trend}")
            return trend
            
        except Exception as e:
            logger.error(f"趋势判断失败: {e}")
            return "未知趋势"
    
    def get_trading_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        try:
            df = data.copy()
            
            # 确保有必要的指标
            if 'RSI' not in df.columns:
                df = self.add_rsi(df)
            if 'MACD' not in df.columns:
                df = self.add_macd(df)
            if 'MA_5' not in df.columns:
                df = self.add_moving_averages(df, [5, 20])
            
            # 初始化信号列
            df['Signal'] = 0
            df['Signal_Strength'] = 0
            df['Signal_Reason'] = ''
            
            # RSI超买超卖信号
            rsi_oversold = df['RSI'] < 30
            rsi_overbought = df['RSI'] > 70
            
            # MACD金叉死叉信号
            macd_golden_cross = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
            macd_death_cross = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
            
            # 均线多头排列
            ma_bullish = df['MA_5'] > df['MA_20']
            ma_bearish = df['MA_5'] < df['MA_20']
            
            # 综合信号
            buy_signals = rsi_oversold | (macd_golden_cross & ma_bullish)
            sell_signals = rsi_overbought | (macd_death_cross & ma_bearish)
            
            df.loc[buy_signals, 'Signal'] = 1
            df.loc[sell_signals, 'Signal'] = -1
            
            # 信号强度
            df.loc[buy_signals, 'Signal_Strength'] = 1
            df.loc[sell_signals, 'Signal_Strength'] = -1
            
            # 强烈信号（多个指标同时发出信号）
            strong_buy = rsi_oversold & macd_golden_cross & ma_bullish
            strong_sell = rsi_overbought & macd_death_cross & ma_bearish
            
            df.loc[strong_buy, 'Signal_Strength'] = 2
            df.loc[strong_sell, 'Signal_Strength'] = -2
            
            logger.debug("交易信号生成完成")
            return df
            
        except Exception as e:
            logger.error(f"生成交易信号失败: {e}")
            return data
    
    def analyze_stock(self, symbol: str, data: pd.DataFrame) -> Dict[str, any]:
        """综合分析股票"""
        try:
            # 计算所有技术指标
            df = self.calculate_all_indicators(data)
            
            # 生成交易信号
            df = self.get_trading_signals(df)
            
            # 计算支撑阻力位
            support_levels, resistance_levels = self.calculate_support_resistance(df)
            
            # 判断趋势
            trend = self.calculate_trend(df)
            
            # 最新数据
            latest = df.iloc[-1]
            
            # 生成分析报告
            analysis = {
                'symbol': symbol,
                'analysis_date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
                'current_price': latest['close'],
                'trend': trend,
                'technical_indicators': {
                    'RSI': latest.get('RSI', 0),
                    'MACD': latest.get('MACD', 0),
                    'MACD_Signal': latest.get('MACD_Signal', 0),
                    'MA_5': latest.get('MA_5', 0),
                    'MA_20': latest.get('MA_20', 0),
                    'BB_Upper': latest.get('BB_Upper', 0),
                    'BB_Lower': latest.get('BB_Lower', 0),
                },
                'trading_signal': {
                    'signal': int(latest.get('Signal', 0)),
                    'strength': int(latest.get('Signal_Strength', 0)),
                    'reason': latest.get('Signal_Reason', '')
                },
                'support_levels': support_levels[-5:] if support_levels else [],  # 最近5个支撑位
                'resistance_levels': resistance_levels[:5] if resistance_levels else [],  # 最近5个阻力位
                'risk_assessment': self._assess_risk(df.tail(20))  # 基于最近20天数据评估风险
            }
            
            logger.info(f"股票 {symbol} 综合分析完成")
            return analysis
            
        except Exception as e:
            logger.error(f"股票综合分析失败: {e}")
            raise
    
    def _assess_risk(self, data: pd.DataFrame) -> Dict[str, any]:
        """风险评估"""
        try:
            # 计算波动率
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)  # 年化波动率
            
            # VaR计算（5%分位数）
            var_5 = returns.quantile(0.05)
            
            # 最大回撤
            cumulative = (1 + returns).cumprod()
            rolling_max = cumulative.expanding().max()
            drawdown = (cumulative - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # 风险等级
            if volatility < 0.2:
                risk_level = "低风险"
            elif volatility < 0.4:
                risk_level = "中等风险"
            else:
                risk_level = "高风险"
            
            return {
                'volatility': volatility,
                'var_5_percent': var_5,
                'max_drawdown': max_drawdown,
                'risk_level': risk_level
            }
            
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return {
                'volatility': 0,
                'var_5_percent': 0,
                'max_drawdown': 0,
                'risk_level': "未知"
            }