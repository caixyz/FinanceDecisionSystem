# 项目目录结构说明

## 📁 根目录结构（整理后）

```
FinanceDecisionSystem/
├── app.py                      # 主应用程序入口
├── public_stock_view.py        # 公开股票查看服务
├── requirements.txt            # Python依赖列表
├── .gitignore                  # Git忽略文件
├── .env.example               # 环境变量示例
├── PROJECT_STRUCTURE.md       # 项目结构文档（本文件）
├── README.md                  # 项目说明文档
├── DATABASE_SCHEMA.md         # 数据库架构文档
├── FINAL_REPORT.md            # 最终报告文档

├── core/                      # 核心模块
│   ├── __init__.py
│   ├── database.py           # 数据库管理
│   ├── cache.py              # 缓存管理
│   ├── user.py               # 用户管理
│   ├── stock_data.py         # 股票数据源
│   ├── technical_analysis.py # 技术分析
│   └── backtest.py           # 回测引擎

├── api/                       # API接口
│   ├── __init__.py
│   ├── routes.py             # 路由定义
│   └── handlers/             # 请求处理器
│       ├── __init__.py
│       ├── auth.py           # 认证处理
│       ├── stocks.py         # 股票API
│       └── backtest.py       # 回测API

├── templates/                 # 网页模板
│   ├── base.html             # 基础模板
│   ├── index.html            # 主页
│   ├── login.html            # 登录页
│   ├── register.html         # 注册页
│   ├── stock_management.html # 股票管理
│   ├── public_stocks.html    # 公开股票查看
│   └── backtest.html         # 回测页面

├── static/                    # 静态资源
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── main.js
│   │   ├── stock.js
│   │   └── backtest.js
│   └── images/
│       └── logo.png

├── data/                      # 数据文件
│   ├── database/             # 数据库文件
│   │   └── finance_system.db
│   ├── cache/                # 缓存数据
│   ├── backups/              # 数据备份
│   ├── temp/                 # 临时数据
│   └── exports/              # 导出数据

├── tests/                     # 测试文件（已整理）
│   ├── __init__.py
│   ├── test_api.py          # API测试
│   ├── test_database.py     # 数据库测试
│   ├── test_analysis.py     # 分析测试
│   ├── unit/                # 单元测试（已保留）
│   ├── integration/         # 集成测试（已保留）
│   ├── performance/         # 性能测试（已保留）
│   └── temp_files/          # 临时测试文件（已整理）
│       ├── check_*.py
│       ├── test_*.py
│       ├── verify_*.py
│       ├── debug_*.py
│       └── fix_*.py

├── dev_tools/                 # 开发工具
│   ├── database_setup.py     # 数据库初始化
│   ├── data_importer.py      # 数据导入工具
│   ├── backup_restore.py     # 备份恢复工具
│   ├── debug_*.py            # 调试工具（已保留）
│   ├── verify_*.py          # 验证工具（已保留）
│   └── quick_test.py        # 快速测试

├── docs/                      # 文档目录
│   ├── API.md               # API文档
│   ├── USER_GUIDE.md        # 用户指南
│   └── DEVELOPMENT.md       # 开发文档

└── logs/                      # 日志文件
    ├── app.log              # 应用日志
    ├── error.log            # 错误日志
    └── access.log           # 访问日志
```

## 🚀 服务启动说明

### 主应用服务
- 启动命令: `python app.py`
- 访问地址: http://localhost:5000
- 功能: 完整的股票管理和回测系统
- 演示账号: admin/admin123, demo/demo123

### 公开股票查看服务
- 启动命令: `python public_stock_view.py`
- 访问地址: http://localhost:5001
- 功能: 无需登录的股票查看页面

## 🎯 主要功能模块

1. **股票管理**: 添加、删除、查看股票信息
2. **技术分析**: 提供多种技术指标分析
3. **回测系统**: 策略回测和性能评估
4. **用户管理**: 注册、登录、权限管理
5. **数据管理**: 股票数据获取和存储
6. **公开查看**: 无需登录的股票信息浏览

## 🗄️ 数据库结构

主要表格:
- users: 用户信息
- stock_info: 股票基本信息（包含close字段）
- stock_prices: 股票价格历史
- backtest_results: 回测结果
- user_stocks: 用户关注的股票

## ✅ 最近更新

- ✅ 添加收盘价(close)字段到股票信息表
- ✅ 更新公开API以包含收盘价信息
- ✅ 更新主应用模板显示收盘价
- ✅ 整理项目文件结构
- ✅ 优化代码组织

## 📊 数据目录结构

```
data/
├── temp/                # 临时数据
│   └── temp_akshare_data.csv
├── cache/               # 缓存数据
└── exports/             # 导出数据
```

## 🎯 目录整理原则

1. **功能分离**: 按功能模块组织代码
2. **测试分类**: 单元测试、集成测试、性能测试分离
3. **工具独立**: 开发调试工具单独存放
4. **数据管理**: 临时数据、缓存、导出数据分类存储
5. **文档清晰**: 每个目录都有明确的用途说明

## 🚀 使用指南

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 运行性能测试
python -m pytest tests/performance/
```

### 开发调试
```bash
# 快速测试K线标注功能
python dev_tools/quick_test.py

# 验证标注功能
python dev_tools/verify_annotations.py

# 调试AKShare数据
python dev_tools/debug_akshare.py
```

### 启动应用
```bash
# 启动Web应用
python app.py

# 启动安全版应用
python app_safe.py

# 运行演示
python demo.py
```