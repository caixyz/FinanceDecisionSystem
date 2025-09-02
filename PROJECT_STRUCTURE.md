# 项目目录结构说明

## 📁 根目录结构

```
FinanceDecisionSystem/
├── 📁 core/              # 核心模块
│   ├── analyzer.py       # 技术分析器
│   ├── backtest.py      # 回测引擎
│   ├── data_source.py   # 数据源
│   ├── storage.py       # 数据存储
│   └── visualization.py # 数据可视化
├── 📁 strategies/        # 交易策略
├── 📁 utils/            # 工具模块
├── 📁 templates/        # Web模板
├── 📁 static/           # 静态资源
├── 📁 data/             # 数据文件
├── 📁 logs/             # 日志文件
├── 📁 notebooks/        # Jupyter笔记本
├── 📁 tests/            # 测试文件
├── 📁 dev_tools/        # 开发工具
├── app.py               # Web应用入口
├── demo.py              # 演示脚本
└── requirements.txt     # 依赖列表
```

## 🧪 测试目录结构

```
tests/
├── unit/                # 单元测试
│   ├── test_basic.py           # 基础功能测试
│   ├── test_data_fetch.py      # 数据获取测试
│   ├── test_fixed_data_source.py  # 数据源修复测试
│   └── test_fixed_data_source_v2.py
├── integration/         # 集成测试
│   ├── test_web_api.py         # Web API测试
│   ├── test_web_annotations.py # Web标注测试
│   ├── test_chart_*.py         # 图表相关测试
│   ├── test_kline_extremes.py  # K线标注测试
│   ├── test_report_*.py        # 报告生成测试
│   └── test_akshare_direct.py  # AKShare直接测试
└── performance/         # 性能测试
    ├── test_backtest_fix.py    # 回测性能测试
    └── test_chinese_display_fix.py  # 中文显示性能测试
```

## 🛠️ 开发工具目录

```
dev_tools/
├── debug_akshare.py     # AKShare调试工具
├── debug_annotations.py # 标注功能调试
├── debug_chart.py       # 图表调试工具
├── verify_annotations.py # 标注验证工具
├── quick_test.py        # 快速测试
├── simple_test.py       # 简单测试
└── final_test.py        # 最终测试
```

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