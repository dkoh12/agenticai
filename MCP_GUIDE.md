# 🔌 Model Context Protocol (MCP) System Guide

This guide shows you how to build AI systems using the Model Context Protocol (MCP) with LangChain and LangGraph.

## 🎯 What is Model Context Protocol (MCP)?

MCP is a standardized protocol that allows AI applications to:
- **Securely connect** to external data sources (databases, files, APIs)
- **Use tools** in a standardized way across different AI providers
- **Maintain context** across different systems and sessions
- **Scale safely** with proper authentication and sandboxing

## 🏗️ MCP Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   MCP Server    │    │  Data Sources   │
│  (LangChain)    │◄──►│   (Protocol)    │◄──►│ (DB, Files, API)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
    ┌───▼────┐              ┌───▼────┐              ┌───▼────┐
    │ Tools  │              │  Auth  │              │ Cache  │
    │ Chain  │              │ & Log  │              │ & Pool │
    └────────┘              └────────┘              └────────┘
```

## 📁 Project Structure

```
mcp_project/
├── mcp/
│   ├── __init__.py
│   ├── tools/              # MCP tool implementations
│   │   ├── database.py
│   │   ├── filesystem.py
│   │   └── api_client.py
│   ├── server.py           # MCP server implementation
│   └── protocol.py         # Protocol definitions
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Base agent with MCP integration
│   └── specialized_agents.py
├── workflows/
│   ├── __init__.py
│   └── langgraph_workflows.py
├── examples/               # Working examples
│   ├── basic_mcp_demo.py
│   ├── langchain_integration.py
│   └── production_example.py
├── config/
│   ├── settings.py
│   └── mcp_manifest.json
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install langchain langgraph sqlite3 asyncio pathlib
```

### 2. Define Your MCP Tools

```python
from mcp import MCPTool
import asyncio

class DatabaseTool(MCPTool):
    def __init__(self, connection_string):
        super().__init__(
            name="database_query",
            description="Query company database"
        )
        self.connection_string = connection_string
    
    async def execute(self, sql: str, params: list = None):
        # Your database logic here
        pass
```

### 3. Create MCP Server

```python
from mcp import MCPServer

server = MCPServer("my-company-server")
server.register_tool(DatabaseTool("sqlite:///company.db"))
server.register_tool(FileSystemTool("./documents"))
```

### 4. Integrate with LangChain

```python
from langchain.tools import Tool
from langchain.agents import create_openai_functions_agent

# Convert MCP tools to LangChain tools
langchain_tools = [
    Tool.from_mcp_tool(tool) 
    for tool in server.get_tools()
]

# Create agent
agent = create_openai_functions_agent(
    llm=ChatOpenAI(),
    tools=langchain_tools
)
```

## 🔧 Building MCP Tools

### Database Tool Example

```python
class DatabaseMCPTool(MCPTool):
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["query", "insert", "update"]},
                "sql": {"type": "string"},
                "params": {"type": "array"}
            },
            "required": ["operation", "sql"]
        }
    
    async def execute(self, operation: str, sql: str, params: list = None):
        # Secure SQL execution with validation
        if not self._validate_sql(sql):
            return {"error": "Invalid SQL"}
        
        # Execute query safely
        return await self._execute_query(sql, params)
```

### File System Tool Example

```python
class FileSystemMCPTool(MCPTool):
    def __init__(self, base_path: str):
        super().__init__("file_system", "File operations")
        self.base_path = Path(base_path)
    
    async def execute(self, operation: str, path: str = None, content: str = None):
        # Validate path is within allowed directory
        full_path = (self.base_path / path).resolve()
        if not str(full_path).startswith(str(self.base_path)):
            return {"error": "Path outside allowed directory"}
        
        if operation == "read":
            return {"content": full_path.read_text()}
        elif operation == "write":
            full_path.write_text(content)
            return {"success": True}
```

## 🤖 LangChain Integration Patterns

### Simple Agent Pattern

```python
# Convert MCP tools to LangChain
def mcp_to_langchain_tool(mcp_tool):
    def tool_func(input_str):
        # Parse input and call MCP tool
        params = json.loads(input_str)
        result = asyncio.run(mcp_tool.execute(**params))
        return json.dumps(result)
    
    return Tool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        func=tool_func
    )

# Create agent
tools = [mcp_to_langchain_tool(tool) for tool in mcp_server.tools.values()]
agent = create_openai_functions_agent(llm, tools)
```

### LangGraph Workflow Pattern

```python
from langgraph.graph import StateGraph, END

class MCPWorkflowState(TypedDict):
    user_request: str
    tool_results: Dict[str, Any]
    final_response: str

