# TableTurn AI

TableTurn AI is a SaaS-ready Streamlit MVP for restaurant seating, waitlist pressure, reservation pacing, and table-turn decisions. It is designed for independent restaurant operators who need a professional host-stand command center during live service.

## Target Users

- Independent restaurant operators
- Operators who need a simple cloud dashboard
- Consultants or agencies packaging this workflow as a client portal

## Key Features

- Reservation and waitlist CRUD
- Shift control panel for service date, service period, capacity, and turn targets
- Occupancy, covers, waitlist, projected sales, and turn-risk KPIs
- Priority queue with next-best host and manager actions
- Table-area load analytics and revenue-weighted service priority
- CSV export for shift review
- AI-style manager brief without paid API dependencies

## AI Value Proposition

TableTurn AI includes deterministic AI-style recommendations that work without paid API keys. The manager brief prioritizes parties by turn pressure, wait time, party size, and expected spend, then produces practical floor actions. For production, connect OpenAI, Azure OpenAI, Anthropic, or another model provider through Streamlit secrets.

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

The MVP uses SQLite (`saas_mvp.db`) as a local fallback. This works for demos and single-instance Streamlit Cloud apps, but production multi-user SaaS deployments should move persistence to Supabase, Firebase, Postgres, or another managed database.

## SaaS-Ready MVP Note

This app is structured as a sellable SaaS MVP: branded interface, CRUD workflow, dashboard, export, persistence fallback, and clear upgrade paths for authentication, billing, team accounts, and cloud storage.
