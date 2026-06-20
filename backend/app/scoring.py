from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    risk_score: float
    risk_level: str
    recommended_action: str
    reason_codes: list[str]


def score_risk(
    *,
    pressure_score: float,
    amount: float,
    is_new_recipient: bool,
    hour_of_day: int,
    recent_urgent_attempts: int,
) -> RiskResult:
    score = pressure_score * 100
    reason_codes: list[str] = []

    if pressure_score >= 0.8:
        reason_codes.append("pressure_high")

    if is_new_recipient:
        score += 15
        reason_codes.append("new_recipient")

    if hour_of_day <= 5 or hour_of_day >= 23:
        score += 10
        reason_codes.append("late_night_transfer")

    if amount >= 100000:
        score += 10
        reason_codes.append("large_amount")

    if recent_urgent_attempts > 0:
        score += min(recent_urgent_attempts * 5, 15)
        reason_codes.append("repeated_attempts")

    score = min(score, 100)

    if score >= 85:
        return RiskResult(
            risk_score=score,
            risk_level="red",
            recommended_action="notify_guardian",
            reason_codes=reason_codes,
        )

    if score >= 60:
        return RiskResult(
            risk_score=score,
            risk_level="orange",
            recommended_action="delay",
            reason_codes=reason_codes,
        )

    return RiskResult(
        risk_score=score,
        risk_level="yellow",
        recommended_action="warn",
        reason_codes=reason_codes,
    )
