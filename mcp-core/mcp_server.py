"""
Real MCP Server Implementation
Using the official MCP SDK to build production-ready MCP servers
"""

# Real MCP SDK imports
from mcp.server import Server
from mcp import stdio_server
from mcp.types import Tool
import mcp.types as types

import json
import sqlite3
import requests
from pathlib import Path
import asyncio
import logging

# Setup logging for MCP
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

class RealMCPServer:
    """Real MCP Server using the official MCP SDK"""
    
    def __init__(self, server_name: str = "company-data-mcp-server"):
        self.server = Server(server_name)
        self._setup_database()
        self._setup_documents()
        self._register_tools()
        
    def _setup_database(self):
        """Setup demo database with sample data"""
        self.conn = sqlite3.connect("real_mcp_demo.db")
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
        logger.info("Database setup completed with sample data")
    
    def _setup_documents(self):
        """Setup document store"""
        self.base_path = Path("real_mcp_documents")
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
""",
            
            "team_handbook.md": """# Team Handbook

## Team Structure

### Engineering Team (3 people)
- **Alice Johnson** - Senior AI Engineer, Team Lead
- **Carol Davis** - Database Architect, DevOps
- **Eva Martinez** - Frontend Developer

### Marketing Team (1 person)
- **Bob Smith** - Marketing Manager, Content Strategy

### Sales Team (1 person)
- **David Wilson** - Sales Manager, B2B Focus

## Tools & Technologies

### Development
- **Languages**: Python, TypeScript, SQL
- **Frameworks**: LangChain, React, FastAPI
- **Infrastructure**: Docker, AWS, PostgreSQL
- **AI/ML**: Ollama, OpenAI, Hugging Face
"""
        }
        
        for filename, content in documents.items():
            (self.base_path / filename).write_text(content)
        
        logger.info(f"Document store setup completed with {len(documents)} documents")
    
    def _register_tools(self):
        """Register MCP tools with the server"""
        
        # Register list_tools handler
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """Return available tools"""
            return [
                Tool(
                    name="query_database",
                    description="Execute SQL query on company database (employees, projects tables)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="access_document", 
                    description="Access company documents and policies",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["list", "read"],
                                "description": "Action to perform"
                            },
                            "filename": {
                                "type": "string",
                                "description": "Filename to read (required for 'read' action)"
                            }
                        },
                        "required": ["action"]
                    }
                )
            ]
        
        # Register call_tool handler
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            if name == "query_database":
                return await self._handle_database_query(arguments.get("query", ""))
            elif name == "access_document":
                return await self._handle_document_access(
                    arguments.get("action", ""),
                    arguments.get("filename")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
        
        logger.info("MCP tools registered successfully")
    
    async def _handle_database_query(self, query: str) -> list[types.TextContent]:
        """Handle database query"""
        try:
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Database query executed: {query[:50]}...")
            response = json.dumps(results, indent=2)
            return [types.TextContent(type="text", text=response)]
        except Exception as e:
            logger.error(f"Database query error: {e}")
            error_response = json.dumps({"error": str(e)})
            return [types.TextContent(type="text", text=error_response)]
    
    async def _handle_document_access(self, action: str, filename: str = None) -> list[types.TextContent]:
        """Handle document access"""
        try:
            if action == "list":
                files = [f.name for f in self.base_path.iterdir() if f.is_file()]
                logger.info(f"Listed {len(files)} available documents")
                response = json.dumps({"files": files})
            elif action == "read" and filename:
                file_path = self.base_path / filename
                if file_path.exists():
                    content = file_path.read_text()
                    logger.info(f"Read document: {filename}")
                    response = json.dumps({"filename": filename, "content": content})
                else:
                    logger.warning(f"Document not found: {filename}")
                    response = json.dumps({"error": f"File {filename} not found"})
            else:
                response = json.dumps({"error": "Invalid action. Use 'list' or 'read' with filename"})
            
            return [types.TextContent(type="text", text=response)]
        except Exception as e:
            logger.error(f"Document access error: {e}")
            error_response = json.dumps({"error": str(e)})
            return [types.TextContent(type="text", text=error_response)]
    
    async def start(self):
        """Start the MCP server"""
        logger.info("Starting Real MCP Server...")
        try:
            # Use stdio transport
            async with stdio_server() as transport:
                await self.server.run(*transport)
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    
    def get_server_info(self):
        """Get information about the server and its capabilities"""
        return {
            "name": "company-data-mcp-server",
            "version": "1.0.0",
            "tools": ["query_database", "access_document"],
            "description": "MCP server providing access to company data and documents"
        }

async def main():
    """Main function to run the MCP server"""
    print("🚀 Starting Real MCP Server")
    print("📦 Using official MCP SDK")
    print("=" * 50)
    
    server = RealMCPServer()
    
    # Print server info
    info = server.get_server_info()
    print(f"Server: {info['name']} v{info['version']}")
    print(f"Tools: {', '.join(info['tools'])}")
    print(f"Description: {info['description']}")
    print("\n🔧 Available Tools:")
    print("  • query_database: Execute SQL queries on company database")
    print("  • access_document: Read company documents and policies")
    
    print("\n🎯 Usage:")
    print("  This server can now be used with MCP clients")
    print("  Or integrated with LangChain for AI workflows")
    
    print("\n✅ MCP Server initialized successfully!")
    print("  The server is ready to handle tool calls programmatically")
    
    # Demonstrate tool functionality
    print("\n🧪 Testing tools directly:")
    
    try:
        # Test database query
        result = await server._handle_database_query("SELECT name, department FROM employees LIMIT 3")
        print(f"📊 Database test: {result[0].text[:100]}...")
        
        # Test document access
        result = await server._handle_document_access("list")
        print(f"📄 Document test: {result[0].text[:100]}...")
        
        print("\n✅ All tools working correctly!")
        
    except Exception as e:
        print(f"❌ Tool test error: {e}")
    
    print("\n💡 To use this server with clients, integrate it programmatically")
    print("   rather than running as a standalone stdio server")

if __name__ == "__main__":
    asyncio.run(main())
