"""Single-screen Market Bot dashboard (market data via Yahoo Finance/yfinance).

Important: Yahoo Finance data may be delayed/incomplete and is not an official halt feed.
This dashboard is for research and paper testing, not order execution.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from config import MIN_PRICE, MAX_PRICE, MIN_LIQUIDITY, EXCLUDE_CHINA_STOCKS

st.set_page_config(page_title="Market Bot Scanner", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
.block-container {padding-top: .8rem; padding-bottom: .8rem;}
[data-testid="stMetric"] {background:#111827; border:1px solid #374151; padding:8px 12px; border-radius:8px;}
h1,h2,h3 {margin-bottom:.35rem;}
.small-note {font-size: .8rem; color:#9ca3af;}
.up {color:#22c55e;} .down {color:#ef4444;}
</style>
""", unsafe_allow_html=True)

st.title("MARKET BOT  |  MOMENTUM • GAPS • NEWS • HALT WATCH")
st.caption("Scanner dashboard prototype — data availability depends on the selected symbols and Yahoo Finance coverage.")

col_input, col_refresh, col_status = st.columns([5, 1, 2])
with col_input:
    raw_symbols = st.text_input(
        "Symbols to monitor (comma-separated)",
        value="SPRC, NBIA, JAGX",
        help="This initial version scans the symbols entered here. Full-market scanning needs a complete symbol universe and a suitable live data provider."
    )
with col_refresh:
    st.write("")
    refresh = st.button("Refresh data", type="primary", use_container_width=True)
with col_status:
    st.metric("Price filter", f"${MIN_PRICE:.2f}–${MAX_PRICE:.2f}")
symbols = list(dict.fromkeys(s.strip().upper() for s in raw_symbols.split(",") if s.strip()))
now = datetime.now(ZoneInfo("America/New_York"))
st.caption(f"Eastern time: {now:%Y-%m-%d %I:%M:%S %p %Z}  |  Min traded volume: {MIN_LIQUIDITY:,}  |  China/HK listings excluded when country metadata is available.")

