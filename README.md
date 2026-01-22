# 🕵️ DealScout: The Autonomous Investment Committee

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)
![Orchestration](https://img.shields.io/badge/Orchestration-LangGraph-purple)

> **"It's like having 2 associates and a principal analyst shredding your deal at 3 AM... except they're AI, and they find loopholes humans miss."**

---

## 🚀 Overview

**DealScout** is a multi-agent due diligence system that automates the "Top of Funnel" analysis for Venture Capitalists. Instead of passively summarizing pitch decks, DealScout employs a **Combative Multi-Agent Architecture** where specialized AI agents actively research, cross-examine, and debate the viability of a startup.

### The Core Loop
1.  **Ingest:** Accepts Pitch Decks (PDF) or Company URLs.
2.  **Research:** Agents dispatch to Google Search & Web Scrapers to verify claims.
3.  **Debate:** The Market and Product agents **argue** in a simulated IC meeting.
4.  **Verdict:** A GP (General Partner) Agent synthesizes the conflict into a final "Pass/Invest" memo.

---

## 🧠 The Agent Swarm

DealScout is powered by **5 specialized agents** running on **Gemini 2.5 Flash** via **LangGraph**:

| Agent | Role | Capabilities |
| :--- | :--- | :--- |
| 🕵️ **Market Analyst** | The Optimist/Skeptic | Verifies TAM/SAM via Google Search. Checks competitor funding & market timing. |
| 🛡️ **Product Analyst** | The Technical Auditor | Scrapes company website. Validates tech stack claims. Checks "Is it live?" |
| 📉 **Traction Analyst** | The BS Detector | Cross-references claimed revenue with public signals (traffic, headcount, news). |
| ⚔️ **Debate Moderator** | The Instigator | Forces the Market & Product agents to argue. Detects contradictions in their reports. |
| 📝 **Synthesizer (GP)** | The Decision Maker | Reads the debate transcript. Writes the final Investment Memo with specific "Next Steps." |

---

## ⚡ Key Features

- **Live Agent Debate:** Watch the Market and Product agents fight over the startup's moat and viability.
- **Active Fact-Checking:** The system doesn't trust the PDF. It googles the competitors and scrapes the landing page.
- **Deep Dive Dashboards:** Expandable technical & market reports with raw data sources.
- **Visual "VC Terminal" UI:** Dark-mode, financial terminal aesthetic built with Streamlit.
- **PDF & URL Support:** Drag-and-drop a deck or just paste a URL to start diligence.

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- A Google Cloud API Key (with access to Gemini models)
- Serper API Key (for Google Search capabilities)

### Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/yourusername/dealscout.git](https://github.com/AKMessi/dealscout.git)
   cd dealscout