# SWE30003 — Veterinary Information Software
## A3 Implementation Progress Tracker

---

## ✅ DONE

- [x] Neon PostgreSQL database created and connected
- [x] FastAPI backend scaffold (`vet_backend/`) set up
- [x] React + TypeScript + Vite frontend scaffold (`vet_frontend/`) set up
- [x] `database.py` configured with SQLAlchemy engine, session, and Base
- [x] `/api/health` endpoint working — returns `status: ok, database: connected`
- [x] Alembic configured and connected to Neon (`alembic current` works)
- [x] `app/models/` folder created with `__init__.py`
- [x] `app/schemas/` folder created with `__init__.py`
- [x] A2 UML updated with full attribute types, method signatures, visibility modifiers (PNG generated)
- [x] 6 functional areas confirmed (all 6 A2 scenarios to be implemented)

---

## 🔲 BACKEND — Models (SQLAlchemy)

Create one file per class in `app/models/`. Each model inherits from `Base`.

- [ ] `app/models/user.py` — `User` base table (userID, name, email, password, role)
- [ ] `app/models/pet_owner.py` — `PetOwner` (contactNumber, FK → users)
- [ ] `app/models/veterinarian.py` — `Veterinarian` (licenseNumber, FK → users)
- [ ] `app/models/association_admin.py` — `AssociationAdministrator` (workID, FK → users)
- [ ] `app/models/pet.py` — `Pet` (petID, petName, petType, age, gender, FK → pet_owners)
- [ ] `app/models/first_aid_content.py` — `FirstAidContent` base table (contentID, title, description, petType, emergencyCategory, publicationStatus, content_type)
- [ ] `app/models/guide.py` — `Guide` (steps as JSON, FK → first_aid_contents)
- [ ] `app/models/video.py` — `Video` (videoURL, FK → first_aid_contents)
- [ ] `app/models/quiz.py` — `Quiz` (totalScore, duration, FK → first_aid_contents)
- [ ] `app/models/question.py` — `Question` (questionText, explanation, FK → quizzes)
- [ ] `app/models/answer.py` — `Answer` (answerText, isCorrect, FK → questions)
- [ ] `app/models/chat.py` — `VeterinaryAdviceChat` (chatID, createdAt, isUrgent, FK → pet_owners + veterinarians)
- [ ] `app/models/message.py` — `Message` (content, timestamp, sender, FK → chats)
- [ ] `app/models/booking.py` — `Booking` (bookingID, createdAt, timeslot, bookingStatus, FK → pet_owners + veterinarians)

---

## 🔲 BACKEND — Alembic Migration

After all models are written:

- [ ] Update `alembic/env.py` — uncomment all model imports
- [ ] Run `alembic revision --autogenerate -m "initial"`
- [ ] Run `alembic upgrade head`
- [ ] Verify all tables appear in Neon dashboard

---

## 🔲 BACKEND — Schemas (Pydantic)

Create in `app/schemas/`. One file per domain area.

- [ ] `app/schemas/user.py` — RegisterRequest, LoginRequest, LoginResponse, UserResponse
- [ ] `app/schemas/pet.py` — PetCreate, PetUpdate, PetResponse
- [ ] `app/schemas/first_aid.py` — GuideResponse, ContentSearchRequest, ContentSearchResponse
- [ ] `app/schemas/quiz.py` — QuizResponse, SubmitAnswerRequest, QuizResultResponse
- [ ] `app/schemas/chat.py` — ChatResponse, SendMessageRequest, MessageResponse
- [ ] `app/schemas/booking.py` — BookingCreate, BookingResponse

---

## 🔲 BACKEND — Auth (JWT)

- [ ] Install `python-jose` and `passlib` — add to `requirements.txt`
- [ ] Create `app/core/security.py` — password hashing + JWT token creation/verification
- [ ] Create `app/api/routes/auth.py` — `POST /api/auth/register`, `POST /api/auth/login`
- [ ] Update `app/main.py` — include auth router

---

## 🔲 BACKEND — Routes (one file per scenario)

Create in `app/api/routes/`. Each route maps to UML methods.

### Scenario 6 — Profile + Pet Management
- [ ] `app/api/routes/profile.py`
  - `GET /api/profile` — get own profile
  - `PUT /api/profile` — updateProfile()
  - `GET /api/pets` — get pet list
  - `POST /api/pets` — createPetProfile()
  - `PUT /api/pets/{petID}` — updatePetProfile()
  - `DELETE /api/pets/{petID}` — deletePetProfile()

