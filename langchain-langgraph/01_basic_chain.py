"""
Basic LangChain example: Simple chain with prompt template and LLM
Using Ollama's Llama3.2 (local, free alternative to OpenAI)

Setup Instructions:
1. Install Ollama: https://ollama.ai/download
2. Pull the model: ollama pull llama3.2
3. Start Ollama: ollama serve (or just run ollama)
4. Install the new langchain-ollama package: pip install -U langchain-ollama
5. Run this script!

Advantages of Ollama:
- 100% Free and local
- No API keys required
- Works offline
- Privacy-focused
"""

import os
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

def basic_chain_example():
    """Simple chain: Prompt -> LLM -> Output Parser"""
    
    # Initialize Ollama with Llama3.2 model (using new OllamaLLM class)
    llm = OllamaLLM(
        model="llama3.2",
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
    """Run the basic chain example with Ollama"""
    
    # Check if Ollama is available
    try:
        # Test connection to Ollama (using new OllamaLLM class)
        test_llm = OllamaLLM(model="llama3.2")
        print("✅ Ollama connection successful!")
    except Exception as e:
        print("❌ Ollama not available. Please install and start Ollama first:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Install langchain-ollama: pip install -U langchain-ollama")
        print("   3. Run: ollama pull llama3.2")
        print("   4. Start: ollama serve")
        print(f"   Error: {e}")
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
