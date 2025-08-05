"""
LangGraph example: Simple state machine workflow using Ollama
Using Ollama's Llama3.2 (local, free alternative to OpenAI)

Setup Instructions:
1. Install Ollama: https://ollama.ai/download
2. Pull the model: ollama pull llama3.2
3. Start Ollama: ollama serve (or just run ollama)
4. Run this script!

This example shows:
- LangGraph state machine workflow
- Problem analysis and recommendations
- Multi-step reasoning with state management
"""

import warnings
from typing import TypedDict, Annotated
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
# Langgraph basically helps you build a DAG workflow for agents

# Suppress deprecation warnings for cleaner output
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_step: str
    analysis_result: str
    recommendation: str

def analyze_problem(state: AgentState) -> AgentState:
    """Analyze the user's problem"""
    llm = OllamaLLM(model="llama3.2", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert analyst. Analyze the given problem and provide a structured analysis."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    # Get the last user message
    user_input = state["messages"][-1].content if state["messages"] else ""
    
    # the dictionary key must match the variable name in the prompt
    # e.g. "{input}" in the prompt means you must pass "input" as the key
    # when invoking the chain
    analysis = chain.invoke({"input": user_input})
    
    return {
        **state,
        "current_step": "analysis_complete",
        "analysis_result": analysis
    }

def generate_recommendation(state: AgentState) -> AgentState:
    """Generate recommendations based on analysis"""
    llm = OllamaLLM(model="llama3.2", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Based on the analysis provided, generate practical recommendations and next steps."),
        ("human", "Analysis: {analysis}\n\nProvide 3-5 concrete recommendations.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    recommendation = chain.invoke({"analysis": state["analysis_result"]})
    
    return {
        **state,
        "current_step": "recommendation_complete",
        "recommendation": recommendation
    }

"""
START → [analyze] → [recommend] → END
         ↓            ↓
    Updates state   Updates state
    with analysis   with recommendations
"""
def create_analysis_workflow():
    """Create a LangGraph workflow for problem analysis"""
    
    # Create the state graph with AgentState as its shared memory
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze", analyze_problem)
    workflow.add_node("recommend", generate_recommendation)
    
    # Define the flow
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "recommend")
    workflow.add_edge("recommend", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app

def run_workflow_example():
    """Run the LangGraph workflow example"""
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
    
    app = create_analysis_workflow()
    
    # Test problems
    problems = [
        "I want to start learning machine learning but don't know where to begin.",
        "My team is having communication issues during remote work.",
        "I need to choose between Python and JavaScript for my next project."
    ]
    
    for problem in problems:
        print(f"\n=== Problem: {problem} ===")
        
        # Run the workflow
        result = app.invoke({
            "messages": [{"role": "user", "content": problem}],
            "current_step": "start",
            "analysis_result": "",
            "recommendation": ""
        })
        
        print(f"\nAnalysis:\n{result['analysis_result']}")
        print(f"\nRecommendations:\n{result['recommendation']}")
        print("-" * 80)

if __name__ == "__main__":
    run_workflow_example()
