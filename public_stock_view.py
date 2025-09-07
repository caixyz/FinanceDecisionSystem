#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公开的股票信息查看页面 - 用于验证行业信息修复效果
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect('data/finance_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def public_stock_view():
    """公开的股票信息查看页面"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票行业信息查看</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .stock-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .stock-table th, .stock-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .stock-table th {
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }
        .stock-table tr:hover {
            background-color: #f9f9f9;
        }
        .industry-tag {
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.9em;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            color: #d32f2f;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 股票行业信息查看</h1>
            <p>验证行业信息修复效果 - 无需登录</p>
        </div>
        
        <div id="loading" class="loading">加载中...</div>
        <div id="content" style="display: none;">
            <h3>主要股票行业信息</h3>
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>股票代码</th>
                        <th>股票名称</th>
                        <th>行业分类</th>
                        <th>最新收盘价(元)</th>
                        <th>更新时间</th>
                    </tr>
                </thead>
                <tbody id="stock-list">
                </tbody>
            </table>
            
            <h3>行业分布统计</h3>
            <table class="stock-table">
                <thead>
                    <tr>
                        <th>行业名称</th>
                        <th>股票数量</th>
                    </tr>
                </thead>
                <tbody id="industry-stats">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function loadStockData() {
            try {
                const response = await fetch('/api/public/stocks');
                const data = await response.json();
                
                if (data.success) {
                    displayStocks(data.stocks);
                    displayIndustryStats(data.industry_stats);
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                } else {
                    document.getElementById('loading').innerHTML = 
                        '<div class="error">加载失败: ' + data.message + '</div>';
                }
            } catch (error) {
                document.getElementById('loading').innerHTML = 
                    '<div class="error">加载失败: ' + error.message + '</div>';
            }
        }

        function displayStocks(stocks) {
            const tbody = document.getElementById('stock-list');
            const testSymbols = ['601398', '600036', '600519', '600030', '000858', '000001'];
            
            const filteredStocks = stocks.filter(stock => 
                testSymbols.includes(stock.symbol)
            );

            tbody.innerHTML = filteredStocks.map(stock => `
                <tr>
                    <td>${stock.symbol}</td>
                    <td>${stock.name}</td>
                    <td><span class="industry-tag">${stock.industry || '未分类'}</span></td>
                    <td>¥${stock.close ? stock.close.toFixed(2) : 'N/A'}</td>
                    <td>${stock.updated_at || '未知'}</td>
                </tr>
            `).join('');
        }

        function displayIndustryStats(stats) {
            const tbody = document.getElementById('industry-stats');
            tbody.innerHTML = stats.map(stat => `
                <tr>
                    <td>${stat.industry}</td>
                    <td>${stat.count}</td>
                </tr>
            `).join('');
        }

        // 页面加载完成后自动加载数据
        document.addEventListener('DOMContentLoaded', loadStockData);
    </script>
</body>
</html>
    ''')

@app.route('/api/public/stocks')
def public_stocks_api():
    """公开的股票数据API"""
    try:
        conn = get_db_connection()
        
        # 获取主要股票信息
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol, name, industry, close, updated_at 
            FROM stock_info 
            WHERE symbol IN ('601398', '600036', '600519', '600030', '000858', '000001')
            ORDER BY symbol
        ''')
        stocks = [dict(row) for row in cursor.fetchall()]
        
        # 获取行业统计
        cursor.execute('''
            SELECT industry, COUNT(*) as count
            FROM stock_info
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry
            ORDER BY count DESC
            LIMIT 15
        ''')
        industry_stats = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stocks': stocks,
            'industry_stats': industry_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)