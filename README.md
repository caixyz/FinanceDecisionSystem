# 🏦 金融决策系统 (Finance Decision System)

基于 AKShare 的智能股票分析和策略回测平台，支持K线图高低点标注功能

[![GitHub](https://img.shields.io/badge/GitHub-caixyz-blue)](https://github.com/caixyz/FinanceDecisionSystem)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📋 项目简介

金融决策系统是一个功能完整的股票分析平台，集成了数据获取、技术分析、策略回测、可视化和Web界面等功能。系统基于AKShare数据源，提供实时和历史的股票数据分析服务。

## 🎆 最新特性

### 🎨 K线图高低点标注功能
- **全局标注**: 红色标记全局最高点，绿色标记全局最低点
- **局部标注**: 橙色标记局部高点，青色标记局部低点
- **灵活选择**: 用户可在Web界面中选择标注模式
- **价格显示**: 标注中包含具体价格数值

### 🛠️ 技术改进
- **多线程安全**: 解决matplotlib在Web环境下的线程安全问题
- **中文支持**: 智能中文字体检测，支持多种字体备选
- **错误处理**: 完善的异常处理和日志记录
- **内存管理**: 自动垃圾回收和资源清理

### 🔧 Web界面功能
- **标注模式选择**: 
  - 全局最高低点：标注整个时间段的绝对极值
  - 局部最高低点：标注多个局部转折点
  - 不标注：保持图表简洁
- **实时切换**: 无需刷新页面即可切换标注模式
- **响应式设计**: 适配不同屏幕尺寸

### 📊 使用示例

在Web界面中：
1. 输入股票代码（如：000858）
2. 选择分析天数（30-252天）
3. 在"高低点标注"下拉菜单中选择标注模式
4. 点击"生成图表"查看带标注的K线图

API调用示例：
```bash
# 获取带全局标注的K线图
curl "http://localhost:5000/api/stocks/000858/chart?mark_extremes=global&days=90"

# 获取带局部标注的K线图  
curl "http://localhost:5000/api/stocks/000858/chart?mark_extremes=local&days=60"
```

## ✨ 主要功能

### 📊 数据获取
- **多数据源支持**: 基于AKShare获取A股、港股、美股等市场数据
- **实时数据**: 股票实时价格、成交量等信息
- **历史数据**: 日线、周线、月线等不同周期数据
- **基本面数据**: 财务指标、公司信息等

### 📈 技术分析
- **技术指标**: MA、EMA、MACD、RSI、布林带、KDJ、ATR等30+指标
- **信号生成**: 自动生成买入/卖出交易信号
- **趋势识别**: 智能判断股票趋势方向
- **支撑阻力**: 自动识别关键价位

### 🔄 策略回测
- **多策略支持**: 移动平均线、RSI、MACD、布林带、综合策略等
- **性能评估**: 收益率、夏普比率、最大回撤、胜率等指标
- **风险控制**: 仓位管理、止损止盈设置
- **组合回测**: 支持多股票组合策略测试

### 📊 数据可视化
- **K线图表**: 专业的蜡烛图展示，支持高低点标注
- **智能标注**: 全局和局部高低点自动识别与标注
- **技术指标图**: 多指标叠加显示
- **交互图表**: 基于Plotly的动态图表
- **分析报告**: 自动生成HTML格式报告
- **中文支持**: 完善的中文字体显示

### 🌐 Web界面
- **直观界面**: 现代化的Web用户界面
- **实时分析**: 在线股票分析和回测
- **图表展示**: 内置图表查看器
- **API接口**: RESTful API支持

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/macOS

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/caixyz/FinanceDecisionSystem.git
cd FinanceDecisionSystem
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **创建目录结构**
```bash
python setup_dirs.py
```

4. **运行演示**
```bash
python demo.py
```

5. **启动Web服务**
```bash
python app.py
```

然后在浏览器打开 `http://localhost:5000`

## 📝 项目结构

```
FinanceDecisionSystem/
├── core/                   # 核心模块
│   ├── data_source.py     # 数据获取模块
│   ├── analyzer.py        # 技术分析模块
│   ├── backtest.py        # 回测框架
│   ├── storage.py         # 数据存储模块
│   └── visualization.py   # 可视化模块(支持K线图标注)
├── strategies/             # 交易策略
│   └── example_strategies.py
├── utils/                  # 工具模块
│   ├── config.py          # 配置管理
│   └── logger.py          # 日志管理
├── templates/              # Web模板
│   └── index.html         # 支持标注功能的主页
├── static/                 # 静态文件
│   ├── charts/            # 图表文件
│   └── reports/           # 报告文件
├── tests/                  # 测试文件(已重新组织)
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── performance/       # 性能测试
├── dev_tools/              # 开发工具
│   ├── debug_*.py         # 调试工具
│   └── verify_*.py        # 验证工具
├── data/                   # 数据文件
│   └── temp/              # 临时数据
├── logs/                   # 日志文件
├── notebooks/              # Jupyter笔记本
├── app.py                  # Web应用入口
├── app_safe.py             # 线程安全版本(支持标注)
├── demo.py                 # 演示脚本
├── config.yml              # 配置文件
├── requirements.txt        # 依赖列表
└── PROJECT_STRUCTURE.md    # 项目结构说明
```

> 📝 **详细结构说明**: 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 了解完整的项目结构和组织原则

## 🛠️ 使用示例

### 数据获取
```python
from core.data_source import DataSource

# 初始化数据源
data_source = DataSource()

# 获取股票列表
stock_list = data_source.get_stock_list()

# 获取股票历史数据
stock_data = data_source.get_stock_data("000001", days=90)
```

### 技术分析
```python
from core.analyzer import TechnicalAnalyzer

# 初始化分析器
analyzer = TechnicalAnalyzer()

# 计算技术指标
data_with_indicators = analyzer.calculate_all_indicators(stock_data)

# 综合分析
analysis = analyzer.analyze_stock("000001", stock_data)
```

### 策略回测
```python
from core.backtest import BacktestEngine, MAStrategy

# 初始化回测引擎
backtest_engine = BacktestEngine(initial_capital=1000000)

# 创建策略
strategy = MAStrategy(short_period=5, long_period=20)

# 运行回测
results = backtest_engine.run_backtest(strategy, stock_data, "000001")
```

### 可视化和K线图标注
```python
from core.visualization import ChartPlotter

# 初始化图表绘制器
plotter = ChartPlotter()

# 生成基本K线图
chart_path = plotter.plot_candlestick_chart(stock_data, "000001")

# 生成带全局最高低点标注的K线图
chart_path = plotter.plot_candlestick_chart(
    stock_data, 
    "000001",
    mark_extremes='global'  # 全局标注
)

# 生成带局部高低点标注的K线图
chart_path = plotter.plot_candlestick_chart(
    stock_data, 
    "000001",
    mark_extremes='local'   # 局部标注
)

# 生成技术指标图
indicators_path = plotter.plot_technical_indicators(stock_data, "000001")
```

## 🎯 API接口

### 股票数据
- `GET /api/stocks/list` - 获取股票列表
- `GET /api/stocks/{symbol}/data` - 获取股票历史数据
- `GET /api/stocks/{symbol}/analysis` - 分析股票
- `GET /api/stocks/{symbol}/chart?mark_extremes={mode}` - 生成股票图表
  - `mark_extremes`: 标注模式 (`global`|全局, `local`|局部, `none`|无)

### 策略回测
- `POST /api/backtest/run` - 运行策略回测
- `GET /api/strategies/list` - 获取策略列表

### 报告生成
- `POST /api/reports/generate` - 生成分析报告

### 市场数据
- `GET /api/market/sentiment` - 获取市场情绪

## 🔧 配置说明

主要配置在 `config.yml` 文件中：

```yaml
# 数据库配置
DATABASE:
  type: sqlite
  path: data/finance_data.db

# 数据源配置
DATA_SOURCE:
  primary: akshare
  update_interval: 300
  retry_times: 3

# 回测配置
BACKTEST:
  initial_capital: 1000000
  commission_rate: 0.0003

# Web服务配置
WEB:
  host: 0.0.0.0
  port: 5000
  debug: false
```

## 📊 内置策略

### 1. 移动平均线策略 (MA Strategy)
- **原理**: 基于短期和长期移动平均线的金叉死叉
- **参数**: 短期周期(默认5)、长期周期(默认20)
- **信号**: 金叉买入，死叉卖出

### 2. RSI策略 (RSI Strategy) 
- **原理**: 基于相对强弱指标的超买超卖
- **参数**: RSI周期(默认14)、超买线(默认70)、超卖线(默认30)
- **信号**: RSI<30买入，RSI>70卖出

### 3. MACD策略 (MACD Strategy)
- **原理**: 基于MACD指标的金叉死叉
- **参数**: 快线(默认12)、慢线(默认26)、信号线(默认9)
- **信号**: MACD金叉买入，死叉卖出

### 4. 布林带策略 (Bollinger Bands Strategy)
- **原理**: 基于布林带的均值回归
- **参数**: 周期(默认20)、标准差倍数(默认2)
- **信号**: 价格突破下轨买入，突破上轨卖出

### 5. 综合策略 (Composite Strategy)
- **原理**: 多个技术指标综合判断
- **指标**: RSI、MACD、布林带、移动平均线
- **信号**: 多重确认机制

## 📈 性能指标

系统计算以下回测性能指标：

- **收益率指标**
  - 总收益率
  - 年化收益率
  - 月度收益率

- **风险指标**
  - 最大回撤
  - 夏普比率
  - 波动率
  - VaR (Value at Risk)

- **交易指标**
  - 交易次数
  - 胜率
  - 盈亏比
  - 平均持仓天数

## 🛡️ 风险提示

⚠️ **重要声明**: 
- 本系统仅供学习和研究使用
- 所有分析结果仅供参考，不构成投资建议
- 股市有风险，投资需谨慎
- 历史表现不代表未来收益

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 🧪 测试

项目包含完整的测试套件：

```bash
# 运行所有测试
python -m pytest tests/

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 快速测试K线标注功能
python dev_tools/quick_test.py

# 验证标注功能
python dev_tools/verify_annotations.py
```

## 📚 文档

- 📝 [K线图标注功能说明](K线图标注功能说明.md)
- 📁 [项目结构说明](PROJECT_STRUCTURE.md)
- ⚙️ [API接口文档](#-api接口)
- 🛠️ [配置说明](#-配置说明)## 📝 开发计划 ✅ K线图高低点标注功能
- [x] ✅ 项目目录结构重构
- [x] ✅ matplotlib多线程安全优化
- [x] ✅ 中文字体智能检测
- [ ] 增加更多技术指标
- [ ] 支持期货、期权数据
- [ ] 机器学习策略
- [ ] 实时交易接口
- [ ] 移动端应用
- [ ] 云端部署支持

## 📜 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 🌐 项目主页: https://github.com/caixyz/FinanceDecisionSystem
- 📝 问题反馈: https://github.com/caixyz/FinanceDecisionSystem/issues
- 📧 邮箱: 3352624214@qq.com
- 👨‍💻 作者: caixyz

## 🙏 致谢

- [AKShare](https://github.com/akfamily/akshare) - 提供优秀的金融数据接口
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Pandas](https://pandas.pydata.org/) - 数据处理
- [Matplotlib](https://matplotlib.org/) - 数据可视化
- [Plotly](https://plotly.com/) - 交互式图表

---

⭐ 如果这个项目对您有帮助，请给它一个Star！