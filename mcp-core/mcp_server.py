"""
Real MCP Server Implementation
Using the official MCP SDK to build production-ready MCP servers
"""

# Real MCP SDK imports
import mcp
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

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
        
        # Register database query tool
        @self.server.tool()
        async def query_database(query: str) -> str:
            """Execute SQL query on company database (employees, projects tables)
            
            Args:
                query: SQL query string to execute
                
            Returns:
                JSON string with query results or error message
            """
            try:
                self.conn.row_factory = sqlite3.Row
                cursor = self.conn.cursor()
                cursor.execute(query)
                results = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Database query executed: {query[:50]}...")
                return json.dumps(results, indent=2)
            except Exception as e:
                logger.error(f"Database query error: {e}")
                return json.dumps({"error": str(e)})
        
        # Register document access tool
        @self.server.tool()
        async def access_document(action: str, filename: str = None) -> str:
            """Access company documents and policies
            
            Args:
                action: Either 'list' to see available documents or 'read' to read a specific file
                filename: Name of the file to read (required when action is 'read')
                
            Returns:
                JSON string with document content, file list, or error message
            """
            try:
                if action == "list":
                    files = [f.name for f in self.base_path.iterdir() if f.is_file()]
                    logger.info(f"Listed {len(files)} available documents")
                    return json.dumps({"files": files})
                
                elif action == "read" and filename:
                    file_path = self.base_path / filename
                    if file_path.exists():
                        content = file_path.read_text()
                        logger.info(f"Read document: {filename}")
                        return json.dumps({"filename": filename, "content": content})
                    else:
                        logger.warning(f"Document not found: {filename}")
                        return json.dumps({"error": f"File {filename} not found"})
                
                else:
                    return json.dumps({"error": "Invalid action. Use 'list' or 'read' with filename"})
                    
            except Exception as e:
                logger.error(f"Document access error: {e}")
                return json.dumps({"error": str(e)})
        
        logger.info("MCP tools registered successfully")
    
    async def start(self):
        """Start the MCP server"""
        logger.info("Starting Real MCP Server...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream, write_stream,
                    InitializationOptions(
                        server_name="company-data-mcp-server",
                        server_version="1.0.0",
                        capabilities=self.server.capabilities
                    )
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
    
    def get_server_info(self):
        """Get information about the server and its capabilities"""
        return {
            "name": "company-data-mcp-server",
            "version": "1.0.0",
            "capabilities": self.server.capabilities,
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
    print("  Connect to this server using MCP clients via stdio protocol")
    print("  Or use with LangChain integration for AI workflows")
    
    print("\n▶️ Starting server (Press Ctrl+C to stop)...")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