### Scenario 1 — Access First-Aid Guide
- [ ] `app/api/routes/first_aid.py`
  - `GET /api/first-aid/search` — accessFirstAidContent(petType, emergency)
  - `GET /api/first-aid/{contentID}` — getContent()

### Scenario 4 — Attempt Quiz
- [ ] `app/api/routes/quiz.py`
  - `GET /api/quizzes` — list available quizzes
  - `GET /api/quizzes/{quizID}` — startQuiz(), getQuestionList()
  - `POST /api/quizzes/{quizID}/submit` — submitAnswer(), calculateScore()

### Scenario 3 — Vet Submits + Admin Manages Content
- [ ] `app/api/routes/content.py`
  - `POST /api/content` — createFirstAidContent() [Vet only]
  - `PUT /api/content/{contentID}` — updateFirstAidContent() [Vet only]
  - `POST /api/content/{contentID}/verify` — verifyFirstAidContent() [Vet only]
  - `POST /api/content/{contentID}/reject` — rejectFirstAidContent() [Vet only]
  - `PUT /api/content/{contentID}/status` — updateFirstAidContentStatus() [Admin only]
  - `POST /api/content/{contentID}/publish` — publishFirstAidContent() [Admin only]
  - `DELETE /api/content/{contentID}` — deleteFirstAidContent() [Admin only]

### Scenario 5 — Vet Provides Quiz Explanations
- [ ] `app/api/routes/quiz_explanation.py`
  - `PUT /api/quizzes/{quizID}/questions/{questionID}/explanation` — setExplanation() [Vet only]

### Scenario 2 — Veterinary Advice Chat + Booking
- [ ] `app/api/routes/chat.py`
  - `POST /api/chats` — startChat()
  - `GET /api/chats/{chatID}` — viewChatHistory()
  - `POST /api/chats/{chatID}/messages` — sendMessage(), createMessage()
  - `PUT /api/chats/{chatID}/messages/{messageID}` — editMessage()
  - `DELETE /api/chats/{chatID}/messages/{messageID}` — deleteMessage()
- [ ] `app/api/routes/booking.py`
  - `POST /api/bookings` — makeBooking() [PetOwner]
  - `PUT /api/bookings/{bookingID}/accept` — acceptBookingSlot() [Vet]
  - `GET /api/bookings` — list own bookings

---

## 🔲 FRONTEND — Pages (React)

Create in `vet_frontend/src/pages/`.

- [ ] `RegisterPage.tsx` + `LoginPage.tsx`
- [ ] `ProfilePage.tsx` — update own profile + manage pets
- [ ] `FirstAidPage.tsx` — search + view guide results
- [ ] `QuizPage.tsx` — attempt quiz, see score + explanations
- [ ] `ContentManagementPage.tsx` — Vet/Admin submit + manage content
- [ ] `ChatPage.tsx` — chat interface
- [ ] `BookingPage.tsx` — booking interface

---

## 🔲 FRONTEND — Setup

- [ ] Install `react-router-dom` for page routing
- [ ] Install `axios` for API calls
- [ ] Create `src/api/` folder — one file per route group (auth.ts, firstaid.ts, quiz.ts, etc.)
- [ ] Create `src/context/AuthContext.tsx` — store logged-in user + token globally
- [ ] Update `App.tsx` — add all routes

---

## 🔲 A3 REPORT WRITEUP

- [ ] Section: Detailed design changes from A2 (class level, responsibilities, dynamic)
- [ ] Section: Bootstrap process update
- [ ] Section: Updated interaction diagrams (6 scenarios with full signatures)
- [ ] Section: Justification for each change
- [ ] Appendix: Original A2 UML diagram
- [ ] Appendix: Updated A3 UML diagram

---

## 📌 RECOMMENDED CODING ORDER

```
1. Models (all 14 files)
2. Alembic migration → tables in Neon
3. Auth routes (register + login)
4. Scenario 6 — Profile + Pet (simplest)
5. Scenario 1 — First-Aid Guide (read-only)
6. Scenario 4 — Quiz attempt (builds on content)
7. Scenario 3 — Vet/Admin content management (feeds 1 & 4)
8. Scenario 5 — Quiz explanations (builds on 3 & 4)
9. Scenario 2 — Chat + Booking (most complex, do last)
10. Frontend pages (parallel with backend or after)
```

---

## 📌 STACK SUMMARY

| Layer | Technology |
|---|---|
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI (Python) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Database | PostgreSQL (Neon cloud) |
| Auth | JWT (python-jose + passlib) |
| API Docs | Swagger UI at `/docs` |
