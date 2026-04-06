from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from api.schemas import TransactionRequest, FraudResponse
from api.predictor import predictor

app = FastAPI(
    title="Payment Fraud Detection API",
    description="Real-time fraud scoring with SHAP explanations",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "healthy", "model_version": "v1.0"}

@app.post("/predict", response_model=FraudResponse)
def predict(transaction: TransactionRequest):
    try:
        result = predictor.predict(transaction.model_dump())
        return FraudResponse(
            transaction_id=transaction.transaction_id,
            evaluated_at=datetime.now(timezone.utc),
            **result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))