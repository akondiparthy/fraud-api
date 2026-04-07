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

st.set_page_config(
    page_title="FraudLens",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Fraunces:ital,wght@0,300;0,600;1,300&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #f7f6f2; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    .fl-header { display:flex;align-items:flex-end;justify-content:space-between;padding:32px 40px 28px;background:#ffffff;border-radius:16px;border:1px solid #e8e5de;margin-bottom:20px;position:relative;overflow:hidden; }
    .fl-header::after { content:'';position:absolute;bottom:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#2563eb 0%,#7c3aed 50%,#db2777 100%); }
    .fl-logo { font-family:'Fraunces',serif;font-size:2.4rem;font-weight:600;color:#111827;letter-spacing:-1px;margin:0;line-height:1; }
    .fl-logo span { color:#2563eb; }
    .fl-tagline { font-family:'DM Mono',monospace;font-size:0.7rem;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase;margin-top:6px; }
    .fl-live-badge { display:flex;align-items:center;gap:7px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:100px;padding:6px 14px;font-family:'DM Mono',monospace;font-size:0.68rem;color:#16a34a;font-weight:500; }
    .fl-live-dot { width:7px;height:7px;background:#16a34a;border-radius:50%;animation:pulse-dot 2s infinite; }
    @keyframes pulse-dot { 0%,100%{opacity:1}50%{opacity:0.4} }
    .fl-card { background:#ffffff;border:1px solid #e8e5de;border-radius:14px;padding:24px 28px;margin-bottom:16px; }
    .fl-card-accent-blue  { border-top:3px solid #2563eb; }
    .fl-card-accent-green { border-top:3px solid #16a34a; }
    .fl-card-accent-amber { border-top:3px solid #d97706; }
    .fl-card-accent-red   { border-top:3px solid #dc2626; }
    .fl-label { font-family:'DM Mono',monospace;font-size:0.65rem;color:#9ca3af;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px; }
    .fl-metric { background:#ffffff;border:1px solid #e8e5de;border-radius:12px;padding:18px 22px;text-align:center; }
    .fl-metric-val { font-family:'Fraunces',serif;font-size:2.2rem;font-weight:600;line-height:1;margin-bottom:4px; }
    .fl-metric-lbl { font-family:'DM Mono',monospace;font-size:0.62rem;color:#9ca3af;letter-spacing:1.5px;text-transform:uppercase; }
    .chip-approved { display:inline-block;background:#f0fdf4;border:1px solid #bbf7d0;color:#16a34a;padding:4px 12px;border-radius:100px;font-family:'DM Mono',monospace;font-size:0.68rem;font-weight:500; }
    .chip-review   { display:inline-block;background:#fffbeb;border:1px solid #fde68a;color:#d97706;padding:4px 12px;border-radius:100px;font-family:'DM Mono',monospace;font-size:0.68rem;font-weight:500; }
    .chip-blocked  { display:inline-block;background:#fef2f2;border:1px solid #fecaca;color:#dc2626;padding:4px 12px;border-radius:100px;font-family:'DM Mono',monospace;font-size:0.68rem;font-weight:500; }
    .fl-score-big { font-family:'Fraunces',serif;font-size:3.8rem;font-weight:600;line-height:1;letter-spacing:-2px; }
    .fl-score-track { height:6px;background:#f3f4f6;border-radius:99px;overflow:hidden;margin:12px 0; }
    .fl-score-fill { height:100%;border-radius:99px;transition:width 0.5s cubic-bezier(0.4,0,0.2,1); }
    .fl-factor-row { display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #f3f4f6; }
    .fl-factor-row:last-child { border-bottom:none; }
    .fl-factor-rank { font-family:'DM Mono',monospace;font-size:0.7rem;color:#9ca3af;min-width:20px; }
    .fl-factor-name { font-family:'DM Mono',monospace;font-size:0.85rem;color:#374151;font-weight:500;flex:1; }
    .fl-factor-bar-wrap { width:80px;height:4px;background:#f3f4f6;border-radius:99px;overflow:hidden; }
    .fl-empty { text-align:center;padding:64px 24px;color:#9ca3af; }
    .fl-empty-icon { font-size:2.5rem;margin-bottom:12px;opacity:0.5; }
    .fl-empty-text { font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:1.5px;text-transform:uppercase;line-height:2; }
    section[data-testid="stSidebar"] { background:#ffffff;border-right:1px solid #e8e5de; }
    .stTabs [data-baseweb="tab-list"] { background:#ffffff;border-radius:10px;border:1px solid #e8e5de;padding:4px;gap:2px; }
    .stTabs [data-baseweb="tab"] { border-radius:8px;font-family:'DM Sans',sans-serif;font-size:0.85rem;font-weight:500;color:#6b7280;padding:8px 20px; }
    .stTabs [aria-selected="true"] { background:#2563eb !important;color:white !important; }
    .stButton > button { background:#2563eb;color:white;border:none;border-radius:8px;font-family:'DM Sans',sans-serif;font-weight:500;padding:10px 24px;font-size:0.9rem;transition:all 0.2s; }
    .stButton > button:hover { background:#1d4ed8;transform:translateY(-1px);box-shadow:0 4px 12px rgba(37,99,235,0.25); }
    .fl-explanation { background:#f8fafc;border-left:3px solid #2563eb;border-radius:0 8px 8px 0;padding:14px 18px;font-family:'DM Sans',sans-serif;font-size:0.9rem;color:#374151;line-height:1.7;margin-top:12px; }
    .fl-endpoint { background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;padding:12px 16px;font-family:'DM Mono',monospace;font-size:0.75rem;color:#374151;line-height:2.2;margin-top:8px; }
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

DEFAULT_API_URL = "https://fraud-api-pzkn.onrender.com"

def score_color(s): return "#16a34a" if s<0.3 else "#d97706" if s<0.7 else "#dc2626"
def score_bg(s):    return "#f0fdf4" if s<0.3 else "#fffbeb" if s<0.7 else "#fef2f2"
def decision_chip(d):
    chips = {"approved":'<span class="chip-approved">Approved</span>',
             "review":'<span class="chip-review">Review</span>',
             "blocked":'<span class="chip-blocked">Blocked</span>'}
    return chips.get(d, d)

def call_api(api_url, txn_id, amount, time_sec, v_values):
    payload = {"transaction_id":txn_id,"amount":float(amount),"time_seconds":float(time_sec),
               **{f"V{i+1}":float(v_values[i]) for i in range(28)}}
    try:
        r = requests.post(f"{api_url}/predict", json=payload, timeout=30)
        return (r.json(), None) if r.status_code==200 else (None, f"API error {r.status_code}")
    except requests.exceptions.ConnectionError: return None,"Cannot connect to API."
    except requests.exceptions.Timeout: return None,"Timeout. Try again in 30s."
    except Exception as e: return None, str(e)

def batch_score(api_url, df, pb, st_txt):
    results=[]
    for i,row in df.iterrows():
        v_vals=[row.get(f"V{j}",0.0) for j in range(1,29)]
        res,err=call_api(api_url,f"txn_{i:05d}",row.get("Amount",1.0),row.get("Time",0.0),v_vals)
        if res:
            results.append({"Transaction":f"txn_{i:05d}","Amount (€)":f"{row.get('Amount',0):.2f}",
                "Fraud Score":res["fraud_score"],"Decision":res["decision"],
                "Top Factor 1":res["top_risk_factors"][0] if res["top_risk_factors"] else "",
                "Top Factor 2":res["top_risk_factors"][1] if len(res["top_risk_factors"])>1 else "",
                "Latency (ms)":res["latency_ms"],"Explanation":res["explanation"]})
        else:
            results.append({"Transaction":f"txn_{i:05d}","Amount (€)":"","Fraud Score":None,
                "Decision":"error","Top Factor 1":err,"Top Factor 2":"","Latency (ms)":None,"Explanation":err})
        pb.progress((i+1)/len(df))
        st_txt.markdown(f'<p style="font-family:DM Mono,monospace;font-size:0.75rem;color:#6b7280">Scoring {i+1} of {len(df)}…</p>',unsafe_allow_html=True)
        time.sleep(0.05)
    return pd.DataFrame(results)

with st.sidebar:
    st.markdown('<p class="fl-label">Configuration</p>',unsafe_allow_html=True)
    api_url=st.text_input("API endpoint",value=DEFAULT_API_URL)
    st.markdown('<div style="height:20px"></div>',unsafe_allow_html=True)
    st.markdown('<p class="fl-label">Model details</p>',unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.72rem;color:#6b7280;line-height:2.2">Algorithm &nbsp;&nbsp; LightGBM<br>Dataset &nbsp;&nbsp;&nbsp;&nbsp; 284,807 rows<br>ROC-AUC &nbsp;&nbsp;&nbsp; 0.97+<br>Explainer &nbsp;&nbsp; SHAP<br>Latency &nbsp;&nbsp;&nbsp;&nbsp; &lt;25ms p99</div>',unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>',unsafe_allow_html=True)
    st.markdown('<p class="fl-label">Decision thresholds</p>',unsafe_allow_html=True)
    st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.72rem;line-height:2.4"><span style="color:#16a34a;font-weight:600">●</span>&nbsp; Approved &nbsp; score &lt; 0.30<br><span style="color:#d97706;font-weight:600">●</span>&nbsp; Review &nbsp;&nbsp;&nbsp; 0.30–0.70<br><span style="color:#dc2626;font-weight:600">●</span>&nbsp; Blocked &nbsp;&nbsp; score &gt; 0.70</div>',unsafe_allow_html=True)

st.markdown(f'<div class="fl-header"><div><p class="fl-logo">Fraud<span>Lens</span></p><p class="fl-tagline">Real-time payment fraud detection</p></div><div class="fl-live-badge"><div class="fl-live-dot"></div>API live — {api_url.replace("https://","")}</div></div>',unsafe_allow_html=True)

tab1,tab2,tab3=st.tabs(["Single Transaction","Batch CSV Scoring","API Health"])

with tab1:
    col_left,col_right=st.columns([1.05,0.95],gap="large")
    with col_left:
        st.markdown('<div class="fl-card fl-card-accent-blue">',unsafe_allow_html=True)
        st.markdown('<p class="fl-label">Transaction details</p>',unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            txn_id=st.text_input("Transaction ID",value="txn_demo_001")
            amount=st.number_input("Amount (€)",min_value=0.01,value=299.99,step=0.01)
        with c2:
            time_sec=st.number_input("Time (seconds)",value=80000.0)
            preset=st.selectbox("Load preset",["Custom","Low-risk legitimate","High-risk fraud","Edge case (review)"])
        presets={
            "Low-risk legitimate":[-1.36,-0.07,2.54,1.38,-0.34,0.46,0.24,0.10,0.36,0.09,-0.55,-0.62,-0.99,-0.31,1.47,-0.47,0.21,0.03,0.40,0.25,-0.02,0.28,-0.11,0.07,0.13,-0.19,0.13,-0.02],
            "High-risk fraud":[-3.04,2.55,3.20,-4.76,3.30,-1.36,1.71,-0.49,-1.51,2.05,-4.61,3.49,-3.44,-7.24,0.58,-2.31,2.23,1.40,0.49,-0.55,-0.10,-0.37,0.11,-0.31,0.10,0.08,-0.25,-0.14],
            "Edge case (review)":[-1.20,0.50,1.80,0.30,-0.80,0.20,0.10,-0.30,0.50,0.70,-1.20,-0.40,-0.60,-1.50,0.80,-0.90,0.30,0.10,0.20,0.10,-0.05,0.15,-0.08,0.04,0.06,-0.10,0.07,-0.01],
        }
        default_v=presets.get(preset,[0.0]*28)
        st.markdown('<p class="fl-label" style="margin-top:16px">V-features (V1–V28)</p>',unsafe_allow_html=True)
        v_values=[]
        rows=[st.columns(7) for _ in range(4)]
        for i in range(28):
            with rows[i//7][i%7]:
                v_values.append(st.number_input(f"V{i+1}",value=default_v[i],format="%.3f",key=f"sv{i+1}",label_visibility="collapsed"))
        st.markdown('</div>',unsafe_allow_html=True)
        run=st.button("Score this transaction",type="primary",use_container_width=True)
    with col_right:
        st.markdown('<p class="fl-label">Result</p>',unsafe_allow_html=True)
        if run:
            with st.spinner(""):
                result,error=call_api(api_url,txn_id,amount,time_sec,v_values)
            if error:
                st.error(f"Error: {error}")
            else:
                score=result["fraud_score"]; decision=result["decision"]
                color=score_color(score); bg=score_bg(score)
                st.markdown(f'<div class="fl-card" style="border-top:3px solid {color};background:{bg}"><div style="display:flex;justify-content:space-between;align-items:flex-start"><div><p class="fl-label">Fraud probability</p><p class="fl-score-big" style="color:{color}">{score:.1%}</p></div><div style="text-align:right;padding-top:4px"><p class="fl-label">Decision</p><div style="margin-top:6px">{decision_chip(decision)}</div></div></div><div class="fl-score-track"><div class="fl-score-fill" style="width:{score*100:.1f}%;background:{color}"></div></div><div style="display:flex;justify-content:space-between;font-family:DM Mono,monospace;font-size:0.65rem;color:#9ca3af"><span>0%</span><span>30%</span><span>70%</span><span>100%</span></div></div>',unsafe_allow_html=True)
                factors=result["top_risk_factors"]; widths=[100,65,40]
                factor_rows="".join([f'<div class="fl-factor-row"><span class="fl-factor-rank">#{j+1}</span><span class="fl-factor-name">{f}</span><div class="fl-factor-bar-wrap"><div style="height:100%;width:{widths[j]}%;background:{color};border-radius:99px"></div></div></div>' for j,f in enumerate(factors)])
                st.markdown(f'<div class="fl-card" style="margin-top:0"><p class="fl-label">Top SHAP risk factors</p>{factor_rows}</div>',unsafe_allow_html=True)
                st.markdown(f'<div class="fl-card" style="margin-top:0"><p class="fl-label">Plain-English explanation</p><div class="fl-explanation">{result["explanation"]}</div><div style="margin-top:14px;display:flex;gap:20px;font-family:DM Mono,monospace;font-size:0.65rem;color:#9ca3af"><span>Latency: {result["latency_ms"]}ms</span><span>Model: {result["model_version"]}</span><span>{result["evaluated_at"][:19].replace("T"," ")} UTC</span></div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="fl-card" style="margin-top:0"><div class="fl-empty"><div class="fl-empty-icon">🛡️</div><p class="fl-empty-text">Choose a preset or enter values<br>then click Score</p></div></div>',unsafe_allow_html=True)

with tab2:
    col_guide,col_drop=st.columns([1,1],gap="large")
    with col_guide:
        st.markdown('<div class="fl-card fl-card-accent-blue"><p class="fl-label">Required CSV columns</p><div style="font-family:DM Mono,monospace;font-size:0.75rem;color:#374151;line-height:2.4"><span style="color:#2563eb">Time</span> &nbsp;&nbsp;&nbsp; seconds elapsed<br><span style="color:#2563eb">Amount</span> &nbsp; transaction amount<br><span style="color:#2563eb">V1–V28</span> &nbsp; PCA features<br><span style="color:#9ca3af">Class</span> &nbsp;&nbsp; optional ground truth</div><div style="margin-top:16px;padding:10px 14px;background:#f8fafc;border-radius:8px;font-family:DM Mono,monospace;font-size:0.68rem;color:#6b7280;line-height:1.8">Tip: use a slice of creditcard.csv<br>Max 50 rows on free tier</div></div>',unsafe_allow_html=True)
    with col_drop:
        uploaded=st.file_uploader("Upload CSV",type=["csv"])
    if uploaded:
        df_raw=pd.read_csv(uploaded)
        st.success(f"Loaded {len(df_raw):,} transactions")
        max_rows=st.slider("Rows to score",1,min(50,len(df_raw)),min(10,len(df_raw)))
        df_sample=df_raw.head(max_rows).reset_index(drop=True)
        if st.button("Score all transactions",type="primary",use_container_width=True):
            pb=st.progress(0); st_txt=st.empty()
            df_res=batch_score(api_url,df_sample,pb,st_txt)
            pb.empty(); st_txt.empty()
            valid=df_res[df_res["Decision"]!="error"]
            if len(valid)>0:
                n_app=(valid["Decision"]=="approved").sum()
                n_rev=(valid["Decision"]=="review").sum()
                n_blk=(valid["Decision"]=="blocked").sum()
                avg_s=valid["Fraud Score"].mean()
                m1,m2,m3,m4,m5=st.columns(5)
                for col,val,color,label in [(m1,str(len(valid)),"#111827","Scored"),(m2,str(n_app),"#16a34a","Approved"),(m3,str(n_rev),"#d97706","Review"),(m4,str(n_blk),"#dc2626","Blocked"),(m5,f"{avg_s:.1%}","#2563eb","Avg score")]:
                    with col:
                        st.markdown(f'<div class="fl-metric"><div class="fl-metric-val" style="color:{color}">{val}</div><div class="fl-metric-lbl">{label}</div></div>',unsafe_allow_html=True)
                st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)
                ch1,ch2=st.columns(2)
                plt.rcParams.update({'font.family':'sans-serif','axes.spines.top':False,'axes.spines.right':False})
                with ch1:
                    fig,ax=plt.subplots(figsize=(5,3.2))
                    fig.patch.set_facecolor('#ffffff'); ax.set_facecolor('#ffffff')
                    scores=valid["Fraud Score"].dropna().values
                    ax.hist(scores[scores<0.3],bins=12,color='#16a34a',alpha=0.8,label='Approved',edgecolor='white')
                    ax.hist(scores[(scores>=0.3)&(scores<0.7)],bins=8,color='#d97706',alpha=0.8,label='Review',edgecolor='white')
                    ax.hist(scores[scores>=0.7],bins=8,color='#dc2626',alpha=0.8,label='Blocked',edgecolor='white')
                    ax.axvline(0.3,color='#e5e7eb',linewidth=1,linestyle='--')
                    ax.axvline(0.7,color='#e5e7eb',linewidth=1,linestyle='--')
                    ax.set_xlabel("Fraud score",fontsize=9,color='#6b7280')
                    ax.set_ylabel("Count",fontsize=9,color='#6b7280')
                    ax.tick_params(colors='#9ca3af',labelsize=8)
                    for sp in ['left','bottom']: ax.spines[sp].set_color('#e5e7eb')
                    ax.legend(fontsize=8,framealpha=0,labelcolor='#374151')
                    ax.set_title("Score distribution",fontsize=10,color='#111827',fontweight='600',pad=12)
                    plt.tight_layout(); st.pyplot(fig); plt.close()
                with ch2:
                    fig2,ax2=plt.subplots(figsize=(5,3.2))
                    fig2.patch.set_facecolor('#ffffff'); ax2.set_facecolor('#ffffff')
                    dc=valid["Decision"].value_counts()
                    cm={"approved":"#16a34a","review":"#d97706","blocked":"#dc2626"}
                    bars=ax2.bar(dc.index,dc.values,color=[cm.get(d,"#6b7280") for d in dc.index],alpha=0.85,edgecolor='white',linewidth=2,width=0.5,zorder=3)
                    for bar,v in zip(bars,dc.values):
                        ax2.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,str(v),ha='center',color='#374151',fontsize=11,fontweight='600')
                    ax2.set_ylabel("Count",fontsize=9,color='#6b7280')
                    ax2.tick_params(colors='#9ca3af',labelsize=9)
                    ax2.set_ylim(0,dc.max()*1.25)
                    ax2.yaxis.grid(True,color='#f3f4f6',zorder=0)
                    for sp in ['left','bottom']: ax2.spines[sp].set_color('#e5e7eb')
                    ax2.set_title("Decision breakdown",fontsize=10,color='#111827',fontweight='600',pad=12)
                    plt.tight_layout(); st.pyplot(fig2); plt.close()
                st.markdown('<p class="fl-label" style="margin-top:8px">All results</p>',unsafe_allow_html=True)
                display=valid[["Transaction","Amount (€)","Fraud Score","Decision","Top Factor 1","Top Factor 2","Latency (ms)"]].copy()
                display["Fraud Score"]=display["Fraud Score"].apply(lambda x:f"{x:.4f}")
                st.dataframe(display,use_container_width=True,hide_index=True)
                st.download_button("Download results as CSV",data=df_res.to_csv(index=False),file_name=f"fraud_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",mime="text/csv",use_container_width=True)

with tab3:
    st.markdown('<p class="fl-label">Check your API is running</p>',unsafe_allow_html=True)
    if st.button("Ping API",type="primary"):
        with st.spinner("Checking…"):
            try:
                t0=time.time()
                r=requests.get(f"{api_url}/health",timeout=20)
                latency=(time.time()-t0)*1000
                if r.status_code==200:
                    d=r.json()
                    st.markdown(f'<div class="fl-card fl-card-accent-green"><div style="display:flex;align-items:center;gap:10px;margin-bottom:16px"><div style="width:10px;height:10px;background:#16a34a;border-radius:50%"></div><span style="font-family:DM Sans,sans-serif;font-weight:600;font-size:1.1rem;color:#111827">API is online</span></div><div style="font-family:DM Mono,monospace;font-size:0.75rem;color:#374151;line-height:2.4">Status &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {d.get("status","—")}<br>Model version &nbsp; {d.get("model_version","—")}<br>Response time &nbsp; {latency:.0f}ms<br>Endpoint &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {api_url}</div></div>',unsafe_allow_html=True)
                else:
                    st.error(f"API returned {r.status_code}")
            except Exception as e:
                st.markdown(f'<div class="fl-card fl-card-accent-red"><div style="font-family:DM Sans,sans-serif;font-weight:600;font-size:1.1rem;color:#dc2626;margin-bottom:10px">Cannot reach API</div><div style="font-family:DM Mono,monospace;font-size:0.72rem;color:#6b7280;line-height:1.8">{str(e)}<br><br>Free tier sleeps after 15 min. Wait 30s and retry.</div></div>',unsafe_allow_html=True)
    st.markdown(f'<div class="fl-card" style="margin-top:0"><p class="fl-label">Available endpoints</p><div class="fl-endpoint">GET &nbsp; {api_url}/health<br>POST {api_url}/predict<br>GET &nbsp; {api_url}/docs</div></div>',unsafe_allow_html=True)