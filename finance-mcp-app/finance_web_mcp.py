"""
Finance Web App with MCP Integration
Modern web interface that connects to Finance MCP Server and Ollama Client
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
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

# Enable CORS for all domains on all routes
CORS(app)

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
# API ROUTES ONLY - React Frontend Handles UI
# ============================================================================

# Remove HTML routes since React frontend handles UI
# Keep only API endpoints for the React app

@app.route('/')
def index():
    """Redirect to React frontend"""
    return jsonify({
        "message": "Finance MCP API Server", 
        "react_frontend": "http://localhost:5173",
        "api_endpoints": [
            "/api/transactions",
            "/api/add_transaction", 
            "/api/financial_summary",
            "/api/budgets",
            "/api/categories",
            "/api/chat"
        ]
    })

# ============================================================================
# API ROUTES
# ============================================================================

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

@app.route('/api/financial_summary')
def api_financial_summary():
    """Get financial summary via API"""
    month = request.args.get('month')
    result = finance_web.get_financial_summary(month)
    if result.get('success'):
        # Return data in the format expected by frontend
        return jsonify({
            "total_income": result.get('total_income', 0),
            "total_expenses": result.get('total_expenses', 0), 
            "net_income": result.get('net_income', 0),
            "expense_by_category": result.get('expenses_by_category', {})
        })
    else:
        return jsonify({"error": result.get('error', 'Unknown error')}), 500

@app.route('/api/budgets')
def api_budgets():
    """Get budgets via API"""
    result = finance_web.get_budget_status()
    if result.get('success'):
        budgets = []
        for budget in result.get('budget_status', []):
            budgets.append({
                "category": budget['category'],
                "budgeted": budget['budget'],
                "spent": budget['spent'],
                "remaining": budget['remaining']
            })
        return jsonify(budgets)
    else:
        return jsonify({"error": result.get('error', 'Unknown error')}), 500

@app.route('/api/transactions')
def api_transactions():
    """Get transactions via API"""
    limit = int(request.args.get('limit', 50))
    result = finance_web.get_transactions(limit)
    if result.get('success'):
        transactions = []
        for txn in result.get('transactions', []):
            transactions.append({
                "amount": txn['amount'],
                "description": txn.get('description', ''),
                "category": txn['category'],
                "date": txn['date']
            })
        return jsonify(transactions)
    else:
        return jsonify({"error": result.get('error', 'Unknown error')}), 500

@app.route('/api/categories')
def api_categories():
    """Get available categories via API"""
    categories = [
        'Food',
        'Transportation', 
        'Entertainment',
        'Utilities',
        'Healthcare',
        'Shopping',
        'Income',
        'Other'
    ]
    return jsonify(categories)

@app.route('/api/summary')
def api_summary():
    """Get financial summary via API (legacy endpoint)"""
    month = request.args.get('month')
    result = finance_web.get_financial_summary(month)
    return jsonify(result)

@app.route('/api/budget_status')
def api_budget_status():
    """Get budget status via API"""
    result = finance_web.get_budget_status()
    return jsonify(result)

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("🌐 Starting Finance MCP API Server...")
    print("📡 Make sure your Finance MCP Server is running!")
    print("🦙 Ollama Llama 3.2 integration enabled")
    print("⚛️  React Frontend: http://localhost:5173")
    print("🚀 API Server: http://localhost:5003")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
