#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKShare接口管理器
用于管理AKShare接口的元数据、参数、示例等信息
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import os

class AKShareInterfaceManager:
    """AKShare接口管理器"""
    
    def __init__(self, db_path: str = None):
        """初始化接口管理器
        
        Args:
            db_path: 数据库路径，默认为项目data目录
        """
        if db_path is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, 'data', 'akshare_interface.db')
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # 检查是否已初始化
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='akshare_interfaces'")
            if not cursor.fetchone():
                # 读取SQL文件并执行
                sql_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'docs', 'akshare_interface_schema.sql')
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                    conn.executescript(sql_content)
    
    def add_interface(self, interface_data: Dict[str, Any]) -> int:
        """添加接口信息
        
        Args:
            interface_data: 接口数据字典
            
        Returns:
            接口ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 插入接口基本信息
            sql = """
            INSERT INTO akshare_interfaces (
                interface_name, interface_name_cn, interface_description,
                category_level1, category_level2, category_level3, module_name,
                update_frequency, data_source, is_free, status, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(sql, (
                interface_data['interface_name'],
                interface_data.get('interface_name_cn', ''),
                interface_data.get('interface_description', ''),
                interface_data.get('category_level1', ''),
                interface_data.get('category_level2', ''),
                interface_data.get('category_level3', ''),
                interface_data.get('module_name', ''),
                interface_data.get('update_frequency', ''),
                interface_data.get('data_source', ''),
                interface_data.get('is_free', True),
                interface_data.get('status', 'active'),
                interface_data.get('version', '1.0')
            ))
            
            interface_id = cursor.lastrowid
            
            # 插入参数信息
            if 'params' in interface_data:
                for param in interface_data['params']:
                    self._add_param(conn, interface_id, param)
            
            # 插入返回字段信息
            if 'returns' in interface_data:
                for field in interface_data['returns']:
                    self._add_return_field(conn, interface_id, field)
            
            return interface_id
    
    def _add_param(self, conn: sqlite3.Connection, interface_id: int, param: Dict[str, Any]):
        """添加参数信息"""
        sql = """
        INSERT INTO akshare_interface_params (
            interface_id, param_name, param_name_cn, param_type,
            is_required, description, example_value, default_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(sql, (
            interface_id,
            param['param_name'],
            param.get('param_name_cn', ''),
            param.get('param_type', 'str'),
            param.get('is_required', True),
            param.get('description', ''),
            param.get('example_value', ''),
            param.get('default_value', '')
        ))
    
    def _add_return_field(self, conn: sqlite3.Connection, interface_id: int, field: Dict[str, Any]):
        """添加返回字段信息"""
        sql = """
        INSERT INTO akshare_interface_returns (
            interface_id, field_name, field_name_cn, field_type,
            description, unit, example_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        conn.execute(sql, (
            interface_id,
            field['field_name'],
            field.get('field_name_cn', ''),
            field.get('field_type', 'str'),
            field.get('description', ''),
            field.get('unit', ''),
            field.get('example_value', '')
        ))
    
    def get_interfaces_by_category(self, category1: str = None, category2: str = None, 
                                 category3: str = None) -> pd.DataFrame:
        """按分类获取接口列表
        
        Args:
            category1: 一级分类
            category2: 二级分类
            category3: 三级分类
            
        Returns:
            DataFrame格式的接口列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conditions = []
            params = []
            
            if category1:
                conditions.append("category_level1 = ?")
                params.append(category1)
            if category2:
                conditions.append("category_level2 = ?")
                params.append(category2)
            if category3:
                conditions.append("category_level3 = ?")
                params.append(category3)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            sql = f"""
            SELECT 
                interface_name, interface_name_cn, interface_description,
                category_level1, category_level2, category_level3,
                update_frequency, data_source, is_free, status
            FROM akshare_interfaces
            WHERE {where_clause}
            ORDER BY category_level1, category_level2, category_level3, interface_name
            """
            
            return pd.read_sql_query(sql, conn, params=params)
    
    def get_interface_detail(self, interface_name: str) -> Dict[str, Any]:
        """获取接口详细信息
        
        Args:
            interface_name: 接口名称
            
        Returns:
            包含接口详细信息的字典
        """
        with sqlite3.connect(self.db_path) as conn:
            # 获取接口基本信息
            interface_sql = """
            SELECT * FROM akshare_interfaces WHERE interface_name = ?
            """
            interface_df = pd.read_sql_query(interface_sql, conn, params=[interface_name])
            
            if interface_df.empty:
                return {}
            
            interface_info = interface_df.iloc[0].to_dict()
            
            # 获取参数信息
            params_sql = """
            SELECT * FROM akshare_interface_params WHERE interface_id = ?
            ORDER BY order_index, id
            """
            params_df = pd.read_sql_query(params_sql, conn, params=[interface_info['id']])
            
            # 获取返回字段信息
            returns_sql = """
            SELECT * FROM akshare_interface_returns WHERE interface_id = ?
            ORDER BY order_index, id
            """
            returns_df = pd.read_sql_query(returns_sql, conn, params=[interface_info['id']])
            
            return {
                'interface': interface_info,
                'params': params_df.to_dict('records'),
                'returns': returns_df.to_dict('records')
            }
    
    def search_interfaces(self, keyword: str) -> pd.DataFrame:
        """搜索接口
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            DataFrame格式的搜索结果
        """
        with sqlite3.connect(self.db_path) as conn:
            sql = """
            SELECT 
                interface_name, interface_name_cn, interface_description,
                category_level1, category_level2, category_level3,
                update_frequency, data_source
            FROM akshare_interfaces
            WHERE interface_name LIKE ? 
               OR interface_name_cn LIKE ?
               OR interface_description LIKE ?
            ORDER BY 
                CASE 
                    WHEN interface_name = ? THEN 1
                    WHEN interface_name LIKE ? THEN 2
                    WHEN interface_name_cn LIKE ? THEN 3
                    ELSE 4
                END,
                interface_name
            """
            like_keyword = f"%{keyword}%"
            exact_keyword = keyword
            
            return pd.read_sql_query(sql, conn, 
                                   params=[like_keyword, like_keyword, like_keyword,
                                          exact_keyword, f"{exact_keyword}%", like_keyword])
    
    def get_categories(self) -> Dict[str, List[str]]:
        """获取所有分类层级
        
        Returns:
            分类层级字典
        """
        with sqlite3.connect(self.db_path) as conn:
            sql = """
            SELECT DISTINCT category_level1, category_level2, category_level3
            FROM akshare_interfaces
            WHERE status = 'active'
            ORDER BY category_level1, category_level2, category_level3
            """
            
            df = pd.read_sql_query(sql, conn)
            
            categories = {}
            for _, row in df.iterrows():
                cat1 = row['category_level1']
                cat2 = row['category_level2']
                cat3 = row['category_level3']
                
                if cat1 not in categories:
                    categories[cat1] = {}
                
                if cat2 not in categories[cat1]:
                    categories[cat1][cat2] = []
                
                if cat3 and cat3 not in categories[cat1][cat2]:
                    categories[cat1][cat2].append(cat3)
            
            return categories
    
    def export_to_excel(self, filename: str = None):
        """导出接口信息到Excel文件
        
        Args:
            filename: 导出文件名
        """
        if filename is None:
            filename = f"akshare_interfaces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取接口基本信息
            interfaces_sql = """
            SELECT 
                interface_name as '接口名称',
                interface_name_cn as '中文名称',
                interface_description as '描述',
                category_level1 as '一级分类',
                category_level2 as '二级分类',
                category_level3 as '三级分类',
                module_name as '模块名',
                update_frequency as '更新频率',
                data_source as '数据源',
                CASE WHEN is_free = 1 THEN '免费' ELSE '收费' END as '是否免费',
                status as '状态',
                version as '版本',
                create_time as '创建时间'
            FROM akshare_interfaces
            ORDER BY category_level1, category_level2, category_level3, interface_name
            """
            
            interfaces_df = pd.read_sql_query(interfaces_sql, conn)
            
            # 获取参数信息
            params_sql = """
            SELECT 
                i.interface_name as '接口名称',
                p.param_name as '参数名',
                p.param_name_cn as '参数中文名',
                p.param_type as '参数类型',
                CASE WHEN p.is_required = 1 THEN '必填' ELSE '可选' END as '是否必填',
                p.description as '参数描述',
                p.example_value as '示例值',
                p.default_value as '默认值'
            FROM akshare_interface_params p
            JOIN akshare_interfaces i ON p.interface_id = i.id
            ORDER BY i.interface_name, p.order_index
            """
            
            params_df = pd.read_sql_query(params_sql, conn)
            
            # 获取返回字段信息
            returns_sql = """
            SELECT 
                i.interface_name as '接口名称',
                r.field_name as '字段名',
                r.field_name_cn as '字段中文名',
                r.field_type as '字段类型',
                r.description as '字段描述',
                r.unit as '单位',
                r.example_value as '示例值'
            FROM akshare_interface_returns r
            JOIN akshare_interfaces i ON r.interface_id = i.id
            ORDER BY i.interface_name, r.order_index
            """
            
            returns_df = pd.read_sql_query(returns_sql, conn)
            
            # 写入Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                interfaces_df.to_excel(writer, sheet_name='接口列表', index=False)
                params_df.to_excel(writer, sheet_name='接口参数', index=False)
                returns_df.to_excel(writer, sheet_name='返回字段', index=False)
    
    def update_interface_status(self, interface_name: str, status: str, remarks: str = None):
        """更新接口状态
        
        Args:
            interface_name: 接口名称
            status: 新状态
            remarks: 备注信息
        """
        with sqlite3.connect(self.db_path) as conn:
            sql = """
            UPDATE akshare_interfaces 
            SET status = ?, update_time = ?, remarks = COALESCE(?, remarks)
            WHERE interface_name = ?
            """
            conn.execute(sql, (status, datetime.now(), remarks, interface_name))

# 使用示例
if __name__ == "__main__":
    manager = AKShareInterfaceManager()
    
    # 示例：添加一个接口
    interface_data = {
        'interface_name': 'stock_zh_a_hist',
        'interface_name_cn': 'A股历史行情数据',
        'interface_description': '获取A股个股历史K线数据，包含开高低收量额等完整行情信息',
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
                'description': '数据周期，默认为daily',
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
                'field_name': 'open',
                'field_name_cn': '开盘价',
                'field_type': 'float',
                'description': '当日开盘价',
                'unit': '元',
                'example_value': '10.50'
            }
        ]
    }
    
    # manager.add_interface(interface_data)
    
    # 获取分类信息
    categories = manager.get_categories()
    print("接口分类结构：")
    for cat1, cat2_dict in categories.items():
        print(f"📁 {cat1}")
        for cat2, cat3_list in cat2_dict.items():
            print(f"  └─ {cat2}: {', '.join(cat3_list)}")
    
    # 导出到Excel
    # manager.export_to_excel()