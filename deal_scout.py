import os
from typing import TypedDict, Annotated
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, END

load_dotenv()

# llm setup
MODEL_NAME="gemini-3-flash-preview"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0.3,
    max_tokens=4000
)

# agent state definitions

class DealState(TypedDict):
    pitch_text: str
    market_analysis: str
    product_analysis: str
    debate_transcript: str
    final_memo: str

# agent definitions

def market_analyst_node(state: DealState):
    """
    Agent 1: Focuses solely on market size, timing and competition.
    """

    print("--- [1/4] market analyst working ---")

    prompt = f"""
        You are a cynical Market Analyst for a VC firm. 
        Analyze this startup pitch strictly on market dynamics:
        
        PITCH DATA:
        {state['pitch_text']}
        
        TASKS:
        1. Estimate TAM/SAM/SOM (guess if not provided).
        2. List 3 potential incumbent competitors.
        3. Give a "Market Timing Score" (1-10) with 1 sentence reasoning.
        
        Output valid JSON only.
    """

    response = llm.invoke(prompt)

    return {"market_analysis": response.content}

def product_analyst_node(state: DealState):
    """
    Agent 2: Focuses solely on product feasibility and differentiation.
    """

    print("--- [2/4] product analyst working ---")

    prompt = f"""
        You are a Product Analyst. Evaluate the feasibility of this startup:
        
        PITCH DATA:
        {state['pitch_text']}
            
        TASKS:
        1. Identify the core technical risk.
        2. Assess "Product-Market Fit" potential (Low/Medium/High).
        3. Is this a feature or a platform?
            
        Output valid JSON only.
    """

    response = llm.invoke(prompt)

    return {"product_analysis": response.content}

def synthesizer_node(state:DealState):
    """
    Agent 3 (The General Partner): Reads the report and makes a decision.
    """

    print("--- [3/4] synthesizer working ---")

    prompt = f"""
        You are a General Partner. Review the diligence reports and the team debate.
        
        STARTUP PITCH:
        {state['pitch_text']}
        
        MARKET REPORT:
        {state['market_analysis']}
        
        PRODUCT REPORT:
        {state['product_analysis']}
        
        >>> DEBATE TRANSCRIPT:
        {state['debate_transcript']}
        
        TASK:
        Write a 1-paragraph investment memo.
        1. Weigh the arguments from the debate.
        2. Decide which analyst makes the stronger case.
        3. Final Recommendation: [PASS] / [INVEST] / [DIG DEEPER].
    """

    response = llm.invoke(prompt)

    return {"final_memo": response.content}

def debate_node(state:DealState):
    """
    Agent 4 (The Moderator): Forces the analysts to debate.
    """

    print("--- [4/4] cross validation debate starting ---")

    prompt = f"""
        You are a Debate Moderator.
        
        MARKET ANALYST REPORT:
        {state['market_analysis']}
        
        PRODUCT ANALYST REPORT:
        {state['product_analysis']}
        
        TASK:
        Identify the biggest disagreement or tension between these two reports.
        Simulate a dialogue where the Market Analyst and Product Analyst argue their points.
        
        Format:
        Market Agent: [Argument]
        Product Agent: [Rebuttal]
        ...
        
        If they agree, have them reinforce each other's skepticism.
    """

    response = llm.invoke(prompt)

    return {"debate_transcript": response.content}

# graph construction

workflow = StateGraph(DealState)

workflow.add_node("market_agent", market_analyst_node)
workflow.add_node("product_agent", product_analyst_node)
workflow.add_node("debate_agent", debate_node)
workflow.add_node("synthesizer_agent", synthesizer_node)

workflow.set_entry_point("market_agent")
workflow.add_edge("market_agent", "product_agent")
workflow.add_edge("product_agent", "debate_agent")
workflow.add_edge("debate_agent", "synthesizer_agent")
workflow.add_edge("synthesizer_agent", END)

app = workflow.compile()

if __name__ == "__main__":
    
    dummy_pitch = """
    Startup Name: TeleportLuxe
    Concept: Instant teleportation for luxury goods (watches, handbags).
    Target: Ultra-high net worth individuals who hate shipping times.
    Tech: Quantum entanglement logistics (theoretical).
    Traction: 50,000 signups on waitlist.
    """
    
    print(f"Analyzing Pitch: {dummy_pitch[:50]}...")
    
    # initialize the state
    initial_state = DealState(
        pitch_text=dummy_pitch,
        market_analysis="",
        product_analysis=""
    )
    
    # run the graph
    result = app.invoke(initial_state)
    
    # print Results
    print("\n" + "="*40)
    print("FINAL MARKET REPORT")
    print("="*40)
    print(result['market_analysis'])
    
    print("\n" + "="*40)
    print("FINAL PRODUCT REPORT")
    print("="*40)
    print(result['product_analysis'])

    print("\n" + "="*40)
    print("FINAL INVESTMENT MEMO")
    print("="*40)
    print(result['final_memo'])
