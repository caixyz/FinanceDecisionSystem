"""
数据可视化模块
提供股票数据和技术指标的图表绘制功能
"""
# 解决多线程环境下的matplotlib问题
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免tkinter线程问题

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from utils.logger import logger
import warnings
import threading
import gc
warnings.filterwarnings('ignore')

# 配置中文字体
def setup_chinese_fonts():
    """设置中文字体"""
    try:
        # 尝试多种中文字体
        chinese_fonts = [
            'SimHei',          # 黑体
            'Microsoft YaHei', # 微软雅黑
            'DejaVu Sans',     # 备选字体
            'Arial Unicode MS', # Mac/Linux备选
            'WenQuanYi Micro Hei', # Linux中文字体
            'Noto Sans CJK SC'  # Google字体
        ]
        
        # 寻找可用的中文字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        selected_font = None
        
        for font in chinese_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            plt.rcParams['font.sans-serif'] = [selected_font]
            plt.rcParams['axes.unicode_minus'] = False
            # 设置线程安全的参数
            plt.rcParams['figure.max_open_warning'] = 0  # 禁用打开图表过多的警告
            logger.info(f"已设置中文字体: {selected_font}")
        else:
            # 如果没有找到中文字体，使用默认设置但警告用户
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['figure.max_open_warning'] = 0
            logger.warning("未找到合适的中文字体，可能会出现中文显示问题")
            
    except Exception as e:
        logger.error(f"字体设置失败: {e}")
        # 使用最基本的设置
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.max_open_warning'] = 0

# 线程锁确保线程安全
_plot_lock = threading.Lock()

# 初始化中文字体
setup_chinese_fonts()

