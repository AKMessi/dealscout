import os
import json
from typing import TypedDict, List
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.tools import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper

from langgraph.graph import StateGraph, END

import PyPDF2
import requests
from bs4 import BeautifulSoup

load_dotenv()

# llm setup

MODEL_NAME = "gemini-3-flash-preview"

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    temperature=0.3,
    max_tokens=4000
)


# tools setup

# tool 1: google search
search = GoogleSerperAPIWrapper() if os.getenv("SERPER_API_KEY") else None

def google_search_tool(query: str = None, **kwargs) -> str:
    """Search Google for current information"""
    
    if query is None and kwargs:
        query = kwargs.get('query') or kwargs.get('__arg1')
    
    if not query:
        return "Error: No search query provided"
    
    if not search:
        return "Google Search not configured. Set SERPER_API_KEY in .env"
    try:
        results = search.results(query)
        
        output = []
        for i, result in enumerate(results.get('organic', [])[:3], 1):
            output.append(f"{i}. {result.get('title', 'No title')}\n   {result.get('snippet', 'No snippet')}\n   {result.get('link', '')}")
        return "\n\n".join(output) if output else "No results found"
    except Exception as e:
        return f"Search error: {str(e)}"

# tool 2: web scraper
def scrape_website_tool(url: str = None, **kwargs) -> str:
    """Scrape and extract text from a website"""
    
    if url is None and kwargs:
        url = kwargs.get('url') or kwargs.get('__arg1')
    
    if not url:
        return "Error: No URL provided"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        
        text = soup.get_text()
        
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        
        return text[:3000] + "..." if len(text) > 3000 else text
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

# tool 3: pdf parser
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# creating langchain tools

tools = [
    Tool(
        name="GoogleSearch",
        func=google_search_tool,
        description="Search Google for current information about companies, markets, competitors, or news. Input should be a search query string."
    ),
    Tool(
        name="WebScraper",
        func=scrape_website_tool,
        description="Scrape and read the content of a website. Input should be a valid URL starting with http:// or https://"
    )
]

# agent state definition

class DealState(TypedDict):
    pitch_text: str
    company_url: str
    market_analysis: str
    product_analysis: str
    traction_analysis: str
    debate_transcript: str
    final_memo: str

# agent nodes with tools

def market_analyst_node(state: DealState):
    """
    Agent 1: Market Analyst with Google Search capability
    """
    print("\n[1/5] Market Analyst researching...")
    
    
    system_prompt = """You are a skeptical Market Analyst for a VC firm.

        You have access to these tools:
        - GoogleSearch: Search for current market data, competitors, news
        - WebScraper: Read website content

        IMPORTANT: 
        - Don't trust pitch deck numbers - verify them with searches
        - Search for recent news about this market
        - Look for failed companies in this space
    """

    user_prompt = f"""
        STARTUP PITCH:
        {state['pitch_text']}

        YOUR TASKS:
        1. Search for the market size and growth rate
        2. Search for top 3-5 competitors in this space
        3. Assess market timing (why now?)
        4. Calculate realistic TAM/SAM/SOM

        Think step by step:
        - What searches do you need to run?
        - Run them and analyze the results
        - Synthesize into final analysis

        Output your analysis as JSON with these fields:
        - tam_estimate
        - competitors (array)
        - market_timing_score (1-10)
        - timing_reason
        - red_flags (array)
    """


    llm_with_tools = llm.bind_tools(tools)
    
    try:
        
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            
            tool_results = []
            for tool_call in response.tool_calls[:3]:
                tool_name = tool_call['name']
                tool_input = tool_call['args']
                
                
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.func(**tool_input)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                        break
            
            
            final_response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
                HumanMessage(content=f"Tool results:\n" + "\n\n".join(tool_results) + "\n\nNow provide your final analysis as JSON.")
            ])
            
            return {"market_analysis": final_response.content}
        else:
            
            return {"market_analysis": response.content}
            
    except Exception as e:
        return {"market_analysis": f"Error: {str(e)}"}


def product_analyst_node(state: DealState):
    """
    Agent 2: Product Analyst with Web Scraping capability
    """
    print("\n[2/5] Product Analyst analyzing website...")
    
    system_prompt = """
        You are a Product Analyst evaluating a startup's product.

        You have access to:
        - GoogleSearch: Search for product reviews, tech stack info
        - WebScraper: Visit and analyze their website
    """

    user_prompt = f"""
        STARTUP PITCH:
        {state['pitch_text']}

        COMPANY WEBSITE:
        {state.get('company_url', 'Not provided')}

        YOUR TASKS:
        1. If website is provided, scrape it and analyze the product
        2. Search for reviews or mentions of the product
        3. Assess technical feasibility
        4. Identify unique differentiation vs competitors
        5. Determine: Is this a feature or a platform?

        Output as JSON with fields:
        - product_quality_score (1-10)
        - is_live (true/false)
        - tech_stack
        - differentiation
        - is_feature_or_platform
        - technical_risks (array)
        - website_quality_score (1-10)
    """

    llm_with_tools = llm.bind_tools(tools)
    
    try:
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls[:3]:
                tool_name = tool_call['name']
                tool_input = tool_call['args']
                
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.func(**tool_input)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                        break
            
            final_response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
                HumanMessage(content=f"Tool results:\n" + "\n\n".join(tool_results) + "\n\nNow provide your final analysis as JSON.")
            ])
            
            return {"product_analysis": final_response.content}
        else:
            return {"product_analysis": response.content}
            
    except Exception as e:
        return {"product_analysis": f"Error: {str(e)}"}


