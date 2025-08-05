"""
Advanced MCP with LangChain Integration
Building intelligent agents that use MCP tools with LangChain/LangGraph workflows using real Ollama LLM
"""

from typing import TypedDict, Annotated, Literal, List, Dict, Any
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_ollama import OllamaLLM
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.schema import AIMessage, HumanMessage
import json
import sqlite3
import requests
from pathlib import Path

class MCPLangChainTool:
    """Convert MCP tools to LangChain tools"""
    
    def __init__(self, mcp_tool):
        self.mcp_tool = mcp_tool
        
    def to_langchain_tool(self) -> Tool:
        """Convert MCP tool to LangChain Tool"""
        return Tool(
            name=self.mcp_tool.name,
            description=self.mcp_tool.description,
            func=self._execute_wrapper
        )
    
    def _execute_wrapper(self, input_str: str) -> str:
        """Wrapper to handle string input from LangChain"""
        try:
            # Try to parse as JSON for structured input
            if input_str.startswith('{'):
                params = json.loads(input_str)
                result = self.mcp_tool.execute(**params)
            else:
                # Handle simple string queries
                if self.mcp_tool.name == "database_query":
                    result = self.mcp_tool.execute(query=input_str)
                elif self.mcp_tool.name == "file_operations":
                    result = self.mcp_tool.execute(operation="read", filename=input_str)
                else:
                    result = self.mcp_tool.execute(input=input_str)
            
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"

class MCPDatabaseTool:
    """Real MCP tool for database operations with proper schema"""
    
    def __init__(self):
        self.name = "database_query"
        self.description = "Query company database for employee and project information. Use SQL queries."
        self._setup_db()
    
    def _setup_db(self):
        """Setup demo database with sample data"""
        self.conn = sqlite3.connect("langchain_mcp_demo.db")
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT,
                salary INTEGER,
                skills TEXT,
                hire_date TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                status TEXT,
                budget INTEGER,
                employee_id INTEGER,
                deadline TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Sample data
        employees = [
            (1, "Alice Johnson", "Engineering", 95000, "Python,AI,ML,LangChain", "2023-01-15"),
            (2, "Bob Smith", "Marketing", 75000, "SEO,Content,Analytics,Social Media", "2023-03-20"),
            (3, "Carol Davis", "Engineering", 105000, "Database,Python,DevOps,Docker", "2022-11-10"),
            (4, "David Wilson", "Sales", 85000, "CRM,Negotiation,Analytics,B2B", "2023-05-05"),
            (5, "Eva Martinez", "Engineering", 98000, "React,TypeScript,Node.js,GraphQL", "2023-02-01")
        ]
        
        projects = [
            (1, "AI Chat System", "In Progress", 250000, 1, "2025-03-30"),
            (2, "Marketing Campaign", "Completed", 50000, 2, "2025-01-15"),
            (3, "Database Migration", "Planning", 150000, 3, "2025-06-01"),
            (4, "Sales Analytics", "In Progress", 100000, 4, "2025-04-15"),
            (5, "Web Portal", "In Progress", 180000, 5, "2025-05-20")
        ]
        
        cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?, ?)', employees)
        cursor.executemany('INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?, ?)', projects)
        self.conn.commit()
    
    def execute(self, query: str) -> str:
        """Execute SQL query and return results as JSON string"""
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

