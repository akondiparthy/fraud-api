import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(
    page_title="FraudLens — Payment Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F6F9FC; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }

    section[data-testid="stSidebar"] { background: #0A2540; border-right: none; }
    section[data-testid="stSidebar"] * { color: #C8D8E8 !important; }
    section[data-testid="stSidebar"] .fl-sidebar-logo { font-family:'Plus Jakarta Sans',sans-serif;font-size:1.3rem;font-weight:800;color:#FFFFFF !important;letter-spacing:-0.5px;padding:4px 0 20px;border-bottom:1px solid #1A3A5C;margin-bottom:20px; }
    section[data-testid="stSidebar"] .fl-sidebar-logo span { color:#635BFF !important; }
    section[data-testid="stSidebar"] .fl-slabel { font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#4A6A8A !important;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px; }
    section[data-testid="stSidebar"] .fl-srow { font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#A0BACE !important;line-height:2.3; }
    section[data-testid="stSidebar"] .fl-srow b { color:#FFFFFF !important; }
    section[data-testid="stSidebar"] .fl-nav-item { display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:8px;margin-bottom:4px;cursor:pointer;font-family:'Plus Jakarta Sans',sans-serif;font-size:0.85rem;font-weight:500;color:#A0BACE !important; }
    section[data-testid="stSidebar"] .fl-nav-item:hover { background:#1A3A5C; }
    section[data-testid="stSidebar"] .fl-stat-box { background:#1A3A5C;border-radius:10px;padding:14px 16px;margin-bottom:8px; }
    section[data-testid="stSidebar"] .fl-stat-box .val { font-family:'Plus Jakarta Sans',sans-serif;font-size:1.3rem;font-weight:800;color:#FFFFFF !important; }
    section[data-testid="stSidebar"] .fl-stat-box .lbl { font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#4A6A8A !important;letter-spacing:1px;text-transform:uppercase;margin-top:2px; }
    section[data-testid="stSidebar"] input { background:#1A3A5C !important;border:1px solid #2A5A8C !important;color:#FFFFFF !important;border-radius:6px !important;font-family:'JetBrains Mono',monospace !important;font-size:0.72rem !important; }

    .fl-hero { background:#0A2540;border-radius:16px;padding:40px 44px;margin-bottom:20px;position:relative;overflow:hidden; }
    .fl-hero::before { content:'';position:absolute;top:-80px;right:-80px;width:300px;height:300px;background:radial-gradient(circle,rgba(99,91,255,0.2) 0%,transparent 70%);pointer-events:none; }
    .fl-hero::after { content:'';position:absolute;bottom:-60px;left:20%;width:400px;height:200px;background:radial-gradient(ellipse,rgba(99,91,255,0.08) 0%,transparent 70%);pointer-events:none; }
    .fl-hero-logo { font-family:'Plus Jakarta Sans',sans-serif;font-size:2.4rem;font-weight:800;color:#FFFFFF;letter-spacing:-1px;margin:0;line-height:1; }
    .fl-hero-logo span { color:#635BFF; }
    .fl-hero-tagline { font-family:'Plus Jakarta Sans',sans-serif;font-size:1.05rem;color:#7A9AB8;margin-top:10px;line-height:1.6;max-width:520px; }
    .fl-hero-pills { display:flex;gap:10px;margin-top:20px;flex-wrap:wrap; }
    .fl-hero-pill { background:rgba(99,91,255,0.15);border:1px solid rgba(99,91,255,0.3);border-radius:100px;padding:6px 16px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#A09CFF; }
    .fl-hero-pill.green { background:rgba(34,139,34,0.15);border-color:rgba(34,139,34,0.3);color:#80D880; }
    .fl-hero-pill.red   { background:rgba(223,27,65,0.15);border-color:rgba(223,27,65,0.3);color:#FF9CAF; }

    .fl-card { background:#FFFFFF;border:1px solid #E3E8EE;border-radius:12px;padding:24px 28px;margin-bottom:14px;box-shadow:0 1px 3px rgba(10,37,64,0.05); }
    .fl-label { font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#8898AA;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px; }

    .fl-metric { background:#FFFFFF;border:1px solid #E3E8EE;border-radius:10px;padding:18px 20px;text-align:center;box-shadow:0 1px 3px rgba(10,37,64,0.04); }
    .fl-metric-val { font-family:'Plus Jakarta Sans',sans-serif;font-size:2rem;font-weight:800;line-height:1;margin-bottom:4px; }
    .fl-metric-lbl { font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#8898AA;letter-spacing:1.5px;text-transform:uppercase; }

    .chip-approved { display:inline-block;background:#EFFFEE;border:1px solid #AAE8AA;color:#228B22;padding:4px 14px;border-radius:100px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:500; }
    .chip-review   { display:inline-block;background:#FFF8E6;border:1px solid #FFD980;color:#B7740A;padding:4px 14px;border-radius:100px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:500; }
    .chip-blocked  { display:inline-block;background:#FFF0F0;border:1px solid #FFB3B3;color:#DF1B41;padding:4px 14px;border-radius:100px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:500; }

    .fl-score-num { font-family:'Plus Jakarta Sans',sans-serif;font-size:4rem;font-weight:800;line-height:1;letter-spacing:-2px; }
    .fl-score-bar-track { height:8px;background:#F6F9FC;border-radius:99px;overflow:hidden;margin:14px 0 6px;border:1px solid #E3E8EE; }
    .fl-score-bar-fill { height:100%;border-radius:99px; }

    .fl-factor { display:flex;align-items:center;gap:14px;padding:11px 0;border-bottom:1px solid #F0F4F8; }
    .fl-factor:last-child { border-bottom:none; }
    .fl-factor-rank { width:22px;height:22px;background:#F6F9FC;border:1px solid #E3E8EE;border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8898AA;flex-shrink:0; }
    .fl-factor-name { font-family:'JetBrains Mono',monospace;font-size:0.82rem;color:#0A2540;font-weight:500;flex:1; }
    .fl-factor-bar-bg { width:90px;height:4px;background:#F0F4F8;border-radius:99px;overflow:hidden; }
    .fl-factor-bar { height:100%;border-radius:99px; }
    .fl-explain { background:#F6F9FC;border-left:3px solid #635BFF;border-radius:0 8px 8px 0;padding:14px 18px;font-family:'Plus Jakarta Sans',sans-serif;font-size:0.88rem;color:#425466;line-height:1.75; }
    .fl-meta { display:flex;gap:20px;font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#8898AA;margin-top:14px; }
    .fl-empty { text-align:center;padding:72px 24px; }
    .fl-empty-icon { font-size:2.8rem;opacity:0.3;margin-bottom:14px; }
    .fl-empty-text { font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8898AA;letter-spacing:1.5px;text-transform:uppercase;line-height:2; }

    .fraud-category-header { display:flex;align-items:center;gap:14px;margin-bottom:20px;padding-bottom:16px;border-bottom:2px solid #F0F4F8; }
    .fraud-category-icon { width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0; }
    .fraud-category-title { font-family:'Plus Jakarta Sans',sans-serif;font-size:1.1rem;font-weight:700;color:#0A2540;margin:0; }
    .fraud-category-subtitle { font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#8898AA;letter-spacing:1.5px;text-transform:uppercase;margin-top:2px; }
    .fraud-type-card { background:#F6F9FC;border:1px solid #E3E8EE;border-radius:10px;padding:18px 20px;margin-bottom:12px; }
    .fraud-type-name { font-family:'Plus Jakarta Sans',sans-serif;font-size:0.95rem;font-weight:700;color:#0A2540;margin-bottom:6px; }
    .fraud-type-desc { font-family:'Plus Jakarta Sans',sans-serif;font-size:0.85rem;color:#425466;line-height:1.65;margin-bottom:12px; }
    .fraud-signals-label { font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#8898AA;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px; }
    .fraud-signal-tag { display:inline-block;background:#FFFFFF;border:1px solid #E3E8EE;border-radius:6px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#635BFF;margin:3px 3px 3px 0; }
    .fraud-dollar { display:inline-block;background:#FFF0F0;border:1px solid #FFB3B3;border-radius:6px;padding:3px 10px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#DF1B41;margin-top:8px; }
    .fraud-stat-row { display:flex;gap:10px;margin-top:10px;flex-wrap:wrap; }
    .fraud-stat-pill { background:#FFFFFF;border:1px solid #E3E8EE;border-radius:8px;padding:6px 12px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#425466; }
    .fraud-stat-pill b { color:#0A2540; }
    .section-divider { height:1px;background:#F0F4F8;margin:28px 0; }

    .stTabs [data-baseweb="tab-list"] { background:#FFFFFF;border-radius:10px;border:1px solid #E3E8EE;padding:4px;gap:2px;box-shadow:0 1px 3px rgba(10,37,64,0.04); }
    .stTabs [data-baseweb="tab"] { border-radius:7px;font-family:'Plus Jakarta Sans',sans-serif;font-size:0.85rem;font-weight:500;color:#8898AA;padding:8px 22px; }
    .stTabs [aria-selected="true"] { background:#635BFF !important;color:#FFFFFF !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top:20px; }

    .stButton > button { background:#635BFF;color:white;border:none;border-radius:8px;font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;padding:11px 24px;font-size:0.9rem;transition:all 0.2s;box-shadow:0 2px 8px rgba(99,91,255,0.3); }
    .stButton > button:hover { background:#5851DB;transform:translateY(-1px);box-shadow:0 4px 14px rgba(99,91,255,0.4); }
    .stTextInput input, .stNumberInput input { border:1px solid #E3E8EE !important;border-radius:8px !important;font-family:'Plus Jakarta Sans',sans-serif !important;color:#0A2540 !important;background:#FFFFFF !important; }

    .fl-upload-zone { background:#FFFFFF;border:2px dashed #E3E8EE;border-radius:12px;padding:36px 28px;text-align:center;transition:border-color 0.2s; }
    .fl-upload-zone:hover { border-color:#635BFF; }
    .fl-how-step { display:flex;align-items:flex-start;gap:16px;padding:16px 0;border-bottom:1px solid #F0F4F8; }
    .fl-how-step:last-child { border-bottom:none; }
    .fl-step-num { width:32px;height:32px;background:#635BFF;border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:'Plus Jakarta Sans',sans-serif;font-size:0.85rem;font-weight:700;color:#FFFFFF;flex-shrink:0; }
    .fl-step-text { font-family:'Plus Jakarta Sans',sans-serif;font-size:0.88rem;color:#425466;line-height:1.6; }
    .fl-step-title { font-weight:700;color:#0A2540;margin-bottom:2px; }

    .fl-online-card { background:#EFFFEE;border:1px solid #AAE8AA;border-radius:12px;padding:20px 24px; }
    .fl-error-card  { background:#FFF0F0;border:1px solid #FFB3B3;border-radius:12px;padding:20px 24px; }
    .fl-csv-guide { background:#F6F9FC;border:1px solid #E3E8EE;border-radius:10px;padding:20px 24px; }
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

API_URL = "https://fraud-api-pzkn.onrender.com"

def score_color(s): return "#228B22" if s<0.3 else "#B7740A" if s<0.7 else "#DF1B41"
def score_bg(s):    return "#EFFFEE" if s<0.3 else "#FFF8E6" if s<0.7 else "#FFF0F0"
def score_border(s):return "#AAE8AA" if s<0.3 else "#FFD980" if s<0.7 else "#FFB3B3"
def bar_color(s):   return "#635BFF" if s<0.3 else "#F5A623" if s<0.7 else "#DF1B41"

def decision_chip(d):
    return {"approved":'<span class="chip-approved">Approved</span>',
            "review":'<span class="chip-review">Review</span>',
            "blocked":'<span class="chip-blocked">Blocked</span>'}.get(d, d)

def call_api(txn_id, amount, time_sec, v_values):
    payload = {"transaction_id":txn_id,"amount":float(amount),"time_seconds":float(time_sec),
               **{f"V{i+1}":float(v_values[i]) for i in range(28)}}
    try:
        r = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
        return (r.json(), None) if r.status_code==200 else (None, f"API error {r.status_code}")
    except requests.exceptions.ConnectionError:
        return None, "API is waking up — please wait 30 seconds and try again."
    except requests.exceptions.Timeout:
        return None, "Request timed out — the API may be cold-starting. Try again in 30 seconds."
    except Exception as e:
        return None, str(e)

def batch_score(df, pb, st_txt):
    results = []
    for i, row in df.iterrows():
        v_vals = [row.get(f"V{j}", 0.0) for j in range(1, 29)]
        res, err = call_api(f"txn_{i:05d}", row.get("Amount",1.0), row.get("Time",0.0), v_vals)
        if res:
            results.append({"Transaction":f"txn_{i:05d}", "Amount":f"€{row.get('Amount',0):.2f}",
                "Fraud Score":res["fraud_score"], "Decision":res["decision"],
                "Top Factor 1":res["top_risk_factors"][0] if res["top_risk_factors"] else "",
                "Top Factor 2":res["top_risk_factors"][1] if len(res["top_risk_factors"])>1 else "",
                "Latency ms":res["latency_ms"], "Explanation":res["explanation"]})
        else:
            results.append({"Transaction":f"txn_{i:05d}","Amount":"","Fraud Score":None,
                "Decision":"error","Top Factor 1":err,"Top Factor 2":"","Latency ms":None,"Explanation":err})
        pb.progress((i+1)/len(df))
        st_txt.markdown(f'<p style="font-family:JetBrains Mono,monospace;font-size:0.72rem;color:#8898AA">Analysing transaction {i+1} of {len(df)}…</p>', unsafe_allow_html=True)
        time.sleep(0.05)
    return pd.DataFrame(results)

FRAUD_DATA = {
    "identity": {
        "icon":"🪪","color":"#635BFF","bg":"#F0EFFF",
        "title":"Identity Fraud","subtitle":"7 fraud types · $52B annual losses",
        "types":[
            {"name":"Account Takeover (ATO)","desc":"A fraudster gains access to an existing account using stolen credentials, phishing, SIM swapping, or credential stuffing. Once inside, they drain funds, change contact details, or open new credit lines before the victim notices.","signals":["Login from new device/location","Password change + immediate transaction","Multiple failed logins then success","New payee added within minutes of login"],"loss":"$11.4B lost in 2023 (Javelin Research)","stats":[("Detection window","4–48 hours"),("Avg loss per victim","$12,000"),("Top vector","Phishing (42%)")]},
            {"name":"Synthetic Identity Fraud","desc":"Fraudsters combine a real Social Security Number (often a child's or deceased person's) with fabricated names and addresses to create a 'Frankenstein' identity. They build credit slowly over months before 'busting out' — maxing everything and disappearing.","signals":["SSN age mismatch with applicant","No credit history despite stated age","Multiple applications, same SSN, different names","Sudden credit utilization spike after long quiet period"],"loss":"$20B+ annual losses (Federal Reserve)","stats":[("Build phase","6–24 months"),("Avg bust-out","$97,000"),("Status","Fastest growing identity fraud type")]},
            {"name":"New Account Fraud (NAF)","desc":"Using stolen or fabricated personal information to open entirely new accounts — credit cards, loans, or bank accounts — in another person's name. The victim may not know for months until debt collectors call.","signals":["Address mismatch with credit bureau","Device fingerprint previously flagged","Email domain created <30 days ago","Multiple applications in 24h"],"loss":"$5.3B in new account fraud (2023)","stats":[("Time to discovery","3–6 months"),("Avg accounts opened","3–5 per identity"),("Common targets","Credit cards, auto loans")]},
            {"name":"SIM Swap Fraud","desc":"The fraudster convinces a mobile carrier to transfer a victim's phone number to a SIM they control — bypassing SMS-based two-factor authentication. Once they control the number, they reset passwords on banking, email, and crypto accounts.","signals":["Sudden loss of mobile signal","Auth requests at unusual hours","New SIM registered + immediate bank login","Carrier change + password reset same day"],"loss":"$68M reported to FBI IC3 in 2023","stats":[("Attack window","Minutes to hours"),("Success rate","High (carrier social engineering)"),("Primary target","Crypto + banking accounts")]},
            {"name":"Credential Stuffing","desc":"Automated bots test billions of username/password combinations leaked from data breaches against financial institutions. Because people reuse passwords, attackers find valid credentials at a predictable rate — typically 0.1–2% success on large lists.","signals":["High-volume login attempts from single IP","Login success rate spike","Logins across impossible geographic range","Browser fingerprint changes between attempts"],"loss":"$6B annually across financial services","stats":[("Breach lists available","15B+ credentials"),("Bot success rate","0.1–2%"),("Detection tool","Velocity + fingerprinting")]},
            {"name":"Phishing & Social Engineering","desc":"Fraudsters impersonate banks, government agencies, or trusted brands via email, SMS (smishing), or phone (vishing) to trick victims into revealing credentials or authorizing transfers. 'Hi, this is your bank's fraud team' is the classic script.","signals":["User-initiated transfer after inbound call","OTP entered + large outbound wire","Transaction destination is new payee","Login from victim's device but unusual transfer"],"loss":"$3.4B in business email compromise (FBI 2023)","stats":[("Most common entry","Email (67%)"),("Avg wire loss","$43,000"),("Fastest vector","SMS smishing (+300%/yr)")]},
            {"name":"Medical Identity Theft","desc":"Using someone else's identity to obtain medical care, prescription drugs, or submit fraudulent insurance claims. Particularly dangerous because it corrupts the victim's medical records — wrong blood type or medications can cause life-threatening errors.","signals":["Claims from multiple providers same day","Medical service in different state","Prescription claims for controlled substances","EOB for services patient denies receiving"],"loss":"$30B+ annually (HHS OIG)","stats":[("Detection lag","1–3 years"),("Victims per breach","Thousands"),("Key danger","Corrupts medical records")]},
        ]
    },
    "payments": {
        "icon":"💳","color":"#DF1B41","bg":"#FFF0F0",
        "title":"Payment Fraud","subtitle":"8 fraud types · $485B annual losses",
        "types":[
            {"name":"Card-Not-Present (CNP) Fraud","desc":"Stolen card details are used to make online purchases where the physical card is never needed. This is the largest category of payment fraud and boomed after EMV chip cards made in-person fraud harder.","signals":["Billing/shipping address mismatch","First-time order to freight forwarder","High-value electronics or gift cards","Multiple cards attempted, one succeeds"],"loss":"$10.16B in the US alone (Nilson Report 2023)","stats":[("Share of card fraud","76% of all card fraud"),("Top categories","Electronics, gift cards, travel"),("Primary defense","3DS2 + ML scoring")]},
            {"name":"Card Testing / Carding","desc":"Fraudsters test stolen card numbers against low-friction merchants with tiny amounts — often $0.01 to $1.00 — to identify which cards are still active before selling them or making larger purchases.","signals":["Many small transactions in rapid succession","High decline-to-approval ratio","Same BIN range across multiple transactions","Transactions at 2–5am"],"loss":"$1.8B+ in testing-related fraud annually","stats":[("Test amount","$0.01–$1.00"),("Cards per batch","Thousands to millions"),("Velocity","100s of attempts per minute")]},
            {"name":"Chargeback / Friendly Fraud","desc":"A cardholder makes a legitimate purchase, receives the goods, then disputes the charge with their bank claiming non-delivery or unauthorized use. Also known as 'cyber shoplifting.'","signals":["High refund rate on same account","Dispute filed immediately after delivery","Pattern of disputes same time each month","Address matches known fraud list"],"loss":"$117B in chargeback losses (MRC 2023)","stats":[("Merchant chargeback fee","$15–$100 per dispute"),("Merchant win rate","Only 22%"),("Fastest growing","Digital goods, subscriptions")]},
            {"name":"Authorized Push Payment (APP) Fraud","desc":"The victim is tricked into voluntarily authorizing a bank transfer to a fraudster's account — through romance scams, investment fraud, or bank impersonation. Unlike card fraud, APP fraud is hard to reverse because the victim authorized the payment.","signals":["Large first-time international wire","New payee + transfer within 5 minutes","Transfer matches recent inbound deposit","Transaction during off-hours on new device"],"loss":"£459M in UK alone (UK Finance H1 2023)","stats":[("Recovery rate","Less than 50%"),("Avg loss per victim","£6,937 (UK)"),("Fastest growing","Investment/romance scams")]},
            {"name":"ACH / Wire Fraud","desc":"Fraudulent ACH debits or wire transfers using stolen banking credentials. Business Email Compromise (BEC) is the most sophisticated variant — attackers compromise vendor email and redirect legitimate invoice payments to their own accounts.","signals":["Change to vendor payment details via email","Wire to new bank + new country","ACH debit from unknown originator","Payroll redirect request via email"],"loss":"$2.9B in BEC losses (FBI IC3 2023)","stats":[("Reversal window","ACH: 24–48h · Wire: minutes"),("Most targeted","Finance + HR employees"),("BEC success rate","Alarmingly high")]},
            {"name":"Refund Fraud","desc":"Exploiting merchant return policies to obtain cash or store credit fraudulently — returning stolen merchandise, claiming non-delivery for received items, or using counterfeit receipts. Organized retail crime rings run sophisticated operations.","signals":["Return without receipt above threshold","Return of empty box or wrong item","Same customer ID across multiple locations","Item returned exceeds original purchase price"],"loss":"$101B in retail return fraud (NRF 2023)","stats":[("Return fraud rate","10.4% of all returns"),("Organized rings","13% of losses"),("Seasonal peak","January (post-holiday)")]},
            {"name":"Money Mule Schemes","desc":"Fraudsters recruit victims (often unknowingly) to receive and forward stolen funds — taking a cut and obscuring the money trail. Mules are recruited via fake job ads, romance scams, or reshipping schemes.","signals":["Account receives multiple inbound then immediate outbound","Transfers to multiple recipients same day","Activity inconsistent with account profile","Wires to high-risk jurisdictions"],"loss":"$3B+ laundered through mule networks annually","stats":[("Mule awareness","50% don't know they're participating"),("Recruitment","Job boards, social media, dating apps"),("Legal risk","Federal money laundering charges")]},
            {"name":"Buy Now Pay Later (BNPL) Fraud","desc":"The explosive growth of BNPL services has created a new attack surface. Fraudsters exploit softer underwriting criteria, use synthetic identities, or take over accounts to make purchases and never repay.","signals":["New BNPL account + immediate high-value purchase","Email/phone changed after approval","Device previously associated with fraud","First repayment missed"],"loss":"$6.4B projected BNPL fraud losses by 2025 (Juniper)","stats":[("BNPL fraud rate","2–5x higher than card"),("Top targets","Electronics, luxury goods"),("Gap","Soft credit checks exploited")]},
        ]
    }
}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="fl-sidebar-logo">Fraud<span>Lens</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="fl-slabel" style="margin-top:8px">About</p>', unsafe_allow_html=True)
    st.markdown("""
    <div class="fl-srow">
        FraudLens uses a real machine learning model trained on 284,807 credit card transactions to detect payment fraud in real time.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown('<p class="fl-slabel">Model stats</p>', unsafe_allow_html=True)
    for val, lbl in [("0.97+","ROC-AUC score"),("284k","Transactions trained on"),("<25ms","Inference latency"),("SHAP","Explainability method")]:
        st.markdown(f'<div class="fl-stat-box"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown('<p class="fl-slabel">Decision thresholds</p>', unsafe_allow_html=True)
    for color, label, threshold in [("#228B22","Approved","score < 0.30"),("#F5A623","Review","0.30 – 0.70"),("#DF1B41","Blocked","score > 0.70")]:
        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;padding:7px 12px;border-radius:8px;background:#1A3A5C;margin-bottom:6px;font-family:JetBrains Mono,monospace;font-size:0.7rem"><div style="width:8px;height:8px;background:{color};border-radius:50%;flex-shrink:0"></div><span style="color:#FFFFFF !important">{label}</span><span style="color:#4A7A9A !important;margin-left:auto">{threshold}</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#1A3A5C;border-radius:10px;padding:12px 14px">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:#4A6A8A;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px">Note</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#A0BACE;line-height:1.8">
            First request may take<br>30–60s (free tier warm-up).<br>Subsequent requests &lt;25ms.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="fl-hero">
    <div>
        <p class="fl-hero-logo">Fraud<span>Lens</span></p>
        <p class="fl-hero-tagline">Upload a CSV of transactions, score them for fraud in real time, and learn what each fraud type actually looks like — built on a production-grade ML model.</p>
        <div class="fl-hero-pills">
            <span class="fl-hero-pill">🤖 LightGBM · 97%+ ROC-AUC</span>
            <span class="fl-hero-pill green">🔍 SHAP explainability</span>
            <span class="fl-hero-pill red">⚡ &lt;25ms inference</span>
            <span class="fl-hero-pill">📚 15 fraud types documented</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🔍 Score Transactions",
    "📚 Fraud Encyclopedia",
    "⚙️ Single Transaction Tester"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Score Transactions (CSV Upload — primary feature)
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_how, col_upload = st.columns([1, 1.4], gap="large")

    with col_how:
        st.markdown("""
        <div class="fl-card">
            <p class="fl-label">How it works</p>
            <div class="fl-how-step">
                <div class="fl-step-num">1</div>
                <div class="fl-step-text">
                    <div class="fl-step-title">Upload your CSV</div>
                    Needs columns: Time, Amount, V1–V28. Use a slice of the Kaggle credit card fraud dataset or any compatible format.
                </div>
            </div>
            <div class="fl-how-step">
                <div class="fl-step-num">2</div>
                <div class="fl-step-text">
                    <div class="fl-step-title">Choose how many rows to score</div>
                    Select 1–50 transactions. Each is sent to the fraud model and scored in real time.
                </div>
            </div>
            <div class="fl-how-step">
                <div class="fl-step-num">3</div>
                <div class="fl-step-text">
                    <div class="fl-step-title">Get scores + explanations</div>
                    Each transaction gets a fraud probability (0–100%), a decision (Approved / Review / Blocked), and the top 3 SHAP risk factors explaining the score.
                </div>
            </div>
            <div class="fl-how-step">
                <div class="fl-step-num">4</div>
                <div class="fl-step-text">
                    <div class="fl-step-title">Download results</div>
                    Export the full scored dataset as CSV for further analysis.
                </div>
            </div>
        </div>

        <div class="fl-card" style="margin-top:0">
            <p class="fl-label">Required CSV columns</p>
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#425466;line-height:2.5">
                <span style="color:#635BFF;font-weight:500">Time</span> &nbsp;&nbsp;&nbsp;&nbsp; seconds elapsed since first transaction<br>
                <span style="color:#635BFF;font-weight:500">Amount</span> &nbsp;&nbsp; transaction amount in euros<br>
                <span style="color:#635BFF;font-weight:500">V1–V28</span> &nbsp; anonymized PCA features<br>
                <span style="color:#8898AA">Class</span> &nbsp;&nbsp;&nbsp;&nbsp; optional (0=legit, 1=fraud)
            </div>
            <div style="margin-top:14px;padding:10px 14px;background:#F6F9FC;border:1px solid #E3E8EE;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#8898AA;line-height:1.8">
                Dataset: kaggle.com/datasets/mlg-ulb/creditcardfraud
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_upload:
        uploaded = st.file_uploader("Upload your transaction CSV", type=["csv"],
                                     help="Must contain Time, Amount, V1–V28 columns")

        if not uploaded:
            st.markdown("""
            <div class="fl-upload-zone">
                <div style="font-size:2.5rem;margin-bottom:12px">📂</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:600;color:#0A2540;font-size:1rem">Drop your CSV file here</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;color:#8898AA;margin-top:8px;line-height:1.8">
                    or click Browse files above<br>
                    Supports .csv files up to 200MB
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            df_raw = pd.read_csv(uploaded)
            st.success(f"✓ Loaded {len(df_raw):,} transactions from {uploaded.name}")

            max_rows = st.slider("How many transactions to score?", 1,
                                  min(50, len(df_raw)), min(10, len(df_raw)),
                                  help="Free tier processes up to 50 rows at a time")
            df_sample = df_raw.head(max_rows).reset_index(drop=True)

            col_btn, col_info = st.columns([1, 1])
            with col_btn:
                score_btn = st.button("Analyse transactions", type="primary", use_container_width=True)
            with col_info:
                st.markdown(f"""
                <div style="padding:11px 16px;background:#F6F9FC;border:1px solid #E3E8EE;border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#8898AA">
                    {max_rows} transactions · ~{max_rows*2}s estimated
                </div>
                """, unsafe_allow_html=True)

            if score_btn:
                pb = st.progress(0)
                st_txt = st.empty()
                df_res = batch_score(df_sample, pb, st_txt)
                pb.empty(); st_txt.empty()

                valid = df_res[df_res["Decision"] != "error"]
                if len(valid) > 0:
                    n_app=(valid["Decision"]=="approved").sum()
                    n_rev=(valid["Decision"]=="review").sum()
                    n_blk=(valid["Decision"]=="blocked").sum()
                    avg_s=valid["Fraud Score"].mean()

                    st.markdown("---")
                    st.markdown('<p class="fl-label">Analysis results</p>', unsafe_allow_html=True)

                    m1,m2,m3,m4,m5 = st.columns(5)
                    for col,val,color,label in [
                        (m1,str(len(valid)),"#0A2540","Scored"),
                        (m2,str(n_app),"#228B22","Approved"),
                        (m3,str(n_rev),"#B7740A","Review"),
                        (m4,str(n_blk),"#DF1B41","Blocked"),
                        (m5,f"{avg_s:.1%}","#635BFF","Avg score"),
                    ]:
                        with col:
                            st.markdown(f'<div class="fl-metric"><div class="fl-metric-val" style="color:{color}">{val}</div><div class="fl-metric-lbl">{label}</div></div>', unsafe_allow_html=True)

                    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                    ch1, ch2 = st.columns(2)
                    plt.rcParams.update({"font.family":"sans-serif","axes.spines.top":False,"axes.spines.right":False})

                    with ch1:
                        fig,ax=plt.subplots(figsize=(5,3.2))
                        fig.patch.set_facecolor("#FFFFFF"); ax.set_facecolor("#FFFFFF")
                        scores=valid["Fraud Score"].dropna().values
                        ax.hist(scores[scores<0.3],bins=12,color="#635BFF",alpha=0.8,label="Approved",edgecolor="white")
                        ax.hist(scores[(scores>=0.3)&(scores<0.7)],bins=8,color="#F5A623",alpha=0.8,label="Review",edgecolor="white")
                        ax.hist(scores[scores>=0.7],bins=8,color="#DF1B41",alpha=0.8,label="Blocked",edgecolor="white")
                        ax.axvline(0.3,color="#E3E8EE",linewidth=1.5,linestyle="--")
                        ax.axvline(0.7,color="#E3E8EE",linewidth=1.5,linestyle="--")
                        ax.set_xlabel("Fraud score",fontsize=9,color="#8898AA")
                        ax.set_ylabel("Count",fontsize=9,color="#8898AA")
                        ax.tick_params(colors="#8898AA",labelsize=8)
                        for sp in ["left","bottom"]: ax.spines[sp].set_color("#E3E8EE")
                        ax.legend(fontsize=8,framealpha=0,labelcolor="#425466")
                        ax.set_title("Score distribution",fontsize=10,color="#0A2540",fontweight="600",pad=10)
                        plt.tight_layout(); st.pyplot(fig); plt.close()

                    with ch2:
                        fig2,ax2=plt.subplots(figsize=(5,3.2))
                        fig2.patch.set_facecolor("#FFFFFF"); ax2.set_facecolor("#FFFFFF")
                        dc=valid["Decision"].value_counts()
                        cm_={"approved":"#635BFF","review":"#F5A623","blocked":"#DF1B41"}
                        bars=ax2.bar(dc.index,dc.values,color=[cm_.get(d,"#8898AA") for d in dc.index],
                                     alpha=0.88,edgecolor="white",linewidth=2,width=0.45,zorder=3)
                        for bar,v in zip(bars,dc.values):
                            ax2.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,
                                     str(v),ha="center",color="#0A2540",fontsize=11,fontweight="700")
                        ax2.set_ylabel("Count",fontsize=9,color="#8898AA")
                        ax2.tick_params(colors="#8898AA",labelsize=9)
                        ax2.set_ylim(0,dc.max()*1.3)
                        ax2.yaxis.grid(True,color="#F6F9FC",zorder=0)
                        for sp in ["left","bottom"]: ax2.spines[sp].set_color("#E3E8EE")
                        ax2.set_title("Decision breakdown",fontsize=10,color="#0A2540",fontweight="600",pad=10)
                        plt.tight_layout(); st.pyplot(fig2); plt.close()

                    st.markdown('<p class="fl-label" style="margin-top:4px">Transaction detail</p>', unsafe_allow_html=True)
                    display=valid[["Transaction","Amount","Fraud Score","Decision","Top Factor 1","Top Factor 2","Latency ms"]].copy()
                    display["Fraud Score"]=display["Fraud Score"].apply(lambda x:f"{x:.4f}")
                    st.dataframe(display,use_container_width=True,hide_index=True)
                    st.download_button("Download full results as CSV",data=df_res.to_csv(index=False),
                        file_name=f"fraudlens_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Fraud Encyclopedia
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="fl-card" style="background:linear-gradient(135deg,#0A2540 0%,#1a1060 100%);border:none;margin-bottom:20px">
        <div style="display:flex;align-items:center;gap:16px">
            <div style="font-size:2rem">📚</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.3rem;font-weight:800;color:#FFFFFF">Fraud Encyclopedia</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#4A6A8A;letter-spacing:1.5px;text-transform:uppercase;margin-top:4px">15 fraud types · $537B in annual losses · Practitioner-level reference</div>
            </div>
        </div>
        <div style="display:flex;gap:12px;margin-top:18px;flex-wrap:wrap">
            <div style="background:rgba(99,91,255,0.2);border:1px solid rgba(99,91,255,0.3);border-radius:8px;padding:10px 16px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#A09CFF"><b style="color:#FFFFFF;font-size:1.1rem">7</b><br>Identity fraud types</div>
            <div style="background:rgba(223,27,65,0.2);border:1px solid rgba(223,27,65,0.3);border-radius:8px;padding:10px 16px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#FF9CAF"><b style="color:#FFFFFF;font-size:1.1rem">8</b><br>Payment fraud types</div>
            <div style="background:rgba(245,166,35,0.2);border:1px solid rgba(245,166,35,0.3);border-radius:8px;padding:10px 16px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#FFD080"><b style="color:#FFFFFF;font-size:1.1rem">$537B</b><br>Annual global losses</div>
            <div style="background:rgba(34,139,34,0.2);border:1px solid rgba(34,139,34,0.3);border-radius:8px;padding:10px 16px;font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#80D880"><b style="color:#FFFFFF;font-size:1.1rem">SHAP</b><br>Signals per fraud type</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for cat_key, cat in FRAUD_DATA.items():
        st.markdown(f"""
        <div class="fl-card" style="border-top:3px solid {cat['color']}">
            <div class="fraud-category-header">
                <div class="fraud-category-icon" style="background:{cat['bg']}">{cat['icon']}</div>
                <div>
                    <p class="fraud-category-title">{cat['title']}</p>
                    <p class="fraud-category-subtitle">{cat['subtitle']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        for ft in cat["types"]:
            signals_html="".join([f'<span class="fraud-signal-tag">{s}</span>' for s in ft["signals"]])
            stats_html="".join([f'<div class="fraud-stat-pill"><b>{s[0]}</b> &nbsp; {s[1]}</div>' for s in ft["stats"]])
            st.markdown(f"""
            <div class="fraud-type-card">
                <div class="fraud-type-name">{ft['name']}</div>
                <div class="fraud-type-desc">{ft['desc']}</div>
                <div class="fraud-signals-label">Detection signals</div>
                <div>{signals_html}</div>
                <div class="fraud-dollar">{ft['loss']}</div>
                <div class="fraud-stat-row">{stats_html}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if cat_key == "identity":
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Single Transaction Tester
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="fl-card" style="border-left:3px solid #635BFF;border-radius:0 12px 12px 12px;margin-bottom:20px">
        <p class="fl-label">About this tab</p>
        <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.88rem;color:#425466;line-height:1.7">
            Score a single transaction manually by entering its features. Use the presets to see how the model handles a clear legitimate transaction vs. a high-risk fraud pattern — and how SHAP explains the difference.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.1, 0.9], gap="large")
    with col_left:
        st.markdown('<div class="fl-card">', unsafe_allow_html=True)
        st.markdown('<p class="fl-label">Transaction details</p>', unsafe_allow_html=True)
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
        st.markdown('<p class="fl-label" style="margin-top:16px">V-features · V1–V28</p>', unsafe_allow_html=True)
        v_values=[]
        rows=[st.columns(7) for _ in range(4)]
        for i in range(28):
            with rows[i//7][i%7]:
                v_values.append(st.number_input(f"V{i+1}",value=default_v[i],format="%.3f",key=f"tv{i+1}",label_visibility="collapsed"))
        st.markdown('</div>', unsafe_allow_html=True)
        run=st.button("Score this transaction",type="primary",use_container_width=True)

    with col_right:
        st.markdown('<p class="fl-label">Result</p>', unsafe_allow_html=True)
        if run:
            with st.spinner(""):
                result,error=call_api(txn_id,amount,time_sec,v_values)
            if error:
                st.error(f"Error: {error}")
            else:
                score=result["fraud_score"]; decision=result["decision"]
                bc=bar_color(score); sc=score_color(score); bg=score_bg(score); bd=score_border(score)
                st.markdown(f'<div class="fl-card" style="background:{bg};border-color:{bd};border-top:3px solid {sc}"><div style="display:flex;justify-content:space-between;align-items:flex-start"><div><p class="fl-label">Fraud probability</p><p class="fl-score-num" style="color:{sc}">{score:.1%}</p></div><div style="text-align:right;padding-top:2px"><p class="fl-label">Decision</p><div style="margin-top:8px">{decision_chip(decision)}</div></div></div><div class="fl-score-bar-track"><div class="fl-score-bar-fill" style="width:{score*100:.1f}%;background:{bc}"></div></div><div style="display:flex;justify-content:space-between;font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#8898AA"><span>0%</span><span>30%</span><span>70%</span><span>100%</span></div></div>', unsafe_allow_html=True)
                factors=result["top_risk_factors"]; widths=[100,62,38]
                frows="".join([f'<div class="fl-factor"><div class="fl-factor-rank">{j+1}</div><div class="fl-factor-name">{f}</div><div class="fl-factor-bar-bg"><div class="fl-factor-bar" style="width:{widths[j]}%;background:{bc}"></div></div></div>' for j,f in enumerate(factors)])
                st.markdown(f'<div class="fl-card" style="margin-top:0"><p class="fl-label">Top SHAP risk factors</p>{frows}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="fl-card" style="margin-top:0"><p class="fl-label">Explanation</p><div class="fl-explain">{result["explanation"]}</div><div class="fl-meta"><span>Latency: {result["latency_ms"]}ms</span><span>·</span><span>Model: {result["model_version"]}</span><span>·</span><span>{result["evaluated_at"][:19].replace("T"," ")} UTC</span></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="fl-card" style="margin-top:0"><div class="fl-empty"><div class="fl-empty-icon">🛡️</div><p class="fl-empty-text">Choose a preset or enter values<br>then click Score</p></div></div>', unsafe_allow_html=True)