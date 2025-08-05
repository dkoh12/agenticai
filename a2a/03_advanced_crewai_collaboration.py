"""
REAL CrewAI A2A Communication Example
Using CrewAI framework with Ollama's Llama3.2

This is ACTUAL A2A communication with a real framework!
CrewAI is specifically designed for agent-to-agent collaboration.
"""

import os
from crewai import Agent, Task, Crew
from crewai.llm import LLM

def create_crewai_a2a_example():
    """Real A2A communication using CrewAI framework"""
    print("🤖 REAL CrewAI Agent-to-Agent Communication")
    print("=" * 50)
    print("Using ACTUAL CrewAI framework with Ollama!")
    print()
    
    # Configure Ollama for CrewAI
    ollama_llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )
    
    # Create researcher agent
    researcher = Agent(
        role="AI Research Specialist",
        goal="Research and provide accurate information about AI developments",
        backstory="""You are Dr. Smith, a seasoned AI researcher with 10 years of experience.
        You specialize in keeping up with the latest AI breakthroughs and can explain
        complex technical concepts clearly. You love collaborating with writers to
        make AI research accessible to everyone.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True  # This enables A2A communication!
    )
    
    # Create writer agent
    writer = Agent(
        role="Tech Content Writer",
        goal="Create engaging and accessible content about technology",
        backstory="""You are Alex, a skilled tech journalist with a talent for turning
        complex research into compelling stories. You work closely with researchers
        to ensure accuracy while making content engaging for general audiences.
        You're not afraid to ask follow-up questions to get the details right.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True  # This enables A2A communication!
    )
    
    # Create critic agent
    critic = Agent(
        role="Content Quality Reviewer",
        goal="Ensure content meets high standards for accuracy and engagement",
        backstory="""You are Jordan, an experienced editor with a keen eye for detail.
        You review content for clarity, accuracy, and reader engagement. You provide
        constructive feedback and work with teams to improve their content.
        You believe great content comes from collaboration.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True  # This enables A2A communication!
    )
    
    # Create research task
    research_task = Task(
        description="""Research the current state of AI technology, focusing on:
        1. Recent breakthroughs in large language models
        2. Real-world applications that are making an impact
        3. Key trends for 2025
        
        Provide detailed findings that a writer can use to create an engaging article.""",
        agent=researcher,
        expected_output="Comprehensive research summary with key findings and real-world examples"
    )
    
    # Create writing task
    writing_task = Task(
        description="""Using the research provided, write a compelling 200-word article about 
        the current state of AI technology. Make it engaging for a general audience while 
        maintaining technical accuracy. 
        
        If you need clarification on any research points, delegate questions back to the researcher.""",
        agent=writer,
        expected_output="Well-written 200-word article about AI technology",
        dependencies=[research_task]  # This creates collaboration workflow
    )
    
    # Create review task
    review_task = Task(
        description="""Review the article for:
        1. Clarity and readability
        2. Technical accuracy
        3. Engagement factor
        4. Overall quality
        
        Provide specific feedback and suggestions for improvement. 
        If major changes are needed, delegate back to the writer.""",
        agent=critic,
        expected_output="Detailed review with specific feedback and final approval",
        dependencies=[writing_task]  # This creates review workflow
    )
    
    # Create the crew (this enables A2A communication!)
    crew = Crew(
        agents=[researcher, writer, critic],
        tasks=[research_task, writing_task, review_task],
        verbose=True,
        process="sequential"  # Agents work together in sequence
    )
    
    print("🎬 Starting REAL CrewAI A2A collaboration...")
    print("Watch agents work together autonomously!\n")
    
    # Execute the crew workflow
    result = crew.kickoff()
    
    print("\n🎉 CrewAI A2A Communication Complete!")
    print("=" * 50)
    print("Final Result:")
    print(result)
    
    return result

def create_negotiation_crew():
    """CrewAI agents negotiating with each other"""
    print("\n🤝 CrewAI Agent Negotiation Example")
    print("=" * 50)
    
    # Configure Ollama
    ollama_llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )
    
    # Buyer agent
    buyer = Agent(
        role="Laptop Buyer",
        goal="Purchase a high-quality laptop within budget constraints",
        backstory="""You are Sam, a freelance developer looking for a new laptop.
        You have a strict budget of $1000 but need good performance for coding work.
        You're a skilled negotiator who researches before making purchases.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Seller agent
    seller = Agent(
        role="Laptop Sales Representative", 
        goal="Make successful sales while maintaining customer satisfaction",
        backstory="""You are Taylor, an experienced laptop sales rep who knows the value
        of building long-term customer relationships. You have flexibility in pricing
        and can offer additional perks to close deals. Your laptop normally sells for $1200.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Negotiation task
    negotiation_task = Task(
        description="""Conduct a negotiation between buyer and seller for a laptop purchase.
        
        Buyer: You want a laptop for development work, budget is $1000 maximum.
        Seller: Your laptop is worth $1200, but you can negotiate down to $950 minimum.
        
        Work together to reach a mutually acceptable deal. Use delegation to communicate
        offers, counteroffers, and find compromises. The negotiation should include
        discussion of price, warranty, and any additional perks.""",
        agent=buyer,  # Buyer initiates
        expected_output="Final negotiated deal with agreed price and terms"
    )
    
    # Create negotiation crew
    negotiation_crew = Crew(
        agents=[buyer, seller],
        tasks=[negotiation_task],
        verbose=True,
        process="sequential"
    )
    
    print("🎬 Starting CrewAI negotiation...")
    print("Watch agents negotiate autonomously!\n")
    
    result = negotiation_crew.kickoff()
    
    print(f"\n💼 Negotiation Result: {result}")
    return result

def test_crewai_connection():
    """Test CrewAI with Ollama"""
    print("🧪 Testing CrewAI with Ollama...")
    
    try:
        # Simple test
        ollama_llm = LLM(
            model="ollama/llama3.2",
            base_url="http://localhost:11434"
        )
        
        test_agent = Agent(
            role="Test Agent",
            goal="Confirm the system is working",
            backstory="You are a test agent designed to verify CrewAI is working properly.",
            llm=ollama_llm,
            verbose=True
        )
        
        test_task = Task(
            description="Say hello and confirm CrewAI is working with Ollama. Keep it brief.",
            agent=test_agent,
            expected_output="Brief confirmation message"
        )
        
        test_crew = Crew(
            agents=[test_agent],
            tasks=[test_task],
            verbose=True
        )
        
        result = test_crew.kickoff()
        print("✅ CrewAI connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error with CrewAI: {e}")
        return False

def main():
    """Run REAL CrewAI A2A examples"""
    print("🚀 REAL CrewAI Agent-to-Agent Communication")
    print("=" * 60)
    print("Using the ACTUAL CrewAI framework for A2A collaboration!")
    print("=" * 60)
    
    # Test connection
    if not test_crewai_connection():
        print("Please make sure Ollama is running with llama3.2")
        return
    
    try:
        # Example 1: Research collaboration
        create_crewai_a2a_example()
        
        # Example 2: Negotiation
        create_negotiation_crew()
        
        print("\n🎉 All REAL CrewAI A2A examples completed!")
        print("\nWhat just happened:")
        print("✅ Used ACTUAL CrewAI framework")
        print("✅ Agents collaborated through delegation")
        print("✅ True agent-to-agent communication")
        print("✅ Autonomous decision-making and collaboration")
        print("✅ Real AI (Ollama/Llama3.2) powering the interactions")
        
        print("\n🎯 Key A2A Features Demonstrated:")
        print("- allow_delegation=True enables agents to talk to each other")
        print("- Agents can ask follow-up questions")
        print("- Sequential and collaborative workflows")
        print("- Real negotiation and consensus building")
        print("- Autonomous agent decision-making")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running with llama3.2 model")

if __name__ == "__main__":
    main()
