"""1단계 분류기 출력 + 송금 메타데이터 -> risk_score/risk_level.
입력: pressure_score, category, delta_t_sec, amount, prior_relation_score, (선택)receiver_new_flag
"""
import argparse
import json
import os

import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load():
    bundle = joblib.load(MODEL_PATH)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    return bundle["model"], bundle["categories"], config


def to_level(score, thresholds):
    if score < thresholds["SAFE"]:
        return "SAFE"
    if score < thresholds["YELLOW"]:
        return "YELLOW"
    if score < thresholds["ORANGE"]:
        return "ORANGE"
    return "RED"


def run(features, model=None, categories=None, config=None):
    if model is None:
        model, categories, config = load()

    row = {
        "pressure_score": float(features["pressure_score"]),
        "delta_t_sec": float(features["delta_t_sec"]),
        "amount": float(features["amount"]),
        "prior_relation_score": float(features["prior_relation_score"]),
        "receiver_new_flag": int(features.get("receiver_new_flag", 0)),
        "category": features["category"],
    }
    X = pd.DataFrame([row])
    X["category"] = X["category"].astype(pd.CategoricalDtype(categories=categories))

    score = float(model.predict(X)[0])
    level = to_level(score, config["thresholds"])

    return {
        "risk_score": round(score, 4),
        "risk_level": level,
        "factors": {
            "pressure_score": row["pressure_score"],
            "delta_t_sec": row["delta_t_sec"],
            "amount": row["amount"],
            "prior_relation_score": row["prior_relation_score"],
            "receiver_new_flag": bool(row["receiver_new_flag"]),
        },
        "category": row["category"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True, help="피처 JSON 파일 경로 또는 JSON 문자열")
    args = parser.parse_args()

    if os.path.exists(args.input_json):
        with open(args.input_json, encoding="utf-8") as f:
            features = json.load(f)
    else:
        features = json.loads(args.input_json)

    result = run(features)
    print(json.dumps(result, ensure_ascii=False, indent=2))
