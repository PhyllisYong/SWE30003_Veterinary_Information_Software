# SWE30003 — Veterinary Information Software
**Group 5**

Web-based veterinary first-aid platform for small pet owners (cats, dogs, rabbits, hamsters, guinea pigs).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript (Vite) |
| Backend | Python — FastAPI |
| Database | Neon (PostgreSQL) |
| ORM / Migrations | SQLAlchemy 2 + Alembic |

---

## Project Structure

```
.
├── vet_backend/       # Python FastAPI backend
│   ├── app/
│   │   ├── api/routes/    # Layer 1 — Controllers / routing
│   │   ├── core/          # DB engine, session, config
│   │   ├── models/        # SQLAlchemy ORM models
│   │   └── schemas/       # Pydantic schemas
│   ├── alembic/           # DB migrations
│   ├── .env.example
│   └── requirements.txt
└── vet_frontend/      # React + TypeScript frontend
    ├── src/
    └── package.json
```

---

## Setup

### Backend

```bash
cd vet_backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your Neon connection string

# Run migrations
alembic upgrade head

# Start dev server (http://localhost:8000)
uvicorn app.main:app --reload
```

> Note: Get the NeonDB link from the Dashboard -> Connect

### Frontend

```bash
cd vet_frontend

npm install

# Start dev server (http://localhost:5173)
npm run dev
```

---

## API

| Method | Route | Description |
|---|---|---|
| GET | `/api/health` | Health check + DB connectivity |

Base URL: `http://localhost:8000`

---

## Team

| Name | Student ID |
|---|---|
| Michael Joo Jia WONG | 104381424 |
| Natalie ROBERT | 102787350 |
| Damian Wei-Quan CHOY | 102788997 |
| Li Ying YEO | 102789314 |
| Phyllis Kai Qi YONG | 102787389 |
