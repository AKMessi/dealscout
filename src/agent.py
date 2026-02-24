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
        for i, result in enumerate(results.get('organic', [])[:5], 1):
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
    
    # Ensure URL starts with http
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        # Try to get meta description
        meta_desc = ""
        meta = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta:
            meta_desc = meta.get("content", "")
        
        # Get title
        title = soup.find("title")
        title_text = title.get_text().strip() if title else ""
        
        # Get main content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Combine title, meta description, and content
        result = ""
        if title_text:
            result += f"Title: {title_text}\n\n"
        if meta_desc:
            result += f"Description: {meta_desc}\n\n"
        result += f"Content:\n{text[:5000]}"
        
        return result if len(result) > 100 else f"Title: {title_text}\n\nContent:\n{text[:3000]}"
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
    company_name: str
    company_url: str
    raw_input: str  # Original user input (could be pitch deck or minimal info)
    pitch_text: str  # Generated or provided pitch text
    market_analysis: str
    product_analysis: str
    traction_analysis: str
    debate_transcript: str
    final_memo: str
    questions_to_reconsider: str

# agent nodes with tools

def research_company_node(state: DealState):
    """
    Agent 0: Research Company - Gathers information when minimal input is provided
    This agent runs first to build a synthetic pitch deck from web research
    """
    print("\n[0/7] Researching company information...")
    
    # Check if we already have a detailed pitch or just minimal info
    raw_input = state.get('raw_input', '')
    company_name = state.get('company_name', '')
    company_url = state.get('company_url', '')
    
    # If user provided detailed pitch (more than 200 chars), use it directly
    if len(raw_input.strip()) > 200:
        print("   Using provided pitch deck (detailed input detected)")
        return {
            "pitch_text": raw_input,
            "company_name": company_name or extract_company_name(raw_input)
        }
    
    # Otherwise, we need to research
    print(f"   Minimal input detected. Researching {company_name or 'company'}...")
    
    search_queries = []
    if company_name:
        search_queries.append(f"{company_name} startup company funding news")
        search_queries.append(f"{company_name} product features pricing")
    if company_url:
        # Extract domain for search
        domain = company_url.replace('https://', '').replace('http://', '').split('/')[0]
        if not company_name:
            search_queries.append(f"{domain} startup company")
    
    system_prompt = """You are a Company Research Specialist. Your job is to gather comprehensive information about a startup from web sources and compile it into a structured pitch deck format.

You have access to:
- GoogleSearch: Search for company information, funding news, competitors
- WebScraper: Extract detailed information from the company's website

Be thorough and extract as much relevant information as possible."""

    user_prompt = f"""
COMPANY NAME: {company_name or "Not provided"}
COMPANY WEBSITE: {company_url or "Not provided"}
USER INPUT: {raw_input or "None"}

YOUR TASK:
1. Scrape the company website if provided to understand what they do
2. Search for recent news about the company (funding, product launches, etc.)
3. Search for information about their market and competitors
4. Compile all findings into a PITCH DECK FORMAT

OUTPUT FORMAT - Create a comprehensive pitch deck with these sections:

---
Company: [Name]
Website: [URL]

Product/Service:
[Detailed description of what the company does, their core offering, key features]

Target Market:
[Who are their customers, market size if available]

Traction:
[Any metrics, user numbers, revenue info, growth rates found]

Funding:
[Funding rounds, investors, total raised if available]

Team:
[Founder names, backgrounds if available]

Competitive Advantage:
[What makes them unique vs competitors]

---

If certain information is not available, note it as "Not found in research" but still provide a complete structure.
"""

    llm_with_tools = llm.bind_tools(tools)
    
    try:
        response = llm_with_tools.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_results = []
            for tool_call in response.tool_calls[:5]:
                tool_name = tool_call['name']
                tool_input = tool_call['args']
                
                for tool in tools:
                    if tool.name == tool_name:
                        result = tool.func(**tool_input)
                        tool_results.append(f"=== {tool_name} RESULT ===\n{result}")
                        break
            
            final_response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
                HumanMessage(content=f"Research results:\n\n" + "\n\n".join(tool_results) + "\n\nNow compile all findings into the structured pitch deck format.")
            ])
            
            generated_pitch = final_response.content
        else:
            generated_pitch = response.content
        
        # Extract company name if not provided
        extracted_name = company_name
        if not extracted_name and "Company:" in generated_pitch:
            for line in generated_pitch.split('\n'):
                if line.strip().startswith('Company:'):
                    extracted_name = line.split(':', 1)[1].strip()
                    break
        
        print(f"   Research complete. Generated pitch for: {extracted_name or 'Unknown Company'}")
        return {
            "pitch_text": generated_pitch,
            "company_name": extracted_name or company_name or "Unknown Company"
        }
            
    except Exception as e:
        print(f"   Research error: {e}")
        # Fall back to raw input if research fails
        return {
            "pitch_text": raw_input or f"Company: {company_name}\nWebsite: {company_url}\n(Auto-research failed, please provide more details)",
            "company_name": company_name or "Unknown Company"
        }


