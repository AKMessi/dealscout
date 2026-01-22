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

# Custom CSS for clean white background aesthetic
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }
    
    /* White theme overrides */
    .stApp {
        background-color: #ffffff;
        color: #1f2937;
    }
    
    /* Ensure all text is dark and readable */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #1f2937 !important;
    }
    
    /* Input styling */
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff;
        color: #1f2937;
        border: 1px solid #d1d5db;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
    }
    
    /* Disabled text areas (for display) */
    .stTextArea textarea[disabled], .stTextInput input[disabled] {
        background-color: #f9fafb;
        color: #1f2937;
        border: 1px solid #e5e7eb;
        opacity: 1;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
        color: #111827;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 500;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        color: #1f2937;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #f3f4f6;
    }
    
    .streamlit-expanderContent {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-top: none;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
    }
    
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #1f2937 !important;
    }
    
    /* Markdown text styling */
    .stMarkdown {
        color: #1f2937;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #1f2937;
    }
    
    /* Status styling */
    [data-testid="stStatus"] {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        color: #1f2937;
    }
    
    /* Final memo container */
    .final-memo-container {
        background-color: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        color: #1f2937;
    }
    
    .final-memo-container p, .final-memo-container div {
        color: #1f2937 !important;
        line-height: 1.6;
    }
    
    .memo-header-invest {
        color: #059669;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .memo-header-pass {
        color: #dc2626;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .memo-header-maybe {
        color: #d97706;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f9fafb;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #ffffff;
        color: #1f2937;
    }
    
    /* Info box styling */
    .stAlert {
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
    }
    
    /* Caption styling */
    .stCaption {
        color: #6b7280;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
                # Empty line might indicate message end, but we'll continue collecting
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
            # Extract message after colon
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
            # Save headers as system messages for context
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


# Sidebar for API key
with st.sidebar:
    st.title("⚙️ Configuration")
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
    st.markdown("### 📖 Instructions")
    st.markdown("""
    1. Enter the startup pitch deck text
    2. Click "Run Analysis" to start
    3. Review the multi-agent analysis
    4. Check the debate and final verdict
    """)


# Main UI
st.title("📊 DealScout VC Terminal")
st.markdown("**Multi-Agent Deal Analysis Platform**")
st.markdown("---")

# Input Section
with st.container():
    st.subheader("📝 Deal Input")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pitch_text = st.text_area(
            "Startup Pitch Deck",
            height=200,
            placeholder="Paste the startup pitch deck text here...\n\nExample:\nCompany: [Name]\nProduct: [Description]\nMarket: [Market info]\nTraction: [Metrics]\nTeam: [Team info]",
            help="Enter the full pitch deck text for analysis"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        st.caption("💡 Enter pitch deck text to analyze")
    
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
    st.header("📊 Analysis Dashboard")
    
    # Row 1: High-Level Metrics
    st.subheader("At a Glance")
    
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
            st.caption(f"TAM: {tam}")
        competitors = market_metrics.get("competitors", [])
        if competitors:
            st.caption(f"Competitors: {len(competitors)} identified")
    
    with col2:
        pmf = product_metrics.get("product_market_fit", "N/A")
        st.metric(
            "Product-Market Fit",
            str(pmf).title(),
            delta=None
        )
        feature_platform = product_metrics.get("is_feature_or_platform", "N/A")
        if feature_platform != "N/A":
            st.caption(f"Type: {str(feature_platform).title()}")
        tech_risk = product_metrics.get("technical_risk", "N/A")
        if tech_risk != "N/A" and tech_risk:
            st.caption(f"Risk: {str(tech_risk)[:50]}...")
    
    st.markdown("---")
    
    # Row 2: Agent Debate (Chat Interface)
    st.subheader("💬 Agent Debate")
    
    debate_messages = parse_debate_transcript(result.get('debate_transcript', ''))
    
    if debate_messages:
        # Create a container for the chat
        chat_container = st.container()
        with chat_container:
            for msg in debate_messages:
                # System messages (TOPIC, CONSENSUS) in center
                if msg["agent"] == "System":
                    st.info(f"{msg['avatar']} {msg['message']}")
                # Market Agent on left, others on right
                elif "Market" in msg["agent"]:
                    with st.chat_message("user", avatar=msg["avatar"]):
                        st.write(f"**{msg['agent']}**")
                        st.write(msg["message"])
                else:
                    with st.chat_message("assistant", avatar=msg["avatar"]):
                        st.write(f"**{msg['agent']}**")
                        st.write(msg["message"])
    else:
        # Fallback: display raw transcript
        st.info("📄 Debate transcript format not recognized. Displaying raw text:")
        st.text_area("Debate Transcript", result.get('debate_transcript', 'N/A'), height=200, disabled=True)
    
    st.markdown("---")
    
    # Row 3: Deep Dives (Expanders)
    st.subheader("🔍 Deep Dives")
    
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
    
    # Row 4: The Verdict (Final Memo)
    st.subheader("⚖️ Investment Verdict")
    
    final_memo = result.get('final_memo', '')
    color_class, verdict_text = get_verdict_color(final_memo)
    
    st.markdown(f'<div class="final-memo-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="{color_class}">{verdict_text}</div>', unsafe_allow_html=True)
    st.markdown(final_memo)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download Report Button
    st.markdown("---")
    report_text = generate_report_text(result)
    
    st.download_button(
        label="📥 Download Full Report",
        data=report_text,
        file_name=f"dealscout_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("DealScout VC Terminal • Multi-Agent Deal Analysis Platform")

