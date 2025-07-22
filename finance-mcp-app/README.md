# Finance MCP Application

This folder contains a complete personal finance management application built using MCP (Model Context Protocol) with a modern web interface.

## Contents

### Core Application
- `finance_web_app.py` - Flask web application with dashboard
- `finance_mcp_tool.py` - MCP tool for financial data management
- `finance_langchain_integration.py` - LangChain integration for AI features

### Web Interface
- `templates/` - HTML templates for the web interface
  - `base.html` - Base template with navigation
  - `dashboard.html` - Main dashboard with budget alerts
  - `transactions.html` - Transaction management
  - `budgets.html` - Budget setup and monitoring
  - `reports.html` - Financial reports and analytics

### Data Management
- `data/` - Database and data files
  - `finance.db` - SQLite database for financial data
- `create_demo_data.py` - Generate sample data for testing

### Documentation & Utilities
- `WEB_INTERFACE_GUIDE.md` - Complete guide to using the web interface
- `FIXES_APPLIED.md` - Documentation of template fixes and troubleshooting
- `run_finance_web.sh` - Quick start script for the web application

## Features

### 🏦 Financial Management
- **Transaction Tracking** - Record income and expenses
- **Category Management** - Organize transactions by category
- **Budget Monitoring** - Set and track spending limits
- **Goal Setting** - Save towards financial objectives

### 🚨 Smart Alerts
- **Budget Alerts** - Visual warnings when approaching limits
- **Overspending Detection** - Immediate notifications for exceeded budgets
- **Progress Tracking** - Monitor goal achievement

### 📊 Analytics & Reports
- **Interactive Charts** - Visual spending analysis
- **Category Breakdown** - Detailed expense categorization
- **Trend Analysis** - Track financial patterns over time
- **Export Capabilities** - Generate reports for analysis

### 🤖 AI Integration
- **Natural Language Queries** - Ask questions about your finances
- **Smart Categorization** - AI-powered transaction categorization
- **Financial Insights** - Intelligent recommendations

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install flask sqlite3 datetime
   ```

2. **Set Up Database**
   ```bash
   python create_demo_data.py
   ```

3. **Run the Application**
   ```bash
   ./run_finance_web.sh
   # OR
   python finance_web_app.py
   ```

4. **Access the Interface**
   - Open your browser to `http://localhost:5001`
   - Explore the dashboard, transactions, and budgets

## Project Structure

```
finance-mcp-app/
├── finance_web_app.py          # Main Flask application
├── finance_mcp_tool.py         # MCP backend for data management
├── finance_langchain_integration.py  # AI features
├── create_demo_data.py         # Sample data generator
├── run_finance_web.sh          # Quick start script
├── templates/                  # Web interface templates
│   ├── base.html              # Navigation and layout
│   ├── dashboard.html         # Main dashboard
│   ├── transactions.html      # Transaction management
│   ├── budgets.html          # Budget monitoring
│   └── reports.html          # Analytics and reports
├── data/                      # Database files
│   └── finance.db            # SQLite database
└── docs/                     # Documentation
    ├── WEB_INTERFACE_GUIDE.md
    └── FIXES_APPLIED.md
```

## Technology Stack

- **Backend**: Python Flask, SQLite, MCP
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **AI**: LangChain integration for natural language processing
- **Database**: SQLite for lightweight, portable data storage

## Usage Examples

### Adding Transactions
```python
# Via web interface - click "Add Transaction"
# Or via MCP tool directly
from finance_mcp_tool import PersonalFinanceMCPTool

tool = PersonalFinanceMCPTool("data/finance.db")
tool.add_transaction(100.0, "Groceries", "Food", "expense")
```

### Setting Budgets
```python
# Set monthly budget via web interface or MCP
tool.set_budget("Food", 500.0, "monthly")
```

### Budget Alerts
The application automatically monitors budgets and displays:
- 🟢 Green: Under 70% of budget
- 🟡 Yellow: 70-90% of budget  
- 🔴 Red: Over 90% or exceeded budget

## Customization

- **Categories**: Add custom expense/income categories
- **Budget Periods**: Support for daily, weekly, monthly, yearly budgets
- **Reports**: Customize date ranges and filtering
- **Themes**: Modify Bootstrap theme in templates
- **AI Features**: Extend LangChain integration for more insights

## Troubleshooting

See `FIXES_APPLIED.md` for common issues and solutions, including:
- Template syntax errors
- Database connection issues
- Flask server problems
- Chart rendering issues
