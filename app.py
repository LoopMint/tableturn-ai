import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

PRODUCT = "TableTurn AI"
CATEGORY = "F&B"
TARGET_USER = "Independent restaurant operators"
DOMAIN = "restaurant seating and reservation optimization"
RECORDS = "reservations"
ITEM_LABEL = "Guest party"
METRIC_LABEL = "Turn risk"
ACCENT = "#7c2d12"
DB = "saas_mvp.db"

st.set_page_config(page_title=PRODUCT, page_icon="AI", layout="wide")

st.markdown(f"""
<style>
.stApp {{ background: #f7f8fb; color: #111827; }}
.hero {{ padding: 28px; border-radius: 8px; background: linear-gradient(135deg, #111827, {ACCENT}); color: white; margin-bottom: 18px; }}
.hero h1 {{ margin: 0; font-size: 42px; letter-spacing: 0; }}
.hero p {{ margin: 8px 0 0; max-width: 920px; font-size: 16px; }}
div[data-testid="stMetric"] {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; }}
.ai-card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px; margin-bottom: 10px; }}
.small {{ color: #4b5563; font-size: 14px; }}
</style>
<div class="hero"><h1>{PRODUCT}</h1><p>{DOMAIN.title()} for {TARGET_USER.lower()}. Manage records, score priorities, export data, and generate practical AI-style recommendations.</p></div>
""", unsafe_allow_html=True)


def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    with connect() as cx:
        cx.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            segment TEXT NOT NULL,
            status TEXT NOT NULL,
            value REAL NOT NULL,
            risk INTEGER NOT NULL,
            notes TEXT,
            updated_at TEXT NOT NULL
        )
        """)


def load_records():
    with connect() as cx:
        return pd.read_sql_query("SELECT * FROM records ORDER BY updated_at DESC", cx)


def save_record(row_id, name, segment, status, value, risk, notes):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with connect() as cx:
        if row_id:
            cx.execute(
                "UPDATE records SET name=?, segment=?, status=?, value=?, risk=?, notes=?, updated_at=? WHERE id=?",
                (name, segment, status, value, risk, notes, now, row_id),
            )
        else:
            cx.execute(
                "INSERT INTO records (name, segment, status, value, risk, notes, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, segment, status, value, risk, notes, now),
            )


def delete_record(row_id):
    with connect() as cx:
        cx.execute("DELETE FROM records WHERE id=?", (row_id,))


init_db()
if load_records().empty:
    for row in [('Rivera 4-top', 'Dinner', 'Booked', 180, 82, 'Anniversary note; prefer window'), ('Patel 2-top', 'Lunch', 'Seated', 55, 35, 'Quick business meal'), ('Morgan 6-top', 'Dinner', 'Waiting', 25, 67, 'High spend likelihood')]:
        save_record(None, *row)

df = load_records()

with st.sidebar:
    st.subheader(f"{ITEM_LABEL} editor")
    choices = ["New record"] + [f"{r.id}: {r.name}" for r in df.itertuples()]
    selected_label = st.selectbox("Select record", choices)
    selected = None if selected_label == "New record" else df[df.id == int(selected_label.split(":")[0])].iloc[0]

    with st.form("record_form"):
        name = st.text_input(ITEM_LABEL, "" if selected is None else selected.name)
        segment = st.text_input("Segment", "Core" if selected is None else selected.segment)
        status_options = ["Draft", "Planned", "Live", "Open", "Review", "Watch", "Healthy", "Booked", "Seated", "Waiting", "Overdue"]
        default_status = "Planned" if selected is None else selected.status
        if default_status not in status_options:
            status_options.insert(0, default_status)
        status = st.selectbox("Status", status_options, index=status_options.index(default_status))
        value = st.number_input("Value", min_value=0.0, value=100.0 if selected is None else float(selected.value), step=50.0)
        risk = st.slider(METRIC_LABEL, 0, 100, 50 if selected is None else int(selected.risk))
        notes = st.text_area("Notes", "" if selected is None else selected.notes)
        submitted = st.form_submit_button("Save record", type="primary")

    if submitted and name:
        save_record(None if selected is None else int(selected.id), name, segment, status, value, risk, notes)
        st.rerun()

    if selected is not None and st.button("Delete selected record"):
        delete_record(int(selected.id))
        st.rerun()

if df.empty:
    st.info("Add the first record to start using the workspace.")
    st.stop()

df["weighted_value"] = df["value"] * (100 - df["risk"]) / 100
high_risk = int((df["risk"] >= 70).sum())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Records", len(df))
m2.metric("Total value", f"${df['value'].sum():,.0f}")
m3.metric("Avg risk", f"{df['risk'].mean():.0f}")
m4.metric("High-risk items", high_risk)

tab1, tab2, tab3 = st.tabs(["Dashboard", "Records", "AI Copilot"])

with tab1:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(df, x="name", y="value", color="status", title="Value by record"), use_container_width=True)
    with right:
        st.plotly_chart(px.scatter(df, x="risk", y="weighted_value", size="value", color="segment", hover_name="name", title=f"{METRIC_LABEL} vs weighted value"), use_container_width=True)

with tab2:
    edited = st.data_editor(df, use_container_width=True, disabled=["id", "updated_at"], hide_index=True)
    st.caption("Use the sidebar for durable edits. The table is optimized for review and export.")
    st.download_button("Download CSV", df.to_csv(index=False), f"{PRODUCT.lower().replace(' ', '_')}_export.csv", "text/csv")

with tab3:
    st.markdown(f"<div class='small'>AI-style recommendations are deterministic and require no paid API key. Add OpenAI, Anthropic, or Azure OpenAI later for generated language.</div>", unsafe_allow_html=True)
    for row in df.sort_values("risk", ascending=False).itertuples():
        priority = "Immediate" if row.risk >= 75 else "Monitor" if row.risk >= 45 else "Maintain"
        st.markdown(f"""
        <div class="ai-card">
        <b>{row.name}</b><br>
        Priority: <b>{priority}</b>. Current status is <b>{row.status}</b>, risk score is <b>{row.risk}</b>, and value is <b>${row.value:,.0f}</b>.<br>
        Recommended action: review the note, assign one owner, set a 7-day checkpoint, and export this record for the operating meeting.<br>
        Notes: {row.notes}
        </div>
        """, unsafe_allow_html=True)
