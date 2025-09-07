-- AKShare接口管理数据库表设计
-- 创建时间: 2025-01-06
-- 用途: 存储和管理AKShare所有接口的详细信息

-- 接口主表：存储核心接口信息
CREATE TABLE akshare_interfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_name VARCHAR(100) NOT NULL UNIQUE,          -- 接口英文名称
    interface_name_cn VARCHAR(200),                        -- 接口中文名称
    interface_description TEXT,                           -- 接口详细中文描述
    category_level1 VARCHAR(50),                        -- 一级分类（股票/债券/基金/期货/指数/宏观/外汇/商品/另类）
    category_level2 VARCHAR(50),                        -- 二级分类（如股票下分：行情/财务/资金/股东等）
    category_level3 VARCHAR(50),                        -- 三级分类（如行情下分：历史/实时/K线等）
    module_name VARCHAR(50),                             -- 所属模块（akshare中的子模块）
    function_type VARCHAR(20),                          -- 函数类型（function/class/method）
    source_url TEXT,                                    -- 数据源网址
    official_doc_url TEXT,                             -- 官方文档链接
    update_frequency VARCHAR(20),                      -- 更新频率（实时/日/周/月）
    data_source VARCHAR(50),                            -- 数据来源（新浪/东财/网易/交易所等）
    is_free BOOLEAN DEFAULT 1,                          -- 是否免费
    need_cookie BOOLEAN DEFAULT 0,                    -- 是否需要cookie
    need_proxy BOOLEAN DEFAULT 0,                      -- 是否需要代理
    rate_limit VARCHAR(50),                             -- 频率限制说明
    status VARCHAR(20) DEFAULT 'active',               -- 接口状态（active/deprecated/error）
    version VARCHAR(20),                               -- 接口版本
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,    -- 记录创建时间
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,    -- 记录更新时间
    last_check_time DATETIME,                          -- 最后检查时间
    remarks TEXT                                        -- 备注信息
);

-- 接口参数表：存储接口的输入参数信息
CREATE TABLE akshare_interface_params (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id INTEGER NOT NULL,                     -- 关联接口ID
    param_name VARCHAR(50) NOT NULL,                   -- 参数名称
    param_name_cn VARCHAR(100),                        -- 参数中文名称
    param_type VARCHAR(20),                            -- 参数类型（str/int/float/list/datetime）
    is_required BOOLEAN DEFAULT 1,                     -- 是否必填
    default_value TEXT,                                -- 默认值
    description TEXT,                                  -- 参数描述
    example_value TEXT,                                -- 示例值
    value_range TEXT,                                  -- 取值范围
    value_format VARCHAR(100),                          -- 格式说明
    constraint_check TEXT,                             -- 约束检查
    order_index INTEGER,                               -- 参数顺序
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE
);

-- 接口返回字段表：存储接口的输出字段信息
CREATE TABLE akshare_interface_returns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id INTEGER NOT NULL,                     -- 关联接口ID
    field_name VARCHAR(50) NOT NULL,                   -- 字段名称
    field_name_cn VARCHAR(100),                        -- 字段中文名称
    field_type VARCHAR(20),                            -- 字段类型
    description TEXT,                                  -- 字段描述
    unit VARCHAR(20),                                  -- 单位
    is_nullable BOOLEAN DEFAULT 1,                    -- 是否可空
    example_value TEXT,                                -- 示例值
    format_pattern VARCHAR(100),                        -- 格式模式
    enum_values TEXT,                                  -- 枚举值（如果有）
    order_index INTEGER,                               -- 字段顺序
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE
);

-- 接口使用示例表：存储接口的调用示例
CREATE TABLE akshare_interface_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id INTEGER NOT NULL,                     -- 关联接口ID
    example_type VARCHAR(20),                          -- 示例类型（basic/advanced/error）
    title VARCHAR(200),                                -- 示例标题
    description TEXT,                                  -- 示例描述
    code_example TEXT,                                 -- 代码示例
    expected_output TEXT,                              -- 预期输出
    actual_output TEXT,                                -- 实际输出（用于验证）
    run_result_status VARCHAR(20),                     -- 运行状态（success/error）
    run_time DATETIME,                                 -- 运行时间
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE
);

-- 接口错误码表：存储接口可能的错误信息
CREATE TABLE akshare_interface_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id INTEGER,                              -- 关联接口ID（可为空，通用错误）
    error_code VARCHAR(20),                            -- 错误码
    error_message TEXT,                                -- 错误描述
    error_type VARCHAR(50),                            -- 错误类型（网络/参数/权限/数据）
    solution TEXT,                                     -- 解决方案
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE
);

-- 接口标签表：用于灵活分类和标记
CREATE TABLE akshare_interface_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name VARCHAR(50) NOT NULL UNIQUE,              -- 标签名称
    tag_color VARCHAR(7),                             -- 标签颜色（十六进制）
    description TEXT,                                  -- 标签描述
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 接口与标签关联表
CREATE TABLE akshare_interface_tag_relations (
    interface_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (interface_id, tag_id),
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES akshare_interface_tags(id) ON DELETE CASCADE
);

