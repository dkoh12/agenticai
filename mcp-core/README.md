# MCP (Model Context Protocol) Core

This folder contains core MCP examples, templates, and integrations.

## Contents

### Core MCP Examples
- `mcp_system_demo.py` - Complete MCP system demonstration
- `mcp_project_template.py` - Template for creating MCP projects
- `mcp_langchain_integration.py` - Integration between MCP and LangChain

### Documentation
- `MCP_GUIDE.md` - Comprehensive guide to MCP implementation

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
