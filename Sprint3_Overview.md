# 🏆 Sprint 3 - Tournament Management

## 🎯 Ziel
Kern-Funktionalität für Turnierverwaltung implementieren.

---

## ✨ Features

### Tournament CRUD
- Turniere erstellen, bearbeiten, löschen
- Verschiedene Turnierformate (Knockout, Round-Robin, Group Stage, Swiss)
- Multi-Sport Support (Fußball, Basketball, Volleyball, etc.)
- Status-Management (Draft → Published → Active → Completed)

### Registration
- Teilnehmer-Anmeldung
- Registrierungs-Zeitfenster
- Min/Max Teilnehmer
- Team vs. Individual Mode

### Lifecycle
```
draft → published → registration_open → active → completed
                                    ↓
                                cancelled
```

---

## 📋 Models

### Tournament
```python
- id, created_at, updated_at
- club_id (FK → clubs)
- created_by (FK → users)
- name, slug, description
- banner_url
- sport_type (Enum)
- tournament_type (Enum)
- status (Enum)
- start_date, end_date
- registration_start, registration_end
- location
- min_participants, max_participants
- participant_type (team/individual)
- rules (Text/JSON)
- prize_info
- entry_fee (optional)
- is_public (Boolean)
```

### TournamentParticipant
```python
- id, created_at, updated_at
- tournament_id (FK → tournaments)
- participant_id (FK → clubs or users)
- participant_name
- registration_date
- status (Enum)
- payment_status (Enum)
- notes
- seed (optional)
```

---

## 🎨 Enums

```python
class SportType(str, Enum):
    FOOTBALL = "football"
    BASKETBALL = "basketball"
    VOLLEYBALL = "volleyball"
    HANDBALL = "handball"
    HOCKEY = "hockey"
    TENNIS = "tennis"
    TABLE_TENNIS = "table_tennis"
    BADMINTON = "badminton"

class TournamentType(str, Enum):
    KNOCKOUT = "knockout"
    ROUND_ROBIN = "round_robin"
    GROUP_STAGE = "group_stage"
    SWISS = "swiss"
    CUSTOM = "custom"

class TournamentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    REGISTRATION_OPEN = "registration_open"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ParticipantStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLIST = "waitlist"
```

---

## 🔌 API Endpoints (12)

### Tournament Management (6)
```
POST   /api/v1/tournaments
GET    /api/v1/tournaments
GET    /api/v1/tournaments/{id}
PUT    /api/v1/tournaments/{id}
DELETE /api/v1/tournaments/{id}
PUT    /api/v1/tournaments/{id}/status
```

### Registration (4)
```
POST   /api/v1/tournaments/{id}/register
GET    /api/v1/tournaments/{id}/participants
PUT    /api/v1/tournaments/{id}/participants/{participant_id}
DELETE /api/v1/tournaments/{id}/participants/{participant_id}
```

### Query (2)
```
GET    /api/v1/tournaments/my
GET    /api/v1/tournaments/participating
```

---

## 🔐 Permissions

- **Create Tournament:** Club owner/admin
- **Edit Tournament:** Tournament creator + Club owner/admin
- **Delete Tournament:** Tournament creator (only if no matches/results)
- **Register:** Any authenticated user (if registration_open)
- **Manage Participants:** Tournament creator + Club owner/admin

---

## 📝 Schemas (Pydantic)

```python
# Base & CRUD
TournamentBase
TournamentCreate
TournamentUpdate
TournamentResponse
TournamentDetail

# Participants
TournamentParticipantBase
TournamentParticipantCreate
TournamentParticipantResponse

# Lists & Filters
TournamentListResponse
TournamentFilterParams
```

---

## ⚙️ Services

### TournamentService
```python
- create(db, tournament_in, club_id, creator_id)
- get_by_id(db, tournament_id)
- get_by_slug(db, slug)
- list_tournaments(db, filters)
- update(db, tournament_id, tournament_in)
- delete(db, tournament_id)
- update_status(db, tournament_id, new_status)
- can_register(db, tournament)
```