def extract_company_name(text: str) -> str:
    """Extract company name from text"""
    lines = text.split('\n')
    for line in lines[:10]:
        if 'company:' in line.lower() or 'startup:' in line.lower():
            return line.split(':', 1)[1].strip()
    return "Unknown Company"


def market_analyst_node(state: DealState):
    """
    Agent 1: Market Analyst with Google Search capability
    """
    print("\n[1/7] Market Analyst researching...")
    
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
    print("\n[2/7] Product Analyst analyzing website...")
    
    system_prompt = """You are a Product Analyst evaluating a startup's product.

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
    print("\n[3/7] Traction Analyst fact-checking metrics...")
    
    system_prompt = """You are a financial analyst who is EXTREMELY skeptical of startup metrics.
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
    print("\n[4/7] Debate starting...")
    
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


def questions_to_reconsider_node(state: DealState):
    """
    Agent 5: Generate critical questions to reconsider before investing
    """
    print("\n[5/7] Generating questions to reconsider...")
    
    prompt = f"""
You are a seasoned VC Partner with 20+ years of experience. You've seen many investments succeed and fail.
Based on ALL the analysis below, generate a list of CRITICAL QUESTIONS that an investor should reconsider/think deeply about before making an investment decision.

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

1. MARKET REALITY CHECK (2-3 questions)
   - Questions about market size validation, timing risks, competitive threats

2. PRODUCT & TECHNOLOGY RISKS (2-3 questions)  
   - Questions about technical feasibility, defensibility, scalability

3. TRACTION & BUSINESS MODEL (2-3 questions)
   - Questions about revenue sustainability, unit economics, growth assumptions

4. TEAM & EXECUTION (2-3 questions)
   - Questions about founder capabilities, past track record, team gaps

FORMAT YOUR RESPONSE AS:

## 🎯 Questions to Reconsider Before Investing

### 📊 Market Reality Check
1. [Question]
   *Why this matters: [Brief explanation of the risk]*

2. [Question]
   *Why this matters: [Brief explanation]*

### 🛠️ Product & Technology Risks
1. [Question]
   *Why this matters: [Brief explanation]*

...and so on for each category.

Make these questions specific to THIS startup, not generic. They should dig into the gaps, contradictions, or blind spots revealed in the analysis.
"""
    
    response = llm.invoke(prompt)
    return {"questions_to_reconsider": response.content}


def synthesizer_node(state: DealState):
    """
    Agent 6: GP who reads everything and makes final call
    """
    print("\n[6/7] GP writing final memo...")
    
    prompt = f"""
You are a General Partner making an investment decision.

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

# main execution

if __name__ == "__main__":
    
    # Test with MINIMAL INPUT - just company name and URL
    print("="*60)
    print("TESTING WITH MINIMAL INPUT (Company Name + URL Only)")
    print("="*60)
    
    initial_state = {
        "company_name": "Anthropic",
        "company_url": "https://www.anthropic.com",
        "raw_input": "",  # Empty - simulating minimal input
        "pitch_text": "",
        "market_analysis": "",
        "product_analysis": "",
        "traction_analysis": "",
        "debate_transcript": "",
        "questions_to_reconsider": "",
        "final_memo": ""
    }
    
    result = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print("FINAL ANALYSIS REPORT")
    print("="*60)
    
    print("\n" + "-"*60)
    print("GENERATED PITCH (from minimal input)")
    print("-"*60)
    print(result['pitch_text'][:1500] + "..." if len(result['pitch_text']) > 1500 else result['pitch_text'])
    
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
    
    print("\n" + "-"*60)
    print("QUESTIONS TO RECONSIDER")
    print("-"*60)
    print(result.get('questions_to_reconsider', 'N/A'))
    
    print("\n" + "="*60)
    print("INVESTMENT RECOMMENDATION")
    print("="*60)
    print(result['final_memo'])
    print("\n")