def route_to_tools(state):
    # Determine which MCP tools to use
    request = state["user_request"].lower()
    if "database" in request:
        return "use_database"
    elif "file" in request:
        return "use_files"
    else:
        return "general_response"

def use_database_tool(state):
    # Call MCP database tool
    result = mcp_server.call_tool("database_query", 
                                  operation="query", 
                                  sql="SELECT * FROM users")
    return {"tool_results": {"database": result}}

# Build workflow
workflow = StateGraph(MCPWorkflowState)
workflow.add_node("route", route_to_tools)
workflow.add_node("use_database", use_database_tool)
workflow.add_conditional_edges("route", route_to_tools, {...})
```

## 🛡️ Security Considerations

### 1. Input Validation

```python
def validate_sql(sql: str) -> bool:
    """Validate SQL to prevent injection"""
    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER"]
    return not any(keyword in sql.upper() for keyword in forbidden)
```

### 2. Path Traversal Prevention

```python
def validate_path(base_path: Path, requested_path: str) -> bool:
    """Prevent path traversal attacks"""
    full_path = (base_path / requested_path).resolve()
    return str(full_path).startswith(str(base_path))
```

### 3. Authentication

```python
class AuthenticatedMCPServer(MCPServer):
    def __init__(self, name, auth_handler):
        super().__init__(name)
        self.auth_handler = auth_handler
    
    async def call_tool(self, tool_name, auth_token, **kwargs):
        if not self.auth_handler.validate_token(auth_token):
            return {"error": "Authentication failed"}
        return await super().call_tool(tool_name, **kwargs)
```

## 📊 Real-World Examples

### Customer Service Agent

```python
# MCP tools for customer service
tools = [
    CustomerDatabaseTool(),      # Customer lookup
    TicketSystemTool(),          # Support tickets
    KnowledgeBaseTool(),         # FAQ and docs
    EmailTool(),                 # Send responses
]

server = MCPServer("customer-service")
for tool in tools:
    server.register_tool(tool)

# LangChain agent
agent = create_customer_service_agent(
    tools=convert_mcp_tools(tools),
    llm=ChatOpenAI()
)
```

### Data Analysis Workflow

```python
# MCP tools for data analysis
tools = [
    DataWarehouseTool(),         # Query data warehouse
    VisualizationTool(),         # Generate charts
    ReportGeneratorTool(),       # Create reports
    EmailDeliveryTool(),         # Send reports
]

# LangGraph workflow
workflow = create_analysis_workflow(tools)
```

## 🧪 Testing MCP Systems

### Unit Tests

```python
import pytest

@pytest.mark.asyncio
async def test_database_tool():
    tool = DatabaseTool("sqlite:///:memory:")
    result = await tool.execute(
        operation="query",
        sql="SELECT 1 as test"
    )
    assert result["success"] == True
    assert len(result["data"]) == 1
```

### Integration Tests

```python
@pytest.mark.asyncio 
async def test_mcp_server():
    server = MCPServer("test-server")
    server.register_tool(DatabaseTool("sqlite:///:memory:"))
    
    result = await server.call_tool(
        "database_query",
        operation="query", 
        sql="SELECT 1"
    )
    assert result["success"] == True
```

## 🚀 Deployment

### Docker Setup

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "mcp_server.py"]
```

### Environment Configuration

```python
# config/settings.py
import os

class MCPSettings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "./storage")
    AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
    MAX_QUERY_ROWS = int(os.getenv("MAX_QUERY_ROWS", "1000"))
```

## 📚 Resources

- **MCP Specification**: [Official MCP Protocol Docs](https://github.com/modelcontextprotocol/specification)
- **LangChain Integration**: Use our examples as templates
- **Security Best Practices**: Always validate inputs and authenticate users
- **Performance Tips**: Use connection pooling and caching

## 🎯 Next Steps

1. **Start Small**: Build one MCP tool (database or file system)
2. **Add Security**: Implement authentication and validation
3. **Integrate with LangChain**: Convert tools for agent use
4. **Build Workflows**: Use LangGraph for complex processes
5. **Deploy Safely**: Add monitoring, logging, and error handling
6. **Scale Up**: Add more tools and data sources as needed

## 💡 Key Benefits

- ✅ **Standardized**: Works with any AI provider
- ✅ **Secure**: Built-in authentication and validation
- ✅ **Scalable**: Add tools without changing agent code
- ✅ **Flexible**: Support multiple data sources
- ✅ **Maintainable**: Clear separation of concerns

Happy building with MCP! 🚀
