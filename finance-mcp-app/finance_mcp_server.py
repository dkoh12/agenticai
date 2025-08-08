"""
Real MCP Finance Server with FastMCP
A proper MCP server that provides finance tools to LLM agents
"""

import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# FastMCP imports
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("finance-mcp-server")

# Global paths
DB_PATH = "finance_mcp.db"

def setup_finance_database():
    """Setup finance database with proper MCP structure"""
    print("Setting up finance MCP database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            account TEXT DEFAULT 'checking',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
            budget_amount REAL DEFAULT 0,
            color TEXT DEFAULT '#3498db'
        )
    ''')
    
    # Goals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            target_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused'))
        )
    ''')
    
    # Insert default categories
    default_categories = [
        ('Food & Dining', 'expense', 500, '#e74c3c'),
        ('Transportation', 'expense', 300, '#f39c12'),
        ('Shopping', 'expense', 200, '#9b59b6'),
        ('Entertainment', 'expense', 150, '#e67e22'),
        ('Bills & Utilities', 'expense', 400, '#34495e'),
        ('Healthcare', 'expense', 100, '#16a085'),
        ('Education', 'expense', 50, '#2980b9'),
        ('Salary', 'income', 0, '#27ae60'),
        ('Freelance', 'income', 0, '#f1c40f'),
        ('Investments', 'income', 0, '#8e44ad'),
    ]
    
    for name, type_, budget, color in default_categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (name, type, budget_amount, color)
            VALUES (?, ?, ?, ?)
        ''', (name, type_, budget, color))
    
    conn.commit()
    conn.close()
    print("✅ Finance database setup complete")

# ============================================================================
# MCP TOOLS - These are exposed to LLM agents
# ============================================================================

@mcp.tool()
def add_transaction(amount: float, category: str, description: str = "", 
                   transaction_type: str = "expense", date: str = None) -> Dict[str, Any]:
    """
    Add a new financial transaction.
    
    Args:
        amount: Transaction amount (positive number)
        category: Category name (e.g., 'Food & Dining', 'Salary')
        description: Optional description of the transaction
        transaction_type: Either 'income' or 'expense'
        date: Date in YYYY-MM-DD format (defaults to today)
    
    Returns:
        Dictionary with success status and transaction details
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO transactions (date, amount, category, description, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, description, transaction_type))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": f"Added {transaction_type} of ${amount:.2f} in {category}",
            "details": {
                "id": transaction_id,
                "amount": amount,
                "category": category,
                "description": description,
                "type": transaction_type,
                "date": date
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@mcp.tool()
def get_transactions(limit: int = 10, category: str = None, month: str = None) -> Dict[str, Any]:
    """
    Get recent transactions with optional filtering.
    
    Args:
        limit: Maximum number of transactions to return
        category: Filter by category name (optional)
        month: Filter by month in YYYY-MM format (optional)
    
    Returns:
        Dictionary with list of transactions
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if month:
            query += " AND date LIKE ?"
            params.append(f"{month}-%")
        
        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        
        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions),
            "filters": {"category": category, "month": month, "limit": limit}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@mcp.tool()
def get_financial_summary(month: str = None) -> Dict[str, Any]:
    """
    Get financial summary for a specific month or current month.
    
    Args:
        month: Month in YYYY-MM format (defaults to current month)
    
    Returns:
        Dictionary with income, expenses, net income, and category breakdown
    """
    if month is None:
        month = datetime.now().strftime("%Y-%m")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        date_filter = f"AND date LIKE '{month}-%'"
        
        # Total income
        cursor.execute(f'''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'income' {date_filter}
        ''')
        total_income = cursor.fetchone()[0]
        
        # Total expenses
        cursor.execute(f'''
            SELECT COALESCE(SUM(amount), 0) FROM transactions 
            WHERE type = 'expense' {date_filter}
        ''')
        total_expenses = cursor.fetchone()[0]
        
        # Expenses by category
        cursor.execute(f'''
            SELECT category, SUM(amount) as total FROM transactions 
            WHERE type = 'expense' {date_filter}
            GROUP BY category ORDER BY total DESC
        ''')
        expenses_by_category = dict(cursor.fetchall())
        
        net_income = total_income - total_expenses
        savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
        
        return {
            "success": True,
            "period": month,
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_income": round(net_income, 2),
            "savings_rate": round(savings_rate, 1),
            "expenses_by_category": expenses_by_category
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@mcp.tool()
def add_financial_goal(goal_name: str, target_amount: float, target_date: str = None) -> Dict[str, Any]:
    """
    Add a new financial goal.
    
    Args:
        goal_name: Name of the financial goal
        target_amount: Target amount to save
        target_date: Target date in YYYY-MM-DD format (optional)
    
    Returns:
        Dictionary with success status and goal details
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO goals (name, target_amount, target_date)
            VALUES (?, ?, ?)
        ''', (goal_name, target_amount, target_date))
        
        goal_id = cursor.lastrowid
        conn.commit()
        
        return {
            "success": True,
            "goal_id": goal_id,
            "message": f"Added goal: {goal_name} (${target_amount:.2f})",
            "details": {
                "id": goal_id,
                "name": goal_name,
                "target_amount": target_amount,
                "target_date": target_date
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

@mcp.tool()
def get_budget_status() -> Dict[str, Any]:
    """
    Get current budget status and alerts.
    
    Returns:
        Dictionary with budget information and overspending alerts
    """
    current_month = datetime.now().strftime("%Y-%m")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get category budgets
        cursor.execute('SELECT name, budget_amount FROM categories WHERE type = "expense" AND budget_amount > 0')
        budgets = dict(cursor.fetchall())
        
        # Get current month spending by category
        cursor.execute(f'''
            SELECT category, SUM(amount) as spent FROM transactions 
            WHERE type = 'expense' AND date LIKE '{current_month}-%'
            GROUP BY category
        ''')
        spending = dict(cursor.fetchall())
        
        # Calculate budget status
        budget_status = []
        alerts = []
        
        for category, budget in budgets.items():
            spent = spending.get(category, 0)
            remaining = budget - spent
            percentage = (spent / budget * 100) if budget > 0 else 0
            
            status = {
                "category": category,
                "budget": budget,
                "spent": round(spent, 2),
                "remaining": round(remaining, 2),
                "percentage": round(percentage, 1)
            }
            budget_status.append(status)
            
            # Generate alerts
            if percentage >= 100:
                alerts.append(f"🚨 OVER BUDGET: {category} ({percentage:.1f}%)")
            elif percentage >= 80:
                alerts.append(f"⚠️ WARNING: {category} ({percentage:.1f}%)")
        
        return {
            "success": True,
            "month": current_month,
            "budget_status": budget_status,
            "alerts": alerts,
            "total_categories": len(budget_status)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

# ============================================================================
# MCP RESOURCES - File system resources available to agents
# ============================================================================

@mcp.resource("file://finance_summary.json")
async def get_finance_summary_resource():
    """Provide current financial summary as a resource"""
    summary = get_financial_summary()
    return json.dumps(summary, indent=2)

# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

def main():
    """Initialize and run the MCP server"""
    print("🏦 Starting Finance MCP Server with FastMCP...")
    
    # Setup database
    setup_finance_database()
    
    # Add some demo data directly to database
    print("Adding demo transactions...")
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if demo data already exists
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        demo_transactions = [
            (datetime.now().strftime("%Y-%m-%d"), 3500.0, "Salary", "Monthly salary", "income"),
            (datetime.now().strftime("%Y-%m-%d"), 85.50, "Food & Dining", "Groceries", "expense"),
            (datetime.now().strftime("%Y-%m-%d"), 45.00, "Transportation", "Gas", "expense"),
            (datetime.now().strftime("%Y-%m-%d"), 12.99, "Entertainment", "Netflix subscription", "expense")
        ]
        
        cursor.executemany('''
            INSERT INTO transactions (date, amount, category, description, type)
            VALUES (?, ?, ?, ?, ?)
        ''', demo_transactions)
        conn.commit()
        print("✅ Demo data added!")
    else:
        print("✅ Using existing data")
    
    conn.close()
    
    print("✅ Finance MCP Server ready!")
    print("Available tools:")
    print("- add_transaction: Add income/expense transactions")
    print("- get_transactions: Retrieve transaction history")
    print("- get_financial_summary: Get monthly financial overview")
    print("- add_financial_goal: Set savings goals")
    print("- get_budget_status: Check budget and overspending alerts")
    print("\n🚀 Server running on stdio...")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()