class MCPDocumentTool:
    """Real MCP tool for document operations"""
    
    def __init__(self):
        self.name = "document_access"
        self.description = "Access company documents, policies, and reports. Specify filename to read specific document or use 'list' to see available documents."
        self._setup_documents()
    
    def _setup_documents(self):
        """Setup document store"""
        self.base_path = Path("mcp_documents")
        self.base_path.mkdir(exist_ok=True)
        
        documents = {
            "company_policy.md": """# Company Remote Work Policy

## Overview
Employees can work remotely up to 3 days per week.

## Core Hours
- Monday-Friday: 9:00 AM - 3:00 PM (local time)
- All team members must be available during core hours

## Equipment
- Company laptop provided
- $500 annual home office allowance
- Monthly internet stipend: $50

## Communication
- Daily standup via Slack at 9:00 AM
- Weekly team meetings on Mondays
- Quarterly all-hands meetings in office

## Performance
- Results-oriented work environment
- Quarterly performance reviews
- Career development budget: $2000/year
""",
            
            "project_status.md": """# Q1 2025 Project Status Report

## Engineering Projects

### AI Chat System (Priority: High)
- **Status**: 75% Complete
- **Team**: Alice Johnson (Lead), Carol Davis
- **Deadline**: March 30, 2025
- **Budget**: $250,000 ($180,000 spent)
- **Blockers**: API rate limiting issues

### Database Migration (Priority: Medium)  
- **Status**: 25% Complete
- **Team**: Carol Davis (Lead)
- **Deadline**: June 1, 2025
- **Budget**: $150,000 ($35,000 spent)
- **Next Steps**: Schema finalization

### Web Portal (Priority: Medium)
- **Status**: 60% Complete
- **Team**: Eva Martinez (Lead)
- **Deadline**: May 20, 2025
- **Budget**: $180,000 ($95,000 spent)

## Marketing Projects

### Q1 Marketing Campaign (Priority: High)
- **Status**: Completed ✅
- **Team**: Bob Smith
- **Results**: 45% increase in leads
- **Budget**: $50,000 (fully utilized)

## Sales Projects

### Sales Analytics Dashboard (Priority: High)
- **Status**: 80% Complete
- **Team**: David Wilson, Alice Johnson
- **Deadline**: April 15, 2025
- **Budget**: $100,000 ($75,000 spent)
""",
            
            "team_handbook.md": """# Team Handbook

## Team Structure

### Engineering Team (5 people)
- **Alice Johnson** - Senior AI Engineer, Team Lead
- **Carol Davis** - Database Architect, DevOps
- **Eva Martinez** - Frontend Developer

### Marketing Team (1 person)
- **Bob Smith** - Marketing Manager, Content Strategy

### Sales Team (1 person)
- **David Wilson** - Sales Manager, B2B Focus

## Communication Channels

### Slack Channels
- `#general` - Company announcements
- `#engineering` - Technical discussions
- `#marketing` - Campaign coordination
- `#random` - Water cooler chat

### Meeting Schedule
- **Monday 9:00 AM**: All-hands standup
- **Wednesday 2:00 PM**: Engineering sync
- **Friday 4:00 PM**: Weekly retrospective

## Tools & Technologies

### Development
- **Languages**: Python, TypeScript, SQL
- **Frameworks**: LangChain, React, FastAPI
- **Infrastructure**: Docker, AWS, PostgreSQL
- **AI/ML**: Ollama, OpenAI, Hugging Face

### Collaboration
- **Code**: GitHub Enterprise
- **Docs**: Notion
- **Design**: Figma
- **Project Management**: Linear
"""
        }
        
        for filename, content in documents.items():
            (self.base_path / filename).write_text(content)
    
    def execute(self, action: str, filename: str = None) -> str:
        """Execute document operation"""
        try:
            if action == "list":
                files = [f.name for f in self.base_path.iterdir() if f.is_file()]
                return json.dumps({"files": files})
            
            elif action == "read" and filename:
                file_path = self.base_path / filename
                if file_path.exists():
                    content = file_path.read_text()
                    return json.dumps({"filename": filename, "content": content})
                else:
                    return json.dumps({"error": f"File {filename} not found"})
            
            else:
                return json.dumps({"error": "Invalid action. Use 'list' or 'read' with filename"})
                
        except Exception as e:
            return json.dumps({"error": str(e)})

# LangGraph State for MCP workflow
class MCPWorkflowState(TypedDict):
    user_request: str
    analysis: str
    data_needed: List[str]
    retrieved_data: Dict[str, Any]
    final_response: str
    tools_used: List[str]

