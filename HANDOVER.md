# SWE30003 — Assignment 3 Handover
**Group 5 · Veterinary Information Software**

| Name | Student ID |
|---|---|
| Michael Joo Jia WONG | 104381424 |
| Natalie ROBERT | 102787350 |
| Damian Wei-Quan CHOY | 102788997 |
| Li Ying YEO | 102789314 |
| Phyllis Kai Qi YONG | 102787389 |

---

## 1. What we are building

A web-based veterinary first-aid platform for small pet owners (cats, dogs, rabbits, hamsters, guinea pigs). The system provides:

- First-aid guides, instructional videos, and knowledge quizzes
- Veterinary advice via real-time chat
- Physical consultation booking
- Content management and verification by vets and admins

---

## 2. Tech stack

| Layer | Technology |
|---|---|
| Frontend (client) | React (separate codebase, **not in UML**) |
| Backend (server) | Python — Flask or FastAPI |
| Database | Neon (PostgreSQL) |
| Auth | External authentication service (Façade) |
| Video hosting | External video hosting service (Façade) |

Frontend and backend communicate via **REST API (JSON)**. The UML class diagram models the **Python backend only**.

---

## 3. Architecture — 3-layer Layered Architecture

Directly from L8 lecture (3-layer enterprise system).

```
┌─────────────────────────────────────────┐
│  React frontend (client)                │  ← NOT in UML
└──────────────┬──────────────────────────┘
               │  HTTP / REST API (JSON)
┌──────────────▼──────────────────────────┐
│  LAYER 1 — Routing                      │
│  UserController                         │
│  ContentController                      │
│  ConsultationController                 │
└──────────────┬──────────────────────────┘
               │  calls methods on
┌──────────────▼──────────────────────────┐
│  LAYER 2 — Logic (Domain)               │
│  All 17 A2 classes live here            │
│  + QuizResult (new)                     │
└──────────────┬──────────────────────────┘
               │  CRUD via
┌──────────────▼──────────────────────────┐
│  LAYER 3 — Data                         │
│  DatabaseManager (Singleton + Façade)   │
│  Talks to Neon PostgreSQL               │
└─────────────────────────────────────────┘
```

**Key rule:** each layer only calls the layer directly below it. `UserController` never calls `DatabaseManager` directly — it calls a domain class method, which calls `DatabaseManager`.

---

## 4. All 20 classes — layer, type, one-line purpose

### Layer 1 — Routing (new for A3)

| Class | Purpose |
|---|---|
| `UserController` | `/login` `/logout` `/register` `/profile` — delegates to `User` subclasses |
| `ContentController` | `/search` `/guide` `/video` `/quiz` `/submit` — delegates to `SearchEngine`, `FirstAidContent` hierarchy |
| `ConsultationController` | `/booking` `/chat` `/message` — delegates to `Booking`, `VetAdviceChat` |

### Layer 2 — Logic (from A2, unchanged structure)

| Class | Type | Purpose |
|---|---|---|
| `User` | Abstract | Shared identity attributes and abstract login/logout for all user roles |
| `PetOwner` | Concrete (extends User) | Primary end-user — searches content, manages pets, books, chats |
| `AssociationAdministrator` | Concrete (extends User) | Manages full content lifecycle — publish, delete, assign verifier |
| `Veterinarian` | Concrete (extends User) | Submits/verifies content, chats, accepts bookings |
| `Authentication` | External service (Façade) | Handles login, logout, token validation — not our code |
| `Pet` | Concrete entity | Profile record for a pet registered under a PetOwner |
| `SearchEngine` | Service class | Filters and retrieves FirstAidContent by petType and category |
| `FirstAidContent` | Abstract | Shared publication lifecycle for Guide, Video, Quiz |
| `Guide` | Concrete (extends FirstAidContent) | Step-by-step written emergency procedure |
| `Video` | Concrete (extends FirstAidContent) | Video metadata; streams via VideoHosting Façade |
| `VideoHosting` | External service (Façade) | Hosts and streams video — not our code |
| `Quiz` | Concrete (extends FirstAidContent) | Interactive knowledge assessment — owns Questions |
| `Question` | Concrete entity | Single quiz item with answer list and vet explanation |
| `Answer` | Data holder | Answer text + correctness flag for a Question |
| `VetAdviceChat` | Concrete entity (Observer) | Chat session between PetOwner and Veterinarian |
| `Message` | Data holder | Single message unit in a VetAdviceChat session |
| `Booking` | Data holder | Physical consultation appointment record |
| `QuizResult` | Data holder (new for A3) | Return value of `startQuiz()` — score, petOwnerID, timestamp |

