"""
LangGraph example: Simple state machine workflow
"""

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_step: str
    analysis_result: str
    recommendation: str

def analyze_problem(state: AgentState) -> AgentState:
    """Analyze the user's problem"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert analyst. Analyze the given problem and provide a structured analysis."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    # Get the last user message
    user_input = state["messages"][-1].content if state["messages"] else ""
    
    analysis = chain.invoke({"input": user_input})
    
    return {
        **state,
        "current_step": "analysis_complete",
        "analysis_result": analysis
    }

def generate_recommendation(state: AgentState) -> AgentState:
    """Generate recommendations based on analysis"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    
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

def create_analysis_workflow():
    """Create a LangGraph workflow for problem analysis"""
    
    # Create the state graph
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
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file")
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
