import re
import streamlit as st
from pathlib import Path
from typing import List, Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from datetime import datetime
import yfinance as yf

# Streamlit configuration (must be first)
st.set_page_config(page_title="Stock Research Agent", layout="wide")

# Configuration
TIMEOUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
YAHOO_FINANCE_URL = "https://finance.yahoo.com/quote/"

# Initialize LLM
@st.cache_resource
def load_llm():
    return Ollama(model="llama3", temperature=0.2)

llm = load_llm()

def clean_text(text: str) -> str:
    """Clean and normalize scraped text"""
    return re.sub(r'\s+', ' ', text).strip()

def format_stat_value(value: Any, stat_type: str) -> str:
    """Format different types of statistics for display"""
    if value is None:
        return "N/A"
    
    if isinstance(value, (int, float)):
        if stat_type == 'currency':
            return f"${value:,.2f}"
        elif stat_type == 'percentage':
            return f"{value:.2%}"
        elif stat_type == 'large_number':
            if abs(value) >= 1e9:
                return f"{value/1e9:,.2f}B"
            elif abs(value) >= 1e6:
                return f"{value/1e6:,.2f}M"
            elif abs(value) >= 1e3:
                return f"{value/1e3:,.2f}K"
        return f"{value:,.2f}"
    return str(value)

