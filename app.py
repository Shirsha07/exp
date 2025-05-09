import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date
import ta

# App Title
st.title("Stock Market Visualizer with Enhanced Analytics")
st.sidebar.title("Options")

# Helper Functions
def fetch_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_candles_stick_bar(df, title="", currency="", show_ema=True, show_rsi=True, show_macd=True, show_atr=True):
    # Compute technical indicators
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['MACD'] = ta.trend.macd_diff(df['Close'])
    df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.4, 0.15, 0.15, 0.15, 0.15],
        subplot_titles=("Candlestick + EMA20" if show_ema else "Candlestick", 
                        "Volume", 
                        "RSI" if show_rsi else "",
                        "MACD" if show_macd else "",
                        "ATR" if show_atr else "")
    )

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green',
        decreasing_line_color='red',
        name="Candlestick"
    ), row=1, col=1)

    # Add EMA20 if selected
    if show_ema:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['EMA20'], mode="lines", name="EMA 20", line=dict(color='orange')
        ), row=1, col=1)

    # Volume chart
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], name="Volume"
    ), row=2, col=1)

    # Add RSI if selected
    if show_rsi:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'], mode="lines", name="RSI", line=dict(color='purple')
        ), row=3, col=1)

    # Add MACD if selected
    if show_macd:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD'], mode="lines", name="MACD", line=dict(color='green')
        ), row=4, col=1)

    # Add ATR if selected
    if show_atr:
        fig.add_trace(go.Scatter(
            x=df.index, y=df['ATR'], mode="lines", name="ATR", line=dict(color='blue')
        ), row=5, col=1)

    fig.update_layout(
        title=f"{title} {currency}",
        template="plotly_dark",
        height=1000,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig)

def plot_volume(data):
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark")
    st.plotly_chart(fig)

def plot_daily_returns(data):
    data['Daily Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Daily Return', title="Daily Returns (%)", template="plotly_dark")
    st.plotly_chart(fig)

def plot_cumulative_returns(data):
    data['Cumulative Return'] = (1 + data['Close'].pct_change()).cumprod() - 1
    fig = px.line(data, x=data.index, y='Cumulative Return', title="Cumulative Returns", template="plotly_dark")
    st.plotly_chart(fig)

def plot_moving_averages(data, windows):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name="Close Price"))
    for window in windows:
        data[f"MA{window}"] = data['Close'].rolling(window=window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}"))
    fig.update_layout(title="Moving Averages", xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig)

