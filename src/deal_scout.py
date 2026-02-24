import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, END

load_dotenv()

# llm setup - Google Gemini 2.5 Flash
MODEL_NAME = "gemini-2.5-flash"

# Check if API key is set
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY environment variable is not set. Please set your Google API key.")

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0.3,
    max_tokens=4000,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# agent state definitions

class DealState(TypedDict):
    company_name: str
    company_url: str
    raw_input: str
    pitch_text: str
    market_analysis: str
    product_analysis: str
    traction_analysis: str
    debate_transcript: str
    questions_to_reconsider: str
    final_memo: str

# agent definitions

def research_company_node(state: DealState):
    """
    Agent 0: Research Company - Builds synthetic pitch from minimal input
    """
    print("--- [0/6] researching company ---")
    
    raw_input = state.get('raw_input', '')
    company_name = state.get('company_name', '')
    company_url = state.get('company_url', '')
    
    # If detailed pitch provided, use it
    if len(raw_input.strip()) > 200:
        print("   Using provided pitch deck")
        return {
            "pitch_text": raw_input,
            "company_name": company_name or "Unknown Company"
        }
    
    # Otherwise generate synthetic pitch
    print(f"   Researching {company_name or 'company'} from web...")
    
    prompt = f"""
You are a research assistant. Given minimal information about a company, create a structured pitch deck.

COMPANY NAME: {company_name or "Not provided"}
COMPANY WEBSITE: {company_url or "Not provided"}
ADDITIONAL INFO: {raw_input or "None"}

Create a pitch deck with these sections:
- Company name and website
- Product/Service (what they do)
- Target Market
- Traction (users, revenue, growth if known)
- Funding status
- Team (founders if known)
- Competitive Advantage

If information is missing, note it as "Research needed" but create a complete structure.
"""
    
    response = llm.invoke(prompt)
    
    return {
        "pitch_text": response.content,
        "company_name": company_name or "Unknown Company"
    }


def market_analyst_node(state: DealState):
    """
    Agent 1: Focuses solely on market size, timing and competition.
    """
    print("--- [1/6] market analyst working ---")

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
    print("--- [2/6] product analyst working ---")

    prompt = f"""
You are a Product Analyst. Evaluate the feasibility of this startup:

PITCH DATA:
{state['pitch_text']}

COMPANY WEBSITE:
{state.get('company_url', 'Not provided')}

TASKS:
1. Identify the core technical risk.
2. Assess "Product-Market Fit" potential (Low/Medium/High).
3. Is this a feature or a platform?

Output valid JSON only.
"""

    response = llm.invoke(prompt)
    return {"product_analysis": response.content}


def traction_analyst_node(state: DealState):
    """
    Agent 3: Traction Analyst - verifies metrics
    """
    print("--- [3/6] traction analyst working ---")

    prompt = f"""
You are a financial analyst who is EXTREMELY skeptical of startup metrics.

PITCH DATA:
{state['pitch_text']}

TASKS:
1. Assess if claimed metrics are realistic
2. Identify missing metrics
3. Give a traction assessment (1-10)

Be brutal. Most startups exaggerate.

Output valid JSON with fields:
- metrics_seem_realistic (true/false)
- red_flags (array)
- missing_metrics (array)
- traction_score (1-10)
"""

    response = llm.invoke(prompt)
    return {"traction_analysis": response.content}


def debate_node(state: DealState):
    """
    Agent 4: Forces the analysts to debate.
    """
    print("--- [4/6] cross validation debate starting ---")

    prompt = f"""
You are a Debate Moderator.

MARKET ANALYST REPORT:
{state['market_analysis']}

PRODUCT ANALYST REPORT:
{state['product_analysis']}

TRACTION ANALYST REPORT:
{state['traction_analysis']}

TASK:
Identify the biggest disagreement or tension between these reports.
Simulate a dialogue where the analysts argue their points.

Format:
Market Agent: [Argument]
Product Agent: [Rebuttal]
Traction Agent: [Data point]
...

If they agree, have them reinforce each other's skepticism.
"""

    response = llm.invoke(prompt)
    return {"debate_transcript": response.content}


