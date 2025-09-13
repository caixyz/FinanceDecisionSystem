#!/usr/bin/env python3
"""
金融决策系统主应用
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from functools import wraps
import os
import sys
import uuid
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import UserManager, login_required
from core.storage import db_manager
from core.data_source import DataSource
from core.analyzer import TechnicalAnalyzer
from core.backtest import BacktestEngine
from core.visualization import ChartPlotter
from utils.logger import logger
from utils.config import config

# 导入股票数据同步管理器
from core.stock_sync import StockDataSynchronizer
from core.sync_progress import sync_progress_manager

# 创建Flask应用
app = Flask(__name__)
app.secret_key = config.get('WEB.secret_key', 'your-secret-key-change-in-production')

# 初始化用户管理器
user_manager = UserManager()
user_manager.init_default_user()

# 设置session密钥
app.secret_key = os.urandom(16)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# 全局实例
user_manager = UserManager()
data_source = DataSource()
analyzer = TechnicalAnalyzer()
backtest_engine = BacktestEngine()
# 注释掉暂时不需要的模块
# chart_plotter = ChartPlotter()
# report_generator = ReportGenerator()


def require_login(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中是否有用户ID
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'code': 401, 'message': '请先登录'}), 401
            return redirect(url_for('login'))
        
        # 验证session token
        session_token = session.get('session_token')
        
        if not session_token or not user_manager.validate_session(session_token):
            session.clear()
            if request.is_json:
                return jsonify({'code': 401, 'message': '登录已过期，请重新登录'}), 401
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


@app.route('/')
def index():
    """主页"""
    # 检查是否登录，如果未登录则跳转到登录页面
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # 已登录用户返回分析界面
    return render_template('index.html')


@app.route('/login')
def login():
    """登录页面"""
    # 如果已登录，跳转到控制台
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """控制台主页（登录后）"""
    return render_template('dashboard.html')


@app.route('/akshare')
@login_required
def akshare_interfaces():
    """AKShare接口独立页面"""
    return render_template('akshare_interfaces.html')


@app.route('/test_stock_management')
@login_required
def test_stock_management():
    """股票数据管理测试页面"""
    return render_template('test_stock_management.html')


@app.route('/debug_index')
@login_required
def debug_index():
    """调试版主页"""
    return render_template('debug_index.html')


@app.route('/value_analysis')
@login_required
def value_analysis():
    """价值投资分析页面"""
    return render_template('value_analysis.html')



# ================================
# 认证API接口
# ================================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API登录接口"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'code': 400,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 用户认证
        user = user_manager.authenticate_user(username, password)
        
        if user:
            # 创建会话
            session_token = user_manager.create_session(user['id'])
            
            if session_token:
                # 设置session
                session['user_id'] = user['id']
                session['session_token'] = session_token
                
                return jsonify({
                    'code': 200,
                    'message': '登录成功',
                    'data': {
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'real_name': user['real_name'],
                            'role': user['role']
                        }
                    }
                })
            else:
                return jsonify({
                    'code': 500,
                    'message': '创建会话失败'
                }), 500
        else:
            return jsonify({
                'code': 401,
                'message': '用户名或密码错误'
            }), 401
            
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'登录失败: {str(e)}'
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """退出登录API"""
    try:
        # 撤销会话
        session_token = session.get('session_token')
        if session_token:
            user_manager.revoke_session(session_token)
        
        # 清除session
        username = session.get('username', '未知用户')
        session.clear()
        
        logger.info(f"用户退出登录: {username}")
        
        return jsonify({
            'code': 200,
            'message': '退出成功'
        })
        
    except Exception as e:
        logger.error(f"退出登录失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'退出失败: {str(e)}'
        }), 500


@app.route('/api/auth/check')
def api_check_auth():
    """检查登录状态API"""
    try:
        if 'user_id' not in session:
            return jsonify({
                'code': 401,
                'message': '未登录'
            }), 401
        
        # 验证session
        session_token = session.get('session_token')
        user_id = user_manager.validate_session(session_token)
        
        if not user_id or user_id != session.get('user_id'):
            session.clear()
            return jsonify({
                'code': 401,
                'message': '登录已过期'
            }), 401
        
        # 获取用户信息
        user = user_manager.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'code': 200,
                'message': '已登录',
                'data': {
                    'user': user
                }
            })
        else:
            session.clear()
            return jsonify({
                'code': 401,
                'message': '用户不存在'
            }), 401
            
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'检查失败: {str(e)}'
        }), 500


@app.route('/api/auth/user')
@login_required
def api_get_user():
    """获取当前用户信息API"""
    try:
        user_id = session.get('user_id')
        user = user_manager.get_user_by_id(user_id)
        
        if user:
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': user
            })
        else:
            return jsonify({
                'code': 404,
                'message': '用户不存在'
            }), 404
            
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


# ================================
# 用户统计信息API
# ================================

@app.route('/api/user/statistics')
@login_required
def api_user_statistics():
    """获取用户统计信息"""
    try:
        # 这里可以根据实际需要从数据库获取统计信息
        # 目前返回模拟数据
        stats = {
            'total_analysis': 0,
            'total_backtest': 0,
            'total_reports': 0,
            'success_rate': 0
        }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取用户统计信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


@app.route('/api/user/activities')
@login_required
def api_user_activities():
    """获取用户最近活动"""
    try:
        # 返回模拟活动数据
        activities = [
            {
                'type': 'login',
                'title': f'用户{session.get("username", "")}登录系统',
                'created_at': datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': activities
        })
        
    except Exception as e:
        logger.error(f"获取用户活动失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


# ================================
# 股票数据API（需要登录）
# ================================


@app.route('/api/stocks/list')
@login_required
def get_stock_list():
    """获取股票列表"""
    try:
        # 从数据库获取股票列表
        from core.storage import DatabaseManager
        db = DatabaseManager()
        stocks = db.get_stock_list()
        
        return jsonify({
            'success': True,
            'data': stocks,
            'message': '获取股票列表成功'
        })
    except Exception as e:
        logging.error(f"获取股票列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取股票列表失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/data')
@login_required
def get_stock_data(symbol):
    """获取股票历史数据"""
    try:
        days = request.args.get('days', 90, type=int)
        
        # 获取股票数据
        from core.data_source import DataSource
        data_source = DataSource()
        df = data_source.get_stock_data(symbol, days=days)
        
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 处理NaN值
        df = df.fillna(0)
        
        # 转换为字典格式
        stock_data = []
        for _, row in df.iterrows():
            record = {
                'date': row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else str(row.name),
                'open': float(row.get('open', 0)),
                'high': float(row.get('high', 0)),
                'low': float(row.get('low', 0)),
                'close': float(row.get('close', 0)),
                'volume': int(row.get('volume', 0)),
                'amount': float(row.get('amount', 0))
            }
            stock_data.append(record)
        
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
@login_required
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
        
        # 处理NaN值
        def clean_nan(obj):
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            elif isinstance(obj, float) and pd.isna(obj):
                return 0.0
            else:
                return obj
        
        analysis = clean_nan(analysis)
        
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
@login_required
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
@login_required
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
        
        # 处理NaN值
        df = df.fillna(0)
        
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
        
        # 处理NaN值
        def clean_nan(obj):
            if isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            elif isinstance(obj, float) and pd.isna(obj):
                return 0.0
            else:
                return obj
        
        # 准备返回数据
        response_data = {
            'backtest_id': backtest_id,
            'strategy_name': results['strategy_name'],
            'symbol': results['symbol'],
            'start_date': results['start_date'],
            'end_date': results['end_date'],
            'initial_capital': float(results['initial_capital']),
            'final_value': float(results['final_value']),
            'total_return': float(results['total_return']),
            'annual_return': float(results['annual_return']),
            'max_drawdown': float(results['max_drawdown']),
            'sharpe_ratio': float(results['sharpe_ratio']),
            'trade_count': int(results['trade_count']),
            'win_rate': float(results['win_rate'])
        }
        
        # 处理equity_curve
        if 'equity_curve' in results and hasattr(results['equity_curve'], 'index'):
            equity_curve = results['equity_curve']
            equity_dict = {}
            for date, value in equity_curve.items():
                date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
                equity_dict[date_str] = float(value) if pd.notna(value) else 0.0
            response_data['equity_curve'] = equity_dict
        else:
            response_data['equity_curve'] = {}
        
        # 清理NaN值
        response_data = clean_nan(response_data)
        
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


# ================================
# 数据同步API（需要登录）
# ================================



@app.route('/api/stocks/sync/latest', methods=['POST'])
@login_required
def sync_stock_latest():
    """同步最新股票数据"""
    try:
        # 获取请求参数
        days = request.json.get('days', 30)
        batch_size = request.json.get('batch_size', 50)
        delay = request.json.get('delay', 1.0)
        
        # 创建同步会话
        session_id = str(uuid.uuid4())
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 在新线程中执行同步
        def run_sync():
            try:
                result = synchronizer.sync_latest_stock_data(
                    days=days, 
                    batch_size=batch_size, 
                    delay=delay,
                    session_id=session_id
                )
            except Exception as e:
                logger.error(f"同步最新股票数据失败: {e}")
                sync_progress_manager.fail_sync(session_id, str(e))
        
        import threading
        sync_thread = threading.Thread(target=run_sync)
        sync_thread.daemon = True
        sync_thread.start()
        
        return jsonify({
            'code': 200,
            'message': '同步任务已启动',
            'data': {
                'session_id': session_id
            }
        })
    except Exception as e:
        logger.error(f"启动同步任务失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'启动同步任务失败: {str(e)}'
        }), 500

@app.route('/api/stocks/sync/history', methods=['POST'])
@login_required
def sync_stock_history():
    """同步股票历史数据"""
    try:
        # 获取请求参数
        days = request.json.get('days', 365)
        batch_size = request.json.get('batch_size', 50)
        delay = request.json.get('delay', 1.0)
        
        # 创建同步会话
        session_id = str(uuid.uuid4())
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 在新线程中执行同步
        def run_sync():
            try:
                result = synchronizer.sync_all_stock_daily_data(
                    days=days, 
                    batch_size=batch_size, 
                    delay=delay,
                    session_id=session_id
                )
            except Exception as e:
                logger.error(f"同步历史数据失败: {e}")
                sync_progress_manager.fail_sync(session_id, str(e))
        
        import threading
        sync_thread = threading.Thread(target=run_sync)
        sync_thread.daemon = True
        sync_thread.start()
        
        return jsonify({
            'code': 200,
            'message': '同步任务已启动',
            'data': {
                'session_id': session_id
            }
        })
    except Exception as e:
        logger.error(f"启动同步任务失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'启动同步任务失败: {str(e)}'
        }), 500

@app.route('/api/stocks/sync/list', methods=['POST'])
@login_required
def sync_stock_list():
    """同步股票列表"""
    try:
        # 创建同步会话
        session_id = str(uuid.uuid4())
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 在新线程中执行同步
        def run_sync():
            try:
                count = synchronizer.sync_stock_list(session_id=session_id)
            except Exception as e:
                logger.error(f"同步股票列表失败: {e}")
                sync_progress_manager.fail_sync(session_id, str(e))
        
        import threading
        sync_thread = threading.Thread(target=run_sync)
        sync_thread.daemon = True
        sync_thread.start()
        
        return jsonify({
            'code': 200,
            'message': '同步任务已启动',
            'data': {
                'session_id': session_id
            }
        })
    except Exception as e:
        logger.error(f"启动同步任务失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'启动同步任务失败: {str(e)}'
        }), 500

@app.route('/api/stocks/sync/progress/<session_id>')
@login_required
def get_sync_progress(session_id):
    """获取同步进度"""
    try:
        progress = sync_progress_manager.get_progress(session_id)
        if not progress:
            return jsonify({
                'code': 404,
                'message': '同步会话不存在或已过期'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取进度成功',
            'data': progress
        })
    except Exception as e:
        logger.error(f"获取同步进度失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取同步进度失败: {str(e)}'
        }), 500

@app.route('/api/stocks/sync/single/<symbol>', methods=['POST'])
@login_required
def sync_single_stock(symbol):
    """同步单只股票数据"""
    try:
        # 获取请求参数
        days = request.json.get('days', 365) if request.json else 365
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 同步单只股票数据（基本信息 + 历史数据）
        success = synchronizer.sync_single_stock_info(symbol)
        if success:
            count = synchronizer.sync_single_stock_daily_data(symbol, days=days)
            return jsonify({
                'code': 200,
                'message': f'股票 {symbol} 同步完成',
                'data': {
                    'symbol': symbol,
                    'info_synced': success,
                    'history_count': count
                }
            })
        else:
            return jsonify({
                'code': 404,
                'message': f'股票 {symbol} 不存在或同步失败'
            }), 404
            
    except Exception as e:
        logger.error(f"同步单只股票失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步失败: {str(e)}'
        }), 500


# ================================
# 行业列表API（需要登录）
# ================================

@app.route('/api/industries')
@login_required
def get_industries():
    """获取股票行业列表"""
    try:
        import sqlite3
        with sqlite3.connect('data/finance_data.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT DISTINCT industry 
                FROM stock_info 
                WHERE industry IS NOT NULL AND industry != ''
                ORDER BY industry
            ''')
            
            industries = [row['industry'] for row in cursor.fetchall()]
            
        return jsonify({
            'success': True,
            'data': industries,
            'message': '获取行业列表成功'
        })
    except Exception as e:
        logger.error(f"获取行业列表失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取行业列表失败: {str(e)}'
        }), 500


# ================================
# 历史数据分析页面
# ================================

@app.route('/analysis/history/<symbol>')
@login_required
def history_analysis(symbol):
    """历史数据分析页面"""
    try:
        # 获取股票名称参数
        stock_name = request.args.get('name', symbol)
        
        # 验证股票代码是否存在
        stock_info = data_source.get_stock_info(symbol)
        if not stock_info:
            return render_template('404.html', message=f'股票代码 {symbol} 不存在'), 404
            
        return render_template('history_analysis.html', 
                             symbol=symbol, 
                             stock_name=stock_name)
        
    except Exception as e:
        logger.error(f"访问历史分析页面失败: {e}")
        return render_template('error.html', message=str(e)), 500


@app.route('/api/stocks/<symbol>')
@login_required
def get_stock_info(symbol):
    """获取股票基本信息"""
    try:
        # 获取股票信息 - 优先从数据库获取
        import sqlite3
        try:
            with sqlite3.connect('data/finance_data.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT symbol, name, industry, market_cap, pe_ratio, pb_ratio, close, updated_at 
                    FROM stock_info WHERE symbol = ?
                ''', [symbol])
                row = cursor.fetchone()
                
                if row:
                    stock_data = dict(row)
                    # 确保返回正确的字段格式
                    stock_info = {
                        'symbol': stock_data['symbol'],
                        'name': stock_data['name'],
                        'industry': stock_data['industry'] or 'N/A',
                        'market_cap': float(stock_data['market_cap'] or 0),
                        'pe_ratio': float(stock_data['pe_ratio'] or 0),
                        'close': float(stock_data['close'] or 0)
                    }
                else:
                    # 如果数据库中没有，从数据源获取
                    stock_info = data_source.get_stock_info(symbol)
                    if not stock_info:
                        return jsonify({
                            'code': 404,
                            'message': '股票不存在'
                        }), 404
        except Exception as db_error:
            logger.error(f"数据库查询失败: {db_error}")
            stock_info = data_source.get_stock_info(symbol)
            if not stock_info:
                return jsonify({
                    'code': 404,
                    'message': '股票不存在'
                }), 404
        
        # 获取最新价格数据
        df = data_source.get_stock_data(symbol, days=1)
        if not df.empty:
            latest_data = df.iloc[-1]
            current_price = float(latest_data['close']) if pd.notna(latest_data['close']) else 0.0
        else:
            current_price = 0.0
        
        # 准备返回数据 - 使用数据库中的数据
        stock_data = {
            'symbol': str(stock_info.get('symbol', symbol)),
            'name': str(stock_info.get('name', symbol)),
            'close': stock_info.get('close', current_price),
            'market_cap': float(stock_info.get('market_cap', 0)),
            'pe_ratio': float(stock_info.get('pe_ratio', 0)),
            'industry': str(stock_info.get('industry', 'N/A'))
        }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': stock_data,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"获取股票基本信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/history')
@login_required
def get_stock_history(symbol):
    """获取股票历史数据"""
    try:
        # 获取参数
        period = request.args.get('period', '1Y')
        
        # 根据周期设置天数
        period_days = {
            '1M': 30,
            '3M': 90,
            '6M': 180,
            '1Y': 365,
            '2Y': 730,
            '5Y': 1825
        }
        
        if period == 'ALL':
            # 获取全部历史数据，设置一个很大的天数
            days = 36500  # 约100年的数据
        else:
            days = period_days.get(period, 365)
        
        # 获取股票数据
        df = data_source.get_stock_data(symbol, days=days)
        if df.empty:
            return jsonify({
                'code': 404,
                'message': '股票数据不存在'
            }), 404
        
        # 计算技术指标
        df = analyzer.calculate_all_indicators(df)
        
        # 处理NaN值
        def clean_nan(value):
            if pd.isna(value):
                return 0.0
            return float(value)
        
        # 准备数据
        history_data = []
        for index, row in df.iterrows():
            history_data.append({
                'date': index.strftime('%Y-%m-%d'),
                'open': clean_nan(row['open']),
                'high': clean_nan(row['high']),
                'low': clean_nan(row['low']),
                'close': clean_nan(row['close']),
                'volume': int(clean_nan(row['volume'])),
                'ma20': clean_nan(row.get('MA20', 0)),
                'ma50': clean_nan(row.get('MA50', 0)),
                'rsi': clean_nan(row.get('RSI14', 0))
            })
        
        # 计算统计数据
        if not df.empty:
            stats = {
                'highest_price': clean_nan(df['high'].max()),
                'lowest_price': clean_nan(df['low'].min()),
                'avg_price': clean_nan(df['close'].mean()),
                'total_volume': int(df['volume'].sum()),
                'avg_volume': int(df['volume'].mean()),
                'price_change': clean_nan(df['close'].iloc[-1] - df['close'].iloc[0]),
                'price_change_percent': clean_nan(((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100),
                'current_price': clean_nan(df['close'].iloc[-1]),
                'latest_date': df.index[-1].strftime('%Y-%m-%d')
            }
        else:
            stats = {}
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'symbol': symbol,
                'history': history_data,
                'stats': stats
            }
        })
        
    except Exception as e:
        logger.error(f"获取股票历史数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


# ================================
# 公司分析相关接口
# ================================

@app.route('/analysis/company/<symbol>')
@login_required
def company_analysis_page(symbol):
    """公司分析页面"""
    try:
        # 获取股票基本信息
        stock_info = data_source.get_stock_info(symbol)
        if not stock_info:
            return "股票不存在", 404
            
        return render_template('company_analysis.html', company=stock_info)
        
    except Exception as e:
        logger.error(f"加载公司分析页面失败: {e}")
        return "加载失败", 500

@app.route('/api/stock/sync', methods=['POST'])
@login_required
def sync_stock_data():
    """同步股票数据"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({
                'code': 400,
                'message': '股票代码不能为空'
            }), 400
        
        # 创建同步器
        syncer = StockDataSynchronizer()
        
        # 同步数据
        result = syncer.sync_stock_data(symbol)
        
        if result['success']:
            return jsonify({
                'code': 200,
                'message': result['message'],
                'data': result['data']
            })
        else:
            return jsonify({
                'code': 500,
                'message': result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"同步股票数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步失败: {str(e)}'
        }), 500

