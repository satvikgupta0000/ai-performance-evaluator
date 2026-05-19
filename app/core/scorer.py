WEIGHTS = {
    "task_completion":    0.25,
    "deadline_adherence": 0.25,
    "priority_management":0.20,
    "work_quality":       0.20,
    "productivity":       0.10,
}

BAND_THRESHOLDS = [
    (85, "A", "Exceeds Expectations"),
    (70, "B", "Meets Expectations"),
    (55, "C", "Partially Meets Expectations"),
    (0,  "D", "Below Expectations"),
]

def compute_composite(metrics: dict) -> float:
    return round(sum(
        metrics[dim] * weight
        for dim, weight in WEIGHTS.items()
    ), 2)

def get_band(composite: float) -> tuple[str, str]:
    for threshold, band, label in BAND_THRESHOLDS:
        if composite >= threshold:
            return band, label
    return "D", "Below Expectations"

def score_employee(metrics: dict) -> dict:
    composite = compute_composite(metrics)
    band, band_label = get_band(composite)

    radar_scores = {
        "task_completion":     metrics["task_completion"],
        "deadline_adherence":  metrics["deadline_adherence"],
        "priority_management": metrics["priority_management"],
        "work_quality":        metrics["work_quality"],
        "productivity":        metrics["productivity"],
    }

    return {
        "composite_score": composite,
        "band": band,
        "band_label": band_label,
        "radar_scores": radar_scores,
    }
