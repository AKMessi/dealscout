import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, Optional, Any
import os

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agent import app as workflow

# Page config
st.set_page_config(
    page_title="DealScout VC Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# World-class CSS design system
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main container - premium spacing */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1600px;
    }
    
    /* App background - pristine white */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
        color: #0f172a;
    }
    
    /* Premium typography */
    h1 {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #0f172a !important;
        margin-bottom: 0.5rem !important;
        line-height: 1.1 !important;
    }
    
    h2 {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
        color: #1e293b !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #334155 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Premium input styling */
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
        outline: none !important;
    }
    
    .stTextArea textarea:hover, .stTextInput input:hover {
        border-color: #cbd5e1 !important;
    }
    
    /* Disabled inputs */
    .stTextArea textarea[disabled], .stTextInput input[disabled] {
        background-color: #f8fafc !important;
        color: #64748b !important;
        border-color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    /* Premium metric cards */
    [data-testid="stMetricContainer"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    [data-testid="stMetricContainer"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 2px 4px rgba(0, 0, 0, 0.06) !important;
        border-color: #cbd5e1 !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: #64748b !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-top: 8px !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    /* Premium expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 16px 20px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06) !important;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 20px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Premium chat messages */
    .stChatMessage {
        padding: 20px 24px !important;
        margin: 12px 0 !important;
        border-radius: 16px !important;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1.5px solid #e2e8f0 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    
    .stChatMessage:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-1px) !important;
    }
    
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #1e293b !important;
        line-height: 1.6 !important;
    }
    
    /* Premium status indicator */
    [data-testid="stStatus"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        color: #1e293b !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Premium final memo container */
    .final-memo-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 20px !important;
        padding: 32px 40px !important;
        margin: 2rem 0 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.04) !important;
        color: #1e293b !important;
        transition: all 0.3s ease !important;
    }
    
    .final-memo-container:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08), 0 4px 8px rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-2px) !important;
    }
    
    .final-memo-container p, .final-memo-container div {
        color: #1e293b !important;
        line-height: 1.75 !important;
        font-size: 15px !important;
    }
    
    .memo-header-invest {
        color: #059669 !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.01em !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    .memo-header-pass {
        color: #dc2626 !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.01em !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    .memo-header-maybe {
        color: #d97706 !important;
        font-size: 1.75rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.01em !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    /* Premium button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2), 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.01em !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3), 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Premium sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
        border-right: 1.5px solid #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1e293b !important;
    }
    
    /* Premium info boxes */
    .stAlert {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
        border: 1.5px solid #93c5fd !important;
        border-radius: 12px !important;
        color: #1e40af !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Premium caption */
    .stCaption {
        color: #64748b !important;
        font-size: 0.8125rem !important;
        font-weight: 500 !important;
        margin-top: 8px !important;
    }
    
    /* Premium dividers */
    hr {
        border: none !important;
        border-top: 1.5px solid #e2e8f0 !important;
        margin: 2.5rem 0 !important;
    }
    
    /* Premium markdown */
    .stMarkdown {
        color: #1e293b !important;
        line-height: 1.7 !important;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #1e293b !important;
    }
    
    .stMarkdown strong {
        font-weight: 600 !important;
        color: #0f172a !important;
    }
    
    /* Premium JSON display */
    .stJson {
        background: #f8fafc !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Premium download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Premium error styling */
    .stAlert[data-baseweb="notification"] {
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06) !important;
    }
    
    /* Smooth scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Premium spacing utilities */
    .premium-spacing {
        margin: 2rem 0;
    }
    
    /* Custom metric badge */
    .metric-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #0369a1;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)


def clean_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Robust JSON parser that handles markdown-wrapped JSON and malformed JSON.
    Returns None if parsing fails completely.
    """
    if not text or not isinstance(text, str):
        return None
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try to find JSON object in the text
    # Look for { ... } pattern
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
    else:
        json_str = text
    
    # Try parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to fix common issues
        # Remove trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Last resort: try to extract key-value pairs manually
            return None


def extract_metrics(analysis_text: str, analysis_type: str) -> Dict[str, Any]:
    """
    Extract key metrics from analysis text.
    Returns a dict with extracted values or defaults.
    """
    parsed = clean_json(analysis_text)
    metrics = {}
    
    if parsed:
        if analysis_type == "market":
            metrics["tam_estimate"] = parsed.get("tam_estimate", parsed.get("TAM", "N/A"))
            metrics["market_timing_score"] = parsed.get("market_timing_score", parsed.get("Market Timing Score", 0))
            metrics["competitors"] = parsed.get("competitors", parsed.get("incumbent_competitors", []))
        elif analysis_type == "product":
            metrics["product_market_fit"] = parsed.get("product_market_fit", parsed.get("Product-Market Fit", "N/A"))
            metrics["is_feature_or_platform"] = parsed.get("is_feature_or_platform", parsed.get("feature_or_platform", "N/A"))
            metrics["technical_risk"] = parsed.get("technical_risk", parsed.get("core_technical_risk", "N/A"))
    
    return metrics


def parse_debate_transcript(transcript: str) -> list:
    """
    Parse debate transcript into structured messages for chat display.
    Returns list of dicts with 'agent', 'message', 'avatar' keys.
    """
    if not transcript:
        return []
    
    messages = []
    lines = transcript.split('\n')
    current_agent = None
    current_message = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_agent and current_message:
                continue
            continue
        
        # Check for agent labels (case-insensitive, handle variations)
        line_lower = line.lower()
        if "market agent" in line_lower and ":" in line:
            if current_agent and current_message:
                messages.append({
                    "agent": current_agent,
                    "message": " ".join(current_message),
                    "avatar": "📈" if "Market" in current_agent else "🛡️"
                })
            current_agent = "Market Agent"
            parts = line.split(":", 1)
            current_message = [parts[1].strip()] if len(parts) > 1 else []
        elif "product agent" in line_lower and ":" in line:
            if current_agent and current_message:
                messages.append({
                    "agent": current_agent,
                    "message": " ".join(current_message),
                    "avatar": "📈" if "Market" in current_agent else "🛡️"
                })
            current_agent = "Product Agent"
            parts = line.split(":", 1)
            current_message = [parts[1].strip()] if len(parts) > 1 else []
        elif line.startswith("TOPIC:") or line.startswith("CONSENSUS:") or line.lower().startswith("turn"):
            if line.startswith("TOPIC:") or line.startswith("CONSENSUS:"):
                messages.append({
                    "agent": "System",
                    "message": line,
                    "avatar": "📌" if "TOPIC" in line else "🤝"
                })
            continue
        elif current_agent:
            current_message.append(line)
    
    # Add last message
    if current_agent and current_message:
        messages.append({
            "agent": current_agent,
            "message": " ".join(current_message),
            "avatar": "📈" if "Market" in current_agent else "🛡️"
        })
    
    return messages


def get_verdict_color(memo: str) -> tuple:
    """
    Determine verdict color based on memo content.
    Returns (color_class, verdict_text)
    """
    memo_upper = memo.upper()
    if "[INVEST]" in memo_upper:
        return ("memo-header-invest", "✅ INVEST")
    elif "[PASS]" in memo_upper:
        return ("memo-header-pass", "❌ PASS")
    elif "[DIG DEEPER]" in memo_upper:
        return ("memo-header-maybe", "⚠️ DIG DEEPER")
    else:
        return ("memo-header-maybe", "📋 VERDICT")


def generate_report_text(state: Dict[str, str]) -> str:
    """
    Generate a formatted text report from the full state.
    """
    report = f"""
{'='*80}
DEALSCOUT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

STARTUP PITCH:
{state.get('pitch_text', 'N/A')}

{'='*80}
MARKET ANALYSIS
{'='*80}
{state.get('market_analysis', 'N/A')}

{'='*80}
PRODUCT ANALYSIS
{'='*80}
{state.get('product_analysis', 'N/A')}

{'='*80}
AGENT DEBATE
{'='*80}
{state.get('debate_transcript', 'N/A')}

{'='*80}
INVESTMENT RECOMMENDATION
{'='*80}
{state.get('final_memo', 'N/A')}

{'='*80}
END OF REPORT
{'='*80}
"""
    return report


# Premium Sidebar
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1 style='font-size: 1.75rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;'>⚙️ Settings</h1>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Configure your API keys</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        value=os.getenv("SERPER_API_KEY", ""),
        help="Enter your Serper API key for Google Search functionality"
    )
    
    if serper_key:
        os.environ["SERPER_API_KEY"] = serper_key
    
    st.markdown("---")
    
    st.markdown("""
    <div style='margin-top: 2rem;'>
        <h3 style='font-size: 1.125rem; font-weight: 600; color: #1e293b; margin-bottom: 1rem;'>📖 Quick Guide</h3>
        <div style='color: #64748b; font-size: 0.875rem; line-height: 1.6;'>
            <p style='margin: 0.75rem 0;'>1. Enter the startup pitch deck text</p>
            <p style='margin: 0.75rem 0;'>2. Click "Run Analysis" to start</p>
            <p style='margin: 0.75rem 0;'>3. Review the multi-agent analysis</p>
            <p style='margin: 0.75rem 0;'>4. Check the debate and final verdict</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Premium Main UI
st.markdown("""
    <div style='margin-bottom: 1rem;'>
        <h1 style='margin-bottom: 0.5rem;'>📊 DealScout VC Terminal</h1>
        <p style='font-size: 1.125rem; color: #64748b; font-weight: 500; margin: 0;'>Multi-Agent Deal Analysis Platform</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Premium Input Section
with st.container():
    st.markdown("""
    <div style='margin-bottom: 1.5rem;'>
        <h2 style='margin-bottom: 0.5rem;'>📝 Deal Input</h2>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Enter the startup pitch deck for comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    pitch_text = st.text_area(
        "Startup Pitch Deck",
        height=220,
        placeholder="Paste the startup pitch deck text here...\n\nExample:\nCompany: [Name]\nProduct: [Description]\nMarket: [Market info]\nTraction: [Metrics]\nTeam: [Team info]",
        help="Enter the full pitch deck text for analysis",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        run_analysis = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

# Initialize session state
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# Run analysis
if run_analysis:
    if not pitch_text:
        st.error("⚠️ Please enter a pitch deck text to analyze.")
    else:
        initial_state = {
            "pitch_text": pitch_text,
            "market_analysis": "",
            "product_analysis": "",
            "debate_transcript": "",
            "final_memo": ""
        }
        
        # Execute workflow with status updates
        with st.status("🔄 Running multi-agent analysis...", expanded=True) as status:
            try:
                status.update(
                    label="🔄 Running analysis pipeline: Market → Product → Debate → Synthesis...",
                    state="running"
                )
                result = workflow.invoke(initial_state)
                
                status.update(label="✅ Analysis complete!", state="complete")
                
                st.session_state.analysis_result = result
                st.session_state.analysis_complete = True
                st.rerun()
                
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")
                st.error(f"Analysis failed: {str(e)}")

# Display results if analysis is complete
if st.session_state.analysis_complete and st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    st.markdown("---")
    
    st.markdown("""
    <div style='margin-bottom: 1.5rem;'>
        <h2 style='margin-bottom: 0.5rem;'>📊 Analysis Dashboard</h2>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Key metrics and insights at a glance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Premium Metrics Display
    market_metrics = extract_metrics(result.get('market_analysis', ''), "market")
    product_metrics = extract_metrics(result.get('product_analysis', ''), "product")
    
    col1, col2 = st.columns(2)
    
    with col1:
        timing_score = market_metrics.get("market_timing_score", 0)
        if isinstance(timing_score, (int, float)) and timing_score > 0:
            st.metric(
                "Market Timing Score",
                f"{timing_score}/10",
                delta=None if timing_score == 0 else f"{timing_score - 5}"
            )
        else:
            st.metric("Market Timing Score", "N/A")
        tam = market_metrics.get("tam_estimate", "N/A")
        if tam != "N/A":
            st.caption(f"📊 TAM: {tam}")
        competitors = market_metrics.get("competitors", [])
        if competitors:
            st.caption(f"🏢 Competitors: {len(competitors)} identified")
    
    with col2:
        pmf = product_metrics.get("product_market_fit", "N/A")
        st.metric(
            "Product-Market Fit",
            str(pmf).title(),
            delta=None
        )
        feature_platform = product_metrics.get("is_feature_or_platform", "N/A")
        if feature_platform != "N/A":
            st.caption(f"🔧 Type: {str(feature_platform).title()}")
        tech_risk = product_metrics.get("technical_risk", "N/A")
        if tech_risk != "N/A" and tech_risk:
            st.caption(f"⚠️ Risk: {str(tech_risk)[:50]}...")
    
    st.markdown("---")
    
    # Premium Debate Section
    st.markdown("""
    <div style='margin-bottom: 1.5rem;'>
        <h2 style='margin-bottom: 0.5rem;'>💬 Agent Debate</h2>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Real-time discussion between Market and Product analysts</p>
    </div>
    """, unsafe_allow_html=True)
    
    debate_messages = parse_debate_transcript(result.get('debate_transcript', ''))
    
    if debate_messages:
        chat_container = st.container()
        with chat_container:
            for msg in debate_messages:
                if msg["agent"] == "System":
                    st.info(f"{msg['avatar']} {msg['message']}")
                elif "Market" in msg["agent"]:
                    with st.chat_message("user", avatar=msg["avatar"]):
                        st.write(f"**{msg['agent']}**")
                        st.write(msg["message"])
                else:
                    with st.chat_message("assistant", avatar=msg["avatar"]):
                        st.write(f"**{msg['agent']}**")
                        st.write(msg["message"])
    else:
        st.info("📄 Debate transcript format not recognized. Displaying raw text:")
        st.text_area("Debate Transcript", result.get('debate_transcript', 'N/A'), height=200, disabled=True, label_visibility="collapsed")
    
    st.markdown("---")
    
    # Premium Deep Dives
    st.markdown("""
    <div style='margin-bottom: 1.5rem;'>
        <h2 style='margin-bottom: 0.5rem;'>🔍 Deep Dives</h2>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Detailed analysis reports from each agent</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📈 Market Analysis", expanded=False):
            market_parsed = clean_json(result.get('market_analysis', ''))
            if market_parsed:
                st.json(market_parsed)
            else:
                st.text(result.get('market_analysis', 'N/A'))
    
    with col2:
        with st.expander("🛡️ Product Analysis", expanded=False):
            product_parsed = clean_json(result.get('product_analysis', ''))
            if product_parsed:
                st.json(product_parsed)
            else:
                st.text(result.get('product_analysis', 'N/A'))
    
    st.markdown("---")
    
    # Premium Final Verdict
    st.markdown("""
    <div style='margin-bottom: 1.5rem;'>
        <h2 style='margin-bottom: 0.5rem;'>⚖️ Investment Verdict</h2>
        <p style='color: #64748b; font-size: 0.875rem; margin: 0;'>Final recommendation from the General Partner</p>
    </div>
    """, unsafe_allow_html=True)
    
    final_memo = result.get('final_memo', '')
    color_class, verdict_text = get_verdict_color(final_memo)
    
    st.markdown(f'<div class="final-memo-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="{color_class}">{verdict_text}</div>', unsafe_allow_html=True)
    st.markdown(final_memo)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Premium Download Button
    st.markdown("---")
    report_text = generate_report_text(result)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Full Report",
            data=report_text,
            file_name=f"dealscout_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# Premium Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #64748b; font-size: 0.875rem;'>
        <p style='margin: 0; font-weight: 500;'>DealScout VC Terminal</p>
        <p style='margin: 0.5rem 0 0 0;'>Multi-Agent Deal Analysis Platform</p>
    </div>
""", unsafe_allow_html=True)
