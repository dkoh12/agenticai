"""
Personal Finance MCP + LangChain Integration
Natural language interface for your personal finance tracking
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finance_mcp_tool import PersonalFinanceMCPTool
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import json
import re

# Import our free LLM for testing
sys.path.append('/Users/davidkoh/devel/llm/agenticai/examples')
from free_practice import FreeLLM

class FinanceLangChainAgent:
    """LangChain agent that can manage personal finances using natural language"""
    
    def __init__(self):
        self.finance_tool = PersonalFinanceMCPTool()
        self.llm = FreeLLM()  # Use free LLM for demo
        self._setup_tools()
        self._setup_chain()
    
    def _setup_tools(self):
        """Create LangChain tools from MCP finance tool"""
        
        def add_expense(query: str) -> str:
            """Add an expense transaction. Format: 'amount|category|description'"""
            try:
                parts = query.split('|')
                if len(parts) < 2:
                    return "Please provide: amount|category|description"
                
                amount = float(parts[0].strip().replace('$', ''))
                category = parts[1].strip()
                description = parts[2].strip() if len(parts) > 2 else ""
                
                result = self.finance_tool.execute(
                    "add_transaction",
                    amount=amount,
                    category=category,
                    description=description,
                    type="expense"
                )
                
                if result['success']:
                    return f"✅ Added expense: ${amount:.2f} for {category}"
                else:
                    return f"❌ Error: {result['error']}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def add_income(query: str) -> str:
            """Add an income transaction. Format: 'amount|category|description'"""
            try:
                parts = query.split('|')
                amount = float(parts[0].strip().replace('$', ''))
                category = parts[1].strip() if len(parts) > 1 else "Income"
                description = parts[2].strip() if len(parts) > 2 else ""
                
                result = self.finance_tool.execute(
                    "add_transaction",
                    amount=amount,
                    category=category,
                    description=description,
                    type="income"
                )
                
                if result['success']:
                    return f"✅ Added income: ${amount:.2f} from {category}"
                else:
                    return f"❌ Error: {result['error']}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def get_summary(query: str = "") -> str:
            """Get financial summary for current month"""
            result = self.finance_tool.execute("get_summary")
            
            if result['success']:
                return f"""📊 Financial Summary for {result['period']}:
• Income: ${result['total_income']:.2f}
• Expenses: ${result['total_expenses']:.2f}
• Net Income: ${result['net_income']:.2f}
• Savings Rate: {result['savings_rate']:.1f}%

