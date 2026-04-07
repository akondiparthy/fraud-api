import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudLens — Real-Time Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .main { background-color: #0a0e1a; }
    .stApp { background-color: #0a0e1a; }

    /* Header */
    .fraud-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a1040 100%);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .fraud-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #7b2fff, #ff3864);
    }
    .fraud-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .fraud-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #00d4ff;
        margin-top: 4px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .api-badge {
        display: inline-block;
        background: #0d2a1a;
        border: 1px solid #00ff88;
        border-radius: 6px;
        padding: 4px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #00ff88;
        margin-top: 12px;
    }

    /* Metric cards */
    .metric-card {
        background: #0d1b2a;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 20px 24px;
        text-align: center;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #6b7a99;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* Decision badges */
    .badge-approved {
        background: #0d2a1a;
        border: 1px solid #00ff88;
        color: #00ff88;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-review {
        background: #2a1f0d;
        border: 1px solid #ffaa00;
        color: #ffaa00;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-blocked {
        background: #2a0d0d;
        border: 1px solid #ff3864;
        color: #ff3864;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
    }

    /* Score bar */
    .score-bar-wrap {
        background: #1a2535;
        border-radius: 4px;
        height: 8px;
        overflow: hidden;
        margin-top: 6px;
    }

    /* Section headers */
    .section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #00d4ff;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-bottom: 1px solid #1e3a5f;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    /* Result box */
    .result-box {
        background: #0d1b2a;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 20px 24px;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    .css-1d391kg { background-color: #080d18; }
    section[data-testid="stSidebar"] {
        background-color: #080d18;
        border-right: 1px solid #1e3a5f;
    }

    /* Dataframe styling */
    .stDataFrame { border: 1px solid #1e3a5f; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_API_URL = "https://fraud-api-pzkn.onrender.com"
V_COLS = [f"V{i}" for i in range(1, 29)]
ALL_FEATURE_COLS = ["Time", "Amount"] + V_COLS

# ─── Helper functions ───────────────────────────────────────────────────────────
def get_decision_badge(decision):
    badges = {
        "approved": '<span class="badge-approved">APPROVED</span>',
        "review":   '<span class="badge-review">REVIEW</span>',
        "blocked":  '<span class="badge-blocked">BLOCKED</span>',
    }
    return badges.get(decision, decision)

def score_color(score):
    if score < 0.3:   return "#00ff88"
    elif score < 0.7: return "#ffaa00"
    else:             return "#ff3864"

def call_api(api_url, transaction_id, amount, time_sec, v_values):
    payload = {
        "transaction_id": transaction_id,
        "amount": float(amount),
        "time_seconds": float(time_sec),
        **{f"V{i+1}": float(v_values[i]) for i in range(28)}
    }
    try:
        response = requests.post(
            f"{api_url}/predict",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API error {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to API. Check the URL in the sidebar."
    except requests.exceptions.Timeout:
        return None, "Request timed out. The API may be cold-starting (free tier sleeps). Try again in 30 seconds."
    except Exception as e:
        return None, str(e)

def batch_score(api_url, df, progress_bar, status_text):
    results = []
    total = len(df)

    for i, row in df.iterrows():
        txn_id = f"txn_{i:05d}"
        v_vals = [row.get(f"V{j}", 0.0) for j in range(1, 29)]
        amount = row.get("Amount", 1.0)
        time_s = row.get("Time", 0.0)

        result, error = call_api(api_url, txn_id, amount, time_s, v_vals)

        if result:
            results.append({
                "txn_id":           txn_id,
                "amount":           amount,
                "fraud_score":      result["fraud_score"],
                "decision":         result["decision"],
                "top_factor_1":     result["top_risk_factors"][0] if result["top_risk_factors"] else "",
                "top_factor_2":     result["top_risk_factors"][1] if len(result["top_risk_factors"]) > 1 else "",
                "top_factor_3":     result["top_risk_factors"][2] if len(result["top_risk_factors"]) > 2 else "",
                "latency_ms":       result["latency_ms"],
                "explanation":      result["explanation"],
            })
        else:
            results.append({
                "txn_id":      txn_id,
                "amount":      amount,
                "fraud_score": None,
                "decision":    "error",
                "top_factor_1": error,
                "top_factor_2": "",
                "top_factor_3": "",
                "latency_ms":  None,
                "explanation": error,
            })

        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Scoring transaction {i+1} of {total}...")
        time.sleep(0.05)  # small delay to avoid rate limiting

    return pd.DataFrame(results)

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-header">Configuration</p>', unsafe_allow_html=True)
    api_url = st.text_input(
        "API endpoint",
        value=DEFAULT_API_URL,
        help="Your Render deployment URL"
    )

    st.markdown('<p class="section-header" style="margin-top:24px">About</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#6b7a99;line-height:1.8">
    Model: LightGBM<br>
    Dataset: 284,807 transactions<br>
    ROC-AUC: 0.97+<br>
    Explainability: SHAP<br>
    Latency: &lt;25ms p99
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-header" style="margin-top:24px">Decision thresholds</p>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;line-height:2">
    <span style="color:#00ff88">■</span> APPROVED  score &lt; 0.30<br>
    <span style="color:#ffaa00">■</span> REVIEW    score 0.30–0.70<br>
    <span style="color:#ff3864">■</span> BLOCKED   score &gt; 0.70
    </div>
    """, unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="fraud-header">
    <p class="fraud-title">🛡️ FraudLens</p>
    <p class="fraud-subtitle">Real-Time Payment Fraud Detection Dashboard</p>
    <span class="api-badge">API → {api_url}/predict</span>
</div>
""", unsafe_allow_html=True)

# ─── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Single Transaction",
    "Batch CSV Scoring",
    "API Health"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Single Transaction
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-header">Score a single transaction</p>', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("**Transaction details**")
        txn_id = st.text_input("Transaction ID", value="txn_demo_001")
        amount = st.number_input("Amount (€)", min_value=0.01, value=299.99, step=0.01)
        time_sec = st.number_input("Time (seconds since first txn)", value=80000.0)

        st.markdown("**V-features** — anonymized PCA components from the Kaggle dataset")

        use_preset = st.selectbox(
            "Load a preset transaction",
            ["Custom", "Low-risk legitimate", "High-risk fraud pattern", "Edge case (review)"]
        )

        presets = {
            "Low-risk legitimate":    [-1.36, -0.07, 2.54, 1.38, -0.34, 0.46, 0.24, 0.10,
                                        0.36,  0.09, -0.55, -0.62, -0.99, -0.31, 1.47, -0.47,
                                        0.21,  0.03,  0.40,  0.25, -0.02,  0.28, -0.11,  0.07,
                                        0.13, -0.19,  0.13, -0.02],
            "High-risk fraud pattern": [-3.04,  2.55,  3.20, -4.76,  3.30, -1.36,  1.71, -0.49,
                                        -1.51,  2.05, -4.61,  3.49, -3.44, -7.24,  0.58, -2.31,
                                         2.23,  1.40,  0.49, -0.55, -0.10, -0.37,  0.11, -0.31,
                                         0.10,  0.08, -0.25, -0.14],
            "Edge case (review)":      [-1.20,  0.50,  1.80,  0.30, -0.80,  0.20,  0.10, -0.30,
                                         0.50,  0.70, -1.20, -0.40, -0.60, -1.50,  0.80, -0.90,
                                         0.30,  0.10,  0.20,  0.10, -0.05,  0.15, -0.08,  0.04,
                                         0.06, -0.10,  0.07, -0.01],
        }

        if use_preset != "Custom":
            default_v = presets[use_preset]
        else:
            default_v = [0.0] * 28

        v_cols_a = st.columns(4)
        v_values = []
        for i in range(28):
            col_idx = i % 4
            with v_cols_a[col_idx]:
                val = st.number_input(
                    f"V{i+1}",
                    value=default_v[i],
                    format="%.4f",
                    key=f"v{i+1}",
                    label_visibility="collapsed" if i >= 4 else "visible"
                )
                v_values.append(val)

    with col_right:
        st.markdown("**Result**")

        if st.button("Score this transaction", type="primary", use_container_width=True):
            with st.spinner("Calling fraud API..."):
                result, error = call_api(api_url, txn_id, amount, time_sec, v_values)

            if error:
                st.error(f"API Error: {error}")
            else:
                score = result["fraud_score"]
                decision = result["decision"]
                color = score_color(score)

                # Main score display
                st.markdown(f"""
                <div class="result-box" style="border-color:{color}40;margin-bottom:16px">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                        color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase">
                                Fraud score
                            </div>
                            <div style="font-family:'Syne',sans-serif;font-size:3rem;
                                        font-weight:800;color:{color};line-height:1">
                                {score:.1%}
                            </div>
                        </div>
                        <div style="text-align:right">
                            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                        color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase">
                                Decision
                            </div>
                            <div style="font-family:'Syne',sans-serif;font-size:1.6rem;
                                        font-weight:800;color:{color};margin-top:4px">
                                {decision.upper()}
                            </div>
                        </div>
                    </div>
                    <div class="score-bar-wrap" style="margin-top:16px">
                        <div style="height:8px;width:{score*100:.1f}%;
                                    background:{color};border-radius:4px;transition:width 0.6s">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Top risk factors
                st.markdown(f"""
                <div class="result-box" style="margin-bottom:16px">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase;
                                margin-bottom:12px">
                        Top risk factors (SHAP)
                    </div>
                    {"".join([f'''
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                                    color:#00d4ff;min-width:40px">#{j+1}</div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.85rem;
                                    color:#ffffff">{f}</div>
                    </div>''' for j, f in enumerate(result["top_risk_factors"])])}
                </div>
                """, unsafe_allow_html=True)

                # Explanation + latency
                st.markdown(f"""
                <div class="result-box">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                                color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase;
                                margin-bottom:8px">Explanation</div>
                    <div style="font-family:'Syne',sans-serif;font-size:0.9rem;
                                color:#c8d4e8;line-height:1.6">
                        {result["explanation"]}
                    </div>
                    <div style="margin-top:12px;font-family:'JetBrains Mono',monospace;
                                font-size:0.7rem;color:#6b7a99">
                        Latency: {result["latency_ms"]}ms &nbsp;|&nbsp;
                        Model: {result["model_version"]} &nbsp;|&nbsp;
                        {result["evaluated_at"][:19].replace("T"," ")} UTC
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="result-box" style="text-align:center;padding:60px 24px">
                <div style="font-size:2.5rem;margin-bottom:12px">🛡️</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                            color:#6b7a99;letter-spacing:1.5px">
                    SELECT A PRESET OR ENTER VALUES<br>THEN CLICK SCORE
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Batch CSV Scoring
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-header">Upload CSV — score all transactions</p>', unsafe_allow_html=True)

    col_info, col_upload = st.columns([1, 1], gap="large")

    with col_info:
        st.markdown("""
        <div class="result-box">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase;
                        margin-bottom:12px">Required CSV columns</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                        color:#c8d4e8;line-height:2">
                Time — seconds elapsed<br>
                Amount — transaction amount<br>
                V1 through V28 — PCA features<br>
                Class — optional (0=legit, 1=fraud)
            </div>
            <div style="margin-top:16px;font-family:'JetBrains Mono',monospace;
                        font-size:0.65rem;color:#6b7a99">
                Tip: Use a sample from your creditcard.csv.<br>
                Max 50 rows recommended on free tier.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_upload:
        uploaded_file = st.file_uploader(
            "Drop your CSV here",
            type=["csv"],
            help="Must contain Time, Amount, V1–V28 columns"
        )

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df_raw):,} transactions — {list(df_raw.columns[:5])}...")

        max_rows = st.slider("How many rows to score?", 1, min(50, len(df_raw)), min(10, len(df_raw)))
        df_sample = df_raw.head(max_rows).reset_index(drop=True)

        if st.button("Score all transactions", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            df_results = batch_score(api_url, df_sample, progress_bar, status_text)

            progress_bar.empty()
            status_text.empty()

            st.success(f"Scored {len(df_results)} transactions!")

            # ── Summary metrics ──
            valid = df_results[df_results["decision"] != "error"]
            if len(valid) > 0:
                n_approved = (valid["decision"] == "approved").sum()
                n_review   = (valid["decision"] == "review").sum()
                n_blocked  = (valid["decision"] == "blocked").sum()
                avg_score  = valid["fraud_score"].mean()
                avg_lat    = valid["latency_ms"].mean()

                m1, m2, m3, m4, m5 = st.columns(5)
                metrics = [
                    (m1, str(len(valid)),        "#ffffff", "Total scored"),
                    (m2, str(n_approved),         "#00ff88", "Approved"),
                    (m3, str(n_review),           "#ffaa00", "Review"),
                    (m4, str(n_blocked),          "#ff3864", "Blocked"),
                    (m5, f"{avg_score:.1%}",      "#00d4ff", "Avg fraud score"),
                ]
                for col, val, color, label in metrics:
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <p class="metric-value" style="color:{color}">{val}</p>
                            <p class="metric-label">{label}</p>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── Charts ──
                chart1, chart2 = st.columns(2)

                with chart1:
                    fig, ax = plt.subplots(figsize=(5, 3.5))
                    fig.patch.set_facecolor('#0d1b2a')
                    ax.set_facecolor('#0d1b2a')

                    scores = valid["fraud_score"].values
                    ax.hist(scores[scores < 0.3],  bins=15, color='#00ff88', alpha=0.85, label='Approved')
                    ax.hist(scores[(scores >= 0.3) & (scores < 0.7)], bins=10, color='#ffaa00', alpha=0.85, label='Review')
                    ax.hist(scores[scores >= 0.7], bins=10, color='#ff3864', alpha=0.85, label='Blocked')
                    ax.axvline(0.3, color='#ffffff', linestyle='--', linewidth=0.8, alpha=0.4)
                    ax.axvline(0.7, color='#ffffff', linestyle='--', linewidth=0.8, alpha=0.4)

                    ax.set_xlabel("Fraud score", color='#6b7a99', fontsize=9)
                    ax.set_ylabel("Count", color='#6b7a99', fontsize=9)
                    ax.tick_params(colors='#6b7a99', labelsize=8)
                    for spine in ax.spines.values():
                        spine.set_edgecolor('#1e3a5f')
                    ax.legend(fontsize=8, facecolor='#0d1b2a', edgecolor='#1e3a5f', labelcolor='white')
                    ax.set_title("Score distribution", color='#c8d4e8', fontsize=10, pad=10)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()

                with chart2:
                    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
                    fig2.patch.set_facecolor('#0d1b2a')
                    ax2.set_facecolor('#0d1b2a')

                    decision_counts = valid["decision"].value_counts()
                    colors_map = {"approved": "#00ff88", "review": "#ffaa00", "blocked": "#ff3864"}
                    bar_colors = [colors_map.get(d, "#6b7a99") for d in decision_counts.index]

                    bars = ax2.bar(decision_counts.index, decision_counts.values,
                                   color=bar_colors, alpha=0.9, edgecolor='#0d1b2a', linewidth=1.5)
                    for bar, val in zip(bars, decision_counts.values):
                        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                                 str(val), ha='center', color='white', fontsize=10, fontweight='bold')

                    ax2.set_ylabel("Count", color='#6b7a99', fontsize=9)
                    ax2.tick_params(colors='#6b7a99', labelsize=9)
                    for spine in ax2.spines.values():
                        spine.set_edgecolor('#1e3a5f')
                    ax2.set_title("Decision breakdown", color='#c8d4e8', fontsize=10, pad=10)
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()

                # ── Results table ──
                st.markdown('<p class="section-header" style="margin-top:8px">All results</p>', unsafe_allow_html=True)

                display_df = valid[["txn_id", "amount", "fraud_score", "decision",
                                    "top_factor_1", "top_factor_2", "latency_ms"]].copy()
                display_df.columns = ["Transaction", "Amount (€)", "Fraud Score",
                                      "Decision", "Top Factor 1", "Top Factor 2", "Latency (ms)"]
                display_df["Fraud Score"] = display_df["Fraud Score"].apply(lambda x: f"{x:.4f}")
                display_df["Amount (€)"] = display_df["Amount (€)"].apply(lambda x: f"{x:.2f}")

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ── Download button ──
                csv_out = df_results.to_csv(index=False)
                st.download_button(
                    label="Download full results as CSV",
                    data=csv_out,
                    file_name=f"fraud_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — API Health
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-header">API health check</p>', unsafe_allow_html=True)

    if st.button("Check API status", type="primary"):
        with st.spinner("Pinging API..."):
            try:
                start = time.time()
                r = requests.get(f"{api_url}/health", timeout=15)
                latency = (time.time() - start) * 1000

                if r.status_code == 200:
                    data = r.json()
                    st.markdown(f"""
                    <div class="result-box" style="border-color:#00ff8840">
                        <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                                    font-weight:800;color:#00ff88;margin-bottom:16px">
                            API is online
                        </div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                                    color:#c8d4e8;line-height:2.2">
                            Status: {data.get("status", "unknown")}<br>
                            Model version: {data.get("model_version", "unknown")}<br>
                            Response time: {latency:.0f}ms<br>
                            Endpoint: {api_url}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"API returned status {r.status_code}")
            except Exception as e:
                st.markdown(f"""
                <div class="result-box" style="border-color:#ff386440">
                    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;
                                font-weight:800;color:#ff3864;margin-bottom:12px">
                        Cannot reach API
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#6b7a99">
                        {str(e)}<br><br>
                        The free Render tier sleeps after 15 minutes of inactivity.<br>
                        Wait 30 seconds and try again — it will wake up automatically.
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-box" style="margin-top:16px">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                    color:#6b7a99;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px">
            API endpoints
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#c8d4e8;line-height:2.2">
            GET  {api_url}/health<br>
            POST {api_url}/predict<br>
            GET  {api_url}/docs &nbsp;&nbsp;← Interactive docs
        </div>
    </div>
    """, unsafe_allow_html=True)
    