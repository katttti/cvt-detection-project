"""LightGBM 송금 위험도 모델 학습. 80/10/10 split, monotone_constraints, 단조성 검증."""
import json
import os

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

SEED = 42
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "synthetic_transfers.jsonl")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

FEATURES = ["pressure_score", "delta_t_sec", "amount", "prior_relation_score", "receiver_new_flag", "category"]
# 단조 제약: pressure_score(+1), delta_t_sec(-1, 짧을수록 위험), amount(+1), prior_relation_score(-1), 나머지 0
MONOTONE_CONSTRAINTS = [1, -1, 1, -1, 0, 0]

THRESHOLDS = {"SAFE": 0.3, "YELLOW": 0.6, "ORANGE": 0.85}  # RED는 >=0.85


def load_df():
    rows = [json.loads(l) for l in open(DATA_PATH, encoding="utf-8")]
    df = pd.DataFrame(rows)
    df["receiver_new_flag"] = df["receiver_new_flag"].astype(int)
    df["category"] = df["category"].astype("category")
    return df


def to_level(score):
    if score < THRESHOLDS["SAFE"]:
        return "SAFE"
    if score < THRESHOLDS["YELLOW"]:
        return "YELLOW"
    if score < THRESHOLDS["ORANGE"]:
        return "ORANGE"
    return "RED"


def check_monotonicity(model, df, categories):
    """다른 피처를 중앙값으로 고정하고 한 피처만 스윕했을 때 예측 방향이 제약과 일치하는지 확인."""
    base = {
        "pressure_score": df["pressure_score"].median(),
        "delta_t_sec": df["delta_t_sec"].median(),
        "amount": df["amount"].median(),
        "prior_relation_score": df["prior_relation_score"].median(),
        "receiver_new_flag": 0,
        "category": categories[0],
    }
    checks = [
        ("pressure_score", np.linspace(0.0, 1.0, 20), 1),
        ("delta_t_sec", np.linspace(1.0, 30 * 24 * 3600, 20), -1),
        ("amount", np.geomspace(1000, 50_000_000, 20), 1),
        ("prior_relation_score", np.linspace(0.0, 1.0, 20), -1),
    ]
    for feat, sweep, expected_dir in checks:
        grid = pd.DataFrame([base] * len(sweep))
        grid[feat] = sweep
        grid["category"] = grid["category"].astype(pd.CategoricalDtype(categories=categories))
        preds = model.predict(grid[FEATURES])
        diffs = np.diff(preds)
        if expected_dir > 0:
            assert (diffs >= -1e-6).all(), f"{feat} 단조성 위반(증가 기대): {diffs}"
        else:
            assert (diffs <= 1e-6).all(), f"{feat} 단조성 위반(감소 기대): {diffs}"
        print(f"[check_monotonicity] {feat}: OK ({'증가' if expected_dir > 0 else '감소'})")


def main():
    df = load_df()
    categories = list(df["category"].cat.categories)
    X = df[FEATURES]
    y = df["label"]

    X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=0.2, random_state=SEED, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=SEED, stratify=y_tmp)
    print(f"[train] split: train={len(X_train)} val={len(X_val)} test={len(X_test)}")

    train_set = lgb.Dataset(X_train, label=y_train, categorical_feature=["category"])
    val_set = lgb.Dataset(X_val, label=y_val, categorical_feature=["category"], reference=train_set)

    params = dict(
        objective="binary",
        metric="auc",
        learning_rate=0.05,
        num_leaves=31,
        min_data_in_leaf=30,
        monotone_constraints=MONOTONE_CONSTRAINTS,
        seed=SEED,
        verbose=-1,
    )
    model = lgb.train(
        params,
        train_set,
        num_boost_round=500,
        valid_sets=[val_set],
        callbacks=[lgb.early_stopping(30, verbose=False), lgb.log_evaluation(0)],
    )

    test_pred = model.predict(X_test)
    auc = roc_auc_score(y_test, test_pred)
    f1 = f1_score(y_test, (test_pred >= 0.5).astype(int))
    print(f"[train] test AUC={auc:.4f} F1(threshold=0.5)={f1:.4f} best_iter={model.best_iteration}")

    check_monotonicity(model, df, categories)

    joblib.dump({"model": model, "categories": categories}, MODEL_PATH)
    config = {
        "features": FEATURES,
        "monotone_constraints": dict(zip(FEATURES, MONOTONE_CONSTRAINTS)),
        "categories": categories,
        "thresholds": THRESHOLDS,
        "levels": ["SAFE", "YELLOW", "ORANGE", "RED"],
        "test_auc": round(float(auc), 4),
        "test_f1": round(float(f1), 4),
        "best_iteration": int(model.best_iteration),
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"[train] 저장: {MODEL_PATH}, {CONFIG_PATH}")


if __name__ == "__main__":
    main()