Top Spending Categories:
{self._format_categories(result['expenses_by_category'])}"""
            else:
                return f"❌ Error: {result['error']}"
        
        def get_recent_transactions(query: str = "5") -> str:
            """Get recent transactions. Specify number as query."""
            try:
                limit = int(query) if query.isdigit() else 5
                result = self.finance_tool.execute("get_transactions", limit=limit)
                
                if result['success']:
                    transactions = result['transactions']
                    output = f"📋 Last {len(transactions)} transactions:\n"
                    
                    for txn in transactions:
                        output += f"• {txn['date']}: ${txn['amount']:.2f} - {txn['category']} ({txn['type']})\n"
                        if txn['description']:
                            output += f"  📝 {txn['description']}\n"
                    
                    return output
                else:
                    return f"❌ Error: {result['error']}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def spending_report(query: str = "30") -> str:
            """Get spending report. Specify days as query."""
            try:
                days = int(query) if query.isdigit() else 30
                result = self.finance_tool.execute("spending_report", days=days)
                
                if result['success']:
                    output = f"📈 Spending Report (Last {days} days):\n"
                    for item in result['spending_report']:
                        output += f"• {item['category']}: ${item['total']:.2f} ({item['transactions']} transactions)\n"
                        output += f"  Average: ${item['average']:.2f} per transaction\n"
                    return output
                else:
                    return f"❌ Error: {result['error']}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        # Create LangChain tools
        self.tools = [
            Tool(
                name="add_expense",
                description="Add an expense transaction. Use format: amount|category|description",
                func=add_expense
            ),
            Tool(
                name="add_income", 
                description="Add an income transaction. Use format: amount|category|description",
                func=add_income
            ),
            Tool(
                name="get_summary",
                description="Get monthly financial summary with income, expenses, and savings rate",
                func=get_summary
            ),
            Tool(
                name="get_transactions",
                description="Get recent transactions. Specify number of transactions to show",
                func=get_recent_transactions
            ),
            Tool(
                name="spending_report",
                description="Get spending report by category. Specify number of days to analyze",
                func=spending_report
            )
        ]
    
    def _format_categories(self, categories_dict: dict) -> str:
        """Format categories dictionary for display"""
        output = ""
        for category, amount in list(categories_dict.items())[:3]:  # Top 3
            output += f"  • {category}: ${amount:.2f}\n"
        return output
    
    def _setup_chain(self):
        """Setup the LangChain processing chain"""
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a personal finance assistant. Help users manage their money by:

1. Understanding natural language requests about finances
2. Converting them to appropriate tool calls
3. Providing helpful summaries and insights

Available tools and their formats:
- add_expense: "amount|category|description" (e.g., "15.50|Food & Dining|Lunch at cafe")
- add_income: "amount|category|description" (e.g., "3000|Salary|Monthly salary")
- get_summary: Get monthly financial overview
- get_transactions: Show recent transactions (specify number)
- spending_report: Analyze spending patterns (specify days)

Common expense categories: Food & Dining, Transportation, Shopping, Entertainment, Bills & Utilities, Healthcare, Education
Common income categories: Salary, Freelance, Investments

Examples:
User: "I spent $25 on lunch today"
→ Use add_expense with: "25|Food & Dining|lunch"

User: "Show me my spending this month"  
→ Use get_summary

User: "What did I spend money on recently?"
→ Use get_transactions

Be conversational and helpful. Ask for clarification if needed."""),
            ("human", "{input}")
        ])
        
        self.output_parser = StrOutputParser()
    
    def process_request(self, user_input: str) -> str:
        """Process a natural language finance request"""
        
        # Simple pattern matching for demo (in real app, use LLM to determine intent)
        user_lower = user_input.lower()
        
        # Expense patterns
        if any(word in user_lower for word in ['spent', 'bought', 'paid', 'expense', 'cost']):
            return self._handle_expense_request(user_input)
        
        # Income patterns  
        elif any(word in user_lower for word in ['earned', 'income', 'salary', 'paid me', 'received']):
            return self._handle_income_request(user_input)
        
        # Summary patterns
        elif any(word in user_lower for word in ['summary', 'overview', 'total', 'how much', 'spending this month']):
            return self.tools[2].func("")  # get_summary
        
        # Recent transactions
        elif any(word in user_lower for word in ['recent', 'last', 'transactions', 'history']):
            return self.tools[3].func("10")  # get_transactions
        
        # Spending report
        elif any(word in user_lower for word in ['report', 'analysis', 'categories', 'breakdown']):
            return self.tools[4].func("30")  # spending_report
        
        else:
            return """I can help you with:
• Adding expenses: "I spent $25 on groceries"
• Adding income: "I earned $500 from freelancing"  
• Getting summaries: "Show me my monthly summary"
• Viewing transactions: "Show me recent transactions"
• Spending reports: "Give me a spending breakdown"

What would you like to do?"""
    
    def _handle_expense_request(self, user_input: str) -> str:
        """Handle expense addition requests"""
        
        # Extract amount using regex
        amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', user_input)
        if not amount_match:
            return "I couldn't find an amount. Please specify how much you spent (e.g., '$25' or '25')"
        
        amount = amount_match.group(1)
        
        # Determine category based on keywords
        user_lower = user_input.lower()
        category = "Other"
        
        if any(word in user_lower for word in ['food', 'lunch', 'dinner', 'coffee', 'restaurant', 'grocery']):
            category = "Food & Dining"
        elif any(word in user_lower for word in ['gas', 'uber', 'taxi', 'bus', 'train', 'car']):
            category = "Transportation"
        elif any(word in user_lower for word in ['clothes', 'shopping', 'store', 'amazon', 'bought']):
            category = "Shopping"
        elif any(word in user_lower for word in ['movie', 'game', 'entertainment', 'show']):
            category = "Entertainment"
        elif any(word in user_lower for word in ['rent', 'utility', 'bill', 'electric', 'internet']):
            category = "Bills & Utilities"
        
        # Extract description (simplified)
        description = user_input.replace('$', '').replace(amount, '').strip()
        
        # Call the tool
        tool_input = f"{amount}|{category}|{description}"
        return self.tools[0].func(tool_input)  # add_expense
    
    def _handle_income_request(self, user_input: str) -> str:
        """Handle income addition requests"""
        
        # Extract amount
        amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', user_input)
        if not amount_match:
            return "I couldn't find an amount. Please specify how much you earned."
        
        amount = amount_match.group(1)
        
        # Determine category
        user_lower = user_input.lower()
        category = "Income"
        
        if any(word in user_lower for word in ['salary', 'paycheck', 'job']):
            category = "Salary"
        elif any(word in user_lower for word in ['freelance', 'consulting', 'contract']):
            category = "Freelance"
        elif any(word in user_lower for word in ['investment', 'dividend', 'stock']):
            category = "Investments"
        
        description = user_input.replace('$', '').replace(amount, '').strip()
        
        tool_input = f"{amount}|{category}|{description}"
        return self.tools[1].func(tool_input)  # add_income

def demo_natural_language_finance():
    """Demo natural language finance management"""
    
    print("🤖 Natural Language Finance Assistant")
    print("=" * 50)
    
    agent = FinanceLangChainAgent()
    
    # Demo conversations
    test_queries = [
        "I spent $45 on groceries today",
        "I earned $2500 from my freelance project",
        "I bought coffee for $4.50 this morning", 
        "Show me my monthly summary",
        "What did I spend money on recently?",
        "Give me a spending breakdown",
        "I paid $120 for my electric bill"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n💬 User: {query}")
        print("-" * 30)
        
        response = agent.process_request(query)
        print(f"🤖 Assistant: {response}")

if __name__ == "__main__":
    demo_natural_language_finance()
    
    print("\n" + "=" * 50)
    print("🎯 This Natural Language Finance Tool Shows:")
    print("• How MCP tools integrate seamlessly with LangChain")
    print("• Natural language to structured data conversion")
    print("• Real-world utility (actually track your finances!)")
    print("• Pattern recognition and intent classification") 
    print("• Tool chaining and result formatting")
    
    print("\n🚀 Enhancements You Could Add:")
    print("• Voice input/output for hands-free tracking")
    print("• Receipt photo OCR for automatic expense entry")
    print("• Budget alerts and spending notifications")
    print("• Integration with bank APIs for automatic import")
    print("• Machine learning for category prediction")
    print("• Financial goal recommendations")
    
    print("\n💡 Why This is a Perfect Learning Project:")
    print("• Combines multiple AI concepts (NLP, classification, tools)")
    print("• Solves a real daily problem")
    print("• Scales from simple to very sophisticated")
    print("• Safe to experiment with (your own data)")
    print("• Immediately useful and motivating")
