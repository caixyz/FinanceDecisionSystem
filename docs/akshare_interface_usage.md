# AKShare接口数据库使用指南

## 🗄️ 数据库结构概览

### 核心表结构

| 表名 | 用途 | 关键字段 |
|---|---|---|
| `akshare_interfaces` | 接口主表 | 接口名称、分类、描述、数据源 |
| `akshare_interface_params` | 参数表 | 参数名、类型、是否必填、示例 |
| `akshare_interface_returns` | 返回字段表 | 字段名、类型、描述、单位 |
| `akshare_interface_examples` | 使用示例表 | 代码示例、预期输出 |
| `akshare_interface_errors` | 错误码表 | 错误码、解决方案 |
| `akshare_interface_stats` | 使用统计表 | 调用次数、成功率、响应时间 |

### 分类体系（三级分类）

#### 📊 一级分类
- **股票** - 股票相关数据
- **债券** - 债券、可转债等固定收益
- **基金** - 公募、私募、ETF等基金产品
- **期货** - 国内期货、外盘期货
- **期权** - 股票期权、商品期权
- **指数** - 各类指数数据
- **宏观经济** - GDP、CPI、PMI等
- **外汇** - 汇率、外币数据
- **商品** - 黄金、原油、农产品
- **另类数据** - 天气、环境、舆情等

#### 📈 二级分类示例（股票）
- **行情数据** - 实时、历史、K线
- **财务数据** - 报表、指标、分析
- **资金流向** - 主力、超大单、融资融券
- **股东数据** - 前十大股东、机构持股
- **基础信息** - 公司资料、行业分类

#### 🔍 三级分类示例（股票-行情数据）
- **历史K线** - 日K、周K、月K
- **实时行情** - 快照、分时
- **分钟数据** - 1分钟、5分钟、15分钟

## 🚀 快速开始

### 1. 初始化数据库

```python
from core.interface_manager import AKShareInterfaceManager

# 创建管理器实例
manager = AKShareInterfaceManager()

# 数据库将自动创建在项目 data/akshare_interface.db
```

### 2. 添加接口信息

```python
# 定义接口数据
interface_data = {
    'interface_name': 'stock_zh_a_hist',
    'interface_name_cn': 'A股历史行情数据',
    'interface_description': '获取A股个股历史K线数据',
    'category_level1': '股票',
    'category_level2': '行情数据', 
    'category_level3': '历史K线',
    'module_name': 'akshare.stock',
    'update_frequency': '日',
    'data_source': '东方财富',
    'params': [
        {
            'param_name': 'symbol',
            'param_name_cn': '股票代码',
            'param_type': 'str',
            'is_required': True,
            'description': '股票代码，如000001',
            'example_value': '000001'
        },
        {
            'param_name': 'period',
            'param_name_cn': '时间周期',
            'param_type': 'str',
            'is_required': False,
            'description': '数据周期',
            'example_value': 'daily',
            'default_value': 'daily'
        }
    ],
    'returns': [
        {
            'field_name': 'date',
            'field_name_cn': '日期',
            'field_type': 'datetime',
            'description': '交易日期',
            'example_value': '2023-01-01'
        },
        {
            'field_name': 'close',
            'field_name_cn': '收盘价',
            'field_type': 'float',
            'description': '当日收盘价',
            'unit': '元',
            'example_value': '10.50'
        }
    ]
}

# 添加接口
interface_id = manager.add_interface(interface_data)
print(f"接口已添加，ID: {interface_id}")
```

### 3. 查询接口信息

#### 按分类查询
```python
# 获取所有股票类接口
stock_interfaces = manager.get_interfaces_by_category(category1='股票')

# 获取股票-行情数据-历史K线接口
kline_interfaces = manager.get_interfaces_by_category(
    category1='股票', 
    category2='行情数据', 
    category3='历史K线'
)
```

#### 搜索接口
```python
# 搜索包含"历史"的接口
results = manager.search_interfaces('历史')

# 搜索包含特定股票代码的接口
results = manager.search_interfaces('000001')
```

