"""
MCP Project Template - Ready to use MCP system with LangChain
This template provides a foundation for building MCP-enabled AI systems
"""

import json
import sqlite3
import os
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Literal
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

# Base MCP Protocol Classes
class MCPTool(ABC):
    """Abstract base class for MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.created_at = datetime.now().isoformat()
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for tool parameters"""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass
    
    def to_mcp_manifest(self) -> Dict[str, Any]:
        """Generate MCP manifest entry"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "schema": self.get_schema(),
            "created_at": self.created_at
        }

class MCPResource(ABC):
    """Abstract base class for MCP resources"""
    
    def __init__(self, uri: str, name: str, description: str):
        self.uri = uri
        self.name = name 
        self.description = description
    
    @abstractmethod
    async def read(self, **kwargs) -> Dict[str, Any]:
        """Read data from the resource"""
        pass
    
    @abstractmethod
    async def list(self, **kwargs) -> List[Dict[str, Any]]:
        """List available items in the resource"""
        pass

# Concrete MCP Tool Implementations
class DatabaseMCPTool(MCPTool):
    """MCP tool for database operations"""
    
    def __init__(self, db_path: str):
        super().__init__(
            name="database_operations",
            description="Execute SQL queries on the company database"
        )
        self.db_path = db_path
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database if it doesn't exist"""
        if not os.path.exists(self.db_path):
            self._create_sample_database()
    
    def _create_sample_database(self):
        """Create sample database with realistic data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                department TEXT,
                role TEXT,
                created_at TEXT
            )
        ''')
        
        # Projects table  
        cursor.execute('''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                status TEXT,
                owner_id INTEGER,
                budget REAL,
                created_at TEXT,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
        ''')
        
        # Sample data
        users = [
            (1, "alice_j", "alice@company.com", "Engineering", "Senior Developer", "2023-01-15"),
            (2, "bob_m", "bob@company.com", "Marketing", "Marketing Manager", "2023-02-01"),
            (3, "carol_d", "carol@company.com", "Engineering", "DevOps Engineer", "2022-11-20"),
            (4, "david_s", "david@company.com", "Sales", "Sales Representative", "2023-04-10")
        ]
        
        projects = [
            (1, "AI Assistant", "Develop AI-powered customer service assistant", "In Progress", 1, 150000, "2023-03-01"),
            (2, "Website Redesign", "Complete company website overhaul", "Planning", 2, 75000, "2023-04-15"),
            (3, "Infrastructure Upgrade", "Migrate to cloud infrastructure", "Completed", 3, 200000, "2023-01-10"),
            (4, "Sales Analytics", "Build sales performance dashboard", "In Progress", 4, 50000, "2023-05-01")
        ]
        
        cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)', users)
        cursor.executemany('INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)', projects)
        
        conn.commit()
        conn.close()
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["query", "insert", "update", "delete"],
                    "description": "Database operation to perform"
                },
                "sql": {
                    "type": "string",
                    "description": "SQL statement to execute"
                },
                "params": {
                    "type": "array",
                    "description": "Parameters for SQL statement",
                    "items": {"type": "string"}
                }
            },
            "required": ["operation", "sql"]
        }
    
    async def execute(self, operation: str, sql: str, params: Optional[List] = None) -> Dict[str, Any]:
        """Execute database operation"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            if operation == "query":
                results = [dict(row) for row in cursor.fetchall()]
                return {"success": True, "data": results, "row_count": len(results)}
            else:
                conn.commit()
                return {"success": True, "affected_rows": cursor.rowcount}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