### TournamentParticipantService
```python
- register(db, tournament_id, participant_data)
- get_participants(db, tournament_id)
- update_participant(db, participant_id, data)
- remove_participant(db, participant_id)
- is_registered(db, tournament_id, user_id)
```

---

## 🗄️ Migration 003

```sql
-- Enums
CREATE TYPE sport_type_enum
CREATE TYPE tournament_type_enum
CREATE TYPE tournament_status_enum
CREATE TYPE participant_status_enum
CREATE TYPE payment_status_enum

-- Tables
CREATE TABLE tournaments (...)
CREATE TABLE tournament_participants (...)

-- Indexes
CREATE INDEX ix_tournaments_slug
CREATE INDEX ix_tournaments_club_id
CREATE INDEX ix_tournaments_status
CREATE INDEX ix_tournament_participants_tournament_id
CREATE UNIQUE INDEX uq_tournament_participants
```

---

## ✅ Entwicklungs-Checklist

### Phase 1: Models & Enums
- [ ] SportType Enum
- [ ] TournamentType Enum
- [ ] TournamentStatus Enum
- [ ] ParticipantStatus Enum
- [ ] Tournament Model
- [ ] TournamentParticipant Model
- [ ] Relationships zu Club & User

### Phase 2: Schemas
- [ ] TournamentBase, Create, Update
- [ ] TournamentResponse, Detail
- [ ] TournamentParticipant Schemas
- [ ] Filter & List Schemas

### Phase 3: Services
- [ ] TournamentService - CRUD
- [ ] TournamentService - Lifecycle
- [ ] TournamentParticipantService
- [ ] Permission Checker

### Phase 4: API
- [ ] Tournament CRUD Endpoints (6)
- [ ] Registration Endpoints (4)
- [ ] Query Endpoints (2)
- [ ] Integration in main.py

### Phase 5: Migration
- [ ] Create migration 003
- [ ] Test migration up/down
- [ ] Verify tables & indexes

### Phase 6: Testing (Optional)
- [ ] Unit Tests
- [ ] Integration Tests
- [ ] Manual API Tests

---

## 🧪 Test-Szenarien

### 1. Tournament erstellen
```bash
curl -X POST http://localhost:8000/api/v1/tournaments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sommerpokal 2025",
    "club_id": "CLUB_UUID",
    "sport_type": "football",
    "tournament_type": "knockout",
    "start_date": "2025-07-15T10:00:00",
    "end_date": "2025-07-15T18:00:00",
    "max_participants": 16
  }'
```

### 2. Registrieren
```bash
curl -X POST http://localhost:8000/api/v1/tournaments/{id}/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "participant_name": "FC Beispiel",
    "participant_type": "team"
  }'
```

### 3. Status ändern
```bash
curl -X PUT http://localhost:8000/api/v1/tournaments/{id}/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "registration_open"}'
```

---

## 🚀 Nächste Schritte nach Sprint 3

### Sprint 4 - Match Management
- Match Model
- Match Scheduling
- Score Entry
- Live Results

### Sprint 5 - Bracket Generation
- Automatic bracket creation
- Match tree/graph
- Seeding logic

### Sprint 6 - Rundown System
- Event timeline
- Activity scheduling

---

## 💡 Business Rules

1. **Nur Club-Owner/Admins** können Turniere erstellen
2. **Tournament Creator** hat volle Kontrolle
3. **Registration** nur wenn status = `registration_open`
4. **Kann nicht löschen** wenn Matches existieren
5. **Status-Übergänge** müssen validiert werden
6. **Min/Max Participants** wird geprüft
7. **Registration Deadline** wird enforced

---

## 📊 Erfolgs-Kriterien

Nach Sprint 3:
- [ ] 12 neue Tournament-Endpoints funktionieren
- [ ] Turniere können erstellt werden
- [ ] Registrierung funktioniert
- [ ] Status-Übergänge validiert
- [ ] Permissions korrekt
- [ ] 6 Tabellen in DB (users, clubs, club_members, tournaments, tournament_participants, alembic_version)
- [ ] API-Dokumentation vollständig

---

**Sprint 3 geschätzte Dauer:** 3-4 Tage  
**Code Lines:** ~2.500  
**API Endpoints danach:** 39 total

**Los geht's!** 🚀