class ChartPlotter:
    """图表绘制器"""
    
    def __init__(self, style: str = "seaborn-v0_8"):
        """
        初始化图表绘制器
        
        Args:
            style: matplotlib样式
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
            
        self.colors = {
            'up': '#FF4444',      # 上涨红色
            'down': '#00AA00',    # 下跌绿色
            'ma5': '#FF6600',     # MA5橙色
            'ma10': '#9900FF',    # MA10紫色
            'ma20': '#0066FF',    # MA20蓝色
            'volume': '#808080'   # 成交量灰色
        }
        
        logger.info("图表绘制器初始化完成")
    
    def safe_plot(self, plot_func):
        """安全绘图装饰器，解决多线程问题"""
        def wrapper(*args, **kwargs):
            with _plot_lock:  # 线程锁
                try:
                    # 确保使用非交互式后端
                    current_backend = matplotlib.get_backend()
                    if current_backend != 'Agg':
                        matplotlib.use('Agg')
                    
                    result = plot_func(*args, **kwargs)
                    
                    # 强制清理内存
                    plt.close('all')
                    gc.collect()
                    
                    return result
                    
                except Exception as e:
                    # 出错时清理所有图表
                    try:
                        plt.close('all')
                        gc.collect()
                    except:
                        pass
                    raise e
                    
        return wrapper
    
    def plot_candlestick_chart(self, 
                              data: pd.DataFrame, 
                              symbol: str,
                              title: str = None,
                              save_path: str = None,
                              show_volume: bool = True,
                              show_ma: bool = True,
                              ma_periods: List[int] = [5, 10, 20],
                              mark_extremes: str = 'global') -> str:
        """
        绘制K线图
        
        Args:
            data: 包含OHLC数据的DataFrame
            symbol: 股票代码
            title: 图表标题
            save_path: 保存路径
            show_volume: 是否显示成交量
            show_ma: 是否显示移动平均线
            ma_periods: 移动平均线周期
            mark_extremes: 标注模式 ('global': 全局最高低点, 'local': 局部最高低点, 'none': 不标注)
        """
        return self.safe_plot(self._plot_candlestick_chart)(data, symbol, title, save_path, show_volume, show_ma, ma_periods, mark_extremes)
    
    def _plot_candlestick_chart(self, data, symbol, title, save_path, show_volume, show_ma, ma_periods, mark_extremes='global'):
        """内部K线图绘制方法"""
        try:
            # 确保中文字体设置
            setup_chinese_fonts()
            
            if title is None:
                title = f"{symbol} K线图"
            
            # 创建子图
            if show_volume:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), 
                                             gridspec_kw={'height_ratios': [3, 1]})
            else:
                fig, ax1 = plt.subplots(1, 1, figsize=(15, 8))
            
            # 准备数据
            df = data.copy()
            if 'date' not in df.columns and df.index.name != 'date':
                df = df.reset_index()
            
            dates = pd.to_datetime(df.index if 'date' not in df.columns else df['date'])
            
            # 绘制K线图
            for i in range(len(df)):
                date = dates[i]
                open_price = df['open'].iloc[i]
                high_price = df['high'].iloc[i]
                low_price = df['low'].iloc[i]
                close_price = df['close'].iloc[i]
                
                # 判断涨跌
                color = self.colors['up'] if close_price >= open_price else self.colors['down']
                
                # 绘制影线
                ax1.plot([date, date], [low_price, high_price], color='black', linewidth=1)
                
                # 绘制实体
                body_height = abs(close_price - open_price)
                bottom = min(open_price, close_price)
                
                if close_price >= open_price:
                    # 阳线
                    ax1.bar(date, body_height, bottom=bottom, color=color, alpha=0.8, width=0.6)
                else:
                    # 阴线
                    ax1.bar(date, body_height, bottom=bottom, color=color, alpha=0.8, width=0.6)
            
            # 标注最高低点
            if mark_extremes == 'global':
                logger.info(f"开始添加全局最高低点标注")
                self._mark_global_extremes(ax1, df, dates)
                logger.info(f"全局标注添加完成")
            elif mark_extremes == 'local':
                logger.info(f"开始添加局部最高低点标注")
                self._mark_local_extremes(ax1, df, dates)
                logger.info(f"局部标注添加完成")
            else:
                logger.info(f"跳过标注，模式: {mark_extremes}")
            
            # 绘制移动平均线
            if show_ma:
                for period in ma_periods:
                    if f'MA_{period}' in df.columns:
                        ax1.plot(dates, df[f'MA_{period}'], 
                               label=f'MA{period}', linewidth=2)
                    else:
                        ma_data = df['close'].rolling(window=period).mean()
                        ax1.plot(dates, ma_data, 
                               label=f'MA{period}', linewidth=2)
            
            # 设置主图
            ax1.set_title(title, fontsize=16, fontweight='bold', fontproperties='SimHei')
            ax1.set_ylabel('价格', fontsize=12, fontproperties='SimHei')
            ax1.grid(True, alpha=0.3)
            if show_ma:
                ax1.legend(prop={'family': 'SimHei'})
            
            # 格式化x轴
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax1.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            
            # 绘制成交量
            if show_volume and 'volume' in df.columns:
                colors = [self.colors['up'] if df['close'].iloc[i] >= df['open'].iloc[i] 
                         else self.colors['down'] for i in range(len(df))]
                
                ax2.bar(dates, df['volume'], color=colors, alpha=0.6)
                ax2.set_ylabel('成交量', fontsize=12, fontproperties='SimHei')
                ax2.set_xlabel('日期', fontsize=12, fontproperties='SimHei')
                ax2.grid(True, alpha=0.3)
                
                # 格式化x轴
                ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax2.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # 保存图表
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"K线图已保存: {save_path}")
                return save_path
            else:
                # 确保目录存在
                import os
                os.makedirs('static/charts', exist_ok=True)
                save_path = f"static/charts/candlestick_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"K线图已保存: {save_path}")
                return save_path
                
        except Exception as e:
            logger.error(f"绘制K线图失败: {e}")
            raise
    
    def _mark_global_extremes(self, ax, df, dates):
        """标注全局最高低点"""
        logger.info(f"进入全局标注方法，数据行数: {len(df)}")
        
        # 计算最高点和最低点的位置索引
        high_idx = df['high'].idxmax()
        low_idx = df['low'].idxmin()
        
        # 转换为位置索引
        high_pos = df.index.get_loc(high_idx)
        low_pos = df.index.get_loc(low_idx)
        
        high_date = dates[high_pos]
        high_price = df['high'].iloc[high_pos]
        low_date = dates[low_pos]
        low_price = df['low'].iloc[low_pos]
        
        logger.info(f"最高点: {high_date}, 价格: {high_price:.2f}")
        logger.info(f"最低点: {low_date}, 价格: {low_price:.2f}")
        
        price_range = high_price - low_price
        
        # 标注最高点
        high_annotation = ax.annotate(f'全局最高\n{high_price:.2f}', 
                   xy=(high_date, high_price), 
                   xytext=(high_date, high_price + price_range * 0.08),
                   fontsize=10, ha='center', va='bottom',
                   fontproperties='SimHei',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
        
        # 标注最低点
        low_annotation = ax.annotate(f'全局最低\n{low_price:.2f}', 
                   xy=(low_date, low_price), 
                   xytext=(low_date, low_price - price_range * 0.08),
                   fontsize=10, ha='center', va='top',
                   fontproperties='SimHei',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8),
                   arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
        
        logger.info(f"标注对象创建成功: 最高点={type(high_annotation)}, 最低点={type(low_annotation)}")
    
    def _mark_local_extremes(self, ax, df, dates, window=5, min_points=3):
        """标注局部最高低点"""
        from scipy.signal import argrelextrema
        
        # 找局部最大值和最小值
        highs = df['high'].values
        lows = df['low'].values
        
        # 局部最高点
        high_peaks = argrelextrema(highs, np.greater, order=window)[0]
        # 局部最低点
        low_peaks = argrelextrema(lows, np.less, order=window)[0]
        
        # 过滤少于min_points个的极值点
        if len(high_peaks) > min_points:
            # 按高度排序，只显示最显著的几个
            high_values = [(i, highs[i]) for i in high_peaks]
            high_values.sort(key=lambda x: x[1], reverse=True)
            high_peaks = [x[0] for x in high_values[:min_points]]
        
        if len(low_peaks) > min_points:
            # 按高度排序，只显示最显著的几个
            low_values = [(i, lows[i]) for i in low_peaks]
            low_values.sort(key=lambda x: x[1])
            low_peaks = [x[0] for x in low_values[:min_points]]
        
        price_range = df['high'].max() - df['low'].min()
        
        # 标注局部最高点
        for i, peak_idx in enumerate(high_peaks):
            peak_date = dates[peak_idx]
            peak_price = highs[peak_idx]
            
            ax.annotate(f'局部高点\n{peak_price:.2f}', 
                       xy=(peak_date, peak_price), 
                       xytext=(peak_date, peak_price + price_range * 0.05),
                       fontsize=9, ha='center', va='bottom',
                       fontproperties='SimHei',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='orange', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='orange', lw=1))
        
        # 标注局部最低点
        for i, peak_idx in enumerate(low_peaks):
            peak_date = dates[peak_idx]
            peak_price = lows[peak_idx]
            
            ax.annotate(f'局部低点\n{peak_price:.2f}', 
                       xy=(peak_date, peak_price), 
                       xytext=(peak_date, peak_price - price_range * 0.05),
                       fontsize=9, ha='center', va='top',
                       fontproperties='SimHei',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='cyan', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='cyan', lw=1))
        
    def plot_technical_indicators(self, 
                                data: pd.DataFrame, 
                                symbol: str,
                                indicators: List[str] = ['RSI', 'MACD', 'KDJ'],
                                save_path: str = None) -> str:
        """
        绘制技术指标图
        
        Args:
            data: 包含技术指标的DataFrame
            symbol: 股票代码
            indicators: 要绘制的指标列表
            save_path: 保存路径
        """
        return self.safe_plot(self._plot_technical_indicators)(data, symbol, indicators, save_path)
    
    def _plot_technical_indicators(self, data, symbol, indicators, save_path):
        """内部技术指标图绘制方法"""
        try:
            # 确保中文字体设置
            setup_chinese_fonts()
            # 创建子图
            fig, axes = plt.subplots(len(indicators), 1, figsize=(15, 4*len(indicators)))
            
            if len(indicators) == 1:
                axes = [axes]
            
            df = data.copy()
            dates = df.index if isinstance(df.index, pd.DatetimeIndex) else pd.to_datetime(df.index)
            
            for i, indicator in enumerate(indicators):
                ax = axes[i]
                
                if indicator == 'RSI':
                    if 'RSI' in df.columns:
                        ax.plot(dates, df['RSI'], label='RSI', linewidth=2)
                        ax.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='超买线')
                        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='超卖线')
                        ax.set_ylim(0, 100)
                        ax.set_ylabel('RSI', fontsize=12, fontproperties='SimHei')
                        ax.set_title(f'{symbol} - RSI指标', fontsize=14, fontproperties='SimHei')
                
                elif indicator == 'MACD':
                    if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                        ax.plot(dates, df['MACD'], label='MACD', linewidth=2)
                        ax.plot(dates, df['MACD_Signal'], label='Signal', linewidth=2)
                        
                        # MACD柱状图
                        colors = ['red' if x > 0 else 'green' for x in df['MACD_Histogram']]
                        ax.bar(dates, df['MACD_Histogram'], color=colors, alpha=0.6, label='Histogram')
                        
                        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
                        ax.set_ylabel('MACD', fontsize=12, fontproperties='SimHei')
                        ax.set_title(f'{symbol} - MACD指标', fontsize=14, fontproperties='SimHei')
                
                elif indicator == 'KDJ':
                    if all(col in df.columns for col in ['KDJ_K', 'KDJ_D', 'KDJ_J']):
                        ax.plot(dates, df['KDJ_K'], label='K', linewidth=2)
                        ax.plot(dates, df['KDJ_D'], label='D', linewidth=2)
                        ax.plot(dates, df['KDJ_J'], label='J', linewidth=2)
                        
                        ax.axhline(y=80, color='red', linestyle='--', alpha=0.7)
                        ax.axhline(y=20, color='green', linestyle='--', alpha=0.7)
                        ax.set_ylim(0, 100)
                        ax.set_ylabel('KDJ', fontsize=12, fontproperties='SimHei')
                        ax.set_title(f'{symbol} - KDJ指标', fontsize=14, fontproperties='SimHei')
                
                ax.grid(True, alpha=0.3)
                ax.legend()
                
                # 格式化x轴
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # 保存图表
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"技术指标图已保存: {save_path}")
                return save_path
            else:
                # 确保目录存在
                import os
                os.makedirs('static/charts', exist_ok=True)
                save_path = f"static/charts/indicators_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"技术指标图已保存: {save_path}")
                return save_path
                
        except Exception as e:
            logger.error(f"绘制技术指标图失败: {e}")
            raise
    
    def plot_interactive_chart(self, 
                             data: pd.DataFrame, 
                             symbol: str,
                             title: str = None) -> go.Figure:
        """
        创建交互式图表（使用Plotly）
        
        Args:
            data: 股票数据
            symbol: 股票代码
            title: 图表标题
        """
        try:
            if title is None:
                title = f"{symbol} 交互式K线图"
            
            df = data.copy()
            
            # 创建子图
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=('K线图', '成交量', '技术指标'),
                row_heights=[0.6, 0.2, 0.2]
            )
            
            # K线图
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='K线'
                ),
                row=1, col=1
            )
            
            # 添加移动平均线
            if 'MA_5' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['MA_5'], name='MA5', line=dict(color='orange')),
                    row=1, col=1
                )
            if 'MA_20' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['MA_20'], name='MA20', line=dict(color='blue')),
                    row=1, col=1
                )
            
            # 成交量
            if 'volume' in df.columns:
                colors = ['red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'green' 
                         for i in range(len(df))]
                
                fig.add_trace(
                    go.Bar(x=df.index, y=df['volume'], name='成交量', marker_color=colors),
                    row=2, col=1
                )
            
            # RSI指标
            if 'RSI' in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
                    row=3, col=1
                )
                
                # RSI超买超卖线
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            # 更新布局
            fig.update_layout(
                title=title,
                xaxis_rangeslider_visible=False,
                height=800,
                showlegend=True
            )
            
            logger.info(f"交互式图表创建完成: {symbol}")
            return fig
            
        except Exception as e:
            logger.error(f"创建交互式图表失败: {e}")
            raise
    
    def plot_correlation_heatmap(self, 
                               data: Dict[str, pd.DataFrame], 
                               save_path: str = None) -> str:
        """
        绘制相关性热力图
        
        Args:
            data: 多只股票的收盘价数据 {symbol: DataFrame}
            save_path: 保存路径
        """
        try:
            # 合并数据
            price_data = pd.DataFrame()
            for symbol, df in data.items():
                price_data[symbol] = df['close']
            
            # 计算相关性矩阵
            correlation_matrix = price_data.corr()
            
            # 创建热力图
            plt.figure(figsize=(12, 10))
            sns.heatmap(correlation_matrix, 
                       annot=True, 
                       cmap='coolwarm', 
                       center=0,
                       square=True,
                       fmt='.2f')
            
            plt.title('股票相关性热力图', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # 保存图表
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"相关性热力图已保存: {save_path}")
                return save_path
            else:
                save_path = f"static/charts/correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"相关性热力图已保存: {save_path}")
                return save_path
                
        except Exception as e:
            logger.error(f"绘制相关性热力图失败: {e}")
            raise
        finally:
            plt.close()
    
    def plot_portfolio_performance(self, 
                                 portfolio_value: pd.Series,
                                 benchmark_value: pd.Series = None,
                                 title: str = "投资组合表现",
                                 save_path: str = None) -> str:
        """
        绘制投资组合表现图
        
        Args:
            portfolio_value: 投资组合价值序列
            benchmark_value: 基准价值序列
            title: 图表标题
            save_path: 保存路径
        """
        try:
            plt.figure(figsize=(15, 8))
            
            # 绘制投资组合曲线
            plt.plot(portfolio_value.index, portfolio_value.values, 
                    label='投资组合', linewidth=2, color='blue')
            
            # 绘制基准曲线
            if benchmark_value is not None:
                plt.plot(benchmark_value.index, benchmark_value.values, 
                        label='基准', linewidth=2, color='red', alpha=0.7)
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('价值', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 格式化x轴
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 保存图表
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"投资组合表现图已保存: {save_path}")
                return save_path
            else:
                save_path = f"static/charts/portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"投资组合表现图已保存: {save_path}")
                return save_path
                
        except Exception as e:
            logger.error(f"绘制投资组合表现图失败: {e}")
            raise
        finally:
            plt.close()


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.plotter = ChartPlotter()
        logger.info("报告生成器初始化完成")
    
    def generate_stock_report(self, 
                            symbol: str, 
                            data: pd.DataFrame, 
                            analysis: Dict,
                            output_dir: str = "static/reports") -> str:
        """
        生成股票分析报告
        
        Args:
            symbol: 股票代码
            data: 股票数据
            analysis: 分析结果
            output_dir: 输出目录
        """
        try:
            from pathlib import Path
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成图表
            candlestick_path = self.plotter.plot_candlestick_chart(
                data, symbol, save_path=str(output_dir / f"{symbol}_candlestick.png")
            )
            
            indicators_path = self.plotter.plot_technical_indicators(
                data, symbol, save_path=str(output_dir / f"{symbol}_indicators.png")
            )
            
            # 生成HTML报告
            html_content = self._generate_html_report(symbol, analysis, candlestick_path, indicators_path)
            
            report_path = output_dir / f"{symbol}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"股票分析报告已生成: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"生成股票分析报告失败: {e}")
            raise
    
    def _generate_html_report(self, symbol: str, analysis: Dict, chart1_path: str, chart2_path: str) -> str:
        """生成HTML格式的分析报告"""
        
        # 将文件系统路径转换为Web URL路径
        import os
        chart1_url = f"/static/reports/{os.path.basename(chart1_path)}"
        chart2_url = f"/static/reports/{os.path.basename(chart2_path)}"
        
        signal_text = {
            1: "买入信号",
            -1: "卖出信号",
            0: "持有/观望"
        }
        
        strength_text = {
            2: "强烈",
            1: "一般", 
            0: "无",
            -1: "一般",
            -2: "强烈"
        }
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{symbol} 股票分析报告</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #dee2e6; border-radius: 8px; }}
                .indicator {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 5px; }}
                .chart {{ text-align: center; margin: 20px 0; }}
                .signal-buy {{ color: #28a745; font-weight: bold; }}
                .signal-sell {{ color: #dc3545; font-weight: bold; }}
                .signal-hold {{ color: #6c757d; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{symbol} 股票分析报告</h1>
                <p><strong>生成时间:</strong> {analysis.get('analysis_date', '')}</p>
                <p><strong>当前价格:</strong> {analysis.get('current_price', 0):.2f}</p>
                <p><strong>趋势判断:</strong> {analysis.get('trend', '')}</p>
            </div>
            
            <div class="section">
                <h2>技术指标</h2>
                <div class="indicator">RSI: {analysis.get('technical_indicators', {}).get('RSI', 0):.2f}</div>
                <div class="indicator">MACD: {analysis.get('technical_indicators', {}).get('MACD', 0):.4f}</div>
                <div class="indicator">MA5: {analysis.get('technical_indicators', {}).get('MA_5', 0):.2f}</div>
                <div class="indicator">MA20: {analysis.get('technical_indicators', {}).get('MA_20', 0):.2f}</div>
            </div>
            
            <div class="section">
                <h2>交易信号</h2>
                <p><strong>信号:</strong> <span class="signal-buy">{signal_text.get(analysis.get('trading_signal', {}).get('signal', 0))}</span></p>
                <p><strong>强度:</strong> {strength_text.get(analysis.get('trading_signal', {}).get('strength', 0))}</p>
            </div>
            
            <div class="section">
                <h2>风险评估</h2>
                <p><strong>风险等级:</strong> {analysis.get('risk_assessment', {}).get('risk_level', '未知')}</p>
                <p><strong>年化波动率:</strong> {analysis.get('risk_assessment', {}).get('volatility', 0):.2%}</p>
                <p><strong>最大回撤:</strong> {analysis.get('risk_assessment', {}).get('max_drawdown', 0):.2%}</p>
            </div>
            
            <div class="chart">
                <h2>K线图</h2>
                <img src="{chart1_url}" alt="K线图" style="max-width: 100%; height: auto;">
            </div>
            
            <div class="chart">
                <h2>技术指标图</h2>
                <img src="{chart2_url}" alt="技术指标图" style="max-width: 100%; height: auto;">
            </div>
        </body>
        </html>
        """
        
        return html_template