from app.core.db import fetch_all, fetch_one

def get_employee_metrics(employee_id: int, year: int) -> dict | None:
    rows = fetch_all("""
        SELECT completion_pct, quality_score, priority, status,
               task_date, deadline
        FROM daily_tasks
        WHERE employee_id = :eid
          AND EXTRACT(YEAR FROM task_date) = :year
    """, {"eid": employee_id, "year": year})

    if not rows:
        return None

    total = len(rows)
    completed = sum(1 for r in rows if r["status"] == "completed")
    avg_completion = sum(r["completion_pct"] for r in rows) / total
    avg_quality = sum(r["quality_score"] for r in rows) / total

    on_time = sum(
        1 for r in rows
        if r["deadline"] and r["task_date"] <= r["deadline"] and r["status"] == "completed"
    )
    eligible = sum(1 for r in rows if r["deadline"] and r["status"] == "completed")
    deadline_adherence = (on_time / eligible * 100) if eligible > 0 else 50.0

    high_priority = [r for r in rows if r["priority"] >= 4]
    high_priority_completion = (
        sum(r["completion_pct"] for r in high_priority) / len(high_priority)
        if high_priority else avg_completion
    )

    working_days = len(set(r["task_date"] for r in rows))
    productivity_raw = (total / working_days) * 20 if working_days > 0 else 0
    productivity = min(100, productivity_raw)

    return {
        "employee_id": employee_id,
        "year": year,
        "total_tasks": total,
        "task_completion": round(avg_completion, 2),
        "deadline_adherence": round(deadline_adherence, 2),
        "priority_management": round(high_priority_completion, 2),
        "work_quality": round((avg_quality / 10) * 100, 2),
        "productivity": round(productivity, 2),
    }

def get_team_task_summary(manager_id: int) -> list[dict]:
    return fetch_all("""
        SELECT u.id AS employee_id, u.name, u.email,
               COUNT(t.id) AS total_tasks,
               ROUND(AVG(t.completion_pct), 1) AS avg_completion,
               ROUND(AVG(t.quality_score), 1) AS avg_quality,
               MAX(t.task_date) AS last_entry
        FROM users u
        LEFT JOIN daily_tasks t ON t.employee_id = u.id
        WHERE u.manager_id = :mid
          AND u.is_active = TRUE
        GROUP BY u.id, u.name, u.email
        ORDER BY u.name
    """, {"mid": manager_id})

def get_employee_tasks(employee_id: int, limit: int = 30) -> list[dict]:
    return fetch_all("""
        SELECT id, task_date, task_name, priority, status,
               completion_pct, quality_score, deadline, notes
        FROM daily_tasks
        WHERE employee_id = :eid
        ORDER BY task_date DESC
        LIMIT :lim
    """, {"eid": employee_id, "lim": limit})

def get_all_employees_summary() -> list[dict]:
    return fetch_all("""
        SELECT u.id, u.name, u.email, d.name AS department,
               m.name AS manager_name,
               COUNT(t.id) AS total_tasks,
               ROUND(AVG(t.completion_pct), 1) AS avg_completion,
               e.band, e.published
        FROM users u
        JOIN roles r ON u.role_id = r.id AND r.name = 'employee'
        LEFT JOIN departments d ON u.department_id = d.id
        LEFT JOIN users m ON u.manager_id = m.id
        LEFT JOIN daily_tasks t ON t.employee_id = u.id
        LEFT JOIN evaluations e ON e.employee_id = u.id
            AND e.year = EXTRACT(YEAR FROM CURRENT_DATE)
        WHERE u.is_active = TRUE
        GROUP BY u.id, u.name, u.email, d.name, m.name, e.band, e.published
        ORDER BY d.name, u.name
    """)
