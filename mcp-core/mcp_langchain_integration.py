"""
Advanced MCP with LangChain Integration
Building intelligent agents that use MCP tools with LangChain/LangGraph workflows
"""

from typing import TypedDict, Annotated, Literal, List, Dict, Any
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
import json
import sqlite3
from pathlib import Path

# Import our free LLM from the practice module
import sys
sys.path.append('../')

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

# Import our MCP tools from the previous example
class SimpleDatabaseTool:
    """Simplified database tool for LangChain integration"""
    
    def __init__(self):
        self.name = "company_database"
        self.description = "Query company database for employee and project information"
        self._setup_db()
    
    def _setup_db(self):
        """Setup in-memory database"""
        self.conn = sqlite3.connect(":memory:")
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT,
                salary INTEGER,
                skills TEXT
            )
        ''')
        
        employees = [
            (1, "Alice Johnson", "Engineering", 95000, "Python,AI,ML"),
            (2, "Bob Smith", "Marketing", 75000, "SEO,Content,Analytics"),
            (3, "Carol Davis", "Engineering", 105000, "Database,Python,DevOps"),
            (4, "David Wilson", "Sales", 85000, "CRM,Negotiation,Analytics")
        ]
        
        cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?, ?)', employees)
        self.conn.commit()
    
    def execute(self, query: str) -> List[Dict]:
        """Execute database query"""
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            return [{"error": str(e)}]

class SimpleFileSystemTool:
    """Simplified file system tool"""
    
    def __init__(self):
        self.name = "document_manager"
        self.description = "Access and manage company documents and reports"
        self.documents = {
            "company_policy.txt": "Remote work policy: Employees can work remotely 3 days per week. Core hours are 9 AM - 3 PM.",
            "project_status.txt": "Q1 Projects: AI Chat (80% complete), Database Migration (30% complete), Marketing Campaign (completed)",
            "team_handbook.txt": "Team structure: Engineering (Alice, Carol), Marketing (Bob), Sales (David). Weekly meetings on Mondays."
        }
    
    def execute(self, operation: str, filename: str = None) -> Dict:
        """Execute file operation"""
        if operation == "list":
            return {"files": list(self.documents.keys())}
        elif operation == "read" and filename:
            if filename in self.documents:
                return {"content": self.documents[filename]}
            else:
                return {"error": f"File {filename} not found"}
        else:
            return {"error": "Invalid operation"}

# LangGraph State for MCP workflow
class MCPWorkflowState(TypedDict):
    user_request: str
    analysis: str
    data_needed: List[str]
    retrieved_data: Dict[str, Any]
    final_response: str
    tools_used: List[str]

# Free LLM for demonstration
class FreeLLM:
    """Simple mock LLM for MCP demonstrations"""
    
    def invoke(self, messages):
        if isinstance(messages, list):
            content = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        else:
            content = str(messages)
        
        content_lower = content.lower()
        
        if "analyze" in content_lower and "request" in content_lower:
            return self._analyze_request(content)
        elif "determine" in content_lower and "data" in content_lower:
            return self._determine_data_needs(content)
        elif "synthesize" in content_lower:
            return self._synthesize_response(content)
        else:
            return "I'm a mock LLM. In production, use ChatOpenAI here."
    
    def _analyze_request(self, content):
        if "employee" in content.lower():
            return "User is asking about employee information. This requires database access."
        elif "project" in content.lower():
            return "User wants project information. Need to check both database and documents."
        elif "policy" in content.lower() or "handbook" in content.lower():
            return "User needs policy/handbook information. Check document system."
        else:
            return "General information request. May need multiple data sources."
    
    def _determine_data_needs(self, content):
        if "employee" in content.lower():
            return "database:employees,documents:team_handbook"
        elif "project" in content.lower():
            return "database:employees,documents:project_status"
        else:
            return "documents:company_policy"
    
    def _synthesize_response(self, content):
        return "Based on the retrieved data, here's a comprehensive response to the user's question..."

def create_mcp_workflow():
    """Create LangGraph workflow that uses MCP tools"""
    
    # Initialize tools
    db_tool = SimpleDatabaseTool()
    file_tool = SimpleFileSystemTool()
    
    # Convert to LangChain tools
    db_langchain = Tool(
        name="database_query",
        description="Query company database",
        func=lambda q: json.dumps(db_tool.execute(q), indent=2)
    )
    
    file_langchain = Tool(
        name="document_access",
        description="Access company documents",
        func=lambda params: json.dumps(file_tool.execute(**json.loads(params) if params.startswith('{') else {"operation": "read", "filename": params}), indent=2)
    )
    
    return [db_langchain, file_langchain], FreeLLM()

def demo_mcp_langchain_integration():
    """Demonstrate MCP integration with LangChain workflow"""
    
    print("🔗 MCP + LangChain Integration Demo")
    print("=" * 50)
    
    tools, llm = create_mcp_workflow()
    
    print(f"✅ Initialized {len(tools)} MCP tools:")
    for tool in tools:
        print(f"   • {tool.name}: {tool.description}")
    
    # Simulate intelligent workflow
    test_scenarios = [
        {
            "request": "Who are our Python developers?",
            "expected_tools": ["database_query"],
            "query": "SELECT name, department, skills FROM employees WHERE skills LIKE '%Python%'"
        },
        {
            "request": "What's our remote work policy?",
            "expected_tools": ["document_access"],
            "query": '{"operation": "read", "filename": "company_policy.txt"}'
        },
        {
            "request": "Give me a team overview with current projects",
            "expected_tools": ["database_query", "document_access"],
            "queries": [
                "SELECT * FROM employees",
                '{"operation": "read", "filename": "project_status.txt"}'
            ]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n" + "="*50)
        print(f"🎯 Scenario {i}: {scenario['request']}")
        print("-" * 30)
        
        # Step 1: Analyze request
        analysis_prompt = f"Analyze this user request and determine what data is needed: {scenario['request']}"
        analysis = llm.invoke(analysis_prompt)
        print(f"📊 Analysis: {analysis}")
        
        # Step 2: Execute appropriate tools
        if scenario['request'] == test_scenarios[0]['request']:  # Python developers
            print(f"🔧 Using tool: {tools[0].name}")
            result = tools[0].func(scenario['query'])
            print(f"📋 Results:\n{result}")
            
        elif scenario['request'] == test_scenarios[1]['request']:  # Remote work policy
            print(f"🔧 Using tool: {tools[1].name}")
            result = tools[1].func(scenario['query'])
            print(f"📋 Results:\n{result}")
            
        else:  # Team overview - multiple tools
            print("🔧 Using multiple tools:")
            for j, query in enumerate(scenario['queries']):
                tool = tools[j % len(tools)]
                print(f"   Tool {j+1}: {tool.name}")
                result = tool.func(query)
                print(f"   Result: {result[:100]}...")
        
        # Step 3: Synthesize response
        synthesis_prompt = f"Synthesize a user-friendly response based on the retrieved data for: {scenario['request']}"
        final_response = llm.invoke(synthesis_prompt)
        print(f"✅ Final Response: {final_response}")

def create_real_mcp_server():
    """Example of how to create a real MCP server"""
    
    print("\n🏗️ Building a Real MCP Server")
    print("=" * 40)
    
    server_code = '''
