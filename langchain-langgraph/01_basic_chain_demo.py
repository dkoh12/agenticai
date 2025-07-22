"""
Demo version of basic LangChain chain - shows structure without API calls
"""

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

def demo_basic_chain():
    """Demonstrates the structure of a basic chain without API calls"""
    
    print("🔗 Creating a Basic LangChain Chain")
    print("=" * 50)
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that explains concepts clearly."),
        ("human", "Explain {topic} in simple terms with an example.")
    ])
    
    print("✅ Step 1: Prompt Template Created")
    print(f"📝 Template: {prompt.format_messages(topic='example topic')[1].content}")
    print()
    
    # Create output parser
    output_parser = StrOutputParser()
    print("✅ Step 2: Output Parser Created")
    print("🔧 Parser will convert LLM response to string")
    print()
    
    # Show how the chain would be constructed
    print("✅ Step 3: Chain Construction")
    print("🔗 chain = prompt | llm | output_parser")
    print("   This creates: Input → Prompt → LLM → Parser → Output")
    print()
    
    # Show what the formatted prompt would look like
    topics = ["machine learning", "blockchain", "quantum computing"]
    
    print("📋 Example inputs and formatted prompts:")
    for topic in topics:
        formatted_messages = prompt.format_messages(topic=topic)
        system_msg = formatted_messages[0].content
        human_msg = formatted_messages[1].content
        
        print(f"\n🎯 Topic: {topic}")
        print(f"   System: {system_msg}")
        print(f"   Human: {human_msg}")
    
    print("\n" + "=" * 50)
    print("🎓 What this demonstrates:")
    print("• How to create prompt templates with variables")
    print("• How to chain components together with | operator")
    print("• How prompts get formatted with actual values")
    print("• The basic pattern: Input → Transform → Output")

if __name__ == "__main__":
    demo_basic_chain()
