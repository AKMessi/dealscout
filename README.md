# 🕵️ DealScout: The Autonomous Investment Committee

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![AI](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)
![Orchestration](https://img.shields.io/badge/Orchestration-LangGraph-purple)

> **"It's like having 3 associates and a principal analyst shredding your deal at 3 AM... except they're AI, and they find loopholes humans miss."**

---

## 🚀 Overview

**DealScout** is a multi-agent due diligence system that automates the "Top of Funnel" analysis for Venture Capitalists. Instead of passively summarizing pitch decks, DealScout employs a **Combative Multi-Agent Architecture** where specialized AI agents actively research, cross-examine, and debate the viability of a startup.

### The Core Loop
1.  **Ingest:** Accepts detailed Pitch Decks OR just Company Name + URL.
2.  **Research:** If minimal input provided, the Research Agent auto-generates a pitch deck from web sources.
3.  **Analyze:** Market, Product, and Traction analysts verify claims via Google Search & Web Scraping.
4.  **Debate:** The three analysts **argue** in a simulated IC meeting.
5.  **Critical Questions:** A dedicated agent generates hard-hitting questions to reconsider before investing.
6.  **Verdict:** A GP (General Partner) Agent synthesizes everything into a final "Pass/Invest" memo.

---

## 🧠 The Agent Swarm

DealScout is powered by **7 specialized agents** running on **Google Gemini 2.5 Flash** via **LangGraph**:

| Agent | Role | Capabilities |
| :--- | :--- | :--- |
| 🔍 **Company Researcher** | The Web Detective | Auto-generates pitch decks from just company name + URL. Scrapes websites, searches news. |
| 🕵️ **Market Analyst** | The Optimist/Skeptic | Verifies TAM/SAM via Google Search. Checks competitor funding & market timing. |
| 🛡️ **Product Analyst** | The Technical Auditor | Scrapes company website. Validates tech stack claims. Checks "Is it live?" |
| 📉 **Traction Analyst** | The BS Detector | Cross-references claimed revenue with public signals (traffic, headcount, news). |
| ⚔️ **Debate Moderator** | The Instigator | Forces the analysts to argue. Detects contradictions in their reports. |
| 🎯 **Questions Generator** | The Devil's Advocate | Generates critical questions to reconsider before investing. |
| 📝 **Synthesizer (GP)** | The Decision Maker | Reads the debate transcript & questions. Writes the final Investment Memo. |

---

## ⚡ Key Features

- **🚀 Quick Mode:** Just enter company name + URL. AI auto-generates a pitch deck from web research before analysis.
- **Live Agent Debate:** Watch the Market, Product, and Traction agents fight over the startup's moat and viability.
- **Questions to Reconsider:** Get 8-12 hard-hitting questions across Market, Product, Traction, and Team categories before making an investment decision.
- **Active Fact-Checking:** The system doesn't trust the PDF. It googles the competitors and scrapes the landing page.
- **Deep Dive Dashboards:** Expandable technical, market, and traction reports with raw data sources.
- **Visual "VC Terminal" UI:** Dark-mode, financial terminal aesthetic built with Streamlit.
- **PDF & URL Support:** Drag-and-drop a deck or just paste a URL to start diligence.

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- A Google API Key (for Gemini 2.5 Flash)
- Serper API Key (for Google Search capabilities)

### Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AKMessi/dealscout.git
   cd dealscout
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Create a `.env` file in the root directory:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run ui/app.py
   ```

---

## 📁 Project Structure

```
dealscout/
├── src/
│   ├── agent.py           # Main agent implementation with tools
│   └── deal_scout.py      # Simplified agent workflow
├── ui/
│   └── app.py             # Streamlit frontend
├── prompts/
│   ├── market_analyst.md
│   ├── product_analyst.md
│   ├── traction_analyst.md
│   ├── debate_moderator.md
│   ├── questions_to_reconsider.md
│   └── gp_synthesizer.md
├── .env                   # API keys (not in git)
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🎯 Usage

DealScout supports **two input modes**:

### ✨ Quick Mode (Company Name + URL Only)
Don't have a pitch deck? No problem! Just enter:
- **Company Name** (e.g., "Anthropic")
- **Company Website** (e.g., "https://anthropic.com")

Our AI Research Agent will:
1. Scrape the company website
2. Search for recent news, funding, and traction data
3. Generate a comprehensive pitch deck automatically
4. Run the full analysis pipeline

### 📄 Full Pitch Deck Mode
Have a detailed pitch deck? Paste it directly:
- **Full Pitch Deck Text** with sections like Product, Market, Traction, Team
- **Company Website** (optional, for additional product analysis)

### Analysis Workflow
1. **Enter Input:** Choose Quick Mode or Full Pitch Deck mode
2. **Run Analysis:** Click "Run Analysis" to start the 7-agent pipeline
3. **Review Results:**
   - Check the **Dashboard** for key metrics
   - Read the **Agent Debate** for conflicting viewpoints
   - View **Auto-Generated Pitch** (if using Quick Mode)
   - Review the **Deep Dives** for detailed analysis
   - **Questions to Reconsider** - Critical questions before investing
   - Check the **Investment Verdict** for the final recommendation

---

## 🔑 API Keys

### Google API Key (for Gemini 2.5 Flash)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GOOGLE_API_KEY`

### Serper API Key (for Google Search)
1. Go to [Serper.dev](https://serper.dev/)
2. Sign up and get an API key
3. Add it to your `.env` file as `SERPER_API_KEY`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚠️ Disclaimer

This tool is for educational and research purposes. Investment decisions should not be made solely based on AI analysis. Always conduct thorough due diligence and consult with financial advisors.