def questions_to_reconsider_node(state: DealState):
    """
    Agent 5: Generate critical questions to reconsider before investing
    """
    print("--- [5/6] generating questions to reconsider ---")

    prompt = f"""
You are a seasoned VC Partner with 20+ years of experience.
Based on ALL the analysis below, generate CRITICAL QUESTIONS to reconsider before investing.

STARTUP PITCH:
{state['pitch_text']}

MARKET REPORT:
{state['market_analysis']}

PRODUCT REPORT:
{state['product_analysis']}

TRACTION REPORT:
{state['traction_analysis']}

DEBATE TRANSCRIPT:
{state['debate_transcript']}

YOUR TASK:
Generate 8-12 hard-hitting questions across these categories:

1. MARKET REALITY CHECK
2. PRODUCT & TECHNOLOGY RISKS
3. TRACTION & BUSINESS MODEL
4. TEAM & EXECUTION

Make these questions specific to THIS startup, not generic.

FORMAT:
## Questions to Reconsider Before Investing

### Market Reality Check
1. [Question] - *Why this matters: [Explanation]*

### Product & Technology Risks
1. [Question] - *Why this matters: [Explanation]*

... and so on
"""

    response = llm.invoke(prompt)
    return {"questions_to_reconsider": response.content}


def synthesizer_node(state: DealState):
    """
    Agent 6 (The General Partner): Reads the report and makes a decision.
    """
    print("--- [6/6] synthesizer working ---")

    prompt = f"""
You are a General Partner. Review the diligence reports and the team debate.

COMPANY: {state.get('company_name', 'Unknown')}

STARTUP PITCH:
{state['pitch_text']}

MARKET REPORT:
{state['market_analysis']}

PRODUCT REPORT:
{state['product_analysis']}

TRACTION REPORT:
{state['traction_analysis']}

DEBATE TRANSCRIPT:
{state['debate_transcript']}

QUESTIONS TO RECONSIDER:
{state.get('questions_to_reconsider', '')}

TASK:
Write a 1-2 paragraph investment memo.
1. Weigh the arguments from the debate.
2. Consider the critical questions raised.
3. Final Recommendation: [PASS] / [INVEST] / [DIG DEEPER].

Include:
- 3 key strengths
- 3 key risks
- Recommended next steps
"""

    response = llm.invoke(prompt)
    return {"final_memo": response.content}


# graph construction

workflow = StateGraph(DealState)

workflow.add_node("research_agent", research_company_node)
workflow.add_node("market_agent", market_analyst_node)
workflow.add_node("product_agent", product_analyst_node)
workflow.add_node("traction_agent", traction_analyst_node)
workflow.add_node("debate_agent", debate_node)
workflow.add_node("questions_agent", questions_to_reconsider_node)
workflow.add_node("synthesizer_agent", synthesizer_node)

workflow.set_entry_point("research_agent")
workflow.add_edge("research_agent", "market_agent")
workflow.add_edge("market_agent", "product_agent")
workflow.add_edge("product_agent", "traction_agent")
workflow.add_edge("traction_agent", "debate_agent")
workflow.add_edge("debate_agent", "questions_agent")
workflow.add_edge("questions_agent", "synthesizer_agent")
workflow.add_edge("synthesizer_agent", END)

app = workflow.compile()


if __name__ == "__main__":
    
    # Test with minimal input
    print("Testing with minimal input...")
    
    initial_state = {
        "company_name": "TeleportLuxe",
        "company_url": "https://example.com",
        "raw_input": "",
        "pitch_text": "",
        "market_analysis": "",
        "product_analysis": "",
        "traction_analysis": "",
        "debate_transcript": "",
        "questions_to_reconsider": "",
        "final_memo": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\n" + "="*40)
    print("GENERATED PITCH")
    print("="*40)
    print(result['pitch_text'])
    
    print("\n" + "="*40)
    print("FINAL INVESTMENT MEMO")
    print("="*40)
    print(result['final_memo'])