@st.cache_data(ttl=45, show_spinner=False)
def load_symbol(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5d", interval="1m", prepost=True, auto_adjust=False)
    info = {}
    try:
        info = ticker.get_info()
    except Exception:
        pass
    news = []
    try:
        news = ticker.news or []
    except Exception:
        pass
    return hist, info, news

rows, histories, all_news = [], {}, []
progress = st.progress(0, text="Loading selected symbols…") if symbols else None
for i, symbol in enumerate(symbols):
    try:
        hist, info, news = load_symbol(symbol)
        if hist is None or hist.empty:
            rows.append({"Symbol": symbol, "Price": None, "Change %": None, "Volume": 0, "Float": None, "Country": "Unknown", "Status": "No data"})
            continue
        hist = hist.dropna(subset=["Close"])
        histories[symbol] = hist
        latest = hist.iloc[-1]
        prior = hist.iloc[-2] if len(hist) > 1 else latest
        price = float(latest["Close"])
        prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose")
        if not prev_close:
            day = ticker_day = hist[hist.index.date == hist.index[-1].date()]
            prev_close = float(day.iloc[0]["Open"]) if not day.empty else float(prior["Close"])
        change = ((price / float(prev_close)) - 1) * 100 if prev_close else 0.0
        volume = int(hist["Volume"].tail(390).sum())
        country = info.get("country") or "Unknown"
        float_shares = info.get("floatShares")
        day_move_1m = ((price / float(prior["Close"])) - 1) * 100 if float(prior["Close"]) else 0
        vol_avg = float(hist["Volume"].tail(20).mean()) if len(hist) else 0
        latest_vol = float(latest["Volume"])
        # Heuristic only: not an exchange halt prediction or official halt status.
        prehalt = abs(day_move_1m) >= 4 and vol_avg > 0 and latest_vol >= 3 * vol_avg
        excluded = EXCLUDE_CHINA_STOCKS and country.upper() in {"CHINA", "CN", "HONG KONG", "HK"}
        status = "EXCLUDED: China/HK" if excluded else ("PRE-HALT WATCH (heuristic)" if prehalt else "Monitoring")
        rows.append({
            "Symbol": symbol, "Price": price, "Change %": change, "Volume": volume,
            "Float": float_shares, "Country": country, "Status": status,
            "Price OK": MIN_PRICE <= price <= MAX_PRICE,
            "Volume OK": volume >= MIN_LIQUIDITY,
            "Momentum": "30%+" if change >= 30 else ("20%+" if change >= 20 else ("10%+" if change >= 10 else "—")),
            "1m move %": day_move_1m,
        })
        for item in news[:5]:
            content = item.get("content", item)
            title = content.get("title", "")
            if title:
                all_news.append({"Symbol": symbol, "Headline": title, "Publisher": (content.get("provider", {}) or {}).get("displayName", ""), "Link": content.get("clickThroughUrl", {}).get("url", "")})
    except Exception as exc:
        rows.append({"Symbol": symbol, "Price": None, "Change %": None, "Volume": 0, "Float": None, "Country": "Unknown", "Status": f"Data error: {type(exc).__name__}"})
    if progress:
        progress.progress((i + 1) / len(symbols), text=f"Loaded {i + 1}/{len(symbols)} symbols")
if progress:
    progress.empty()

df = pd.DataFrame(rows)
if df.empty:
    st.info("Enter one or more ticker symbols above to populate the dashboard.")
else:
    if "Price OK" not in df: df["Price OK"] = False
    if "Volume OK" not in df: df["Volume OK"] = False
    if "Change %" not in df: df["Change %"] = None
    qualified = df[df["Price OK"].fillna(False) & df["Volume OK"].fillna(False) & ~df["Status"].astype(str).str.startswith("EXCLUDED")].copy()
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Symbols monitored", len(symbols))
    g2.metric("Price + volume qualified", len(qualified))
    g3.metric("Gap / momentum candidates", int((pd.to_numeric(df["Change %"], errors="coerce") >= 10).sum()))
    g4.metric("Pre-halt heuristic alerts", int(df["Status"].astype(str).str.contains("PRE-HALT").sum()))

    left, mid, right = st.columns([1.25, 1.25, 1])
    with left:
        st.subheader("MOMENTUM / GAP SCANNER")
        show_cols = [c for c in ["Symbol", "Price", "Change %", "Volume", "Float", "Momentum", "Status"] if c in df.columns]
        movers = df.sort_values("Change %", ascending=False, na_position="last")
        st.dataframe(movers[show_cols], hide_index=True, use_container_width=True, height=300,
                     column_config={"Price": st.column_config.NumberColumn(format="$%.2f"), "Change %": st.column_config.NumberColumn(format="%.2f%%"), "Volume": st.column_config.NumberColumn(format="%d")})
        st.caption("Gap-up ranking uses the available change field; 1-minute and 15-minute gap rules need reliable intraday reference data.")
    with mid:
        st.subheader("2-MINUTE MOMENTUM UP / DOWN")
        if histories:
            short_rows = []
            for symbol, h in histories.items():
                if len(h) >= 3:
                    last = float(h["Close"].iloc[-1]); two = float(h["Close"].iloc[-3])
                    move = ((last / two) - 1) * 100 if two else 0
                    short_rows.append({"Symbol": symbol, "2m Change %": move, "Price": last, "2m Volume": int(h["Volume"].tail(2).sum())})
            short_df = pd.DataFrame(short_rows)
            if not short_df.empty:
                up, down = st.columns(2)
                with up:
                    st.markdown("🟢 **TOP UP**")
                    st.dataframe(short_df.sort_values("2m Change %", ascending=False).head(5), hide_index=True, use_container_width=True, height=220)
                with down:
                    st.markdown("🔴 **TOP DOWN**")
                    st.dataframe(short_df.sort_values("2m Change %").head(5), hide_index=True, use_container_width=True, height=220)
        st.subheader("HALT / PRE-HALT WATCH")
        st.warning("Official exchange halt/resumption feed is not connected. The pre-halt label is a volatility/volume heuristic only; it is not an exchange halt prediction.")
        halt_cols = [c for c in ["Symbol", "Price", "1m move %", "Status"] if c in df.columns]
        st.dataframe(df[df["Status"].astype(str).str.contains("HALT|EXCLUDED", case=False)][halt_cols], hide_index=True, use_container_width=True, height=140)
    with right:
        st.subheader("BREAKING NEWS")
        if all_news:
            seen = set()
            for item in all_news:
                key = (item["Symbol"], item["Headline"])
                if key in seen: continue
                seen.add(key)
                st.markdown(f"**{item['Symbol']}** — {item['Headline']}")
                if item["Publisher"]: st.caption(item["Publisher"])
                if item["Link"]: st.markdown(f"[Open story]({item['Link']})")
                st.divider()
        else:
            st.info("No headlines returned for the selected symbols.")

    st.subheader("PRICE ACTION / VOLUME CHARTS")
    chart_symbols = list(histories.keys())[:2]
    chart_cols = st.columns(2)
    for col, symbol in zip(chart_cols, chart_symbols):
        h = histories[symbol].tail(180)
        with col:
            st.markdown(f"**{symbol} — 1-minute candles**")
            fig = go.Figure(data=[go.Candlestick(x=h.index, open=h["Open"], high=h["High"], low=h["Low"], close=h["Close"], name=symbol)])
            fig.add_trace(go.Bar(x=h.index, y=h["Volume"], name="Volume", yaxis="y2", opacity=.35))
            fig.update_layout(height=330, margin=dict(l=5,r=5,t=10,b=5), xaxis_rangeslider_visible=False,
                              yaxis=dict(title="Price"), yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False))
            st.plotly_chart(fig, use_container_width=True)
    if len(chart_symbols) < 2:
        st.caption("Add at least two symbols to fill both chart panels.")

st.divider()
st.caption("Next integration milestones: full-market symbol universe, licensed/approved real-time quotes, official halt feed, catalyst/news provider, and Schwab paper-order adapter. No orders are sent from this dashboard.")
