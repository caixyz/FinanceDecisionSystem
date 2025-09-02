"""
Web应用主入口
基于Flask的金融分析系统API
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from pathlib import Path

from utils.config import config
from utils.logger import logger
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer
from core.backtest import BacktestEngine, MAStrategy, RSIStrategy
from core.visualization import ChartPlotter, ReportGenerator
from core.storage import db_manager, cache_manager
from strategies.example_strategies import MACDStrategy, BollingerBandsStrategy, CompositeStrategy


app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# 全局实例
data_source = DataSource()
analyzer = TechnicalAnalyzer()
backtest_engine = BacktestEngine()
chart_plotter = ChartPlotter()
report_generator = ReportGenerator()


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/stocks/list')
def get_stock_list():
    """获取股票列表"""
    try:
        # 先从缓存获取
        cache_key = "stock_list"
        stock_list = cache_manager.get(cache_key)
        
        if stock_list is None:
            df = data_source.get_stock_list()
            stock_list = df[['代码', '名称', '最新价', '涨跌幅', '市值']].head(100).to_dict('records')
            cache_manager.set(cache_key, stock_list, ttl=3600)  # 缓存1小时
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stock_list
        })
        
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/data')
def get_stock_data(symbol):
    """获取股票历史数据"""
    try:
        days = request.args.get('days', 90, type=int)
        period = request.args.get('period', 'daily')
        
        # 检查缓存
        cache_key = f"stock_data_{symbol}_{days}_{period}"
        stock_data = cache_manager.get(cache_key)
        
        if stock_data is None:
            df = data_source.get_stock_data(symbol, period=period, days=days)
            stock_data = df.reset_index().to_dict('records')
            cache_manager.set(cache_key, stock_data, ttl=300)  # 缓存5分钟
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stock_data
        })
        
    except Exception as e:
        logger.error(f"获取股票数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/analysis')
def analyze_stock(symbol):
    """分析股票"""
    try:
        days = request.args.get('days', 90, type=int)
        
        # 获取股票数据
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 技术分析
        analysis = analyzer.analyze_stock(symbol, df)
        
        return jsonify({
            'code': 200,
            'message': '分析完成',
            'data': analysis
        })
        
    except Exception as e:
        logger.error(f"股票分析失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'分析失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/chart')
def get_stock_chart(symbol):
    """生成股票图表"""
    try:
        days = request.args.get('days', 90, type=int)
        chart_type = request.args.get('type', 'candlestick')
        
        # 获取数据
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 添加技术指标
        df = analyzer.calculate_all_indicators(df)
        
        # 生成图表
        if chart_type == 'candlestick':
            chart_path = chart_plotter.plot_candlestick_chart(df, symbol)
        elif chart_type == 'indicators':
            chart_path = chart_plotter.plot_technical_indicators(df, symbol)
        else:
            return jsonify({
                'code': 400,
                'message': '不支持的图表类型'
            }), 400
        
        # 返回图表路径
        return jsonify({
            'code': 200,
            'message': '图表生成成功',
            'data': {
                'chart_url': f'/static/charts/{os.path.basename(chart_path)}'
            }
        })
        
    except Exception as e:
        logger.error(f"生成图表失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'生成图表失败: {str(e)}'
        }), 500


@app.route('/api/backtest/run', methods=['POST'])
def run_backtest():
    """运行回测"""
    try:
        data = request.json
        symbol = data.get('symbol')
        strategy_name = data.get('strategy', 'MA策略')
        days = data.get('days', 252)
        initial_capital = data.get('initial_capital', 1000000)
        
        if not symbol:
            return jsonify({
                'code': 400,
                'message': '请提供股票代码'
            }), 400
        
        # 获取股票数据
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 选择策略
        strategy_map = {
            'MA策略': MAStrategy(),
            'RSI策略': RSIStrategy(),
            'MACD策略': MACDStrategy(),
            '布林带策略': BollingerBandsStrategy(),
            '综合策略': CompositeStrategy()
        }
        
        strategy = strategy_map.get(strategy_name, MAStrategy())
        
        # 运行回测
        backtest_engine.initial_capital = initial_capital
        results = backtest_engine.run_backtest(strategy, df, symbol)
        
        # 保存结果
        backtest_id = backtest_engine.save_backtest_result(results)
        
        # 准备返回数据（去除不能序列化的对象）
        response_data = {
            'backtest_id': backtest_id,
            'strategy_name': results['strategy_name'],
            'symbol': results['symbol'],
            'start_date': results['start_date'],
            'end_date': results['end_date'],
            'initial_capital': results['initial_capital'],
            'final_value': results['final_value'],
            'total_return': results['total_return'],
            'annual_return': results['annual_return'],
            'max_drawdown': results['max_drawdown'],
            'sharpe_ratio': results['sharpe_ratio'],
            'trade_count': results['trade_count'],
            'win_rate': results['win_rate']
        }
        
        # 处理equity_curve的序列化问题
        if 'equity_curve' in results and hasattr(results['equity_curve'], 'index'):
            # 将Timestamp索引转换为字符串
            equity_curve = results['equity_curve']
            equity_dict = {}
            for date, value in equity_curve.items():
                # 将Timestamp转换为字符串
                date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                equity_dict[date_str] = float(value) if pd.notna(value) else 0.0
            response_data['equity_curve'] = equity_dict
        else:
            response_data['equity_curve'] = {}
        
        return jsonify({
            'code': 200,
            'message': '回测完成',
            'data': response_data
        })
        
    except Exception as e:
        logger.error(f"回测运行失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'回测失败: {str(e)}'
        }), 500


@app.route('/api/strategies/list')
def get_strategies():
    """获取可用策略列表"""
    strategies = [
        {
            'name': 'MA策略',
            'description': '基于移动平均线的金叉死叉策略'
        },
        {
            'name': 'RSI策略', 
            'description': '基于RSI超买超卖的策略'
        },
        {
            'name': 'MACD策略',
            'description': '基于MACD指标的策略'
        },
        {
            'name': '布林带策略',
            'description': '基于布林带的均值回归策略'
        },
        {
            'name': '综合策略',
            'description': '多指标综合判断策略'
        }
    ]
    
    return jsonify({
        'code': 200,
        'message': '获取成功',
        'data': strategies
    })


@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """生成分析报告"""
    try:
        data = request.json
        symbol = data.get('symbol')
        days = data.get('days', 90)
        
        if not symbol:
            return jsonify({
                'code': 400,
                'message': '请提供股票代码'
            }), 400
        
        # 获取数据和分析
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 添加技术指标
        df = analyzer.calculate_all_indicators(df)
        
        # 分析股票
        analysis = analyzer.analyze_stock(symbol, df)
        
        # 生成报告
        report_path = report_generator.generate_stock_report(symbol, df, analysis)
        
        return jsonify({
            'code': 200,
            'message': '报告生成成功',
            'data': {
                'report_url': f'/static/reports/{os.path.basename(report_path)}'
            }
        })
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'生成报告失败: {str(e)}'
        }), 500


@app.route('/api/market/sentiment')
def get_market_sentiment():
    """获取市场情绪"""
    try:
        # 检查缓存
        cache_key = "market_sentiment"
        sentiment = cache_manager.get(cache_key)
        
        if sentiment is None:
            sentiment = data_source.get_market_sentiment()
            cache_manager.set(cache_key, sentiment, ttl=600)  # 缓存10分钟
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': sentiment
        })
        
    except Exception as e:
        logger.error(f"获取市场情绪失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


# 静态文件服务
@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件服务"""
    return send_from_directory('static', filename)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'code': 404,
        'message': '页面不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'code': 500,
        'message': '服务器内部错误'
    }), 500


if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('static/charts', exist_ok=True)
    os.makedirs('static/reports', exist_ok=True)
    
    # 获取配置
    web_config = config.get_web_config()
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', True)
    
    logger.info(f"启动Web服务: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)