# ================================
# AKShare接口管理API
# ================================

@app.route('/api/akshare/interfaces', methods=['GET'])
@login_required
def get_akshare_interfaces():
    """获取所有AKShare接口数据"""
    try:
        # 查询akshare_interfaces表
        query = """
            SELECT 
                id,
                interface_name,
                interface_name_cn,
                interface_description,
                module_name,
                function_type,
                category_level1,
                category_level2,
                status,
                update_time
            FROM akshare_interfaces
            ORDER BY category_level1, interface_name
        """
        
        interfaces = db_manager.query(query)
        
        return jsonify({
            'code': 200,
            'message': '获取接口数据成功',
            'data': interfaces
        })
        
    except Exception as e:
        logger.error(f"获取AKShare接口数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取接口数据失败: {str(e)}'
        }), 500

@app.route('/api/akshare/interfaces/<int:interface_id>', methods=['GET'])
@login_required
def get_interface_detail(interface_id):
    """获取单个接口详细信息"""
    try:
        # 查询接口详情
        query = """
            SELECT *
            FROM akshare_interfaces
            WHERE id = ?
        """
        
        interface = db_manager.query(query, [interface_id])
        
        if not interface:
            return jsonify({
                'code': 404,
                'message': '接口不存在'
            }), 404
        
        return jsonify({
            'code': 200,
            'message': '获取接口详情成功',
            'data': interface[0]
        })
        
    except Exception as e:
        logger.error(f"获取接口详情失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取接口详情失败: {str(e)}'
        }), 500

