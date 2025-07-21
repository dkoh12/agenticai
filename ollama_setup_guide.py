"""
How to set up Ollama - FREE local AI for LangChain practice
"""

print("🤖 Setting up Ollama - FREE Local AI")
print("=" * 50)

print("📋 Step-by-Step Setup:")
print("1. Install Ollama:")
print("   macOS: brew install ollama")
print("   Linux: curl -fsSL https://ollama.ai/install.sh | sh")
print("   Windows: Download from ollama.ai")

print("\n2. Start Ollama service:")
print("   ollama serve")

print("\n3. Download a model (first time only):")
print("   ollama pull llama3.2        # 2GB, fast")
print("   ollama pull codellama       # 3.8GB, good for code")
print("   ollama pull mistral         # 4.1GB, general purpose")

print("\n4. Test it works:")
print("   ollama run llama3.2")
print("   >>> Hello! How are you?")

print("\n" + "=" * 50)
print("🔧 Using Ollama with LangChain:")

code_example = '''
# Install the Ollama LangChain integration
# pip install langchain-ollama

from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Create LLM (FREE!)
llm = ChatOllama(model="llama3.2")

# Same prompt templates as before
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Explain {topic} in simple terms.")
])

# Same chain pattern!
chain = prompt | llm | StrOutputParser()

# Use it exactly like OpenAI!
result = chain.invoke({"topic": "machine learning"})
print(result)
'''

print(code_example)

print("=" * 50)
print("⚡ Quick Comparison:")
print("")

comparison = [
    ["Feature", "OpenAI API", "Ollama (Local)"],
    ["Cost", "$0.002/1K tokens", "100% FREE"],
    ["Speed", "Very fast", "Moderate (depends on computer)"],
    ["Quality", "Excellent", "Good (improving rapidly)"],
    ["Privacy", "Sent to OpenAI", "Stays on your computer"],
    ["Internet", "Required", "Works offline"],
    ["Setup", "Just API key", "Download model (~2-4GB)"],
    ["Rate limits", "Yes (but generous)", "None"],
]

for row in comparison:
    print(f"{row[0]:<12} | {row[1]:<15} | {row[2]}")

print("\n💡 BEST STRATEGY:")
print("1. 🆓 Learn concepts with our mock examples")
print("2. 🤖 Practice with Ollama (free, good quality)")
print("3. 🎯 Test with OpenAI when you're ready to build something real")

print("\n🎁 All our LangChain examples work with ANY LLM provider!")
print("   Just swap: ChatOpenAI() → ChatOllama() → Any other LLM")