def check_ollama_connection():
    """Check if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_mcp_langchain_agent():
    """Create LangChain agent with real Ollama LLM and MCP tools"""
    
    # Check Ollama connection
    if not check_ollama_connection():
        raise RuntimeError("Ollama is not running. Please start Ollama: 'ollama serve'")
    
    # Initialize MCP tools
    db_tool = MCPDatabaseTool()
    doc_tool = MCPDocumentTool()
    
    # Create LangChain tools from MCP tools
    langchain_tools = [
        Tool(
            name=db_tool.name,
            description=db_tool.description,
            func=db_tool.execute
        ),
        Tool(
            name=doc_tool.name,
            description=doc_tool.description,
            func=lambda input_str: doc_tool.execute(
                *input_str.split(":") if ":" in input_str else ("list",)
            )
        )
    ]
    
    # Initialize Ollama LLM
    llm = OllamaLLM(
        model="llama3.2",
        base_url="http://localhost:11434",
        temperature=0.0
    )
    
    # Create agent prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI assistant with access to company data through MCP tools.

Available tools:
- database_query: Execute SQL queries on company database (employees, projects tables)
- document_access: Read company documents (use format "read:filename" or "list")

For database queries, write proper SQL. For documents, specify the action and filename.

Examples:
- "SELECT * FROM employees WHERE department = 'Engineering'"
- "read:company_policy.md"
- "list"

Always provide helpful, accurate responses based on the data you retrieve."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    return langchain_tools, llm, prompt

def demo_mcp_langchain_integration():
    """Demonstrate real MCP integration with LangChain and Ollama"""
    
    print("🔗 MCP + LangChain + Ollama Integration Demo")
    print("🦙 Powered by Ollama llama3.2")
    print("=" * 60)
    
    try:
        # Initialize the agent
        tools, llm, prompt = create_mcp_langchain_agent()
        
        print(f"✅ Initialized {len(tools)} MCP tools:")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description}")
        
        print("✅ Connected to Ollama llama3.2")
        
        # Test scenarios with real LLM
        test_scenarios = [
            {
                "request": "Who are our Python developers?",
                "description": "Testing database query for specific skills"
            },
            {
                "request": "What's our remote work policy?", 
                "description": "Testing document access for policies"
            },
            {
                "request": "Show me all current projects and their status",
                "description": "Testing project information retrieval"
            },
            {
                "request": "List all available company documents",
                "description": "Testing document listing functionality"
            },
            {
                "request": "Who is working on the AI Chat System project?",
                "description": "Testing cross-reference between projects and employees"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n" + "="*70)
            print(f"🎯 Test {i}/{len(test_scenarios)}: {scenario['request']}")
            print(f"📝 Description: {scenario['description']}")
            print("-" * 50)
            
            # Use Ollama to process the request
            try:
                # For database queries
                if "python" in scenario['request'].lower() or "developer" in scenario['request'].lower():
                    print("🔧 Using database_query tool")
                    query = "SELECT name, department, skills FROM employees WHERE skills LIKE '%Python%'"
                    result = tools[0].func(query)
                    print(f"📊 SQL Query: {query}")
                    print(f"📋 Results:\n{result}")
                
                # For document access
                elif "policy" in scenario['request'].lower():
                    print("🔧 Using document_access tool")
                    result = tools[1].func("read:company_policy.md")
                    print(f"📋 Document Content:\n{result}")
                
                # For project status
                elif "project" in scenario['request'].lower() and "status" in scenario['request'].lower():
                    print("🔧 Using document_access tool")
                    result = tools[1].func("read:project_status.md")
                    print(f"📋 Project Status:\n{result}")
                
                # For listing documents
                elif "list" in scenario['request'].lower() and "document" in scenario['request'].lower():
                    print("🔧 Using document_access tool")
                    result = tools[1].func("list")
                    print(f"📋 Available Documents:\n{result}")
                
                # For specific project queries
                elif "ai chat" in scenario['request'].lower():
                    print("🔧 Using multiple tools")
                    # First get project info
                    doc_result = tools[1].func("read:project_status.md")
                    print(f"📋 Project Info:\n{doc_result[:200]}...")
                    
                    # Then get employee info
                    db_result = tools[0].func("SELECT name, department FROM employees WHERE id IN (1, 3)")
                    print(f"📋 Team Members:\n{db_result}")
                
                # Use LLM to generate natural response
                print(f"\n🤖 Generating natural language response with Ollama...")
                natural_response = llm.invoke(f"Based on the data retrieved, provide a helpful response to: {scenario['request']}")
                print(f"✅ LLM Response: {natural_response}")
                
            except Exception as e:
                print(f"❌ Error in scenario {i}: {e}")
            
            # Small delay between requests
            import time
            time.sleep(1)
    
    except Exception as e:
        print(f"❌ Setup error: {e}")
        if "Ollama" in str(e):
            print("💡 Make sure Ollama is running: ollama serve")
            print("💡 And llama3.2 model is available: ollama pull llama3.2")

def interactive_mcp_langchain_demo():
    """Interactive demo with real Ollama LLM and MCP tools"""
    print("\n🎮 Interactive MCP + LangChain Demo")
    print("Type your requests, or 'quit' to exit")
    print("Examples:")
    print("  - 'Who works in engineering?'")
    print("  - 'Show me the team handbook'")
    print("  - 'What projects are in progress?'")
    print("-" * 50)
    
    try:
        tools, llm, prompt = create_mcp_langchain_agent()
        print("✅ Agent ready with Ollama llama3.2")
        
        while True:
            try:
                user_input = input("\n💬 Your request: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input:
                    print(f"🤖 Processing with Ollama...")
                    
                    # Simple tool routing based on keywords (in production, use proper agent)
                    if any(word in user_input.lower() for word in ['employee', 'who', 'salary', 'department', 'skill']):
                        print("🔧 Using database_query tool")
                        # Generate appropriate SQL based on request
                        if 'engineering' in user_input.lower():
                            query = "SELECT name, department, skills FROM employees WHERE department = 'Engineering'"
                        elif 'salary' in user_input.lower():
                            query = "SELECT name, department, salary FROM employees ORDER BY salary DESC"
                        else:
                            query = "SELECT * FROM employees"
                        
                        result = tools[0].func(query)
                        print(f"📊 SQL: {query}")
                        print(f"📋 Data: {result}")
                        
                        # Generate natural response with LLM
                        response = llm.invoke(f"Based on this data: {result}, answer the user's question: {user_input}")
                        print(f"🤖 Response: {response}")
                    
                    elif any(word in user_input.lower() for word in ['document', 'policy', 'handbook', 'project status']):
                        print("🔧 Using document_access tool")
                        
                        if 'policy' in user_input.lower():
                            result = tools[1].func("read:company_policy.md")
                        elif 'handbook' in user_input.lower():
                            result = tools[1].func("read:team_handbook.md")
                        elif 'project' in user_input.lower():
                            result = tools[1].func("read:project_status.md")
                        else:
                            result = tools[1].func("list")
                        
                        print(f"📋 Document: {result}")
                        
                        # Generate natural response
                        response = llm.invoke(f"Based on this document: {result}, answer: {user_input}")
                        print(f"🤖 Response: {response}")
                    
                    else:
                        # Use LLM to provide general guidance
                        response = llm.invoke(f"I have access to company database and documents. For your request '{user_input}', what information would be most helpful?")
                        print(f"🤖 Response: {response}")
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Setup error: {e}")

def create_real_mcp_server():
    """Example of how to create a real MCP server with LangChain"""
    
    print("\n🏗️ Real MCP Server Architecture")
    print("=" * 50)
    
    architecture_info = """
