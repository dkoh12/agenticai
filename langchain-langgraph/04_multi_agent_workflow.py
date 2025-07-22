"""
Advanced LangGraph example: Multi-agent workflow with conditional routing
"""

import os
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

# Load environment variables
load_dotenv()

# Define the state
class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task_type: str
    content: str
    review_feedback: str
    final_output: str
    iteration_count: int

def classify_task(state: MultiAgentState) -> MultiAgentState:
    """Classify the type of task"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Classify the user's request into one of these categories:
        - 'creative': Creative writing, storytelling, poetry
        - 'technical': Code, documentation, technical explanations
        - 'analytical': Analysis, research, data interpretation
        - 'general': General questions or other tasks
        
        Respond with just the category name."""),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    user_input = state["messages"][-1].content if state["messages"] else ""
    task_type = chain.invoke({"input": user_input}).strip().lower()
    
    return {
        **state,
        "task_type": task_type,
        "iteration_count": 0
    }

def creative_agent(state: MultiAgentState) -> MultiAgentState:
    """Handle creative tasks"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.8)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a creative writing assistant. Create engaging, imaginative content."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    user_input = state["messages"][-1].content if state["messages"] else ""
    content = chain.invoke({"input": user_input})
    
    return {
        **state,
        "content": content
    }

def technical_agent(state: MultiAgentState) -> MultiAgentState:
    """Handle technical tasks"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical expert. Provide accurate, detailed technical information and solutions."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    user_input = state["messages"][-1].content if state["messages"] else ""
    content = chain.invoke({"input": user_input})
    
    return {
        **state,
        "content": content
    }

def analytical_agent(state: MultiAgentState) -> MultiAgentState:
    """Handle analytical tasks"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a data analyst. Provide structured analysis with clear insights and conclusions."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    user_input = state["messages"][-1].content if state["messages"] else ""
    content = chain.invoke({"input": user_input})
    
    return {
        **state,
        "content": content
    }

def general_agent(state: MultiAgentState) -> MultiAgentState:
    """Handle general tasks"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Provide clear, helpful responses to user questions."),
        ("human", "{input}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    user_input = state["messages"][-1].content if state["messages"] else ""
    content = chain.invoke({"input": user_input})
    
    return {
        **state,
        "content": content
    }

def review_agent(state: MultiAgentState) -> MultiAgentState:
    """Review and provide feedback on the content"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a quality reviewer. Evaluate the content and provide feedback.
        Rate the content on a scale of 1-10 and suggest improvements if needed.
        If the score is 8 or above, respond with 'APPROVED'.
        If below 8, provide specific feedback for improvement."""),
        ("human", "Content to review: {content}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    feedback = chain.invoke({"content": state["content"]})
    
    return {
        **state,
        "review_feedback": feedback,
        "iteration_count": state["iteration_count"] + 1
    }

def finalize_output(state: MultiAgentState) -> MultiAgentState:
    """Finalize the output"""
    return {
        **state,
        "final_output": state["content"]
    }

def route_by_task_type(state: MultiAgentState) -> Literal["creative", "technical", "analytical", "general"]:
    """Route to appropriate agent based on task type"""
    task_type = state["task_type"]
    if task_type in ["creative"]:
        return "creative"
    elif task_type in ["technical"]:
        return "technical"
    elif task_type in ["analytical"]:
        return "analytical"
    else:
        return "general"

def should_continue_review(state: MultiAgentState) -> Literal["finalize", "revise"]:
    """Decide whether to finalize or revise based on review"""
    feedback = state["review_feedback"].lower()
    max_iterations = 2
    
    if "approved" in feedback or state["iteration_count"] >= max_iterations:
        return "finalize"
    else:
        return "revise"

def revise_content(state: MultiAgentState) -> MultiAgentState:
    """Revise content based on feedback"""
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Revise the content based on the feedback provided. Improve quality and address the concerns."),
        ("human", "Original content: {content}\n\nFeedback: {feedback}\n\nProvide improved version:")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    revised_content = chain.invoke({
        "content": state["content"],
        "feedback": state["review_feedback"]
    })
    
    return {
        **state,
        "content": revised_content
    }

def create_multi_agent_workflow():
    """Create a multi-agent workflow with conditional routing"""
    
    workflow = StateGraph(MultiAgentState)
    
    # Add nodes
    workflow.add_node("classify", classify_task)
    workflow.add_node("creative", creative_agent)
    workflow.add_node("technical", technical_agent)
    workflow.add_node("analytical", analytical_agent)
    workflow.add_node("general", general_agent)
    workflow.add_node("review", review_agent)
    workflow.add_node("revise", revise_content)
    workflow.add_node("finalize", finalize_output)
    
    # Define the flow
    workflow.set_entry_point("classify")
    
    # Route to appropriate agent
    workflow.add_conditional_edges(
        "classify",
        route_by_task_type,
        {
            "creative": "creative",
            "technical": "technical",
            "analytical": "analytical",
            "general": "general"
        }
    )
    
    # All agents go to review
    workflow.add_edge("creative", "review")
    workflow.add_edge("technical", "review")
    workflow.add_edge("analytical", "review")
    workflow.add_edge("general", "review")
    
    # Conditional routing after review
    workflow.add_conditional_edges(
        "review",
        should_continue_review,
        {
            "finalize": "finalize",
            "revise": "revise"
        }
    )
    
    # After revision, go back to review
    workflow.add_edge("revise", "review")
    workflow.add_edge("finalize", END)
    
    app = workflow.compile()
    return app

def run_multi_agent_example():
    """Run the multi-agent workflow example"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file")
        return
    
    app = create_multi_agent_workflow()
    
    # Test different types of tasks
    tasks = [
        "Write a short story about a robot learning to paint",
        "Explain how to implement a binary search algorithm in Python",
        "Analyze the pros and cons of remote work vs office work",
        "What's the weather like today?"
    ]
    
    for task in tasks:
        print(f"\n=== Task: {task} ===")
        
        result = app.invoke({
            "messages": [{"role": "user", "content": task}],
            "task_type": "",
            "content": "",
            "review_feedback": "",
            "final_output": "",
            "iteration_count": 0
        })
        
        print(f"Task Type: {result['task_type']}")
        print(f"Iterations: {result['iteration_count']}")
        print(f"Final Output:\n{result['final_output']}")
        print("-" * 80)

if __name__ == "__main__":
    run_multi_agent_example()
