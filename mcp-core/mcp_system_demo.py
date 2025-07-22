"""
Model Context Protocol (MCP) System Example
Building AI agents that can connect to external data sources and tools
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Simulate MCP-style tool definitions
class MCPTool:
    """Base class for MCP-compatible tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def to_schema(self) -> Dict[str, Any]:
        """Return tool schema in MCP format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters()
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        """Override in subclasses"""
        return {}
    
    def execute(self, **kwargs) -> Any:
        """Override in subclasses"""
        raise NotImplementedError

class DatabaseTool(MCPTool):
    """MCP tool for database operations"""
    
    def __init__(self, db_path: str):
        super().__init__(
            name="database_query",
            description="Query SQLite database for information"
        )
        self.db_path = db_path
        self._setup_demo_db()
    
    def _setup_demo_db(self):
        """Create demo database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                department TEXT,
                salary INTEGER,
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
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Insert sample data
        employees = [
            (1, "Alice Johnson", "Engineering", 95000, "2023-01-15"),
            (2, "Bob Smith", "Marketing", 75000, "2023-03-20"),
            (3, "Carol Davis", "Engineering", 105000, "2022-11-10"),
            (4, "David Wilson", "Sales", 85000, "2023-05-05")
        ]
        
        projects = [
            (1, "AI Chat System", "In Progress", 250000, 1),
            (2, "Marketing Campaign", "Completed", 50000, 2),
            (3, "Database Migration", "Planning", 150000, 3),
            (4, "Sales Analytics", "In Progress", 100000, 4)
        ]
        
        cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?)', employees)
        cursor.executemany('INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?)', projects)
        
        conn.commit()
        conn.close()
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                }
            },
            "required": ["query"]
        }
    
    def execute(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
        except Exception as e:
            conn.close()
            return [{"error": str(e)}]

class FileSystemTool(MCPTool):
    """MCP tool for file system operations"""
    
    def __init__(self, base_path: str):
        super().__init__(
            name="file_operations",
            description="Read, write, and list files in the workspace"
        )
        self.base_path = Path(base_path)
        self._setup_demo_files()
    
    def _setup_demo_files(self):
        """Create demo files"""
        self.base_path.mkdir(exist_ok=True)
        
        # Create sample files
        (self.base_path / "meeting_notes.txt").write_text("""
Meeting Notes - Project Planning
Date: 2025-01-15

Attendees: Alice, Bob, Carol
Topics:
- AI Chat System progress update
- Database migration timeline
- Q1 budget review

Action Items:
- Alice: Complete API integration by Jan 30
- Bob: Prepare marketing materials
- Carol: Review database schema
        """.strip())
        
        (self.base_path / "budget_2025.json").write_text(json.dumps({
            "departments": {
                "engineering": {"budget": 500000, "spent": 125000},
                "marketing": {"budget": 200000, "spent": 75000},
                "sales": {"budget": 150000, "spent": 45000}
            },
            "projects": {
                "ai_chat": {"allocated": 250000, "spent": 80000},
                "db_migration": {"allocated": 150000, "spent": 25000}
            }
        }, indent=2))
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "list"],
                    "description": "File operation to perform"
                },
                "filename": {
                    "type": "string",
                    "description": "Name of the file"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)"
                }
            },
            "required": ["operation"]
        }
    
    def execute(self, operation: str, filename: Optional[str] = None, content: Optional[str] = None) -> Any:
        """Execute file operation"""
        try:
            if operation == "list":
                files = [f.name for f in self.base_path.iterdir() if f.is_file()]
                return {"files": files}
            
            elif operation == "read" and filename:
                file_path = self.base_path / filename
                if file_path.exists():
                    return {"content": file_path.read_text()}
                else:
                    return {"error": f"File {filename} not found"}
            
            elif operation == "write" and filename and content:
                file_path = self.base_path / filename
                file_path.write_text(content)
                return {"success": f"File {filename} written successfully"}
            
            else:
                return {"error": "Invalid operation or missing parameters"}
                
        except Exception as e:
            return {"error": str(e)}

