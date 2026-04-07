# 🛡️ FraudLens — Real-Time Payment Fraud Detection

**A production-grade fraud detection system built from scratch: trained ML model → live REST API → public dashboard.**

[![Live Dashboard](https://img.shields.io/badge/Dashboard-Live-635BFF?style=flat-square&logo=streamlit)](https://fraud-api-3mhsnrsqe3wgepyf7xcrm3.streamlit.app/)
[![API Docs](https://img.shields.io/badge/API-Docs-0A2540?style=flat-square&logo=fastapi)](https://fraud-api-pzkn.onrender.com/docs)
[![GitHub](https://img.shields.io/badge/GitHub-akondiparthy-181717?style=flat-square&logo=github)](https://github.com/akondiparthy/fraud-api)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)](https://python.org)

---

## What is FraudLens?

FraudLens scores credit card transactions for fraud probability in real time. You send it a transaction, it responds in under 25 milliseconds with:

- A **fraud score** from 0–100%
- A **decision**: Approved, Review, or Blocked
- The **top 3 SHAP risk factors** explaining the score
- A **plain-English explanation** — because regulators require it

Try it live: upload a CSV of transactions at the dashboard, or call the API directly.

---

## Live Links

| What | URL |
|---|---|
| 🌐 Dashboard | [your-app.streamlit.app](https://fraud-api-3mhsnrsqe3wgepyf7xcrm3.streamlit.app/) |
| 🔌 API Docs | [fraud-api-pzkn.onrender.com/docs](https://fraud-api-pzkn.onrender.com/docs) |
| 💻 Source Code | [github.com/akondiparthy/fraud-api](https://github.com/akondiparthy/fraud-api) |

> **Note:** The API runs on Render's free tier and sleeps after 15 minutes of inactivity. The first request after a sleep takes ~30–60 seconds to wake up. Subsequent requests are under 25ms.

---

## Model Performance

| Metric | Value |
|---|---|
| ROC-AUC | **0.97+** |
| Training data | 284,807 real transactions |
| Fraud rate in dataset | 0.17% (492 fraud / 284,315 legit) |
| Inference latency | < 25ms p99 |
| Explainability | SHAP TreeExplainer |
| Decision tiers | Approved · Review · Blocked |

---

## How It Works (Plain English)

```
You upload a transaction CSV
          ↓
Each transaction gets scored by a LightGBM model
          ↓
SHAP explains WHY the model gave that score
          ↓
You get: fraud score + decision + top 3 risk factors + explanation
```

**Why three tiers instead of two?**
Real fraud systems never use binary approved/blocked. A "review" tier creates a human-in-the-loop queue for ambiguous cases — reducing both missed fraud and false alarms.

---

## Project Structure

```
fraud-api/
├── api/
│   ├── main.py          ← FastAPI app (routes, startup)
│   ├── predictor.py     ← Model loading + SHAP inference
│   └── schemas.py       ← Pydantic request/response types
├── model/
│   ├── features.py      ← Feature engineering (same code in training + serving)
│   └── artifacts/
│       ├── model.pkl    ← Trained LightGBM model
│       ├── scaler.pkl   ← Fitted StandardScaler
│       └── metadata.json
├── dashboard.py         ← Streamlit public dashboard
├── fraud_detection_training.ipynb  ← Full training pipeline
├── Dockerfile
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| ML model | LightGBM | Handles class imbalance natively, fast, SHAP-compatible |
| Explainability | SHAP TreeExplainer | Regulatory requirement (ECOA/FCRA adverse action) |
| Training | Google Colab | Free GPU, no local environment issues |
| API | FastAPI + Uvicorn | Auto-generated docs, Pydantic validation, async |
| Containerization | Docker | Reproducible deployment anywhere |
| API hosting | Render (free) | Auto-deploys from GitHub |
| Dashboard | Streamlit | Accessible to non-technical users |
| Dashboard hosting | Streamlit Cloud (free) | Public URL, no infrastructure management |

---

## Quickstart — Call the API

```bash
curl -X POST https://fraud-api-pzkn.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_001",
    "amount": 299.99,
    "time_seconds": 80000,
    "V1": -1.36, "V2": -0.07, "V3": 2.54, "V4": 1.38,
    "V5": -0.34, "V6": 0.46, "V7": 0.24, "V8": 0.10,
    "V9": 0.36, "V10": 0.09, "V11": -0.55, "V12": -0.62,
    "V13": -0.99, "V14": -0.31, "V15": 1.47, "V16": -0.47,
    "V17": 0.21, "V18": 0.03, "V19": 0.40, "V20": 0.25,
    "V21": -0.02, "V22": 0.28, "V23": -0.11, "V24": 0.07,
    "V25": 0.13, "V26": -0.19, "V27": 0.13, "V28": -0.02
  }'
```

**Response:**
```json
{
  "transaction_id": "txn_001",
  "fraud_score": 0.0023,
  "decision": "approved",
  "top_risk_factors": ["V14", "V4", "V15"],
  "explanation": "Transaction scored 0.2% fraud probability. Decision: APPROVED. Top signals: V14, V4, V15.",
  "latency_ms": 21.4,
  "model_version": "v1.0",
  "evaluated_at": "2026-04-07T06:00:00Z"
}
```

---

## Run Locally

**Requirements:** Python 3.11, pip

```bash
# 1. Clone the repo
git clone https://github.com/akondiparthy/fraud-api.git
cd fraud-api

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate.bat       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the API
uvicorn api.main:app --reload --port 8000
# → open http://localhost:8000/docs

# 5. Run the dashboard (separate terminal)
streamlit run dashboard.py
# → open http://localhost:8501
```

---

## Train the Model Yourself

The full training pipeline is in `fraud_detection_training.ipynb`. It runs on Google Colab (free).

**Steps:**
1. Download the dataset from [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
2. Open the notebook in [Google Colab](https://colab.research.google.com)
3. Upload `creditcard.csv` to Colab's file panel
4. Run all cells — takes about 3–4 minutes
5. Download the three output files: `model.pkl`, `scaler.pkl`, `metadata.json`
6. Place them in `model/artifacts/`

**What the notebook covers:**

| Step | What it does |
|---|---|
| Data exploration | Visualizes class imbalance, amount/time distributions |
| Feature engineering | Creates 6 fraud-signal features from raw Time and Amount columns |
| Train/test split | Stratified 80/20 split preserving fraud ratio |
| Model training | LightGBM with `scale_pos_weight` for class imbalance |
| Evaluation | ROC-AUC, PR-AUC, confusion matrix, threshold analysis |
| SHAP | Global and per-transaction explanations |
| Save artifacts | `model.pkl`, `scaler.pkl`, `metadata.json` |

---

## The Class Imbalance Problem

This is the core challenge of fraud detection. The dataset has a **578:1 ratio** of legitimate to fraudulent transactions.

```
Legitimate: 284,315 transactions (99.83%)
Fraudulent:        492 transactions (0.17%)
```

A model that always predicts "legitimate" would be 99.83% accurate — and catch zero fraud.

**The fix:** `scale_pos_weight=578` in LightGBM tells the model to treat each fraud example as 578 times more important during training. This is why we use **ROC-AUC** instead of accuracy as our primary metric.

---

## Why SHAP Matters (Regulation)

SHAP isn't just a debugging tool — it's a compliance requirement.

Under **ECOA** (Equal Credit Opportunity Act) and **FCRA** (Fair Credit Reporting Act), if you take adverse action on a transaction or credit application, you must provide specific reasons. "Our ML model said so" is not a valid adverse action notice.

FraudLens returns the top 3 SHAP factors for every blocked transaction — the specific features that most contributed to the fraud score. These can be translated directly into compliant adverse action language.

---

## Fraud Encyclopedia

The dashboard includes a built-in reference guide covering 15 fraud types with practitioner-level detail:

**Identity Fraud (7 types)**
- Account Takeover (ATO)
- Synthetic Identity Fraud
- New Account Fraud
- SIM Swap Fraud
- Credential Stuffing
- Phishing & Social Engineering
- Medical Identity Theft

**Payment Fraud (8 types)**
- Card-Not-Present (CNP) Fraud
- Card Testing / Carding
- Chargeback / Friendly Fraud
- Authorized Push Payment (APP) Fraud
- ACH / Wire Fraud
- Refund Fraud
- Money Mule Schemes
- Buy Now Pay Later (BNPL) Fraud

Each type includes: description, detection signals, real loss figures, and industry statistics.

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| API times out on first request | Render free tier cold start | Wait 30–60 seconds and retry |
| `FileNotFoundError: creditcard.csv` | Dataset in wrong folder | Place CSV at `/content/creditcard.csv` in Colab |
| `numpy binary incompatibility` | Python version conflict | Use Google Colab instead of local Python |
| `ModuleNotFoundError` | Library not installed | Run `%pip install lightgbm shap` in Colab |
| GitHub push rejected (100MB limit) | CSV file too large | Run `git rm -r --cached data/` then push |

---

## Built By

**Animesh Kondiparthy** — Senior Product Manager
10+ years at eBay, JPMorgan Chase (WePay), Sephora  
Bay Area, California

[LinkedIn](https://linkedin.com/in/animeshkondiparthy) · [Website](https://akondiparthy.com) · [Email](mailto:akondiparthy@gmail.com)

---

## License

MIT License — use freely, attribution appreciated.