@app.route('/api/akshare/interfaces/stats', methods=['GET'])
@login_required
def get_interface_stats():
    """获取接口统计信息"""
    try:
        # 统计各分类接口数量
        query = """
            SELECT 
                category_level1,
                COUNT(*) as count
            FROM akshare_interfaces
            GROUP BY category_level1
            ORDER BY count DESC
        """
        
        stats = db_manager.query(query)
        
        # 总接口数
        total_query = "SELECT COUNT(*) as total FROM akshare_interfaces"
        total = db_manager.query(total_query)[0]['total']
        
        return jsonify({
            'code': 200,
            'message': '获取统计信息成功',
            'data': {
                'total': total,
                'by_category': stats
            }
        })
        
    except Exception as e:
        logger.error(f"获取接口统计信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500

@app.route('/api/akshare/interfaces/download', methods=['POST'])
@login_required
def download_interface_data():
    """下载接口数据到本地数据库"""
    try:
        data = request.get_json()
        interface_name = data.get('interface_name')
        
        if not interface_name:
            return jsonify({
                'code': 400,
                'message': '接口名称不能为空'
            }), 400
        
        # 获取接口详细信息
        query = """
            SELECT * FROM akshare_interfaces 
            WHERE interface_name = ?
        """
        interface_info = db_manager.query(query, [interface_name])
        
        if not interface_info:
            return jsonify({
                'code': 404,
                'message': '接口不存在'
            }), 404
        
        # 使用AKShare获取数据
        import akshare as ak
        
        # 验证接口是否存在
        if not hasattr(ak, interface_name):
            return jsonify({
                'code': 404,
                'message': f'接口不存在: {interface_name}',
                'interface_name': interface_name,
                'suggestion': '请检查接口名称是否正确，或联系管理员更新接口列表'
            }), 404
        
        # 动态获取接口函数
        func = getattr(ak, interface_name)
        
        # 尝试调用接口获取数据，增加网络错误和空数据保护
        try:
            import requests
            import json
            
            # 根据接口名称选择不同的调用策略
            df = None
            
            # 特殊处理已知问题接口
            if interface_name == 'stock_a_indicator_lg':
                df = func()
            elif interface_name == 'stock_zh_a_spot':
                # stock_zh_a_spot接口经常返回HTML而不是JSON，需要特殊处理
                try:
                    df = func()
                except Exception as e:
                    if 'decode' in str(e).lower() or 'json' in str(e).lower():
                        return jsonify({
                            'code': 503,
                            'message': '接口暂时不可用: A股现货接口当前数据源异常',
                            'interface_name': interface_name,
                            'suggestion': '该接口可能由于数据源维护暂时不可用，请稍后重试或使用其他接口',
                            'error_type': 'data_source_unavailable',
                            'error_detail': str(e)
                        }), 503
                    else:
                        raise  # 重新抛出其他类型的异常
            else:
                # 普通接口调用
                try:
                    df = func()
                except TypeError:
                    # 如果接口需要参数
                    if interface_name.startswith('stock_') and 'hist' in interface_name:
                        df = func(symbol="000001", period="daily", adjust="")
                    elif interface_name.startswith('stock_') and 'spot' in interface_name:
                        df = func()
                    elif interface_name.startswith('bond_'):
                        df = func()
                    elif interface_name.startswith('fund_'):
                        df = func()
                    else:
                        df = func()
        
        except (json.JSONDecodeError, ValueError) as e:
            # 处理stock_a_indicator_lg接口的空数据或格式错误
            if interface_name == 'stock_a_indicator_lg':
                return jsonify({
                    'code': 503,
                    'message': '接口暂时不可用: A股技术指标接口当前无法访问',
                    'interface_name': interface_name,
                    'suggestion': '该接口可能由于数据源问题暂时不可用，请稍后重试或使用其他接口',
                    'error_type': 'data_source_unavailable'
                }), 503
            else:
                return jsonify({
                    'code': 500,
                    'message': '数据解析失败: 接口返回的数据格式不正确',
                    'interface_name': interface_name,
                    'suggestion': '该接口的数据源可能正在维护，请稍后重试'
                }), 500
                
        except requests.exceptions.RequestException as net_error:
            return jsonify({
                'code': 503,
                'message': '网络请求失败',
                'interface_name': interface_name,
                'suggestion': '请检查网络连接，或该接口数据源可能暂时不可用',
                'error_detail': str(net_error)
            }), 503
            
        except Exception as e:
            # 区分不同类型的错误
            error_msg = str(e).lower()
            if 'json' in error_msg or 'decode' in error_msg:
                return jsonify({
                    'code': 500,
                    'message': '数据解析失败: 接口返回的数据格式不正确',
                    'interface_name': interface_name,
                    'suggestion': '该接口的数据源可能正在维护，请稍后重试'
                }), 500
            elif 'connection' in error_msg or 'timeout' in error_msg:
                return jsonify({
                    'code': 503,
                    'message': '网络连接失败: 无法连接到数据源',
                    'interface_name': interface_name,
                    'suggestion': '请检查网络连接或稍后再试'
                }), 503
            else:
                return jsonify({
                    'code': 500,
                    'message': f'接口调用失败: {str(e)}',
                    'interface_name': interface_name,
                    'suggestion': '请检查接口名称是否正确，或联系管理员'
                }), 500
        
        if df is None or df.empty:
            return jsonify({
                'code': 404,
                'message': '接口返回数据为空',
                'interface_name': interface_name
            }), 404
        
        # 创建表名（安全处理）
        table_name = f"akshare_{interface_name}"
        table_name = table_name.replace('-', '_').replace('.', '_')
        
        # 检查表是否存在
        check_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        table_exists = db_manager.query(check_query, [table_name])
        
        # 创建安全的列名映射
        import re
        
        # 安全的列名映射 - 按接口类型分组
        column_mapping = {}
        
        # 概念板块接口映射
        if interface_name == 'stock_board_concept_name_em':
            column_mapping = {
                '排名': 'rank',
                '板块名称': 'board_name',
                '板块代码': 'board_code', 
                '最新价': 'latest_price',
                '涨跌额': 'change_amount',
                '涨跌幅': 'change_percent',
                '总市值': 'total_market_cap',
                '换手率': 'turnover_rate',
                '上涨家数': 'up_count',
                '下跌家数': 'down_count',
                '领涨股票': 'leading_stock',
                '领涨股票-涨跌幅': 'leading_stock_change'
            }
        # A股现货接口映射
        elif interface_name == 'stock_zh_a_spot':
            column_mapping = {
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'latest_price',
                '涨跌额': 'change_amount',
                '涨跌幅': 'change_percent',
                '买入': 'bid_price',
                '卖出': 'ask_price',
                '昨收': 'prev_close',
                '今开': 'open_price',
                '最高': 'high_price',
                '最低': 'low_price',
                '成交量': 'volume',
                '成交额': 'turnover',
                '时间戳': 'timestamp'
            }
        else:
            # 通用映射 - 处理常见的中文列名
            column_mapping = {
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'latest_price',
                '收盘价': 'close_price',
                '开盘价': 'open_price',
                '最高价': 'high_price',
                '最低价': 'low_price',
                '成交量': 'volume',
                '成交额': 'turnover',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '市值': 'market_cap'
            }
        
        # 重命名DataFrame的列
        safe_column_mapping = {}
        for i, col in enumerate(df.columns):
            safe_col = column_mapping.get(str(col), None)
            if not safe_col:
                # 将特殊字符替换为下划线，确保列名安全
                safe_col = re.sub(r'[^a-zA-Z0-9_]', '_', str(col))
                # 确保列名是有效的SQL标识符
                if not safe_col or safe_col[0].isdigit():
                    safe_col = f'col_{i}'
                elif safe_col in safe_column_mapping.values():
                    # 确保列名唯一
                    safe_col = f'{safe_col}_{i}'
                else:
                    safe_col = safe_col
            safe_column_mapping[str(col)] = safe_col
        
        # 重命名DataFrame的列
        df_renamed = df.rename(columns=safe_column_mapping)
        
        # 添加下载时间
        df_renamed['download_time'] = datetime.now()
        
        # 插入数据
        df_renamed.to_sql(table_name, db_manager.get_connection(), if_exists='append', index=False)
        
        # 获取插入的记录数
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        total_records = db_manager.query(count_query)[0]['count']
        
        return jsonify({
            'code': 200,
            'message': '数据下载成功',
            'data': {
                'interface_name': interface_name,
                'table_name': table_name,
                'records_inserted': len(df),
                'total_records': total_records,
                'columns': list(df.columns),
                'download_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        logger.error(f"下载接口数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'下载失败: {str(e)}'
        }), 500

@app.route('/api/akshare/interfaces/download/all', methods=['POST'])
@login_required
def download_all_interface_data():
    """下载所有接口数据到本地数据库"""
    try:
        # 获取所有接口
        query = "SELECT interface_name FROM akshare_interfaces WHERE status = 'active'"
        interfaces = db_manager.query(query)
        
        if not interfaces:
            return jsonify({
                'code': 404,
                'message': '没有找到可用的接口'
            }), 404
        
        import akshare as ak
        results = []
        
        for interface in interfaces:
            interface_name = interface['interface_name']
            
            # 验证接口是否存在
            if not hasattr(ak, interface_name):
                results.append({
                    'interface_name': interface_name,
                    'status': 'not_found',
                    'message': f'接口不存在: {interface_name}'
                })
                continue
            
            try:
                # 获取接口函数
                func = getattr(ak, interface_name)
                
                # 尝试调用接口，增强错误处理
                try:
                    import requests
                    import json
                    
                    df = None
                    max_retries = 2
                    
                    for attempt in range(max_retries):
                        try:
                            # 特殊处理已知问题接口
                            if interface_name == 'stock_a_indicator_lg':
                                try:
                                    df = func()
                                except (json.JSONDecodeError, ValueError) as e:
                                    # stock_a_indicator_lg接口经常返回空数据或格式错误
                                    results.append({
                                        'interface_name': interface_name,
                                        'status': 'unavailable',
                                        'message': 'A股技术指标接口暂时不可用',
                                        'error': str(e),
                                        'suggestion': '该接口数据源可能正在维护，建议跳过此接口'
                                    })
                                    break
                                except Exception as e:
                                    results.append({
                                        'interface_name': interface_name,
                                        'status': 'error',
                                        'message': str(e),
                                        'suggestion': '接口调用失败'
                                    })
                                    break
                            else:
                                # 普通接口调用
                                try:
                                    df = func()
                                except TypeError:
                                    # 如果接口需要参数
                                    if interface_name.startswith('stock_') and 'hist' in interface_name:
                                        df = func(symbol="000001", period="daily", adjust="")
                                    elif interface_name.startswith('stock_') and 'spot' in interface_name:
                                        df = func()
                                    else:
                                        df = func()
                            
                            # 如果成功获取数据，跳出重试循环
                            if df is not None:
                                break
                                
                        except (requests.exceptions.RequestException, json.JSONDecodeError) as net_error:
                            if attempt == max_retries - 1:
                                results.append({
                                    'interface_name': interface_name,
                                    'status': 'network_error',
                                    'message': f'网络请求失败: {str(net_error)}',
                                    'suggestion': '请检查网络连接'
                                })
                                break
                            else:
                                continue
                        except Exception as e:
                            if attempt == max_retries - 1:
                                error_msg = str(e).lower()
                                if 'json' in error_msg or 'decode' in error_msg:
                                    results.append({
                                        'interface_name': interface_name,
                                        'status': 'data_error',
                                        'message': '数据解析失败: 接口返回数据格式错误',
                                        'suggestion': '接口数据源可能正在维护'
                                    })
                                elif 'connection' in error_msg or 'timeout' in error_msg:
                                    results.append({
                                        'interface_name': interface_name,
                                        'status': 'network_error',
                                        'message': '网络连接失败',
                                        'suggestion': '请检查网络连接'
                                    })
                                else:
                                    results.append({
                                        'interface_name': interface_name,
                                        'status': 'error',
                                        'message': str(e),
                                        'suggestion': '接口调用失败'
                                    })
                                break
                            else:
                                continue
                    
                    # 检查是否成功获取数据
                    if df is not None and not df.empty:
                        # 创建表并插入数据
                        table_name = f"akshare_{interface_name}".replace('-', '_').replace('.', '_')
                        
                        df['download_time'] = datetime.now()
                        df.to_sql(table_name, db_manager.get_connection(), if_exists='replace', index=False)
                        
                        results.append({
                            'interface_name': interface_name,
                            'status': 'success',
                            'records': len(df),
                            'table_name': table_name
                        })
                    elif df is not None and interface_name != 'stock_a_indicator_lg':
                        # 避免重复记录stock_a_indicator_lg的错误
                        results.append({
                            'interface_name': interface_name,
                            'status': 'empty',
                            'records': 0,
                            'message': '返回空数据'
                        })
                        
                except Exception as e:
                    results.append({
                        'interface_name': interface_name,
                        'status': 'error',
                        'message': str(e),
                        'suggestion': '接口调用失败'
                    })
                    
            except Exception as e:
                results.append({
                    'interface_name': interface_name,
                    'status': 'error',
                    'message': str(e)
                })
        
        success_count = len([r for r in results if r['status'] == 'success'])
        total_records = sum([r.get('records', 0) for r in results])
        
        return jsonify({
            'code': 200,
            'message': f'批量下载完成，成功{success_count}个接口',
            'data': {
                'total_interfaces': len(interfaces),
                'success_count': success_count,
                'total_records': total_records,
                'results': results
            }
        })
        
    except Exception as e:
        logger.error(f"批量下载接口数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'批量下载失败: {str(e)}'
        }), 500


@app.route('/api/company/<symbol>/data')
@login_required
def get_company_data(symbol):
    """获取公司分析数据"""
    try:
        days = request.args.get('days', 90, type=int)
        
        # 优先从本地数据库获取股票基本信息
        from core.storage import DatabaseManager
        db = DatabaseManager()
        stock_info = db.get_stock_info(symbol)
        
        if not stock_info:
            # 如果本地没有，尝试从外部获取
            try:
                stock_info = data_source.get_stock_info(symbol)
                if not stock_info:
                    return jsonify({
                        'code': 404,
                        'message': '股票不存在'
                    }), 404
            except Exception as e:
                logger.warning(f"外部数据源获取失败，使用本地数据: {e}")
                return jsonify({
                    'code': 404,
                    'message': '股票不存在'
                }), 404
        
        # 转换字段名称以适应API，处理可能的字符串值
        def safe_float(value, default=0.0):
            """安全地将值转换为浮点数"""
            if value is None or value == '' or str(value).upper() == 'N/A':
                return default
            try:
                return float(str(value).replace(',', ''))
            except (ValueError, TypeError):
                return default
        
        # 统一处理数据格式
        if isinstance(stock_info, dict):
            # 外部数据源格式
            company_data = {
                'symbol': str(stock_info.get('股票代码', symbol)),
                'name': str(stock_info.get('股票简称', symbol)),
                'industry': str(stock_info.get('行业', 'N/A')),
                'market': str(stock_info.get('市场', '深证')),
                'list_date': str(stock_info.get('上市时间', '')),
                'market_cap': safe_float(stock_info.get('总市值', 0)) / 100000000,  # 转换为亿元
                'close': safe_float(stock_info.get('最新价', 0)),
                'pe_ratio': safe_float(stock_info.get('市盈率', 0)),
                'pb_ratio': safe_float(stock_info.get('市净率', 0))
            }
        else:
            # 本地数据库格式 (tuple)
            company_data = {
                'symbol': str(stock_info[0]),
                'name': str(stock_info[1]),
                'industry': str(stock_info[5]),
                'market': str(stock_info[6]) if len(stock_info) > 6 else '深证',
                'list_date': str(stock_info[7]) if len(stock_info) > 7 else '',
                'market_cap': safe_float(stock_info[4]) / 100000000 if len(stock_info) > 4 else 0.0,
                'close': safe_float(stock_info[2]),
                'pe_ratio': safe_float(stock_info[3]),
                'pb_ratio': safe_float(stock_info[4])
            }
        
        # 尝试获取历史价格数据，使用本地数据作为备用
        df = None
        try:
            df = data_source.get_stock_data(symbol, days=days)
            if df.empty:
                # 如果外部数据为空，使用本地历史数据
                from core.storage import DatabaseManager
                db = DatabaseManager()
                df = db.get_stock_data(symbol, limit=days)
        except Exception as e:
            logger.warning(f"外部历史数据获取失败，使用本地数据: {e}")
            from core.storage import DatabaseManager
            db = DatabaseManager()
            df = db.get_stock_data(symbol, limit=days)
        
        if df is None or df.empty:
            # 如果仍然没有数据，创建模拟数据
            from datetime import datetime, timedelta
            import random
            
            # 创建基于最新价格的模拟数据
            latest_price = company_data['close']
            dates = [datetime.now() - timedelta(days=i) for i in range(days, 0, -1)]
            
            # 生成模拟价格数据
            prices_data = []
            current_price = latest_price
            for date in dates:
                # 添加一些随机波动
                change = random.uniform(-0.02, 0.02)
                current_price = current_price * (1 + change)
                prices_data.append({
                    'open': current_price * 0.99,
                    'close': current_price,
                    'high': current_price * 1.01,
                    'low': current_price * 0.98,
                    'volume': random.randint(1000000, 10000000)
                })
            
            df = pd.DataFrame(prices_data, index=dates)
        
        # 计算技术指标
        try:
            df = analyzer.calculate_all_indicators(df)
        except Exception as e:
            logger.warning(f"技术指标计算失败: {e}")
        
        # 处理NaN值
        def clean_nan(value):
            if pd.isna(value):
                return 0.0
            return float(value)
        
        # 准备价格数据
        prices = []
        for index, row in df.iterrows():
            date_str = str(index)
            if hasattr(index, 'strftime'):
                date_str = index.strftime('%Y-%m-%d')
            else:
                # 处理日期字符串中的时间部分
                date_str = str(index).split(' ')[0]
            
            prices.append({
                'date': date_str,
                'open': clean_nan(row.get('open', row.get('close', 0))),
                'high': clean_nan(row.get('high', row.get('close', 0))),
                'low': clean_nan(row.get('low', row.get('close', 0))),
                'close': clean_nan(row.get('close', 0)),
                'volume': int(clean_nan(row.get('volume', 0)))
            })
        
        # 准备技术指标数据
        indicators = []
        for index, row in df.iterrows():
            date_str = str(index)
            if hasattr(index, 'strftime'):
                date_str = index.strftime('%Y-%m-%d')
            else:
                # 处理日期字符串中的时间部分
                date_str = str(index).split(' ')[0]
                
            indicator_data = {
                'date': date_str,
                'close': clean_nan(row.get('close', 0))
            }
            
            # 添加各种技术指标
            for col in ['MA5', 'MA10', 'MA20', 'MA50', 'RSI14', 'MACD', 'MACD_signal', 'MACD_hist']:
                if col in row:
                    key = col.lower().replace('rsi14', 'rsi').replace('macd_signal', 'macd_signal').replace('macd_hist', 'macd_hist')
                    indicator_data[key] = clean_nan(row[col])
            
            indicators.append(indicator_data)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'company': company_data,
                'prices': prices,
                'indicators': indicators
            }
        })
        
    except Exception as e:
        logger.error(f"获取公司分析数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500


@app.route('/api/company/<symbol>/sync', methods=['POST'])
@login_required
def sync_company_data(symbol):
    """同步公司最新数据"""
    try:
        from core.stock_sync import StockDataSynchronizer
        synchronizer = StockDataSynchronizer()
        
        # 同步股票基本信息
        success = synchronizer.sync_single_stock_info(symbol)
        
        if success:
            # 同步历史数据
            count = synchronizer.sync_single_stock_history(symbol)
            
            logger.info(f"成功同步股票 {symbol} 的最新数据")
            return jsonify({
                'code': 200,
                'message': f'数据同步成功，共同步{count}条历史数据',
                'success': True
            })
        else:
            # 即使基本信息同步失败，也尝试同步历史数据
            count = synchronizer.sync_single_stock_history(symbol)
            if count > 0:
                logger.info(f"成功同步股票 {symbol} 的历史数据")
                return jsonify({
                    'code': 200,
                    'message': f'历史数据同步成功，共同步{count}条数据',
                    'success': True
                })
            else:
                return jsonify({
                    'code': 500,
                    'message': '同步失败：无法获取股票数据',
                    'success': False
                })
            
    except Exception as e:
        logger.error(f"同步公司数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步失败: {str(e)}',
            'success': False
        }), 500


