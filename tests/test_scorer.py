from app.core.scorer import compute_composite, get_band, score_employee

def make_metrics(tc=80, da=80, pm=80, wq=80, pr=80):
    return {
        "task_completion": tc,
        "deadline_adherence": da,
        "priority_management": pm,
        "work_quality": wq,
        "productivity": pr,
    }

def test_composite_all_100():
    assert compute_composite(make_metrics(100, 100, 100, 100, 100)) == 100.0

def test_composite_all_0():
    assert compute_composite(make_metrics(0, 0, 0, 0, 0)) == 0.0

def test_composite_weighted():
    metrics = make_metrics(tc=100, da=0, pm=0, wq=0, pr=0)
    assert compute_composite(metrics) == 25.0

def test_band_A():
    band, label = get_band(90)
    assert band == "A"
    assert "Exceeds" in label

def test_band_B():
    band, _ = get_band(75)
    assert band == "B"

def test_band_C():
    band, _ = get_band(60)
    assert band == "C"

def test_band_D():
    band, _ = get_band(40)
    assert band == "D"

def test_band_boundary_85():
    band, _ = get_band(85)
    assert band == "A"

def test_band_boundary_84():
    band, _ = get_band(84)
    assert band == "B"

def test_score_employee_returns_all_keys():
    result = score_employee(make_metrics())
    assert "band" in result
    assert "composite_score" in result
    assert "band_label" in result
    assert "radar_scores" in result

def test_radar_scores_keys():
    result = score_employee(make_metrics())
    expected_keys = {"task_completion", "deadline_adherence",
                     "priority_management", "work_quality", "productivity"}
    assert set(result["radar_scores"].keys()) == expected_keys
