"""
AutoGen Example: Basic Agent-to-Agent Communication
Using Ollama's Llama3.2 (local, free alternative to OpenAI)

Setup Instructions:
1. Install AutoGen: pip install pyautogen
2. Install Ollama: https://ollama.ai/download
3. Pull the model: ollama pull llama3.2
4. Start Ollama: ollama serve (or just run ollama)
5. Run this script!

This example shows:
- True agent-to-agent communication (not orchestrated workflows)
- Agents having conversations with each other
- Direct message passing between agents
- Collaborative problem solving

Key Difference from LangGraph:
- Agents TALK TO EACH OTHER directly
- No central orchestrator
- Conversational back-and-forth
- Autonomous decision-making about communication
"""

import os
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Configure Ollama for AutoGen
config_list = [
    {
        "model": "llama3.2",
        "base_url": "http://localhost:11434/v1",  # Ollama OpenAI-compatible endpoint
        "api_key": "ollama",  # Ollama doesn't need real API key
        "api_type": "openai"
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.1,
    "timeout": 60,
}

def basic_two_agent_conversation():
    """
    Two agents having a direct conversation
    This is TRUE A2A - agents talk directly to each other
    """
    print("🤖 Basic Two-Agent Conversation Example")
    print("=" * 50)
    
    # Create researcher agent
    researcher = AssistantAgent(
        name="researcher",
        system_message="""You are a research specialist. Your job is to:
        1. Research topics thoroughly
        2. Provide factual information
        3. Ask clarifying questions when needed
        4. Collaborate with writers to create content
        
        Keep responses concise but informative.""",
        llm_config=llm_config,
    )
    
    # Create writer agent  
    writer = AssistantAgent(
        name="writer",
        system_message="""You are a content writer. Your job is to:
        1. Take research and turn it into engaging content
        2. Ask researchers for specific information you need
        3. Create well-structured, readable content
        4. Collaborate to produce the best final product
        
        Keep responses concise but creative.""",
        llm_config=llm_config,
    )
    
    # Create user proxy (represents human user)
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",  # Fully automated
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,  # Disable code execution for this example
    )
    
    # Start the conversation
    print("\n🎬 Starting agent conversation...")
    print("Agents will now talk to each other directly!\n")
    
    user_proxy.initiate_chat(
        researcher,
        message="""I need help creating content about artificial intelligence. 
        Researcher, please gather key information about AI, then work with the writer 
        to create a brief article. When you're done, end with 'TERMINATE'."""
    )

def multi_agent_group_chat():
    """
    Multiple agents in a group chat - more complex A2A
    Agents decide who speaks next and collaborate dynamically
    """
    print("\n🤖 Multi-Agent Group Chat Example")
    print("=" * 50)
    
    # Create specialized agents
    researcher = AssistantAgent(
        name="researcher",
        system_message="""You are a research specialist. Focus on gathering facts and data.""",
        llm_config=llm_config,
    )
    
    writer = AssistantAgent(
        name="writer", 
        system_message="""You are a content writer. Turn research into engaging articles.""",
        llm_config=llm_config,
    )
    
    critic = AssistantAgent(
        name="critic",
        system_message="""You are a content critic. Review and suggest improvements to written content.""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    # Create group chat
    groupchat = GroupChat(
        agents=[user_proxy, researcher, writer, critic],
        messages=[],
        max_round=12,
    )
    
    # Create group chat manager
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    print("\n🎬 Starting multi-agent group chat...")
    print("Watch agents collaborate and decide who speaks next!\n")
    
    # Start group conversation
    user_proxy.initiate_chat(
        manager,
        message="""Create a short article about machine learning. 
        Researcher: gather information
        Writer: create the article  
        Critic: review and suggest improvements
        Collaborate until you have a good final product. End with 'TERMINATE'."""
    )

def negotiation_example():
    """
    Agents negotiating with each other - true A2A interaction
    Shows how agents can have opposing views and negotiate
    """
    print("\n🤖 Agent Negotiation Example")
    print("=" * 50)
    
    # Buyer agent
    buyer = AssistantAgent(
        name="buyer",
        system_message="""You are a buyer trying to get the best price for a laptop.
        - Your budget is $1000 maximum
        - You want good performance for the price
        - Negotiate firmly but respectfully
        - Try to get additional perks (warranty, accessories)""",
        llm_config=llm_config,
    )
    
    # Seller agent
    seller = AssistantAgent(
        name="seller", 
        system_message="""You are a laptop seller trying to make a good sale.
        - Your laptop normally costs $1200
        - Your minimum acceptable price is $950
        - You can offer some perks to close the deal
        - Be persuasive but fair""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="moderator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=8,
        is_termination_msg=lambda x: "deal" in x.get("content", "").lower() or 
                                    "no deal" in x.get("content", "").lower() or
                                    x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    print("\n🎬 Starting negotiation between buyer and seller...")
    print("Watch agents negotiate directly with each other!\n")
    
    user_proxy.initiate_chat(
        buyer,
        message="""You want to buy a laptop. Start negotiating with the seller.
        Try to reach a mutually acceptable deal. When you reach agreement or decide
        no deal is possible, end with 'TERMINATE'."""
    )

def test_ollama_connection():
    """Test if Ollama is working with AutoGen"""
    print("🧪 Testing Ollama Connection with AutoGen...")
    
    try:
        test_agent = AssistantAgent(
            name="test_agent",
            system_message="You are a test agent. Respond briefly.",
            llm_config=llm_config,
        )
        
        user_proxy = UserProxyAgent(
            name="user",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config=False,
        )
        
        user_proxy.initiate_chat(
            test_agent,
            message="Say hello and confirm you're working. Keep it brief."
        )
        
        print("✅ Ollama connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        print("Please make sure:")
        print("1. Ollama is installed and running")
        print("2. Llama3.2 model is downloaded: ollama pull llama3.2") 
        print("3. Ollama is serving on http://localhost:11434")
        return False

if __name__ == "__main__":
    print("🚀 AutoGen Agent-to-Agent Communication Examples")
    print("=" * 60)
    print("This demonstrates TRUE A2A communication where agents")
    print("talk directly to each other (unlike LangGraph workflows)")
    print("=" * 60)
    
    # Test connection first
    if not test_ollama_connection():
        exit(1)
    
    # Run examples
    try:
        # Example 1: Basic two-agent conversation
        basic_two_agent_conversation()
        
        # Example 2: Multi-agent group chat
        multi_agent_group_chat()
        
        # Example 3: Negotiation between agents
        negotiation_example()
        
        print("\n🎉 All examples completed!")
        print("\nKey Takeaways:")
        print("- Agents communicated DIRECTLY with each other")
        print("- No central orchestrator needed")
        print("- Agents made autonomous decisions about communication")
        print("- True collaborative and competitive interactions")
        print("\nThis is fundamentally different from LangGraph's orchestrated workflows!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure AutoGen is installed: pip install pyautogen")
