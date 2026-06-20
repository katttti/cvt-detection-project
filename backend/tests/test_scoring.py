from backend.app.scoring import score_risk


def test_score_risk_returns_red_for_high_pressure_new_recipient_late_night_transfer():
    result = score_risk(
        pressure_score=0.85,
        amount=120000,
        is_new_recipient=True,
        hour_of_day=1,
        recent_urgent_attempts=2,
    )

    assert result.risk_level == "red"
    assert result.recommended_action == "notify_guardian"
    assert "pressure_high" in result.reason_codes
    assert "new_recipient" in result.reason_codes
