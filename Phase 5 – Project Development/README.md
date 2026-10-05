# PocketSmart AI — Smart Budget & Recommendation Assistant

PocketSmart AI is a runnable FastAPI + Jinja2 web application for budget-aware recommendations across **Home Interior**, **Party Planning**, and **Jewelry**. It follows the project specification: modular backend, Gemini integration, optional jewelry outfit-image input, authentication, session/JWT endpoints, recommendation history, platform search links, and responsive HTML/CSS UI.

## Features
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image
- Gemini-powered recommendations when `GEMINI_API_KEY` is configured
- Local fallback recommendations so the project can run without an API key
- Register / Login / Logout
- JWT `/token` endpoint
- `/session-info` and `/session-data`
- Recommendation history and detail view
- Search links for Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO, Booking, Tanishq and BlueStone
- SQLite database

## Project structure
```text
PocketSmart_AI/
├── main.py
├── config.py
├── database.py
├── auth.py
├── schemas.py
├── gemini_utils.py
├── recommendation_service.py
├── routes.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── home_planner.html
│   ├── party_planner.html
│   ├── jewelry_planner.html
│   ├── recommendations.html
│   ├── history.html
│   └── error.html
└── static/
    ├── styles.css
    └── uploads/.gitkeep
```

## Run in VS Code / Windows
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python main.py
```

Open **http://127.0.0.1:8000**.

FastAPI documentation is available at **http://127.0.0.1:8000/docs**.

## Enable Gemini
Open `.env` and set:
```text
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_available_gemini_model
```
Never upload `.env` or your API key to GitHub. `.gitignore` already excludes `.env`.

If no API key is configured, the application still runs and uses deterministic local fallback recommendations. The fallback is useful for demonstrating the complete UI, authentication, history and planner workflow.

## GitHub upload
Upload the complete project folder except `venv`, `.env`, `pocketsmart.db`, and generated uploads. The included `.gitignore` handles these automatically.
