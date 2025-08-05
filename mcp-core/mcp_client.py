"""
Real MCP Client Implementation
Using the official MCP SDK to connect to MCP servers and provide LangChain integration
"""

from typing import List, Dict, Any
from langchain.tools import Tool

# Real MCP SDK imports
import mcp
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

import json
import asyncio
import logging

# Setup logging for MCP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-client")

class RealMCPClient:
    """Real MCP Client that connects to MCP servers and provides LangChain integration"""
    
    def __init__(self):
        self.client_session = None
        self.tools = []
        self.server_info = None
        self.connected = False
        
    async def connect_to_server(self, server_command: List[str]):
        """Connect to an MCP server via stdio
        
        Args:
            server_command: Command to start the MCP server (e.g., ["python", "mcp_server.py"])
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to MCP server: {' '.join(server_command)}")
            
            # Connect to MCP server via stdio
            async with stdio_client(server_command) as (read, write):
                async with ClientSession(read, write) as session:
                    self.client_session = session
                    
                    # Initialize the session
                    init_result = await session.initialize()
                    logger.info(f"Connected to MCP server: {init_result}")
                    self.server_info = init_result
                    
                    # List available tools
                    tools_result = await session.list_tools()
                    self.tools = tools_result.tools
                    logger.info(f"Available MCP tools: {[tool.name for tool in self.tools]}")
                    
                    self.connected = True
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.connected = False
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an MCP tool and return the result
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            RuntimeError: If not connected to MCP server
        """
        if not self.client_session:
            raise RuntimeError("Not connected to MCP server")
        
        try:
            logger.info(f"Calling MCP tool: {tool_name} with args: {arguments}")
            result = await self.client_session.call_tool(tool_name, arguments)
            logger.info(f"Tool {tool_name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    def to_langchain_tools(self) -> List[Tool]:
        """Convert MCP tools to LangChain tools
        
        Returns:
            List of LangChain Tool objects that wrap MCP tools
        """
        if not self.tools:
            logger.warning("No MCP tools available to convert")
            return []
        
        langchain_tools = []
        
        for mcp_tool in self.tools:
            def create_tool_func(tool_name):
                async def tool_func(input_str: str) -> str:
                    """LangChain tool function that calls MCP tool"""
                    try:
                        # Try to parse as JSON for structured input
                        if input_str.startswith('{'):
                            params = json.loads(input_str)
                        else:
                            # Handle simple string queries based on tool name
                            if "database" in tool_name.lower() or "query" in tool_name.lower():
                                params = {"query": input_str}
                            elif "document" in tool_name.lower() or "access" in tool_name.lower():
                                if ":" in input_str:
                                    action, filename = input_str.split(":", 1)
                                    params = {"action": action, "filename": filename}
                                else:
                                    params = {"action": input_str}
                            else:
                                params = {"input": input_str}
                        
                        result = await self.call_tool(tool_name, params)
                        return json.dumps(result, indent=2)
                    except Exception as e:
                        return f"Error: {str(e)}"
                
                return tool_func
            
            langchain_tools.append(Tool(
                name=mcp_tool.name,
                description=mcp_tool.description,
                func=create_tool_func(mcp_tool.name)
            ))
        
        logger.info(f"Converted {len(langchain_tools)} MCP tools to LangChain tools")
        return langchain_tools
    
    def get_tool_info(self) -> List[Dict[str, str]]:
        """Get information about available MCP tools
        
        Returns:
            List of dictionaries with tool information
        """
        if not self.tools:
            return []
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "schema": getattr(tool, 'inputSchema', {})
            }
            for tool in self.tools
        ]
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get information about the connected MCP server
        
        Returns:
            Dictionary with server information
        """
        return {
            "connected": self.connected,
            "server_info": self.server_info,
            "tools_count": len(self.tools),
            "tool_names": [tool.name for tool in self.tools] if self.tools else []
        }
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.client_session:
            try:
                # Note: The actual disconnection is handled by the context managers
                # in the connect_to_server method
                self.client_session = None
                self.connected = False
                logger.info("Disconnected from MCP server")
            except Exception as e:
                logger.error(f"Error during disconnection: {e}")

class SimpleMCPDatabaseTool:
    """Simplified MCP-style database tool for demonstration (when real MCP server isn't running)"""
    
    def __init__(self):
        self.name = "query_database"
        self.description = "Execute SQL query on company database (employees, projects tables)"
        self._setup_db()
    
    def _setup_db(self):
        """Setup demo database with sample data"""
        import sqlite3
        self.conn = sqlite3.connect("simple_mcp_demo.db")
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
        try:
            import sqlite3
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            return json.dumps(results, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

class SimpleMCPDocumentTool:
    """Simplified MCP-style document tool for demonstration"""
    
    def __init__(self):
        self.name = "access_document"
        self.description = "Access company documents. Use 'list' to see available docs or 'read' with filename"
        self._setup_documents()
    
    def _setup_documents(self):
        """Setup document store"""
        from pathlib import Path
        self.base_path = Path("simple_mcp_documents")
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
""",
            
            "project_status.md": """# Q1 2025 Project Status Report

## Engineering Projects

### AI Chat System (Priority: High)
- **Status**: 75% Complete  
- **Team**: Alice Johnson (Lead), Carol Davis
- **Deadline**: March 30, 2025
- **Budget**: $250,000 ($180,000 spent)

### Database Migration (Priority: Medium)
- **Status**: 25% Complete
- **Team**: Carol Davis (Lead)  
- **Deadline**: June 1, 2025
- **Budget**: $150,000 ($35,000 spent)
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

async def demo_mcp_client():
    """Demo function to test MCP client functionality"""
    print("🔗 MCP Client Demo")
    print("=" * 30)
    
    client = RealMCPClient()
    
    # Show client info
    info = client.get_server_info()
    print(f"Client Status: {'Connected' if info['connected'] else 'Disconnected'}")
    print(f"Available Tools: {info['tools_count']}")
    
    # In a real scenario, you would connect to an actual MCP server:
    # success = await client.connect_to_server(["python", "mcp_server.py"])
    
    print("\n💡 To connect to a real MCP server:")
    print("  client = RealMCPClient()")
    print("  await client.connect_to_server(['python', 'mcp_server.py'])")
    print("  tools = client.to_langchain_tools()")
    
    print("\n🔧 Using simplified tools for demo:")
    
    # Use simplified tools for demo
    db_tool = SimpleMCPDatabaseTool()
    doc_tool = SimpleMCPDocumentTool()
    
    # Test database tool
    print("\n📊 Database Tool Test:")
    query = "SELECT name, department FROM employees LIMIT 3"
    result = db_tool.execute(query)
    print(f"Query: {query}")
    print(f"Result: {result}")
    
    # Test document tool
    print("\n📄 Document Tool Test:")
    result = doc_tool.execute("list")
    print(f"Action: list")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(demo_mcp_client())
