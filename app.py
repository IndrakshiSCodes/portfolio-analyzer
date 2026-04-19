import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Folio — Portfolio Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
            
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@300;400;500&family=Instrument+Sans:wght@400;500;600&display=swap');

:root {
    --midnight:   #0d2b2b;
    --moss:       #2d4a3e;
    --darkgreen:  #1a3a2a;
    --beige:      #f0e6d3;
    --beige-dim:  #d9cbb8;
    --rosy:       #c4837a;
    --rosy-light: #e8b4ad;
    --accent:     #4a7c6f;
    --card-bg:    #112626;
    --card-border:#1e3d35;
    --text-muted: #8aab9e;
}

html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif;
    background-color: var(--midnight) !important;
    color: var(--beige) !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--midnight); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--darkgreen) !important;
    border-right: 1px solid var(--card-border);
}
[data-testid="stSidebar"] * { color: var(--beige) !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    color: var(--beige) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stDateInput input {
    background-color: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    color: var(--beige) !important;
    border-radius: 6px !important;
}

/* Buttons */
.stButton > button {
    background-color: var(--rosy) !important;
    color: var(--midnight) !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 0.5rem 1.5rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: var(--rosy-light) !important;
    transform: translateY(-1px) !important;
}

/* Main content background */
.main .block-container {
    background-color: var(--midnight) !important;
    padding-top: 2rem !important;
}

/* Metric cards */
.metric-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--rosy), var(--accent));
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    line-height: 1;
    color: var(--beige);
}
.metric-value.positive { color: #6fcba8; }
.metric-value.negative { color: var(--rosy); }
.metric-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 0.3rem;
}

/* Section headers */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--beige);
    margin: 2rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--card-border);
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

/* Table styling */
.stDataFrame {
    background: var(--card-bg) !important;
    border-radius: 10px !important;
    border: 1px solid var(--card-border) !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
    color: var(--beige) !important;
    font-family: 'Instrument Sans', sans-serif !important;
}

/* Divider */
hr { border-color: var(--card-border) !important; }

/* Toggle */
[data-testid="stCheckbox"] label { color: var(--beige) !important; }