class FileSystemMCPTool(MCPTool):
    """MCP tool for file system operations"""
    
    def __init__(self, base_path: str):
        super().__init__(
            name="file_system",
            description="Read, write, and manage files in the workspace"
        )
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self._create_sample_files()
    
    def _create_sample_files(self):
        """Create sample files"""
        files = {
            "company_readme.md": """# Company Documentation

## Overview
Welcome to our company documentation system.

## Departments
- Engineering: Building innovative solutions
- Marketing: Growing our brand and reach  
- Sales: Connecting with customers
- Operations: Keeping everything running smoothly

## Current Initiatives
1. AI-driven customer service
2. Cloud infrastructure migration
3. Sales process optimization
4. Employee wellness programs
""",
            "meeting_minutes.json": json.dumps({
                "date": "2025-01-20",
                "attendees": ["Alice Johnson", "Bob Martinez", "Carol Davis"],
                "topics": [
                    "Q1 project status review",
                    "New hire onboarding process",
                    "Budget allocation for Q2"
                ],
                "action_items": [
                    {"owner": "Alice", "task": "Complete API documentation", "due": "2025-01-30"},
                    {"owner": "Bob", "task": "Launch marketing campaign", "due": "2025-02-15"},
                    {"owner": "Carol", "task": "Infrastructure audit", "due": "2025-02-05"}
                ]
            }, indent=2),
            "policies.txt": """REMOTE WORK POLICY

1. Employees may work remotely up to 3 days per week
2. Core collaboration hours: 10 AM - 3 PM local time
3. Weekly team check-ins are mandatory
4. Home office equipment stipend: $500/year

EXPENSE POLICY

1. Meals: Up to $50/day for business travel
2. Software/Tools: Pre-approval required for purchases over $100
3. Conference attendance: Budget allocated per department annually
"""
        }
        
        for filename, content in files.items():
            file_path = self.base_path / filename
            if not file_path.exists():
                file_path.write_text(content)
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object", 
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "list", "delete", "search"],
                    "description": "File operation to perform"
                },
                "path": {
                    "type": "string",
                    "description": "File path relative to workspace"
                },
                "content": {
                    "type": "string", 
                    "description": "Content for write operations"
                },
                "query": {
                    "type": "string",
                    "description": "Search query for search operations"
                }
            },
            "required": ["operation"]
        }
    
    async def execute(self, operation: str, path: Optional[str] = None, 
                     content: Optional[str] = None, query: Optional[str] = None) -> Dict[str, Any]:
        """Execute file system operation"""
        try:
            if operation == "list":
                files = [f.name for f in self.base_path.iterdir() if f.is_file()]
                return {"success": True, "files": files}
            
            elif operation == "read" and path:
                file_path = self.base_path / path
                if file_path.exists() and file_path.is_file():
                    content = file_path.read_text()
                    return {"success": True, "content": content, "size": len(content)}
                else:
                    return {"success": False, "error": f"File {path} not found"}
            
            elif operation == "write" and path and content:
                file_path = self.base_path / path
                file_path.write_text(content)
                return {"success": True, "message": f"File {path} written successfully"}
            
            elif operation == "search" and query:
                results = []
                for file_path in self.base_path.glob("*"):
                    if file_path.is_file():
                        try:
                            file_content = file_path.read_text()
                            if query.lower() in file_content.lower():
                                results.append({
                                    "file": file_path.name,
                                    "matches": file_content.lower().count(query.lower())
                                })
                        except:
                            continue
                return {"success": True, "results": results}
            
            else:
                return {"success": False, "error": "Invalid operation or missing parameters"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

# MCP Server Implementation
class MCPServer:
    """MCP Server that hosts tools and resources"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.manifest = {
            "name": name,
            "version": version,
            "protocol_version": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            }
        }
    
    def register_tool(self, tool: MCPTool):
        """Register a tool with the server"""
        self.tools[tool.name] = tool
        self.manifest["capabilities"]["tools"][tool.name] = tool.to_mcp_manifest()
        print(f"✅ Registered tool: {tool.name}")
    
    def register_resource(self, resource: MCPResource):
        """Register a resource with the server"""
        self.resources[resource.uri] = resource
        self.manifest["capabilities"]["resources"][resource.uri] = {
            "name": resource.name,
            "description": resource.description
        }
        print(f"✅ Registered resource: {resource.uri}")
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a registered tool"""
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool {tool_name} not found"}
        
        return await self.tools[tool_name].execute(**kwargs)
    
    def get_manifest(self) -> Dict[str, Any]:
        """Get server manifest"""
        return self.manifest
    
    def list_tools(self) -> List[str]:
        """List available tools"""
        return list(self.tools.keys())

# Usage Example and Demo
async def demo_mcp_system():
    """Demonstrate the complete MCP system"""
    
    print("🔌 Model Context Protocol (MCP) System Demo")
    print("=" * 60)
    
    # Create MCP server
    server = MCPServer("company-data-server")
    
    # Register tools
    db_tool = DatabaseMCPTool("company_data.db")
    file_tool = FileSystemMCPTool("workspace")
    
    server.register_tool(db_tool)
    server.register_tool(file_tool)
    
    print(f"\n📋 Server Manifest:")
    print(json.dumps(server.get_manifest(), indent=2))
    
    # Test scenarios
    scenarios = [
        {
            "name": "Database Query - All Users",
            "tool": "database_operations",
            "params": {
                "operation": "query",
                "sql": "SELECT username, email, department, role FROM users"
            }
        },
        {
            "name": "File Read - Company README",
            "tool": "file_system", 
            "params": {
                "operation": "read",
                "path": "company_readme.md"
            }
        },
        {
            "name": "Database Query - Engineering Projects",
            "tool": "database_operations",
            "params": {
                "operation": "query", 
                "sql": "SELECT p.name, p.status, p.budget, u.username FROM projects p JOIN users u ON p.owner_id = u.id WHERE u.department = 'Engineering'"
            }
        },
        {
            "name": "File Search - Policy Information", 
            "tool": "file_system",
            "params": {
                "operation": "search",
                "query": "remote work"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n" + "="*60)
        print(f"🎯 Scenario {i}: {scenario['name']}")
        print("-" * 40)
        
        result = await server.call_tool(scenario['tool'], **scenario['params'])
        
        if result.get('success'):
            print("✅ Success!")
            if 'data' in result:
                print(f"📊 Data ({len(result['data'])} rows):")
                for row in result['data'][:3]:  # Show first 3 rows
                    print(f"   {row}")
                if len(result['data']) > 3:
                    print(f"   ... and {len(result['data']) - 3} more rows")
            elif 'content' in result:
                content = result['content']
                print(f"📄 Content ({len(content)} chars):")
                print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
            elif 'results' in result:
                print(f"🔍 Search Results:")
                for match in result['results']:
                    print(f"   {match}")
            else:
                print(f"📋 Result: {result}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    import asyncio
    
    # Run the demo
    asyncio.run(demo_mcp_system())
    
    print("\n" + "="*60)
    print("🎓 MCP Learning Summary:")
    print("• Tools: Standardized interfaces to external systems")
    print("• Resources: Managed data sources with controlled access")
    print("• Server: Hosts and orchestrates tools/resources")
    print("• Protocol: Ensures secure, consistent communication")
    print("• Manifest: Describes server capabilities")
    
    print("\n🔧 Integration with LangChain:")
    print("• Convert MCP tools to LangChain Tools")
    print("• Use in agent workflows and chains")
    print("• Combine with LangGraph for complex workflows")
    print("• Add authentication and security layers")
    
    print("\n🚀 Production Considerations:")
    print("• Authentication and authorization")
    print("• Rate limiting and resource management")
    print("• Error handling and logging")
    print("• Tool versioning and compatibility")
    print("• Security sandboxing")
