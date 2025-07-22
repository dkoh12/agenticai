"""
Demo Data Generator for Personal Finance Web App
Creates realistic sample data to showcase budget alerts and features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finance_mcp_tool import PersonalFinanceMCPTool
from datetime import datetime, timedelta
import random

def create_demo_data():
    """Create comprehensive demo data for the finance app"""
    
    print("🎭 Creating Demo Data for Personal Finance Web App")
    print("=" * 55)
    
    # Initialize the finance tool
    finance_tool = PersonalFinanceMCPTool()
    
    # Set budgets for categories (this will trigger alerts)
    import sqlite3
    conn = sqlite3.connect(finance_tool.db_path)
    cursor = conn.cursor()
    
    # Update budgets to realistic amounts that will show alerts
    budget_updates = [
        ('Food & Dining', 400),
        ('Transportation', 250),
        ('Shopping', 150),
        ('Entertainment', 100),
        ('Bills & Utilities', 300),
        ('Healthcare', 80),
        ('Education', 50),
    ]
    
    print("💰 Setting budgets...")
    for category, amount in budget_updates:
        cursor.execute(
            'UPDATE categories SET budget_amount = ? WHERE name = ?',
            (amount, category)
        )
        print(f"   {category}: ${amount}")
    
    conn.commit()
    conn.close()
    
    # Generate transactions for the current month
    print("\n📊 Adding transactions...")
    
    # Start from beginning of current month
    start_date = datetime.now().replace(day=1)
    current_date = start_date
    
    # Sample transactions that will create budget alerts
    transactions = [
        # Income (monthly salary)
        {"amount": 4500, "category": "Salary", "description": "Monthly salary", "type": "income", "date": start_date.strftime("%Y-%m-%d")},
        {"amount": 800, "category": "Freelance", "description": "Web design project", "type": "income", "date": (start_date + timedelta(days=5)).strftime("%Y-%m-%d")},
        
        # Food & Dining (will exceed budget of $400)
        {"amount": 65.50, "category": "Food & Dining", "description": "Grocery shopping", "type": "expense", "date": (start_date + timedelta(days=1)).strftime("%Y-%m-%d")},
        {"amount": 35.75, "category": "Food & Dining", "description": "Dinner out", "type": "expense", "date": (start_date + timedelta(days=3)).strftime("%Y-%m-%d")},
        {"amount": 12.50, "category": "Food & Dining", "description": "Coffee shop", "type": "expense", "date": (start_date + timedelta(days=4)).strftime("%Y-%m-%d")},
        {"amount": 45.20, "category": "Food & Dining", "description": "Lunch meeting", "type": "expense", "date": (start_date + timedelta(days=6)).strftime("%Y-%m-%d")},
        {"amount": 78.30, "category": "Food & Dining", "description": "Weekend groceries", "type": "expense", "date": (start_date + timedelta(days=8)).strftime("%Y-%m-%d")},
        {"amount": 25.00, "category": "Food & Dining", "description": "Pizza delivery", "type": "expense", "date": (start_date + timedelta(days=10)).strftime("%Y-%m-%d")},
        {"amount": 55.80, "category": "Food & Dining", "description": "Date night dinner", "type": "expense", "date": (start_date + timedelta(days=12)).strftime("%Y-%m-%d")},
        {"amount": 18.90, "category": "Food & Dining", "description": "Morning coffee", "type": "expense", "date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d")},
        {"amount": 95.00, "category": "Food & Dining", "description": "Family dinner", "type": "expense", "date": (start_date + timedelta(days=16)).strftime("%Y-%m-%d")},
        {"amount": 32.40, "category": "Food & Dining", "description": "Quick lunch", "type": "expense", "date": (start_date + timedelta(days=18)).strftime("%Y-%m-%d")},
        
        # Transportation (will hit warning at 80% of $250 budget)
        {"amount": 45.00, "category": "Transportation", "description": "Gas fill-up", "type": "expense", "date": (start_date + timedelta(days=2)).strftime("%Y-%m-%d")},
        {"amount": 25.50, "category": "Transportation", "description": "Uber ride", "type": "expense", "date": (start_date + timedelta(days=5)).strftime("%Y-%m-%d")},
        {"amount": 50.00, "category": "Transportation", "description": "Gas station", "type": "expense", "date": (start_date + timedelta(days=9)).strftime("%Y-%m-%d")},
        {"amount": 15.75, "category": "Transportation", "description": "Parking fee", "type": "expense", "date": (start_date + timedelta(days=11)).strftime("%Y-%m-%d")},
        {"amount": 35.00, "category": "Transportation", "description": "Taxi to airport", "type": "expense", "date": (start_date + timedelta(days=15)).strftime("%Y-%m-%d")},
        {"amount": 28.00, "category": "Transportation", "description": "Public transit", "type": "expense", "date": (start_date + timedelta(days=17)).strftime("%Y-%m-%d")},
        
        # Shopping (will be close to budget)
        {"amount": 85.99, "category": "Shopping", "description": "Clothing purchase", "type": "expense", "date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d")},
        {"amount": 45.50, "category": "Shopping", "description": "Online order", "type": "expense", "date": (start_date + timedelta(days=13)).strftime("%Y-%m-%d")},
        
        # Entertainment (will exceed $100 budget)
        {"amount": 65.00, "category": "Entertainment", "description": "Concert tickets", "type": "expense", "date": (start_date + timedelta(days=4)).strftime("%Y-%m-%d")},
        {"amount": 25.50, "category": "Entertainment", "description": "Movie night", "type": "expense", "date": (start_date + timedelta(days=8)).strftime("%Y-%m-%d")},
        {"amount": 35.00, "category": "Entertainment", "description": "Streaming services", "type": "expense", "date": (start_date + timedelta(days=12)).strftime("%Y-%m-%d")},
        
        # Bills & Utilities (under budget)
        {"amount": 125.00, "category": "Bills & Utilities", "description": "Electric bill", "type": "expense", "date": (start_date + timedelta(days=1)).strftime("%Y-%m-%d")},
        {"amount": 89.99, "category": "Bills & Utilities", "description": "Internet bill", "type": "expense", "date": (start_date + timedelta(days=6)).strftime("%Y-%m-%d")},
        {"amount": 45.00, "category": "Bills & Utilities", "description": "Water bill", "type": "expense", "date": (start_date + timedelta(days=10)).strftime("%Y-%m-%d")},
        
        # Healthcare (under budget)
        {"amount": 35.00, "category": "Healthcare", "description": "Pharmacy", "type": "expense", "date": (start_date + timedelta(days=14)).strftime("%Y-%m-%d")},
        {"amount": 25.00, "category": "Healthcare", "description": "Vitamins", "type": "expense", "date": (start_date + timedelta(days=19)).strftime("%Y-%m-%d")},
    ]
    
    # Add all transactions
    for i, txn in enumerate(transactions, 1):
        result = finance_tool.execute("add_transaction", **txn)
        if result.get('success'):
            status = "✅" if txn['type'] == 'income' else "💸"
            print(f"   {status} {txn['date']}: ${txn['amount']:.2f} - {txn['category']} ({txn['type']})")
        else:
            print(f"   ❌ Error adding transaction {i}: {result.get('error')}")
    
    # Add some financial goals
    print("\n🎯 Adding financial goals...")
    goals = [
        {"goal_name": "Emergency Fund", "target_amount": 10000, "target_date": "2025-12-31"},
        {"goal_name": "Vacation Fund", "target_amount": 3000, "target_date": "2025-08-15"},
        {"goal_name": "New Laptop", "target_amount": 2500, "target_date": "2025-09-01"},
    ]
    
    for goal in goals:
        result = finance_tool.execute("add_goal", **goal)
        if result.get('success'):
            print(f"   🎯 {goal['goal_name']}: ${goal['target_amount']:.2f}")
    
    # Simulate some progress on goals
    print("\n📈 Updating goal progress...")
    conn = sqlite3.connect(finance_tool.db_path)
    cursor = conn.cursor()
    
    # Update goal progress (simulate savings)
    goal_progress = [
        ("Emergency Fund", 2500),  # 25% progress
        ("Vacation Fund", 750),    # 25% progress  
        ("New Laptop", 500),       # 20% progress
    ]
    
    for goal_name, progress in goal_progress:
        cursor.execute(
            'UPDATE goals SET current_amount = ? WHERE name = ?',
            (progress, goal_name)
        )
        print(f"   📊 {goal_name}: ${progress:.2f}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 55)
    print("🎉 Demo data created successfully!")
    print("\n📊 What you'll see in the web app:")
    print("   🔴 BUDGET EXCEEDED: Food & Dining (~$464 of $400)")
    print("   🟡 BUDGET WARNING: Transportation (~$199 of $250)")
    print("   🔴 BUDGET EXCEEDED: Entertainment (~$125 of $100)")
    print("   🟢 UNDER BUDGET: Bills & Utilities (~$260 of $300)")
    print("   🟢 UNDER BUDGET: Healthcare (~$60 of $80)")
    print("\n💡 Features demonstrated:")
    print("   • Real-time budget alerts with color coding")
    print("   • Monthly financial summary")
    print("   • Transaction history with filtering")
    print("   • Financial goals with progress tracking")
    print("   • Spending reports and charts")
    print("\n🌐 Open http://localhost:5001 to see the web interface!")

if __name__ == "__main__":
    create_demo_data()
