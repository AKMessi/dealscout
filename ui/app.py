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

try:
    from agent import app as workflow
except ImportError as e:
    st.error(f"Failed to import agent module: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="DealScout VC Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Test element to ensure content renders
try:
    st.write("")  # Empty write to ensure Streamlit is working
except:
    pass

# GOD-TIER CSS Design System
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Main content wrapper */
    .main {
        position: relative;
        z-index: 1;
    }
    
    /* Ensure all Streamlit elements are visible */
    .main > div,
    .main > div > div {
        position: relative;
        z-index: 1;
    }
    
    /* Main container - ultimate spacing */
    .main .block-container {
        padding-top: 4rem;
        padding-bottom: 4rem;
        padding-left: 4rem;
        padding-right: 4rem;
        max-width: 1600px;
    }
    
    /* App background - pristine white with subtle animation */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #fafbfc 50%, #ffffff 100%);
        color: #0f172a;
        position: relative;
        z-index: 0;
    }
    
    /* Ensure content is visible */
    .stApp > div {
        position: relative;
        z-index: 1;
    }
    
    /* Ultimate typography system */
    h1 {
        font-size: 3rem !important;
        font-weight: 900 !important;
        letter-spacing: -0.03em !important;
        color: #0f172a !important;
        margin-bottom: 0.75rem !important;
        line-height: 1.1 !important;
        animation: fadeInUp 0.6s ease-out;
        position: relative;
        z-index: 1;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #1e293b !important;
        margin-top: 3rem !important;
        margin-bottom: 1.75rem !important;
        animation: fadeInUp 0.7s ease-out;
    }
    
    h3 {
        font-size: 1.625rem !important;
        font-weight: 700 !important;
        color: #334155 !important;
        margin-top: 2.5rem !important;
        margin-bottom: 1.25rem !important;
    }
    
    /* Keyframe animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Ultimate input styling with glassmorphism */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        color: #0f172a !important;
        border: 2px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 16px !important;
        padding: 18px 20px !important;
        font-size: 15px !important;
        font-weight: 400 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.06) !important;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 6px rgba(59, 130, 246, 0.12), 0 4px 12px rgba(59, 130, 246, 0.15), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    .stTextArea textarea:hover, .stTextInput input:hover {
        border-color: #cbd5e1 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Disabled inputs */
    .stTextArea textarea[disabled], .stTextInput input[disabled] {
        background: rgba(248, 250, 252, 0.9) !important;
        color: #64748b !important;
        border-color: #e2e8f0 !important;
        opacity: 1 !important;
    }
    
    /* Ultimate metric cards with circular progress */
    [data-testid="stMetricContainer"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-radius: 24px !important;
        padding: 32px !important;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 8px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out;
    }
    
    [data-testid="stMetricContainer"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
        transition: left 0.5s;
    }
    
    [data-testid="stMetricContainer"]:hover::before {
        left: 100%;
    }
    
    [data-testid="stMetricContainer"]:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 
            0 12px 32px rgba(0, 0, 0, 0.1),
            0 4px 16px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.03em !important;
        line-height: 1.1 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem !important;
        color: #64748b !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-top: 12px !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 700 !important;
        font-size: 0.9375rem !important;
    }
    
    /* Circular progress indicator */
    .circular-progress {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(#3b82f6 0deg, #e2e8f0 0deg);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 20px auto;
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
    }
    
    .circular-progress::before {
        content: '';
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: white;
        position: absolute;
    }
    
    .progress-value {
        position: relative;
        z-index: 1;
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    /* Ultimate expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-radius: 16px !important;
        color: #1e293b !important;
        font-weight: 700 !important;
        font-size: 1.0625rem !important;
        padding: 20px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 1) 0%, rgba(248, 250, 252, 1) 100%) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-2px) !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.98) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-top: none !important;
        border-radius: 0 0 16px 16px !important;
        padding: 28px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
    }
    
    /* Ultimate chat messages */
    .stChatMessage {
        padding: 24px 28px !important;
        margin: 16px 0 !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 8px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: slideIn 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .stChatMessage::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #3b82f6 0%, #10b981 100%);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .stChatMessage:hover::before {
        opacity: 1;
    }
    
    .stChatMessage:hover {
        box-shadow: 
            0 8px 24px rgba(0, 0, 0, 0.1),
            0 4px 12px rgba(0, 0, 0, 0.08) !important;
        transform: translateY(-2px) translateX(4px) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
    }
    
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #1e293b !important;
        line-height: 1.7 !important;
    }
    
    /* Ultimate status indicator */
    [data-testid="stStatus"] {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-radius: 20px !important;
        padding: 32px !important;
        color: #1e293b !important;
        box-shadow: 
            0 4px 16px rgba(0, 0, 0, 0.06),
            0 2px 8px rgba(0, 0, 0, 0.04) !important;
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Ultimate final memo container */
    .final-memo-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%) !important;
        backdrop-filter: blur(30px) !important;
        border: 3px solid rgba(226, 232, 240, 0.8) !important;
        border-radius: 28px !important;
        padding: 48px 56px !important;
        margin: 3rem 0 !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.08),
            0 4px 16px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        color: #1e293b !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 1s ease-out;
    }
    
    .final-memo-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.05) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    .final-memo-container:hover {
        box-shadow: 
            0 16px 48px rgba(0, 0, 0, 0.12),
            0 8px 24px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 1) !important;
        transform: translateY(-4px) scale(1.01) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
    }
    
    .final-memo-container p, .final-memo-container div {
        color: #1e293b !important;
        line-height: 1.8 !important;
        font-size: 16px !important;
        position: relative;
        z-index: 1;
    }
    
    .memo-header-invest {
        color: #059669 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin-bottom: 2rem !important;
        letter-spacing: -0.02em !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(5, 150, 105, 0.2);
    }
    
    .memo-header-pass {
        color: #dc2626 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin-bottom: 2rem !important;
        letter-spacing: -0.02em !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(220, 38, 38, 0.2);
    }
    
    .memo-header-maybe {
        color: #d97706 !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        margin-bottom: 2rem !important;
        letter-spacing: -0.02em !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 8px rgba(217, 119, 6, 0.2);
    }
    
    /* Ultimate button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 18px 36px !important;
        border-radius: 14px !important;
        box-shadow: 
            0 4px 12px rgba(59, 130, 246, 0.3),
            0 2px 6px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.02em !important;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%) !important;
        box-shadow: 
            0 8px 20px rgba(59, 130, 246, 0.4),
            0 4px 10px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        transform: translateY(-2px) scale(1.02) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Ultimate sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 2px solid rgba(226, 232, 240, 0.6) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        color: #0f172a !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #1e293b !important;
    }
    
    /* Ultimate info boxes */
    .stAlert {
        background: linear-gradient(135deg, rgba(239, 246, 255, 0.95) 0%, rgba(219, 234, 254, 0.95) 100%) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(147, 197, 253, 0.6) !important;
        border-radius: 16px !important;
        color: #1e40af !important;
        padding: 20px 24px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1) !important;
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* Ultimate caption */
    .stCaption {
        color: #64748b !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        margin-top: 12px !important;
        letter-spacing: 0.01em !important;
        visibility: visible !important;
        opacity: 1 !important;
        display: block !important;
        line-height: 1.5 !important;
    }
    
    /* Ensure caption text is visible */
    [data-testid="stCaption"] {
        color: #64748b !important;
        visibility: visible !important;
        opacity: 1 !important;
        display: block !important;
    }
    
    [data-testid="stCaption"] > * {
        color: #64748b !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Ultimate dividers */
    hr {
        border: none !important;
        border-top: 2px solid rgba(226, 232, 240, 0.8) !important;
        margin: 3.5rem 0 !important;
        position: relative;
    }
    
    hr::after {
        content: '';
        position: absolute;
        top: -1px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    }
    
    /* Ultimate markdown */
    .stMarkdown {
        color: #1e293b !important;
        line-height: 1.8 !important;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #1e293b !important;
    }
    
    .stMarkdown strong {
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    
    /* Ultimate JSON display */
    .stJson {
        background: rgba(248, 250, 252, 0.9) !important;
        backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(226, 232, 240, 0.6) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Ensure pre-formatted text is visible */
    pre {
        color: #1e293b !important;
        background: #f8fafc !important;
        padding: 20px !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        overflow-x: auto !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Ensure expander content is visible */
    .streamlit-expanderContent pre,
    .streamlit-expanderContent code,
    .streamlit-expanderContent .stJson {
        visibility: visible !important;
        opacity: 1 !important;
        color: #1e293b !important;
    }
    
    /* Ultimate download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        box-shadow: 
            0 4px 12px rgba(16, 185, 129, 0.3),
            0 2px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative;
        overflow: hidden;
    }
    
    .stDownloadButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
        transition: left 0.5s;
    }
    
    .stDownloadButton > button:hover::before {
        left: 100%;
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 50%, #065f46 100%) !important;
        box-shadow: 
            0 8px 20px rgba(16, 185, 129, 0.4),
            0 4px 10px rgba(0, 0, 0, 0.15) !important;
        transform: translateY(-2px) scale(1.02) !important;
    }
    
    /* Ultimate error styling */
    .stAlert[data-baseweb="notification"] {
        border-radius: 16px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Smooth scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force visibility of all content */
    [data-testid="stAppViewContainer"] {
        position: relative !important;
        z-index: 1 !important;
    }
    
    [data-testid="stAppViewContainer"] > div {
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Ensure all Streamlit elements are visible */
    .element-container,
    .stMarkdown,
    .stTextArea,
    .stTextInput,
    .stButton {
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Critical: Ensure main content is always visible */
    .main .block-container {
        visibility: visible !important;
        opacity: 1 !important;
        display: block !important;
    }
    
    /* Ensure text is always visible */
    p, h1, h2, h3, h4, h5, h6, span, div, label {
        color: inherit !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Loading skeleton */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 12px;
        height: 20px;
        margin: 10px 0;
    }
    
    /* Badge component */
    .premium-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
        border: 1.5px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #0369a1;
        margin-top: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
    }
    
    /* Progress bar */
    .progress-bar-container {
        width: 100%;
        height: 8px;
        background: rgba(226, 232, 240, 0.5);
        border-radius: 10px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
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
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
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


# Ultimate Sidebar
with st.sidebar:
    st.markdown("""
    <div style='margin-bottom: 2.5rem; animation: fadeInUp 0.6s ease-out;'>
        <h1 style='font-size: 2rem; font-weight: 900; color: #0f172a; margin-bottom: 0.75rem; letter-spacing: -0.02em;'>⚙️ Settings</h1>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Configure your API keys</p>
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
    <div style='margin-top: 2.5rem; animation: fadeInUp 0.8s ease-out;'>
        <h3 style='font-size: 1.25rem; font-weight: 700; color: #1e293b; margin-bottom: 1.25rem; letter-spacing: -0.01em;'>📖 Quick Guide</h3>
        <div style='color: #64748b; font-size: 0.9375rem; line-height: 1.8; font-weight: 500;'>
            <p style='margin: 1rem 0; padding-left: 8px; border-left: 3px solid #3b82f6;'>1. Enter the startup pitch deck text</p>
            <p style='margin: 1rem 0; padding-left: 8px; border-left: 3px solid #10b981;'>2. Click "Run Analysis" to start</p>
            <p style='margin: 1rem 0; padding-left: 8px; border-left: 3px solid #8b5cf6;'>3. Review the multi-agent analysis</p>
            <p style='margin: 1rem 0; padding-left: 8px; border-left: 3px solid #f59e0b;'>4. Check the debate and final verdict</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Ultimate Main UI
st.markdown("""
    <div style='margin-bottom: 1.5rem; animation: fadeInUp 0.6s ease-out;'>
        <h1 style='margin-bottom: 0.75rem;'>📊 DealScout VC Terminal</h1>
        <p style='font-size: 1.25rem; color: #64748b; font-weight: 600; margin: 0; letter-spacing: -0.01em;'>Multi-Agent Deal Analysis Platform</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Ultimate Input Section
with st.container():
    st.markdown("""
    <div style='margin-bottom: 2rem; animation: fadeInUp 0.7s ease-out;'>
        <h2 style='margin-bottom: 0.75rem;'>📝 Deal Input</h2>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Enter the startup pitch deck for comprehensive analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    pitch_text = st.text_area(
        "Startup Pitch Deck",
        height=240,
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
    <div style='margin-bottom: 2rem; animation: fadeInUp 0.8s ease-out;'>
        <h2 style='margin-bottom: 0.75rem;'>📊 Analysis Dashboard</h2>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Key metrics and insights at a glance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ultimate Metrics Display
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
        if tam != "N/A" and tam:
            # Use markdown for better visibility
            st.markdown(f"""
            <div style='margin-top: 12px; padding: 8px 12px; background: rgba(248, 250, 252, 0.8); border-radius: 8px; border-left: 3px solid #3b82f6;'>
                <p style='margin: 0; color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                    📊 <strong>TAM:</strong> <span style='color: #1e293b;'>{tam}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        competitors = market_metrics.get("competitors", [])
        if competitors and len(competitors) > 0:
            st.markdown(f"""
            <div style='margin-top: 8px; padding: 8px 12px; background: rgba(248, 250, 252, 0.8); border-radius: 8px; border-left: 3px solid #10b981;'>
                <p style='margin: 0; color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                    🏢 <strong>Competitors:</strong> <span style='color: #1e293b;'>{len(competitors)} identified</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        pmf = product_metrics.get("product_market_fit", "N/A")
        st.metric(
            "Product-Market Fit",
            str(pmf).title(),
            delta=None
        )
        feature_platform = product_metrics.get("is_feature_or_platform", "N/A")
        if feature_platform != "N/A" and feature_platform:
            st.markdown(f"""
            <div style='margin-top: 12px; padding: 8px 12px; background: rgba(248, 250, 252, 0.8); border-radius: 8px; border-left: 3px solid #8b5cf6;'>
                <p style='margin: 0; color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                    🔧 <strong>Type:</strong> <span style='color: #1e293b;'>{str(feature_platform).title()}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
        tech_risk = product_metrics.get("technical_risk", "N/A")
        if tech_risk != "N/A" and tech_risk:
            risk_text = str(tech_risk)[:50] + "..." if len(str(tech_risk)) > 50 else str(tech_risk)
            st.markdown(f"""
            <div style='margin-top: 8px; padding: 8px 12px; background: rgba(248, 250, 252, 0.8); border-radius: 8px; border-left: 3px solid #f59e0b;'>
                <p style='margin: 0; color: #64748b; font-size: 0.875rem; font-weight: 600;'>
                    ⚠️ <strong>Risk:</strong> <span style='color: #1e293b;'>{risk_text}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ultimate Debate Section
    st.markdown("""
    <div style='margin-bottom: 2rem; animation: fadeInUp 0.9s ease-out;'>
        <h2 style='margin-bottom: 0.75rem;'>💬 Agent Debate</h2>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Real-time discussion between Market and Product analysts</p>
    </div>
    """, unsafe_allow_html=True)
    
    debate_messages = parse_debate_transcript(result.get('debate_transcript', ''))
    
    if debate_messages:
        chat_container = st.container()
        with chat_container:
            for i, msg in enumerate(debate_messages):
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
    
    # Ultimate Deep Dives
    st.markdown("""
    <div style='margin-bottom: 2rem; animation: fadeInUp 1s ease-out;'>
        <h2 style='margin-bottom: 0.75rem;'>🔍 Deep Dives</h2>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Detailed analysis reports from each agent</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📈 Market Analysis", expanded=True):
            market_analysis_raw = result.get('market_analysis', '')
            
            # Try to parse as JSON first
            market_parsed = clean_json(market_analysis_raw)
            
            if market_parsed:
                st.json(market_parsed)
            elif market_analysis_raw:
                # Display raw text with better formatting
                st.markdown(f"""
                <div style='background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;'>
                    <pre style='white-space: pre-wrap; word-wrap: break-word; font-family: "JetBrains Mono", monospace; font-size: 14px; color: #1e293b; margin: 0;'>{market_analysis_raw}</pre>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Market analysis not available")
                st.text("No market analysis data found.")
    
    with col2:
        with st.expander("🛡️ Product Analysis", expanded=True):
            product_analysis_raw = result.get('product_analysis', '')
            
            # Debug: Show if data exists
            if not product_analysis_raw or product_analysis_raw.strip() == '':
                st.error("⚠️ Product analysis is empty or not available")
                st.info("The product analysis field appears to be empty. This might indicate an issue with the agent workflow.")
            else:
                # Try to parse as JSON first
                product_parsed = clean_json(product_analysis_raw)
                
                if product_parsed:
                    st.json(product_parsed)
                else:
                    # Display raw text with better formatting
                    st.markdown("**Raw Analysis Text:**")
                    st.markdown(f"""
                    <div style='background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-top: 10px;'>
                        <pre style='white-space: pre-wrap; word-wrap: break-word; font-family: "JetBrains Mono", monospace; font-size: 14px; color: #1e293b; margin: 0; line-height: 1.6;'>{product_analysis_raw}</pre>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Ultimate Final Verdict
    st.markdown("""
    <div style='margin-bottom: 2rem; animation: fadeInUp 1.1s ease-out;'>
        <h2 style='margin-bottom: 0.75rem;'>⚖️ Investment Verdict</h2>
        <p style='color: #64748b; font-size: 0.9375rem; margin: 0; font-weight: 500;'>Final recommendation from the General Partner</p>
    </div>
    """, unsafe_allow_html=True)
    
    final_memo = result.get('final_memo', '')
    color_class, verdict_text = get_verdict_color(final_memo)
    
    st.markdown(f'<div class="final-memo-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="{color_class}">{verdict_text}</div>', unsafe_allow_html=True)
    st.markdown(final_memo)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Ultimate Download Button
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

# Ultimate Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 3rem 0; color: #64748b; font-size: 0.9375rem; animation: fadeInUp 1.2s ease-out;'>
        <p style='margin: 0; font-weight: 700; font-size: 1.0625rem; color: #1e293b;'>DealScout VC Terminal</p>
        <p style='margin: 0.75rem 0 0 0; font-weight: 500;'>Multi-Agent Deal Analysis Platform</p>
    </div>
""", unsafe_allow_html=True)
