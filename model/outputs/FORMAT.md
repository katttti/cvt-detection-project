# 입력/출력 형식

## 입력 (JSON)

```json
[
  {"speaker": "화자1", "text": "메시지 내용1"},
  {"speaker": "화자2", "text": "메시지 내용2"}
]
```

- `speaker`: 등장 순서대로 화자1, 화자2, ... 로 넣어주세요 (실제 사용자 이름/역할명 X)
- `text`: 메시지 원문

## 출력 (JSON)

```json
{
  "is_risk": 1,
  "category": "직거래사기",
  "risk_score": 0.99,
  "category_confidence": 0.99
}
```

- `is_risk`: 0 또는 1 (위험 여부, threshold 0.5)
- `category`: 8개 중 하나 — 게임사기, 쇼핑몰사기, 연예빙자로맨스, 일반일상, 정상송금, 지인사칭, 직거래사기, 투자사기
- `risk_score`: 0~1 사이 위험도 점수 (pressure_score로 그대로 사용 가능)
- `category_confidence`: 0~1 사이 카테고리 예측 확신도

## 모델 입출력 텐서 스펙

| | 이름 | shape | dtype |
|---|---|---|---|
| 입력 | `input_ids` | [1, 320] | int32 |
| 입력 | `attention_mask` | [1, 320] | int32 |
| 출력 | `category_logits` | [1, 8] | float32 (softmax 적용 전) |
| 출력 | `risk_logit` | [1, 1] | float32 (sigmoid 적용 전) |

토크나이즈는 `vocab.txt`(WordPiece) 사용, `do_lower_case=false`, 320 토큰 초과 시 뒤쪽(최근 메시지) 유지.