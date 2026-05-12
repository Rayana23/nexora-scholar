import json
import re
from io import BytesIO
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from calendar_utils import parse_ics, build_week_calendar_context
from foundry_agents import run_trainer_agent, run_dietician_agent, run_scheduler_agent
from storage_utils import append_history, get_recent_history_text


st.set_page_config(
    page_title="Nexora Scheduler",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================
# DARK UI STYLING
# =========================
st.markdown(
    """
<style>
/* Global app */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0B1020 0%, #111827 45%, #172033 100%);
    color: #F8FAFC;
}

[data-testid="stHeader"] {
    background: rgba(11, 16, 32, 0);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* General text */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #F8FAFC;
}

small {
    color: #CBD5E1;
}

/* Streamlit labels */
[data-testid="stWidgetLabel"] p {
    color: #E5E7EB !important;
    font-weight: 600;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #94A3B8 !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

.stSelectbox span {
    color: #F8FAFC !important;
}

/* Multiselect */
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

.stMultiSelect span {
    color: #F8FAFC !important;
}

/* Sliders */
.stSlider label {
    color: #E5E7EB !important;
}

/* Checkbox */
.stCheckbox label {
    color: #E5E7EB !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #CBD5E1 !important;
    background-color: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 3px solid #38BDF8 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border-radius: 12px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: #111827;
    border: 1px dashed #475569;
    border-radius: 16px;
    padding: 12px;
}

[data-testid="stFileUploader"] * {
    color: #F8FAFC !important;
}

/* Buttons */
div[data-testid="stButton"] > button {
    border-radius: 14px;
    background: linear-gradient(135deg, #4F46E5, #06B6D4);
    color: white !important;
    font-weight: 800;
    height: 48px;
    border: none;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 14px;
    background: #243447;
    color: white !important;
    font-weight: 700;
    height: 44px;
    border: 1px solid #475569;
}

/* Main hero */
.nexora-hero {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 60%, #111827 100%);
    border: 1px solid #334155;
    border-radius: 28px;
    padding: 30px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 18px 50px rgba(0,0,0,0.35);
    position: relative;
    overflow: hidden;
}

.nexora-hero:after {
    content: "";
    position: absolute;
    right: -50px;
    top: -50px;
    width: 220px;
    height: 220px;
    background: radial-gradient(circle, rgba(56,189,248,0.20), rgba(79,70,229,0.08), transparent 70%);
    border-radius: 50%;
}

.nexora-title {
    font-size: 42px;
    font-weight: 850;
    letter-spacing: -0.045em;
    margin-bottom: 6px;
    color: #FFFFFF;
}

.nexora-subtitle {
    color: #CBD5E1;
    font-size: 15px;
    max-width: 850px;
    line-height: 1.55;
}

.nexora-pill {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 999px;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.28);
    margin-right: 8px;
    margin-top: 16px;
    font-size: 12px;
    color: #E0F2FE;
}

/* Cards */
.panel-card {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.28);
}

.output-card {
    background: rgba(15, 23, 42, 0.96);
    border: 1px solid #334155;
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.28);
}

.card-title {
    font-size: 17px;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.small {
    color: #CBD5E1;
    font-size: 0.93rem;
    line-height: 1.5;
}

/* Quote */
.quote-card {
    background: linear-gradient(135deg, #FACC15 0%, #FDE68A 100%);
    border: 1px solid #FBBF24;
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 18px;
    color: #1F2937;
    box-shadow: 0 12px 30px rgba(250, 204, 21, 0.18);
}

.quote-card * {
    color: #1F2937 !important;
}

/* KPI cards */
.kpi-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.22);
}

.kpi-label {
    color: #94A3B8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.kpi-value {
    font-size: 28px;
    font-weight: 850;
    color: #FFFFFF;
}

/* Day cards */
.day-card {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 22px;
    padding: 18px;
    margin-bottom: 14px;
}

.day-card h3 {
    color: #FFFFFF;
}

/* Schedule blocks */
.block-row {
    border-left: 5px solid #CBD5E1;
    background: #0B1220;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 12px 14px;
    margin-bottom: 8px;
}

.block-row b {
    color: #FFFFFF;
}

.block-row .small {
    color: #CBD5E1;
}

.category-fixed { border-left-color: #94A3B8; }
.category-deep_work { border-left-color: #60A5FA; }
.category-admin { border-left-color: #A78BFA; }
.category-training { border-left-color: #22C55E; }
.category-recovery { border-left-color: #34D399; }
.category-meal { border-left-color: #F59E0B; }
.category-hobby { border-left-color: #F472B6; }
.category-self_care { border-left-color: #22D3EE; }
.category-sleep { border-left-color: #818CF8; }
.category-personal { border-left-color: #FB923C; }

/* Weekly report */
.report-box {
    background: #0F172A;
    border: 2px solid #475569;
    border-radius: 18px;
    padding: 0;
    overflow: hidden;
}

.report-header {
    background: #243447;
    color: white;
    padding: 26px;
    font-size: 34px;
    font-weight: 850;
    letter-spacing: -0.03em;
}

.report-body {
    padding: 24px;
}

.report-table {
    width: 100%;
    border-collapse: collapse;
}

.report-table th {
    background: #FACC15;
    color: #1F2937 !important;
    padding: 12px;
    text-align: left;
}

.report-table td {
    border-bottom: 1px solid #334155;
    padding: 12px;
    vertical-align: top;
    color: #F8FAFC !important;
}

/* Chat */
[data-testid="stChatMessage"] {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 10px;
}

[data-testid="stChatInput"] textarea {
    background-color: #111827 !important;
    color: #F8FAFC !important;
}

/* Plotly container */
.js-plotly-plot {
    background: #111827 !important;
    border-radius: 20px;
    padding: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# HELPERS
# =========================
CATEGORY_LABELS = {
    "fixed": "Fixed Event",
    "deep_work": "Deep Work",
    "admin": "Admin",
    "training": "Training",
    "recovery": "Recovery",
    "meal": "Meal",
    "hobby": "Hobby",
    "self_care": "Self-Care",
    "sleep": "Sleep",
    "personal": "Personal",
}


def label_category(category: str) -> str:
    if not category:
        return "Personal"
    clean = category.strip().lower().replace(" ", "_")
    return CATEGORY_LABELS.get(clean, clean.replace("_", " ").title())


def css_category(category: str) -> str:
    if not category:
        return "personal"
    return category.strip().lower().replace(" ", "_")


def extract_json(text: str) -> dict:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned)
        cleaned = re.sub(r"```$", "", cleaned).strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)


def minutes_between(start: str, end: str) -> int:
    try:
        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")
        mins = int((e - s).total_seconds() / 60)
        if mins < 0:
            mins += 24 * 60
        return mins
    except Exception:
        return 0


def summarize_time_distribution(schedule_data: dict) -> dict:
    totals = {}

    for day in schedule_data.get("days", []):
        for block in day.get("blocks", []):
            category = label_category(block.get("category", "personal"))
            mins = minutes_between(block.get("start", ""), block.get("end", ""))
            totals[category] = totals.get(category, 0) + mins

    return totals


def summarize_macros(meal_data: dict) -> dict:
    targets = meal_data.get("macro_targets", {})
    return {
        "Protein": targets.get("protein_g", 0),
        "Carbs": targets.get("carbs_g", 0),
        "Fat": targets.get("fat_g", 0),
    }


def donut_chart(labels, values, title):
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.62,
                textinfo="label+percent",
                hoverinfo="label+value",
            )
        ]
    )

    fig.update_layout(
        title=title,
        height=360,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#F8FAFC"),
        showlegend=True,
    )

    return fig


def create_pdf(text: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        spaceAfter=12,
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )

    story = [Paragraph("Nexora Scholar Weekly Report", title_style), Spacer(1, 10)]

    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            story.append(Spacer(1, 8))
        else:
            safe = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, body))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def schedule_to_text(schedule_data: dict) -> str:
    lines = []
    lines.append("Nexora Scholar Weekly Schedule")
    lines.append("")
    lines.append(f"Weekly motivation: {schedule_data.get('weekly_motivation', '')}")
    lines.append("")

    for day in schedule_data.get("days", []):
        lines.append(f"{day.get('day_name', '')}, {day.get('date', '')}")
        lines.append(f"Motivation: {day.get('motivation', '')}")
        for block in day.get("blocks", []):
            lines.append(
                f"- {block.get('start', '')}-{block.get('end', '')}: "
                f"{block.get('title', '')} [{label_category(block.get('category', 'personal'))}]"
            )
        lines.append(f"Reflection: {day.get('reflection_prompt', '')}")
        lines.append("")

    return "\n".join(lines)


def render_block(block: dict):
    raw_category = block.get("category", "personal")
    category_class = css_category(raw_category)
    category_label = label_category(raw_category)

    st.markdown(
        f"""
<div class="block-row category-{category_class}">
<b>{block.get("start", "")}–{block.get("end", "")}</b> &nbsp; {block.get("title", "")}<br>
<span class="small">{category_label} · {block.get("notes", "")}</span>
</div>
""",
        unsafe_allow_html=True,
    )


# =========================
# HEADER
# =========================
st.markdown(
    """
<div class="nexora-hero">
    <div class="nexora-title">Nexora Scholar</div>
    <div class="nexora-subtitle">
        Azure Foundry multi-agent planner for weekly scheduling, training, nutrition,
        recovery, deep work, and ADHD-friendly execution.
    </div>
    <span class="nexora-pill">Dashboard</span>
    <span class="nexora-pill">Weekly Report</span>
    <span class="nexora-pill">Daily View</span>
    <span class="nexora-pill">Copilot Chat</span>
</div>
""",
    unsafe_allow_html=True,
)


# =========================
# 30 / 70 LAYOUT
# =========================
left, right = st.columns([0.30, 0.70], gap="large")


# =========================
# INPUT PANEL
# =========================
with left:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Setup</div>', unsafe_allow_html=True)

    calendar_file = st.file_uploader("Upload Google Calendar export (.ics)", type=["ics"])

    yearly_fitness_goals = st.text_area(
        "Yearly fitness goals",
        height=130,
        placeholder="HYROX base, build long run from 20 km to 40 km, swim for recovery, maintain Pilates/yoga.",
    )

    current_training_level = st.text_area(
        "Current training level",
        height=100,
        placeholder="Example: I run 5–8 km comfortably, Pilates weekly, HIIT 1–2x/week.",
    )

    preferred_hobby = st.text_input(
        "Preferred weekly hobby",
        placeholder="Example: reading, music, baking, long walk",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Meals</div>', unsafe_allow_html=True)

    dietary_preferences = st.text_input(
        "Dietary preferences",
        placeholder="Example: halal, high protein, low sugar",
    )

    cuisine_preferences = st.text_input(
        "Cuisine preferences",
        placeholder="Example: Malaysian, Bangladeshi, Mediterranean",
    )

    calorie_target = st.text_input("Calorie target", placeholder="Example: 1800 kcal")
    meals_per_day = st.selectbox("Meals per day", [2, 3, 4, 5], index=1)
    meal_prep_time = st.selectbox("Meal prep time", ["15 min", "30 min", "45 min", "1 hour"], index=1)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">Planning Preferences</div>', unsafe_allow_html=True)

    wake_hour = st.slider("Start planning day from", 4, 10, 6)
    sleep_hour = st.slider("Protect sleep from", 20, 24, 23)
    stress_level = st.slider("Expected stress level", 1, 10, 6)
    adhd_friendly = st.checkbox("ADHD-friendly planning", value=True)

    weekly_tasks = st.text_area(
        "Tasks to fit this week",
        height=180,
        placeholder="Prepare slides, mark reports, grant work, groceries, cleaning, paper outline...",
    )

    generate = st.button("Generate weekly plan", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# GENERATION
# =========================
with right:
    if generate:
        if not calendar_file:
            st.error("Please upload a Google Calendar .ics file first.")
            st.stop()

        events = parse_ics(calendar_file)
        calendar_context = build_week_calendar_context(
            events,
            wake_hour=wake_hour,
            sleep_hour=sleep_hour,
        )

        previous_training = get_recent_history_text("training_history", limit=3)
        previous_meals = get_recent_history_text("meal_history", limit=3)
        previous_weekly_plans = get_recent_history_text("weekly_plans", limit=2)

        trainer_payload = f"""
Return ONLY valid JSON.

Calendar and free blocks:
{calendar_context}

Yearly fitness goals:
{yearly_fitness_goals}

Current training level:
{current_training_level}

Expected stress level:
{stress_level}/10

Previous training recommendations:
{previous_training}
"""

        with st.spinner("Trainer Agent is creating the weekly training plan..."):
            training_raw = run_trainer_agent(trainer_payload)

        training_data = extract_json(training_raw)

        dietician_payload = f"""
Return ONLY valid JSON.

Calendar and free blocks:
{calendar_context}

Training plan JSON:
{json.dumps(training_data)}

Dietary preferences:
{dietary_preferences}

Cuisine preferences:
{cuisine_preferences}

Calorie target:
{calorie_target}

Meals per day:
{meals_per_day}

Meal prep time:
{meal_prep_time}

Previous meal recommendations:
{previous_meals}
"""

        with st.spinner("Dietician Agent is planning meals..."):
            meal_raw = run_dietician_agent(dietician_payload)

        meal_data = extract_json(meal_raw)

        scheduler_payload = f"""
Return ONLY valid JSON.

Calendar and free blocks:
{calendar_context}

Training plan JSON:
{json.dumps(training_data)}

Meal plan JSON:
{json.dumps(meal_data)}

User tasks:
{weekly_tasks}

Preferred weekly hobby:
{preferred_hobby}

Stress level:
{stress_level}/10

ADHD-friendly planning:
{adhd_friendly}

Previous weekly plans:
{previous_weekly_plans}

Mandatory:
- Include one original weekly motivation sentence.
- Include one protected hobby block.
- Keep all suggested activities inside free blocks.
- Preserve fixed calendar events.
- Use proper category values, but output labels will be rendered by the app.
"""

        with st.spinner("Scheduler Agent is assembling the final schedule..."):
            schedule_raw = run_scheduler_agent(scheduler_payload)

        schedule_data = extract_json(schedule_raw)

        append_history("training_history", json.dumps(training_data))
        append_history("meal_history", json.dumps(meal_data))
        append_history("weekly_plans", json.dumps(schedule_data))

        st.session_state["training_data"] = training_data
        st.session_state["meal_data"] = meal_data
        st.session_state["schedule_data"] = schedule_data
        st.session_state["calendar_context"] = calendar_context

    # =========================
    # OUTPUT AREA
    # =========================
    if "schedule_data" not in st.session_state:
        st.markdown(
            """
<div class="output-card">
<div class="card-title">Upload your calendar and generate a weekly plan</div>
<div class="small">
The output will appear here as a modern dashboard with charts, weekly report,
daily view, and copilot chat.
</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.stop()

    schedule_data = st.session_state["schedule_data"]
    meal_data = st.session_state["meal_data"]
    training_data = st.session_state["training_data"]

    tabs = st.tabs(["Dashboard", "Weekly Report", "Daily View", "Copilot Chat", "Raw Agent Outputs"])

    # =========================
    # DASHBOARD TAB
    # =========================
    with tabs[0]:
        st.markdown(
            f"""
<div class="quote-card">
<b>Weekly Motivation</b><br>
<span style="font-size:22px;font-weight:800;">{schedule_data.get("weekly_motivation", "Small progress builds strong weeks.")}</span>
</div>
""",
            unsafe_allow_html=True,
        )

        summary = schedule_data.get("week_summary", {})

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(
                f"""
<div class="kpi-card">
<div class="kpi-label">Deep Work</div>
<div class="kpi-value">{summary.get("deep_work_hours", 0)}h</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown(
                f"""
<div class="kpi-card">
<div class="kpi-label">Training</div>
<div class="kpi-value">{summary.get("training_sessions", 0)} sessions</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with k3:
            st.markdown(
                f"""
<div class="kpi-card">
<div class="kpi-label">Recovery</div>
<div class="kpi-value">{summary.get("recovery_sessions", 0)} sessions</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with k4:
            st.markdown(
                f"""
<div class="kpi-card">
<div class="kpi-label">Hobby Blocks</div>
<div class="kpi-value">{summary.get("hobby_blocks", 0)}</div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            time_dist = summarize_time_distribution(schedule_data)
            if time_dist:
                st.plotly_chart(
                    donut_chart(
                        list(time_dist.keys()),
                        list(time_dist.values()),
                        "Weekly Time Distribution",
                    ),
                    use_container_width=True,
                )

        with chart_col2:
            macros = summarize_macros(meal_data)
            if any(macros.values()):
                st.plotly_chart(
                    donut_chart(
                        list(macros.keys()),
                        list(macros.values()),
                        "Meal Macro Targets",
                    ),
                    use_container_width=True,
                )

        st.markdown("### Weekly Schedule Cards")

        for day in schedule_data.get("days", []):
            st.markdown(
                f"""
<div class="day-card">
<h3>{day.get("day_name", "")}, {day.get("date", "")}</h3>
<div class="small">{day.get("motivation", "")}</div>
</div>
""",
                unsafe_allow_html=True,
            )

            for block in day.get("blocks", []):
                render_block(block)

    # =========================
    # WEEKLY REPORT TAB
    # =========================
    with tabs[1]:
        st.markdown(
            """
<div class="report-box">
<div class="report-header">Weekly Progress Report</div>
<div class="report-body">
""",
            unsafe_allow_html=True,
        )

        st.markdown(f"**Motivation:** {schedule_data.get('weekly_motivation', '')}")

        table_rows = ""

        for day in schedule_data.get("days", []):
            tasks_html = "<br>".join(
                [
                    f"{block.get('start', '')}-{block.get('end', '')}: "
                    f"{block.get('title', '')} ({label_category(block.get('category', 'personal'))})"
                    for block in day.get("blocks", [])
                ]
            )

            table_rows += f"""
<tr>
<td><b>{day.get("day_name", "")}</b><br>{day.get("date", "")}</td>
<td>{tasks_html}</td>
<td>{day.get("reflection_prompt", "")}</td>
</tr>
"""

        st.markdown(
            f"""
<table class="report-table">
<tr>
<th>Date</th>
<th>Schedule</th>
<th>Reflection</th>
</tr>
{table_rows}
</table>
</div>
</div>
""",
            unsafe_allow_html=True,
        )

        pdf_text = schedule_to_text(schedule_data)
        pdf = create_pdf(pdf_text)

        st.download_button(
            "Download weekly report as PDF",
            data=pdf,
            file_name="nexora_weekly_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # =========================
    # DAILY VIEW TAB
    # =========================
    with tabs[2]:
        days = schedule_data.get("days", [])
        labels = [f"{d.get('day_name', '')}, {d.get('date', '')}" for d in days]

        selected = st.selectbox("Choose a day", labels)

        selected_day = None
        for day in days:
            label = f"{day.get('day_name', '')}, {day.get('date', '')}"
            if label == selected:
                selected_day = day
                break

        if selected_day:
            st.markdown(
                f"""
<div class="output-card">
<h2>{selected_day.get("day_name", "")}, {selected_day.get("date", "")}</h2>
<div class="small">{selected_day.get("motivation", "")}</div>
</div>
""",
                unsafe_allow_html=True,
            )

            for block in selected_day.get("blocks", []):
                render_block(block)

            st.markdown("### Meals")
            for meal in selected_day.get("meals", []):
                st.markdown(f"**{meal.get('meal_type', '').title()}**")
                for option in meal.get("options", []):
                    st.markdown(
                        f"- {option.get('name', '')}: {option.get('recipe', '')} "
                        f"({option.get('protein_g', 0)}g protein, {option.get('carbs_g', 0)}g carbs, {option.get('fat_g', 0)}g fat)"
                    )

    # =========================
    # CHAT TAB
    # =========================
    with tabs[3]:
        st.markdown(
            """
<div class="output-card">
<div class="card-title">Copilot Chat</div>
<div class="small">
Ask for adjustments like: “Move my run to Thursday”, “Make Wednesday lighter”,
“Reduce cooking time”, or “Add more protein”.
</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = []

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_msg = st.chat_input("Ask Nexora Scholar to adjust your plan...")

        if user_msg:
            st.session_state["chat_messages"].append({"role": "user", "content": user_msg})

            with st.chat_message("user"):
                st.markdown(user_msg)

            chat_payload = f"""
You are updating an existing weekly schedule.

Current schedule JSON:
{json.dumps(st.session_state["schedule_data"])}

Meal plan JSON:
{json.dumps(st.session_state["meal_data"])}

Training plan JSON:
{json.dumps(st.session_state["training_data"])}

Calendar and free blocks:
{st.session_state.get("calendar_context", "")}

User request:
{user_msg}

Rules:
- Return ONLY updated schedule JSON using the same schema.
- Do not return markdown.
- Do not explain reasoning.
- Preserve calendar events.
- Do not schedule outside free blocks.
"""

            with st.spinner("Updating schedule..."):
                updated_raw = run_scheduler_agent(chat_payload)

            updated_schedule = extract_json(updated_raw)
            st.session_state["schedule_data"] = updated_schedule

            assistant_text = "Updated your weekly schedule. Go back to Dashboard or Weekly Report to view the revised plan."
            st.session_state["chat_messages"].append({"role": "assistant", "content": assistant_text})

            with st.chat_message("assistant"):
                st.markdown(assistant_text)

    # =========================
    # RAW OUTPUTS TAB
    # =========================
    with tabs[4]:
        with st.expander("Training Agent JSON"):
            st.json(training_data)

        with st.expander("Dietician Agent JSON"):
            st.json(meal_data)

        with st.expander("Scheduler Agent JSON"):
            st.json(schedule_data)