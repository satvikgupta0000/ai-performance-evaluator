import streamlit as st
from datetime import datetime
from app.core.parser import get_team_task_summary
from app.core.evaluator import run_team_evaluation
from app.core.db import fetch_all, fetch_one
from app.core.charts import radar_chart

def render(user: dict):
    st.title(f"Manager Dashboard — {user['name']}")
    tab_team, tab_eval, tab_results = st.tabs(["My Team", "Run Evaluation", "Evaluation Results"])

    with tab_team:
        _team_overview(user)

    with tab_eval:
        _trigger_evaluation(user)

    with tab_results:
        _team_results(user)

def _team_overview(user: dict):
    st.subheader("Team task summary")
    summary = get_team_task_summary(user["id"])

    if not summary:
        st.info("No team members found.")
        return

    for emp in summary:
        with st.expander(f"{emp['name']} — {emp['total_tasks']} tasks logged"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total tasks", emp["total_tasks"])
            c2.metric("Avg completion", f"{emp['avg_completion']}%")
            c3.metric("Avg quality", f"{emp['avg_quality']}/10")
            c4.metric("Last entry", str(emp["last_entry"]) if emp["last_entry"] else "—")

def _trigger_evaluation(user: dict):
    st.subheader("Run annual evaluation for your team")
    year = datetime.now().year

    existing = fetch_all("""
        SELECT u.name, e.band, e.composite_score, e.published
        FROM evaluations e
        JOIN users u ON e.employee_id = u.id
        WHERE u.manager_id = :mid AND e.year = :yr
    """, {"mid": user["id"], "yr": year})

    if existing:
        st.info(f"Evaluation for {year} already exists for {len(existing)} team member(s).")
        st.dataframe(
            [{"Name": r["name"], "Band": r["band"],
              "Score": r["composite_score"], "Published": r["published"]}
             for r in existing],
            use_container_width=True
        )
        return

    team = get_team_task_summary(user["id"])
    eligible = [e for e in team if e["total_tasks"] > 0]
    no_data = [e for e in team if e["total_tasks"] == 0]

    if no_data:
        st.warning(f"{len(no_data)} member(s) have no task data: {', '.join(e['name'] for e in no_data)}")

    if not eligible:
        st.error("No team members have task data. Evaluation cannot be run.")
        return

    st.write(f"Ready to evaluate **{len(eligible)}** team member(s) for **{year}**.")

    if st.button("Run evaluation", type="primary"):
        with st.spinner("Running evaluations via GPT-4o..."):
            results = run_team_evaluation(user["id"], year)

        for r in results:
            if r["status"] == "success":
                st.success(f"{r['employee']}: Band {r['band']} ({r['composite']})")
            elif r["status"] == "skipped":
                st.warning(f"{r['employee']}: Skipped — {r['reason']}")
            else:
                st.error(f"{r['employee']}: Failed")

def _team_results(user: dict):
    st.subheader("Team evaluation results")
    year = st.selectbox("Year", options=list(range(datetime.now().year, 2023, -1)))

    results = fetch_all("""
        SELECT u.name, e.band, e.composite_score, e.ai_feedback,
               e.radar_scores, e.published, e.published_at, e.created_at
        FROM evaluations e
        JOIN users u ON e.employee_id = u.id
        WHERE u.manager_id = :mid AND e.year = :yr
        ORDER BY e.composite_score DESC
    """, {"mid": user["id"], "yr": year})

    if not results:
        st.info(f"No evaluations found for {year}.")
        return

    selected_name = st.selectbox("Select employee", [r["name"] for r in results])
    emp = next(r for r in results if r["name"] == selected_name)

    col1, col2 = st.columns([1, 2])
    with col1:
        band_colors = {"A": "green", "B": "blue", "C": "orange", "D": "red"}
        color = band_colors.get(emp["band"], "gray")
        st.markdown(f"<h1 style='color:{color};font-size:64px'>{emp['band']}</h1>",
                    unsafe_allow_html=True)
        st.metric("Score", f"{emp['composite_score']} / 100")
        st.caption(f"Published: {'Yes' if emp['published'] else 'No'}")

    with col2:
        fig = radar_chart(emp["radar_scores"], emp["band"], emp["name"])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**AI Feedback**")
    st.write(emp["ai_feedback"])
