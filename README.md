# StockAutoAgent
## StockAutoAgent: Real-Time Autonomous Analysis of U.S. Stocks Powered by LangChain-Ollama (Llama-3) Agentic Framework
The code and additional resources for this project are on my GitHub.
Imagine having your own AI research assistant that works like a Wall Street analyst - except it's free, private, and runs entirely on your laptop. This agentic AI framework automates the entire stock research process, transforming raw market data into actionable insights without relying on expensive terminals or cloud APIs. Let's say you want to analyze NVIDIA (NVDA). Here's what the system does autonomously:
Real-Time Data Fetching: Pulls live prices, financial statements, and key metrics (P/E ratios, revenue growth, etc.) directly from market sources.
Intelligent News Analysis: Scrapes the latest articles, earnings reports, and analyst updates - then summarizes the most impactful developments.
Decision-Ready Outputs: Generates a structured report with a buy/hold/sell recommendation, backed by valuation models, risk assessments, and competitive analysis.

The magic? It does this offline using open-source tools, with no subscriptions or data leaks. Whether you're an investor looking for an edge, a developer curious about agentic AI, or a student exploring applied LLMs, this project turns cutting-edge research techniques into a practical, free toolkit.
Here is the high-level design below.
## Tools & Tech Used:
### LangChain (for autonomous agent workflows)
### Llama-3 via Ollama (local LLM that reasons about stocks)
### yFinance (free Yahoo Finance API alternative)
### BeautifulSoup/Requests (for scraping and cleaning data)
### Streamlit (interactive web dashboard)

## Here is the high-level design below
  <img src="high-level Advanced Stock Research Agent.png" alt="Agentic_rag" width="400"/>

## Key Process Stages:
### Input Phase:
User enters stock ticker
System validates input format

### Data Acquisition:
Parallel fetching via:
 -  yFinance API (fundamentals)
 -  Web scraping (price/news)
Error handling for failed requests

### Data Processing:
Statistics:
 -  Categorization (Valuation/Financial/Dividends/Trading) 
- Number formatting (currency, percentages)
### News:
 - Metadata extraction (source, timestamp) 
- Summary truncation 
- Link formatting

### UI Rendering:
Price header with refresh time
Tabbed statistics display
Expandable news cards
AI analysis generation: 
- Prompt engineering 
- LLM processing 
- Markdown rendering

### Output:
Complete dashboard with:
- Real-time data
- Organized statistics
- Detailed news
- AI recommendations

### Error Handling Paths:
Invalid tickers skip processing
Failed API calls show user-friendly errors
Missing data fields show "N/A" gracefully


## Run the following command in CMD after saving and configuring (installing the modules) the file: finance_yahoo.py
  streamlit run finance_yahoo.py

## Details on the architecture are provided below
  <img src="Advanced Stock Research Agent_detail.png" alt="Agentic_rag" width="400"/>

