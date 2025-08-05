# AutoGen Agent-to-Agent Communication Examples

This folder contains examples of **true Agent-to-Agent (A2A) communication** using Microsoft's AutoGen framework with local Ollama models.

## 🎯 What is A2A Communication?

**Agent-to-Agent (A2A)** communication means agents talk **directly to each other**, not through a central orchestrator. Think of it like a human conversation or meeting where people respond to each other dynamically.

### A2A vs Orchestrated Workflows

| **AutoGen (A2A)** | **LangGraph (Orchestrated)** |
|---|---|
| Agents decide who to talk to | Central orchestrator controls flow |
| Conversational, back-and-forth | Sequential state processing |
| Emergent solutions | Predictable workflows |
| Dynamic group discussions | Predetermined execution paths |
| Human-like team dynamics | Reliable, repeatable processes |

## 🛠️ Setup Instructions

### 1. Install AutoGen
```bash
pip install pyautogen
```

### 2. Setup Ollama (Free Local AI)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the model
ollama pull llama3.2

# Start Ollama (keep running)
ollama serve
```

### 3. Run the Examples
```bash
# Basic A2A examples
python 01_autogen_basic_a2a.py

# Advanced collaboration patterns  
python 02_autogen_advanced_a2a.py

# Conceptual comparison (works without AutoGen installed)
python 03_autogen_vs_langgraph_comparison.py
```

## 📁 File Descriptions

### `01_autogen_basic_a2a.py`
**Basic A2A Communication Patterns**
- Two agents having direct conversations
- Multi-agent group chats
- Negotiation between agents
- Connection testing

**Key Examples:**
- Researcher ↔ Writer collaboration
- Group chat with Researcher, Writer, Critic
- Buyer ↔ Seller negotiation

### `02_autogen_advanced_a2a.py`
**Advanced A2A Patterns**
- Software development team collaboration
- Academic research partnerships
- Debate and consensus building
- Creative collaboration

**Key Examples:**
- Product Manager, Developer, Frontend Dev, QA working together
- CS Researcher, Psychology Researcher, Stats Expert on a paper
- Optimist vs Pessimist finding consensus
- Writer, Artist, Sound Designer creating a film concept

### `03_autogen_vs_langgraph_comparison.py`
**Conceptual Comparison**
- Side-by-side comparison of A2A vs Orchestrated approaches
- Code pattern examples
- When to use which approach
- Hybrid strategies

## 🤝 Key A2A Communication Patterns

### 1. Direct Agent Conversations
```python
# Agents talk directly to each other
user_proxy.initiate_chat(researcher, message="Research AI trends")
# researcher → writer (autonomous decision)
# writer → researcher (responds directly)
```

### 2. Group Discussions
```python
# Multiple agents in group chat
groupchat = GroupChat(agents=[researcher, writer, critic])
# Agents decide who speaks next
# Dynamic, conversational flow
```

### 3. Role-Based Collaboration
```python
# Agents with different expertise
product_manager = AssistantAgent(name="PM", system_message="Define requirements...")
developer = AssistantAgent(name="Dev", system_message="Technical solutions...")
# They collaborate autonomously based on their roles
```

### 4. Negotiation and Debate
```python
# Agents with opposing viewpoints
buyer = AssistantAgent(name="buyer", system_message="Get best price...")
seller = AssistantAgent(name="seller", system_message="Make good sale...")
# They negotiate directly until reaching agreement
```

## 🔍 Compare with LangGraph Examples

To see the difference, compare these A2A examples with the orchestrated workflows in:
- `../langchain-langgraph/03_langgraph_workflow.py`
- `../langchain-langgraph/04_multi_agent_workflow.py`

**Key Differences:**
- **AutoGen**: Agents have conversations, build on each other's ideas, negotiate
- **LangGraph**: Central orchestrator routes between predefined functions

## 🎯 When to Use A2A Communication

**Use AutoGen A2A when you want:**
- Brainstorming and creative collaboration
- Negotiation scenarios
- Emergent solutions from team interaction
- Human-like group dynamics
- Flexible, conversational problem-solving

**Use LangGraph workflows when you want:**
- Reliable, repeatable processes
- Clear workflow documentation
- Predictable execution paths
- Easy debugging and monitoring
- Structured data processing pipelines

## 🚀 Benefits of A2A with Local Models

✅ **Cost-Free Learning**: Use Ollama instead of OpenAI APIs  
✅ **Privacy**: Everything runs locally  
✅ **Experimentation**: Try unlimited agent conversations  
✅ **Realistic Interactions**: Agents develop dynamic relationships  
✅ **Emergent Behavior**: Solutions emerge from agent collaboration  

## 🔧 Troubleshooting

### AutoGen Import Error
```bash
pip install pyautogen
```

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve

# Pull model if missing
ollama pull llama3.2
```

### Agent Conversations Too Long
- Adjust `max_consecutive_auto_reply` parameter
- Use more specific termination conditions
- Set clearer agent instructions

## 💡 Next Steps

1. **Run the examples** to see A2A communication in action
2. **Experiment** with different agent personalities and roles
3. **Compare** with the LangGraph examples in `../langchain-langgraph/`
4. **Combine approaches** - use LangGraph for workflows, AutoGen for collaborative stages

The future of AI is agents working together autonomously! 🚀
