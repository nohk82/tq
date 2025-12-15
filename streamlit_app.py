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
    /* Compact Sidebar Elements */
    section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    section[data-testid="stSidebar"] .stElementContainer {
        margin-bottom: 0.2rem !important;
    }
    section[data-testid="stSidebar"] hr {
        margin: 1rem 0 !important;
    }
    
    /* ======================================= */
    /* 🛠️ SIDEBAR & HEADER CONFIGURATION       */
    /* ======================================= */
    
    /* 1. Sidebar Text Brightness */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
        color: #e6edf3 !important; /* Default Text Color */
    }
    
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div[data-testid="stMarkdown"],
    section[data-testid="stSidebar"] div[data-testid="stSliderTickBarMin"],
    section[data-testid="stSidebar"] div[data-testid="stSliderTickBarMax"] {
        color: #e6edf3 !important; /* Force Bright Text */
    }
    
    /* 2. Transparent Header (Remove White Bar) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        background-color: transparent !important;
        border-bottom: none !important;
    }

    /* 3. Ensure Sidebar Toggle is Visible & White */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        color: #e6edf3 !important;
        background: transparent !important;
        z-index: 999 !important;
    }
    [data-testid="stSidebarCollapsedControl"] > svg {
        fill: #e6edf3 !important;
    }

    /* Hide standard UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    
    /* Start of Accent Colors  */
    .accent { color: #58a6ff !important; font-weight: bold; }
    .red { color: #f85149 !important; font-weight: bold; }
    .green { color: #3fb950 !important; font-weight: bold; }
    
    /* Metric Box */
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .metric-lbl { font-size: 0.9em; color: #c9d1d9 !important; margin-bottom: 5px; } /* Brightened Label */
    .metric-val { font-size: 1.2em; font-weight: bold; color: #f0f6fc; }
    
    /* Top Bar Grid */
    .top-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .top-grid-2 {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .top-item {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    
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
    
    /* Trade Table Styling */
    .trade-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Outfit', sans-serif;
        font-size: 0.9em;
    }
    .trade-table th {
        text-align: left;
        padding: 10px;
        color: #8b949e;
        border-bottom: 1px solid #30363d;
    }
    .trade-table td {
        padding: 10px;
        border-bottom: 1px solid #21262d;
        color: #c9d1d9;
    }
    .trade-row:hover { background-color: #161b22; }
    .type-buy { color: #3fb950; font-weight: bold; }
    .type-sell { color: #f85149; font-weight: bold; }
    .profit-pos { color: #58a6ff; }
    .profit-neg { color: #f85149; }
    
    /* Status Icon Box (New 6-State Style) */
    .status-container {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-bottom: 20px;
    }
    .status-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 10px 15px;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 80px;
        opacity: 0.5; /* Default Dimmed */
        transition: all 0.3s;
    }
    .status-box.active {
        opacity: 1.0;
        border: 2px solid #58a6ff; /* Blue Highlight */
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
        background-color: #1f242c;
    }
    .status-emoji { font-size: 1.8em; margin-bottom: 5px; }
    .status-text { font-size: 0.9em; font-weight: bold; color: #8b949e; }
    .status-box.active .status-text { color: #f0f6fc; }
    
    /* History Strip */
    .history-container {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: hidden; /* Hide scrollbar if possible, but fit content */
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 5px 10px; /* Tighter padding */
        margin-bottom: 20px;
        align-items: center;
        gap: 2px; /* Tighter gap */
        justify-content: center; /* Center align items */
    }
    .hist-item {
        font-size: 0.9em; /* Smaller font */
        min-width: 15px; /* Smaller width */
        text-align: center;
        cursor: default;
    }
    .hist-item:hover {
        transform: scale(1.2);
    }
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
    
    # Sliders using custom markdown for styling "Default" text
    def styled_slider(label, min_v, max_v, default_v, step=None, key_suffix=""):
        st.markdown(f"""
        <div style="margin-bottom: -10px; font-size: 0.9em; color: #e6edf3;">
            {label} <span style="color: #8b949e; margin-left: 5px; font-size: 0.85em;">(Def: {default_v})</span>
        </div>
        """, unsafe_allow_html=True)
        return st.slider("", min_v, max_v, default_v, step=step, label_visibility="collapsed", key=f"slider_{key_suffix}_{label}")

    ma_period = styled_slider("MA Period (Days)", 50, 300, 192, key_suffix="ma")
    w_period = styled_slider("Weekly RSI Period", 10, 50, 23, key_suffix="w_p")
    w_buy_max = styled_slider("RSI-W Buy Max", 30, 80, 63, key_suffix="w_buy")
    d_buy_cross = styled_slider("RSI-D Buy Cross", 10, 50, 28, key_suffix="d_buy")
    w_sell_cross = styled_slider("Sell Cross (W)", 50, 90, 68, key_suffix="w_sell")
    w_profit_max = styled_slider("Profit Max (W)", 70, 95, 83, key_suffix="w_prof")
    stop_loss = styled_slider("Stop Loss (%)", 0.05, 0.30, 0.18, step=0.01, key_suffix="stop")

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
# Using Custom HTML for exact styling control (Bright labels, Custom Colors)

# Diagnosis Keys Map
diag = data['diagnosis']

html_stats = f"""
<!-- Row 1: Market Info -->
<div class="top-grid">
    <div class="top-item">
        <div class="metric-lbl">Price</div>
        <div class="metric-val">${diag['price']:,.2f}</div>
    </div>
    <div class="top-item">
        <div class="metric-lbl">MA({params['ma_period']})</div>
        <div class="metric-val">${diag['ma']:,.2f}</div>
    </div>
    <div class="top-item">
        <div class="metric-lbl">RSI(W)</div>
        <div class="metric-val">{diag['rsi_w']:.1f}</div>
    </div>
    <div class="top-item">
        <div class="metric-lbl">RSI(D)</div>
        <div class="metric-val">{diag['rsi_d']:.1f}</div>
    </div>
</div>

<!-- Row 1.5: Status Icons (6-State System) -->
<div class="status-container">
    <!-- 0: Bearish -->
    <div class="status-box {'active' if diag['active_status_id'] == 0 else ''}">
        <div class="status-emoji">⛔</div>
        <div class="status-text">Bearish</div>
    </div>
    <!-- 1: Wait -->
    <div class="status-box {'active' if diag['active_status_id'] == 1 else ''}">
        <div class="status-emoji">💤</div>
        <div class="status-text">Wait</div>
    </div>
    <!-- 2: Buy -->
    <div class="status-box {'active' if diag['active_status_id'] == 2 else ''}">
        <div class="status-emoji">🔥</div>
        <div class="status-text">Buy</div>
    </div>
    <!-- 3: Hold -->
    <div class="status-box {'active' if diag['active_status_id'] == 3 else ''}">
        <div class="status-emoji">👌</div>
        <div class="status-text">Hold</div>
    </div>
    <!-- 4: Sell -->
    <div class="status-box {'active' if diag['active_status_id'] == 4 else ''}">
        <div class="status-emoji">⚠️</div>
        <div class="status-text">Sell</div>
    </div>
    <!-- 5: Profit -->
    <div class="status-box {'active' if diag['active_status_id'] == 5 else ''}">
        <div class="status-emoji">💰</div>
        <div class="status-text">Profit</div>
    </div>
</div>

<!-- History Strip (Last 30 Days) -->
<div class="history-container">
    <div style="font-size: 0.8em; color: #8b949e; margin-right: 10px; white-space: nowrap;">Recent Activity (30d):</div>
    <!-- Icons inserted here via Python loop -->
"""

# Extract last 30 days status
recent_curve = data['equity_curve'][-35:] # Get a bit more, user said approx 30
# Mapping: 0=Bear, 1=Wait, 2=Buy, 3=Hold, 4=Profit, 5/6=Sell
# Note: Strategy Core 's' values: 0=Bear, 1=Wait/Bull, 2=Buy, 3=Hold, 4=Profit, 5=Stop, 6=Break
status_map = {
    0: "⛔", # Bearish
    1: "💤", # Wait
    2: "🔥", # Buy
    3: "👌", # Hold
    4: "💰", # Profit
    5: "⚠️", # Sell (Stop)
    6: "⚠️"  # Sell (Break)
}

hist_html = ""
for day in recent_curve:
    s = day.get('s', 1)
    icon = status_map.get(s, "❓")
    date_str = day['date']
    # Tooltip with date
    hist_html += f"<div class='hist-item' title='{date_str}'>{icon}</div>"

html_stats += hist_html + "</div>" + f"""
<!-- Row 2: Strategy Results -->
<div class="top-grid-2">
    <div class="top-item">
        <div class="metric-lbl">CAGR</div>
        <div class="metric-val accent">{data['cagr']:.1f}%</div> <!-- Sky Blue -->
    </div>
    <div class="top-item">
        <div class="metric-lbl">MDD</div>
        <div class="metric-val red">{data['mdd']:.1f}%</div> <!-- Red -->
    </div>
    <div class="top-item">
        <div class="metric-lbl">Final Balance</div>
        <div class="metric-val">${int(data['final_balance']):,}</div>
    </div>
    <div class="top-item">
        <div class="metric-lbl">B&H (Start)</div>
        <div class="metric-val">${int(data['bnh_start']):,}</div>
    </div>
    <div class="top-item">
        <div class="metric-lbl">B&H (1st Buy)</div>
        <div class="metric-val">${int(data['bnh_first_buy']):,}</div>
    </div>
</div>
"""
st.markdown(html_stats, unsafe_allow_html=True)

st.markdown("---")

# 2. SECONDARY STATS & CONDITIONS
c1, c2, c3 = st.columns([1.5, 2, 2])

with c1:
    st.markdown(f"""
    <div class='metric-box'>
        <div class='metric-lbl'>Total Trades</div>
        <div class='metric-val'>{data['total_trades']} <span style='font-size:0.6em; color:#8b949e'>(Win {data['win_count']})</span></div>
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
# MA Line: User requested "Dark Color". Using a dimmed gray-blue.
fig_tech.add_trace(go.Scatter(x=dates, y=ma_line, mode='lines', name=f'MA({ma_period})', line=dict(color='#3d444d', width=1.5)), row=1, col=1)

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
            showarrow=True, arrowhead=1, ax=0, ay=-25,
            font=dict(color=profit_color, size=14, family="Arial Black") # Larger font
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

fig_tech.update_layout(
    height=600, 
    template="plotly_dark", 
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=True, 
        gridcolor='#21262d', 
        tickformat="%Y-%m-%d", 
        type="date",
        showticklabels=True, # Force labels
        automargin=True, # Prevent cutoff
        tickangle=-45, # Tilt for better fit
        nticks=20 # Suggest approximately 20 ticks
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#21262d'
    ),
    legend=dict(
        font=dict(color="white") # Legend Text White
    )
)
st.plotly_chart(fig_tech, use_container_width=True)

# --- CHART 2: EQUITY CURVE ---
st.subheader("Equity Curve")
# Use the extracted equity values
fig_equity = go.Figure()

# Calculate B&H (1st Buy) Curve
bnh_values = [None] * len(dates) # Default to None
first_buy_price = 0
start_idx = -1

# Find first buy date from trades
# We need to match trade dates to our 'dates' list
# 'trades' is a list of dicts. We find the earliest 'Buy' type.
# Assuming trades are chronological or we sort them.
# Let's verify trade order or just find the min date.
buy_trades = [t for t in trades if t['type'] == 'Buy']
if buy_trades:
    # Get earliest buy
    first_buy = min(buy_trades, key=lambda x: x['date']) # Ensure we get the very first
    start_date = first_buy['date']
    
    # Find index in dates list
    if start_date in dates:
        start_idx = dates.index(start_date)
        first_buy_price = closes[start_idx]
        
        # Calculate B&H series starting from this index
        # align with strategy's starting capital (usually 1st equity value)
        initial_cap = equity_vals[0] if equity_vals else 10000
        shares = initial_cap / first_buy_price
        
        for i in range(start_idx, len(dates)):
            bnh_values[i] = shares * closes[i]

# Add B&H Trace (Dark/Dimmed)
fig_equity.add_trace(go.Scatter(
    x=dates, y=bnh_values, 
    mode='lines', 
    name='B&H (1st Buy)', 
    line=dict(color='#e3b341', width=1.5) # Solid Yellow Line
))

# Add Strategy Equity Trace (Blue)
fig_equity.add_trace(go.Scatter(x=dates, y=equity_vals, mode='lines', name='Equity', line=dict(color='#58a6ff', width=2)))
fig_equity.update_layout(
    height=400, 
    template="plotly_dark", 
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=True, 
        gridcolor='#21262d',
        tickformat="%Y-%m-%d"
    ),
    yaxis=dict(
        showgrid=True, 
        gridcolor='#21262d'
    ),
    legend=dict(
        font=dict(color="white") # Legend Text White
    )
)
st.plotly_chart(fig_equity, use_container_width=True)

# =========================================================
# 📋 RECENT TRADES
# =========================================================
st.subheader("Recent Trades")
if trades:
    # Custom HTML Table (Styles moved to global CSS)
    
    # Header
    html_table = """
    <table class="trade-table">
        <thead>
            <tr>
                <th>Type</th>
                <th>Date</th>
                <th>Price</th>
                <th>Info</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for t in trades:
        t_type = t['type']
        t_date = t['date']
        t_price = f"${t['price']:,.2f}"
        
        type_class = "type-buy" if t_type == "Buy" else "type-sell"
        info_html = ""
        
        if t_type == "Sell":
            profit = t.get('profit_pct', 0)
            p_class = "profit-pos" if profit > 0 else "profit-neg"
            days = t.get('holding_days', 0)
            reason = t.get('reason', '')
            info_html = f"<span class='{p_class}'>{profit:+.1f}%</span> <span style='color:#666'>({days}d)</span> <span style='font-size:0.8em; color:#8b949e'>{reason}</span>"
        else:
            info_html = "<span style='color: #444'>Entry</span>"
            
        # IMPORTANT: No indentation for the HTML string to avoid Code Block rendering
        row_html = f"""<tr class="trade-row"><td class="{type_class}">{t_type}</td><td>{t_date}</td><td>{t_price}</td><td>{info_html}</td></tr>"""
        html_table += row_html
        
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)
else:
    st.info("No trades found.")
