from src.db.dq_checks import run_dq_checks


def test_run_dq_checks_passes_for_valid_payload():
    payload = {"id": 25, "name": "Pikachu", "height": 4, "weight": 60}

    issues, passed = run_dq_checks(payload)

    assert passed is True
    assert issues["errors"] == []


def test_run_dq_checks_fails_for_missing_and_invalid_fields():
    payload = {"id": 25, "name": "", "height": 0, "weight": -1}

    issues, passed = run_dq_checks(payload)

    assert passed is False
    assert any("missing field" in issue for issue in issues["errors"])
    assert any("height" in issue for issue in issues["errors"])
    assert any("weight" in issue for issue in issues["errors"])
