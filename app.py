import sqlite3
from datetime import datetime, time

import pandas as pd
import plotly.express as px
import streamlit as st

PRODUCT = "TableTurn AI"
DB = "tableturn_ai.db"

st.set_page_config(page_title=PRODUCT, page_icon="TT", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #111827;
        --muted: #64748b;
        --line: #e2e8f0;
        --panel: #ffffff;
        --accent: #7c2d12;
        --gold: #b45309;
        --green: #047857;
        --blue: #0369a1;
        --red: #b91c1c;
    }
    .stApp { background: #f6f7f9; color: var(--ink); }
    section[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--line); }
    .topbar {
        display: flex; justify-content: space-between; align-items: flex-start; gap: 20px;
        padding: 22px 24px; border: 1px solid #d8dee8; border-radius: 8px;
        background: linear-gradient(135deg, #111827 0%, #4a2518 58%, #7c2d12 100%);
        color: white; margin-bottom: 18px;
    }
    .topbar h1 { margin: 0; font-size: 36px; letter-spacing: 0; }
    .topbar p { margin: 8px 0 0; color: #f3e8df; max-width: 820px; font-size: 15px; }
    .badge-row { display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; }
    .badge {
        border: 1px solid rgba(255,255,255,.28); background: rgba(255,255,255,.11);
        padding: 6px 10px; border-radius: 6px; font-size: 12px; white-space: nowrap;
    }
    div[data-testid="stMetric"] {
        background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
        padding: 14px 16px; box-shadow: 0 1px 2px rgba(15,23,42,.04);
    }
    .section-title { font-weight: 700; font-size: 17px; margin: 8px 0 10px; }
    .queue-card {
        background: white; border: 1px solid var(--line); border-radius: 8px; padding: 14px;
        margin-bottom: 10px; box-shadow: 0 1px 2px rgba(15,23,42,.04);
    }
    .queue-card b { font-size: 15px; }
    .meta { color: var(--muted); font-size: 13px; margin-top: 4px; }
    .priority-high { border-left: 4px solid var(--red); }
    .priority-med { border-left: 4px solid var(--gold); }
    .priority-low { border-left: 4px solid var(--green); }
    .pill { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 12px; border: 1px solid var(--line); margin-right: 6px; }
    .pill-red { background: #fef2f2; color: #991b1b; }
    .pill-gold { background: #fffbeb; color: #92400e; }
    .pill-green { background: #ecfdf5; color: #065f46; }
    .pill-blue { background: #eff6ff; color: #1d4ed8; }
    </style>
    """,
    unsafe_allow_html=True,
)


def connect():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    with connect() as cx:
        cx.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                service_period TEXT NOT NULL,
                status TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                table_area TEXT NOT NULL,
                check_estimate REAL NOT NULL,
                seated_at TEXT,
                quoted_minutes INTEGER NOT NULL,
                turn_target INTEGER NOT NULL,
                vip_score INTEGER NOT NULL,
                notes TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )


def load_data():
    with connect() as cx:
        return pd.read_sql_query("SELECT * FROM reservations ORDER BY updated_at DESC", cx)


def save_reservation(row_id, guest_name, service_period, status, party_size, table_area, check_estimate, seated_at, quoted_minutes, turn_target, vip_score, notes):
    now = datetime.utcnow().isoformat(timespec="seconds")
    with connect() as cx:
        if row_id:
            cx.execute(
                """
                UPDATE reservations
                SET guest_name=?, service_period=?, status=?, party_size=?, table_area=?, check_estimate=?,
                    seated_at=?, quoted_minutes=?, turn_target=?, vip_score=?, notes=?, updated_at=?
                WHERE id=?
                """,
                (guest_name, service_period, status, party_size, table_area, check_estimate, seated_at, quoted_minutes, turn_target, vip_score, notes, now, row_id),
            )
        else:
            cx.execute(
                """
                INSERT INTO reservations (
                    guest_name, service_period, status, party_size, table_area, check_estimate,
                    seated_at, quoted_minutes, turn_target, vip_score, notes, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (guest_name, service_period, status, party_size, table_area, check_estimate, seated_at, quoted_minutes, turn_target, vip_score, notes, now),
            )


def delete_reservation(row_id):
    with connect() as cx:
        cx.execute("DELETE FROM reservations WHERE id=?", (row_id,))


def seed():
    if not load_data().empty:
        return
    sample_rows = [
        ("Rivera 4-top", "Dinner", "Booked", 4, "Window", 185, "", 0, 92, 88, "Anniversary note; prefer quiet table."),
        ("Patel 2-top", "Lunch", "Seated", 2, "Bar", 62, "12:18", 0, 54, 42, "Business lunch; wants quick pacing."),
        ("Morgan 6-top", "Dinner", "Waiting", 6, "Main Room", 340, "", 22, 118, 76, "High spend likelihood; ask manager to greet."),
        ("Nguyen 3-top", "Dinner", "Seated", 3, "Patio", 145, "18:42", 0, 86, 51, "Needs high chair removed."),
        ("Santos 5-top", "Dinner", "Quoted", 5, "Main Room", 265, "", 35, 110, 69, "Celebration; dessert upsell opportunity."),
    ]
    for row in sample_rows:
        save_reservation(None, *row)


def elapsed_minutes(seated_at):
    if not seated_at:
        return 0
    try:
        parsed = datetime.strptime(seated_at.strip(), "%H:%M").time()
        now = datetime.now()
        seated = datetime.combine(now.date(), parsed)
        return max(0, int((now - seated).total_seconds() // 60))
    except ValueError:
        return 0


def risk_score(row):
    elapsed = elapsed_minutes(row["seated_at"])
    over_target = max(0, elapsed - int(row["turn_target"]))
    waiting_pressure = int(row["quoted_minutes"]) * 1.25 if row["status"] in ["Waiting", "Quoted"] else 0
    seated_pressure = over_target * 2.1 if row["status"] == "Seated" else 0
    vip_pressure = int(row["vip_score"]) * 0.18
    party_pressure = int(row["party_size"]) * 2.2
    return min(100, round(waiting_pressure + seated_pressure + vip_pressure + party_pressure))


def service_action(row):
    if row["status"] in ["Waiting", "Quoted"]:
        if row["turn_risk"] >= 70:
            return "Manager touch now, offer bar seating or a comped starter, and protect the next open table."
        return "Keep quote honest, confirm contact number, and prepare the best-fit table area."
    if row["status"] == "Seated":
        elapsed = row["elapsed_minutes"]
        if elapsed > row["turn_target"]:
            return "Send floor lead to check dessert/payment status and clear blockers immediately."
        if row["turn_risk"] >= 55:
            return "Pace entrees and check table satisfaction before the turn window tightens."
        return "Maintain service cadence; no escalation needed."
    if row["status"] == "Booked":
        return "Confirm arrival risk, table preference, and expected spend before the shift peak."
    return "Archive after closeout or convert notes into tomorrow's pre-shift brief."


init_db()
seed()
df = load_data()

with st.sidebar:
    st.markdown("### Shift Control")
    service_date = st.date_input("Service date", value=datetime.now().date())
    active_period = st.selectbox("Active service", ["Lunch", "Dinner", "Brunch", "Late Night"], index=1)
    capacity = st.number_input("Dining room seats", min_value=10, value=74, step=2)
    avg_turn = st.number_input("Target average turn", min_value=35, value=82, step=5)

    st.markdown("### Reservation Editor")
    choices = ["New reservation"] + [f"{r.id}: {r.guest_name}" for r in df.itertuples()]
    selected_label = st.selectbox("Select record", choices)
    selected = None if selected_label == "New reservation" else df[df.id == int(selected_label.split(":")[0])].iloc[0]

    with st.form("reservation_form"):
        guest_name = st.text_input("Guest / party name", "" if selected is None else selected.guest_name)
        service_period = st.selectbox("Service period", ["Lunch", "Dinner", "Brunch", "Late Night"], index=1 if selected is None else ["Lunch", "Dinner", "Brunch", "Late Night"].index(selected.service_period))
        status = st.selectbox("Status", ["Booked", "Quoted", "Waiting", "Seated", "Closed", "No-show"], index=0 if selected is None else ["Booked", "Quoted", "Waiting", "Seated", "Closed", "No-show"].index(selected.status))
        party_size = st.number_input("Party size", min_value=1, max_value=20, value=2 if selected is None else int(selected.party_size))
        table_area = st.selectbox("Table area", ["Main Room", "Window", "Patio", "Bar", "Private", "Chef Counter"], index=0 if selected is None else ["Main Room", "Window", "Patio", "Bar", "Private", "Chef Counter"].index(selected.table_area))
        check_estimate = st.number_input("Expected check", min_value=0.0, value=120.0 if selected is None else float(selected.check_estimate), step=10.0)
        seated_at = st.text_input("Seated at (HH:MM)", "" if selected is None else (selected.seated_at or ""))
        quoted_minutes = st.number_input("Quoted wait minutes", min_value=0, value=0 if selected is None else int(selected.quoted_minutes), step=5)
        turn_target = st.number_input("Turn target minutes", min_value=30, value=int(avg_turn) if selected is None else int(selected.turn_target), step=5)
        vip_score = st.slider("VIP / service value score", 0, 100, 50 if selected is None else int(selected.vip_score))
        notes = st.text_area("Host notes", "" if selected is None else selected.notes)
        submitted = st.form_submit_button("Save reservation", type="primary")

    if submitted and guest_name:
        save_reservation(None if selected is None else int(selected.id), guest_name, service_period, status, party_size, table_area, check_estimate, seated_at, quoted_minutes, turn_target, vip_score, notes)
        st.rerun()

    if selected is not None and st.button("Delete reservation"):
        delete_reservation(int(selected.id))
        st.rerun()

if df.empty:
    st.info("Add the first reservation to start the shift board.")
    st.stop()

df["elapsed_minutes"] = df["seated_at"].apply(elapsed_minutes)
df["turn_risk"] = df.apply(risk_score, axis=1)
df["revenue_weight"] = df["check_estimate"] * (df["vip_score"] / 100)
df["action"] = df.apply(service_action, axis=1)

active_df = df[df["service_period"] == active_period].copy()
if active_df.empty:
    active_df = df.copy()

st.markdown(
    f"""
    <div class="topbar">
        <div>
            <h1>TableTurn AI</h1>
            <p>Professional host-stand command center for reservation pacing, table turns, waitlist pressure, and floor manager decisions.</p>
        </div>
        <div class="badge-row">
            <span class="badge">{service_date}</span>
            <span class="badge">{active_period} service</span>
            <span class="badge">{capacity} seats</span>
            <span class="badge">{avg_turn} min target</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

seated = active_df[active_df["status"] == "Seated"]
waiting = active_df[active_df["status"].isin(["Waiting", "Quoted"])]
occupancy = min(100, round((seated["party_size"].sum() / capacity) * 100)) if capacity else 0
projected_revenue = active_df[active_df["status"] != "No-show"]["check_estimate"].sum()
avg_risk = active_df["turn_risk"].mean()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Active covers", int(active_df["party_size"].sum()))
m2.metric("Occupancy", f"{occupancy}%")
m3.metric("Waiting parties", len(waiting))
m4.metric("Projected sales", f"${projected_revenue:,.0f}")
m5.metric("Avg turn risk", f"{avg_risk:.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Service Board", "Floor Analytics", "Reservations", "AI Brief"])

with tab1:
    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown('<div class="section-title">Priority Queue</div>', unsafe_allow_html=True)
        for row in active_df.sort_values(["turn_risk", "check_estimate"], ascending=[False, False]).itertuples():
            css = "priority-high" if row.turn_risk >= 70 else "priority-med" if row.turn_risk >= 45 else "priority-low"
            pill = "pill-red" if row.turn_risk >= 70 else "pill-gold" if row.turn_risk >= 45 else "pill-green"
            st.markdown(
                f"""
                <div class="queue-card {css}">
                    <b>{row.guest_name}</b>
                    <span class="pill pill-blue">{row.status}</span>
                    <span class="pill {pill}">Risk {row.turn_risk}</span>
                    <div class="meta">{row.party_size} guests • {row.table_area} • ${row.check_estimate:,.0f} est. check • seated {row.elapsed_minutes} min</div>
                    <div class="meta"><b>Next action:</b> {row.action}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        st.markdown('<div class="section-title">Table Area Load</div>', unsafe_allow_html=True)
        area = active_df.groupby("table_area", as_index=False).agg(covers=("party_size", "sum"), revenue=("check_estimate", "sum"), risk=("turn_risk", "mean"))
        st.plotly_chart(px.bar(area, x="table_area", y="covers", color="risk", color_continuous_scale="OrRd", title="Covers by area"), use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.scatter(active_df, x="elapsed_minutes", y="turn_risk", size="check_estimate", color="status", hover_name="guest_name", title="Turn risk by elapsed time"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(active_df.sort_values("revenue_weight", ascending=False), x="guest_name", y="revenue_weight", color="status", title="Revenue-weighted service priority"), use_container_width=True)
    st.plotly_chart(px.histogram(active_df, x="status", y="party_size", histfunc="sum", color="table_area", title="Covers by status and table area"), use_container_width=True)

with tab3:
    columns = ["id", "guest_name", "service_period", "status", "party_size", "table_area", "check_estimate", "seated_at", "quoted_minutes", "turn_target", "vip_score", "turn_risk", "notes", "updated_at"]
    st.dataframe(active_df[columns], use_container_width=True, hide_index=True)
    st.download_button("Export shift CSV", active_df[columns].to_csv(index=False), "tableturn_shift_export.csv", "text/csv")

with tab4:
    st.markdown('<div class="section-title">Manager Brief</div>', unsafe_allow_html=True)
    if avg_risk >= 65:
        tone = "High pressure shift. Assign a floor lead to turns and have the host quote conservatively."
    elif avg_risk >= 40:
        tone = "Moderate pressure. Keep pacing visible and review high-value waiting parties every 10 minutes."
    else:
        tone = "Controlled shift. Maintain cadence and use the opportunity to improve guest notes."
    st.markdown(f"<div class='queue-card'><b>Shift read:</b> {tone}</div>", unsafe_allow_html=True)
    for row in active_df.sort_values("turn_risk", ascending=False).head(5).itertuples():
        st.markdown(
            f"""
            <div class="queue-card">
                <b>{row.guest_name}</b><br>
                {row.action}<br>
                <span class="meta">Why: {row.status}, {row.party_size} guests, risk {row.turn_risk}, expected check ${row.check_estimate:,.0f}. Notes: {row.notes}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
