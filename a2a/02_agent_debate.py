"""
CrewAI Agent Debate Example
Real agents arguing and reaching consensus
"""

from crewai import Agent, Task, Crew
from crewai.llm import LLM

def agent_debate_example():
    """Two agents having a debate and reaching consensus"""
    print("🔥 CrewAI Agent Debate Example")
    print("=" * 40)
    
    # Ollama LLM configuration
    ollama_llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )
    
    # Agent 1: Pro-Remote Work
    remote_advocate = Agent(
        role="Remote Work Advocate",
        goal="Argue for the benefits of remote work arrangements",
        backstory="""You are Sarah, a tech worker who has thrived in remote work.
        You believe remote work increases productivity, improves work-life balance,
        and opens up global talent pools. You have data to support your arguments.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Agent 2: Pro-Office Work  
    office_advocate = Agent(
        role="Office Work Advocate",
        goal="Argue for the benefits of in-person office work",
        backstory="""You are Mike, a manager who values face-to-face collaboration.
        You believe office work improves communication, builds stronger teams,
        and enables better mentorship. You've seen productivity issues with remote work.""",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Debate task
    debate_task = Task(
        description="""Conduct a civilized debate about remote work vs office work.
        
        Remote Work Advocate: Present 3 strong arguments for remote work.
        Office Work Advocate: Counter with 3 arguments for office work.
        
        Then work together to find common ground and reach a compromise solution
        that both sides can accept. Use delegation to exchange arguments and
        build toward consensus.
        
        Keep arguments professional and fact-based.""",
        agent=remote_advocate,  # Remote advocate starts
        expected_output="A compromise solution both sides agree on"
    )
    
    # Create debate crew
    debate_crew = Crew(
        agents=[remote_advocate, office_advocate],
        tasks=[debate_task],
        verbose=True
    )
    
    print("🥊 Starting agent debate...\n")
    result = debate_crew.kickoff()
    
    print(f"\n🤝 Debate Resolution:\n{result}")
    return result

if __name__ == "__main__":
    agent_debate_example()