# 静态文件服务
@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件服务"""


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

# ================================
# 数据库表管理API
# ================================

@app.route('/database')
@login_required
def database_page():
    """数据库管理页面"""
    return render_template('database.html')

@app.route('/stock-sync')
@login_required
def stock_sync_page():
    """股票数据同步页面"""
    return render_template('stock_sync.html')

@app.route('/api/database/tables', methods=['GET'])
@login_required
def get_database_tables():
    """获取数据库所有表信息"""
    try:
        # 获取所有表
        query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables = db_manager.query(query)
        
        table_info = []
        total_records = 0
        interface_tables = 0
        data_tables = 0
        
        for table in tables:
            table_name = table['name']
            
            # 获取记录数
            count_query = f"SELECT COUNT(*) as count FROM {table_name}"
            count_result = db_manager.query(count_query)
            row_count = count_result[0]['count'] if count_result else 0
            
            # 获取列信息
            columns_query = f"PRAGMA table_info({table_name})"
            columns = db_manager.query(columns_query)
            column_count = len(columns)
            
            # 分类
            category = get_table_category(table_name)
            description = get_table_description(table_name)
            
            # 统计
            total_records += row_count
            if 'interface' in table_name.lower() or table_name.startswith('akshare_interface'):
                interface_tables += 1
            elif table_name.startswith('akshare_') and 'interface' not in table_name:
                data_tables += 1
            
            table_info.append({
                'name': table_name,
                'row_count': row_count,
                'column_count': column_count,
                'category': category,
                'description': description,
                'columns': [{'name': col['name'], 'type': col['type']} for col in columns]
            })
        
        # 按记录数排序
        table_info.sort(key=lambda x: x['row_count'], reverse=True)
        
        return jsonify({
            'code': 200,
            'message': '获取数据库表信息成功',
            'data': {
                'total_tables': len(tables),
                'total_records': total_records,
                'interface_tables': interface_tables,
                'data_tables': data_tables,
                'tables': table_info
            }
        })
        
    except Exception as e:
        logger.error(f"获取数据库表信息失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取数据库表信息失败: {str(e)}'
        }), 500

def get_table_category(table_name):
    """获取表的分类"""
    if table_name.startswith('akshare_interface'):
        return '接口元数据'
    elif table_name.startswith('akshare_stock_balance_sheet') or table_name.startswith('akshare_stock_cash_flow_sheet') or table_name.startswith('akshare_stock_profit_sheet'):
        return '财务报表'
    elif table_name.startswith('akshare_stock_board_concept') or table_name.startswith('akshare_stock_board_industry'):
        return '板块数据'
    elif table_name.startswith('akshare_stock_gdfx'):
        return '股东数据'
    elif table_name.startswith('akshare_stock_individual_fund_flow') or table_name.startswith('akshare_stock_market_fund_flow'):
        return '资金流向'
    elif table_name.startswith('akshare_stock_margin'):
        return '融资融券'
    elif table_name.startswith('akshare_stock_financial_abstract'):
        return '财务指标'
    elif table_name.startswith('akshare_stock_individual_info') or table_name.startswith('akshare_stock_info_a'):
        return '股票信息'
    elif table_name.startswith('akshare_stock_zh_a_daily') or table_name.startswith('akshare_stock_zh_a_spot'):
        return 'A股行情'
    elif table_name.startswith('akshare_stock_zh_index'):
        return '指数行情'
    elif table_name.startswith('akshare_'):
        return 'AKShare数据'
    elif table_name in ['stock_info', 'stock_daily']:
        return '股票基础数据'
    elif table_name.startswith('technical_indicators'):
        return '技术指标'
    elif table_name.startswith('backtest_'):
        return '回测数据'
    elif table_name.startswith('user'):
        return '用户管理'
    elif table_name.startswith('sqlite_'):
        return '系统表'
    else:
        return '其他'

def get_table_description(table_name):
    """获取表的描述"""
    descriptions = {
        # 接口元数据表
        'akshare_interfaces': 'AKShare接口主表，包含所有接口的基本信息',
        'akshare_interface_params': '接口参数表，记录每个接口的参数信息',
        'akshare_interface_returns': '接口返回表，记录接口的返回字段信息',
        'akshare_interface_examples': '接口示例表，包含接口的使用示例',
        'akshare_interface_errors': '接口错误表，记录接口可能的错误信息',
        'akshare_interface_tags': '接口标签表，定义接口的分类标签',
        'akshare_interface_tag_relations': '接口标签关联表，关联接口和标签',
        'akshare_interface_stats': '接口统计表，记录接口的统计信息',
        
        # 股票基础数据
        'stock_info': '股票基础信息表，包含所有A股股票的基本信息',
        'stock_daily': '股票日线数据表，包含历史K线数据',
        'technical_indicators': '技术指标表，存储计算的技术指标数据',
        'backtest_results': '回测结果表，存储策略回测的结果',
        'trades': '交易记录表，存储回测中的交易明细',
        'users': '用户表，存储系统用户信息',
        'user_sessions': '用户会话表，存储用户登录会话',
        
        # AKShare股票数据
        'akshare_stock_balance_sheet_by_report_em': '资产负债表数据，包含A股公司资产负债信息',
        'akshare_stock_board_concept_name_em': '概念板块名称表，包含A股概念板块基本信息',
        'akshare_stock_board_industry_name_em': '行业板块名称表，包含A股行业板块基本信息',
        'akshare_stock_cash_flow_sheet_by_report_em': '现金流量表数据，包含A股公司现金流信息',
        'akshare_stock_financial_abstract': '财务摘要数据，包含A股公司核心财务指标',
        'akshare_stock_gdfx_free_top_10_em': '前十大流通股东数据，包含A股公司流通股东信息',
        'akshare_stock_gdfx_top_10_em': '前十大股东数据，包含A股公司股东信息',
        'akshare_stock_individual_fund_flow': '个股资金流向数据，包含A股个股资金流入流出',
        'akshare_stock_individual_fund_flow_rank': '个股资金排行数据，包含A股个股资金排名',
        'akshare_stock_individual_info_em': '个股基本信息表，包含A股个股详细资料',
        'akshare_stock_info_a_code_name': 'A股代码名称表，包含所有A股股票代码和名称',
        'akshare_stock_margin_detail_sse': '融资融券明细数据，包含上交所融资融券详细信息',
        'akshare_stock_margin_sse': '融资融券汇总数据，包含上交所融资融券统计',
        'akshare_stock_profit_sheet_by_report_em': '利润表数据，包含A股公司盈利信息',
        'akshare_stock_zh_a_daily': 'A股日线行情数据，包含A股个股历史K线',
        'akshare_stock_zh_a_spot': 'A股实时行情数据，包含A股个股最新价格',
        'akshare_stock_zh_index_daily': '指数日线数据，包含主要股票指数历史行情',
        
        # SQLite系统表
        'sqlite_sequence': 'SQLite序列号表，记录自增主键信息',
        'sqlite_stat1': 'SQLite统计信息表，用于查询优化'
    }
    
    # 为未定义的akshare表提供默认描述
    if table_name.startswith('akshare_') and table_name not in descriptions:
        # 从表名提取接口名
        interface_name = table_name.replace('akshare_', '')
        return f'AKShare接口数据：{interface_name} 相关数据'
    
    return descriptions.get(table_name, f'{table_name} 数据表')


@app.route('/long_term_stocks')
@login_required
def long_term_stocks():
    """长期存活股票分析页面"""
    return render_template('long_term_stocks.html')

@app.route('/api/long_term_analysis')
@login_required
def api_long_term_analysis():
    """获取长期存活股票分析数据"""
    try:
        # 导入长期存活分析器
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from dev_tools.long_term_survival_analysis import LongTermSurvivalAnalyzer
            analyzer = LongTermSurvivalAnalyzer()
            
            # 获取长期存活股票数据
            long_term_stocks = analyzer.get_long_term_survivors()
            
            # 转换为前端需要的格式
            stocks_data = []
            for stock in long_term_stocks:
                stocks_data.append({
                    'symbol': stock.get('symbol', ''),
                    'name': stock.get('name', ''),
                    'industry': stock.get('industry', ''),
                    'survival_years': stock.get('survival_years', 0),
                    'quality_score': stock.get('quality_score', 0),
                    'category': stock.get('category', '未知')
                })
            
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'stocks': stocks_data,
                    'summary': {
                        'total': len(stocks_data),
                        'twenty_year_plus': len([s for s in stocks_data if s['survival_years'] >= 20]),
                        'fifteen_year_plus': len([s for s in stocks_data if 15 <= s['survival_years'] < 20]),
                        'ten_year_plus': len([s for s in stocks_data if 10 <= s['survival_years'] < 15])
                    }
                }
            })
            
        except ImportError:
            # 如果分析器不可用，返回演示数据
            demo_data = [
                {'symbol': '000001', 'name': '平安银行', 'industry': '银行', 'survival_years': 34, 'quality_score': 95, 'category': '20年+'},
                {'symbol': '000002', 'name': '万科A', 'industry': '房地产', 'survival_years': 34, 'quality_score': 92, 'category': '20年+'},
                {'symbol': '600036', 'name': '招商银行', 'industry': '银行', 'survival_years': 34, 'quality_score': 98, 'category': '20年+'},
                {'symbol': '000858', 'name': '五粮液', 'industry': '白酒', 'survival_years': 27, 'quality_score': 96, 'category': '20年+'},
                {'symbol': '600519', 'name': '贵州茅台', 'industry': '白酒', 'survival_years': 24, 'quality_score': 100, 'category': '20年+'},
                {'symbol': '000651', 'name': '格力电器', 'industry': '家电', 'survival_years': 29, 'quality_score': 94, 'category': '20年+'},
                {'symbol': '000333', 'name': '美的集团', 'industry': '家电', 'survival_years': 32, 'quality_score': 93, 'category': '20年+'},
                {'symbol': '601318', 'name': '中国平安', 'industry': '保险', 'survival_years': 18, 'quality_score': 97, 'category': '15-20年'},
                {'symbol': '600031', 'name': '三一重工', 'industry': '工程机械', 'survival_years': 22, 'quality_score': 85, 'category': '20年+'},
                {'symbol': '600276', 'name': '恒瑞医药', 'industry': '医药', 'survival_years': 25, 'quality_score': 90, 'category': '20年+'}
            ]
            
            return jsonify({
                'code': 200,
                'message': '获取成功（演示数据）',
                'data': {
                    'stocks': demo_data,
                    'summary': {
                        'total': len(demo_data),
                        'twenty_year_plus': len([s for s in demo_data if s['survival_years'] >= 20]),
                        'fifteen_year_plus': len([s for s in demo_data if 15 <= s['survival_years'] < 20]),
                        'ten_year_plus': len([s for s in demo_data if 10 <= s['survival_years'] < 15])
                    }
                }
            })
            
    except Exception as e:
        logger.error(f"获取长期存活股票分析数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500

# 全局变量用于进度跟踪
analysis_progress = {}

# ================================
# 价值投资分析API接口
# ================================

@app.route('/api/value_analysis/progress/<session_id>')
@require_login
def get_analysis_progress(session_id):
    """获取分析进度"""
    progress = analysis_progress.get(session_id, {})
    return jsonify({
        'code': 200,
        'data': progress
    })

@app.route('/api/value_analysis/top_stocks')
@require_login
def get_top_value_stocks():
    """获取价值投资分析结果"""
    import os  # 确保在函数作用域内导入os
    import uuid
    
    session_id = str(uuid.uuid4())
    
    try:
        limit_str = request.args.get('limit', '10')
        min_score = request.args.get('min_score', 0, type=int)
        industry_filter = request.args.get('industry', '')  # 新增行业筛选参数
        
        # 处理"all"选项和数字限制
        if str(limit_str).lower() == 'all':
            limit = None  # 不限制数量
        else:
            limit = int(limit_str)
            limit = min(max(limit, 1), 1000)  # 放宽限制到1000
        
        # 初始化进度
        analysis_progress[session_id] = {
            'status': 'starting',
            'current': 0,
            'total': 0,
            'percent': 0,
            'message': '正在获取股票列表...'
        }
        
        # 导入简化版价值投资分析器
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from simple_value_analyzer import SimpleValueAnalyzer
            
            analyzer = SimpleValueAnalyzer()
            
            # 获取股票数据并分析
            if limit is None:
                stock_limit = None  # 获取全部股票
            else:
                stock_limit = limit * 3  # 获取更多股票用于筛选
            stocks_df = analyzer.get_all_stocks(stock_limit)  # 获取股票数据
            
            if stocks_df.empty:
                analysis_progress[session_id]['status'] = 'error'
                analysis_progress[session_id]['message'] = '无法获取股票数据'
                return jsonify({
                    'code': 404,
                    'message': '无法获取股票数据',
                    'session_id': session_id
                })
            
            # 过滤股票
            if industry_filter:
                stocks_df = stocks_df[stocks_df['industry'] == industry_filter]
            
            total_stocks = len(stocks_df)
            analysis_progress[session_id]['total'] = total_stocks
            analysis_progress[session_id]['message'] = f'开始分析 {total_stocks} 只股票...'
            
            qualified_stocks = []
            current = 0
            
            for _, stock in stocks_df.iterrows():
                try:
                    current += 1
                    symbol = stock.get('symbol', '未知')
                    
                    # 更新进度
                    analysis_progress[session_id]['current'] = current
                    analysis_progress[session_id]['percent'] = int((current / total_stocks) * 100)
                    analysis_progress[session_id]['message'] = f'正在分析 {symbol}... ({current}/{total_stocks})'
                    
                    result = analyzer.analyze_stock(stock.to_dict())
                    
                    if result.get('qualified', False) and 'error' not in result:
                        qualified_stocks.append(result)
                        
                except Exception as e:
                    logger.error(f"分析股票失败 {stock.get('symbol', '未知')}: {e}")
                    continue
            
            # 完成分析
            analysis_progress[session_id]['status'] = 'completed'
            analysis_progress[session_id]['percent'] = 100
            analysis_progress[session_id]['message'] = '分析完成'
            
            # 按得分排序并应用最小评分过滤
            qualified_stocks = [s for s in qualified_stocks if s.get('score', 0) >= min_score]
            qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
            
            # 应用数量限制
            if limit:
                qualified_stocks = qualified_stocks[:limit]
            
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': qualified_stocks,
                'session_id': session_id
            })
            
        except ImportError:
            # 使用现有的分析结果文件
            import pandas as pd
            import glob
            import os
            
            # 查找最新的推荐文件
            reports_dir = 'reports'
            pattern = 'simple_recommendations_*.csv'
            files = glob.glob(os.path.join(reports_dir, pattern))
            
            if files:
                # 使用最新的分析结果
                latest_file = max(files, key=os.path.getctime)
                df = pd.read_csv(latest_file)
                
                # 转换为API格式
                stocks = []
                for _, row in df.iterrows():
                    # 处理CSV列名映射
                    stock_data = {
                        'symbol': str(row['股票代码']).zfill(6),  # 补零到6位
                        'name': str(row['股票名称']),
                        'industry': str(row.get('行业', '未分类')),
                        'score': int(row['得分']),
                        'score_percent': float(str(row['得分百分比']).replace('%', '')),
                        'recommendation': str(row['推荐等级']),
                        'risk_level': str(row['风险等级']),
                        'key_metrics': {
                            '市值': str(row['市值']),
                            'PE': float(row['PE']),
                            'PB': float(row['PB']),
                            '收盘价': float(row['PE'])  # 使用PE值作为示例
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 15, 'passed': True}
                        }
                    }
                    stocks.append(stock_data)
                
                # 应用最小评分过滤并排序
                stocks = [s for s in stocks if s.get('score', 0) >= min_score]
                stocks.sort(key=lambda x: x['score'], reverse=True)
                
                # 应用数量限制
                if limit:
                    stocks = stocks[:limit]
                
                return jsonify({
                    'code': 200,
                    'message': '获取成功',
                    'data': stocks,
                    'session_id': session_id
                })
            else:
                # 如果没有现有文件，使用扩展的演示数据
                analysis_progress[session_id]['status'] = 'completed'
                analysis_progress[session_id]['percent'] = 100
                analysis_progress[session_id]['message'] = '分析完成(使用演示数据)'
                demo_data = [
                    {
                        'symbol': '000001',
                        'name': '平安银行',
                        'industry': '银行',
                        'score': 85,
                        'score_percent': 85.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '84.0亿',
                            'PE': 6.0,
                            'PB': 3.5,
                            '收盘价': 43.0
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '000002',
                        'name': '万科A',
                        'industry': '房地产',
                        'score': 82,
                        'score_percent': 82.0,
                        'recommendation': '推荐',
                        'risk_level': '中低风险',
                        'key_metrics': {
                            '市值': '156.0亿',
                            'PE': 8.5,
                            'PB': 1.2,
                            '收盘价': 15.8
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '000858',
                        'name': '五粮液',
                        'industry': '白酒',
                        'score': 90,
                        'score_percent': 90.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '245.0亿',
                            'PE': 18.5,
                            'PB': 4.2,
                            '收盘价': 178.5
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '600519',
                        'name': '贵州茅台',
                        'industry': '白酒',
                        'score': 95,
                        'score_percent': 95.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '890.0亿',
                            'PE': 25.8,
                            'PB': 8.5,
                            '收盘价': 1685.0
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '601398',
                        'name': '工商银行',
                        'industry': '银行',
                        'score': 88,
                        'score_percent': 88.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '456.0亿',
                            'PE': 5.2,
                            'PB': 0.8,
                            '收盘价': 5.85
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '600036',
                        'name': '招商银行',
                        'industry': '银行',
                        'score': 92,
                        'score_percent': 92.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '298.0亿',
                            'PE': 7.8,
                            'PB': 1.25,
                            '收盘价': 42.5
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '000066',
                        'name': '中国长城',
                        'industry': '计算机',
                        'score': 78,
                        'score_percent': 78.0,
                        'recommendation': '推荐',
                        'risk_level': '中低风险',
                        'key_metrics': {
                            '市值': '45.0亿',
                            'PE': 12.0,
                            'PB': 2.8,
                            '收盘价': 15.5
                        },
                        'checks': {
                            '市值': {'score': 15, 'passed': True},
                            '估值': {'score': 25, 'passed': True},
                            '价格': {'score': 18, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 5, 'passed': True}
                        }
                    },
                    {
                        'symbol': '000333',
                        'name': '美的集团',
                        'industry': '家电',
                        'score': 87,
                        'score_percent': 87.0,
                        'recommendation': '强烈推荐',
                        'risk_level': '低风险',
                        'key_metrics': {
                            '市值': '189.0亿',
                            'PE': 12.5,
                            'PB': 2.8,
                            '收盘价': 65.8
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 30, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    },
                    {
                        'symbol': '600887',
                        'name': '伊利股份',
                        'industry': '食品饮料',
                        'score': 83,
                        'score_percent': 83.0,
                        'recommendation': '推荐',
                        'risk_level': '中低风险',
                        'key_metrics': {
                            '市值': '156.0亿',
                            'PE': 15.2,
                            'PB': 3.8,
                            '收盘价': 28.5
                        },
                        'checks': {
                            '市值': {'score': 20, 'passed': True},
                            '估值': {'score': 28, 'passed': True},
                            '价格': {'score': 20, 'passed': True},
                            '行业': {'score': 15, 'passed': True},
                            '流动性': {'score': 10, 'passed': True}
                        }
                    }
                ]
                
                # 应用最小评分过滤并排序
                demo_data = [s for s in demo_data if s.get('score', 0) >= min_score]
                
                # 应用数量限制
                if limit:
                    demo_data = demo_data[:limit]
                
                return jsonify({
                    'code': 200,
                    'message': '获取成功',
                    'data': demo_data,
                    'session_id': session_id
                })
                
    except Exception as e:
        logger.error(f"价值投资分析API错误: {e}")
        return jsonify({
            'code': 500,
            'message': '分析过程中发生错误',
            'session_id': session_id
        })
            
    except Exception as e:
        logger.error(f"获取价值投资分析结果失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取失败: {str(e)}'
        }), 500

@app.route('/api/value_analysis/quick_scan')
@require_login
def quick_value_scan():
    """快速价值投资扫描"""
    import os  # 确保在函数作用域内导入os
    
    try:
        # 导入简化版价值投资分析器
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            from simple_value_analyzer import SimpleValueAnalyzer
            
            analyzer = SimpleValueAnalyzer()
            
            # 获取所有股票进行快速扫描
            stocks_df = analyzer.get_all_stocks()
            
            if stocks_df.empty:
                return jsonify({
                    'code': 404,
                    'message': '无法获取股票数据'
                })
            
            qualified_stocks = []
            total_analyzed = 0
            
            for _, stock in stocks_df.iterrows():
                try:
                    result = analyzer.analyze_stock(stock.to_dict())
                    total_analyzed += 1
                    
                    if result.get('qualified', False) and 'error' not in result:
                        qualified_stocks.append(result)
                            
                except Exception as e:
                    continue
            
            # 按得分排序并取前20名用于快速展示
            qualified_stocks.sort(key=lambda x: x['score'], reverse=True)
            top_stocks = qualified_stocks[:20]
            
            return jsonify({
                'code': 200,
                'message': '扫描完成',
                'data': {
                    'total_analyzed': total_analyzed,
                    'qualified_count': len(qualified_stocks),
                    'qualified_rate': round(len(qualified_stocks) / total_analyzed * 100, 2) if total_analyzed > 0 else 0,
                    'top_stocks': top_stocks
                }
            })
            
        except ImportError:
            # 如果分析器不可用，返回演示数据
            return jsonify({
                'code': 200,
                'message': '扫描完成（演示数据）',
                'data': {
                    'total_analyzed': 100,
                    'qualified_count': 35,
                    'qualified_rate': 35.0,
                    'top_stocks': [
                        {
                            'symbol': '000001',
                            'name': '平安银行',
                            'industry': '银行',
                            'score': 85,
                            'score_percent': 85.0,
                            'recommendation': '强烈推荐',
                            'risk_level': '低风险'
                        },
                        {
                            'symbol': '000858',
                            'name': '五粮液',
                            'industry': '白酒',
                            'score': 82,
                            'score_percent': 82.0,
                            'recommendation': '推荐',
                            'risk_level': '中低风险'
                        }
                    ]
                }
            })
            
    except Exception as e:
        logger.error(f"快速价值投资扫描失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'扫描失败: {str(e)}'
        }), 500

@app.route('/api/akshare/interfaces/<interface_name>/data', methods=['GET'])
@login_required
def get_interface_data(interface_name):
    """获取接口数据的分页显示"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 创建表名
        table_name = f"akshare_{interface_name}"
        table_name = table_name.replace('-', '_').replace('.', '_')
        
        # 检查表是否存在
        check_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        table_exists = db_manager.query(check_query, [table_name])
        
        if not table_exists:
            return jsonify({
                'code': 404,
                'message': f'接口数据表不存在: {table_name}',
                'suggestion': '请先下载该接口的数据到数据库'
            }), 404
        
        # 获取总记录数
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        total_records = db_manager.query(count_query)[0]['count']
        
        if total_records == 0:
            return jsonify({
                'code': 200,
                'message': '数据为空',
                'data': {
                    'records': [],
                    'columns': [],
                    'total_records': 0,
                    'page': page,
                    'page_size': page_size,
                    'table_name': table_name
                }
            })
        
        # 获取列名
        columns_query = f"PRAGMA table_info({table_name})"
        columns_info = db_manager.query(columns_query)
        columns = [col['name'] for col in columns_info]
        
        # 计算分页偏移
        offset = (page - 1) * page_size
        
        # 获取分页数据
        data_query = f"""
            SELECT * FROM {table_name}
            LIMIT {page_size} OFFSET {offset}
        """
        records = db_manager.query(data_query)
        
        # 将记录转换为字典列表
        records_list = []
        for record in records:
            record_dict = {}
            for col in columns:
                value = record.get(col)
                # 处理日期时间格式
                if hasattr(value, 'strftime'):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                record_dict[col] = str(value) if value is not None else ''
            records_list.append(record_dict)
        
        return jsonify({
            'code': 200,
            'message': '获取数据成功',
            'data': {
                'records': records_list,
                'columns': columns,
                'total_records': total_records,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_records + page_size - 1) // page_size,
                'table_name': table_name
            }
        })
        
    except Exception as e:
        logger.error(f"获取接口数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取数据失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('static/charts', exist_ok=True)
    os.makedirs('static/reports', exist_ok=True)
    
    # 初始化用户数据
    logger.info("初始化用户系统...")
    user_manager.init_default_user()
    
    # 获取配置
    web_config = config.get_web_config()
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', True)
    
    logger.info(f"启动Web服务: http://{host}:{port}")
    logger.info("默认用户账号:")
    logger.info("  管理员: admin / admin123")
    logger.info("  演示用户: demo / demo123")
    
    app.run(host=host, port=port, debug=debug)