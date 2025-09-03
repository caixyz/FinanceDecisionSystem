#!/usr/bin/env python3
"""
金融决策系统主应用
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
from functools import wraps
import os
import sys
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
    """获取股票列表（支持搜索）"""
    try:
        # 获取查询参数
        keyword = request.args.get('keyword', '')
        limit = request.args.get('limit', 100, type=int)
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 搜索股票
        stocks = synchronizer.search_stocks(keyword=keyword, limit=limit)
        
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'stocks': stocks,
                'total': len(stocks)
            }
        })
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'获取股票列表失败: {str(e)}'
        }), 500


@app.route('/api/stocks/<symbol>/data')
@login_required
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


# ================================
# 数据同步API（需要登录）
# ================================

@app.route('/api/stocks/sync/list', methods=['POST'])
@login_required
def sync_stock_list():
    """同步股票列表"""
    try:
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 同步股票列表
        count = synchronizer.sync_stock_list()
        
        return jsonify({
            'code': 200,
            'message': '股票列表同步成功',
            'data': {
                'synced_count': count
            }
        })
    except Exception as e:
        logger.error(f"同步股票列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步股票列表失败: {str(e)}'
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
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 同步历史数据
        result = synchronizer.sync_all_stock_daily_data(
            days=days, 
            batch_size=batch_size, 
            delay=delay
        )
        
        return jsonify({
            'code': 200,
            'message': '股票历史数据同步成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"同步股票历史数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步股票历史数据失败: {str(e)}'
        }), 500

@app.route('/api/stocks/sync/latest', methods=['POST'])
@login_required
def sync_stock_latest():
    """同步最新股票数据"""
    try:
        # 获取请求参数
        days = request.json.get('days', 30)
        batch_size = request.json.get('batch_size', 50)
        delay = request.json.get('delay', 1.0)
        
        # 创建同步管理器
        synchronizer = StockDataSynchronizer()
        
        # 同步最新数据
        result = synchronizer.sync_latest_stock_data(
            days=days, 
            batch_size=batch_size, 
            delay=delay
        )
        
        return jsonify({
            'code': 200,
            'message': '最新股票数据同步成功',
            'data': result
        })
    except Exception as e:
        logger.error(f"同步最新股票数据失败: {e}")
        return jsonify({
            'code': 500,
            'message': f'同步最新股票数据失败: {str(e)}'
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