#### 获取接口详情
```python
# 获取完整接口信息
detail = manager.get_interface_detail('stock_zh_a_hist')
print("接口基本信息:", detail['interface'])
print("参数列表:", detail['params'])
print("返回字段:", detail['returns'])
```

### 4. 分类结构查询

```python
# 获取完整的分类树形结构
categories = manager.get_categories()

# 打印分类结构
for cat1, cat2_dict in categories.items():
    print(f"📁 {cat1}")
    for cat2, cat3_list in cat2_dict.items():
        print(f"  └─ {cat2}: {len(cat3_list)}个三级分类")
```

### 5. 数据导出

```python
# 导出所有接口信息到Excel
manager.export_to_excel('akshare_interfaces_2025.xlsx')

# 导出将包含：
# - 接口列表（基本信息）
# - 接口参数（所有参数详情）
# - 返回字段（所有返回字段详情）
```

## 📋 使用场景示例

### 场景1：快速找到需要的接口
```python
# 需要获取贵州茅台的历史行情
keyword = "茅台"
results = manager.search_interfaces(keyword)
print(f"找到 {len(results)} 个相关接口")

# 按分类筛选
stock_kline = manager.get_interfaces_by_category(
    category1='股票', 
    category2='行情数据', 
    category3='历史K线'
)
```

### 场景2：接口参数验证
```python
# 获取接口参数信息
interface_detail = manager.get_interface_detail('stock_zh_a_hist')
params = interface_detail['params']

# 验证用户输入
for param in params:
    if param['is_required'] and not user_input.get(param['param_name']):
        print(f"缺少必填参数: {param['param_name_cn']} ({param['param_name']})")
```

### 场景3：数据源选择
```python
# 获取特定数据源的所有接口
df = manager.get_interfaces_by_category()
 eastmoney_interfaces = df[df['data_source'] == '东方财富']
```

## 🔧 数据库维护

### 更新接口状态
```python
# 标记接口为已弃用
manager.update_interface_status('old_interface', 'deprecated', '该接口已被新接口替代')

# 标记接口为错误状态
manager.update_interface_status('error_interface', 'error', '数据源暂时不可用')
```

### 批量导入接口
```python
# 从CSV批量导入
import pandas as pd

interfaces_df = pd.read_csv('akshare_stock_interfaces.csv')
for _, row in interfaces_df.iterrows():
    interface_data = {
        'interface_name': row['interface_name'],
        'interface_name_cn': row['interface_name_cn'],
        'category_level1': '股票',
        'category_level2': row['category_level2'],
        'category_level3': row['category_level3'],
        # ... 其他字段
    }
    manager.add_interface(interface_data)
```

## 📊 查询示例SQL

### 统计各类接口数量
```sql
SELECT 
    category_level1,
    category_level2,
    COUNT(*) as interface_count
FROM akshare_interfaces
WHERE status = 'active'
GROUP BY category_level1, category_level2
ORDER BY interface_count DESC;
```

### 查找免费接口
```sql
SELECT interface_name, interface_name_cn, data_source
FROM akshare_interfaces
WHERE is_free = 1 AND status = 'active'
ORDER BY category_level1, category_level2;
```

### 高频使用接口
```sql
SELECT i.interface_name, i.interface_name_cn, COUNT(s.id) as usage_count
FROM akshare_interfaces i
JOIN akshare_interface_stats s ON i.id = s.interface_id
WHERE s.create_date >= date('now', '-30 days')
GROUP BY i.id, i.interface_name, i.interface_name_cn
ORDER BY usage_count DESC
LIMIT 20;
```

## 🎯 最佳实践

1. **定期更新**：建议每月更新一次接口状态
2. **数据验证**：添加接口时验证参数和返回字段
3. **使用统计**：收集接口使用统计，优化常用接口
4. **错误处理**：建立错误码和解决方案库
5. **版本管理**：跟踪接口版本变化

## 📁 文件位置

- **数据库文件**: `data/akshare_interface.db`
- **表结构SQL**: `docs/akshare_interface_schema.sql`
- **管理器代码**: `core/interface_manager.py`
- **使用指南**: `docs/akshare_interface_usage.md`