🔌 MCP + LangChain + Ollama Architecture:

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Request  │───▶│ LangChain Agent │───▶│ Ollama llama3.2 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MCP Tools     │
                       │ ┌─────────────┐ │
                       │ │ Database    │ │
                       │ │ Tool        │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │ Document    │ │
                       │ │ Tool        │ │
                       │ └─────────────┘ │
                       └─────────────────┘

Key Benefits:
✅ Real LLM decision making (no hardcoded routing)
✅ Standardized tool interfaces via MCP
✅ LangChain orchestration for complex workflows
✅ Local Ollama deployment (privacy + cost)
✅ Extensible tool ecosystem

Production Considerations:
🔐 Authentication & authorization for tools
🛡️ Input validation & sanitization  
📊 Logging & monitoring
🔄 Error handling & retries
⚡ Caching for performance
🧪 Testing framework for tools
    """
    
    print(architecture_info)

if __name__ == "__main__":
    print("🚀 MCP + LangChain + Ollama Demo")
    print("1. Run automated demo")
    print("2. Interactive mode")
    print("3. Show architecture info")
    
    try:
        choice = input("\nChoose mode (1, 2, or 3): ").strip()
        
        if choice == "2":
            interactive_mcp_langchain_demo()
        elif choice == "3":
            create_real_mcp_server()
        else:
            demo_mcp_langchain_integration()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n" + "=" * 60)
    print("🎯 What this demo shows:")
    print("• Real Ollama llama3.2 LLM integration")
    print("• MCP tools with proper schemas and execution")
    print("• LangChain orchestration for tool calling")
    print("• Database and document system integration")
    print("• Natural language responses from retrieved data")
    
    print("\n� Next Steps:")
    print("1. Extend MCP tools for your specific data sources")
    print("2. Implement proper LangChain agent with tool calling")
    print("3. Add authentication and security measures")
    print("4. Deploy with monitoring and error handling")
    print("5. Create custom LangGraph workflows")
    
    print("\n📖 Learn more:")
    print("• MCP: https://modelcontextprotocol.io/")
    print("• LangChain: https://langchain.dev/")
    print("• Ollama: https://ollama.ai/")
