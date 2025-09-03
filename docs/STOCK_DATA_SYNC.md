# 股票数据同步功能使用说明

## 🎯 功能概述

股票数据同步功能允许您从AKShare获取股票数据并存储到本地数据库中，包括：

1. **股票列表同步** - 获取所有A股股票的基本信息
2. **历史数据同步** - 获取股票的历史价格数据
3. **最新数据同步** - 增量更新最新的股票数据
4. **股票搜索** - 在数据库中搜索股票

## 🏗️ 系统架构

```
股票数据同步管理器 (StockDataSynchronizer)
├── 数据源接口 (DataSource) - 基于AKShare
├── 数据库存储 (DatabaseManager) - SQLite
└── 技术分析器 (TechnicalAnalyzer) - 技术指标计算
```

## 🚀 快速开始

### 1. 通过Web界面使用

登录系统后，在主页的"股票数据管理"区域可以：

- **搜索股票** - 输入关键词搜索股票代码或名称
- **同步股票列表** - 更新所有股票的基本信息
- **同步历史数据** - 获取所有股票的历史价格数据
- **同步最新数据** - 增量更新最新的股票数据

### 2. 通过开发工具使用

在 `dev_tools/` 目录下有以下脚本：

```bash
# 同步股票列表
python dev_tools/sync_stock_list.py

# 测试股票数据同步功能
python dev_tools/test_stock_sync.py

# 同步所有股票数据
python dev_tools/sync_all_stock_data.py
```

## 📊 API接口

### 股票搜索
```
GET /api/stocks/list?keyword=平安&limit=10
```

### 同步股票列表
```
POST /api/stocks/sync/list
```

### 同步历史数据
```
POST /api/stocks/sync/history
{
  "days": 365,
  "batch_size": 50,
  "delay": 1.0
}
```

### 同步最新数据
```
POST /api/stocks/sync/latest
{
  "days": 30,
  "batch_size": 50,
  "delay": 1.0
}
```

## 🛠️ 核心类说明

### StockDataSynchronizer (股票数据同步管理器)

#### 主要方法:

1. **sync_stock_list()** - 同步股票列表
   - 从AKShare获取所有A股股票列表
   - 保存到stock_info表

2. **sync_all_stock_daily_data()** - 同步所有股票历史数据
   - 参数:
     - `days`: 获取最近多少天的数据
     - `batch_size`: 批处理大小
     - `delay`: 请求间隔(秒)

3. **sync_latest_stock_data()** - 同步最新数据
   - 增量更新最新股票数据
   - 只获取数据库中缺失的数据

4. **search_stocks()** - 搜索股票
   - 支持关键词、行业等条件搜索

## 🗃️ 数据库结构

### stock_info (股票基础信息表)
```sql
CREATE TABLE stock_info (
    symbol TEXT PRIMARY KEY,     -- 股票代码
    name TEXT,                   -- 股票名称
    industry TEXT,               -- 所属行业
    market_cap REAL,             -- 总市值
    pe_ratio REAL,               -- 市盈率
    pb_ratio REAL,               -- 市净率
    updated_at TIMESTAMP         -- 更新时间
);
```

### stock_daily (股票日线数据表)
```sql
CREATE TABLE stock_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,                 -- 股票代码
    date DATE,                   -- 交易日期
    open REAL,                   -- 开盘价
    high REAL,                   -- 最高价
    low REAL,                    -- 最低价
    close REAL,                  -- 收盘价
    volume BIGINT,               -- 成交量
    turnover REAL,               -- 成交额
    created_at TIMESTAMP         -- 创建时间
);
```

## ⚙️ 配置说明

在 `config.yml` 中可以配置:

```yaml
DATA_SOURCE:
  primary: akshare
  retry_times: 3      # 请求失败重试次数
  timeout: 30         # 请求超时时间(秒)

STOCK:
  default_period: daily
  max_history_days: 1000
```

## 🔄 同步策略

### 批量处理
- 为了避免AKShare API限流，采用批量处理方式
- 默认每批次处理50只股票
- 每次请求间隔0.5-1秒

### 增量更新
- `sync_latest_stock_data()` 方法只同步最新的数据
- 通过检查数据库中最新日期来确定需要获取的数据范围

### 错误处理
- 自动重试机制，失败后会重试3次
- 单只股票同步失败不会影响其他股票
- 详细日志记录便于问题排查

## 📈 使用示例

### Python代码示例
```python
from core.stock_sync import StockDataSynchronizer

# 创建同步管理器
synchronizer = StockDataSynchronizer()

# 同步股票列表
count = synchronizer.sync_stock_list()
print(f"同步了 {count} 只股票")

# 同步历史数据
result = synchronizer.sync_all_stock_daily_data(days=365)
print(f"同步结果: {result}")

# 搜索股票
stocks = synchronizer.search_stocks(keyword="银行", limit=10)
for stock in stocks:
    print(f"{stock['symbol']} - {stock['name']}")
```

## 🧪 测试验证

### 验证股票列表同步
```bash
python dev_tools/sync_stock_list.py
```

### 验证数据同步功能
```bash
python dev_tools/test_stock_sync.py
```

## 📊 数据统计

系统会自动记录以下统计信息：
- 同步股票数量
- 成功/失败数量
- 同步时间范围
- 数据质量指标

## ⚠️ 注意事项

1. **API限流** - AKShare有请求频率限制，请合理设置delay参数
2. **数据量大** - A股有数千只股票，首次同步需要较长时间
3. **网络稳定性** - 确保网络连接稳定，避免同步中断
4. **存储空间** - 历史数据会占用较多磁盘空间
5. **定时同步** - 建议设置定时任务定期同步最新数据

## 🛠️ 维护建议

1. **定期同步** - 建议每天同步一次最新数据
2. **监控日志** - 定期检查同步日志，发现问题及时处理
3. **备份数据** - 定期备份数据库文件
4. **性能优化** - 根据实际需求调整批处理大小和延迟时间

## 🆘 故障排除

### 同步失败
1. 检查网络连接是否正常
2. 查看日志文件获取详细错误信息
3. 调整请求间隔避免API限流
4. 确认AKShare库是否正常工作

### 数据不完整
1. 检查数据库存储空间
2. 确认同步参数设置是否正确
3. 重新运行同步任务

### 搜索无结果
1. 确认关键词是否正确
2. 检查数据库中是否有相关数据
3. 验证数据库连接是否正常