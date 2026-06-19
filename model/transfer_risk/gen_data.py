"""합성 송금 위험도 데이터 생성. data/synthetic_transfers.jsonl (~10000건, seed=42)."""
import json
import os

import numpy as np

SEED = 42
N_TOTAL = 10000
OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "synthetic_transfers.jsonl")

# 시나리오별 (pressure, delta_t, amount, prior_relation, receiver_new_flag) 분포 파라미터
SCENARIOS = {
    "정상송금": dict(
        weight=0.40,
        pressure=("beta", 1.0, 9.0),
        delta_t=("lognormal", 6.0, 2.0),  # 보통 수초~수분, 가끔 수시간~수일(예약송금 등)
        amount=("lognormal", 9.5, 0.8),
        prior_relation=("beta", 9.0, 1.2),
        new_flag_p=0.03,
    ),
    "직거래사기": dict(
        weight=0.12,
        pressure=("beta", 4.0, 2.5),
        delta_t=("lognormal", 6.0, 1.2),
        amount=("lognormal", 11.0, 0.9),
        prior_relation=("beta", 1.5, 4.0),
        new_flag_p=0.7,
    ),
    "협박갈취": dict(
        weight=0.10,
        pressure=("beta", 7.0, 1.5),
        delta_t=("lognormal", 4.5, 1.0),
        amount=("lognormal", 11.5, 1.1),
        prior_relation=("beta", 1.2, 3.0),
        new_flag_p=0.5,
    ),
    "로맨스스캠": dict(
        weight=0.13,
        pressure=("beta", 5.5, 2.5),
        delta_t=("lognormal", 7.0, 1.3),
        amount=("lognormal", 12.0, 1.0),
        prior_relation=("beta", 3.0, 2.0),  # "친밀해 보이지만" 짧은 실제 관계
        new_flag_p=0.6,
    ),
    "몸캠피싱": dict(
        weight=0.10,
        pressure=("beta", 8.0, 1.3),
        delta_t=("lognormal", 4.0, 1.0),
        amount=("lognormal", 10.8, 1.0),
        prior_relation=("beta", 1.2, 4.0),
        new_flag_p=0.8,
    ),
    "게임아이템사기": dict(
        weight=0.15,
        pressure=("beta", 3.5, 3.0),
        delta_t=("lognormal", 6.5, 1.2),
        amount=("lognormal", 9.5, 0.9),
        prior_relation=("beta", 2.0, 3.0),
        new_flag_p=0.65,
    ),
}


def sample_dist(rng, spec, size):
    kind = spec[0]
    if kind == "beta":
        return rng.beta(spec[1], spec[2], size=size)
    if kind == "lognormal":
        return rng.lognormal(spec[1], spec[2], size=size)
    raise ValueError(kind)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    rng = np.random.default_rng(SEED)
    names = list(SCENARIOS.keys())
    weights = np.array([SCENARIOS[n]["weight"] for n in names])
    weights = weights / weights.sum()
    counts = rng.multinomial(N_TOTAL, weights)

    rows = []
    for name, n in zip(names, counts):
        spec = SCENARIOS[name]
        pressure = np.clip(sample_dist(rng, spec["pressure"], n), 0.0, 1.0)
        delta_t = np.clip(sample_dist(rng, spec["delta_t"], n), 1.0, 30 * 24 * 3600)
        amount = np.clip(sample_dist(rng, spec["amount"], n), 1000, 50_000_000)
        prior_relation = np.clip(sample_dist(rng, spec["prior_relation"], n), 0.0, 1.0)
        new_flag = rng.random(n) < spec["new_flag_p"]

        risk_prob = sigmoid(
            -2
            + 3 * pressure
            + 1.6 * np.exp(-delta_t / 600)
            + 1.4 * sigmoid((np.log10(amount) - np.log10(50000)) / 0.4)
            + 1.2 * new_flag.astype(float)
            + 1.0 * (1 - prior_relation)
        )
        label = (rng.random(n) < risk_prob).astype(int)

        for i in range(n):
            rows.append(
                {
                    "category": name,
                    "pressure_score": round(float(pressure[i]), 4),
                    "delta_t_sec": round(float(delta_t[i]), 1),
                    "amount": round(float(amount[i]), 0),
                    "prior_relation_score": round(float(prior_relation[i]), 4),
                    "receiver_new_flag": bool(new_flag[i]),
                    "risk_prob": round(float(risk_prob[i]), 4),
                    "label": int(label[i]),
                }
            )

    order = rng.permutation(len(rows))
    rows = [rows[i] for i in order]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[gen_data] 저장: {OUT_PATH} (n={len(rows)})")
    print(f"[gen_data] 라벨 비율: positive={sum(r['label'] for r in rows)} ({sum(r['label'] for r in rows)/len(rows):.3f})")
    print("[gen_data] 시나리오별 건수 및 라벨 비율:")
    for name in names:
        sub = [r for r in rows if r["category"] == name]
        pos_rate = sum(r["label"] for r in sub) / len(sub)
        print(f"  - {name}: n={len(sub)}, positive_rate={pos_rate:.3f}")


if __name__ == "__main__":
    main()
