# TableTurn AI

TableTurn AI is a SaaS-ready Streamlit MVP for restaurant table management, guest registration, waitlist seating, and order capture. It is designed for independent restaurant operators who need a practical front-of-house operating system to fill seats, manage parties, and track orders during live service.

## Target Users

- Independent restaurant operators
- Operators who need a simple cloud dashboard
- Consultants or agencies packaging this workflow as a client portal

## Key Features

- Table inventory management by area, seat count, and status
- Fast guest registration for walk-ins, reservations, call-aheads, and VIPs
- Waitlist queue with AI-style table matching and seat-priority scoring
- Seat assignment workflow that fills open tables and marks them occupied
- Table clearing workflow that closes guests and resets tables
- Order capture by seated guest, table, item, category, quantity, and status
- Guest registry with edit/delete/export support
- Floor analytics for table state, area load, guest mix, and sales by category
- AI-style operating brief for seating and service decisions

## AI Value Proposition

TableTurn AI includes deterministic AI-style recommendations that work without paid API keys. The waitlist board scores parties by priority, party size, quote time, and registration type, then recommends the best-fit table. The operating brief summarizes current service pressure and suggests practical host and manager actions. For production, connect OpenAI, Azure OpenAI, Anthropic, or another model provider through Streamlit secrets.

## Setup

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Create a GitHub repository named `tableturn-ai`.
2. Push `app.py`, `requirements.txt`, and `README.md` to the repository root.
3. In Streamlit Cloud, choose the repo, branch `main`, and main file `app.py`.
4. Deploy.

## Optional Integrations and Secrets

- `OPENAI_API_KEY` for true generative recommendations.
- Supabase or Firebase for durable multi-user persistence.
- Google Sheets for lightweight shared data operations.
- S3-compatible storage for exports and attachments.

## Persistence Notes

The MVP uses SQLite (`tableturn_ai.db`) as a local fallback. This works for demos and single-instance Streamlit Cloud apps, but production multi-user SaaS deployments should move persistence to Supabase, Firebase, Postgres, or another managed database.

## SaaS-Ready MVP Note

This app is structured as a sellable SaaS MVP: branded interface, CRUD workflow, dashboard, export, persistence fallback, and clear upgrade paths for authentication, billing, team accounts, and cloud storage.
