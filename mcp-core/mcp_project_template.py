"""
MCP Project Template - Production-ready MCP system with Ollama LLM
This template provides a complete foundation for building MCP-enabled AI systems with real LLM integration
"""

import json
import sqlite3
import os
import asyncio
import requests
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

# Ollama LLM Integration for MCP
class OllamaMCPAgent:
    """MCP Agent powered by Ollama LLM for intelligent tool selection"""
    
    def __init__(self, server: MCPServer, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.server = server
        self.model = model
        self.base_url = base_url
        self.conversation_history = []
        
        # Check Ollama connection
        if not self._check_ollama():
            raise RuntimeError("Cannot connect to Ollama. Please ensure Ollama is running: 'ollama serve'")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _call_ollama(self, prompt: str) -> str:
        """Make API call to Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "num_predict": 512
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            return f"Error calling Ollama: {e}"
    
    async def process_request(self, user_request: str) -> str:
        """Process user request using Ollama LLM to select and execute tools"""
        print(f"🤖 Processing request with Ollama {self.model}: {user_request}")
        
        # Build tool context for LLM
        available_tools = []
        for tool_name, tool in self.server.tools.items():
            tool_info = {
                "name": tool_name,
                "description": tool.description,
                "schema": tool.get_schema()
            }
            available_tools.append(tool_info)
        
        # Create prompt for tool selection
        prompt = f"""You are an AI assistant with access to company data through MCP tools.

Available tools:
{json.dumps(available_tools, indent=2)}

User request: "{user_request}"

Analyze the request and respond with ONLY a JSON object specifying which tool to use:
{{
  "tool_name": "exact_tool_name",
  "parameters": {{
    "param1": "value1",
    "param2": "value2"
  }},
  "reasoning": "brief explanation of why this tool was chosen"
}}

Examples:
- For database queries: {{"tool_name": "database_operations", "parameters": {{"operation": "query", "sql": "SELECT * FROM users"}}}}
- For file operations: {{"tool_name": "file_system", "parameters": {{"operation": "read", "path": "filename.txt"}}}}

Respond with ONLY the JSON, no other text:"""
        
        # Get LLM response
        llm_response = self._call_ollama(prompt)
        print(f"📤 Ollama response: {llm_response}")
        
        try:
            # Parse LLM response
            response_clean = llm_response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].strip()
            
            tool_call = json.loads(response_clean)
            tool_name = tool_call.get("tool_name")
            parameters = tool_call.get("parameters", {})
            reasoning = tool_call.get("reasoning", "No reasoning provided")
            
            if not tool_name:
                return "❌ LLM did not specify a tool to use"
            
            print(f"🔧 Executing tool: {tool_name}")
            print(f"💭 Reasoning: {reasoning}")
            print(f"📋 Parameters: {parameters}")
            
            # Execute the selected tool
            result = await self.server.call_tool(tool_name, **parameters)
            
            # Generate natural language response
            if result.get('success'):
                # Create context for natural response generation
                context_prompt = f"""Based on this tool execution result, provide a helpful natural language response to the user.

User question: "{user_request}"
Tool used: {tool_name}
Tool result: {json.dumps(result, indent=2)}

Provide a clear, helpful response in natural language. Focus on the key information the user needs:"""
                
                natural_response = self._call_ollama(context_prompt)
                
                return f"""✅ **Tool Execution Successful**
**Tool Used:** {tool_name}
**Reasoning:** {reasoning}

**Response:** {natural_response}

**Raw Data:** {json.dumps(result, indent=2)}"""
            else:
                return f"❌ **Tool Execution Failed**\n**Tool:** {tool_name}\n**Error:** {result.get('error', 'Unknown error')}"
                
        except json.JSONDecodeError as e:
            return f"❌ Failed to parse LLM response as JSON: {e}\nRaw response: {llm_response}"
        except Exception as e:
            return f"❌ Error processing request: {e}"
    
    async def interactive_mode(self):
        """Start interactive chat mode"""
        print("\n🎮 Interactive MCP Agent (Powered by Ollama)")
        print("Type your requests, or 'quit' to exit")
        print("Examples:")
        print("  - 'Show me all users in the database'")
        print("  - 'Read the company readme file'")
        print("  - 'Find projects owned by engineering team'")
        print("  - 'Search for remote work policies'")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💬 Your request: ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if user_input:
                    response = await self.process_request(user_input)
                    print(f"\n🤖 Agent Response:\n{response}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

# Usage Example and Demo
async def demo_mcp_system():
    """Demonstrate the complete MCP system with Ollama LLM"""
    
    print("🔌 Model Context Protocol (MCP) System Demo")
    print("🦙 Powered by Ollama llama3.2")
    print("=" * 70)
    
    # Create MCP server
    server = MCPServer("company-data-server")
    
    # Register tools
    db_tool = DatabaseMCPTool("company_data.db")
    file_tool = FileSystemMCPTool("workspace")
    
    server.register_tool(db_tool)
    server.register_tool(file_tool)
    
    print(f"\n📋 Server Manifest:")
    manifest = server.get_manifest()
    print(f"   Server: {manifest['name']} v{manifest['version']}")
    print(f"   Tools: {len(manifest['capabilities']['tools'])}")
    print(f"   Protocol: {manifest['protocol_version']}")
    
    try:
        # Create Ollama-powered agent
        agent = OllamaMCPAgent(server)
        print("✅ Ollama agent initialized successfully")
        
        # Intelligent test scenarios using natural language
        intelligent_scenarios = [
            "Show me all users in the database",
            "What's in the company readme file?",
            "Find all projects owned by engineering team members",
            "Search for information about remote work policies",
            "List all available files in the workspace",
            "Show me the meeting minutes"
        ]
        
        print(f"\n🧪 Running {len(intelligent_scenarios)} intelligent scenarios...")
        
        for i, request in enumerate(intelligent_scenarios, 1):
            print(f"\n" + "="*80)
            print(f"🎯 Intelligent Test {i}/{len(intelligent_scenarios)}")
            print(f"📝 User Request: {request}")
            print("-" * 60)
            
            try:
                response = await agent.process_request(request)
                print(response)
            except Exception as e:
                print(f"❌ Error in scenario {i}: {e}")
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        # Offer interactive mode
        print(f"\n" + "="*80)
        choice = input("\n🎮 Would you like to try interactive mode? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            await agent.interactive_mode()
            
    except RuntimeError as e:
        print(f"❌ Cannot initialize Ollama agent: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 And llama3.2 model is available: ollama pull llama3.2")
        
        # Fall back to basic MCP demo without LLM
        print("\n🔄 Running basic MCP demo without LLM...")
        await demo_basic_mcp(server)

async def demo_basic_mcp(server: MCPServer):
    """Basic MCP demo without LLM (fallback)"""
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
        print(f"🎯 Basic Test {i}: {scenario['name']}")
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
    print("🚀 MCP Project Template with Ollama LLM")
    print("1. Run intelligent demo (with Ollama)")
    print("2. Run basic demo (without LLM)")
    print("3. Interactive mode (with Ollama)")
    
    try:
        choice = input("\nChoose mode (1, 2, or 3): ").strip()
        
        if choice == "2":
            # Basic demo without LLM
            async def basic_demo():
                server = MCPServer("company-data-server")
                db_tool = DatabaseMCPTool("company_data.db")
                file_tool = FileSystemMCPTool("workspace")
                server.register_tool(db_tool)
                server.register_tool(file_tool)
                await demo_basic_mcp(server)
            
            asyncio.run(basic_demo())
            
        elif choice == "3":
            # Interactive mode only
            async def interactive_only():
                server = MCPServer("company-data-server")
                db_tool = DatabaseMCPTool("company_data.db")
                file_tool = FileSystemMCPTool("workspace")
                server.register_tool(db_tool)
                server.register_tool(file_tool)
                
                try:
                    agent = OllamaMCPAgent(server)
                    await agent.interactive_mode()
                except RuntimeError as e:
                    print(f"❌ {e}")
            
            asyncio.run(interactive_only())
            
        else:
            # Full demo with Ollama
            asyncio.run(demo_mcp_system())
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n" + "="*70)
    print("🎓 MCP + Ollama Integration Summary:")
    print("• 🔌 MCP Tools: Standardized interfaces to data sources")
    print("• 🤖 Ollama LLM: Real intelligence for tool selection")
    print("• 🧠 Natural Language: Process requests in plain English")
    print("• 📊 Rich Data: Database and file system integration")
    print("• 🔄 Interactive: Chat-like interface for exploration")
    
    print("\n🔧 Technical Architecture:")
    print("• MCPTool: Abstract base class for all tools")
    print("• MCPServer: Hosts and orchestrates tool execution")
    print("• OllamaMCPAgent: LLM-powered request processing")
    print("• Tool Selection: Ollama analyzes requests and chooses tools")
    print("• Natural Responses: LLM generates human-friendly output")
    
    print("\n� Production Ready Features:")
    print("• Async/await support for scalability")
    print("• Error handling and graceful degradation")
    print("• Tool registration and discovery")
    print("• JSON schema validation")
    print("• Extensible architecture for new tools")
    
    print("\n� Integration Options:")
    print("• LangChain: Convert MCP tools to LangChain Tools")
    print("• LangGraph: Use in complex multi-step workflows")
    print("• FastAPI: Expose as REST API endpoints")
    print("• Authentication: Add security layers as needed")
    print("• Monitoring: Log tool usage and performance")
    print("• Security sandboxing")
