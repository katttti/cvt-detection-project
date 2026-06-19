# 송금 위험도 모델 사용법

1단계 텍스트 분류기 출력(pressure_score, category)과 송금 메타데이터를 받아 risk_score와 위험등급을 반환하는 모델.

## 입력

| 필드 | 타입 | 설명 |
|---|---|---|
| `pressure_score` | float (0~1) | 1단계 분류기의 risk_score |
| `category` | string | 게임아이템사기, 로맨스스캠, 몸캠피싱, 정상송금, 직거래사기, 협박갈취 중 하나 |
| `delta_t_sec` | float | 대화 시작~송금 요청까지 경과 시간(초) |
| `amount` | float | 송금 금액(원) |
| `prior_relation_score` | float (0~1) | 수취인과의 기존 관계 친밀도 |
| `receiver_new_flag` | bool | 처음 거래하는 수취인인지 여부 (기본값 false) |

## 출력

```json
{
  "risk_score": 0.9787,
  "risk_level": "RED",
  "factors": {
    "pressure_score": 0.82,
    "delta_t_sec": 120.0,
    "amount": 500000.0,
    "prior_relation_score": 0.1,
    "receiver_new_flag": true
  },
  "category": "직거래사기"
}
```

- `risk_score`: 0~1 사이 위험도 점수
- `risk_level`: SAFE(<0.3) / YELLOW(<0.6) / ORANGE(<0.85) / RED(≥0.85)
- `factors`: 입력으로 들어온 값 그대로 echo (디버깅/로깅용)

## 쓰는 법

### 1. 코드에서 바로 호출

```python
from infer import run

result = run({
    "pressure_score": 0.82,
    "category": "직거래사기",
    "delta_t_sec": 120,
    "amount": 500000,
    "prior_relation_score": 0.1,
    "receiver_new_flag": True,
})
```

### 2. CLI

```bash
python infer.py --input-json '{"pressure_score":0.82,"category":"직거래사기","delta_t_sec":120,"amount":500000,"prior_relation_score":0.1,"receiver_new_flag":true}'
```

### 3. API 서버

설치 없이 Docker로 바로 실행 (권장):

```bash
docker build -t transfer-risk .
docker run -p 8000:8000 transfer-risk
```

또는 Docker 없이 직접 설치:

```bash
./install.sh
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

서버 띄운 뒤 `http://<서버주소>:8000/docs` 에서 Swagger UI로 직접 테스트 가능. 실제 연동은 `POST /predict`에 위 입력 형식 그대로 JSON으로 보내면 됨.

## 파일 구성

- `gen_data.py` — 합성 학습 데이터 생성 (`data/synthetic_transfers.jsonl`)
- `train.py` — 모델 학습, `model.joblib` / `config.json` 출력
- `infer.py` — 예측 함수 및 CLI
- `app.py` — FastAPI 서버
- `model.joblib`, `config.json` — 학습된 모델과 설정 (threshold, feature 목록 등)
- `Dockerfile`, `requirements.txt`, `install.sh` — 배포/설치용

## 참고

- `amount`가 5만원 근처거나 `delta_t_sec`이 짧으면 정상송금이라도 risk_score가 다소 올라갈 수 있음 (모델이 의도적으로 그렇게 학습됨, 버그 아님).
- `receiver_new_flag=true`는 위험도를 꽤 크게 올림. 정상적인 첫 거래(중고거래 등)에서도 risk_level이 ORANGE까지 나올 수 있으니 단독 판단 근거로 쓰지 말 것.
