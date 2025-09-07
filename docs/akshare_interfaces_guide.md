# AKShare接口中文指南

## 📋 简介

本指南为AKShare接口提供了详细的中文描述和使用说明，帮助用户快速理解和使用各类金融数据接口。

## 📊 数据分类

### 1. 股票数据 (Stock Data)

**文件**: `akshare_stock_interfaces_with_chinese.csv`

包含26个核心股票接口，覆盖：
- **基础信息**: 股票代码对照表、个股基本信息
- **行情数据**: 历史K线、实时行情、日线数据
- **资金流向**: 个股资金流向、市场资金流向、资金排行
- **财务数据**: 财务报表、分析指标、三大会计报表
- **股东数据**: 前十大股东、前十大流通股东
- **融资融券**: 两融明细、两融汇总数据
- **板块数据**: 行业板块、概念板块历史数据
- **估值指标**: 市盈率、市净率、估值分析

### 2. 市场数据 (Market Data)

**文件**: `akshare_market_interfaces_with_chinese.csv`

包含多类市场数据接口：

#### 🏛️ 债券数据
- **可转债**: 实时行情、强赎信息、比价表、发行信息
- **国债**: 收益率曲线、收盘收益率
- **企业债**: 发行信息、市场数据
- **指数**: 中债综合指数、债券指数

#### 💰 基金数据
- **公募基金**: 基本信息、净值数据、排行榜
- **ETF**: ETF基金净值、持仓明细
- **货币基金**: 万份收益、7日年化收益率
- **基金持仓**: 基金持仓明细、基金经理信息

#### 📈 指数数据
- **成分股**: 各大指数成分股列表
- **历史行情**: 指数历史K线数据
- **基本信息**: 指数基本信息列表

#### 🏛️ 宏观经济
- **价格指数**: CPI、PPI、GDP
- **货币数据**: 货币供应量、利率数据
- **贸易数据**: 进出口、贸易差额
- **利率**: SHIBOR、LPR利率

#### ⚖️ 期货期权
- **期货**: 国内期货、外盘期货、期货库存
- **期权**: 沪深300期权、上证50ETF期权

### 3. 完整接口列表

**文件**: `akshare_interfaces.csv`

包含5239个完整接口，涵盖：
- 股票、债券、基金、期货、期权
- 外汇、黄金、原油等大宗商品
- 宏观经济数据
- 另类数据（天气、环境等）

## 🚀 使用建议

### 快速开始
1. **股票分析**: 从 `akshare_stock_interfaces_with_chinese.csv` 开始
2. **市场研究**: 参考 `akshare_market_interfaces_with_chinese.csv`
3. **深度挖掘**: 使用 `akshare_interfaces.csv` 探索更多接口

### 常用组合
- **个股分析**: stock_individual_info_em + stock_zh_a_hist + stock_financial_analysis_indicator
- **行业研究**: stock_board_industry_name_em + stock_board_industry_hist_em
- **可转债策略**: bond_cb_jsl + bond_cb_redeem_jsl + bond_cov_comparison

## 📁 文件位置

所有接口文档位于项目 `docs/` 目录：
- `akshare_stock_interfaces_with_chinese.csv` - 股票接口中文描述
- `akshare_market_interfaces_with_chinese.csv` - 市场数据接口中文描述
- `akshare_interfaces.csv` - 完整接口列表
- `akshare_interfaces_guide.md` - 本指南文档

## 💡 注意事项

1. **数据频率**: 不同接口数据更新频率不同，注意实时性要求
2. **调用限制**: 部分接口有访问频率限制，建议添加延迟
3. **数据质量**: 使用前请验证数据完整性和准确性
4. **接口变更**: AKShare会定期更新接口，建议关注官方文档

## 🔗 相关资源

- [AKShare官方文档](https://www.akshare.xyz/)
- [项目GitHub](https://github.com/akfamily/akshare)
- 项目测试文件: `test_api.py`、`test_simple.py`