import streamlit as st
import requests
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Decision System",
    page_icon="📦",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e8e8;
}

.main { background-color: #0d0d0d; }

h1 { 
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.4rem !important;
    letter-spacing: 0.08em;
    color: #e8e8e8 !important;
    border-bottom: 1px solid #2a2a2a;
    padding-bottom: 0.8rem;
    margin-bottom: 1.5rem !important;
}

.metric-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}

.metric-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    color: #666;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #e8e8e8;
}

.metric-value.accent { color: #ff4444; }
.metric-value.green { color: #00cc88; }
.metric-value.yellow { color: #ffcc00; }

.action-box {
    background: #0a0a0a;
    border-left: 3px solid #ff4444;
    padding: 1rem 1.4rem;
    border-radius: 0 4px 4px 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    margin-top: 1rem;
    color: #e8e8e8;
}

.action-box.ok {
    border-left-color: #00cc88;
}

.action-box.warning {
    border-left-color: #ffcc00;
}

.risk-bar-container {
    background: #1a1a1a;
    border-radius: 2px;
    height: 6px;
    margin-top: 0.6rem;
    overflow: hidden;
}

.risk-bar {
    height: 100%;
    border-radius: 2px;
    transition: width 0.5s ease;
}

.tag {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    padding: 0.2rem 0.5rem;
    border-radius: 2px;
    margin-right: 0.4rem;
    text-transform: uppercase;
}

.tag-urgent { background: #3a0000; color: #ff4444; border: 1px solid #ff4444; }
.tag-ok { background: #003a1a; color: #00cc88; border: 1px solid #00cc88; }
.tag-warning { background: #3a3000; color: #ffcc00; border: 1px solid #ffcc00; }

.divider {
    border: none;
    border-top: 1px solid #1e1e1e;
    margin: 1.5rem 0;
}

.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    background: #e8e8e8 !important;
    color: #0d0d0d !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: #ffffff !important;
}

.stNumberInput > div > div > input {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    color: #e8e8e8 !important;
    border-radius: 2px !important;
}

label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #666 !important;
}

.footer {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #333;
    text-align: center;
    margin-top: 3rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 📦 SUPPLY CHAIN / DECISION SYSTEM")
st.markdown(
    "<p style='color:#555; font-size:0.8rem; font-family:IBM Plex Mono,monospace; "
    "letter-spacing:0.06em; margin-top:-1rem;'>LightGBM · MAPE 13.74% · 1,115 stores</p>",
    unsafe_allow_html=True
)

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    store_id = st.number_input("Store ID", min_value=1, max_value=1115, value=1, step=1)
with col2:
    current_stock = st.number_input("Current Stock (units)", min_value=0, value=5000, step=500)

st.markdown("")
run = st.button("▶  RUN DECISION ENGINE")

# ── API Call & Results ────────────────────────────────────────────────────────
if run:
    with st.spinner(""):
        try:
            resp = requests.post(
                "http://localhost:8000/predict",
                json={"store_id": int(store_id), "current_stock": float(current_stock)},
                timeout=10,
            )
            data = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("⚠ API not reachable. Make sure the FastAPI server or Docker container is running on port 8000.")
            st.stop()

    # ── Determine risk level ──────────────────────────────────────────────
    risk = data["stockout_risk"]
    if risk >= 0.6:
        risk_color = "#ff4444"
        risk_label = "HIGH"
        tag_class = "tag-urgent"
        action_class = "action-box"
    elif risk >= 0.3:
        risk_color = "#ffcc00"
        risk_label = "MODERATE"
        tag_class = "tag-warning"
        action_class = "action-box warning"
    else:
        risk_color = "#00cc88"
        risk_label = "LOW"
        tag_class = "tag-ok"
        action_class = "action-box ok"

    reorder_color = "accent" if data["reorder_recommended"] else "green"
    overstock_color = "yellow" if data["overstock_flag"] else "green"

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Metrics row ───────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">7-Day Forecast</div>
            <div class="metric-value">{int(data['forecast_7d']):,}</div>
            <div style="color:#555; font-size:0.7rem; font-family:'IBM Plex Mono',monospace; margin-top:0.3rem;">units</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Reorder Qty</div>
            <div class="metric-value {'accent' if data['reorder_recommended'] else 'green'}">{int(data['reorder_quantity']):,}</div>
            <div style="color:#555; font-size:0.7rem; font-family:'IBM Plex Mono',monospace; margin-top:0.3rem;">units</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Stockout Risk</div>
            <div class="metric-value" style="color:{risk_color}">{risk*100:.0f}%</div>
            <div class="risk-bar-container">
                <div class="risk-bar" style="width:{risk*100:.0f}%; background:{risk_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Status tags ───────────────────────────────────────────────────────
    reorder_tag = '<span class="tag tag-urgent">REORDER</span>' if data["reorder_recommended"] else '<span class="tag tag-ok">STOCKED</span>'
    overstock_tag = '<span class="tag tag-warning">OVERSTOCK</span>' if data["overstock_flag"] else ""
    risk_tag = f'<span class="tag {tag_class}">RISK: {risk_label}</span>'

    st.markdown(f"<div style='margin: 0.5rem 0'>{reorder_tag}{risk_tag}{overstock_tag}</div>", unsafe_allow_html=True)

    # ── Action string ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="{action_class}">
        <span style="color:#555; font-size:0.65rem; letter-spacing:0.1em;">ACTION →</span><br>
        {data['action']}
    </div>
    """, unsafe_allow_html=True)

    # ── Raw JSON expander ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("RAW JSON RESPONSE"):
        st.code(json.dumps(data, indent=2), language="json")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='footer'>ROSSMANN STORE SALES · WALK-FORWARD CV · LGBM TUNED · 64% MAPE IMPROVEMENT</div>",
    unsafe_allow_html=True
)
