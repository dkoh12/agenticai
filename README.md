# 🤖 Agentic AI Practice Workspace

This workspace is set up for practicing with LangChain and LangGraph to build sophisticated AI agent workflows.

## 📁 Project Structure

```
agenticai/
├── README.md                          # This file
├── LICENSE                           # MIT License
├── requirements.txt                  # Python dependencies
├── .env.example                     # Environment variables template
├── langchain_langgraph_practice.ipynb  # Interactive practice notebook
└── examples/                        # Example implementations
    ├── 01_basic_chain.py           # Simple LangChain example
    ├── 02_agent_with_tools.py      # Agent with calculator tool
    ├── 03_langgraph_workflow.py    # Basic LangGraph workflow
    └── 04_multi_agent_workflow.py  # Complex multi-agent system
```

## 🚀 Quick Start

### 1. Set up your environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start practicing!

#### Option A: Interactive Notebook (Recommended for Learning)
Open `langchain_langgraph_practice.ipynb` in VS Code and follow the interactive exercises.

#### Option B: Run Example Scripts
```bash
# Basic chain example
python examples/01_basic_chain.py

# Agent with tools
python examples/02_agent_with_tools.py

# LangGraph workflow
python examples/03_langgraph_workflow.py

# Multi-agent workflow
python examples/04_multi_agent_workflow.py
```

## 🎯 What You'll Learn

### 1. **LangChain Fundamentals**
- Creating chains with prompts and LLMs
- Building agents with tools
- Memory and conversation management
- Output parsing and formatting

### 2. **LangGraph Workflows**
- Graph-based agent architectures
- State management across nodes
- Conditional routing and branching
- Multi-agent coordination

### 3. **Advanced Patterns**
- Tool integration and custom functions
- Error handling and recovery
- Performance optimization
- Testing and debugging strategies

## 📊 Example Workflows Included

### 1. **Calculator Agent** (`01_basic_chain.py`)
Simple agent that can perform mathematical calculations using tools.

### 2. **Problem Analysis Workflow** (`03_langgraph_workflow.py`)
LangGraph workflow that analyzes problems and provides recommendations.

### 3. **Multi-Agent Content Creation** (`04_multi_agent_workflow.py`)
Complex workflow with specialized agents for different types of content creation:
- Technical content agent
- Creative writing agent
- Business content agent
- Educational content agent
- Review and revision system

## 🛠️ Key Technologies

- **LangChain**: Framework for building LLM applications
- **LangGraph**: Library for building stateful, multi-actor applications
- **OpenAI GPT**: Primary LLM provider (easily swappable)
- **Python**: Programming language
- **Jupyter**: Interactive development environment

## 🔧 Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

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


