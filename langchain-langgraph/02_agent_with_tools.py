"""
Advanced LangChain example: Multiple chains with memory and tools
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.output_parser import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub

# Load environment variables
load_dotenv()

def calculator_tool(expression: str) -> str:
    """Simple calculator tool"""
    try:
        result = eval(expression)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

def create_research_agent():
    """Create an agent with tools and memory"""
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Define tools
    tools = [
        Tool(
            name="calculator",
            description="Useful for mathematical calculations. Input should be a mathematical expression.",
            func=calculator_tool
        )
    ]
    
    # Get a pre-built prompt from the hub
    prompt = hub.pull("hwchase17/openai-functions-agent")
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3
    )
    
    return agent_executor

def run_agent_example():
    """Run the agent example"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file")
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
