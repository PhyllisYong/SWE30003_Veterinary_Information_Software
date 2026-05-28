# SWE30003 — Veterinary Information Software
**Group 5**

Web-based veterinary information platform for small pet owners (cats, dogs, rabbits, hamsters, guinea pigs).

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 + TypeScript (Vite) |
| Backend | Python — FastAPI |
| Database | Neon (PostgreSQL) |
| ORM / Migrations | SQLAlchemy 2 + Alembic |

---

## User Roles

| Role | Description |
|---|---|
| `pet_owner` | Books vets, chats, takes quizzes, manages pets |
| `veterinarian` | Sets availability, manages content (guides/videos/quizzes), reviews assigned content |
| `association_admin` | Approves/rejects/publishes all content, assigns reviewers, manages users |

---

## Features

| Module | Description |
|---|---|
| Auth | Register, login, JWT-based auth (`/api/auth`) |
| Profile & Pets | View/edit/delete profile; manage pet records (name, type, age, gender) |
| Booking | Pet owners book vets by timeslot; vets set availability, accept/cancel bookings |
| Chat | Real-time vet-client messaging via WebSocket; send/edit/delete messages |
| First Aid | Search and browse published first-aid content by pet type and emergency category |
| Guides | Vet-authored step-by-step guides; admin review/publish workflow |
| Videos | Vet-submitted YouTube videos; admin review/publish workflow |
| Quizzes | Pet owners take timed quizzes; per-question answer checking; result tracking with content recommendations |
| Content Workflow | Vet submits → Admin assigns reviewer → Vet verifies → Admin publishes |
| Vet Quiz Management | Vets edit question text, answer text, and explanations on their quizzes |

---

## Project Structure

```
.
├── vet_backend/
│   ├── app/
│   │   ├── api/routes/        # Controllers
│   │   │   ├── auth.py        # Register, login, /me
│   │   │   ├── booking.py     # Vet availability, bookings CRUD
│   │   │   ├── chat.py        # Chat rooms, messages, WebSocket
│   │   │   ├── content.py     # Content creation, review, publish workflow
│   │   │   ├── first_aid.py   # First-aid search and detail
│   │   │   ├── health.py      # Health check
│   │   │   ├── profile.py     # Profile and pet CRUD
│   │   │   └── quiz.py        # Quiz list, submit, check, results
│   │   ├── core/
│   │   │   ├── database.py    # DB engine + session
│   │   │   └── security.py    # JWT + password hashing
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── answer.py
│   │   │   ├── association_admin.py
│   │   │   ├── booking.py
│   │   │   ├── chat.py
│   │   │   ├── first_aid_content.py
│   │   │   ├── guide.py
│   │   │   ├── message.py
│   │   │   ├── pet.py
│   │   │   ├── pet_owner.py
│   │   │   ├── question.py
│   │   │   ├── quiz.py
│   │   │   ├── quiz_result.py
│   │   │   ├── user.py
│   │   │   ├── veterinarian.py
│   │   │   └── video.py
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── authentication.py  # Session invalidation facade
│   │   │   ├── search_engine.py   # First-aid content search
│   │   │   └── video_hosting.py   # YouTube URL validation + embed
│   │   └── patterns/
│   │       └── observer.py    # WebSocket observer for real-time chat
│   ├── alembic/               # DB migrations
│   ├── seeds/                 # Seed data
│   ├── .env.example
│   └── requirements.txt
└── vet_frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── HomePage.tsx
    │   │   ├── LoginPage.tsx
    │   │   ├── RegisterPage.tsx
    │   │   ├── ProfilePage.tsx
    │   │   ├── FirstAidPage.tsx
    │   │   ├── GuidesPage.tsx
    │   │   ├── VideoPage.tsx
    │   │   ├── QuizListPage.tsx
    │   │   ├── QuizPage.tsx
    │   │   ├── VetAdvicePage.tsx
    │   │   ├── ChatPage.tsx
    │   │   ├── BookingPage.tsx
    │   │   ├── VetAvailabilityPage.tsx
    │   │   ├── VetContentPage.tsx
    │   │   ├── VetQuizManagePage.tsx
    │   │   ├── VetVideoManagePage.tsx
    │   │   └── AdminContentPage.tsx
    │   └── components/        # Navbar, Footer
    └── package.json
```

---

## Frontend Routes

| Path | Page | Access |
|---|---|---|
| `/` | Home | Public |
| `/login` | Login | Public |
| `/register` | Register | Public |
| `/guides` | Guides | Public |
| `/videos` | Videos | Public |
| `/quizzes` | Quiz list | Public |
| `/quizzes/:id` | Take quiz | Pet owner |
| `/profile` | Profile & pets | Authenticated |
| `/vet-advice` | Vet advice hub | Pet owner |
| `/vet-advice/chat` | Chat | Pet owner |
| `/vet-advice/booking` | Booking | Pet owner |
| `/vet/availability` | Set availability | Vet |
| `/vet/content-management` | Manage content | Vet |
| `/vet/quiz-manage` | Manage quizzes | Vet |
| `/vet/video-manage` | Manage videos | Vet |
| `/admin/content-management` | Review & publish | Admin |

