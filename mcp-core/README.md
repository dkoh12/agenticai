# Real MCP SDK Integration with LangChain and Ollama

This directory contains a **refactored implementation** that uses the official Model Context Protocol (MCP) SDK to build production-ready MCP servers and clients that integrate with LangChain and Ollama.

## 📁 File Structure (REFACTORED)

### New Modular Architecture:

#### `mcp_server.py` - MCP Server Implementation
- **Purpose**: Production-ready MCP server using official MCP SDK
- **Features**:
  - Real `@server.tool()` decorators for tool registration
  - Database access tools with SQL query execution
  - Document access tools for company policies and reports
  - Proper MCP protocol implementation
  - stdio server for client connections
  - Comprehensive logging and error handling

#### `mcp_client.py` - MCP Client Implementation
- **Purpose**: MCP client that connects to servers and provides LangChain integration
- **Features**:
  - Real MCP client with stdio communication
  - Automatic tool discovery and listing
  - LangChain tool conversion utilities
  - Connection management and error handling
  - Simplified fallback tools for demo purposes

#### `mcp_langchain_demo.py` - Integration Demo
- **Purpose**: Demonstrates MCP + LangChain + Ollama integration
- **Features**:
  - Multiple demo modes (automated, interactive, architecture info)
  - Real Ollama LLM integration for natural language responses
  - LangChain tool orchestration
  - Interactive chat interface
  - Production architecture examples

### Legacy Files:
- `mcp_langchain_integration.py` - Original monolithic file (can be removed)
- `mcp_system_demo.py` - Basic MCP system demonstration
- `mcp_project_template.py` - Template for creating MCP projects

## What is MCP?

Model Context Protocol (MCP) is a standardized way for AI applications to securely access external data and tools. It provides:

- **Secure tool access** - Controlled access to external systems
- **Standardized interfaces** - Consistent API patterns
- **Resource management** - Efficient handling of external resources
- **Integration flexibility** - Works with various AI frameworks

## Getting Started

1. Install dependencies:
   ```bash
   pip install mcp langchain
   ```

2. Review the MCP guide:
   ```bash
   cat MCP_GUIDE.md
   ```

3. Start with the system demo:
   ```bash
   python mcp_system_demo.py
   ```

4. Use the project template for new MCP implementations

## Key Features

- Tool registration and execution
- Resource management
- LangChain integration
- Extensible architecture
- Security and sandboxing
