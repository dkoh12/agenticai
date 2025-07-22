# 🤖 Agentic AI Learning Repository

A comprehensive collection of AI agent examples, MCP implementations, and practical applications for learning agentic AI workflows.

## 📁 Repository Structure

This repository is organized into three main sections:

### 🔗 [langchain-langgraph/](./langchain-langgraph/)
Complete learning materials for LangChain and LangGraph agentic AI workflows.
- Basic chains and agents
- Multi-agent coordination
- Free alternatives to paid APIs
- Interactive Jupyter notebooks
- Local model setup with Ollama

### 🔧 [mcp-core/](./mcp-core/)
Core Model Context Protocol (MCP) examples and integrations.
- MCP system demonstrations
- Project templates
- LangChain-MCP integration
- Comprehensive documentation

### 💰 [finance-mcp-app/](./finance-mcp-app/)
Complete personal finance management application with MCP backend and web interface.
- Modern Flask web dashboard
- Budget alerts and monitoring
- Transaction management
- AI-powered financial insights
- Interactive charts and reports

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agenticai
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Choose your learning path:**
   - **New to LangChain?** → Start with [`langchain-langgraph/`](./langchain-langgraph/)
   - **Interested in MCP?** → Explore [`mcp-core/`](./mcp-core/)
   - **Want a complete app?** → Try [`finance-mcp-app/`](./finance-mcp-app/)

## 🎯 What You'll Learn

- **Agentic AI Patterns** - Building autonomous AI agents
- **Tool Integration** - Connecting AI to external systems
- **Multi-Agent Systems** - Coordinating multiple AI agents
- **MCP Protocol** - Standardized tool and resource access
- **Real-World Applications** - Practical AI implementations
- **Cost-Effective Solutions** - Using free alternatives to paid APIs

## 📋 Prerequisites

- Python 3.8+
- Basic understanding of Python
- Interest in AI and automation

## � Project Structure

```
agenticai/
├── README.md                      # This file  
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
├── .env.example                 # Environment variables template
├── langchain-langgraph/         # LangChain & LangGraph learning materials
│   ├── README.md               # LangChain/LangGraph documentation
│   ├── 01_basic_chain.py       # Simple LangChain example
│   ├── 02_agent_with_tools.py  # Agent with calculator tool
│   ├── 03_langgraph_workflow.py # Basic LangGraph workflow
│   ├── 04_multi_agent_workflow.py # Complex multi-agent system
│   ├── langchain_langgraph_practice.ipynb # Interactive notebook
│   ├── free_practice.py        # Free alternatives examples
│   ├── free_alternatives_guide.py # Guide to free APIs
│   └── ollama_setup_guide.py   # Local model setup
├── mcp-core/                    # Model Context Protocol examples
│   ├── README.md               # MCP documentation
│   ├── MCP_GUIDE.md           # Comprehensive MCP guide
│   ├── mcp_system_demo.py     # Complete MCP demo
│   ├── mcp_project_template.py # MCP project template
│   └── mcp_langchain_integration.py # MCP-LangChain integration
└── finance-mcp-app/            # Complete finance management app
    ├── README.md               # Finance app documentation
    ├── finance_web_app.py      # Flask web application
    ├── finance_mcp_tool.py     # MCP backend
    ├── finance_langchain_integration.py # AI features
    ├── create_demo_data.py     # Sample data generator
    ├── run_finance_web.sh      # Quick start script
    ├── WEB_INTERFACE_GUIDE.md  # Web interface guide
    ├── FIXES_APPLIED.md        # Troubleshooting guide
    ├── templates/              # HTML templates
    │   ├── base.html          # Base template
    │   ├── dashboard.html     # Main dashboard
    │   ├── transactions.html  # Transaction management
    │   ├── budgets.html      # Budget monitoring
    │   └── reports.html      # Reports and analytics
    └── data/                  # Database files
        └── finance.db         # SQLite database
```

## � Learning Paths

### Path 1: LangChain Fundamentals
1. Start with `langchain-langgraph/README.md`
2. Work through the numbered examples (01-04)
3. Use the interactive notebook for practice
4. Explore free alternatives if you don't have API keys

### Path 2: MCP Deep Dive
1. Read `mcp-core/MCP_GUIDE.md`
2. Run `mcp_system_demo.py` to see MCP in action
3. Use `mcp_project_template.py` for your own projects
4. Integrate with LangChain using the integration example

### Path 3: Complete Application
1. Go to `finance-mcp-app/`
2. Follow the README setup instructions
3. Run the web application
4. Explore the source code to understand the architecture

## � Setup Instructions

### 1. Environment Setup
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your API keys (optional for free alternatives)
# OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Choose Your Starting Point
- **Beginners**: Start with `langchain-langgraph/`
- **Advanced**: Jump to `mcp-core/` or `finance-mcp-app/`

## 🌟 Key Features

- **Progressive Learning** - From basics to advanced implementations
- **Cost-Conscious** - Free alternatives to paid APIs included
- **Practical Applications** - Real-world examples and complete applications
- **Modern Architecture** - MCP protocol and best practices
- **Interactive Learning** - Jupyter notebooks and web interfaces
- **Comprehensive Documentation** - Detailed guides and troubleshooting

## � Getting Help

- Each folder has its own README with specific instructions
- Check troubleshooting guides in the respective folders
- Look at code comments for implementation details
- Use the interactive notebooks for hands-on learning

## 🤝 Contributing

Feel free to contribute examples, improvements, or bug fixes:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

### Optional Environment Variables
```bash
# For LangSmith tracing and monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=agenticai-practice

# For other LLM providers
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

## 🎓 Learning Path

1. **Start with the Notebook**: Work through `langchain_langgraph_practice.ipynb` for hands-on learning
2. **Explore Examples**: Run and modify the example scripts
3. **Build Your Own**: Create custom agents for your specific use cases
4. **Advanced Topics**: Explore memory, tools, and complex workflows

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Make sure you've set `OPENAI_API_KEY` in your `.env` file
- Verify the API key is valid and has sufficient credits

**"Module not found" errors**
- Run `pip install -r requirements.txt` to install dependencies
- Make sure you're using the correct Python environment

**LangGraph workflow errors**
- Check that all state fields are properly defined
- Ensure node functions return the correct state format

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [LangSmith for Debugging](https://smith.langchain.com/)

## 🤝 Contributing

This is a practice workspace! Feel free to:
- Add new examples
- Improve existing code
- Create additional workflows
- Share your custom agents

## 📄 License

MIT License - see LICENSE file for details.

---

Happy building with LangChain and LangGraph! 🎉


