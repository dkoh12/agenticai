"""
Personal Finance Web Interface
A modern web UI for the Personal Finance MCP Tool with budget alerts
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finance_mcp_tool import PersonalFinanceMCPTool
import json
from datetime import datetime, timedelta
from typing import Dict, List

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize the finance tool
finance_tool = PersonalFinanceMCPTool()

class BudgetAlertSystem:
    """Handles budget alerts and notifications"""
    
    def __init__(self, finance_tool):
        self.finance_tool = finance_tool
    
    def check_budget_alerts(self, month: str = None) -> List[Dict]:
        """Check for budget alerts and return warnings"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        alerts = []
        
        # Get monthly summary
        summary_result = self.finance_tool.execute("get_summary", month=month)
        if not summary_result.get('success'):
            return alerts
        
        expenses_by_category = summary_result['expenses_by_category']
        
        # Get category budgets from database
        import sqlite3
        conn = sqlite3.connect(self.finance_tool.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, budget_amount FROM categories WHERE type = "expense" AND budget_amount > 0')
        budgets = dict(cursor.fetchall())
        conn.close()
        
        # Check each category against budget
        for category, budget_amount in budgets.items():
            spent = expenses_by_category.get(category, 0)
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            if percentage >= 100:
                alerts.append({
                    'type': 'danger',
                    'category': category,
                    'message': f'Budget exceeded! Spent ${spent:.2f} of ${budget_amount:.2f} ({percentage:.1f}%)',
                    'percentage': percentage,
                    'spent': spent,
                    'budget': budget_amount
                })
            elif percentage >= 80:
                alerts.append({
                    'type': 'warning',
                    'category': category,
                    'message': f'Budget warning: Spent ${spent:.2f} of ${budget_amount:.2f} ({percentage:.1f}%)',
                    'percentage': percentage,
                    'spent': spent,
                    'budget': budget_amount
                })
            elif percentage >= 60:
                alerts.append({
                    'type': 'info',
                    'category': category,
                    'message': f'Budget check: Spent ${spent:.2f} of ${budget_amount:.2f} ({percentage:.1f}%)',
                    'percentage': percentage,
                    'spent': spent,
                    'budget': budget_amount
                })
        
        return alerts

# Initialize budget alert system
budget_alerts = BudgetAlertSystem(finance_tool)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    
    # Get current month summary
    summary_result = finance_tool.execute("get_summary")
    summary = summary_result if summary_result.get('success') else {}
    
    # Get recent transactions
    transactions_result = finance_tool.execute("get_transactions", limit=5)
    recent_transactions = transactions_result.get('transactions', []) if transactions_result.get('success') else []
    
    # Get budget alerts
    alerts = budget_alerts.check_budget_alerts()
    
    # Get goals
    goals_result = finance_tool.execute("get_goals")
    goals = goals_result.get('goals', []) if goals_result.get('success') else []
    
    return render_template('dashboard.html', 
                         summary=summary, 
                         recent_transactions=recent_transactions,
                         alerts=alerts,
                         goals=goals)

@app.route('/transactions')
def transactions():
    """Transactions page"""
    
    # Get all transactions
    transactions_result = finance_tool.execute("get_transactions", limit=50)
    all_transactions = transactions_result.get('transactions', []) if transactions_result.get('success') else []
    
    # Get categories for filter
    import sqlite3
    conn = sqlite3.connect(finance_tool.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT name FROM categories ORDER BY name')
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('transactions.html', 
                         transactions=all_transactions,
                         categories=categories)

@app.route('/budgets')
def budgets():
    """Budget management page"""
    
    # Get categories with budgets
    import sqlite3
    conn = sqlite3.connect(finance_tool.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM categories WHERE type = "expense" ORDER BY name')
    categories = [dict(row) for row in cursor.fetchall()]
    
    # Get current month spending for each category
    current_month = datetime.now().strftime("%Y-%m")
    summary_result = finance_tool.execute("get_summary", month=current_month)
    expenses_by_category = summary_result.get('expenses_by_category', {}) if summary_result.get('success') else {}
    
    # Add spending info to categories
    for category in categories:
        category['spent'] = expenses_by_category.get(category['name'], 0)
        if category['budget_amount'] > 0:
            category['percentage'] = (category['spent'] / category['budget_amount']) * 100
        else:
            category['percentage'] = 0
    
    conn.close()
    
    return render_template('budgets.html', categories=categories)

@app.route('/reports')
def reports():
    """Reports and analytics page"""
    
    # Get spending report
    spending_result = finance_tool.execute("spending_report", days=30)
    spending_report = spending_result.get('spending_report', []) if spending_result.get('success') else []
    
    # Get monthly summaries for the last 6 months
    monthly_data = []
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        month = date.strftime("%Y-%m")
        summary_result = finance_tool.execute("get_summary", month=month)
        if summary_result.get('success'):
            summary_result['month'] = month
            summary_result['month_name'] = date.strftime("%B %Y")
            monthly_data.append(summary_result)
    
    return render_template('reports.html', 
                         spending_report=spending_report,
                         monthly_data=monthly_data)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        type_tx = request.form['type']
        date = request.form.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        result = finance_tool.execute(
            "add_transaction",
            amount=amount,
            category=category,
            description=description,
            type=type_tx,
            date=date
        )
        
        if result.get('success'):
            flash(f'Successfully added {type_tx} of ${amount:.2f}', 'success')
        else:
            flash(f'Error: {result.get("error")}', 'error')
    
    except Exception as e:
        flash(f'Error adding transaction: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/update_budget', methods=['POST'])
def update_budget():
    """Update category budget"""
    
    try:
        category = request.form['category']
        budget_amount = float(request.form['budget_amount'])
        
        # Update budget in database
        import sqlite3
        conn = sqlite3.connect(finance_tool.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE categories SET budget_amount = ? WHERE name = ?',
            (budget_amount, category)
        )
        
        conn.commit()
        conn.close()
        
        flash(f'Budget updated for {category}: ${budget_amount:.2f}', 'success')
    
    except Exception as e:
        flash(f'Error updating budget: {str(e)}', 'error')
    
    return redirect(url_for('budgets'))

@app.route('/api/budget_alerts')
def api_budget_alerts():
    """API endpoint for budget alerts"""
    alerts = budget_alerts.check_budget_alerts()
    return jsonify(alerts)

@app.route('/api/summary')
def api_summary():
    """API endpoint for financial summary"""
    result = finance_tool.execute("get_summary")
    return jsonify(result)

@app.route('/api/spending_chart')
def api_spending_chart():
    """API endpoint for spending chart data"""
    
    # Get last 6 months of data
    chart_data = {
        'labels': [],
        'income': [],
        'expenses': [],
        'net': []
    }
    
    for i in range(5, -1, -1):  # Last 6 months, oldest first
        date = datetime.now() - timedelta(days=30*i)
        month = date.strftime("%Y-%m")
        month_name = date.strftime("%b %Y")
        
        summary_result = finance_tool.execute("get_summary", month=month)
        if summary_result.get('success'):
            chart_data['labels'].append(month_name)
            chart_data['income'].append(summary_result['total_income'])
            chart_data['expenses'].append(summary_result['total_expenses'])
            chart_data['net'].append(summary_result['net_income'])
    
    return jsonify(chart_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
