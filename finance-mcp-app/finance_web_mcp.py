"""
Finance Web App with MCP Integration
Modern web interface that connects to Finance MCP Server and Ollama Client
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import asyncio
import sys
import os
import json
import subprocess
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import our MCP client
from finance_mcp_client import FinanceMCPClient

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

class FinanceWebMCP:
    """Web interface that uses MCP client for finance operations"""
    
    def __init__(self):
        self.mcp_client = FinanceMCPClient()
        self.setup_client()
    
    def setup_client(self):
        """Setup the MCP client"""
        print("🔧 Setting up Finance Web MCP...")
        
        # Setup Ollama LLM
        if not self.mcp_client.setup_ollama_llm():
            print("❌ Failed to setup Ollama LLM")
            return False
        
        # Setup agent
        if not self.mcp_client.setup_agent():
            print("❌ Failed to setup MCP agent")
            return False
        
        print("✅ Finance Web MCP ready!")
        return True
    
    def add_transaction(self, amount: float, category: str, description: str = "", transaction_type: str = "expense") -> Dict[str, Any]:
        """Add transaction via MCP client"""
        try:
            # Use the simple agent to add transaction
            query = f"{amount}|{category}|{description}|{transaction_type}"
            result = self.mcp_client.tools[0].func(query)  # add_transaction tool
            
            if "✅" in result:
                return {"success": True, "message": result}
            else:
                return {"success": False, "error": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """Get transactions via MCP client"""
        try:
            result = self.mcp_client.tools[1].func("")  # get_transactions tool
            
            # Parse the text response to extract transaction data
            if "📋" in result and "transactions:" in result:
                lines = result.split('\n')[1:]  # Skip header
                transactions = []
                
                for line in lines:
                    if line.strip() and ':' in line and '$' in line:
                        # Parse line like "  2025-08-07: $85.5 - Food & Dining (expense)"
                        parts = line.strip().split(': $')
                        if len(parts) == 2:
                            date = parts[0]
                            rest = parts[1].split(' - ')
                            if len(rest) >= 2:
                                amount = float(rest[0])
                                category_type = rest[1]
                                if '(' in category_type:
                                    category = category_type.split('(')[0].strip()
                                    txn_type = category_type.split('(')[1].replace(')', '').strip()
                                else:
                                    category = category_type
                                    txn_type = "expense"
                                
                                transactions.append({
                                    "date": date,
                                    "amount": amount,
                                    "category": category,
                                    "type": txn_type,
                                    "description": ""
                                })
                
                return {"success": True, "transactions": transactions}
            else:
                return {"success": False, "error": "Failed to parse transactions"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_financial_summary(self, month: str = None) -> Dict[str, Any]:
        """Get financial summary via MCP client"""
        try:
            result = self.mcp_client.tools[2].func(month or "")  # get_summary tool
            
            # Parse the text response
            if "📊" in result and "Financial Summary" in result:
                lines = result.split('\n')
                summary = {}
                
                for line in lines:
                    if "Income:" in line:
                        summary["total_income"] = float(line.split('$')[1])
                    elif "Expenses:" in line:
                        summary["total_expenses"] = float(line.split('$')[1])
                    elif "Net:" in line:
                        summary["net_income"] = float(line.split('$')[1])
                    elif "Savings Rate:" in line:
                        summary["savings_rate"] = float(line.split(': ')[1].replace('%', ''))
                    elif "Financial Summary for" in line:
                        summary["period"] = line.split('for ')[1].replace(':', '')
                
                # Parse expenses by category
                expenses_by_category = {}
                in_expenses_section = False
                for line in lines:
                    if "Top expenses:" in line:
                        in_expenses_section = True
                        continue
                    elif in_expenses_section and "- " in line and "$" in line:
                        parts = line.strip().split(': $')
                        if len(parts) == 2:
                            category = parts[0].replace('- ', '').strip()
                            amount = float(parts[1])
                            expenses_by_category[category] = amount
                
                summary["expenses_by_category"] = expenses_by_category
                return {"success": True, **summary}
            else:
                return {"success": False, "error": "Failed to parse summary"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get budget status via MCP client"""
        try:
            result = self.mcp_client.tools[3].func("")  # get_budget tool
            
            # Parse the budget response
            if "💰" in result and "Budget Status" in result:
                lines = result.split('\n')
                alerts = []
                budget_status = []
                
                in_alerts = False
                for line in lines:
                    if "🚨 ALERTS:" in line:
                        in_alerts = True
                        continue
                    elif in_alerts and line.strip() and ("🚨" in line or "⚠️" in line):
                        # Parse alert lines like "⚠️ WARNING: Food & Dining (17.1%)"
                        alert_text = line.strip()
                        alert_type = "danger" if "🚨" in alert_text else "warning"
                        
                        # Extract percentage if available
                        percentage = 0
                        category = "Budget Alert"
                        if "(" in alert_text and "%" in alert_text:
                            try:
                                pct_str = alert_text.split("(")[1].split("%")[0]
                                percentage = float(pct_str)
                                # Extract category name
                                if ":" in alert_text:
                                    category = alert_text.split(":")[1].split("(")[0].strip()
                            except:
                                pass
                        
                        alerts.append({
                            "type": alert_type,
                            "message": alert_text,
                            "category": category,
                            "percentage": percentage
                        })
                    elif ":" in line and "$" in line and "/" in line and "%" in line:
                        # Parse budget line like "  Food & Dining: $85.50/$500.00 (17.1%)"
                        parts = line.strip().split(': $')
                        if len(parts) == 2:
                            category = parts[0]
                            amounts = parts[1].split(' (')
                            if len(amounts) == 2:
                                spent_budget = amounts[0].split('/$')
                                spent = float(spent_budget[0])
                                budget = float(spent_budget[1])
                                percentage = float(amounts[1].replace('%)', ''))
                                
                                budget_status.append({
                                    "category": category,
                                    "spent": spent,
                                    "budget": budget,
                                    "percentage": percentage,
                                    "remaining": budget - spent
                                })
                
                return {
                    "success": True,
                    "alerts": alerts,
                    "budget_status": budget_status,
                    "month": datetime.now().strftime("%Y-%m")
                }
            else:
                return {"success": False, "error": "Failed to parse budget status"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def chat_with_assistant(self, user_input: str) -> str:
        """Chat with the finance assistant"""
        try:
            return self.mcp_client.simple_agent(user_input)
        except Exception as e:
            return f"❌ Error: {str(e)}"

# Initialize the finance web MCP
finance_web = FinanceWebMCP()

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def dashboard():
    """Main dashboard page"""
    
    # Get current month summary
    summary_result = finance_web.get_financial_summary()
    summary = summary_result if summary_result.get('success') else {
        'total_income': 0,
        'total_expenses': 0,
        'net_income': 0,
        'savings_rate': 0,
        'period': datetime.now().strftime("%Y-%m")
    }
    
    # Get recent transactions
    transactions_result = finance_web.get_transactions(limit=5)
    recent_transactions = transactions_result.get('transactions', []) if transactions_result.get('success') else []
    
    # Get budget status
    budget_result = finance_web.get_budget_status()
    alerts = budget_result.get('alerts', []) if budget_result.get('success') else []
    budget_status = budget_result.get('budget_status', []) if budget_result.get('success') else []
    
    return render_template('dashboard.html', 
                         summary=summary, 
                         recent_transactions=recent_transactions,
                         alerts=alerts,
                         budget_status=budget_status)

@app.route('/transactions')
def transactions():
    """Transactions page"""
    
    # Get all transactions
    transactions_result = finance_web.get_transactions(limit=50)
    all_transactions = transactions_result.get('transactions', []) if transactions_result.get('success') else []
    
    # Get unique categories for filter
    categories = list(set([t.get('category', '') for t in all_transactions if t.get('category')]))
    categories.sort()
    
    return render_template('transactions.html', 
                         transactions=all_transactions,
                         categories=categories)

@app.route('/budgets')
def budgets():
    """Budget management page"""
    
    # Get budget status
    budget_result = finance_web.get_budget_status()
    budget_status = budget_result.get('budget_status', []) if budget_result.get('success') else []
    alerts = budget_result.get('alerts', []) if budget_result.get('success') else []
    
    return render_template('budgets.html', 
                         budget_status=budget_status,
                         alerts=alerts)

@app.route('/chat')
def chat():
    """AI Chat interface"""
    return render_template('chat.html')

@app.route('/reports')
def reports():
    """Financial reports page"""
    
    # Get summary for current month
    summary_result = finance_web.get_financial_summary()
    summary = summary_result if summary_result.get('success') else {}
    
    # Get last 3 months for trend
    monthly_summaries = []
    for i in range(3):
        date = datetime.now() - timedelta(days=i*30)
        month = date.strftime("%Y-%m")
        month_summary = finance_web.get_financial_summary(month)
        if month_summary.get('success'):
            month_summary['month_name'] = date.strftime("%B %Y")
            monthly_summaries.append(month_summary)
    
    return render_template('reports.html', 
                         summary=summary,
                         monthly_summaries=monthly_summaries)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Add transaction via form submission"""
    try:
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        transaction_type = request.form.get('type', 'expense')
        
        result = finance_web.add_transaction(
            amount=amount,
            category=category,
            description=description,
            transaction_type=transaction_type
        )
        
        if result['success']:
            flash('Transaction added successfully!', 'success')
        else:
            flash(f'Error: {result["error"]}', 'error')
        
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/api/add_transaction', methods=['POST'])
def api_add_transaction():
    """Add transaction via API"""
    try:
        data = request.get_json()
        
        result = finance_web.add_transaction(
            amount=float(data['amount']),
            category=data['category'],
            description=data.get('description', ''),
            transaction_type=data.get('type', 'expense')
        )
        
        if result['success']:
            flash('Transaction added successfully!', 'success')
        else:
            flash(f'Error: {result["error"]}', 'error')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat with AI assistant via API"""
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        
        if not user_input:
            return jsonify({"success": False, "error": "No message provided"})
        
        response = finance_web.chat_with_assistant(user_input)
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/summary')
def api_summary():
    """Get financial summary via API"""
    month = request.args.get('month')
    result = finance_web.get_financial_summary(month)
    return jsonify(result)

@app.route('/api/transactions')
def api_transactions():
    """Get transactions via API"""
    limit = int(request.args.get('limit', 10))
    result = finance_web.get_transactions(limit)
    return jsonify(result)

@app.route('/api/budget_status')
def api_budget_status():
    """Get budget status via API"""
    result = finance_web.get_budget_status()
    return jsonify(result)

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500

if __name__ == '__main__':
    print("🌐 Starting Finance Web App with MCP Integration...")
    print("📡 Make sure your Finance MCP Server is running!")
    print("🦙 Ollama Llama 3.2 integration enabled")
    print("\n🚀 Web app will be available at: http://localhost:5002")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