### Layer 3 — Data (new for A3)

| Class | Purpose |
|---|---|
| `DatabaseManager` | Singleton + Façade over Neon PostgreSQL — all SQL lives here |

---

## 5. Attributes and methods — quick reference

### User (abstract)
```
- userID: String
- name: String
- email: String
- password: String
- role: String
+ createUser(name, email, pw, role): void
+ deleteUser(): void
+ updateProfile(name, email): void
+ login(email, pw): boolean  {abstract}
+ logout(): void             {abstract}
+ getRole(): String
```

### PetOwner (extends User)
```
- contactNumber: String
- pets: List<Pet>
- bookings: List<Booking>
+ login(email, pw): boolean
+ logout(): void
+ searchContent(petType, cat): List
+ startQuiz(quizID): QuizResult
+ startChat(vetID): VetAdviceChat
+ makeBooking(vetID, slot): Booking
+ addPet(data): void
+ updatePet(petID, data): void
+ deletePet(petID): void
```

### AssociationAdministrator (extends User)
```
- workID: String
+ login(email, pw): boolean
+ logout(): void
+ deleteContent(contentID): void
+ updateContentStatus(id, status): void
+ publishContent(contentID): void
+ assignVerifier(contentID, vetID): void
+ listPendingContent(): List
+ manageUsers(): List<User>
```

### Veterinarian (extends User)
```
- licenseNumber: String
- specialisation: String
- availableSlots: List<String>
+ login(email, pw): boolean
+ logout(): void
+ submitContent(data): void
+ updateContent(id, data): void
+ verifyContent(contentID): void
+ provideExplanation(questionID, txt): void
+ acceptBooking(bookingID): void
+ sendMessage(chatID, txt): void
+ setAvailability(slots): void
```

### Authentication (external Façade)
```
+ login(email, pw): boolean
+ logout(token): void
+ validateToken(token): boolean
+ generateToken(uid): String
+ hashPassword(pw): String
```

### Pet
```
- petID: String
- name: String
- age: int
- type: String
- gender: String
- ownerID: String
+ getPetInfo(): Map
+ updateInfo(data): void
+ getOwnerID(): String
+ getID(): String
```

### SearchEngine
```
- contentRepository: List
+ searchContent(petType, cat): List
+ filterByPetType(type): List
+ filterByCategory(cat): List
+ getContentByID(id): Object
+ loadRepository(): void
+ refreshCache(): void
```

### FirstAidContent (abstract)
```
- contentID: String
- title: String
- description: String
- petType: String
- emergencyCategory: String
- publicationStatus: String
- authorVetID: String
+ getMetadata(): Map
+ updateStatus(status): void
+ display(): void  {abstract}
+ getAuthorID(): String
+ getID(): String
```

### Guide (extends FirstAidContent)
```
- steps: List<String>
- stepCount: int
+ display(): void
+ getSteps(): List<String>
+ addStep(step): void
+ updateStep(idx, txt): void
+ removeStep(idx): void
```

### Video (extends FirstAidContent)
```
- videoURL: String
- durationSec: int
+ display(): void
+ play(): void
+ getURL(): String
+ getDuration(): int
```

### VideoHosting (external Façade)
```
+ streamVideo(url): void
+ uploadVideo(file): String
+ deleteVideo(url): void
+ getStreamURL(id): String
```

### Quiz (extends FirstAidContent)
```
- questions: List<Question>
- totalScore: int
- durationSec: int
+ display(): void
+ startQuiz(): void
+ submitAnswer(questionID, answerID): void
+ calculateScore(): int
+ getQuestions(): List
+ addQuestion(q): void
```

### Question
```
- questionID: String
- questionText: String
- answers: List<Answer>
- explanation: String
+ getAnswers(): List<Answer>
+ checkAnswer(answerID): boolean
+ getText(): String
+ setExplanation(txt): void
+ getExplanation(): String
```

### Answer
```
- answerID: String
- answerText: String
- isCorrect: boolean
+ getAnswerText(): String
+ isCorrect(): boolean
+ getID(): String
+ setText(txt): void
```

### VetAdviceChat
```
- chatID: String
- messages: List<Message>
- petOwnerID: String
- vetID: String
- isUrgent: boolean
- createdAt: String
+ startSession(ownerID, vetID): void
+ sendMessage(senderID, txt): void
+ receiveMessage(): Message
+ viewChatHistory(): List
+ editMessage(msgID, txt): void
+ deleteMessage(msgID): void
+ notifyParticipants(msg): void
+ closeChat(): void
```

