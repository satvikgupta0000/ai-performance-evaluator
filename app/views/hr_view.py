import streamlit as st
from datetime import datetime
from app.core.parser import get_all_employees_summary
from app.core.db import fetch_all, execute
from app.core.charts import radar_chart

def render(user: dict):
    st.title(f"HR Dashboard — {user['name']}")
    tab_overview, tab_publish = st.tabs(["Company Overview", "Publish Evaluations"])

    with tab_overview:
        _company_overview()

    with tab_publish:
        _publish_evaluations()

def _company_overview():
    st.subheader("All employees — current year")
    rows = get_all_employees_summary()

    if not rows:
        st.info("No employee data found.")
        return

    band_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "🔴", None: "⚪"}
    table = []
    for r in rows:
        table.append({
            "Name":       r["name"],
            "Department": r["department"],
            "Manager":    r["manager_name"],
            "Tasks":      r["total_tasks"],
            "Avg Compl.": f"{r['avg_completion']}%" if r["avg_completion"] else "—",
            "Band":       f"{band_emoji.get(r['band'], '⚪')} {r['band']}" if r["band"] else "Not evaluated",
            "Published":  "Yes" if r["published"] else "No",
        })

    st.dataframe(table, use_container_width=True)

def _publish_evaluations():
    st.subheader("Publish / unpublish evaluation results")
    year = st.selectbox("Year", options=list(range(datetime.now().year, 2023, -1)))

    evaluations = fetch_all("""
        SELECT e.id, u.name, d.name AS department, e.band,
               e.composite_score, e.published, e.created_at
        FROM evaluations e
        JOIN users u ON e.employee_id = u.id
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE e.year = :yr
        ORDER BY d.name, u.name
    """, {"yr": year})

    if not evaluations:
        st.info(f"No evaluations found for {year}.")
        return

    unpublished = [e for e in evaluations if not e["published"]]
    published = [e for e in evaluations if e["published"]]

    if unpublished:
        st.markdown(f"**{len(unpublished)} unpublished evaluation(s)**")
        selected_ids = []
        for e in unpublished:
            checked = st.checkbox(
                f"{e['name']} ({e['department']}) — Band {e['band']} — Score {e['composite_score']}",
                key=f"pub_{e['id']}"
            )
            if checked:
                selected_ids.append(e["id"])

        if st.button("Publish selected", type="primary", disabled=not selected_ids):
            for eid in selected_ids:
                execute("""
                    UPDATE evaluations
                    SET published = TRUE, published_at = NOW()
                    WHERE id = :id
                """, {"id": eid})
            st.success(f"Published {len(selected_ids)} evaluation(s). Employees can now view their results.")
            st.rerun()

    if published:
        st.markdown(f"**{len(published)} published evaluation(s)**")
        for e in published:
            col1, col2 = st.columns([4, 1])
            col1.write(f"{e['name']} ({e['department']}) — Band {e['band']}")
            if col2.button("Unpublish", key=f"unpub_{e['id']}"):
                execute("""
                    UPDATE evaluations
                    SET published = FALSE, published_at = NULL
                    WHERE id = :id
                """, {"id": e["id"]})
                st.rerun()
