from app.core.db import fetch_one

def build_prompt(employee_id: int, metrics: dict, scored: dict) -> str:
    user = fetch_one("""
        SELECT u.name, d.name AS department
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.id = :eid
    """, {"eid": employee_id})

    name = user["name"] if user else "the employee"
    dept = user["department"] if user else "the department"

    radar = scored["radar_scores"]

    return f"""You are an experienced HR analyst writing a professional performance evaluation.

Employee: {name}
Department: {dept}
Evaluation Year: {metrics['year']}

Performance Metrics (scored 0-100):
- Task Completion Rate: {radar['task_completion']}
- Deadline Adherence: {radar['deadline_adherence']}
- Priority Management: {radar['priority_management']}
- Work Quality: {radar['work_quality']}
- Productivity: {radar['productivity']}

Composite Score: {scored['composite_score']} / 100
Band Assigned: {scored['band']} — {scored['band_label']}
Total Tasks Logged: {metrics['total_tasks']}

Write a professional 3-sentence performance feedback paragraph for {name}.
- Sentence 1: Acknowledge their strongest dimension with a specific reference to the score.
- Sentence 2: Identify the area needing the most improvement with constructive framing.
- Sentence 3: Give a forward-looking recommendation aligned with their band.

Write only the paragraph. No headings, no bullet points, no preamble.
"""