# Real MCP Server Implementation (conceptual)

from mcp import MCPServer, Tool, Resource
import asyncio

class CompanyMCPServer(MCPServer):
    """Production MCP server for company data"""
    
    def __init__(self):
        super().__init__(name="company-data-server")
        self.register_tools()
        self.register_resources()
    
    def register_tools(self):
        """Register available tools"""
        
        @self.tool("employee_lookup")
        async def employee_lookup(name: str = None, department: str = None):
            """Look up employee information"""
            # Implementation here
            pass
        
        @self.tool("document_search")
        async def document_search(query: str, doc_type: str = None):
            """Search company documents"""
            # Implementation here
            pass
    
    def register_resources(self):
        """Register data resources"""
        
        @self.resource("company://employees")
        async def employees_resource():
            """Employee database resource"""
            # Implementation here
            pass
        
        @self.resource("company://documents")
        async def documents_resource():
            """Document store resource"""
            # Implementation here
            pass

# Usage with LangChain
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(
    server_url="mcp://company-data-server",
    auth_token="your-auth-token"
)

agent = create_agent(
    tools=toolkit.get_tools(),
    llm=ChatOpenAI()
)
'''
    
    print("Key components of a real MCP server:")
    print("• Tool registration with async functions")
    print("• Resource management for data sources")
    print("• Authentication and authorization")
    print("• Error handling and validation")
    print("• Protocol compliance")
    
    print(f"\n💻 Example server code:\n{server_code}")

if __name__ == "__main__":
    demo_mcp_langchain_integration()
    create_real_mcp_server()
    
    print("\n" + "=" * 50)
    print("🎯 MCP System Architecture:")
    print("1. 🔌 MCP Tools: Define interfaces to external systems")
    print("2. 🤖 AI Agent: Uses tools through standardized protocol")
    print("3. 🔗 LangChain: Orchestrates tool usage and workflows")
    print("4. 🏗️ MCP Server: Hosts tools and manages access")
    print("5. 🛡️ Security: Authentication, validation, sandboxing")
    
    print("\n💡 Benefits of MCP:")
    print("• Standardized tool interfaces")
    print("• Secure data access")
    print("• Multi-modal data integration") 
    print("• Scalable architecture")
    print("• Reusable components")
    
    print("\n🚀 Next Steps:")
    print("1. Define your data sources and tools")
    print("2. Implement MCP tool interfaces")
    print("3. Create LangChain agents that use MCP tools")
    print("4. Build workflows with LangGraph")
    print("5. Deploy with proper security and monitoring")