def plot_correlation_matrix(data):
    corr = data.corr()
    fig = px.imshow(corr, title="Correlation Matrix", template="plotly_dark", text_auto=True, color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Fetch Nifty 200 list (hardcoded sample for demo – replace with full list or API if needed)
nifty_200 = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "WIPRO.NS", "LT.NS", "HCLTECH.NS",
    "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS", "HINDUNILVR.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "HDFC.NS", "TITAN.NS", "ULTRACEMCO.NS", "NTPC.NS",
    "NESTLEIND.NS", "POWERGRID.NS", "ONGC.NS", "BAJAJFINSV.NS", "TATAMOTORS.NS", "COALINDIA.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "TECHM.NS", "HINDALCO.NS", "JSWSTEEL.NS", "BPCL.NS", "IOC.NS", "GRASIM.NS", "CIPLA.NS",
    "DRREDDY.NS", "DIVISLAB.NS", "EICHERMOT.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "SHREECEM.NS",
    "INDUSINDBK.NS", "HDFCLIFE.NS", "SBILIFE.NS", "ICICIPRULI.NS", "HAVELLS.NS", "GAIL.NS", "PIDILITIND.NS",
    "DABUR.NS", "GODREJCP.NS", "BERGEPAINT.NS", "AMBUJACEM.NS", "ACC.NS", "TATACONSUM.NS", "M&M.NS", "LUPIN.NS",
    "AUROPHARMA.NS", "BIOCON.NS", "CADILAHC.NS", "GLENMARK.NS", "TORNTPHARM.NS", "PEL.NS", "SRF.NS", "ABBOTINDIA.NS",
    "ALKEM.NS", "APOLLOHOSP.NS", "FORTIS.NS", "MAXHEALTH.NS", "METROPOLIS.NS", "DRL.NS", "LALPATHLAB.NS", "IPCALAB.NS",
    "PFIZER.NS", "SANOFI.NS", "SUNTV.NS", "ZEEL.NS", "PVR.NS", "INOXLEISUR.NS", "TV18BRDCST.NS", "NETWORK18.NS",
    "DISHTV.NS", "HATHWAY.NS", "DEN.NS", "SAREGAMA.NS", "TIPSINDLTD.NS", "MIRZAINT.NS", "TANLA.NS", "NAUKRI.NS",
    "INFOEDGE.NS", "IRCTC.NS", "ZOMATO.NS", "PAYTM.NS", "POLYCAB.NS", "KEI.NS", "FINCABLES.NS", "HINDZINC.NS",
    "VEDL.NS", "NMDC.NS", "NATIONALUM.NS", "MOIL.NS", "HINDCOPPER.NS", "BALRAMCHIN.NS", "DHAMPURSUG.NS", "EIDPARRY.NS",
    "TRIVENI.NS", "DWARKESH.NS", "DCMSHRIRAM.NS", "DCL.NS", "RAJESHEXPO.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS",
    "BAJAJHLDNG.NS", "CHOLAFIN.NS", "LICHSGFIN.NS", "CANFINHOME.NS", "RECLTD.NS", "PFC.NS", "IRFC.NS", "HUDCO.NS",
    "NBCC.NS", "NCC.NS", "KNRCON.NS", "PNCINFRA.NS", "ASHOKLEY.NS", "ESCORTS.NS", "VOLTAS.NS", "BLUESTARCO.NS",
    "WHIRLPOOL.NS", "IFBIND.NS", "TTKPRESTIG.NS", "CROMPTON.NS", "BAJAJELEC.NS", "HAVELLS.NS", "ORIENTELEC.NS",
    "BOSCHLTD.NS", "MOTHERSON.NS", "AMARAJABAT.NS", "EXIDEIND.NS", "LUMAXIND.NS", "VARROC.NS", "MINDTREE.NS",
    "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTI.NS", "LTTS.NS", "TATAELXSI.NS", "CYIENT.NS", "ZENSARTECH.NS",
    "NIITTECH.NS", "BIRLACORPN.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "HEIDELBERG.NS", "INDIACEM.NS", "ORIENTCEM.NS",
    "PRSMJOHNSN.NS", "JKLAKSHMI.NS", "SAGCEM.NS", "NCLIND.NS", "KCP.NS", "DECCANCE.NS", "ANDHRACEMT.NS", "SHREECEM.NS",
    "ULTRACEMCO.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "HEIDELBERG.NS",
    "INDIACEM.NS", "ORIENTCEM.NS", "PRSMJOHNSN.NS", "JKLAKSHMI.NS", "SAGCEM.NS", "NCLIND.NS", "KCP.NS", "DECCANCE.NS",
    "ANDHRACEMT.NS", "SHREECEM.NS", "ULTRACEMCO.NS", "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "JKCEMENT.NS",
    "RAMCOCEM.NS", "HEIDELBERG.NS", "INDIACEM.NS", "ORIENTCEM.NS", "PRSMJOHNSN.NS", "JKLAKSHMI.NS", "SAGCEM.NS",
    "NCLIND.NS", "KCP.NS", "DECCANCE.NS", "ANDHRACEMT.NS", "SHREECEM.NS", "ULTRACEMCO.NS", "AMBUJACEM.NS", "ACC.NS",
    "DALBHARAT.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "HEIDELBERG.NS", "INDIACEM.NS", "ORIENTCEM.NS", "PRSMJOHNSN.NS",
    "JKLAKSHMI.NS", "SAGCEM.NS", "NCLIND.NS", "KCP.NS", "DECCANCE.NS", "ANDHRACEMT.NS", "SHREECEM.NS", "ULTRACEMCO.NS",
    "AMBUJACEM.NS", "ACC.NS", "DALBHARAT.NS", "JKCEMENT.NS", "RAMCOCEM.NS", "HEIDELBERG.NS", "INDIACEM.NS",
    "ORIENTCEM.NS", "PRSMJOHNSN.NS", "JKLAKSHMI.NS", "SAGCEM.NS", "NCLIND.NS", "KCP.NS", "DECCANCE.NS", "ANDHRACEMT.NS"
]
# Sidebar Inputs
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="RELIANCE.NS")
start_date = st.sidebar.date_input("Start Date", value=date(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

data = fetch_stock_data(ticker, start_date, end_date)

# Sidebar Checkboxes for Indicators
show_ema = st.sidebar.checkbox("EMA (20)", value=True)
show_rsi = st.sidebar.checkbox("RSI")
show_macd = st.sidebar.checkbox("MACD")
show_atr = st.sidebar.checkbox("ATR")

# Stock Visualizations
if not data.empty:
    st.subheader(f"Stock Data for {ticker}")
    st.write(data.tail())

    st.subheader("Candlestick + Indicators")
    plot_candles_stick_bar(data, title=ticker, show_ema=show_ema, show_rsi=show_rsi, show_macd=show_macd, show_atr=show_atr)

    st.subheader("Volume Chart")
    plot_volume(data)

    st.subheader("Daily Returns")
    plot_daily_returns(data)

    st.subheader("Cumulative Returns")
    plot_cumulative_returns(data)

    st.sidebar.header("Moving Averages")
    moving_averages = st.sidebar.multiselect("Select Moving Averages (days)", options=[10, 20, 50, 100, 200], default=[20, 50])
    if moving_averages:
        st.subheader("Moving Averages")
        plot_moving_averages(data, moving_averages)

# Portfolio Correlation
st.sidebar.header("Portfolio Analysis")
portfolio_file = st.sidebar.file_uploader("Upload Portfolio (CSV or Excel)")
if portfolio_file:
    portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith("csv") else pd.read_excel(portfolio_file)
    tickers = portfolio['Ticker'].tolist()
    st.subheader("Portfolio Data")
    st.write(portfolio)

    portfolio_data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
    portfolio_df = pd.DataFrame(portfolio_data)
    st.subheader("Correlation Matrix")
    plot_correlation_matrix(portfolio_df)

# Top Gainers & Losers in Nifty 200
st.markdown("---")
st.header("📊 Market Summary: Gainers, Losers & Trend")

# Define a list of sample tickers (replace with actual index tickers if desired)
market_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'INTC', 'CSCO']
price_changes = {}

for symbol in market_tickers:
    try:
        df = fetch_stock_data(symbol, start_date, end_date)
        if len(df) >= 2:
            change = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
            price_changes[symbol] = round(change, 2)
    except:
        continue

# Sort to get top gainers and losers
sorted_changes = dict(sorted(price_changes.items(), key=lambda item: item[1], reverse=True))
gainers = dict(list(sorted_changes.items())[:5])
losers = dict(list(sorted_changes.items())[-5:])

col1, col2 = st.columns(2)
with col1:
    st.subheader("🚀 Top Gainers")
    st.write(pd.DataFrame(gainers.items(), columns=["Ticker", "Change (%)"]))

with col2:
    st.subheader("📉 Top Losers")
    st.write(pd.DataFrame(losers.items(), columns=["Ticker", "Change (%)"]))
# Upward Trend Stocks based on TA
st.subheader("📊 Scan for Bullish Breakout Stocks")

start_date = date(2024, 1, 1)
end_date = date.today()

def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

# Automatically run the analysis
bullish_stocks = []

progress = st.progress(0)
for i, t in enumerate(nifty_200):
    try:
        df = fetch_stock_data(t)
        if df.empty or len(df) < 50:
            continue

        df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20).fillna(0)
        macd = ta.trend.macd(df['Close']).fillna(0)
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi().fillna(0)
        boll = ta.volatility.BollingerBands(df['Close'], window=20)

        macd_val = macd.iloc[-1]
        rsi_val = rsi.iloc[-1]
        close = df['Close'].iloc[-1]
        upper_band = boll.bollinger_hband().iloc[-1]
        ema20 = df['EMA20'].iloc[-1]

        if macd_val > 0 and rsi_val > 50 and close >= upper_band and close > ema20:
            bullish_stocks.append({
                "Ticker": t,
                "MACD": round(macd_val, 2),
                "RSI": round(rsi_val, 2),
                "Close": round(close, 2),
                "Upper Band": round(upper_band, 2),
                "EMA20": round(ema20, 2)
            })
    except Exception as e:
        st.error(f"Error processing {t}: {e}")
    progress.progress((i + 1) / len(nifty_200))

# Display the results
if bullish_stocks:
    df_result = pd.DataFrame(bullish_stocks)
    st.success("📋 Bullish breakout stocks detected:")
    st.dataframe(df_result)
else:
    st.warning("❌ No bullish breakout stocks found.")
# 📩 Contact Me
st.sidebar.markdown("---")
st.sidebar.markdown("📬 **Contact Me**")
if st.sidebar.button("Get in Touch"):
    st.sidebar.markdown("📧 Email: yourname@example.com")
    st.sidebar.markdown("🔗 [LinkedIn](https://www.linkedin.com/in/yourprofile)")