def fetch_stock_data(ticker: str) -> Optional[Dict[str, Any]]:
    """Enhanced data fetcher using yfinance and web scraping"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Get all available data from yfinance
        yf_ticker = yf.Ticker(ticker)
        info = yf_ticker.info
        history = yf_ticker.history(period="1d")
        
        # Get current price from most recent trading data
        current_price = history['Close'].iloc[-1] if not history.empty else info.get('currentPrice')
        
        # Scrape news with details from Yahoo Finance
        url = f"{YAHOO_FINANCE_URL}{ticker}"
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Extract detailed news items with metadata
        detailed_news = []
        news_items = soup.find_all('li', {'class': 'js-stream-content'})[:10]
        for item in news_items:
            try:
                headline = item.find('h3').text.strip()
                source = item.find('div', {'class': 'C(#959595)'}).text.strip()
                timestamp = item.find('span', {'class': 'C(#959595)'}).text.strip()
                summary = item.find('p').text.strip() if item.find('p') else ""
                link = item.find('a')['href'] if item.find('a') else "#"
                
                detailed_news.append({
                    'headline': headline,
                    'source': source,
                    'timestamp': timestamp,
                    'summary': summary,
                    'link': f"https://finance.yahoo.com{link}" if not link.startswith('http') else link
                })
            except Exception as e:
                continue
        
        # Organize all available statistics into categories
        stats_categories = {
            'Valuation': {
                'marketCap': ('Market Cap', 'currency'),
                'enterpriseValue': ('Enterprise Value', 'currency'),
                'trailingPE': ('P/E Ratio', 'float'),
                'forwardPE': ('Forward P/E', 'float'),
                'pegRatio': ('PEG Ratio', 'float'),
                'priceToSalesTrailing12Months': ('Price/Sales', 'float'),
                'priceToBook': ('Price/Book', 'float'),
            },
            'Financial': {
                'totalRevenue': ('Revenue', 'currency'),
                'revenuePerShare': ('Revenue/Share', 'currency'),
                'profitMargins': ('Profit Margin', 'percentage'),
                'operatingMargins': ('Operating Margin', 'percentage'),
                'ebitda': ('EBITDA', 'currency'),
                'totalDebt': ('Total Debt', 'currency'),
                'debtToEquity': ('Debt/Equity', 'float'),
            },
            'Dividends': {
                'dividendYield': ('Dividend Yield', 'percentage'),
                'dividendRate': ('Dividend Rate', 'currency'),
                'payoutRatio': ('Payout Ratio', 'percentage'),
                'fiveYearAvgDividendYield': ('5Y Avg Yield', 'percentage'),
            },
            'Trading': {
                'beta': ('Beta', 'float'),
                'fiftyTwoWeekHigh': ('52W High', 'currency'),
                'fiftyTwoWeekLow': ('52W Low', 'currency'),
                'fiftyDayAverage': ('50D Avg', 'currency'),
                'twoHundredDayAverage': ('200D Avg', 'currency'),
                'volume': ('Volume', 'large_number'),
                'averageVolume': ('Avg Volume', 'large_number'),
                'shortRatio': ('Short Ratio', 'float'),
            }
        }
        
        # Build formatted statistics dictionary
        formatted_stats = {}
        for category, stats in stats_categories.items():
            category_stats = {}
            for yf_key, (display_name, fmt_type) in stats.items():
                value = info.get(yf_key)
                category_stats[display_name] = format_stat_value(value, fmt_type)
            formatted_stats[category] = {k: v for k, v in category_stats.items() if v != "N/A"}
        
        return {
            'company_name': info.get('shortName', ticker),
            'ticker': ticker,
            'current_price': format_stat_value(current_price, 'currency'),
            'stats': formatted_stats,
            'news': detailed_news if detailed_news else [{
                'headline': 'No recent news available',
                'source': '',
                'timestamp': '',
                'summary': '',
                'link': '#'
            }],
            'last_updated': current_time,
            'url': url
        }
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}: {str(e)}")
        return None

def display_stock_report(stock_data: Dict[str, Any]):
    """Enhanced display with detailed statistics and news"""
    st.subheader(f"{stock_data['company_name']} ({stock_data['ticker']})")
    
    # Price and update time
    col1, col2 = st.columns([2, 4])
    with col1:
        st.metric("Current Price", stock_data['current_price'])
    with col2:
        st.caption(f"Last updated: {stock_data['last_updated']}")
    
    # Detailed Statistics in tabs
    st.subheader("📊 Detailed Statistics")
    stats_tabs = st.tabs(list(stock_data['stats'].keys()))
    
    for tab, (category, stats) in zip(stats_tabs, stock_data['stats'].items()):
        with tab:
            for stat, value in stats.items():
                st.markdown(f"**{stat}:** `{value}`")
    
    # Enhanced News Section
    st.subheader("📰 Recent News")
    for news_item in stock_data['news']:
        with st.expander(f"{news_item['headline']}", expanded=False):
            if news_item['source'] or news_item['timestamp']:
                st.caption(f"{news_item['source']} • {news_item['timestamp']}")
            if news_item['summary']:
                st.write(news_item['summary'])
            st.markdown(f"[Read more]({news_item['link']})", unsafe_allow_html=True)
    
    # AI Analysis
    st.subheader("🤖 AI Analysis & Recommendation")
    with st.spinner("Generating analysis..."):
        analysis = generate_stock_analysis(stock_data)
        st.markdown(analysis)

def generate_stock_analysis(stock_data: Dict[str, Any]) -> str:
    """Generate detailed AI analysis of the stock"""
    template = """
    Analyze {ticker} ({company_name}) stock with the following data:
    
    **Current Price:** {price}
    
    **Key Statistics:**
    {stats}
    
    **Recent News Highlights:**
    {news}
    
    Provide a comprehensive report with:
    1. **Company Overview**: Business model and industry position
    2. **Financial Health**: Analysis of key metrics and ratios
    3. **Valuation Assessment**: Fair value estimate and comparison
    4. **Recent Developments**: News impact analysis
    5. **Investment Thesis**: Conviction level and time horizon
    6. **Recommendation**: Buy/Hold/Sell with price targets
    7. **Risk Factors**: Key risks to the investment thesis
    """
    
    # Format statistics for the prompt
    stats_str = ""
    for category, stats in stock_data['stats'].items():
        stats_str += f"\n**{category}**\n"
        stats_str += "\n".join([f"- {k}: {v}" for k, v in stats.items()])
    
    # Format news for the prompt
    news_str = "\n".join([
        f"- {item['headline']} ({item['timestamp']}): {item['summary'][:200]}..."
        for item in stock_data['news']
    ])
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["ticker", "company_name", "price", "stats", "news"]
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({
        "ticker": stock_data['ticker'],
        "company_name": stock_data['company_name'],
        "price": stock_data['current_price'],
        "stats": stats_str,
        "news": news_str
    })

def main():
    st.title("💰 Advanced Stock Research Agent")
    st.markdown("""
    Comprehensive stock analysis with detailed statistics, news, and AI-powered insights.
    """)
    
    # Ticker input
    ticker = st.text_input(
        "Enter stock ticker (e.g., AAPL, TSLA, ORCL):",
        placeholder="ORCL",
        help="Use standard ticker symbols"
    ).strip().upper()
    
    if st.button("Get Detailed Report", type="primary") and ticker:
        with st.spinner(f"Fetching comprehensive data for {ticker}..."):
            stock_data = fetch_stock_data(ticker)
        
        if stock_data:
            display_stock_report(stock_data)
        else:
            st.error(f"Could not fetch data for {ticker}. Please try again.")

if __name__ == "__main__":
    main()