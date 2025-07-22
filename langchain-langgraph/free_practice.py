"""
Free LangChain Practice - No API Key Required!
This shows how to learn LangChain concepts without spending money on API calls.
"""

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.tools import Tool
from typing import TypedDict, Annotated, Literal
import json

# 1. FREE: Mock LLM for Learning
class FreeLLM:
    """A free mock LLM that responds based on simple patterns"""
    
    def __init__(self, temperature=0.7):
        self.temperature = temperature
        
    def invoke(self, messages):
        """Generate responses based on keywords in the input"""
        # Get the last message content
        if hasattr(messages, 'content'):
            content = messages.content
        elif isinstance(messages, list) and len(messages) > 0:
            content = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        else:
            content = str(messages)
        
        content_lower = content.lower()
        
        # Pattern-based responses for learning
        if any(word in content_lower for word in ['python', 'code', 'programming', 'function']):
            return self._generate_tech_response(content)
        elif any(word in content_lower for word in ['story', 'creative', 'write', 'narrative']):
            return self._generate_creative_response(content)
        elif any(word in content_lower for word in ['business', 'proposal', 'strategy', 'plan']):
            return self._generate_business_response(content)
        elif any(word in content_lower for word in ['calculate', 'math', 'number', '+', '-', '*', '/']):
            return self._generate_math_response(content)
        else:
            return self._generate_general_response(content)
    
    def _generate_tech_response(self, content):
        return """Here's a Python function example:

```python
def bubble_sort(arr):
    \"\"\"
    Sorts an array using bubble sort algorithm
    \"\"\"
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Example usage:
numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers)
print(sorted_numbers)  # [11, 12, 22, 25, 34, 64, 90]
```

This algorithm compares adjacent elements and swaps them if they're in the wrong order."""

    def _generate_creative_response(self, content):
        return """The cobblestone streets of 1920s Paris gleamed wet under the streetlamps as Marie stepped out of the swirling temporal vortex. Her time machine had malfunctioned, leaving her stranded in an era of jazz music and art deco elegance.

She clutched her modern smartphone—now useless without cellular towers—and realized she'd have to blend in until she could find the rare materials needed to repair her temporal displacement device. The scent of fresh croissants and coffee drifted from a nearby café, where she could hear the animated conversations of artists and writers planning their next masterpieces.

Little did she know that her knowledge of future events would soon make her the most sought-after consultant in all of Montparnasse..."""

    def _generate_business_response(self, content):
        return """# Employee Wellness Program Proposal

## Executive Summary
We propose implementing a comprehensive employee wellness program to improve staff health, reduce healthcare costs, and increase productivity.

## Key Components
1. **Fitness Initiatives**
   - On-site gym membership subsidies
   - Weekly yoga classes
   - Walking meeting programs

2. **Mental Health Support**
   - Employee assistance programs
   - Stress management workshops
   - Mental health days

3. **Nutrition Programs**
   - Healthy snack options in break rooms
   - Nutrition education seminars
   - Subsidized healthy meal delivery

## Expected ROI
- 25% reduction in sick days
- 15% increase in employee satisfaction
- $500 per employee annual healthcare savings

## Implementation Timeline
- Month 1-2: Program design and vendor selection
- Month 3: Pilot program launch
- Month 4-6: Full rollout and evaluation"""

    def _generate_math_response(self, content):
        return """I can help with mathematical calculations! Here are some examples:

Basic arithmetic:
- 15 × 23 = 345
- Circle area with radius 5: A = πr² = 3.14159 × 5² = 78.54 square units
- Compound interest: A = P(1 + r)^t = $1000(1.05)³ = $1,157.63

For complex calculations, I recommend using Python:
```python
import math

# Circle area
radius = 5
area = math.pi * radius ** 2
print(f"Area: {area:.2f}")

# Compound interest
principal = 1000
rate = 0.05
time = 3
amount = principal * (1 + rate) ** time
print(f"Final amount: ${amount:.2f}")
```"""

    def _generate_general_response(self, content):
        return f"""Thank you for your question about: "{content[:100]}..."

I'm a mock LLM designed for learning LangChain concepts without API costs. In a real application, this would be replaced with ChatOpenAI() and provide much more sophisticated responses.

This demonstrates how LangChain chains work:
1. Your input → Prompt formatting
2. Prompt → LLM processing  
3. LLM response → Output parsing
4. Final result → Your application

To use real AI, simply replace FreeLLM() with ChatOpenAI() and add your API key!"""

# 2. FREE: Practice with Free LLM
def demo_free_langchain():
    """Demonstrate LangChain concepts without API costs"""
    
    print("🆓 Free LangChain Practice Session")
    print("=" * 50)
    
    # Create chain with free LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}")
    ])
    
    free_llm = FreeLLM()
    output_parser = StrOutputParser()
    
    # Create the chain
    chain = prompt | free_llm | output_parser
    
    # Test different types of requests
    test_inputs = [
        "Write a Python function for bubble sort",
        "Create a short story about time travel", 
        "Draft a business proposal for employee wellness",
        "Calculate compound interest on $1000 at 5% for 3 years"
    ]
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n📝 Test {i}: {test_input}")
        try:
            result = chain.invoke({"input": test_input})
            print(f"✅ Response:\n{result[:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        print("-" * 30)

# 3. FREE: Local LLM Options
def explain_free_alternatives():
    """Explain free alternatives to OpenAI API"""
    
    print("\n🆓 FREE Alternatives for Learning:")
    print("=" * 40)
    
    alternatives = {
        "Ollama (Local)": {
            "cost": "100% Free",
            "setup": "Download and run models locally",
            "models": "Llama 2, Mistral, CodeLlama",
            "pros": "No API costs, privacy, offline",
            "cons": "Requires good computer specs"
        },
        "Hugging Face Transformers": {
            "cost": "Free tier available", 
            "setup": "Use transformers library",
            "models": "Many open-source models",
            "pros": "Free tier, lots of models",
            "cons": "Rate limits on free tier"
        },
        "Google Colab": {
            "cost": "Free GPU access",
            "setup": "Run models in Colab notebooks", 
            "models": "Any open-source model",
            "pros": "Free GPU, no local setup",
            "cons": "Session limits"
        },
        "Mock LLMs (Learning)": {
            "cost": "100% Free",
            "setup": "Use pattern-based responses",
            "models": "Custom logic",
            "pros": "Perfect for learning concepts",
            "cons": "Not real AI responses"
        }
    }
    
    for name, details in alternatives.items():
        print(f"\n🔧 {name}")
        for key, value in details.items():
            print(f"   {key.title()}: {value}")

if __name__ == "__main__":
    demo_free_langchain()
    explain_free_alternatives()
    
    print("\n" + "=" * 50)
    print("💡 LEARNING STRATEGY:")
    print("1. Start with mock LLMs to learn LangChain concepts")
    print("2. Try Ollama for local free AI")
    print("3. Use OpenAI's free $5 credits for testing")
    print("4. Only pay for API when building real applications")
    print("\n🎯 Focus on learning the patterns, not the LLM provider!")
