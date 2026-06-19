"""송금 위험도 모델 API. 실행: uvicorn app:app --host 0.0.0.0 --port 8000
Swagger UI: http://localhost:8000/docs
"""
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from infer import load, run

app = FastAPI(
    title="Transfer Risk API",
    description="1단계 분류기 출력 + 송금 메타데이터를 받아 risk_score/risk_level을 반환합니다.",
    version="1.0.0",
)

_model, _categories, _config = load()


class TransferRiskRequest(BaseModel):
    pressure_score: float = Field(..., ge=0, le=1, description="1단계 텍스트 분류기의 위험도 점수(0~1)")
    category: str = Field(..., description=f"카테고리, 다음 중 하나: {_categories}")
    delta_t_sec: float = Field(..., ge=0, description="대화 시작~송금 요청 시점까지 경과 시간(초)")
    amount: float = Field(..., gt=0, description="송금 금액(원)")
    prior_relation_score: float = Field(..., ge=0, le=1, description="수취인과의 기존 관계 친밀도(0~1)")
    receiver_new_flag: bool = Field(False, description="이전에 거래한 적 없는 신규 수취인인지 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "pressure_score": 0.82,
                "category": "직거래사기",
                "delta_t_sec": 120,
                "amount": 500000,
                "prior_relation_score": 0.1,
                "receiver_new_flag": True,
            }
        }


class TransferRiskResponse(BaseModel):
    risk_score: float
    risk_level: Literal["SAFE", "YELLOW", "ORANGE", "RED"]
    factors: dict
    category: str


@app.get("/health", tags=["health"], summary="헬스체크")
def health():
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=TransferRiskResponse,
    tags=["risk"],
    summary="송금 위험도 예측",
    description="1단계 텍스트 분류기 출력(pressure_score, category)과 송금 메타데이터를 받아 risk_score(0~1)와 risk_level(SAFE/YELLOW/ORANGE/RED)을 반환합니다.",
)
def predict(req: TransferRiskRequest):
    return run(req.model_dump(), model=_model, categories=_categories, config=_config)