### Message
```
- messageID: String
- senderID: String
- content: String
- timestamp: String
+ getContent(): String
+ getSenderID(): String
+ getTimestamp(): String
+ getID(): String
```

### Booking
```
- bookingID: String
- createdAt: String
- timeslot: String
- status: String
- petOwnerID: String
- vetID: String
+ getStatus(): String
+ updateStatus(s): void
+ getTimeslot(): String
+ getID(): String
+ getPetOwnerID(): String
```

### QuizResult (new for A3)
```
- resultID: String
- petOwnerID: String
- quizID: String
- score: int
- attemptedAt: String
+ getScore(): int
+ getPassed(): boolean
+ getSummary(): String
+ getID(): String
```

### DatabaseManager (new for A3, Singleton)
```
- connectionURL: String
- isConnected: boolean
- instance: DatabaseManager
+ getInstance(): DatabaseManager
+ connect(): void
+ disconnect(): void
+ query(sql, params): List
+ execute(sql, params): boolean
+ save(entity): boolean
+ update(entity): boolean
+ delete(table, id): boolean
+ findByID(table, id): Map
+ findAll(table): List
+ findWhere(table, conditions): List
+ beginTransaction(): void
+ commitTransaction(): void
+ rollbackTransaction(): void
```

---

## 6. All relationships

| # | Type | From | To | Multiplicity | Note |
|---|---|---|---|---|---|
| 1 | Generalisation | `PetOwner` | `User` | — | extends |
| 2 | Generalisation | `AssocAdmin` | `User` | — | extends |
| 3 | Generalisation | `Veterinarian` | `User` | — | extends |
| 4 | Generalisation | `Guide` | `FirstAidContent` | — | extends |
| 5 | Generalisation | `Video` | `FirstAidContent` | — | extends |
| 6 | Generalisation | `Quiz` | `FirstAidContent` | — | extends |
| 7 | Aggregation ◇ | `PetOwner` | `Pet` | 1 → 0..* | PetOwner owns Pets; Pets can exist independently |
| 8 | Composition ◆ | `Quiz` | `Question` | 1 → 1..* | Questions cannot exist without Quiz |
| 9 | Composition ◆ | `Question` | `Answer` | 1 → 2..* | Answers cannot exist without Question |
| 10 | Composition ◆ | `VetAdviceChat` | `Message` | 1 → 1..* | Messages cannot exist without Chat |
| 11 | Association → | `PetOwner` | `Booking` | 1 → 0..* | makes |
| 12 | Association → | `PetOwner` | `VetAdviceChat` | 1 → 0..* | starts |
| 13 | Association → | `Veterinarian` | `Booking` | 1 → 0..* | accepts |
| 14 | Association → | `Quiz` | `QuizResult` | 1 → 0..* | produces |
| 15 | Dependency ⇢ | `User` | `Authentication` | — | «uses» — delegates login/logout |
| 16 | Dependency ⇢ | `PetOwner` | `SearchEngine` | — | «uses» |
| 17 | Dependency ⇢ | `SearchEngine` | `FirstAidContent` | — | «uses» |
| 18 | Dependency ⇢ | `Video` | `VideoHosting` | — | «uses» |
| 19 | Dependency ⇢ | `UserController` | User subclasses | — | «calls» |
| 20 | Dependency ⇢ | `ContentController` | `SearchEngine`, `FirstAidContent` | — | «calls» |
| 21 | Dependency ⇢ | `ConsultationController` | `Booking`, `VetAdviceChat` | — | «calls» |
| 22–26 | Dependency ⇢ | `User`, `SearchEngine`, `FirstAidContent`, `VetAdviceChat`, `Booking` | `DatabaseManager` | — | «persists» |

---

## 7. Design patterns (from A2 — do not change)

### Template Method
Applied to `User` and `FirstAidContent` hierarchies. The abstract parent defines the shared structure; subclasses override specifics.
- `User.login()` and `User.logout()` are abstract — every subclass (`PetOwner`, `Veterinarian`, `AssocAdmin`) implements them
- `FirstAidContent.display()` is abstract — `Guide`, `Video`, `Quiz` each implement it differently

### Façade
Applied to `Authentication` and `VideoHosting` (from A2) and `DatabaseManager` (new for A3).
- Domain classes never call the external service or database directly
- They call the Façade, which handles the complexity internally

