#!/usr/bin/env python3
"""
获取AKShare所有可用接口列表
"""
import akshare as ak
import pandas as pd
import inspect
from typing import Dict, List

def get_akshare_interfaces():
    """获取AKShare所有接口信息"""
    print("=== 获取AKShare所有接口信息 ===")
    
    try:
        # 获取akshare模块的所有属性
        all_attrs = dir(ak)
        
        # 过滤出函数和类
        interfaces = []
        
        for attr_name in all_attrs:
            if not attr_name.startswith('_'):  # 忽略私有属性
                try:
                    attr = getattr(ak, attr_name)
                    if callable(attr):
                        # 获取函数签名
                        try:
                            sig = inspect.signature(attr)
                            params = list(sig.parameters.keys())
                        except:
                            params = []
                        
                        # 获取文档字符串
                        doc = inspect.getdoc(attr) or "无文档"
                        
                        interfaces.append({
                            'name': attr_name,
                            'type': 'function',
                            'parameters': params,
                            'description': doc[:200] + '...' if len(doc) > 200 else doc
                        })
                except Exception as e:
                    continue
        
        return interfaces
    except Exception as e:
        print(f"获取接口失败: {e}")
        return []

def get_stock_market_interfaces():
    """获取股票相关接口"""
    print("\n=== 股票相关接口 ===")
    
    stock_interfaces = [
        # 股票基本信息
        'stock_info_a_code_name',  # A股代码和名称
        'stock_individual_info_em',  # 个股信息
        'stock_individual_fund_flow',  # 个股资金流向
        
        # 股票历史数据
        'stock_zh_a_hist',  # A股历史行情
        'stock_zh_a_spot',  # A股实时行情
        'stock_zh_a_daily',  # A股日线数据
        
        # 指数数据
        'stock_zh_index_daily',  # 指数日线数据
        'stock_zh_index_spot',  # 指数实时行情
        
        # 板块数据
        'stock_board_industry_name_em',  # 行业板块
        'stock_board_concept_name_em',  # 概念板块
        'stock_board_industry_hist_em',  # 行业板块历史
        
        # 财务数据
        'stock_financial_abstract',  # 财务摘要
        'stock_financial_analysis_indicator',  # 财务指标
        'stock_balance_sheet_by_report_em',  # 资产负债表
        'stock_profit_sheet_by_report_em',  # 利润表
        'stock_cash_flow_sheet_by_report_em',  # 现金流量表
        
        # 估值数据
        'stock_a_pe',  # A股市盈率
        'stock_a_pb',  # A股市净率
        'stock_a_lg_indicator',  # A股技术指标
        
        # 资金流向
        'stock_individual_fund_flow_rank',  # 个股资金流向排名
        'stock_market_fund_flow',  # 市场资金流向
        
        # 股东数据
        'stock_gdfx_free_top_10_em',  # 十大流通股东
        'stock_gdfx_top_10_em',  # 十大股东
        
        # 融资融券
        'stock_margin_detail_sse',  # 融资融券明细
        'stock_margin_sse',  # 融资融券汇总
    ]
    
    return stock_interfaces

def get_market_data_interfaces():
    """获取市场数据接口"""
    print("\n=== 市场数据接口 ===")
    
    market_interfaces = [
        # 期货数据
        'futures_zh_daily_sina',  # 期货历史数据
        'futures_spot_price_daily',  # 期货现货价格
        
        # 基金数据
        'fund_em_fund_name',  # 基金列表
        'fund_em_open_fund_daily',  # 开放式基金净值
        'fund_em_etf_fund_daily',  # ETF基金净值
        
        # 债券数据
        'bond_zh_cov',  # 可转债数据
        'bond_zh_hs_daily',  # 债券历史数据
        
        # 外汇数据
        'fx_pair_quote',  # 外汇行情
        
        # 黄金数据
        'futures_glob_sina',  # 全球期货
    ]
    
    return market_interfaces

def save_interfaces_to_file():
    """保存接口信息到文件"""
    print("\n=== 保存接口信息到文件 ===")
    
    try:
        # 获取所有接口
        all_interfaces = get_akshare_interfaces()
        stock_interfaces = get_stock_market_interfaces()
        market_interfaces = get_market_data_interfaces()
        
        # 创建DataFrame
        if all_interfaces:
            df = pd.DataFrame(all_interfaces)
            
            # 保存到CSV
            csv_path = 'docs/akshare_interfaces.csv'
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"✅ 接口信息已保存到: {csv_path}")
            
            # 保存股票相关接口
            stock_df = pd.DataFrame({
                '接口名称': stock_interfaces,
                '类型': '股票相关'
            })
            stock_df.to_csv('docs/akshare_stock_interfaces.csv', index=False, encoding='utf-8-sig')
            
            # 保存市场数据接口
            market_df = pd.DataFrame({
                '接口名称': market_interfaces,
                '类型': '市场数据'
            })
            market_df.to_csv('docs/akshare_market_interfaces.csv', index=False, encoding='utf-8-sig')
            
            # 打印总结
            print(f"\n📊 接口统计:")
            print(f"   总接口数: {len(all_interfaces)}")
            print(f"   股票接口: {len(stock_interfaces)}")
            print(f"   市场接口: {len(market_interfaces)}")
            
            # 打印前20个接口
            if len(all_interfaces) > 0:
                print(f"\n🔍 前20个接口示例:")
                for i, interface in enumerate(all_interfaces[:20]):
                    print(f"   {i+1}. {interface['name']} - {interface['description'][:50]}...")
            
            return True
        else:
            print("❌ 未能获取接口信息")
            return False
            
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False

def main():
    """主函数"""
    print("AKShare接口获取工具")
    print("=" * 50)
    
    try:
        # 测试AKShare是否可用
        print("测试AKShare连接...")
        ak_version = ak.__version__
        print(f"✅ AKShare版本: {ak_version}")
        
        # 保存接口信息
        success = save_interfaces_to_file()
        
        if success:
            print("\n🎉 接口信息获取完成！")
            print("\n生成的文件:")
            print("   docs/akshare_interfaces.csv - 所有接口")
            print("   docs/akshare_stock_interfaces.csv - 股票相关接口")
            print("   docs/akshare_market_interfaces.csv - 市场数据接口")
        else:
            print("\n❌ 接口获取失败")
            
    except ImportError:
        print("❌ 未安装AKShare，请先安装: pip install akshare")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()