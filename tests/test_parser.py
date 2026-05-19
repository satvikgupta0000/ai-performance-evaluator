from datetime import date, timedelta
from app.core.scorer import compute_composite, get_band

def simulate_metrics(rows: list[dict]) -> dict:
    total = len(rows)
    avg_completion = sum(r["completion_pct"] for r in rows) / total
    avg_quality = sum(r["quality_score"] for r in rows) / total

    on_time = sum(
        1 for r in rows
        if r.get("deadline") and r["task_date"] <= r["deadline"] and r["status"] == "completed"
    )
    eligible = sum(1 for r in rows if r.get("deadline") and r["status"] == "completed")
    deadline_adherence = (on_time / eligible * 100) if eligible > 0 else 50.0

    high_priority = [r for r in rows if r["priority"] >= 4]
    high_priority_completion = (
        sum(r["completion_pct"] for r in high_priority) / len(high_priority)
        if high_priority else avg_completion
    )

    working_days = len(set(r["task_date"] for r in rows))
    productivity = min(100, (total / working_days) * 20 if working_days > 0 else 0)

    return {
        "task_completion": round(avg_completion, 2),
        "deadline_adherence": round(deadline_adherence, 2),
        "priority_management": round(high_priority_completion, 2),
        "work_quality": round((avg_quality / 10) * 100, 2),
        "productivity": round(productivity, 2),
    }

def make_row(completion=100, quality=9, priority=3, status="completed",
             days_offset=0, deadline_offset=1):
    today = date.today()
    task_date = today - timedelta(days=days_offset)
    return {
        "completion_pct": completion,
        "quality_score": quality,
        "priority": priority,
        "status": status,
        "task_date": task_date,
        "deadline": task_date + timedelta(days=deadline_offset),
    }

def test_perfect_employee():
    rows = [make_row(100, 10, 5, "completed", i) for i in range(10)]
    metrics = simulate_metrics(rows)
    assert metrics["task_completion"] == 100.0
    assert metrics["work_quality"] == 100.0
    composite = compute_composite(metrics)
    band, _ = get_band(composite)
    assert band == "A"

def test_poor_employee():
    rows = [make_row(20, 2, 1, "in_progress", i, 5) for i in range(10)]
    metrics = simulate_metrics(rows)
    assert metrics["task_completion"] == 20.0
    composite = compute_composite(metrics)
    band, _ = get_band(composite)
    assert band in ("C", "D")

def test_deadline_adherence_all_on_time():
    rows = [make_row(100, 8, 3, "completed", i, 2) for i in range(5)]
    metrics = simulate_metrics(rows)
    assert metrics["deadline_adherence"] == 100.0

def test_productivity_capped_at_100():
    rows = [make_row(100, 9, 3, "completed", 0) for _ in range(10)]
    metrics = simulate_metrics(rows)
    assert metrics["productivity"] == 100.0

def test_no_high_priority_uses_avg():
    rows = [make_row(70, 7, 2, "completed", i) for i in range(5)]
    metrics = simulate_metrics(rows)
    assert metrics["priority_management"] == metrics["task_completion"]
