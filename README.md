# 🔍 ResearchAI – Multi-Agent AI Research System

An AI-powered research assistant that autonomously searches the web, extracts relevant information, generates detailed research reports, and evaluates them using multiple specialized AI agents.

Built using **Python, LangChain, Gemini 2.5 Flash, Tavily, BeautifulSoup, LCEL, and Streamlit.**

---

## 🚀 Overview

ResearchAI is a multi-agent research system designed to automate the entire research process.

Instead of manually searching multiple websites, reading articles, and preparing reports, users can simply enter a research topic and let multiple AI agents collaborate to complete the task.

The system uses specialized agents, each responsible for a particular stage of the research workflow.

## ✨ Key Features

- **Autonomous Web Search:** Uses Tavily to retrieve relevant and recent information from the web.
- **Intelligent Web Scraping:** Uses BeautifulSoup to extract meaningful content from websites.
- **Multi-Agent Architecture:** Uses specialized AI agents for searching and reading information.
- **ReAct Agents:** Agents can reason about tasks and decide when to invoke available tools.
- **AI-Powered Report Generation:** Generates structured research reports using Gemini.
- **Automated Report Evaluation:** A Critic Agent reviews the generated report and provides a score, strengths, and improvement suggestions.
- **LCEL Pipelines:** Uses LangChain Expression Language and Runnables to compose processing pipelines.
- **Interactive Dashboard:** Streamlit frontend for entering research topics and viewing results.
- **Report Export:** Download generated research reports for future reference.

---

## 🏗️ System Architecture

The system consists of four major stages:

```text
              USER RESEARCH QUERY
                       |
                       ▼
             ┌──────────────────┐
             │  SEARCH AGENT    │
             │   (ReAct Agent)  │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │   TAVILY TOOL    │
             │   Web Search     │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │  READER AGENT    │
             │   (ReAct Agent)  │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │ BEAUTIFULSOUP    │
             │  Scraping Tool   │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │   WRITER CHAIN   │
             │  Gemini + LCEL   │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │   CRITIC CHAIN   │
             │  Gemini + LCEL   │
             └──────────────────┘
                       |
                       ▼
             ┌──────────────────┐
             │  FINAL REPORT    │
             │ + CRITIC REVIEW  │
             └──────────────────┘
```

## 🤖 AI Agents & Their Responsibilities

### 1. Search Agent

- Powered by Gemini 2.5 Flash.
- Uses the Tavily Search API.
- Searches for relevant information based on the user's research topic.
- Retrieves article titles, URLs, and content snippets.

### 2. Reader Agent

- Uses BeautifulSoup for web scraping.
- Extracts relevant information from selected URLs.
- Removes unnecessary HTML elements.
- Provides extracted website content for further analysis.

### 3. Writer Agent

- Implemented using LCEL.
- Uses a ChatPromptTemplate, Gemini LLM, and StrOutputParser.
- Converts collected research into a structured report.
- Organizes information into introduction, key findings, conclusion, and sources.

### 4. Critic Agent

- Implemented using LCEL.
- Reviews the generated research report.
- Evaluates the quality of the report.
- Provides a score out of 10.
- Identifies strengths and areas for improvement.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | Agent development and orchestration |
| LangChain LCEL | Pipeline composition |
| Gemini 2.5 Flash | LLM for reasoning and generation |
| Tavily | Web search |
| BeautifulSoup | Web scraping |
| Requests | HTTP requests |
| Streamlit | Frontend dashboard |
| Python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
multiagent/
│
├── __pycache__/
│
├── venv/
│
├── .env
│
├── tools.py
│   └── Tavily search and BeautifulSoup scraping tools
│
├── agents.py
│   └── Gemini initialization, ReAct agents and LCEL chains
│
├── pipeline.py
│   └── Main research pipeline and agent execution
│
├── app.py
│   └── Streamlit frontend
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
```

Navigate to the project directory:

```bash
cd multiagent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory.

Add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get your API keys:

- Gemini API: https://aistudio.google.com/apikey
- Tavily API: https://app.tavily.com/

**Important:** Never upload your `.env` file or expose your API keys publicly.

### 5. Run the Application

Start the Streamlit application:

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

## 💻 Usage

1. Launch the ResearchAI application.
2. Enter a research topic in the input field.
3. Click on **Start Research**.
4. The Search Agent retrieves relevant web resources.
5. The Reader Agent extracts content from selected websites.
6. The Writer Agent generates a structured research report.
7. The Critic Agent evaluates the generated report.
8. View and download the final research report and evaluation.

### Example Research Topics

```text
Latest developments in Artificial Intelligence

Impact of Electric Vehicles on the Automobile Industry

Recent developments in semiconductor technology

Latest sports news and major sporting events

Future of Generative AI and Large Language Models
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | API key for Gemini LLM |
| `TAVILY_API_KEY` | API key for Tavily Search |

---

## 🔮 Future Improvements

- Implement iterative research with automatic report refinement based on Critic feedback.
- Add conditional execution and retry mechanisms using LangGraph.
- Introduce source credibility scoring and cross-source fact verification.
- Improve article-specific content extraction.
- Add research history and persistent storage.
- Support PDF report generation.
- Add streaming responses and real-time agent execution tracking.
- Introduce more specialized agents for domain-specific research.

---

## ⚠️ Limitations

- Search quality depends on Tavily search results.
- Some websites may block automated scraping.
- Dynamic websites may require browser-based scraping.
- LLM-generated reports can contain inaccurate or unsupported claims.
- Critic evaluation is AI-generated and should not be treated as guaranteed fact verification.

Always verify important information against the original sources.

---

## 👨‍💻 Author

**Harish Kushwaha**

B.Tech – Electronics and Communication Engineering  
Maulana Azad National Institute of Technology (MANIT), Bhopal

---

## ⭐ Support

If you find this project interesting, consider giving it a star on GitHub!

**ResearchAI – Making research smarter through collaborative AI agents.**
