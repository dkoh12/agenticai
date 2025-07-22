"""
Basic LangChain example: Simple chain with prompt template and LLM
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Load environment variables
load_dotenv()

def basic_chain_example():
    """Simple chain: Prompt -> LLM -> Output Parser"""
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.7
    )
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that explains concepts clearly."),
        ("human", "Explain {topic} in simple terms with an example.")
    ])
    
    # Create output parser
    output_parser = StrOutputParser()
    
    # Chain them together
    chain = prompt | llm | output_parser
    
    return chain

def run_example():
    """Run the basic chain example"""
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set your OPENAI_API_KEY in the .env file")
        return
    
    chain = basic_chain_example()
    
    # Test the chain
    topics = ["machine learning", "blockchain", "quantum computing"]
    
    for topic in topics:
        print(f"\n=== Explaining: {topic} ===")
        result = chain.invoke({"topic": topic})
        print(result)
        print("-" * 50)

if __name__ == "__main__":
    run_example()
