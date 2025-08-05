# CrewAI Agent-to-Agent Communication Examples

This folder contains examples of **true Agent-to-Agent (A2A) communication** using CrewAI framework with local Ollama models.

## 🎯 What is A2A Communication?

**Agent-to-Agent (A2A)** communication means agents talk **directly to each other**, not through a central orchestrator. Think of it like a human conversation or meeting where people respond to each other dynamically.

### A2A vs Orchestrated Workflows

| **CrewAI (A2A)** | **LangGraph (Orchestrated)** |
|---|---|
| Agents decide who to talk to | Central orchestrator controls flow |
| Conversational, back-and-forth | Sequential state processing |
| Emergent solutions | Predictable workflows |
| Dynamic group discussions | Predetermined execution paths |
| Human-like team dynamics | Reliable, repeatable processes |

## 🛠️ Setup Instructions

### 1. Install CrewAI
```bash
pip install crewai
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
# Basic A2A conversation
python 01_simple_crewai_chat.py

# Agent debate and negotiation
python 02_agent_debate.py

# Advanced multi-agent collaboration
python 03_advanced_crewai_collaboration.py
```

## 📁 File Descriptions

### `01_simple_crewai_chat.py`
**Basic A2A Communication**
- Student and Teacher agents having educational conversation
- Shows `allow_delegation=True` enabling A2A communication
- Demonstrates real agent-to-agent communication with Ollama

**Key Features:**
- Student asks questions about neural networks
- Teacher responds and asks follow-up questions
- Natural conversational flow between agents

### `02_agent_debate.py`
**Agent Debate and Negotiation**
- Remote Work Advocate vs Office Work Advocate
- Agents present arguments and counter-arguments
- Collaborative consensus building

**Key Features:**
- Opposing viewpoints and structured debate
- Agents work toward compromise solution
- Real negotiation and consensus building

### `03_advanced_crewai_collaboration.py`
**Advanced Multi-Agent Collaboration**
- Research collaboration between Researcher, Writer, and Critic
- Complex multi-step workflows with agent autonomy
- Negotiation and quality review cycles

**Key Features:**
- 3-agent research → writing → review workflow
- Buyer-seller negotiation scenarios
- Advanced delegation patterns

## 🤝 Key A2A Communication Patterns

### 1. Agent Delegation
```python
# Agents use delegation to communicate
student = Agent(
    role="Curious Student",
    allow_delegation=True  # Enables A2A communication
)
teacher = Agent(
    role="AI Teacher", 
    allow_delegation=True  # Can respond to student
)
```

### 2. Collaborative Workflows
```python
# Sequential collaboration with dependencies
research_task = Task(description="Research AI trends", agent=researcher)
writing_task = Task(
    description="Write based on research", 
    agent=writer,
    dependencies=[research_task]  # Creates collaboration
)
```

### 3. Multi-Agent Crews
```python
# Multiple agents working together
crew = Crew(
    agents=[researcher, writer, critic],
    tasks=[research_task, writing_task, review_task],
    process="sequential"  # Enables agent collaboration
)
```

### 4. Real-Time Agent Communication
- Agents ask questions to coworkers using `🔧 Using Ask question to coworker`
- Dynamic conversation flow based on agent decisions
- Autonomous collaboration without central control

## 🔍 Compare with LangGraph Examples

To see the difference, compare these A2A examples with the orchestrated workflows in:
- `../langchain-langgraph/03_langgraph_workflow.py`
- `../langchain-langgraph/04_multi_agent_workflow.py`

**Key Differences:**
- **AutoGen**: Agents have conversations, build on each other's ideas, negotiate
- **LangGraph**: Central orchestrator routes between predefined functions

## 🎯 When to Use A2A Communication

**Use CrewAI A2A when you want:**
- Brainstorming and creative collaboration
- Educational conversations and mentoring
- Negotiation scenarios and debate
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
✅ **Real A2A Framework**: CrewAI provides working A2A communication

## 🔧 Troubleshooting

### CrewAI Import Error
```bash
pip install crewai
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

### Agent Conversations Taking Too Long
- Agents thinking extensively means they're working properly
- The `🧠 Thinking...` indicates real agent processing
- `🔧 Using Ask question to coworker` shows A2A communication happening

## 💡 Next Steps

1. **Run the examples** to see real A2A communication in action
2. **Experiment** with different agent personalities and roles
3. **Compare** with the LangGraph examples in `../langchain-langgraph/`
4. **Create custom crews** with your own agent combinations

The future of AI is agents working together autonomously! 🚀
