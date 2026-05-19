import json
import os
from openai import OpenAI
from app.core.parser import get_employee_metrics
from app.core.scorer import score_employee
from app.core.prompt_builder import build_prompt
from app.core.db import fetch_one, execute, execute_returning

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_evaluation(employee_id: int, year: int, triggered_by: int) -> dict:
    existing = fetch_one(
        "SELECT id FROM evaluations WHERE employee_id = :eid AND year = :yr",
        {"eid": employee_id, "yr": year}
    )
    if existing:
        return {"status": "skipped", "reason": f"Evaluation already exists for {year}"}

    metrics = get_employee_metrics(employee_id, year)
    if not metrics:
        return {"status": "skipped", "reason": "No task data found"}

    scored = score_employee(metrics)
    prompt = build_prompt(employee_id, metrics, scored)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.4,
    )
    ai_feedback = response.choices[0].message.content.strip()

    execute("""
        INSERT INTO evaluations
            (employee_id, year, band, composite_score, ai_feedback, radar_scores, triggered_by)
        VALUES
            (:eid, :yr, :band, :score, :feedback, :radar, :tby)
    """, {
        "eid":      employee_id,
        "yr":       year,
        "band":     scored["band"],
        "score":    scored["composite_score"],
        "feedback": ai_feedback,
        "radar":    json.dumps(scored["radar_scores"]),
        "tby":      triggered_by,
    })

    return {
        "status":    "success",
        "band":      scored["band"],
        "composite": scored["composite_score"],
    }

def run_team_evaluation(manager_id: int, year: int) -> list[dict]:
    from app.core.db import fetch_all
    employees = fetch_all(
        "SELECT id, name FROM users WHERE manager_id = :mid AND is_active = TRUE",
        {"mid": manager_id}
    )
    results = []
    for emp in employees:
        result = run_evaluation(emp["id"], year, triggered_by=manager_id)
        results.append({"employee": emp["name"], **result})
    return results
