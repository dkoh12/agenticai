"""
Real MCP Project Template - Using FastMCP for Simplicity
This template provides a complete foundation for building actual MCP-enabled AI systems
"""

import json
import sqlite3
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Official MCP SDK imports - using FastMCP for simplicity
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("real-mcp-project-server")

# Global paths
DB_PATH = "real_mcp_project.db"
WORKSPACE_PATH = Path("real_mcp_workspace")

def setup_database():
    """Setup demo database with sample data"""
    print("Setting up database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            salary INTEGER,
            skills TEXT,
            hire_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            status TEXT,
            budget INTEGER,
            team_lead_id INTEGER,
            start_date TEXT,
            FOREIGN KEY (team_lead_id) REFERENCES employees (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            project_id INTEGER,
            assignee_id INTEGER,
            status TEXT,
            priority TEXT,
            due_date TEXT,
            FOREIGN KEY (project_id) REFERENCES projects (id),
            FOREIGN KEY (assignee_id) REFERENCES employees (id)
        )
    ''')
    
    # Sample data
    employees = [
        (1, "Alice Johnson", "alice@company.com", "Engineering", "Senior Developer", 120000, "Python,AI,ML", "2023-01-15"),
        (2, "Bob Martinez", "bob@company.com", "Marketing", "Marketing Manager", 90000, "Content,SEO,Analytics", "2023-02-01"),
        (3, "Carol Davis", "carol@company.com", "Engineering", "DevOps Engineer", 110000, "AWS,Docker,Kubernetes", "2022-11-20"),
        (4, "David Smith", "david@company.com", "Sales", "Sales Representative", 80000, "CRM,Negotiation,Presentations", "2023-04-10"),
        (5, "Eva Martinez", "eva@company.com", "Engineering", "Frontend Developer", 95000, "React,TypeScript,Design", "2023-03-15")
    ]
    
    projects = [
        (1, "AI Customer Assistant", "Develop AI-powered customer service chat", "In Progress", 200000, 1, "2023-03-01"),
        (2, "Website Redesign", "Complete company website overhaul", "Planning", 80000, 5, "2023-04-15"),
        (3, "Cloud Migration", "Migrate infrastructure to AWS", "Completed", 150000, 3, "2023-01-10"),
        (4, "Sales Dashboard", "Build comprehensive sales analytics", "In Progress", 60000, 4, "2023-05-01"),
        (5, "Mobile App", "Native iOS and Android app", "Planning", 250000, 1, "2023-06-01")
    ]
    
    tasks = [
        (1, "Train ML model", "Train and optimize customer service AI model", 1, 1, "In Progress", "High", "2025-02-15"),
        (2, "API integration", "Integrate with existing CRM system", 1, 3, "Pending", "Medium", "2025-02-28"),
        (3, "UI mockups", "Create new website design mockups", 2, 5, "In Progress", "High", "2025-02-10"),
        (4, "Database schema", "Design new analytics database", 4, 3, "Completed", "High", "2025-01-30"),
        (5, "Market research", "Research mobile app requirements", 5, 2, "Pending", "Low", "2025-03-15")
    ]
    
    cursor.executemany('INSERT OR REPLACE INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)', employees)
    cursor.executemany('INSERT OR REPLACE INTO projects VALUES (?, ?, ?, ?, ?, ?, ?)', projects)
    cursor.executemany('INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)', tasks)
    
    conn.commit()
    conn.close()
    print("Database setup completed")

def setup_workspace():
    """Setup workspace with sample files"""
    print("Setting up workspace...")
    
    WORKSPACE_PATH.mkdir(exist_ok=True)
    
    files = {
        "company_handbook.md": """# Company Handbook

## Mission
To build innovative AI solutions that improve business efficiency and customer experiences.

## Core Values
- Innovation through collaboration
- Customer-centric development
- Continuous learning and improvement
- Work-life balance and flexibility

## Remote Work Policy
- Up to 4 days remote per week
- Core hours: 10 AM - 3 PM local time
- Weekly team sync required
- Quarterly in-person meetings

## Benefits
- Health insurance (company pays 100%)
- 401k matching up to 6%
- $2000 annual learning budget
- Flexible PTO policy
- $500 home office stipend
""",
        
        "project_roadmap.json": json.dumps({
            "roadmap": {
                "Q1_2025": {
                    "focus": "AI and Infrastructure",
                    "projects": [
                        {"name": "AI Customer Assistant", "priority": "P0", "completion": "75%"},
                        {"name": "Cloud Migration", "priority": "P1", "completion": "100%"}
                    ]
                },
                "Q2_2025": {
                    "focus": "User Experience",
                    "projects": [
                        {"name": "Website Redesign", "priority": "P0", "completion": "0%"},
                        {"name": "Sales Dashboard", "priority": "P1", "completion": "30%"}
                    ]
                },
                "Q3_2025": {
                    "focus": "Mobile Strategy", 
                    "projects": [
                        {"name": "Mobile App", "priority": "P0", "completion": "0%"}
                    ]
                }
            },
            "updated": "2025-01-20"
        }, indent=2),
        
        "meeting_notes.md": """# Weekly Team Meeting - January 20, 2025

## Attendees
- Alice Johnson (Engineering Lead)
- Bob Martinez (Marketing)
- Carol Davis (DevOps)
- Eva Martinez (Frontend)

## Key Updates

### Engineering
- AI Assistant model training 90% complete
- Cloud migration finished ahead of schedule
- Need to resolve API rate limiting issues

### Marketing
- Q1 campaign planning underway
- Website redesign kickoff next week
- Customer feedback analysis complete

### Operations  
- New hire onboarding process updated
- Quarterly planning session scheduled
- Budget review for Q2 approved

## Action Items
1. Alice: Complete AI model optimization by Feb 15
2. Eva: Finalize website mockups by Feb 10
3. Carol: Document cloud migration process
4. Bob: Prepare Q1 marketing metrics report

## Next Meeting
January 27, 2025 - 10:00 AM
""",
        
        "tech_specs.md": """# Technical Specifications

## AI Customer Assistant

### Architecture
- **Model**: Fine-tuned GPT-3.5 for customer service
- **Backend**: Python FastAPI with Redis caching
- **Database**: PostgreSQL for conversation history
- **Deployment**: Docker containers on AWS EKS

### Performance Requirements
- Response time: < 2 seconds average
- Availability: 99.9% uptime SLA
- Throughput: 1000 concurrent conversations
- Accuracy: > 85% first-response resolution

### Security
- End-to-end encryption for customer data
- GDPR compliance for EU customers
- Regular security audits
- Role-based access control

### Monitoring
- Real-time conversation quality metrics
- Performance dashboards via Grafana
- Alert system for downtime/errors
- Customer satisfaction tracking
"""
    }
    
    for filename, content in files.items():
        file_path = WORKSPACE_PATH / filename
        if not file_path.exists():
            file_path.write_text(content)
    
    print(f"Workspace setup completed with {len(files)} files")

# Initialize data on module load
setup_database()
setup_workspace()

@mcp.tool()
def query_database(sql: str) -> str:
    """Execute SQL queries on the company database (employees, projects, tasks)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
        
        response = {
            "success": True,
            "query": sql,
            "row_count": len(results),
            "data": results
        }
        
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "query": sql,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)
    finally:
        conn.close()

@mcp.tool()
def read_file(filename: str) -> str:
    """Read contents of files in the workspace."""
    file_path = WORKSPACE_PATH / filename
    
    if not file_path.exists():
        error_response = {
            "success": False,
            "filename": filename,
            "error": "File not found"
        }
        return json.dumps(error_response, indent=2)
    
    try:
        content = file_path.read_text()
        response = {
            "success": True,
            "filename": filename,
            "size": len(content),
            "content": content
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "filename": filename,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)

@mcp.tool()
def list_files() -> str:
    """List all files in the workspace."""
    try:
        files = []
        for file_path in WORKSPACE_PATH.iterdir():
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        response = {
            "success": True,
            "file_count": len(files),
            "files": files
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)

@mcp.tool()
def search_content(query: str) -> str:
    """Search for content across all workspace files."""
    try:
        results = []
        for file_path in WORKSPACE_PATH.iterdir():
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    if query.lower() in content.lower():
                        # Find line numbers where query appears
                        lines = content.split('\n')
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if query.lower() in line.lower():
                                matches.append({
                                    "line_number": i,
                                    "line_content": line.strip()
                                })
                        
                        results.append({
                            "filename": file_path.name,
                            "match_count": len(matches),
                            "matches": matches[:5]  # Limit to first 5 matches per file
                        })
                except:
                    continue
        
        response = {
            "success": True,
            "query": query,
            "files_searched": len(list(WORKSPACE_PATH.glob("*"))),
            "files_with_matches": len(results),
            "results": results
        }
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "query": query,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)

@mcp.tool()
def employee_summary(employee_id: Optional[int] = None) -> str:
    """Get detailed summary of employee information."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if employee_id:
            # Get specific employee with their projects and tasks
            cursor.execute("""
                SELECT e.*, COUNT(DISTINCT p.id) as projects_leading, 
                       COUNT(DISTINCT t.id) as tasks_assigned
                FROM employees e
                LEFT JOIN projects p ON e.id = p.team_lead_id
                LEFT JOIN tasks t ON e.id = t.assignee_id
                WHERE e.id = ?
                GROUP BY e.id
            """, (employee_id,))
            
            employee = cursor.fetchone()
            if not employee:
                response = {
                    "success": False,
                    "employee_id": employee_id,
                    "error": "Employee not found"
                }
            else:
                # Get employee's current projects
                cursor.execute("""
                    SELECT p.name, p.status, p.budget
                    FROM projects p
                    WHERE p.team_lead_id = ?
                """, (employee_id,))
                projects = [dict(row) for row in cursor.fetchall()]
                
                # Get employee's current tasks
                cursor.execute("""
                    SELECT t.title, t.status, t.priority, t.due_date, p.name as project_name
                    FROM tasks t
                    JOIN projects p ON t.project_id = p.id
                    WHERE t.assignee_id = ?
                """, (employee_id,))
                tasks = [dict(row) for row in cursor.fetchall()]
                
                response = {
                    "success": True,
                    "employee": dict(employee),
                    "projects_leading": projects,
                    "tasks_assigned": tasks
                }
        else:
            # Get all employees summary
            cursor.execute("""
                SELECT e.*, 
                       COUNT(DISTINCT p.id) as projects_leading,
                       COUNT(DISTINCT t.id) as tasks_assigned
                FROM employees e
                LEFT JOIN projects p ON e.id = p.team_lead_id
                LEFT JOIN tasks t ON e.id = t.assignee_id
                GROUP BY e.id
                ORDER BY e.department, e.name
            """)
            employees = [dict(row) for row in cursor.fetchall()]
            
            response = {
                "success": True,
                "employee_count": len(employees),
                "employees": employees
            }
        
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "employee_id": employee_id,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)
    finally:
        conn.close()

@mcp.tool()
def project_status(project_id: Optional[int] = None) -> str:
    """Get comprehensive project status and analytics."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if project_id:
            # Get specific project details
            cursor.execute("""
                SELECT p.*, e.name as team_lead_name, e.email as team_lead_email
                FROM projects p
                JOIN employees e ON p.team_lead_id = e.id
                WHERE p.id = ?
            """, (project_id,))
            
            project = cursor.fetchone()
            if not project:
                response = {
                    "success": False,
                    "project_id": project_id,
                    "error": "Project not found"
                }
            else:
                # Get project tasks
                cursor.execute("""
                    SELECT t.*, e.name as assignee_name
                    FROM tasks t
                    JOIN employees e ON t.assignee_id = e.id
                    WHERE t.project_id = ?
                    ORDER BY t.priority, t.due_date
                """, (project_id,))
                tasks = [dict(row) for row in cursor.fetchall()]
                
                # Calculate project progress
                total_tasks = len(tasks)
                completed_tasks = len([t for t in tasks if t["status"] == "Completed"])
                progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                
                response = {
                    "success": True,
                    "project": dict(project),
                    "tasks": tasks,
                    "progress": {
                        "total_tasks": total_tasks,
                        "completed_tasks": completed_tasks,
                        "percentage": round(progress_percentage, 1)
                    }
                }
        else:
            # Get all projects summary
            cursor.execute("""
                SELECT p.*, e.name as team_lead_name,
                       COUNT(t.id) as total_tasks,
                       SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks
                FROM projects p
                JOIN employees e ON p.team_lead_id = e.id
                LEFT JOIN tasks t ON p.id = t.project_id
                GROUP BY p.id
                ORDER BY p.status, p.start_date DESC
            """)
            projects = []
            for row in cursor.fetchall():
                project_dict = dict(row)
                total = project_dict["total_tasks"] or 0
                completed = project_dict["completed_tasks"] or 0
                project_dict["progress_percentage"] = round((completed / total * 100) if total > 0 else 0, 1)
                projects.append(project_dict)
            
            response = {
                "success": True,
                "project_count": len(projects),
                "projects": projects
            }
        
        return json.dumps(response, indent=2)
    except Exception as e:
        error_response = {
            "success": False,
            "project_id": project_id,
            "error": str(e)
        }
        return json.dumps(error_response, indent=2)
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Real MCP Project Template Server (FastMCP)")
    print("This is a proper MCP server using the official MCP SDK")
    print("Use this with an MCP client like the example/client.py")
    print("")
    print("To run: python fastmcp_project_template.py")
    print("To test: python example/client.py fastmcp_project_template.py")
    print("")
    print("Available tools:")
    print("  - query_database: Execute SQL queries")
    print("  - read_file: Read workspace files")
    print("  - list_files: List all files")
    print("  - search_content: Search across files")
    print("  - employee_summary: Get employee information")
    print("  - project_status: Get project details")
    
    # Run the MCP server
    mcp.run(transport='stdio')
