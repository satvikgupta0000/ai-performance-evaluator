import streamlit as st
from datetime import date, timedelta
from app.core.db import fetch_one, execute
from app.core.parser import get_employee_tasks
from app.core.charts import radar_chart

PRIORITY_LABELS = {1: "Low", 2: "Below Average", 3: "Medium", 4: "High", 5: "Critical"}
STATUS_OPTIONS = ["not_started", "in_progress", "completed", "blocked"]

def render(user: dict):
    st.title(f"Welcome, {user['name']}")
    tab_form, tab_history, tab_result = st.tabs(["Log Today's Task", "My Task History", "My Evaluation"])

    with tab_form:
        _task_form(user)

    with tab_history:
        _task_history(user)

    with tab_result:
        _evaluation_result(user)

def _task_form(user: dict):
    st.subheader("Log a task")
    with st.form("task_form", clear_on_submit=True):
        task_name = st.text_input("Task name", max_chars=255)
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("Priority", options=list(PRIORITY_LABELS.keys()),
                                    format_func=lambda x: f"{x} — {PRIORITY_LABELS[x]}")
            status = st.selectbox("Status", options=STATUS_OPTIONS)
        with col2:
            completion_pct = st.slider("Completion %", 0, 100, 50)
            quality_score = st.slider("Quality score (1–10)", 1, 10, 7)

        deadline = st.date_input("Deadline", value=date.today() + timedelta(days=3))
        notes = st.text_area("Notes (optional)", max_chars=500)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not task_name.strip():
            st.error("Task name cannot be empty.")
            return

        execute("""
            INSERT INTO daily_tasks
                (employee_id, task_date, task_name, priority, status,
                 completion_pct, quality_score, deadline, notes)
            VALUES
                (:eid, :td, :tn, :pr, :st, :cp, :qs, :dl, :nt)
        """, {
            "eid": user["id"], "td": date.today(), "tn": task_name.strip(),
            "pr": priority, "st": status, "cp": completion_pct,
            "qs": quality_score, "dl": deadline, "nt": notes or None,
        })
        st.success("Task logged successfully.")

def _task_history(user: dict):
    st.subheader("Recent tasks (last 30 entries)")
    tasks = get_employee_tasks(user["id"], limit=30)
    if not tasks:
        st.info("No tasks logged yet.")
        return

    for t in tasks:
        with st.expander(f"{t['task_date']} — {t['task_name']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Completion", f"{t['completion_pct']}%")
            c2.metric("Quality", f"{t['quality_score']}/10")
            c3.metric("Priority", PRIORITY_LABELS.get(t["priority"], t["priority"]))
            st.caption(f"Status: {t['status']}  |  Deadline: {t['deadline']}")
            if t["notes"]:
                st.write(t["notes"])

def _evaluation_result(user: dict):
    st.subheader("My annual evaluation")
    from datetime import datetime
    year = datetime.now().year

    evaluation = fetch_one("""
        SELECT band, composite_score, ai_feedback, radar_scores, published_at
        FROM evaluations
        WHERE employee_id = :eid AND year = :yr AND published = TRUE
    """, {"eid": user["id"], "yr": year})

    if not evaluation:
        st.info("Your evaluation for this year has not been published yet.")
        return

    band_colors = {"A": "green", "B": "blue", "C": "orange", "D": "red"}
    color = band_colors.get(evaluation["band"], "gray")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### Band")
        st.markdown(
            f"<h1 style='color:{color};font-size:64px;margin:0'>{evaluation['band']}</h1>",
            unsafe_allow_html=True
        )
        st.metric("Composite score", f"{evaluation['composite_score']} / 100")
        st.caption(f"Published on {evaluation['published_at'].strftime('%d %b %Y')}")

    with col2:
        fig = radar_chart(evaluation["radar_scores"], evaluation["band"], user["name"])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("**Feedback**")
    st.write(evaluation["ai_feedback"])
