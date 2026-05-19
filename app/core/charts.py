import json
import plotly.graph_objects as go

DIMENSIONS = [
    "task_completion",
    "deadline_adherence",
    "priority_management",
    "work_quality",
    "productivity",
]

LABELS = [
    "Task Completion",
    "Deadline Adherence",
    "Priority Management",
    "Work Quality",
    "Productivity",
]

BAND_COLORS = {
    "A": "#1D9E75",
    "B": "#378ADD",
    "C": "#EF9F27",
    "D": "#E24B4A",
}

def radar_chart(radar_scores: dict | str, band: str, employee_name: str) -> go.Figure:
    if isinstance(radar_scores, str):
        radar_scores = json.loads(radar_scores)

    values = [radar_scores.get(dim, 0) for dim in DIMENSIONS]
    values_closed = values + [values[0]]
    labels_closed = LABELS + [LABELS[0]]

    color = BAND_COLORS.get(band, "#888780")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor=color,
        opacity=0.25,
        line=dict(color=color, width=2),
        name=employee_name,
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor="#D3D1C7",
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text=f"{employee_name} — Band {band}",
            font=dict(size=14),
            x=0.5,
        ),
    )
    return fig
