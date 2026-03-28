"""
dashboard/app.py
Personal productivity dashboard — styled to DKM brand palette.
Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date
from processor import daily_summary, weekly_summary, peak_focus_hours, top_distractions


# ── DKM Brand Colors ──────────────────────────────────────────────────────────

DKM_BLUE     = "#1B4F8A"
DKM_GREEN    = "#4CAF50"
DKM_WHITE    = "#FFFFFF"
DKM_LIGHT    = "#F4F7FB"
DKM_NAVY     = "#1A1A2E"
DKM_GRAY     = "#6B7280"
DKM_BORDER   = "#D1DCF0"

CATEGORY_COLORS = {
    "Work":          DKM_BLUE,
    "Learning":      DKM_GREEN,
    "Communication": "#2196F3",
    "Distraction":   "#E53935",
    "Idle":          "#B0BEC5",
}


# ── Page Config & Global Styles ───────────────────────────────────────────────

st.set_page_config(page_title="Pulse — DKM", layout="centered", page_icon="⚡")

st.markdown(f"""
<style>
    /* Background */
    .stApp {{ background-color: {DKM_LIGHT}; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background-color: {DKM_BLUE}; }}

    /* Main header */
    .main-header {{
        background-color: {DKM_BLUE};
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .main-header h1 {{
        color: {DKM_WHITE};
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    .main-header p {{
        color: rgba(255,255,255,0.7);
        font-size: 13px;
        margin: 4px 0 0;
    }}

    /* Metric cards */
    .metric-card {{
        background: {DKM_WHITE};
        border: 1px solid {DKM_BORDER};
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 700;
        color: {DKM_BLUE};
    }}
    .metric-label {{
        font-size: 12px;
        color: {DKM_GRAY};
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* Section headers */
    .section-title {{
        font-size: 16px;
        font-weight: 600;
        color: {DKM_NAVY};
        border-left: 4px solid {DKM_BLUE};
        padding-left: 10px;
        margin: 28px 0 14px;
    }}

    /* Info box */
    .info-box {{
        background: {DKM_WHITE};
        border: 1px solid {DKM_BORDER};
        border-radius: 10px;
        padding: 16px 20px;
        color: {DKM_GRAY};
        font-size: 14px;
    }}

    /* Peak hours badge */
    .hour-badge {{
        display: inline-block;
        background: {DKM_BLUE};
        color: white;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 13px;
        font-weight: 500;
        margin: 4px;
    }}

    /* Hide streamlit default elements */
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 2rem; }}
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="main-header">
    <div>
        <h1>⚡ Pulse Productivity</h1>
        <p>Personal Productivity Agent · DKM Consult Pvt Ltd.</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Date Picker ───────────────────────────────────────────────────────────────

selected_date = st.date_input("Select date", value=date.today(), label_visibility="collapsed")
date_str = selected_date.strftime("%Y-%m-%d")


# ── Daily Summary Cards ───────────────────────────────────────────────────────

st.markdown('<div class="section-title">Today at a glance</div>', unsafe_allow_html=True)

summary = daily_summary(date_str)

if summary:
    cols = st.columns(len(summary))
    for col, (category, minutes) in zip(cols, summary.items()):
        hours = round(minutes / 60, 1)
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{hours}h</div>
            <div class="metric-label">{category}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown('<div class="info-box">No data for this date yet. Make sure main.py is running.</div>', unsafe_allow_html=True)


# ── Category Breakdown ────────────────────────────────────────────────────────

if summary:
    st.markdown('<div class="section-title">Time breakdown</div>', unsafe_allow_html=True)

    df_pie = pd.DataFrame(summary.items(), columns=["Category", "Minutes"])
    colors = [CATEGORY_COLORS.get(c, DKM_GRAY) for c in df_pie["Category"]]

    fig = go.Figure(go.Pie(
        labels=df_pie["Category"],
        values=df_pie["Minutes"],
        hole=0.45,
        marker=dict(colors=colors, line=dict(color=DKM_WHITE, width=2)),
        textinfo="label+percent",
        textfont=dict(size=13),
    ))
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Weekly Trend ──────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">This week</div>', unsafe_allow_html=True)

weekly_df = weekly_summary(date_str)

if not weekly_df.empty:
    fig2 = go.Figure()
    for category in weekly_df.columns:
        fig2.add_trace(go.Bar(
            name=category,
            x=weekly_df.index,
            y=weekly_df[category],
            marker_color=CATEGORY_COLORS.get(category, DKM_GRAY),
        ))
    fig2.update_layout(
        barmode="stack",
        margin=dict(t=10, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Minutes",
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=300,
    )
    st.plotly_chart(fig2, use_container_width=True)


# ── Peak Focus Hours ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title">Peak focus hours</div>', unsafe_allow_html=True)

peak_hours = peak_focus_hours(date_str)

if peak_hours:
    badges = " ".join([f'<span class="hour-badge">{h}:00 – {h+1}:00</span>' for h in peak_hours])
    st.markdown(badges, unsafe_allow_html=True)
else:
    st.markdown('<div class="info-box">Not enough data yet.</div>', unsafe_allow_html=True)


# ── Top Distractions ──────────────────────────────────────────────────────────

st.markdown('<div class="section-title">Top distractions</div>', unsafe_allow_html=True)

distractions = top_distractions(date_str)

if distractions:
    df_dist = pd.DataFrame(distractions)
    df_dist["minutes"] = df_dist["minutes"].round(1)

    fig3 = go.Figure(go.Bar(
        x=df_dist["minutes"],
        y=df_dist["app"],
        orientation="h",
        marker_color="#E53935",
    ))
    fig3.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Minutes",
        yaxis_title="",
        height=200,
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.markdown('<div class="info-box">No distractions recorded.</div>', unsafe_allow_html=True)


# ── Export Buttons ────────────────────────────────────────────────────────────

st.markdown('<div class="section-title">Export timesheet</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("⬇ Download CSV", use_container_width=True):
        from exports.csv_export import export_csv
        export_csv(date_str)
        st.success("Saved to exports/output/")

with col2:
    if st.button("⬇ Download PDF", use_container_width=True):
        from exports.pdf_export import export_pdf
        export_pdf(date_str)
        st.success("Saved to exports/output/")