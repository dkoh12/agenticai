"""
Finance MCP Client with Ollama Llama 3.2 Integration
Natural language interface to the finance MCP server
"""

import asyncio
import json
from typing import Dict, Any, List
import subprocess
import sys
import os

# LangChain and Ollama imports
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class FinanceMCPClient:
    """Client that connects to Finance MCP Server and provides LLM interface"""
    
    def __init__(self):
        self.session = None
        self.llm = None
        self.agent_executor = None
        self.tools = []
        
    async def connect_to_mcp_server(self):
        """Connect to the Finance MCP Server"""
        print("🔌 Connecting to Finance MCP Server...")
        
        # Server parameters - adjust path as needed
        server_params = StdioServerParameters(
            command="python",
            args=["finance_mcp_server.py"],
            env=None
        )
        
        try:
            # Create session with the server
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # Initialize the session
                    await session.initialize()
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    print(f"✅ Connected! Available tools: {len(tools_result.tools)}")
                    
                    for tool in tools_result.tools:
                        print(f"  - {tool.name}: {tool.description}")
                    
                    return session
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            print("Make sure the Finance MCP Server is running!")
            return None
    
    def setup_ollama_llm(self):
        """Setup Ollama Llama 3.2 LLM"""
        print("🦙 Setting up Ollama Llama 3.2...")
        
        try:
            # Check if Ollama is installed and llama3.2 is available
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "llama3.2" not in result.stdout:
                print("📥 Pulling Llama 3.2 model...")
                subprocess.run(["ollama", "pull", "llama3.2"], check=True)
            
            # Initialize Ollama LLM
            self.llm = OllamaLLM(model="llama3.2", temperature=0.1)
            print("✅ Ollama Llama 3.2 ready!")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Ollama not found. Please install Ollama first:")
            print("  1. Visit: https://ollama.ai/download")
            print("  2. Install Ollama")
            print("  3. Run: ollama pull llama3.2")
            return False
        except Exception as e:
            print(f"❌ Error setting up Ollama: {e}")
            return False
    
    def create_mcp_tools(self) -> List[Tool]:
        """Create LangChain tools that call MCP server functions"""
        
        def add_transaction_tool(query: str) -> str:
            """Add a financial transaction. Format: amount|category|description|type"""
            try:
                # Parse the query - handle natural language input
                if '|' not in query:
                    # Try to parse natural language like "50 grocery expense"
                    words = query.lower().split()
                    amount = None
                    category = "general"
                    transaction_type = "expense"
                    
                    for word in words:
                        if word.replace('$', '').replace('.', '').isdigit():
                            amount = float(word.replace('$', ''))
                        elif word in ['income', 'salary', 'pay']:
                            transaction_type = "income"
                        elif word in ['expense', 'cost', 'spend']:
                            transaction_type = "expense"
                        elif word in ['grocery', 'groceries', 'food']:
                            category = "groceries"
                    
                    if amount is None:
                        return "Please specify an amount for the transaction."
                    
                    description = query
                else:
                    # Parse structured format
                    parts = [p.strip() for p in query.split('|')]
                    if len(parts) < 2:
                        return "Please provide: amount|category|description|type"
                    
                    amount = float(parts[0].replace('$', ''))
                    category = parts[1]
                    description = parts[2] if len(parts) > 2 else ""
                    transaction_type = parts[3] if len(parts) > 3 else "expense"
                
                # Call MCP server tool
                result = self.call_mcp_tool("add_transaction", {
                    "amount": amount,
                    "category": category,
                    "description": description,
                    "transaction_type": transaction_type
                })
                
                if result.get("success"):
                    return f"✅ Added {transaction_type}: ${amount} for {category} - {description}"
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        def get_transactions_tool(query: str) -> str:
            """Get recent transactions. Format: limit|category|month (all optional)"""
            try:
                parts = [p.strip() for p in query.split('|')] if query.strip() else []
                
                params = {}
                if len(parts) > 0 and parts[0].isdigit():
                    params["limit"] = int(parts[0])
                if len(parts) > 1 and parts[1]:
                    params["category"] = parts[1]
                if len(parts) > 2 and parts[2]:
                    params["month"] = parts[2]
                
                result = self.call_mcp_tool("get_transactions", params)
                
                if result.get("success"):
                    transactions = result["transactions"]
                    output = f"📋 Found {len(transactions)} transactions:\n"
                    for txn in transactions[:5]:  # Show top 5
                        output += f"  {txn['date']}: ${txn['amount']} - {txn['category']} ({txn['type']})\n"
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"❌ Error getting transactions: {str(e)}"
        
        def get_summary_tool(month: str = "") -> str:
            """Get financial summary for a month (YYYY-MM format, optional)"""
            try:
                params = {"month": month} if month.strip() else {}
                result = self.call_mcp_tool("get_financial_summary", params)
                
                if result.get("success"):
                    s = result
                    output = f"📊 Financial Summary for {s['period']}:\n"
                    output += f"  💰 Income: ${s['total_income']}\n"
                    output += f"  💸 Expenses: ${s['total_expenses']}\n"
                    output += f"  🏦 Net: ${s['net_income']}\n"
                    output += f"  📈 Savings Rate: {s['savings_rate']}%\n"
                    
                    if s['expenses_by_category']:
                        output += "  Top expenses:\n"
                        for cat, amount in list(s['expenses_by_category'].items())[:3]:
                            output += f"    - {cat}: ${amount}\n"
                    
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"❌ Error getting summary: {str(e)}"
        
        def get_budget_tool(query: str = "") -> str:
            """Get budget status and alerts"""
            try:
                result = self.call_mcp_tool("get_budget_status", {})
                
                if result.get("success"):
                    output = f"💰 Budget Status for {result['month']}:\n"
                    
                    # Show alerts first
                    if result['alerts']:
                        output += "🚨 ALERTS:\n"
                        for alert in result['alerts']:
                            output += f"  {alert}\n"
                        output += "\n"
                    
                    # Show budget details
                    for status in result['budget_status'][:5]:  # Top 5
                        output += f"  {status['category']}: ${status['spent']:.2f}/${status['budget']:.2f} ({status['percentage']:.1f}%)\n"
                    
                    return output
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"❌ Error getting budget: {str(e)}"
        
        # Create LangChain tools
        tools = [
            Tool(
                name="add_transaction",
                description="Add a financial transaction (income or expense). Use format: amount|category|description|type",
                func=add_transaction_tool
            ),
            Tool(
                name="get_transactions",
                description="Get recent transactions. Optional format: limit|category|month",
                func=get_transactions_tool
            ),
            Tool(
                name="get_financial_summary",
                description="Get financial summary for current or specific month (YYYY-MM)",
                func=get_summary_tool
            ),
            Tool(
                name="get_budget_status",
                description="Get current budget status and overspending alerts",
                func=get_budget_tool
            )
        ]
        
        return tools
    
    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate calling MCP server tool (in real implementation this would be async)"""
        # For demo purposes, simulate the calls
        # In real implementation, this would call: await self.session.call_tool(tool_name, params)
        
        if tool_name == "add_transaction":
            return {
                "success": True,
                "message": f"Added {params.get('transaction_type', 'expense')} of ${params.get('amount', 0):.2f}"
            }
        elif tool_name == "get_transactions":
            return {
                "success": True,
                "transactions": [
                    {"date": "2025-08-07", "amount": 85.50, "category": "Food & Dining", "type": "expense", "description": "Groceries"},
                    {"date": "2025-08-06", "amount": 3500.00, "category": "Salary", "type": "income", "description": "Monthly salary"},
                    {"date": "2025-08-05", "amount": 45.00, "category": "Transportation", "type": "expense", "description": "Gas"}
                ]
            }
        elif tool_name == "get_financial_summary":
            return {
                "success": True,
                "period": "2025-08",
                "total_income": 3500.00,
                "total_expenses": 143.49,
                "net_income": 3356.51,
                "savings_rate": 95.9,
                "expenses_by_category": {
                    "Food & Dining": 85.50,
                    "Transportation": 45.00,
                    "Entertainment": 12.99
                }
            }
        elif tool_name == "get_budget_status":
            return {
                "success": True,
                "month": "2025-08",
                "alerts": ["⚠️ WARNING: Food & Dining (17.1%)"],
                "budget_status": [
                    {"category": "Food & Dining", "budget": 500, "spent": 85.50, "remaining": 414.50, "percentage": 17.1},
                    {"category": "Transportation", "budget": 300, "spent": 45.00, "remaining": 255.00, "percentage": 15.0}
                ]
            }
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    def setup_agent(self):
        """Setup a simple LangChain agent with MCP tools"""
        if not self.llm:
            print("❌ LLM not initialized")
            return False
        
        # Create tools
        self.tools = self.create_mcp_tools()
        
        # Create a simple agent that directly handles user input
        from langchain.schema import SystemMessage, HumanMessage
        
        def simple_agent(user_input: str) -> str:
            """Simple agent that determines which tool to use based on user input"""
            user_input_lower = user_input.lower()
            
            try:
                if any(word in user_input_lower for word in ['add', 'spent', 'bought', 'paid', 'expense', 'income']):
                    # Add transaction
                    result = self.tools[0].func(user_input)
                    return result
                    
                elif any(word in user_input_lower for word in ['show', 'list', 'recent', 'transactions', 'history']):
                    # Get transactions
                    result = self.tools[1].func("")
                    return result
                    
                elif any(word in user_input_lower for word in ['summary', 'total', 'overview', 'report']):
                    # Get summary
                    result = self.tools[2].func("")
                    return result
                    
                elif any(word in user_input_lower for word in ['budget', 'spending', 'overspent', 'alerts']):
                    # Get budget
                    result = self.tools[3].func("")
                    return result
                    
                else:
                    return "I can help you with:\n• Adding transactions (e.g., 'add $50 grocery expense')\n• Viewing transactions ('show my recent transactions')\n• Financial summaries ('what's my financial summary?')\n• Budget status ('check my budget')"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        self.simple_agent = simple_agent
        print("✅ Agent ready with finance tools!")
        return True
    
    async def chat_loop(self):
        """Interactive chat loop with the finance agent"""
        print("\n" + "="*60)
        print("🏦 Finance Assistant with Ollama Llama 3.2 + MCP")
        print("="*60)
        print("Ask me anything about your finances!")
        print("Examples:")
        print("  - 'Add a $50 grocery expense'")
        print("  - 'Show me my recent transactions'")
        print("  - 'What's my financial summary?'")
        print("  - 'Check my budget status'")
        print("  - Type 'quit' to exit")
        print("="*60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Keep tracking those finances!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Finance Assistant is thinking...")
                
                # Get response from simple agent
                response = self.simple_agent(user_input)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Keep tracking those finances!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function to run the Finance MCP Client"""
    client = FinanceMCPClient()
    
    # Setup Ollama
    if not client.setup_ollama_llm():
        return
    
    # Setup agent
    if not client.setup_agent():
        return
    
    # Note: In a full implementation, you would also connect to MCP server here
    # await client.connect_to_mcp_server()
    
    # Start chat loop
    await client.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