def traction_analyst_node(state: DealState):
    """
    Agent 3: Traction Analyst - verifies metrics and searches for validation
    """
    print("\n[3/5] Traction Analyst fact-checking metrics...")
    
    system_prompt = """
        You are a financial analyst who is EXTREMELY skeptical of startup metrics.
    """

    user_prompt = f"""
        STARTUP PITCH:
        {state['pitch_text']}

        YOUR TASKS:
        1. Search for any public information about their traction (Crunchbase, news, etc.)
        2. Verify if claimed metrics are realistic
        3. Calculate unit economics if data is available
        4. Search for red flags (layoffs, pivots, failed raises)

        Be brutal. Most startups exaggerate.

        Output as JSON with fields:
        - metrics_seem_realistic (true/false)
        - red_flags (array)
        - missing_metrics (array)
        - validation_found
        - traction_score (1-10)
    """

    llm_with_tools = llm.bind_tools(tools)
    
    try:
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls[:3]:
                tool_name = tool_call['name']
                tool_input = tool_call['args']
                
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.func(**tool_input)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                        break
            
            final_response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
                HumanMessage(content=f"Tool results:\n" + "\n\n".join(tool_results) + "\n\nNow provide your final analysis as JSON.")
            ])
            
            return {"traction_analysis": final_response.content}
        else:
            return {"traction_analysis": response.content}
            
    except Exception as e:
        return {"traction_analysis": f"Error: {str(e)}"}


def debate_node(state: DealState):
    """
    Agent 4: Multi-turn debate between analysts
    """
    print("\n[4/5] Debate starting...")
    
    prompt = f"""
        Analyze these three reports for contradictions or tensions:

        MARKET: {state['market_analysis']}
        PRODUCT: {state['product_analysis']}
        TRACTION: {state['traction_analysis']}

        Identify the BIGGEST disagreement or concern. Then simulate a 3-turn debate:

        Format:
        TOPIC: [one sentence topic]

        Turn 1:
        Market Agent: [argument]
        Product Agent: [counter]

        Turn 2:
        Market Agent: [response]
        Traction Agent: [interjects with data]

        Turn 3:
        Product Agent: [final point]
        Market Agent: [conclusion]

        CONSENSUS: [what they agree on, if anything]
    """
    
    response = llm.invoke(prompt)
    return {"debate_transcript": response.content}


def synthesizer_node(state: DealState):
    """
    Agent 5: GP who reads everything and makes final call
    """
    print("\n[5/5] GP writing final memo...")
    
    prompt = f"""
        You are a General Partner making an investment decision.

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

        Write a 2-3 paragraph investment memo that:
        1. Synthesizes the key insights
        2. Weighs the debate arguments
        3. Makes a clear recommendation: [PASS] / [MAYBE - DIG DEEPER] / [STRONG YES]

        Include:
        - 3 key strengths
        - 3 key risks
        - Recommended next steps

        Be direct and data-driven.
    """
    
    response = llm.invoke(prompt)
    return {"final_memo": response.content}


# graph construction

workflow = StateGraph(DealState)

workflow.add_node("market_agent", market_analyst_node)
workflow.add_node("product_agent", product_analyst_node)
workflow.add_node("traction_agent", traction_analyst_node)
workflow.add_node("debate_agent", debate_node)
workflow.add_node("synthesizer_agent", synthesizer_node)

workflow.set_entry_point("market_agent")
workflow.add_edge("market_agent", "product_agent")
workflow.add_edge("product_agent", "traction_agent")
workflow.add_edge("traction_agent", "debate_agent")
workflow.add_edge("debate_agent", "synthesizer_agent")
workflow.add_edge("synthesizer_agent", END)

app = workflow.compile()

# main execution

if __name__ == "__main__":
    
    test_pitch = """
        Company: Anthropic
        Product: Claude AI - advanced large language model
        Market: Enterprise AI/LLM market, competing with OpenAI, Google
        Traction: 
        - Used by Fortune 500 companies
        - Constitutional AI approach for safety
        - Multiple model tiers (Opus, Sonnet, Haiku)
        Team: 
        - Founded by former OpenAI researchers
        - Dario Amodei (CEO) - ex-OpenAI VP of Research
        Funding: Raised $7B+ from Google, Spark Capital, others
        Website: https://www.anthropic.com
    """
    
    print("="*60)
    print("DEALSCOUT ANALYSIS STARTING")
    print("="*60)
    
    initial_state = {
        "pitch_text": test_pitch,
        "company_url": "https://www.anthropic.com",
        "market_analysis": "",
        "product_analysis": "",
        "traction_analysis": "",
        "debate_transcript": "",
        "final_memo": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print("FINAL ANALYSIS REPORT")
    print("="*60)
    
    print("\n" + "-"*60)
    print("MARKET ANALYSIS")
    print("-"*60)
    print(result['market_analysis'])
    
    print("\n" + "-"*60)
    print("PRODUCT ANALYSIS")
    print("-"*60)
    print(result['product_analysis'])
    
    print("\n" + "-"*60)
    print("TRACTION ANALYSIS")
    print("-"*60)
    print(result['traction_analysis'])
    
    print("\n" + "-"*60)
    print("AGENT DEBATE")
    print("-"*60)
    print(result['debate_transcript'])
    
    print("\n" + "="*60)
    print("INVESTMENT RECOMMENDATION")
    print("="*60)
    print(result['final_memo'])
    print("\n")