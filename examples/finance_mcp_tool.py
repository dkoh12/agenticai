"""
Personal Finance Tracker MCP Tool
A practical MCP tool for managing personal finances - perfect for learning!
"""

import json
import csv
import sqlite3
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path
import calendar

class PersonalFinanceMCPTool:
    """MCP tool for personal finance tracking"""
    
    def __init__(self, data_path: str = "finance_data"):
        self.name = "personal_finance"
        self.description = "Track income, expenses, budgets, and financial goals"
        self.version = "1.0.0"
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        self.db_path = self.data_path / "finance.db"
        self._setup_database()
    
    def _setup_database(self):
        """Initialize the finance database"""
        conn = sqlite3.connect(self.db_path)
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
        
        # Insert default categories if they don't exist
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
    
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for the tool"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "add_transaction", "get_transactions", "get_summary",
                        "set_budget", "get_budget", "add_goal", "update_goal",
                        "get_goals", "get_categories", "spending_report",
                        "monthly_summary", "export_data", "import_csv"
                    ],
                    "description": "Action to perform"
                },
                "amount": {"type": "number", "description": "Transaction amount"},
                "category": {"type": "string", "description": "Transaction category"},
                "description": {"type": "string", "description": "Transaction description"},
                "type": {"type": "string", "enum": ["income", "expense"], "description": "Transaction type"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "month": {"type": "string", "description": "Month in YYYY-MM format"},
                "goal_name": {"type": "string", "description": "Name of financial goal"},
                "target_amount": {"type": "number", "description": "Target amount for goal"},
                "file_path": {"type": "string", "description": "Path to CSV file for import"}
            },
            "required": ["action"]
        }
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute finance operation"""
        try:
            if action == "add_transaction":
                return self._add_transaction(**kwargs)
            elif action == "get_transactions":
                return self._get_transactions(**kwargs)
            elif action == "get_summary":
                return self._get_summary(**kwargs)
            elif action == "set_budget":
                return self._set_budget(**kwargs)
            elif action == "get_budget":
                return self._get_budget(**kwargs)
            elif action == "add_goal":
                return self._add_goal(**kwargs)
            elif action == "get_goals":
                return self._get_goals()
            elif action == "spending_report":
                return self._spending_report(**kwargs)
            elif action == "monthly_summary":
                return self._monthly_summary(**kwargs)
            elif action == "export_data":
                return self._export_data(**kwargs)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _add_transaction(self, amount: float, category: str, description: str = "",
                        type: str = "expense", date: str = None, **kwargs) -> Dict[str, Any]:
        """Add a new transaction"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (date, amount, category, description, type)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, description, type))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": f"Added {type} of ${amount:.2f} in {category}"
        }
    
    def _get_transactions(self, limit: int = 10, category: str = None, 
                         month: str = None, **kwargs) -> Dict[str, Any]:
        """Get recent transactions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if month:  # YYYY-MM format
            query += " AND date LIKE ?"
            params.append(f"{month}-%")
        
        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {"success": True, "transactions": transactions, "count": len(transactions)}
    
    def _get_summary(self, month: str = None, **kwargs) -> Dict[str, Any]:
        """Get financial summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if month:
            date_filter = f"AND date LIKE '{month}-%'"
        else:
            # Current month
            current_month = datetime.now().strftime("%Y-%m")
            date_filter = f"AND date LIKE '{current_month}-%'"
        
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
        
        conn.close()
        
        net_income = total_income - total_expenses
        
        return {
            "success": True,
            "period": month or datetime.now().strftime("%Y-%m"),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "expenses_by_category": expenses_by_category,
            "savings_rate": (net_income / total_income * 100) if total_income > 0 else 0
        }
    
    def _spending_report(self, days: int = 30, **kwargs) -> Dict[str, Any]:
        """Generate spending report for last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date.replace(day=1) if days >= 30 else end_date
        
        cursor.execute('''
            SELECT category, COUNT(*) as transactions, SUM(amount) as total,
                   AVG(amount) as average
            FROM transactions 
            WHERE type = 'expense' AND date >= ?
            GROUP BY category 
            ORDER BY total DESC
        ''', (start_date.strftime("%Y-%m-%d"),))
        
        spending_data = cursor.fetchall()
        conn.close()
        
        report = []
        for row in spending_data:
            report.append({
                "category": row[0],
                "transactions": row[1],
                "total": round(row[2], 2),
                "average": round(row[3], 2)
            })
        
        return {"success": True, "spending_report": report, "period_days": days}
    
    def _add_goal(self, goal_name: str, target_amount: float, 
                 target_date: str = None, **kwargs) -> Dict[str, Any]:
        """Add a financial goal"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goals (name, target_amount, target_date)
            VALUES (?, ?, ?)
        ''', (goal_name, target_amount, target_date))
        
        goal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "goal_id": goal_id,
            "message": f"Added goal: {goal_name} (${target_amount:.2f})"
        }
    
    def _get_goals(self, **kwargs) -> Dict[str, Any]:
        """Get all financial goals"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM goals ORDER BY created_at DESC')
        goals = [dict(row) for row in cursor.fetchall()]
        
        # Calculate progress for each goal
        for goal in goals:
            if goal['target_amount'] > 0:
                goal['progress_percent'] = (goal['current_amount'] / goal['target_amount']) * 100
            else:
                goal['progress_percent'] = 0
        
        conn.close()
        
        return {"success": True, "goals": goals}
    
    def _export_data(self, format: str = "csv", **kwargs) -> Dict[str, Any]:
        """Export transaction data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, amount, category, description, type 
            FROM transactions ORDER BY date DESC
        ''')
        
        transactions = cursor.fetchall()
        conn.close()
        
        if format == "csv":
            export_file = self.data_path / f"transactions_export_{datetime.now().strftime('%Y%m%d')}.csv"
            
            with open(export_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Amount', 'Category', 'Description', 'Type'])
                writer.writerows(transactions)
            
            return {
                "success": True,
                "export_file": str(export_file),
                "record_count": len(transactions)
            }
        
        return {"success": False, "error": "Unsupported export format"}

def demo_finance_tool():
    """Demonstrate the Personal Finance MCP Tool"""
    
    print("💰 Personal Finance MCP Tool Demo")
    print("=" * 50)
    
    # Create the tool
    finance_tool = PersonalFinanceMCPTool()
    
    print("✅ Finance tool initialized!")
    print(f"📊 Database created at: {finance_tool.db_path}")
    
    # Demo scenarios
    scenarios = [
        {
            "name": "Add Grocery Expense",
            "action": "add_transaction",
            "params": {
                "amount": 85.50,
                "category": "Food & Dining",
                "description": "Weekly groceries at Whole Foods",
                "type": "expense"
            }
        },
        {
            "name": "Add Salary Income",
            "action": "add_transaction", 
            "params": {
                "amount": 3500.00,
                "category": "Salary",
                "description": "Monthly salary",
                "type": "income"
            }
        },
        {
            "name": "Add Coffee Expense",
            "action": "add_transaction",
            "params": {
                "amount": 4.75,
                "category": "Food & Dining", 
                "description": "Morning coffee",
                "type": "expense"
            }
        },
        {
            "name": "Get Recent Transactions",
            "action": "get_transactions",
            "params": {"limit": 5}
        },
        {
            "name": "Get Monthly Summary",
            "action": "get_summary",
            "params": {}
        },
        {
            "name": "Add Emergency Fund Goal",
            "action": "add_goal",
            "params": {
                "goal_name": "Emergency Fund",
                "target_amount": 10000.00,
                "target_date": "2025-12-31"
            }
        },
        {
            "name": "Get Spending Report",
            "action": "spending_report",
            "params": {"days": 30}
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📝 Demo {i}: {scenario['name']}")
        print("-" * 30)
        
        result = finance_tool.execute(scenario['action'], **scenario['params'])
        
        if result.get('success'):
            print("✅ Success!")
            
            # Pretty print results based on action
            if scenario['action'] == 'get_transactions':
                print(f"📋 Found {result['count']} transactions:")
                for txn in result['transactions'][:3]:
                    print(f"   {txn['date']}: ${txn['amount']} - {txn['category']} ({txn['type']})")
            
            elif scenario['action'] == 'get_summary':
                summary = result
                print(f"📊 Financial Summary for {summary['period']}:")
                print(f"   Income: ${summary['total_income']:.2f}")
                print(f"   Expenses: ${summary['total_expenses']:.2f}")
                print(f"   Net: ${summary['net_income']:.2f}")
                print(f"   Savings Rate: {summary['savings_rate']:.1f}%")
            
            elif scenario['action'] == 'spending_report':
                print("📈 Top spending categories:")
                for category in result['spending_report'][:3]:
                    print(f"   {category['category']}: ${category['total']} ({category['transactions']} transactions)")
            
            else:
                print(f"   {result.get('message', 'Operation completed')}")
        
        else:
            print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    demo_finance_tool()
    
    print("\n" + "=" * 50)
    print("🎯 Why This MCP Tool is Perfect for Learning:")
    print("• Solves a real personal problem (finance tracking)")
    print("• Uses multiple data operations (CRUD)")
    print("• Demonstrates MCP patterns clearly")
    print("• Safe to experiment with (your own data)")
    print("• Immediately useful in daily life")
    print("• Can integrate with banks/apps later")
    
    print("\n🚀 Next Steps:")
    print("1. Customize categories for your spending habits")
    print("2. Add bank CSV import functionality")
    print("3. Create budget alerts and notifications")
    print("4. Build a simple web interface")
    print("5. Integrate with LangChain for natural language queries")
    
    print("\n💡 Example LangChain Integration:")
    print('   "How much did I spend on food this month?"')
    print('   "Add a $50 gas expense"')
    print('   "Am I on track for my savings goal?"')