-- 接口使用统计表：记录接口调用情况
CREATE TABLE akshare_interface_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interface_id INTEGER NOT NULL,                     -- 接口ID
    call_count INTEGER DEFAULT 0,                      -- 调用次数
    success_count INTEGER DEFAULT 0,                   -- 成功次数
    error_count INTEGER DEFAULT 0,                     -- 失败次数
    avg_response_time REAL,                            -- 平均响应时间（秒）
    last_call_time DATETIME,                           -- 最后调用时间
    create_date DATE DEFAULT CURRENT_DATE,             -- 统计日期
    FOREIGN KEY (interface_id) REFERENCES akshare_interfaces(id) ON DELETE CASCADE
);

-- 创建索引优化查询性能
CREATE INDEX idx_interfaces_category ON akshare_interfaces(category_level1, category_level2, category_level3);
CREATE INDEX idx_interfaces_name ON akshare_interfaces(interface_name);
CREATE INDEX idx_interfaces_status ON akshare_interfaces(status);
CREATE INDEX idx_params_interface ON akshare_interface_params(interface_id);
CREATE INDEX idx_returns_interface ON akshare_interface_returns(interface_id);
CREATE INDEX idx_examples_interface ON akshare_interface_examples(interface_id);
CREATE INDEX idx_stats_interface ON akshare_interface_stats(interface_id);
CREATE INDEX idx_stats_date ON akshare_interface_stats(create_date);

-- 插入示例数据
INSERT INTO akshare_interfaces (
    interface_name, interface_name_cn, interface_description, 
    category_level1, category_level2, category_level3, module_name,
    update_frequency, data_source, is_free, status, version
) VALUES 
('stock_zh_a_hist', 'A股历史行情数据', '获取A股个股历史K线数据，包含开高低收量额等完整行情信息', 
 '股票', '行情数据', '历史K线', 'akshare.stock', '日', '东方财富', 1, 'active', '1.0'),
('stock_individual_info_em', '个股基本信息', '获取个股基本信息，包括行业、市值、流通股、上市时间等', 
 '股票', '基础信息', '个股信息', 'akshare.stock', '日', '东方财富', 1, 'active', '1.0'),
('bond_cb_jsl', '可转债实时行情', '获取集思录可转债实时行情数据，包括价格、溢价率、转股价等', 
 '债券', '可转债', '实时行情', 'akshare.bond', '实时', '集思录', 1, 'active', '1.0'),
('fund_em_open_fund_daily', '开放式基金净值', '获取开放式公募基金每日净值数据', 
 '基金', '公募基金', '净值数据', 'akshare.fund', '日', '东方财富', 1, 'active', '1.0'),
('macro_china_cpi', '中国CPI数据', '获取中国居民消费价格指数(CPI)月度数据', 
 '宏观经济', '价格指数', 'CPI', 'akshare.macro', '月', '国家统计局', 1, 'active', '1.0');

-- 插入示例参数
INSERT INTO akshare_interface_params (interface_id, param_name, param_name_cn, param_type, is_required, description, example_value) VALUES
(1, 'symbol', '股票代码', 'str', 1, '股票代码，如000001', '000001'),
(1, 'period', '时间周期', 'str', 0, '数据周期，默认为daily', 'daily'),
(1, 'start_date', '开始日期', 'str', 0, '开始日期，格式YYYY-MM-DD', '2023-01-01'),
(1, 'end_date', '结束日期', 'str', 0, '结束日期，格式YYYY-MM-DD', '2023-12-31'),
(2, 'symbol', '股票代码', 'str', 1, '股票代码，如000001', '000001');

-- 插入示例返回字段
INSERT INTO akshare_interface_returns (interface_id, field_name, field_name_cn, field_type, description, unit) VALUES
(1, 'date', '日期', 'datetime', '交易日期', ''),
(1, 'open', '开盘价', 'float', '当日开盘价', '元'),
(1, 'high', '最高价', 'float', '当日最高价', '元'),
(1, 'low', '最低价', 'float', '当日最低价', '元'),
(1, 'close', '收盘价', 'float', '当日收盘价', '元'),
(1, 'volume', '成交量', 'int', '当日成交量', '手'),
(1, 'amount', '成交额', 'float', '当日成交额', '元');

-- 插入示例标签
INSERT INTO akshare_interface_tags (tag_name, tag_color, description) VALUES
('高频使用', '#FF6B6B', '常用接口'),
('实时数据', '#4ECDC4', '提供实时数据'),
('历史数据', '#45B7D1', '提供历史数据'),
('免费接口', '#96CEB4', '完全免费的接口'),
('官方推荐', '#FECA57', '官方推荐使用的接口');

-- 创建视图：接口完整信息视图
CREATE VIEW v_interface_detail AS
SELECT 
    i.id,
    i.interface_name,
    i.interface_name_cn,
    i.interface_description,
    i.category_level1,
    i.category_level2,
    i.category_level3,
    CONCAT(i.category_level1, ' > ', i.category_level2, ' > ', i.category_level3) as full_category,
    i.module_name,
    i.update_frequency,
    i.data_source,
    i.is_free,
    i.status,
    i.version,
    i.create_time,
    i.update_time,
    COUNT(p.id) as param_count,
    COUNT(r.id) as return_field_count
FROM akshare_interfaces i
LEFT JOIN akshare_interface_params p ON i.id = p.interface_id
LEFT JOIN akshare_interface_returns r ON i.id = r.interface_id
GROUP BY i.id, i.interface_name, i.interface_name_cn, i.interface_description,
         i.category_level1, i.category_level2, i.category_level3, i.module_name,
         i.update_frequency, i.data_source, i.is_free, i.status, i.version,
         i.create_time, i.update_time;