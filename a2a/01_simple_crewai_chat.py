"""
Simple CrewAI A2A Example
Showing basic agent-to-agent communication
"""

from crewai import Agent, Task, Crew
from crewai.llm import LLM

def simple_crewai_chat():
    """Two agents having a conversation"""
    print("💬 Simple CrewAI Agent Chat")
    print("=" * 30)
    
    # Ollama LLM configuration
    ollama_llm = LLM(
        model="ollama/llama3.2",
        base_url="http://localhost:11434"
    )
    
    # Agent 1: Curious student
    student = Agent(
        role="Curious Student",
        goal="Learn about AI by asking questions",
        backstory="You are an eager computer science student who loves learning about AI.",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True, # this enables A2A communication
        max_retry=1 # retry up to 1 times if task fails
    )
    
    # Agent 2: Teacher
    teacher = Agent(
        role="AI Teacher", 
        goal="Explain AI concepts clearly and encourage questions",
        backstory="You are a patient AI instructor who enjoys teaching students.",
        llm=ollama_llm,
        verbose=True,
        allow_delegation=True,
        max_retry=1 # retry up to 1 time if task fails
    )
    
    # Conversation task
    chat_task = Task(
        description="""Have a brief educational conversation about machine learning.
        
        Student: Ask a specific question about how neural networks learn.
        Teacher: Answer clearly and ask if the student has follow-up questions.
        
        Keep the conversation natural and educational.""",
        agent=student,
        expected_output="Educational conversation about neural networks"
    )
    
    # Create crew
    chat_crew = Crew(
        agents=[student, teacher],
        tasks=[chat_task],
        verbose=True
    )
    
    print("🎬 Starting agent conversation...\n")
    result = chat_crew.kickoff()
    
    print(f"\n📝 Conversation Result:\n{result}")
    return result

if __name__ == "__main__":
    simple_crewai_chat()