/* Hero title */
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    color: var(--beige);
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.tag {
    display: inline-block;
    background: var(--moss);
    color: var(--beige-dim);
    border-radius: 4px;
    padding: 2px 10px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    margin-right: 6px;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
COLORS = ["#c4837a", "#4a7c6f", "#e8b4ad", "#6fcba8", "#8aab9e", "#d9cbb8", "#2d4a3e"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#112626",
    font=dict(family="DM Mono, monospace", color="#f0e6d3", size=11),
    xaxis=dict(gridcolor="#1e3d35", showgrid=True, zeroline=False,
               tickfont=dict(size=10), linecolor="#1e3d35"),
    yaxis=dict(gridcolor="#1e3d35", showgrid=True, zeroline=False,
               tickfont=dict(size=10), linecolor="#1e3d35"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e3d35",
                borderwidth=1, font=dict(size=10)),
    margin=dict(l=10, r=10, t=30, b=10),
    hovermode="x unified",
)

@st.cache_data(show_spinner=False)
def fetch_data(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        closes = raw["Close"]
    else:
        closes = raw[["Close"]] if "Close" in raw.columns else raw
    closes = closes.dropna(how="all")
    return closes

def calculate_metrics(prices, investment):
    norm   = prices / prices.iloc[0]
    port   = norm.mean(axis=1) * investment
    daily_ret = port.pct_change().dropna()
    total_ret = (port.iloc[-1] / port.iloc[0] - 1) * 100
    days  = (prices.index[-1] - prices.index[0]).days
    cagr  = ((port.iloc[-1] / port.iloc[0]) ** (365 / max(days, 1)) - 1) * 100
    vol   = daily_ret.std() * np.sqrt(252) * 100
    sharpe = (daily_ret.mean() * 252) / (daily_ret.std() * np.sqrt(252) + 1e-9)
    roll_max = port.cummax()
    drawdown = (port - roll_max) / roll_max * 100
    max_dd = drawdown.min()
    return port, total_ret, cagr, vol, sharpe, drawdown, max_dd

def color_val(val):
    if val > 0:   return "positive"
    if val < 0:   return "negative"
    return ""

def metric_card(label, value, sub=""):
    cls = color_val(float(str(value).replace("%","").replace("x","")) if any(c.isdigit() or c in "-." for c in str(value)) else 0)
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {cls}">{value}</div>
        {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.8rem">folio.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Portfolio Analyzer</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        **Enter NSE tickers** with `.NS` suffix:
        - `RELIANCE.NS` — Reliance
        - `TCS.NS` — TCS
        - `INFY.NS` — Infosys
        - `HDFCBANK.NS` — HDFC Bank

        For **US stocks** just use the ticker:
        - `AAPL`, `MSFT`, `GOOGL`

        **Sharpe Ratio** measures return per unit of risk.
        Above 1 is good, above 2 is excellent.

        **Max Drawdown** is the worst peak-to-trough fall.
        """)

    st.markdown("### Portfolio Setup")
    ticker_input = st.text_input(
        "Stock tickers (comma separated)",
        value="RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS",
        help="Use .NS for NSE stocks"
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("To", value=date.today())

    investment = st.number_input("Investment amount (₹)", value=100000, step=10000, min_value=1000)
    compare_nifty = st.checkbox("Compare with NIFTY 50", value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("Analyze Portfolio", use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────
# Hero
st.markdown("""
<div style="margin-bottom: 0.5rem">
    <span class="tag">NSE / BSE / Global</span>
    <span class="tag">Live Data</span>
    <span class="tag">Risk Analysis</span>
</div>
<div class="hero-title">Your Portfolio,<br><i>Decoded.</i></div>
<div class="hero-subtitle" style="margin-bottom: 2rem">Enter tickers in the sidebar and hit Analyze</div>
""", unsafe_allow_html=True)

if not run:
    st.markdown("""
    <div style="background:#112626; border:1px solid #1e3d35; border-radius:12px; padding:2rem; margin-top:1rem; text-align:center;">
        <div style="font-family:'DM Serif Display',serif; font-size:1.2rem; color:#8aab9e; margin-bottom:0.5rem">
            Configure your portfolio in the sidebar
        </div>
        <div style="font-family:'DM Mono',monospace; font-size:11px; color:#4a7c6f; letter-spacing:0.08em">
            ENTER TICKERS → SET DATE RANGE → CLICK ANALYZE
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Fetch ─────────────────────────────────────────────────────────────────────
tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

with st.spinner("Fetching market data..."):
    prices = fetch_data(tickers, start_date, end_date)
    if compare_nifty:
        nifty = fetch_data(["^NSEI"], start_date, end_date)

if prices.empty:
    st.error("Could not fetch data. Check your tickers and date range.")
    st.stop()

# align columns
valid_tickers = [t for t in tickers if t in prices.columns]
if not valid_tickers:
    valid_tickers = prices.columns.tolist()
prices = prices[valid_tickers].dropna(how="all")


# ── Calculations ───────────────────────────────────────────────────────────────
port_value, total_ret, cagr, vol, sharpe, drawdown, max_dd = calculate_metrics(prices, investment)

if compare_nifty and not nifty.empty:
    nifty_prices = nifty.iloc[:, 0].reindex(prices.index).ffill()
    nifty_norm   = (nifty_prices / nifty_prices.iloc[0]) * investment


# ── Section 1: Metrics ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Portfolio Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(metric_card("Total Return", f"{total_ret:+.2f}%",
                f"₹{port_value.iloc[0]:,.0f} → ₹{port_value.iloc[-1]:,.0f}"), unsafe_allow_html=True)
with c2:
    st.markdown(metric_card("CAGR", f"{cagr:+.2f}%", "Annualized return"), unsafe_allow_html=True)
with c3:
    st.markdown(metric_card("Sharpe Ratio", f"{sharpe:.2f}x",
                "↑ Higher is better"), unsafe_allow_html=True)
with c4:
    st.markdown(metric_card("Max Drawdown", f"{max_dd:.2f}%",
                "Worst peak-to-trough"), unsafe_allow_html=True)


# ── Section 2: Performance Chart ──────────────────────────────────────────────
st.markdown('<div class="section-header">📈 Performance vs Benchmark</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=port_value.index, y=port_value.round(2),
    name="Your Portfolio",
    line=dict(color="#c4837a", width=2.5),
    fill="tozeroy", fillcolor="rgba(196,131,122,0.07)",
    hovertemplate="₹%{y:,.0f}<extra>Portfolio</extra>"
))

if compare_nifty and not nifty.empty:
    fig.add_trace(go.Scatter(
        x=nifty_norm.index, y=nifty_norm.round(2),
        name="NIFTY 50",
        line=dict(color="#4a7c6f", width=1.8, dash="dot"),
        hovertemplate="₹%{y:,.0f}<extra>NIFTY 50</extra>"
    ))

