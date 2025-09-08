"""
稳定版Web应用主入口
基于Flask的金融分析系统API - 增强稳定性版本
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import gc
import psutil
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

# 内存监控装饰器
def monitor_memory(func):
    """监控内存使用的装饰器"""
    def wrapper(*args, **kwargs):
        # 获取当前内存使用
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            
            # 清理内存
            gc.collect()
            
            # 检查内存使用
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            if memory_used > 100:  # 如果内存增长超过100MB，记录警告
                logger.warning(f"函数 {func.__name__} 内存使用较高: {memory_used:.2f}MB")
            
            logger.info(f"内存使用: {memory_after:.2f}MB (增长: {memory_used:.2f}MB)")
            
            return result
            
        except Exception as e:
            # 出错时强制清理内存
            gc.collect()
            logger.error(f"函数 {func.__name__} 执行失败: {e}")
            raise
            
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/stocks/list')
@monitor_memory
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
@monitor_memory
def get_stock_data(symbol):
    """获取股票历史数据"""
    try:
        days = request.args.get('days', 90, type=int)
        period = request.args.get('period', 'daily')
        
        # 限制天数避免内存过载
        if days > 1000:
            days = 1000
            logger.warning(f"天数限制为1000天，原请求: {request.args.get('days')}")
        
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
@monitor_memory
def analyze_stock(symbol):
    """分析股票"""
    try:
        days = request.args.get('days', 90, type=int)
        
        # 限制天数
        if days > 500:
            days = 500
            logger.warning(f"分析天数限制为500天，原请求: {request.args.get('days')}")
        
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
@monitor_memory
def get_stock_chart(symbol):
    """生成股票图表"""
    try:
        days = request.args.get('days', 90, type=int)
        chart_type = request.args.get('type', 'candlestick')
        
        # 限制天数避免图表过大
        if days > 300:
            days = 300
            logger.warning(f"图表天数限制为300天，原请求: {request.args.get('days')}")
        
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


@app.route('/api/reports/generate', methods=['POST'])
@monitor_memory
def generate_report():
    """生成分析报告 - 增强版本"""
    try:
        data = request.json
        symbol = data.get('symbol')
        days = data.get('days', 90)
        
        if not symbol:
            return jsonify({
                'code': 400,
                'message': '请提供股票代码'
            }), 400
        
        # 限制天数避免生成过大报告
        if days > 200:
            days = 200
            logger.warning(f"报告天数限制为200天，原请求: {data.get('days')}")
        
        # 检查内存使用
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        if memory_usage > 1000:  # 超过1GB内存时拒绝生成报告
            logger.warning(f"内存使用过高 ({memory_usage:.2f}MB)，拒绝生成报告")
            return jsonify({
                'code': 429,
                'message': '系统繁忙，请稍后重试'
            }), 429
        
        # 获取股票数据
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 分段处理以避免内存过载
        logger.info(f"开始生成 {symbol} 的分析报告 (数据量: {len(df)} 条)")
        
        # 添加技术指标
        df = analyzer.calculate_all_indicators(df)
        
        # 分析股票
        analysis = analyzer.analyze_stock(symbol, df)
        
        # 生成报告
        report_path = report_generator.generate_stock_report(symbol, df, analysis)
        
        # 强制清理内存
        del df
        gc.collect()
        
        return jsonify({
            'code': 200,
            'message': '报告生成成功',
            'data': {
                'report_url': f'/static/reports/{os.path.basename(report_path)}'
            }
        })
        
    except Exception as e:
        # 出错时清理内存
        gc.collect()
        logger.error(f"生成报告失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'生成报告失败: {str(e)}'
        }), 500


# 健康检查端点
@app.route('/api/health')
def health_check():
    """系统健康检查"""
    try:
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_percent = process.cpu_percent()
        
        status = "healthy"
        if memory_usage > 1500:  # 超过1.5GB
            status = "warning"
        if memory_usage > 2000:  # 超过2GB
            status = "critical"
            
        return jsonify({
            'status': status,
            'memory_mb': round(memory_usage, 2),
            'cpu_percent': round(cpu_percent, 2),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
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
    debug = web_config.get('debug', False)  # 生产环境关闭debug
    
    logger.info(f"启动稳定版Web服务: http://{host}:{port}")
    logger.info("增强功能: 内存监控、资源限制、健康检查")
    
    app.run(host=host, port=port, debug=debug, threaded=True)