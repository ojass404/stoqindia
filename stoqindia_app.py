
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

# Load NSE universe (upload your CSV to GitHub)
@st.cache_data
def load_universe():
    df = pd.read_csv("indian_stocks_all_nse.csv")
    df["symbol"] = df["symbol"].str.strip().str.upper()
    df["name"] = df["name"].str.strip()
    return df

STOCK_UNIVERSE = load_universe()

def stoqindia_pro():
    st.markdown("""
    <style>
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #e3f2fd 100%);}
    .stMetric {background: #e8f5e8; border-radius: 12px;}
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 StoqIndia")
    st.sidebar.success(f"✅ {len(STOCK_UNIVERSE):,} NSE Stocks")
    
    tab = st.sidebar.radio("Select:", 
        ["📈 Market", "🔍 Stocks", "💼 Portfolio"])
    
    if "📈 Market" in tab:
        st.header("📊 NIFTY 50 Live")
        nifty_data = yf.download("^NSEI", period="6mo", progress=False)
        if not nifty_data.empty:
            close_prices = nifty_data['Close']
            current_price = close_prices.iloc[-1]
            total_return = (close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("NIFTY 50", f"{current_price:.0f}")
            col2.metric("6M Return", f"{total_return:.1f}%")
            col3.metric("Volume", f"{nifty_data['Volume'].iloc[-1]:,.0f}")
            
            fig = go.Figure(data=[go.Candlestick(
                x=nifty_data.index,
                open=nifty_data.Open, high=nifty_data.High,
                low=nifty_data.Low, close=nifty_data.Close
            )])
            fig.update_layout(title="NIFTY 50 Live", height=500)
            st.plotly_chart(fig, use_container_width=True)
    
    elif "🔍 Stocks" in tab:
        st.header("🔍 NSE Stocks")
        search_symbols = STOCK_UNIVERSE['symbol'].head(20).tolist()
        search = st.selectbox("Quick search:", [""] + search_symbols)
        
        if search:
            data = yf.download(f"{search}.NS", period="6mo", progress=False)
            if not data.empty:
                col1, col2 = st.columns([3,1])
                fig = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data.Open, high=data.High,
                    low=data.Low, close=data.Close
                )])
                fig.update_layout(title=f"{search}.NS", height=400)
                col1.plotly_chart(fig, use_container_width=True)
                
                close_prices = data['Close']
                current_price = close_prices.iloc[-1]
                price_change = (close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100
                col2.metric("Price", f"₹{current_price:.0f}")
                col2.metric("6M Return", f"{price_change:.1f}%")
    
    elif "💼 Portfolio" in tab:
        st.header("💼 Portfolio")
        safe_symbols = STOCK_UNIVERSE['symbol'].head(20).tolist()
        selected = st.multiselect("Pick stocks:", safe_symbols[:6], default=safe_symbols[:3])
        
        if len(selected) >= 3 and st.button("⚙️ Optimize"):
            demo_weights = np.random.random(len(selected))
            demo_weights = demo_weights / demo_weights.sum()
            demo_df = pd.DataFrame({
                'Symbol': selected,
                'Weight': [f"{w:.1%}" for w in demo_weights]
            })
            st.dataframe(demo_df)
            fig = px.pie(demo_df, values='Weight', names='Symbol', hole=0.4)
            st.plotly_chart(fig)

stoqindia_pro()