fig.update_layout(**PLOTLY_LAYOUT, height=380,
                  yaxis_title="Portfolio Value (₹)",
                  title=dict(text="Portfolio Value Over Time", font=dict(family="DM Serif Display", size=15, color="#f0e6d3")))
fig.update_yaxes(tickprefix="₹", tickformat=",.0f")
st.plotly_chart(fig, use_container_width=True)


# ── Section 3: Individual Stock Breakdown ─────────────────────────────────────
st.markdown('<div class="section-header">🔍 Stock Breakdown</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])

with col_left:
    individual_returns = []
    for t in valid_tickers:
        s = prices[t].dropna()
        if len(s) < 2: continue
        ret = (s.iloc[-1] / s.iloc[0] - 1) * 100
        days = (s.index[-1] - s.index[0]).days
        t_cagr = ((s.iloc[-1] / s.iloc[0]) ** (365 / max(days, 1)) - 1) * 100
        individual_returns.append({
            "Ticker": t,
            "Current Price": f"₹{s.iloc[-1]:,.2f}",
            "Return %": f"{ret:+.2f}%",
            "CAGR %": f"{t_cagr:+.2f}%",
            "Weight": f"{100/len(valid_tickers):.1f}%"
        })

    df_stocks = pd.DataFrame(individual_returns)
    st.dataframe(df_stocks, use_container_width=True, hide_index=True,
                 column_config={
                     "Return %": st.column_config.TextColumn("Return %"),
                 })

with col_right:
    weights = [100 / len(valid_tickers)] * len(valid_tickers)
    fig_pie = go.Figure(go.Pie(
        labels=valid_tickers,
        values=weights,
        hole=0.55,
        marker=dict(colors=COLORS[:len(valid_tickers)],
                    line=dict(color="#0d2b2b", width=2)),
        textfont=dict(family="DM Mono, monospace", size=10, color="#f0e6d3"),
        hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>"
    ))
    fig_pie.update_layout(
        **{k: v for k, v in PLOTLY_LAYOUT.items() if k not in ["xaxis","yaxis","hovermode","legend"]},
        height=260,
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=10), x=1, y=0.5),
        annotations=[dict(text="Allocation", x=0.5, y=0.5,
                          font=dict(family="DM Serif Display", size=13, color="#f0e6d3"),
                          showarrow=False)]
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# ── Section 4: Risk Analysis ───────────────────────────────────────────────────
st.markdown('<div class="section-header">⚠️ Risk Analysis</div>', unsafe_allow_html=True)

col_dd, col_corr = st.columns(2)

with col_dd:
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=drawdown.index, y=drawdown.round(2),
        name="Drawdown",
        line=dict(color="#e8b4ad", width=1.5),
        fill="tozeroy", fillcolor="rgba(196,131,122,0.15)",
        hovertemplate="%{y:.2f}%<extra>Drawdown</extra>"
    ))
    fig_dd.update_layout(**PLOTLY_LAYOUT, height=280,
                         title=dict(text="Portfolio Drawdown",
                                    font=dict(family="DM Serif Display", size=14, color="#f0e6d3")),
                         yaxis_ticksuffix="%")
    st.plotly_chart(fig_dd, use_container_width=True)

with col_corr:
    if len(valid_tickers) > 1:
        ret_df = prices[valid_tickers].pct_change().dropna()
        corr   = ret_df.corr()

        fig_corr, ax = plt.subplots(figsize=(4, 3))
        fig_corr.patch.set_facecolor("#112626")
        ax.set_facecolor("#112626")
        sns.heatmap(corr, annot=True, fmt=".2f", ax=ax,
                    cmap=sns.diverging_palette(10, 150, s=60, l=40, n=9),
                    linewidths=0.5, linecolor="#0d2b2b",
                    annot_kws={"size": 9, "family": "monospace", "color": "#f0e6d3"},
                    cbar_kws={"shrink": 0.7})
        ax.tick_params(colors="#8aab9e", labelsize=8)
        ax.set_title("Correlation Matrix", color="#f0e6d3",
                     fontsize=11, pad=8, fontfamily="serif")
        for spine in ax.spines.values():
            spine.set_edgecolor("#1e3d35")
        plt.tight_layout()
        st.pyplot(fig_corr, use_container_width=True)
        plt.close()
    else:
        st.info("Add more stocks to see correlation analysis.")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; font-family:'DM Mono',monospace; font-size:10px;
            color:#4a7c6f; letter-spacing:0.1em; padding-bottom:1rem">
    FOLIO · BUILT WITH PYTHON + STREAMLIT · DATA VIA YAHOO FINANCE
</div>
""", unsafe_allow_html=True)
