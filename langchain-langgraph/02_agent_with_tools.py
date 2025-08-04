"""
Advanced LangChain example: Agent with tools using Ollama
Using Ollama's Llama3.2 (local, free alternative to OpenAI)

Setup Instructions:
1. Install Ollama: https://ollama.ai/download
2. Pull the model: ollama pull llama3.2
3. Start Ollama: ollama serve (or just run ollama)
4. Run this script!

This example shows:
- Agent with custom tools
- Mathematical calculations
- Tool execution and reasoning
"""

import warnings
from langchain_ollama import OllamaLLM
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

def calculator_tool(expression: str) -> str:
    """Simple calculator tool"""
    try:
        # Replace ^ with ** for Python exponentiation
        expression = expression.replace('^', '**')
        # Remove quotes if they exist
        expression = expression.strip('"\'')
        result = eval(expression)
        return str(result)  # Just return the number, not "The result is: X"
    except Exception as e:
        return f"Error: {str(e)}. Use ** for exponentiation, not ^"

def create_research_agent():
    """Create an agent with tools and memory"""
    
    # Initialize the Ollama LLM
    print("Connecting to Ollama (Llama3.2)...")
    llm = OllamaLLM(
        model="llama3.2",
        temperature=0.1
    )
    
    # Define tools
    tools = [
        Tool(
            name="calculator",
            description="Calculate mathematical expressions. Input: Python math expression (use ** for power). Returns: numerical result only.",
            func=calculator_tool
        )
    ]
    
    # Create the agent executor with a compatible agent type for Ollama
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=2,
        handle_parsing_errors=True,
        early_stopping_method="generate"
    )
    
    return agent_executor

def run_agent_example():
    """Run the agent example"""
    # Test Ollama connection first
    try:
        test_llm = OllamaLLM(model="llama3.2")
        test_response = test_llm.invoke("Hello")
        print(f"✅ Ollama connection successful! Test response: {test_response[:50]}...")
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Please make sure:")
        print("1. Ollama is installed and running")
        print("2. Llama3.2 model is downloaded: ollama pull llama3.2")
        return
    
    agent = create_research_agent()
    
    # Test the agent
    queries = [
        "What is 15 * 23 + 100?",
        "Calculate the area of a circle with radius 5 (use π = 3.14159)",
        "If I have $1000 and invest it at 5% annual interest, how much will I have after 3 years?"
    ]
    
    for query in queries:
        print(f"\n=== Query: {query} ===")
        result = agent.invoke({"input": query})
        print(f"Final Answer: {result['output']}")
        print("-" * 50)

if __name__ == "__main__":
    run_agent_example()