### Observer
Applied to `VetAdviceChat`.
- `VetAdviceChat` is the Subject (publisher)
- `PetOwner` and `Veterinarian` are the Observers (subscribers)
- When a message is sent, `notifyParticipants()` pushes the update to both participants
- Implemented via `sendMessage()` → `notifyParticipants(msg)`

---

## 8. Bootstrap order (from A2 — do not change)

When the Python backend starts up, initialise in this exact order:

1. **Resolve external service Façades** — `Authentication` proxy and `VideoHosting` proxy first, as all subsequent steps may depend on them
2. **Load `FirstAidContent` hierarchy** — load `Guide`, `Video`, `Quiz` instances from the database via `DatabaseManager`
3. **Instantiate `SearchEngine`** — depends on the content repository loaded in step 2
4. **Initialise routing layer** — `UserController`, `ContentController`, `ConsultationController` reference the services from steps 1–3
5. **Lazy-load domain entities** — `PetOwner`, `Veterinarian`, `AssocAdmin`, `Pet`, `Booking`, `VetAdviceChat` instances are loaded on demand per request, not at startup

---

## 9. Coding conventions — keep these consistent

### Naming
- Classes: `PascalCase` — `PetOwner`, `VetAdviceChat`, `DatabaseManager`
- Methods: `camelCase` — `startQuiz()`, `makeBooking()`, `findByID()`
- Attributes: `camelCase` — `petOwnerID`, `isCorrect`, `createdAt`
- Constants: `UPPER_SNAKE` — `MAX_RETRIES`, `DB_URL`
- API routes: `kebab-case` — `/api/vet-advice-chat`, `/api/first-aid-content`

### IDs and timestamps
- All IDs are `String` type — use UUID format (`uuid4()` in Python)
- All timestamps are `String` type — use ISO 8601 format (`2025-05-27T14:30:00Z`)
- Do not use integers for IDs

### Visibility
- All attributes are `private` (prefix `_` in Python, e.g. `self._userID`)
- All public methods have no prefix
- Use getters/setters for attribute access — do not expose attributes directly

### Layer boundary rules
- Controllers (Layer 1) only call domain class methods — never call `DatabaseManager` directly
- Domain classes (Layer 2) call `DatabaseManager` for persistence — never write raw SQL elsewhere
- `DatabaseManager` (Layer 3) is the only class that writes SQL queries
- External services (`Authentication`, `VideoHosting`) are only called from domain classes, not controllers

### Return types from controllers
- All controller methods return JSON
- Success: `{ "status": "ok", "data": { ... } }`
- Error: `{ "status": "error", "message": "..." }`

### Database
- Use `DatabaseManager.getInstance()` — never instantiate it directly (Singleton)
- Always wrap multi-step DB operations in a transaction: `beginTransaction()` → work → `commitTransaction()` or `rollbackTransaction()` on error
- Table names match class names in lowercase snake: `pet_owner`, `first_aid_content`, `vet_advice_chat`

---

## 10. What each team member should build

Suggested split — adjust as needed:

| Area | Classes to implement |
|---|---|
| Auth + user management | `User`, `PetOwner`, `AssocAdmin`, `Veterinarian`, `Authentication` (Façade), `UserController` |
| Content management | `FirstAidContent`, `Guide`, `Video`, `VideoHosting` (Façade), `ContentController` |
| Quiz system | `Quiz`, `Question`, `Answer`, `QuizResult`, (+ ContentController quiz endpoints) |
| Chat + booking | `VetAdviceChat`, `Message`, `Booking`, `ConsultationController` |
| Search + persistence | `SearchEngine`, `Pet`, `DatabaseManager` |

All team members must use `DatabaseManager` the same way. Do not write your own DB connection code.

---

## 11. What changed from A2 to A3

| Change | Why |
|---|---|
| Added `UserController`, `ContentController`, `ConsultationController` | 3-layer architecture — routing layer to receive HTTP from React |
| Added `DatabaseManager` | Persistence Façade — consistent with A2 Façade pattern, isolates all SQL in one place |
| Added `QuizResult` | Return type for `PetOwner.startQuiz()` — needed to pass score back to controller |
| Added `Question.explanation: String` | Storage target for `Veterinarian.provideExplanation()` which had no attribute in A2 |
| Added `Veterinarian.availableSlots: List<String>` | Needed for booking availability check |
| Added full attribute types, method signatures, visibility markers | A3 detailed design requirement — A2 deliberately omitted these |
| All 17 A2 classes, all A2 relationships, all multiplicities | Unchanged — minimal update principle |

---

*Last updated based on A2 document and A3 design decisions. If you change a class interface, update this file before merging.*
