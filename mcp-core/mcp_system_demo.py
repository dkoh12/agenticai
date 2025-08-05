"""
Model Context Protocol (MCP) System Example
Building AI agents that can connect to external data sources and tools
"""

import json
import sqlite3
import os
import requests
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
    """LLM-driven MCP Agent with tool-calling via LLM"""
    def __init__(self, tools: List[MCPTool], llm_model: str = None, llm_base_url: str = None):
        self.tools = {tool.name: tool for tool in tools}
        self.llm_model = llm_model
        self.llm_base_url = llm_base_url
        print(f"🔌 MCP Agent initialized with {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        return self.tools[tool_name].execute(**kwargs)

    def process_request(self, request: str) -> str:
        """Send user request and tool schemas to LLM, parse tool call, execute, return result"""
        print(f"\n🤖 Processing request with Ollama llama3.2: {request}")
        tool_schemas = self.get_available_tools()
        llm_prompt = self._build_llm_prompt(request, tool_schemas)

        # Call Ollama LLM
        print("🔄 Calling Ollama...")
        llm_response = self._call_llm(llm_prompt)
        print(f"📤 LLM response: {llm_response}")

        # Try to parse tool call from LLM response
        try:
            # Clean up response - sometimes LLM adds extra text
            response_clean = llm_response.strip()
            if '```json' in response_clean:
                response_clean = response_clean.split('```json')[1].split('```')[0].strip()
            elif '```' in response_clean:
                response_clean = response_clean.split('```')[1].strip()
            
            tool_call = json.loads(response_clean)
            tool_name = tool_call.get("tool_name")
            tool_args = tool_call.get("tool_args", {})
            
            if not tool_name:
                return f"❌ LLM did not return a tool_name. Raw response: {llm_response}"
            
            print(f"🔧 Executing tool: {tool_name} with args: {tool_args}")
            result = self.execute_tool(tool_name, **tool_args)
            
            # Format the final response nicely
            if isinstance(result, dict) and "error" in result:
                return f"❌ Tool error: {json.dumps(result, indent=2)}"
            else:
                return f"✅ Tool `{tool_name}` executed successfully:\n{json.dumps(result, indent=2)}"
                
        except json.JSONDecodeError as e:
            return f"❌ Failed to parse LLM JSON response: {e}\nRaw response: {llm_response}"
        except Exception as e:
            return f"❌ Error executing tool: {e}\nRaw response: {llm_response}"

    def _build_llm_prompt(self, request: str, tool_schemas: List[Dict[str, Any]]) -> str:
        return f'''You are an AI assistant with access to tools via the Model Context Protocol (MCP).

Available tools:
{json.dumps(tool_schemas, indent=2)}

User request: "{request}"

To use a tool, respond with ONLY a JSON object in this exact format:
{{
  "tool_name": "exact_tool_name_from_schema",
  "tool_args": {{
    "parameter_name": "parameter_value"
  }}
}}

Examples:
- To query database: {{"tool_name": "database_query", "tool_args": {{"query": "SELECT * FROM employees"}}}}
- To read a file: {{"tool_name": "file_operations", "tool_args": {{"operation": "read", "filename": "meeting_notes.txt"}}}}
- To list files: {{"tool_name": "file_operations", "tool_args": {{"operation": "list"}}}}

Respond ONLY with the JSON tool call, no explanation:'''

    def _call_llm(self, prompt: str) -> str:
        """Call Ollama LLM with the given prompt"""
        try:
            # Use Ollama API endpoint
            url = f"{self.llm_base_url or 'http://localhost:11434'}/api/generate"
            payload = {
                "model": self.llm_model or "llama3.2",
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
            return f'{{"error": "LLM call failed: {e}"}}'


def demo_mcp_system():
    """Demonstrate LLM+MCP system in action with Ollama"""
    print("🔌 Model Context Protocol (MCP) System Demo")
    print("🦙 Powered by Ollama llama3.2 + MCP Tools")
    print("=" * 60)

    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
        else:
            print("❌ Ollama is not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please make sure Ollama is running: ollama serve")
        return

    # Initialize MCP tools
    print("\n🔧 Initializing MCP tools...")
    db_tool = DatabaseTool("demo_company.db")
    file_tool = FileSystemTool("demo_workspace")

    # Create MCP agent with Ollama llama3.2
    agent = MCPAgent([db_tool, file_tool], llm_model="llama3.2", llm_base_url="http://localhost:11434")

    # Test requests that demonstrate MCP capabilities
    test_requests = [
        "Show me all employees in the database",
        "List all files in the workspace", 
        "Read the meeting notes file",
        "Show me employees in the engineering department",
        "What's in the budget file?",
        "Show me all projects with their status"
    ]

    print(f"\n🧪 Running {len(test_requests)} test requests...")
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n" + "="*80)
        print(f"📝 Test {i}/{len(test_requests)}: {request}")
        print("-" * 80)
        
        try:
            response = agent.process_request(request)
            print(f"📋 Result:\n{response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between requests to be nice to Ollama
        import time
        time.sleep(1)

def interactive_mcp_demo():
    """Interactive MCP demo where user can type requests"""
    print("\n🎮 Interactive MCP Demo")
    print("Type your requests, or 'quit' to exit")
    print("-" * 40)
    
    # Initialize tools and agent
    db_tool = DatabaseTool("demo_company.db")
    file_tool = FileSystemTool("demo_workspace")
    agent = MCPAgent([db_tool, file_tool], llm_model="llama3.2", llm_base_url="http://localhost:11434")
    
    while True:
        try:
            user_input = input("\n💬 Your request: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_input:
                response = agent.process_request(user_input)
                print(f"\n🤖 Response:\n{response}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 MCP + Ollama Demo")
    print("1. Run automated demo")
    print("2. Interactive mode") 
    
    try:
        choice = input("\nChoose mode (1 or 2): ").strip()
        if choice == "2":
            interactive_mcp_demo()
        else:
            demo_mcp_system()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    
    print("\n" + "=" * 60)
    print("💡 What this demo shows:")
    print("• Real LLM (Ollama llama3.2) making tool selection decisions")
    print("• MCP-style tool registration and schema definition")
    print("• Structured tool calling via JSON parsing")
    print("• Database and file system tool integration")
    print("• Error handling and response formatting")
    print("\n🔧 Next steps: Build your own MCP tools and connect them!")
    print("� Learn more: https://modelcontextprotocol.io/")
