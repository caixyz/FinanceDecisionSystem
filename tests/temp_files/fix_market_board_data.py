#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复上证主板/深证主板等市场板块数据
将市场板块数据替换为真实的行业分类
"""
import sqlite3
import pandas as pd

def fix_market_board_to_industry():
    """将市场板块数据修复为真实行业分类"""
    
    # 正确的行业映射
    industry_mapping = {
        # 银行类
        '601398': '银行',      # 工商银行
        '600036': '银行',      # 招商银行
        '000001': '银行',      # 平安银行
        '601288': '银行',      # 农业银行
        '601939': '银行',      # 建设银行
        '601988': '银行',      # 中国银行
        
        # 白酒类
        '600519': '酿酒行业',   # 贵州茅台
        '000858': '酿酒行业',   # 五粮液
        '000568': '酿酒行业',   # 泸州老窖
        '000799': '酿酒行业',   # 酒鬼酒
        
        # 证券类
        '600030': '证券',      # 中信证券
        '601688': '证券',      # 华泰证券
        '000776': '证券',      # 广发证券
        '601211': '证券',      # 国泰君安
        
        # 保险类
        '601318': '保险',      # 中国平安
        '601628': '保险',      # 中国人寿
        '601336': '保险',      # 新华保险
        
        # 其他重要股票
        '605599': '珠宝首饰',   # 菜百股份
        '600519': '酿酒行业',   # 贵州茅台（重复确认）
        '000002': '房地产',     # 万科A
        '000333': '家电行业',   # 美的集团
        '000651': '家电行业',   # 格力电器
        
        # 更多映射可以继续添加
    }
    
    conn = sqlite3.connect('data/finance_data.db')
    cursor = conn.cursor()
    
    try:
        # 1. 先查看当前状态
        print("📊 修复前的数据状态:")
        
        # 统计市场板块数据
        cursor.execute('''
            SELECT industry, COUNT(*) as count
            FROM stock_info 
            WHERE industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
            GROUP BY industry
            ORDER BY count DESC
        ''')
        market_board_stats = cursor.fetchall()
        
        print("当前市场板块分布:")
        for industry, count in market_board_stats:
            print(f"  {industry}: {count}只股票")
        
        # 2. 查看需要修复的具体股票
        print("\n🔍 需要修复的股票:")
        
        for symbol, correct_industry in industry_mapping.items():
            cursor.execute('''
                SELECT symbol, name, industry 
                FROM stock_info 
                WHERE symbol = ?
            ''', (symbol,))
            
            result = cursor.fetchone()
            if result:
                print(f"  {result[0]} - {result[1]}: {result[2]} → {correct_industry}")
                
                # 更新行业信息
                cursor.execute('''
                    UPDATE stock_info 
                    SET industry = ?, updated_at = datetime('now')
                    WHERE symbol = ?
                ''', (correct_industry, symbol))
        
        # 3. 批量修复其他股票
        print("\n🔄 批量修复其他重要股票...")
        
        # 修复银行类股票
        cursor.execute('''
            UPDATE stock_info 
            SET industry = '银行', updated_at = datetime('now')
            WHERE name LIKE '%银行%' AND industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        ''')
        
        # 修复证券类股票
        cursor.execute('''
            UPDATE stock_info 
            SET industry = '证券', updated_at = datetime('now')
            WHERE (name LIKE '%证券%' OR name LIKE '%券商%') 
            AND industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        ''')
        
        # 修复保险类股票
        cursor.execute('''
            UPDATE stock_info 
            SET industry = '保险', updated_at = datetime('now')
            WHERE name LIKE '%保险%' AND industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        ''')
        
        # 修复酿酒类股票
        cursor.execute('''
            UPDATE stock_info 
            SET industry = '酿酒行业', updated_at = datetime('now')
            WHERE (name LIKE '%茅台%' OR name LIKE '%五粮液%' OR name LIKE '%泸州老窖%' 
                   OR name LIKE '%汾酒%' OR name LIKE '%古井贡%' OR name LIKE '%洋河%')
            AND industry IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
        ''')
        
        # 4. 提交更改
        conn.commit()
        
        # 5. 查看修复后的效果
        print("\n✅ 修复后的数据状态:")
        
        cursor.execute('''
            SELECT industry, COUNT(*) as count
            FROM stock_info 
            WHERE industry NOT IN ('上证主板', '深证主板', '创业板', '科创板', '北交所')
            AND industry IS NOT NULL AND industry != ''
            GROUP BY industry
            ORDER BY count DESC
            LIMIT 15
        ''')
        
        industry_stats = cursor.fetchall()
        
        print("主要行业分布:")
        for industry, count in industry_stats:
            print(f"  {industry}: {count}只股票")
        
        # 6. 验证修复结果
        print("\n🔍 验证修复结果:")
        for symbol, expected_industry in list(industry_mapping.items())[:5]:
            cursor.execute('''
                SELECT symbol, name, industry 
                FROM stock_info 
                WHERE symbol = ?
            ''', (symbol,))
            
            result = cursor.fetchone()
            if result:
                status = "✅" if result[2] == expected_industry else "❌"
                print(f"  {status} {result[0]} - {result[1]}: {result[2]}")
        
        print(f"\n🎉 数据修复完成！共处理了 {len(industry_mapping)} 只重点股票")
        
    except Exception as e:
        print(f"❌ 修复过程中出现错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_market_board_to_industry()