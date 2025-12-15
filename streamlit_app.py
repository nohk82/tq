import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import strategy_core
from datetime import datetime

# =========================================================
# ⚙️ PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="StrategyPro Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 🎨 CUSTOM CSS (Dark Theme + Styling)
# =========================================================
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Accent Color */
    .accent { color: #58a6ff !important; font-weight: bold; }
    .red { color: #f85149 !important; font-weight: bold; }
    .green { color: #3fb950 !important; font-weight: bold; }
    
    /* Custom Box Styling */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .metric-lbl { font-size: 0.8em; color: #8b949e; margin-bottom: 5px; }
    .metric-val { font-size: 1.2em; font-weight: bold; color: #f0f6fc; }
    
    /* Condition Boxes */
    .cond-box {
        padding: 12px;
        border-radius: 8px;
        font-size: 0.85em;
        line-height: 1.4;
        background: rgba(255,255,255,0.03);
        border: 1px solid #30363d;
        height: 100%;
    }
    .cond-box.buy { border-left: 3px solid #3fb950; }
    .cond-box.sell { border-left: 3px solid #f85149; }
    .cond-title { font-weight: bold; margin-bottom: 8px; font-size: 1em; }
    .cond-list { margin: 0; padding-left: 1.2em; }
    
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔢 SIDEBAR CONTROLS
# =========================================================
with st.sidebar:
    st.markdown("## Strategy<span class='accent'>Pro</span>", unsafe_allow_html=True)
    
    # Symbol & Refresh
    c1, c2 = st.columns([3, 1])
    with c1:
        symbol = st.text_input("Target Symbol", value="TQQQ")
    with c2:
        st.write("") # Spacer
        st.write("") 
        if st.button("⟳"):
            st.rerun()

    # Start Date (Default: 2010-02-01)
    start_date_input = st.date_input("Start Date", value=datetime(2010, 2, 1))
    start_date_str = start_date_input.strftime("%Y-%m-%d")

    st.markdown("---")
    
    # Sliders
    ma_period = st.slider("MA Period (Days)", 50, 300, 192)
    w_period = st.slider("Weekly RSI Period", 10, 50, 23)
    w_buy_max = st.slider("RSI-W Buy Max", 30, 80, 63)
    d_buy_cross = st.slider("RSI-D Buy Cross", 10, 50, 28)
    w_sell_cross = st.slider("Sell Cross (W)", 50, 90, 68)
    w_profit_max = st.slider("Profit Max (W)", 70, 95, 83)
    stop_loss = st.slider("Stop Loss (%)", 0.05, 0.30, 0.18, step=0.01)

    if st.button("Reset to Defaults", type="primary"):
        st.rerun()

# =========================================================
# 🧠 STRATEGY EXECUTION
# =========================================================
params = {
    'ma_period': ma_period,
    'd_period': 3, # Fixed as per original code
    'w_period': w_period,
    'w_buy_max': w_buy_max,
    'd_buy_cross': d_buy_cross,
    'w_sell_cross': w_sell_cross,
    'w_profit_max': w_profit_max,
    'stop_loss': stop_loss,
    'start_date': start_date_str
}

with st.spinner('Calculating Strategy...'):
    try:
        data = strategy_core.get_strategy_data(symbol, params)
        if not data:
            st.error("No data returned. Please check the symbol and start date.")
            st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

# =========================================================
# 📊 DASHBOARD LAYOUT
# =========================================================

# 1. TOP METRICS
# Row 1: Market Info
m1, m2, m3, m4 = st.columns(4)
m1.metric("Price", f"${data['diagnosis']['price']:,.2f}")
m2.metric("MA(200)", f"${data['diagnosis']['ma']:,.2f}")
m3.metric("RSI(W)", f"{data['diagnosis']['rsi_w']:.1f}")
m4.metric("RSI(D)", f"{data['diagnosis']['rsi_d']:.1f}")

st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)

# Row 2: Strategy Results
s1, s2, s3, s4, s5 = st.columns(5)
s1.metric("CAGR", f"{data['cagr']:.1f}%")
s2.metric("MDD", f"{data['mdd']:.1f}%")
s3.metric("Final Balance", f"${int(data['final_balance']):,}")
s4.metric("B&H (Start)", f"${int(data['bnh_start']):,}")
s5.metric("B&H (1st Buy)", f"${int(data['bnh_first_buy']):,}")

st.markdown("---")

# 2. SECONDARY STATS & CONDITIONS
c1, c2, c3 = st.columns([1.5, 2, 2])

with c1:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-lbl'>Total Trades</div>
        <div class='metric-val'>{data['total_trades']}</div>
        <div class='metric-lbl' style='margin-top:10px'>Win Rate</div>
        <div class='metric-val accent'>{data['win_rate']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='cond-box buy'>
        <div class='cond-title'>🟢 Buy 조건</div>
        <ul class='cond-list'>
            <li>1. 추세상승: C > MA (장기이평선 위)</li>
            <li>2. 주봉RSI < 63 (과매수 아님)</li>
            <li>3. 일봉RSI 28 돌파 (1,2 만족 시)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='cond-box sell'>
        <div class='cond-title'>🔴 Sell 조건</div>
        <ul class='cond-list'>
            <li>1. Bearish: MA 아래로 하락</li>
            <li>2. Stop Loss: -18%</li>
            <li>3. Trend Broken: 주봉RSI 68 하향돌파</li>
            <li>4. Profit Max: 주봉RSI 83 이상</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# =========================================================
# 📈 CHARTS (Plotly)
# =========================================================

# --- CHART 1: TECHNICAL ANALYSIS ---
st.subheader("Technical Analysis")

# Convert date strings back to datetime objects for Plotly if needed, 
# but Plotly handles ISO strings well.
# EXTRACT DATA FROM EQUITY CURVE
eq_data = data['equity_curve']
dates = [e['date'] for e in eq_data]
closes = [e['price'] for e in eq_data]
ma_line = [e['ma'] for e in eq_data]
equity_vals = [e['equity'] for e in eq_data]

fig_tech = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                         vertical_spacing=0.05, row_heights=[0.7, 0.3])

# Price Candle (Approximated with Line + Fill or just Line for simplicity as backend sends arrays)
fig_tech.add_trace(go.Scatter(x=dates, y=closes, mode='lines', name='Price', line=dict(color='#c9d1d9', width=1)), row=1, col=1)
fig_tech.add_trace(go.Scatter(x=dates, y=ma_line, mode='lines', name=f'MA({ma_period})', line=dict(color='#58a6ff', width=1)), row=1, col=1)

# Add Trades (Buy/Sell Markers)
trades = data['trades'] 
# Note: trades is a list of events (newest first). We should reverse it or handle it.
# Usually easiest to process oldest to newest for pairing, but markers don't care.

buy_x = []
buy_y = []
sell_x = []
sell_y = []

# Process events for markers
for t in trades:
    if t['type'] == 'Buy':
        buy_x.append(t['date'])
        buy_y.append(t['price'])
    elif t['type'] == 'Sell':
        sell_x.append(t['date'])
        sell_y.append(t['price'])
        # Add profit label
        profit_pct = t.get('profit_pct', 0)
        profit_color = '#58a6ff' if profit_pct > 0 else '#f85149'
        fig_tech.add_annotation(
            x=t['date'], y=t['price'],
            text=f"{profit_pct:.1f}%",
            showarrow=True, arrowhead=1, ax=0, ay=-20,
            font=dict(color=profit_color, size=10)
        )

# Buy Markers
fig_tech.add_trace(go.Scatter(
    x=buy_x, y=buy_y, mode='markers', name='Buy',
    marker=dict(symbol='triangle-up', size=10, color='#3fb950')
), row=1, col=1)

# Sell Markers
fig_tech.add_trace(go.Scatter(
    x=sell_x, y=sell_y, mode='markers', name='Sell',
    marker=dict(symbol='triangle-down', size=10, color='#f85149')
), row=1, col=1)

# RSI Subplot (Assuming we can recalculate or if backend sends it? 
# Backend DOES NOT send RSI arrays in the filtered dict 'get_strategy_data'.
# It only returns current values. 
# So we skip RSI chart or recalculate. 
# Since we import strategy_core, we could call get_data and calc RSI locally?
# For now, let's stick to what's available: Price + Equity.)

fig_tech.update_layout(height=600, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_tech, use_container_width=True)

# --- CHART 2: EQUITY CURVE ---
st.subheader("Equity Curve")
# Use the extracted equity values
fig_equity = go.Figure()
fig_equity.add_trace(go.Scatter(x=dates, y=equity_vals, mode='lines', name='Equity', line=dict(color='#58a6ff', width=2)))
fig_equity.update_layout(height=400, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig_equity, use_container_width=True)

# =========================================================
# 📋 RECENT TRADES
# =========================================================
st.subheader("Recent Trades")
if trades:
    # Trades are returned newest first. Let's reverse to process chronologically if needed,
    # but for display we want newest first.
    # However, to pair them (Buy -> Sell), we need to find the matching events.
    # Strategy core returns simple list. 
    # Let's reconstruct pairs.
    
    # Sort by date ascending to pair easily
    sorted_trades = sorted(trades, key=lambda x: x['date'])
    
    trade_pairs = []
    current_buy = None
    
    for t in sorted_trades:
        if t['type'] == 'Buy':
            current_buy = t
        elif t['type'] == 'Sell' and current_buy:
            # Found a pair
            trade_pairs.append({
                "Date": current_buy['date'],
                "Price": f"${current_buy['price']:.2f} → ${t['price']:.2f}",
                "Profit": f"{t['profit_pct']:.1f}%",
                "Days": f"{t['holding_days']}d",
                "Exit": t['reason']
            })
            current_buy = None
            
    # Include currently holding position if any
    if current_buy:
         trade_pairs.append({
                "Date": current_buy['date'],
                "Price": f"${current_buy['price']:.2f} → -",
                "Profit": "-",
                "Days": "-",
                "Exit": "Holding"
            })
    
    # Show newest first
    if trade_pairs:
        st.dataframe(pd.DataFrame(trade_pairs[::-1]), use_container_width=True)
    else:
        st.info("No completed trades yet.")

else:
    st.info("No trades found.")
