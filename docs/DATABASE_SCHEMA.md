# 📊 金融决策系统数据库结构文档

## 📋 概述
本文档详细描述了金融决策系统的数据库结构，包含所有数据表的字段定义、数据类型、约束条件及业务说明。

## 🗂️ 数据库表清单

| 表名 | 数据条数 | 主要用途 | 最后更新 |
|------|----------|----------|----------|
| [stock_info](#stock_info-股票基本信息表) | 5,744条 | 股票基础信息 | 实时更新 |
| [stock_daily](#stock_daily-股票日线数据表) | 大量数据 | 历史K线数据 | 每日更新 |
| [technical_indicators](#technical_indicators-技术指标表) | 技术指标 | 技术分析数据 | 每日计算 |
| [backtest_results](#backtest_results-回测结果表) | 回测记录 | 策略回测结果 | 策略运行后 |
| [trades](#trades-交易记录表) | 交易记录 | 模拟交易明细 | 交易执行后 |
| [users](#users-用户表) | 2条 | 系统用户管理 | 用户注册时 |
| [user_sessions](#user_sessions-用户会话表) | 14条 | 登录会话管理 | 登录时创建 |

---

## 📈 股票相关表

### `stock_info` - 股票基本信息表
**用途**: 存储所有股票的基础信息，包括行业分类、财务指标等

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **symbol** | TEXT | PRIMARY KEY | 股票代码，唯一标识 | "000001" |
| **name** | TEXT | - | 股票名称 | "平安银行" |
| **industry** | TEXT | - | 所属行业分类 | "银行" |
| **market_cap** | REAL | - | 总市值（元） | 2,847,503,400,000 |
| **pe_ratio** | REAL | - | 市盈率 | 6.78 |
| **pb_ratio** | REAL | - | 市净率 | 0.89 |
| **close** | REAL | - | 最新收盘价（元） | 14.65 |
| **updated_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 最后更新时间 | 2024-01-15 15:30:00 |

**数据示例**:
```
symbol: 000001, name: 平安银行, industry: 银行, market_cap: 2847503400000.00, pe_ratio: 6.78, pb_ratio: 0.89, close: 14.65
```

---

### `stock_daily` - 股票日线数据表
**用途**: 存储股票历史日线行情数据

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **symbol** | TEXT | - | 股票代码 | "000001" |
| **date** | DATE | - | 交易日期 | 2024-01-15 |
| **open** | REAL | - | 开盘价（元） | 14.50 |
| **high** | REAL | - | 最高价（元） | 14.80 |
| **low** | REAL | - | 最低价（元） | 14.30 |
| **close** | REAL | - | 收盘价（元） | 14.65 |
| **volume** | INTEGER | - | 成交量（股） | 45,678,900 |
| **amount** | REAL | - | 成交额（元） | 668,456,135 |

---

### `technical_indicators` - 技术指标表
**用途**: 存储股票的技术分析指标数据

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **symbol** | TEXT | - | 股票代码 | "000001" |
| **date** | DATE | - | 指标日期 | 2024-01-15 |
| **ma5** | REAL | - | 5日均线 | 14.52 |
| **ma10** | REAL | - | 10日均线 | 14.48 |
| **ma20** | REAL | - | 20日均线 | 14.35 |
| **rsi** | REAL | - | RSI相对强弱指标 | 65.23 |
| **macd** | REAL | - | MACD指标 | 0.45 |
| **kdj_k** | REAL | - | KDJ-K值 | 78.90 |
| **kdj_d** | REAL | - | KDJ-D值 | 72.34 |
| **kdj_j** | REAL | - | KDJ-J值 | 91.12 |

---

## 🎯 回测相关表

### `backtest_results` - 回测结果表
**用途**: 存储策略回测的完整结果和性能指标

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **id** | INTEGER | PRIMARY KEY | 回测记录ID | 1 |
| **strategy_name** | TEXT | - | 策略名称 | "MA交叉策略" |
| **start_date** | DATE | - | 回测开始日期 | 2023-01-01 |
| **end_date** | DATE | - | 回测结束日期 | 2023-12-31 |
| **initial_capital** | REAL | - | 初始资金（元） | 100,000 |
| **final_capital** | REAL | - | 最终资金（元） | 125,000 |
| **total_return** | REAL | - | 总收益率（%） | 25.0 |
| **annual_return** | REAL | - | 年化收益率（%） | 25.0 |
| **max_drawdown** | REAL | - | 最大回撤（%） | -8.5 |
| **win_rate** | REAL | - | 胜率（%） | 65.2 |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2024-01-15 16:00:00 |

---

### `trades` - 交易记录表
**用途**: 存储回测过程中的详细交易记录

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **id** | INTEGER | PRIMARY KEY | 交易记录ID | 1 |
| **backtest_id** | INTEGER | - | 关联回测ID | 1 |
| **symbol** | TEXT | - | 股票代码 | "000001" |
| **trade_date** | DATE | - | 交易日期 | 2024-01-15 |
| **action** | TEXT | - | 操作类型 | "BUY" / "SELL" |
| **price** | REAL | - | 成交价格（元） | 14.65 |
| **quantity** | INTEGER | - | 成交数量（股） | 1000 |
| **amount** | REAL | - | 成交金额（元） | 14,650 |
| **commission** | REAL | - | 手续费（元） | 14.65 |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2024-01-15 14:30:00 |

---

## 👤 用户管理表

### `users` - 用户表
**用途**: 存储系统用户账户信息

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **id** | INTEGER | PRIMARY KEY | 用户ID | 1 |
| **username** | TEXT | NOT NULL | 用户名 | "admin" |
| **password_hash** | TEXT | NOT NULL | 密码哈希 | "pbkdf2:sha256:260000..." |
| **email** | TEXT | - | 邮箱地址 | "admin@example.com" |
| **real_name** | TEXT | - | 真实姓名 | "管理员" |
| **role** | TEXT | - | 用户角色 | "admin" / "user" |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2024-01-01 00:00:00 |
| **last_login** | TIMESTAMP | - | 最后登录时间 | 2024-01-15 15:30:00 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 是否激活 | true |

**当前用户**:
- 管理员: admin/admin123
- 演示用户: demo/demo123

---

### `user_sessions` - 用户会话表
**用途**: 管理用户登录会话和令牌

| 字段名 | 数据类型 | 约束 | 说明 | 示例 |
|--------|----------|------|------|------|
| **id** | INTEGER | PRIMARY KEY | 会话ID | 1 |
| **user_id** | INTEGER | - | 关联用户ID | 1 |
| **session_token** | TEXT | NOT NULL | 会话令牌 | "a1b2c3d4e5f6..." |
| **created_at** | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 | 2024-01-15 15:30:00 |
| **expires_at** | TIMESTAMP | - | 过期时间 | 2024-01-16 15:30:00 |
| **is_active** | BOOLEAN | DEFAULT TRUE | 是否激活 | true |

---

## 🔄 数据更新策略

### 实时更新
- **stock_info**: 实时更新股票基本信息
- **updated_at**: 自动记录最后更新时间

### 每日更新
- **stock_daily**: 每日收盘后更新日线数据
- **technical_indicators**: 每日计算技术指标

### 事件驱动更新
- **backtest_results**: 策略回测完成后生成
- **trades**: 回测过程中实时记录交易
- **user_sessions**: 用户登录时创建，退出时失效

---

## 📋 数据质量说明

### ✅ 已修复数据
- **行业分类**: 5,744只股票的行业数据已从垃圾数据修复为真实行业分类
- **股票代码**: 保持唯一性和准确性
- **财务指标**: 定期从可靠数据源同步更新

### 🎯 数据完整性
- **主键约束**: symbol字段在stock_info表中作为主键
- **时间戳**: 所有表都包含created_at或updated_at字段
- **默认值**: 时间字段默认使用CURRENT_TIMESTAMP

### 📊 数据规模
- **股票数量**: 5,744只A股股票
- **历史数据**: 包含完整的日线历史数据
- **技术指标**: 支持多种技术分析指标

---

## 🚀 使用指南

### 查询示例
```sql
-- 查看特定行业的股票
SELECT symbol, name, market_cap, pe_ratio 
FROM stock_info 
WHERE industry = '银行' 
ORDER BY market_cap DESC;

-- 查看股票最新价格
SELECT symbol, name, close, updated_at 
FROM stock_info 
WHERE symbol = '000001';

-- 查看回测结果
SELECT strategy_name, total_return, max_drawdown, win_rate
FROM backtest_results
ORDER BY created_at DESC;
```

### API端点
- **股票列表**: GET `/api/stocks/list`
- **股票详情**: GET `/api/stocks/<symbol>`
- **回测结果**: GET `/api/backtest/results`
- **用户登录**: POST `/api/auth/login`

---

**最后更新**: 2024年1月15日
**数据库文件**: `data/finance_data.db`