---

## API Routes

| Method | Route | Description | Role |
|---|---|---|---|
| GET | `/api/health` | Health check + DB connectivity | Public |
| POST | `/api/auth/register` | Register new user | Public |
| POST | `/api/auth/login` | Login, returns JWT | Public |
| GET | `/api/auth/me` | Current user info | Auth |
| GET | `/api/profile` | Get profile | Auth |
| PUT | `/api/profile` | Update profile | Auth |
| DELETE | `/api/profile` | Delete account + all data | Auth |
| GET | `/api/pets` | List pets | Pet owner |
| POST | `/api/pets` | Add pet | Pet owner |
| PUT | `/api/pets/{petID}` | Update pet | Pet owner |
| DELETE | `/api/pets/{petID}` | Delete pet | Pet owner |
| GET | `/api/users?role=veterinarian` | List users by role | Admin |
| GET | `/api/vets` | List vets with availability | Auth |
| PUT | `/api/vets/availability` | Set vet availability | Vet |
| POST | `/api/bookings` | Create booking | Pet owner |
| GET | `/api/bookings` | List own bookings | Auth |
| PUT | `/api/bookings/{bookingID}/accept` | Accept booking | Vet |
| PUT | `/api/bookings/{bookingID}/cancel` | Cancel booking | Pet owner / Vet |
| POST | `/api/chats` | Create chat | Pet owner |
| GET | `/api/chats` | List chats | Auth |
| GET | `/api/chats/{chatID}` | Get chat + message history | Participant |
| WS | `/api/chats/{chatID}/ws` | WebSocket connection | Participant |
| POST | `/api/chats/{chatID}/messages` | Send message | Participant |
| PUT | `/api/chats/{chatID}/messages/{messageID}` | Edit message | Sender |
| DELETE | `/api/chats/{chatID}/messages/{messageID}` | Delete message | Sender |
| GET | `/api/first-aid/search` | Search first-aid content | Public |
| GET | `/api/first-aid/{content_id}` | Get first-aid detail | Public |
| GET | `/api/content` | List all content | Admin |
| GET | `/api/content/mine` | Vet's own content | Vet |
| GET | `/api/content/assigned` | Content assigned for review | Vet |
| POST | `/api/content` | Submit content (guide/video/quiz) | Vet |
| PUT | `/api/content/{content_id}` | Update own content | Vet |
| DELETE | `/api/content/{content_id}` | Delete content | Admin |
| POST | `/api/content/{content_id}/assign` | Assign reviewer | Admin |
| POST | `/api/content/{content_id}/review` | Verify or reject content | Vet (reviewer) |
| POST | `/api/content/{content_id}/publish` | Publish content | Admin |
| POST | `/api/content/{content_id}/set-draft` | Assign reviewer + set pending_verification | Admin |
| POST | `/api/content/{content_id}/request-amend` | Reject + request amendment | Admin |
| PUT | `/api/content/{content_id}/status` | Set arbitrary status | Admin |
| GET | `/api/quizzes` | List published quizzes | Public |
| GET | `/api/quizzes/{quiz_id}` | Get quiz (randomised order) | Public |
| POST | `/api/quizzes/{quiz_id}/check` | Check single answer (no result saved) | Public |
| POST | `/api/quizzes/{quiz_id}/submit` | Submit all answers, save result | Pet owner |
| GET | `/api/quizzes/results/all` | All quiz results for current user | Auth |
| GET | `/api/quizzes/results/{result_id}` | Single quiz result | Auth |
| PUT | `/api/quizzes/{quiz_id}/questions/{question_id}/explanation` | Update question explanation | Vet |
| PUT | `/api/quizzes/{quiz_id}/questions/{question_id}/text` | Update question text | Vet |
| PUT | `/api/quizzes/{quiz_id}/questions/{question_id}/answers/{answer_id}/text` | Update answer text | Vet |

Base URL: `http://localhost:8000`

---

## Content Publication Workflow

```
Vet submits
    → status: submitted
Admin assigns reviewer + confirms
    → status: pending_verification
Assigned vet reviews (verify / reject)
    → status: verified | rejected
Admin publishes
    → status: published
Admin can request amendment (reject + feedback)
    → status: rejected (vet edits and resubmits)
```

---

## Setup

### Backend

```bash
cd vet_backend

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# Edit .env — set DATABASE_URL to your Neon connection string

alembic upgrade head

uvicorn app.main:app --reload
```

> Get NeonDB connection string from Dashboard → Connect

### Frontend

```bash
cd vet_frontend

npm install

npm run dev
```

Frontend runs at `http://localhost:5173`, backend at `http://localhost:8000`.

---

## Team

| Name | Student ID |
|---|---|
| Michael Joo Jia WONG | 104381424 |
| Natalie ROBERT | 102787350 |
| Damian Wei-Quan CHOY | 102788997 |
| Li Ying YEO | 102789314 |
| Phyllis Kai Qi YONG | 102787389 |
