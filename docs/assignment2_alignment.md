# Assignment 2 Design Alignment

This document records how the current implementation maps to the Assignment 2
class diagram, CRC cards, design patterns, and sequence diagrams.

## Current Standing

The backend represents all 17 Assignment 2 candidate classes:

| Assignment 2 class | Implementation status | Notes |
| --- | --- | --- |
| User | Partial, aligned by methods | SQLAlchemy superclass with identity fields, `getID`, `getRole`, `getName`, `getEmail`, and `updateProfile`. Registration/deletion persistence remains in routes. |
| PetOwner | Accurate | Joined-table subclass with contact number and relationships to pets, bookings, chats, and quiz results. Role-specific actions are exposed through API routes. |
| AssociationAdministrator | Accurate | Joined-table subclass with `workID`; admin content responsibilities are implemented in content routes. |
| Veterinarian | Accurate with extension | Joined-table subclass with license/specialisation plus `availableSlots` for practical booking. |
| Authentication | Accurate with implementation change | Implemented as an internal facade over JWT/bcrypt, not a third-party identity provider. Provides `login`, `logout`, and `invalidateSession`. |
| Pet | Accurate | Stores pet profile details and owner reference. Includes `updatePetDetails`. |
| SearchEngine | Accurate | Dedicated service for published first-aid content search/filtering. |
| FirstAidContent | Accurate with extension | Abstract superclass for Guide, Video, and Quiz. Adds `assignedVetID` and `reviewComment` for review workflow. |
| Guide | Accurate | FirstAidContent subclass with ordered steps and step operations. |
| Video | Accurate | FirstAidContent subclass with URL/duration and `requestVideoStream`. |
| Quiz | Accurate with extension | FirstAidContent subclass with questions, scoring helpers, pass evaluation, and recommendation helper. Persistence of attempts is handled by `QuizResult`. |
| Question | Accurate | Owns question text, answers, explanation, answer checking, and text correction helpers. |
| Answer | Accurate | Data-holder with answer text, correctness flag, and `isCorrectAnswer`. |
| VeterinaryAdviceChat | Partial, aligned by methods | Owns chat metadata, message history, and message helper methods. WebSocket transport remains in route layer. |
| Message | Accurate | Data-holder for sender, content, timestamp, and chat reference. |
| VideoHosting | Accurate with implementation change | Internal YouTube facade with `displayVideo`, URL validation, embed URL, and thumbnail helpers. |
| Booking | Accurate with extension | Appointment record with status methods. Adds `petID` and uses vet slots to prevent double-booking. |

## Design Pattern Status

- Template Method: implemented through `FirstAidContent.display()` and concrete overrides in Guide, Video, and Quiz. The User hierarchy shares identity fields and lifecycle helpers, but role-specific behaviors remain route-orchestrated.
- Facade: implemented through `Authentication` and `VideoHostingFacade`. Both hide concrete JWT/password and YouTube URL handling behind simple methods.
- Observer: implemented with `ChatSubject`, `ChatObserver`, and `WebSocketObserver`. The active observer registry lives in the chat route because WebSocket connections are request/runtime objects.

## Sequence Diagram Alignment

- Scenario 1, first-aid guide access: aligned through `SearchEngine.searchContent`, including exact category search and free-text fallback.
- Scenario 2, veterinary advice: aligned. Chat creation, message creation, history, booking creation, and booking acceptance exist. WebSocket delivery is route-managed.
- Scenario 3, content submission: aligned with extensions. The implementation uses `submitted` and `pending_verification` before `verified`, `published`, or `rejected`.
- Scenario 4, quiz attempt: aligned. Quiz now owns score calculation, answer evaluation, pass threshold, and recommendation selection. `QuizResult` persists attempts.
- Scenario 5, quiz explanations: aligned. Vets can set explanations and correct question/answer text through Question and Answer methods.
- Scenario 6, profile and pet management: aligned. User profile updates, pet updates, account deletion, pet cleanup, and session invalidation are implemented. Persistence remains route-orchestrated.

## Known Deliberate Changes

- `QuizResult` is an implementation persistence class, not an Assignment 2 candidate class.
- `assignedVetID`, `reviewComment`, `submitted`, and `pending_verification` were added to support a usable peer-review workflow.
- `Booking.petID` and veterinarian `availableSlots` were added to support pet-specific bookings and slot locking.
- Authentication is local JWT/bcrypt instead of an external provider, but exposed through an Authentication facade.
- Video seeds keep normal YouTube watch URLs; frontend rendering converts them to playable embeds.
- WebSocket observers are registered in the route layer because connections are runtime transport objects, not persistent domain objects.