class MCPAgent:
    """AI Agent with MCP tool capabilities"""
    
    def __init__(self, tools: List[MCPTool]):
        self.tools = {tool.name: tool for tool in tools}
        print(f"🔌 MCP Agent initialized with {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get schemas for all available tools"""
        return [tool.to_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a specific tool"""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        return self.tools[tool_name].execute(**kwargs)
    
    def process_request(self, request: str) -> str:
        """Process user request and determine which tools to use"""
        request_lower = request.lower()
        
        print(f"\n🤖 Processing request: {request}")
        
        # Simple routing logic (in real MCP, this would be more sophisticated)
        if any(word in request_lower for word in ['database', 'query', 'employee', 'project', 'sql']):
            return self._handle_database_request(request)
        elif any(word in request_lower for word in ['file', 'read', 'notes', 'budget', 'document']):
            return self._handle_file_request(request)
        else:
            return self._handle_general_request(request)
    
    def _handle_database_request(self, request: str) -> str:
        """Handle database-related requests"""
        print("🗄️ Routing to database tool...")
        
        # Example queries based on request content
        if "employees" in request.lower():
            query = "SELECT * FROM employees"
        elif "projects" in request.lower():
            query = "SELECT * FROM projects"
        elif "engineering" in request.lower():
            query = "SELECT * FROM employees WHERE department = 'Engineering'"
        elif "salary" in request.lower():
            query = "SELECT name, salary FROM employees ORDER BY salary DESC"
        else:
            query = "SELECT * FROM employees LIMIT 5"
        
        print(f"   Executing query: {query}")
        results = self.execute_tool("database_query", query=query)
        
        if results and not any("error" in str(r) for r in results):
            formatted_results = json.dumps(results, indent=2)
            return f"Database query results:\n{formatted_results}"
        else:
            return f"Database error: {results}"
    
    def _handle_file_request(self, request: str) -> str:
        """Handle file-related requests"""
        print("📁 Routing to file system tool...")
        
        if "list" in request.lower():
            results = self.execute_tool("file_operations", operation="list")
        elif "notes" in request.lower():
            results = self.execute_tool("file_operations", operation="read", filename="meeting_notes.txt")
        elif "budget" in request.lower():
            results = self.execute_tool("file_operations", operation="read", filename="budget_2025.json")
        else:
            results = self.execute_tool("file_operations", operation="list")
        
        print(f"   File operation result: {type(results)}")
        return f"File system result:\n{json.dumps(results, indent=2)}"
    
    def _handle_general_request(self, request: str) -> str:
        """Handle general requests"""
        return f"""I'm an MCP-enabled agent with access to:
        
Available Tools:
{json.dumps(self.get_available_tools(), indent=2)}

I can help you with:
• Database queries (employees, projects, departments)
• File operations (read meeting notes, budget files)
• Real-time data access through MCP protocol

Try asking me:
- "Show me all employees"
- "What's in the meeting notes?"
- "List available files"
- "Show engineering team members"
"""

def demo_mcp_system():
    """Demonstrate MCP system in action"""
    
    print("🔌 Model Context Protocol (MCP) System Demo")
    print("=" * 60)
    
    # Initialize MCP tools
    db_tool = DatabaseTool("demo_company.db")
    file_tool = FileSystemTool("demo_workspace")
    
    # Create MCP agent
    agent = MCPAgent([db_tool, file_tool])
    
    # Test requests
    test_requests = [
        "Show me all employees in the database",
        "What's in the meeting notes file?",
        "List all available files",
        "Show me employees in the engineering department",
        "What's our current budget status?",
        "Tell me about your capabilities"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n" + "="*60)
        print(f"📝 Request {i}: {request}")
        print("-" * 40)
        
        response = agent.process_request(request)
        print(f"✅ Response:\n{response}")

if __name__ == "__main__":
    demo_mcp_system()
    
    print("\n" + "=" * 60)
    print("💡 Key MCP Concepts Demonstrated:")
    print("• Tool registration and schema definition")
    print("• Secure data access through defined interfaces")  
    print("• Multi-modal data sources (DB + files)")
    print("• Request routing based on content")
    print("• Structured responses in JSON format")
    print("\n🔑 In production, add authentication, validation, and error handling!")
