"""
AutoGen Example: Advanced A2A Patterns
Using Ollama's Llama3.2 for complex agent interactions

This example shows:
- Agents with different personalities and expertise
- Dynamic role assignment
- Conflict resolution between agents
- Collaborative problem-solving workflows
- Agent memory and context sharing
"""

import os
from typing import Dict, List, Any

# Note: Install AutoGen with: pip install pyautogen
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
except ImportError:
    print("❌ AutoGen not installed. Install with: pip install pyautogen")
    exit(1)

# Ollama configuration for AutoGen
config_list = [
    {
        "model": "llama3.2",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "api_type": "openai"
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.2,
    "timeout": 60,
}

def software_development_team():
    """
    A software development team where agents have different roles
    and must collaborate to solve a complex problem
    """
    print("💻 Software Development Team A2A Example")
    print("=" * 50)
    
    # Product Manager - defines requirements
    product_manager = AssistantAgent(
        name="product_manager",
        system_message="""You are a Product Manager. Your responsibilities:
        - Define clear product requirements
        - Prioritize features based on user needs
        - Communicate business goals to the team
        - Make decisions on scope and timeline
        
        Be decisive but collaborative. Ask good questions.""",
        llm_config=llm_config,
    )
    
    # Senior Developer - technical leadership
    senior_dev = AssistantAgent(
        name="senior_dev",
        system_message="""You are a Senior Developer. Your responsibilities:
        - Propose technical solutions and architecture
        - Guide junior developers
        - Identify potential technical risks
        - Ensure code quality and best practices
        
        Be technically precise but explain things clearly.""",
        llm_config=llm_config,
    )
    
    # Frontend Developer - UI/UX focus
    frontend_dev = AssistantAgent(
        name="frontend_dev", 
        system_message="""You are a Frontend Developer. Your responsibilities:
        - Focus on user interface and user experience
        - Propose UI solutions and user workflows
        - Consider accessibility and responsiveness
        - Collaborate on API requirements
        
        Think from the user's perspective.""",
        llm_config=llm_config,
    )
    
    # QA Engineer - quality and testing
    qa_engineer = AssistantAgent(
        name="qa_engineer",
        system_message="""You are a QA Engineer. Your responsibilities:
        - Identify potential bugs and edge cases
        - Propose testing strategies
        - Ensure requirements are testable
        - Think about user scenarios
        
        Be thorough and consider what could go wrong.""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="client",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=15,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    # Create group chat
    groupchat = GroupChat(
        agents=[user_proxy, product_manager, senior_dev, frontend_dev, qa_engineer],
        messages=[],
        max_round=20,
    )
    
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    print("\n🎬 Software team collaboration starting...")
    print("Watch how different roles contribute to solving a problem!\n")
    
    user_proxy.initiate_chat(
        manager,
        message="""We need to build a task management app for remote teams.
        
        Product Manager: Define the core requirements
        Senior Dev: Propose the technical approach
        Frontend Dev: Design the user experience  
        QA Engineer: Identify testing needs and potential issues
        
        Collaborate to create a comprehensive plan. End with 'TERMINATE' when done."""
    )

def research_paper_collaboration():
    """
    Academic researchers collaborating on a paper
    Shows how agents can have different expertise and viewpoints
    """
    print("\n📚 Academic Research Collaboration Example")
    print("=" * 50)
    
    # Computer Science researcher
    cs_researcher = AssistantAgent(
        name="cs_researcher",
        system_message="""You are a Computer Science researcher specializing in AI/ML.
        - Focus on technical accuracy and algorithmic details
        - Cite relevant papers and methodologies
        - Propose rigorous experimental approaches
        - Be precise about technical terminology""",
        llm_config=llm_config,
    )
    
    # Psychology researcher  
    psych_researcher = AssistantAgent(
        name="psych_researcher",
        system_message="""You are a Psychology researcher studying human-AI interaction.
        - Focus on human factors and behavioral aspects
        - Consider ethical implications and bias
        - Propose user studies and qualitative research
        - Think about real-world human impact""",
        llm_config=llm_config,
    )
    
    # Statistics expert
    stats_expert = AssistantAgent(
        name="stats_expert",
        system_message="""You are a Statistics expert.
        - Ensure experimental design is statistically sound
        - Propose appropriate statistical tests and measures
        - Identify potential confounding variables
        - Focus on data validity and significance""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="editor",
        human_input_mode="NEVER", 
        max_consecutive_auto_reply=12,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    groupchat = GroupChat(
        agents=[user_proxy, cs_researcher, psych_researcher, stats_expert],
        messages=[],
        max_round=15,
    )
    
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    print("\n🎬 Research collaboration starting...")
    print("Different expertise areas working together!\n")
    
    user_proxy.initiate_chat(
        manager,
        message="""We're writing a research paper on "The Impact of AI Assistants on Human Productivity".
        
        CS Researcher: Propose technical methodology and AI metrics
        Psychology Researcher: Design human studies and consider behavioral factors
        Statistics Expert: Ensure rigorous experimental design and analysis
        
        Collaborate to create a research plan. End with 'TERMINATE' when done."""
    )

def debate_and_consensus():
    """
    Agents with opposing viewpoints reaching consensus
    Demonstrates conflict resolution and persuasion
    """
    print("\n🗣️ Agent Debate and Consensus Example")
    print("=" * 50)
    
    # Optimist agent
    optimist = AssistantAgent(
        name="optimist",
        system_message="""You are an optimistic technology advocate.
        - See the positive potential in new technologies
        - Focus on benefits and opportunities
        - Believe in human adaptability and progress
        - Propose solutions rather than dwelling on problems
        
        But be willing to listen and find middle ground.""",
        llm_config=llm_config,
    )
    
    # Pessimist agent
    pessimist = AssistantAgent(
        name="pessimist",
        system_message="""You are a cautious technology critic.
        - Focus on potential risks and unintended consequences
        - Consider long-term societal impacts
        - Advocate for careful regulation and oversight
        - Prioritize safety over speed of adoption
        
        But be open to reasonable compromises.""",
        llm_config=llm_config,
    )
    
    # Mediator agent
    mediator = AssistantAgent(
        name="mediator",
        system_message="""You are a neutral mediator.
        - Help both sides understand each other's perspectives
        - Identify common ground and shared values
        - Propose balanced solutions
        - Keep discussions productive and respectful
        
        Focus on finding win-win outcomes.""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="moderator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=15,
        is_termination_msg=lambda x: "consensus" in x.get("content", "").lower() or 
                                    x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    groupchat = GroupChat(
        agents=[user_proxy, optimist, pessimist, mediator],
        messages=[],
        max_round=18,
    )
    
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    print("\n🎬 Debate starting...")
    print("Watch agents with different viewpoints find common ground!\n")
    
    user_proxy.initiate_chat(
        manager,
        message="""Topic: "Should AI systems be given more autonomy in decision-making?"
        
        Optimist: Argue for the benefits of AI autonomy
        Pessimist: Argue for the risks and need for human oversight
        Mediator: Help both sides find a balanced consensus
        
        Debate respectfully and try to reach agreement. End with 'TERMINATE' when consensus is reached."""
    )

def creative_collaboration():
    """
    Creative agents working together on a project
    Shows how agents can build on each other's ideas
    """
    print("\n🎨 Creative Collaboration Example")
    print("=" * 50)
    
    # Story writer
    writer = AssistantAgent(
        name="writer",
        system_message="""You are a creative writer.
        - Create engaging narratives and characters
        - Focus on plot development and storytelling
        - Build on others' ideas creatively
        - Think about themes and emotional impact""",
        llm_config=llm_config,
    )
    
    # Visual artist
    artist = AssistantAgent(
        name="artist", 
        system_message="""You are a visual artist and designer.
        - Think about visual elements, colors, and composition
        - Describe scenes cinematically
        - Consider how visuals enhance the story
        - Propose artistic styles and moods""",
        llm_config=llm_config,
    )
    
    # Sound designer
    sound_designer = AssistantAgent(
        name="sound_designer",
        system_message="""You are a sound designer and composer.
        - Think about audio elements, music, and soundscapes
        - Consider how sound enhances emotion and atmosphere
        - Propose musical themes and sound effects
        - Think about rhythm and pacing""",
        llm_config=llm_config,
    )
    
    user_proxy = UserProxyAgent(
        name="director",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=12,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config=False,
    )
    
    groupchat = GroupChat(
        agents=[user_proxy, writer, artist, sound_designer],
        messages=[],
        max_round=15,
    )
    
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    print("\n🎬 Creative collaboration starting...")
    print("Watch creative agents build on each other's ideas!\n")
    
    user_proxy.initiate_chat(
        manager,
        message="""Create a concept for a short film about "A robot learning to appreciate art".
        
        Writer: Develop the story, characters, and narrative arc
        Artist: Describe the visual style, scenes, and cinematography  
        Sound Designer: Propose the musical score and sound design
        
        Build on each other's ideas to create a cohesive vision. End with 'TERMINATE' when done."""
    )

if __name__ == "__main__":
    print("🚀 Advanced AutoGen A2A Communication Patterns")
    print("=" * 60)
    print("Demonstrating complex agent interactions:")
    print("- Multi-role collaboration")
    print("- Conflict resolution")
    print("- Creative partnerships")
    print("- Professional teamwork")
    print("=" * 60)
    
    try:
        # Example 1: Software development team
        software_development_team()
        
        # Example 2: Academic research collaboration
        research_paper_collaboration()
        
        # Example 3: Debate and consensus building
        debate_and_consensus()
        
        # Example 4: Creative collaboration
        creative_collaboration()
        
        print("\n🎉 All advanced examples completed!")
        print("\nKey A2A Patterns Demonstrated:")
        print("✅ Role-based collaboration")
        print("✅ Expertise sharing between agents")
        print("✅ Conflict resolution and negotiation")
        print("✅ Creative idea building")
        print("✅ Consensus formation")
        print("✅ Dynamic group decision-making")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure AutoGen is installed: pip install pyautogen")
        print("And Ollama is running with llama3.2 model")
