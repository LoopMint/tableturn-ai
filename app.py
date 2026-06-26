import sqlite3
from datetime import datetime

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
    .hero {
        display: flex; justify-content: space-between; align-items: flex-start; gap: 20px;
        padding: 24px; border: 1px solid #d8dee8; border-radius: 8px;
        background: linear-gradient(135deg, #111827 0%, #4a2518 58%, #7c2d12 100%);
        color: white; margin-bottom: 16px;
    }
    .hero h1 { margin: 0; font-size: 34px; letter-spacing: 0; }
    .hero p { margin: 8px 0 0; color: #f3e8df; max-width: 900px; font-size: 15px; }
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
    .card {
        background: white; border: 1px solid var(--line); border-radius: 8px; padding: 14px;
        margin-bottom: 10px; box-shadow: 0 1px 2px rgba(15,23,42,.04);
    }
    .card b { font-size: 15px; }
    .muted { color: var(--muted); font-size: 13px; margin-top: 4px; }
    .high { border-left: 4px solid var(--red); }
    .med { border-left: 4px solid var(--gold); }
    .low { border-left: 4px solid var(--green); }
    .pill { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 12px; border: 1px solid var(--line); margin-right: 6px; }
    .pill-red { background: #fef2f2; color: #991b1b; }
    .pill-gold { background: #fffbeb; color: #92400e; }
    .pill-green { background: #ecfdf5; color: #065f46; }
    .pill-blue { background: #eff6ff; color: #1d4ed8; }
    .pill-gray { background: #f8fafc; color: #334155; }
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
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                area TEXT NOT NULL,
                seats INTEGER NOT NULL,
                status TEXT NOT NULL,
                current_guest_id INTEGER,
                updated_at TEXT NOT NULL
            )
            """
        )
        cx.execute(
            """
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                phone TEXT,
                party_size INTEGER NOT NULL,
                registration_type TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                quoted_wait INTEGER NOT NULL,
                assigned_table_id INTEGER,
                seated_at TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cx.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_id INTEGER NOT NULL,
                table_id INTEGER,
                item TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def now():
    return datetime.utcnow().isoformat(timespec="seconds")


def load_tables():
    with connect() as cx:
        return pd.read_sql_query("SELECT * FROM tables ORDER BY area, table_name", cx)


def load_guests():
    with connect() as cx:
        return pd.read_sql_query("SELECT * FROM guests ORDER BY updated_at DESC", cx)


def load_orders():
    with connect() as cx:
        return pd.read_sql_query("SELECT * FROM orders ORDER BY updated_at DESC", cx)


def seed_data():
    if load_tables().empty:
        tables = [
            ("T1", "Main Room", 2, "Open"),
            ("T2", "Main Room", 4, "Open"),
            ("T3", "Main Room", 4, "Open"),
            ("T4", "Window", 2, "Open"),
            ("T5", "Window", 4, "Open"),
            ("P1", "Patio", 4, "Open"),
            ("P2", "Patio", 6, "Open"),
            ("B1", "Bar", 2, "Open"),
            ("B2", "Bar", 2, "Open"),
            ("DR", "Private", 10, "Reserved"),
        ]
        with connect() as cx:
            cx.executemany(
                "INSERT INTO tables (table_name, area, seats, status, current_guest_id, updated_at) VALUES (?, ?, ?, ?, NULL, ?)",
                [(name, area, seats, status, now()) for name, area, seats, status in tables],
            )
    if load_guests().empty:
        save_guest(None, "Rivera", "555-0140", 4, "Reservation", "Waiting", 92, 15, None, "", "Anniversary; wants quiet table.")
        save_guest(None, "Patel", "555-0188", 2, "Walk-in", "Waiting", 54, 10, None, "", "Business lunch; quick service.")
        save_guest(None, "Morgan", "555-0122", 6, "Walk-in", "Waiting", 78, 25, None, "", "High spend likelihood; manager greet.")


def save_table(row_id, table_name, area, seats, status):
    with connect() as cx:
        if row_id:
            cx.execute(
                "UPDATE tables SET table_name=?, area=?, seats=?, status=?, updated_at=? WHERE id=?",
                (table_name, area, seats, status, now(), row_id),
            )
        else:
            cx.execute(
                "INSERT INTO tables (table_name, area, seats, status, current_guest_id, updated_at) VALUES (?, ?, ?, ?, NULL, ?)",
                (table_name, area, seats, status, now()),
            )


def save_guest(row_id, guest_name, phone, party_size, registration_type, status, priority, quoted_wait, assigned_table_id, seated_at, notes):
    assigned_table_id = assigned_table_id or None
    timestamp = now()
    with connect() as cx:
        if row_id:
            cx.execute(
                """
                UPDATE guests
                SET guest_name=?, phone=?, party_size=?, registration_type=?, status=?, priority=?,
                    quoted_wait=?, assigned_table_id=?, seated_at=?, notes=?, updated_at=?
                WHERE id=?
                """,
                (guest_name, phone, party_size, registration_type, status, priority, quoted_wait, assigned_table_id, seated_at, notes, timestamp, row_id),
            )
        else:
            cx.execute(
                """
                INSERT INTO guests (
                    guest_name, phone, party_size, registration_type, status, priority,
                    quoted_wait, assigned_table_id, seated_at, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (guest_name, phone, party_size, registration_type, status, priority, quoted_wait, assigned_table_id, seated_at, notes, timestamp, timestamp),
            )


def delete_guest(row_id):
    with connect() as cx:
        cx.execute("UPDATE tables SET status='Open', current_guest_id=NULL, updated_at=? WHERE current_guest_id=?", (now(), row_id))
        cx.execute("DELETE FROM orders WHERE guest_id=?", (row_id,))
        cx.execute("DELETE FROM guests WHERE id=?", (row_id,))


def seat_guest(guest_id, table_id):
    seated_time = datetime.now().strftime("%H:%M")
    with connect() as cx:
        old = cx.execute("SELECT assigned_table_id FROM guests WHERE id=?", (guest_id,)).fetchone()
        if old and old[0]:
            cx.execute("UPDATE tables SET status='Open', current_guest_id=NULL, updated_at=? WHERE id=?", (now(), old[0]))
        cx.execute(
            "UPDATE guests SET status='Seated', assigned_table_id=?, seated_at=?, updated_at=? WHERE id=?",
            (table_id, seated_time, now(), guest_id),
        )
        cx.execute(
            "UPDATE tables SET status='Occupied', current_guest_id=?, updated_at=? WHERE id=?",
            (guest_id, now(), table_id),
        )


def clear_table(table_id):
    with connect() as cx:
        guest = cx.execute("SELECT current_guest_id FROM tables WHERE id=?", (table_id,)).fetchone()
        if guest and guest[0]:
            cx.execute("UPDATE guests SET status='Closed', updated_at=? WHERE id=?", (now(), guest[0]))
            cx.execute("UPDATE orders SET status='Served', updated_at=? WHERE guest_id=? AND status != 'Served'", (now(), guest[0]))
        cx.execute("UPDATE tables SET status='Open', current_guest_id=NULL, updated_at=? WHERE id=?", (now(), table_id))


def save_order(row_id, guest_id, table_id, item, category, quantity, price, status, notes):
    timestamp = now()
    with connect() as cx:
        if row_id:
            cx.execute(
                "UPDATE orders SET guest_id=?, table_id=?, item=?, category=?, quantity=?, price=?, status=?, notes=?, updated_at=? WHERE id=?",
                (guest_id, table_id, item, category, quantity, price, status, notes, timestamp, row_id),
            )
        else:
            cx.execute(
                "INSERT INTO orders (guest_id, table_id, item, category, quantity, price, status, notes, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (guest_id, table_id, item, category, quantity, price, status, notes, timestamp, timestamp),
            )


def delete_order(row_id):
    with connect() as cx:
        cx.execute("DELETE FROM orders WHERE id=?", (row_id,))


def wait_score(row):
    base = int(row["priority"]) + int(row["party_size"]) * 3 + int(row["quoted_wait"]) * 1.4
    if row["registration_type"] == "Reservation":
        base += 12
    return min(100, round(base))


def elapsed_minutes(seated_at):
    if not seated_at:
        return 0
    try:
        parsed = datetime.strptime(seated_at.strip(), "%H:%M")
        current = datetime.now()
        seated = current.replace(hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0)
        return max(0, int((current - seated).total_seconds() // 60))
    except ValueError:
        return 0


def best_table_match(guest_row, tables_df):
    open_tables = tables_df[tables_df["status"].isin(["Open", "Reserved"])].copy()
    if open_tables.empty:
        return "No open table available."
    open_tables["fit_gap"] = open_tables["seats"] - int(guest_row["party_size"])
    valid = open_tables[open_tables["fit_gap"] >= 0].sort_values(["fit_gap", "seats"])
    if valid.empty:
        largest = open_tables.sort_values("seats", ascending=False).iloc[0]
        return f"Hold for {largest.table_name} or combine tables; current largest open table seats {largest.seats}."
    table = valid.iloc[0]
    return f"Seat at {table.table_name} in {table.area}; capacity fit leaves {int(table.fit_gap)} spare seat(s)."


init_db()
seed_data()
tables = load_tables()
guests = load_guests()
orders = load_orders()

guests["wait_score"] = guests.apply(wait_score, axis=1) if not guests.empty else []
guests["elapsed_minutes"] = guests["seated_at"].apply(elapsed_minutes) if not guests.empty else []
orders["line_total"] = orders["quantity"] * orders["price"] if not orders.empty else []

with st.sidebar:
    st.markdown("### Service Setup")
    service_date = st.date_input("Service date", value=datetime.now().date())
    service_period = st.selectbox("Service period", ["Breakfast", "Lunch", "Dinner", "Late Night"], index=2)
    quote_step = st.slider("Default quote step", 5, 20, 10, step=5)

    st.markdown("### Fast Registration")
    with st.form("fast_registration"):
        g_name = st.text_input("Guest name")
        g_phone = st.text_input("Phone")
        g_party = st.number_input("Party size", min_value=1, max_value=20, value=2)
        g_type = st.radio("Type", ["Walk-in", "Reservation"], horizontal=True)
        g_priority = st.slider("Priority", 0, 100, 50)
        g_quote = st.number_input("Quoted wait", min_value=0, value=quote_step, step=5)
        g_notes = st.text_area("Notes")
        if st.form_submit_button("Register guest", type="primary") and g_name:
            save_guest(None, g_name, g_phone, g_party, g_type, "Waiting", g_priority, g_quote, None, "", g_notes)
            st.rerun()

st.markdown(
    f"""
    <div class="hero">
        <div>
            <h1>TableTurn AI</h1>
            <p>Table management, guest registration, waitlist seating, and order capture for restaurants that need a professional front-of-house operating system.</p>
        </div>
        <div class="badge-row">
            <span class="badge">{service_date}</span>
            <span class="badge">{service_period}</span>
            <span class="badge">{len(tables)} tables</span>
            <span class="badge">SQLite MVP</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

occupied_tables = tables[tables["status"] == "Occupied"]
open_tables = tables[tables["status"] == "Open"]
waiting_guests = guests[guests["status"].isin(["Waiting", "Quoted"])] if not guests.empty else guests
seated_guests = guests[guests["status"] == "Seated"] if not guests.empty else guests
total_sales = float(orders["line_total"].sum()) if not orders.empty else 0
covers_waiting = int(waiting_guests["party_size"].sum()) if not waiting_guests.empty else 0
covers_seated = int(seated_guests["party_size"].sum()) if not seated_guests.empty else 0
seat_capacity = int(tables["seats"].sum()) if not tables.empty else 0
occupancy = round((occupied_tables["seats"].sum() / seat_capacity) * 100) if seat_capacity else 0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Open tables", len(open_tables))
m2.metric("Occupied tables", len(occupied_tables))
m3.metric("Waiting covers", covers_waiting)
m4.metric("Seated covers", covers_seated)
m5.metric("Open order value", f"${total_sales:,.0f}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Floor Plan", "Waitlist & Seating", "Orders", "Guest Registry", "Analytics"])

with tab1:
    st.markdown('<div class="section-title">Table Management</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, row in enumerate(tables.itertuples()):
        css = "high" if row.status == "Occupied" else "med" if row.status == "Reserved" else "low"
        pill = "pill-red" if row.status == "Occupied" else "pill-gold" if row.status == "Reserved" else "pill-green"
        guest_label = ""
        if row.current_guest_id:
            match = guests[guests["id"] == row.current_guest_id]
            if not match.empty:
                guest_label = f"Guest: {match.iloc[0].guest_name}"
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="card {css}">
                    <b>{row.table_name}</b>
                    <span class="pill {pill}">{row.status}</span>
                    <div class="muted">{row.area} • {row.seats} seats</div>
                    <div class="muted">{guest_label or "No active guest"}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if row.status == "Occupied" and st.button(f"Clear {row.table_name}", key=f"clear_{row.id}"):
                clear_table(int(row.id))
                st.rerun()

    with st.expander("Add or update table"):
        table_choices = ["New table"] + [f"{r.id}: {r.table_name}" for r in tables.itertuples()]
        table_pick = st.selectbox("Select table", table_choices)
        table_selected = None if table_pick == "New table" else tables[tables.id == int(table_pick.split(":")[0])].iloc[0]
        with st.form("table_form"):
            t_name = st.text_input("Table name", "" if table_selected is None else table_selected.table_name)
            t_area = st.selectbox("Area", ["Main Room", "Window", "Patio", "Bar", "Private", "Chef Counter"], index=0 if table_selected is None else ["Main Room", "Window", "Patio", "Bar", "Private", "Chef Counter"].index(table_selected.area))
            t_seats = st.number_input("Seats", min_value=1, max_value=20, value=2 if table_selected is None else int(table_selected.seats))
            t_status = st.selectbox("Status", ["Open", "Reserved", "Occupied", "Blocked"], index=0 if table_selected is None else ["Open", "Reserved", "Occupied", "Blocked"].index(table_selected.status))
            if st.form_submit_button("Save table", type="primary") and t_name:
                save_table(None if table_selected is None else int(table_selected.id), t_name, t_area, t_seats, t_status)
                st.rerun()

with tab2:
    left, right = st.columns([1.1, 0.9])
    with left:
        st.markdown('<div class="section-title">Waitlist Queue</div>', unsafe_allow_html=True)
        if waiting_guests.empty:
            st.info("No guests are currently waiting.")
        for row in waiting_guests.sort_values("wait_score", ascending=False).itertuples():
            css = "high" if row.wait_score >= 75 else "med" if row.wait_score >= 45 else "low"
            pill = "pill-red" if row.wait_score >= 75 else "pill-gold" if row.wait_score >= 45 else "pill-green"
            st.markdown(
                f"""
                <div class="card {css}">
                    <b>{row.guest_name}</b>
                    <span class="pill pill-blue">{row.registration_type}</span>
                    <span class="pill {pill}">Seat score {row.wait_score}</span>
                    <div class="muted">{row.party_size} guests • quoted {row.quoted_wait} min • {row.phone or "no phone"}</div>
                    <div class="muted"><b>AI table match:</b> {best_table_match(pd.Series(row._asdict()), tables)}</div>
                    <div class="muted">{row.notes or ""}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        st.markdown('<div class="section-title">Seat Guest</div>', unsafe_allow_html=True)
        if guests.empty or tables.empty:
            st.info("Register guests and tables first.")
        else:
            guest_options = [f"{r.id}: {r.guest_name} ({r.party_size})" for r in guests[guests["status"].isin(["Waiting", "Quoted", "Booked"])].itertuples()]
            table_options = [f"{r.id}: {r.table_name} ({r.seats} seats, {r.status})" for r in tables[tables["status"].isin(["Open", "Reserved"])].itertuples()]
            if guest_options and table_options:
                with st.form("seat_form"):
                    guest_choice = st.selectbox("Guest", guest_options)
                    table_choice = st.selectbox("Table", table_options)
                    if st.form_submit_button("Seat now", type="primary"):
                        seat_guest(int(guest_choice.split(":")[0]), int(table_choice.split(":")[0]))
                        st.rerun()
            else:
                st.warning("No seatable guest or open table is available.")

with tab3:
    st.markdown('<div class="section-title">Order Capture</div>', unsafe_allow_html=True)
    seated_options = [f"{r.id}: {r.guest_name}" for r in guests[guests["status"] == "Seated"].itertuples()]
    if not seated_options:
        st.info("Seat a guest before taking an order.")
    else:
        with st.form("order_form"):
            guest_choice = st.selectbox("Seated guest", seated_options)
            guest_id = int(guest_choice.split(":")[0])
            guest = guests[guests.id == guest_id].iloc[0]
            table_id = int(guest.assigned_table_id) if pd.notna(guest.assigned_table_id) else None
            item = st.text_input("Menu item")
            category = st.selectbox("Category", ["Starter", "Entree", "Dessert", "Drink", "Special"])
            quantity = st.number_input("Quantity", min_value=1, value=1)
            price = st.number_input("Unit price", min_value=0.0, value=18.0, step=0.5)
            order_status = st.selectbox("Order status", ["Sent", "Preparing", "Ready", "Served", "Voided"])
            order_notes = st.text_area("Order notes")
            if st.form_submit_button("Add order", type="primary") and item:
                save_order(None, guest_id, table_id, item, category, quantity, price, order_status, order_notes)
                st.rerun()

    if orders.empty:
        st.info("No orders captured yet.")
    else:
        display = orders.merge(guests[["id", "guest_name"]], left_on="guest_id", right_on="id", how="left", suffixes=("", "_guest"))
        st.dataframe(display[["id", "guest_name", "item", "category", "quantity", "price", "line_total", "status", "notes", "updated_at"]], use_container_width=True, hide_index=True)
        order_to_delete = st.selectbox("Delete order", ["None"] + [f"{r.id}: {r.item}" for r in orders.itertuples()])
        if order_to_delete != "None" and st.button("Delete selected order"):
            delete_order(int(order_to_delete.split(":")[0]))
            st.rerun()

with tab4:
    st.markdown('<div class="section-title">Guest Registry</div>', unsafe_allow_html=True)
    guest_choices = ["New guest"] + [f"{r.id}: {r.guest_name}" for r in guests.itertuples()]
    guest_pick = st.selectbox("Select guest", guest_choices)
    guest_selected = None if guest_pick == "New guest" else guests[guests.id == int(guest_pick.split(":")[0])].iloc[0]
    with st.form("guest_form"):
        name = st.text_input("Guest name", "" if guest_selected is None else guest_selected.guest_name)
        phone = st.text_input("Phone", "" if guest_selected is None else guest_selected.phone)
        party = st.number_input("Party size", min_value=1, max_value=20, value=2 if guest_selected is None else int(guest_selected.party_size))
        reg_type = st.selectbox("Registration type", ["Walk-in", "Reservation", "Call-ahead", "VIP"], index=0 if guest_selected is None else ["Walk-in", "Reservation", "Call-ahead", "VIP"].index(guest_selected.registration_type if guest_selected.registration_type in ["Walk-in", "Reservation", "Call-ahead", "VIP"] else "Walk-in"))
        status = st.selectbox("Status", ["Waiting", "Quoted", "Booked", "Seated", "Closed", "No-show"], index=0 if guest_selected is None else ["Waiting", "Quoted", "Booked", "Seated", "Closed", "No-show"].index(guest_selected.status))
        priority = st.slider("Priority", 0, 100, 50 if guest_selected is None else int(guest_selected.priority))
        quoted = st.number_input("Quoted wait", min_value=0, value=10 if guest_selected is None else int(guest_selected.quoted_wait), step=5)
        notes = st.text_area("Notes", "" if guest_selected is None else guest_selected.notes)
        if st.form_submit_button("Save guest", type="primary") and name:
            save_guest(None if guest_selected is None else int(guest_selected.id), name, phone, party, reg_type, status, priority, quoted, None if guest_selected is None else guest_selected.assigned_table_id, "" if guest_selected is None else guest_selected.seated_at, notes)
            st.rerun()
    if guest_selected is not None and st.button("Delete guest and orders"):
        delete_guest(int(guest_selected.id))
        st.rerun()

    st.dataframe(guests, use_container_width=True, hide_index=True)
    st.download_button("Export guests CSV", guests.to_csv(index=False), "tableturn_guest_registry.csv", "text/csv")

with tab5:
    c1, c2 = st.columns(2)
    with c1:
        status_counts = tables.groupby("status", as_index=False).size()
        st.plotly_chart(px.pie(status_counts, names="status", values="size", title="Table state mix"), use_container_width=True)
        if not orders.empty:
            sales_by_category = orders.groupby("category", as_index=False)["line_total"].sum()
            st.plotly_chart(px.bar(sales_by_category, x="category", y="line_total", title="Order value by category"), use_container_width=True)
    with c2:
        area_load = tables.groupby("area", as_index=False).agg(seats=("seats", "sum"), occupied=("current_guest_id", "count"))
        area_load["occupancy_proxy"] = area_load["occupied"] / area_load["seats"] * 100
        st.plotly_chart(px.bar(area_load, x="area", y="occupancy_proxy", title="Area occupancy proxy"), use_container_width=True)
        wait_by_type = guests.groupby("registration_type", as_index=False)["party_size"].sum() if not guests.empty else pd.DataFrame()
        if not wait_by_type.empty:
            st.plotly_chart(px.bar(wait_by_type, x="registration_type", y="party_size", title="Covers by registration type"), use_container_width=True)

    st.markdown('<div class="section-title">AI Operating Brief</div>', unsafe_allow_html=True)
    if len(open_tables) == 0 and covers_waiting > 0:
        brief = "Dining room is full with active waitlist. Quote conservatively, identify near-finished tables, and assign one manager to table turns."
    elif covers_waiting > 10:
        brief = "Waitlist pressure is building. Seat high-score parties first, avoid under-filling large tables, and push bar seating for two-tops."
    elif occupancy < 55:
        brief = "Capacity is available. Prioritize speed to seat, capture orders quickly, and use server sections to balance the floor."
    else:
        brief = "Service is balanced. Maintain order pacing and keep guest notes current for repeat-visit value."
    st.markdown(f"<div class='card'><b>Current read:</b> {brief}</div>", unsafe_allow_html=True)
