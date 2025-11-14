# UnserTurnierplan - Projekt-Kontext für Claude

> Diese Datei enthält alle wichtigen Informationen, damit Claude in neuen Chat-Sessions nahtlos weiterarbeiten kann.

## 📊 Projekt-Status

**Aktueller Stand:** Sprint 3 ABGESCHLOSSEN ✅  
**Nächster Sprint:** Sprint 4 - Match Scheduling & Brackets (oder alternatives Feature)  
**Letzte Aktualisierung:** 14. November 2025  
**GitHub Repository:** Auf `main` Branch gepusht  

---

## 🎯 Projekt-Übersicht

**UnserTurnierplan** ist eine All-in-One-Plattform für Sportvereine zur Organisation von Turnieren und Veranstaltungen.

### Technologie-Stack
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 16
- **Cache:** Redis 7
- **ORM:** SQLAlchemy (async)
- **Migrations:** Alembic
- **Container:** Docker & Docker-Compose
- **Frontend:** React/Next.js (geplant - noch nicht gestartet)

### Unique Features
- ⭐ **Rundown-Management** (einzigartig im Markt)
- ⭐ **Vereinsverifizierung** mit Badge-System
- ⭐ **Multi-Sport-Support** (Team & Individual)
- ⭐ **Catering-Integration**
- ⭐ **Mobile Native Apps** (geplant)

---

## ✅ Was ist FERTIG

### Sprint 1 - User Management & Authentication ✅
- Backend Infrastructure (FastAPI, PostgreSQL, Redis)
- User Model & Authentication System
- JWT Tokens (Access + Refresh)
- 13 User/Auth API Endpoints
- Vollständige Dokumentation

### Sprint 2 - Club Management ✅
- Club & ClubMember Models
- 12 Club Schemas (Pydantic)
- ClubService & ClubMemberService
- 14 Club API Endpoints
- Permission System mit 5 Rollen
- Database Migration 002
- **23/23 Tests bestanden** ✅
- Vollständige Dokumentation

**Test-Suite:** `tests/sprint2_tests.sh` (100% Pass Rate)

### Sprint 3 - Tournament Management ✅ (COMPLETED)
- Tournament & TournamentParticipant Models
- 16 Tournament Schemas (Pydantic)
- TournamentService & TournamentParticipantService
- 23 Tournament API Endpoints
- Status Workflow System
- Multi-Sport Support (8+ Sportarten)
- **Team AND Individual Support** ✅
- Flexible Participant System
- Payment Tracking
- Registration Management
- Database Migration 003
- **27/27 Tests bestanden** ✅
- Vollständige Dokumentation

**Test-Suite:** `tests/sprint3_tests.sh` (100% Pass Rate)

**Lessons Learned Sprint 3:**
- `or_` Import in SQLAlchemy für komplexe Queries nicht vergessen
- URL-Encoding für Umlaute in Tests: `M%C3%BCnchen` statt `München`
- Status-Transitions müssen Business Rules folgen (cancelled state für delete)
- Foreign Keys müssen als String in SQLAlchemy Relationships: `"[Tournament.created_by]"`
- Participant System ist flexibel genug für Teams UND Einzelspieler

**API Endpoints Total:** 50 (13 User + 14 Club + 23 Tournament)  
**Database Tables:** 6 (users, clubs, club_members, tournaments, tournament_participants, alembic_version)

---

## 🎾 Multi-Sport & Individual Participant Support

### ✅ Struktur ist BEREIT für Team- und Einzelsport

Das Tournament-System ist **vollständig flexibel** für beide Teilnehmertypen:

#### Participant Type Enum
```python
class ParticipantType(str, Enum):
    TEAM = "team"        # Mannschaften (Fußball, Basketball, etc.)
    INDIVIDUAL = "individual"  # Einzelpersonen (Tennis, Schach, etc.)
```

#### Flexible Participant Registration

**TournamentParticipant Model unterstützt BEIDE Szenarien:**

```python
# Für TEAMS (z.B. Fußball)
tournament_participants:
- participant_club_id: UUID (FK to clubs) ✅
- participant_user_id: NULL
- participant_name: "FC Bayern München II"
- display_name: "FCB II"

# Für INDIVIDUAL (z.B. Tennis, Schach)
tournament_participants:
- participant_club_id: UUID (FK to clubs) ✅ Optional - Club des Spielers
- participant_user_id: UUID (FK to users) ✅ Der Spieler selbst
- participant_name: "Anna Schmidt"
- display_name: "A. Schmidt"
```

#### Wie es funktioniert für verschiedene Sportarten:

**⚽ Fußball / Basketball / Volleyball (Team-Sport):**
```json
{
  "participant_type": "team",
  "participant_club_id": "uuid-of-club",
  "participant_name": "Erste Mannschaft",
  "display_name": "1. Mannschaft"
}
```

**🎾 Tennis / 🏓 Tischtennis (Individual, aber aus Club):**
```json
{
  "participant_type": "individual",
  "participant_club_id": "uuid-of-club",  // Spieler ist Mitglied eines Clubs
  "participant_user_id": "uuid-of-user",  // Der Spieler
  "participant_name": "Max Mustermann",
  "display_name": "M. Mustermann"
}
```

**♟️ Schach (Individual, unabhängig):**
```json
{
  "participant_type": "individual",
  "participant_club_id": null,  // Kein Club
  "participant_user_id": "uuid-of-user",  // Der Spieler
  "participant_name": "Anna Schmidt",
  "display_name": "A. Schmidt"
}
```

#### Vorteile dieser Struktur:

✅ **Flexibel:** Unterstützt Teams, Einzelspieler mit/ohne Club  
✅ **Skalierbar:** Einfach erweiterbar für Doppel (Tennis/Badminton)  
✅ **Trackbar:** Spieler bleiben mit ihrem User-Account verknüpft  
✅ **Club-Integration:** Clubs können sowohl Teams als auch Einzelspieler melden  
✅ **Multi-Sport:** Ein System für alle Sportarten  

#### Zukünftige Erweiterungen (Sprint 4+):

- **Doppel/Paare:** Zwei participant_user_ids pro Registration
- **Staffeln:** Mehrere Spieler pro Team-Registration
- **Ersatzspieler:** Additional players field
- **Team-Roster:** Separate player_list JSON field (bereits vorhanden!)

### Unterstützte Sportarten (aktuell)

**Team-Sports:**
- ⚽ Football (Fußball)
- 🏀 Basketball
- 🏐 Volleyball
- 🤾 Handball

**Individual Sports:**
- 🎾 Tennis
- 🏓 Table Tennis
- 🏸 Badminton
- ♟️ Chess (Schach)

Alle Sportarten nutzen **dasselbe Tournament-System** mit flexiblem `participant_type`!

---

## 🚀 Sprint 4 - Optionen (NÄCHSTER SCHRITT)

### Option A: Match Scheduling & Brackets
- Match Model & Scheduling
- Bracket Generation (Knockout)
- Round-Robin Schedule Generation
- Match Results & Scoring
- Live Standings

### Option B: Advanced Features
- File Uploads (Tournament Banners, Documents)
- Email Notifications System
- Advanced Reporting & Analytics
- Tournament Templates
- Real-time Updates (WebSockets)

### Option C: Frontend Start
- Next.js Setup
- Tournament List Page
- Tournament Detail Page
- Registration Flow
- Basic Dashboard

**Entscheidung steht noch aus - Diskussion im nächsten Chat!**

---

## 📋 Database Schema (Aktuell)

### tournaments Table ✅
```sql
- id (UUID, PK)
- club_id (UUID, FK to clubs)
- created_by (UUID, FK to users)
- name (String, 200)
- slug (String, 200, unique, indexed)
- description (Text)
- banner_url (String)
- department (String) - Club-Abteilung
- sport_type (Enum: football, basketball, volleyball, handball)
- tournament_type (Enum: knockout, round_robin, group_stage, swiss)
- status (Enum: draft, published, registration_open, active, completed, cancelled)
- start_date, end_date (DateTime)
- registration_start, registration_end (DateTime)
- location (String)
- venue_name, address, city, postal_code, country (String)
- participant_type (Enum: team, individual) ✅
- min_participants, max_participants (Integer)
- current_participants (Integer) - Cached count
- rules (Text)
- prize_info (Text)
- entry_fee (Decimal, optional)
- is_public (Boolean)
- is_active (Boolean)
- contact_email, contact_phone (String)
- created_at, updated_at (DateTime)
```

### tournament_participants Table ✅
```sql
- id (UUID, PK)
- tournament_id (UUID, FK to tournaments)
- participant_club_id (UUID, FK to clubs, nullable) ✅
- participant_user_id (UUID, FK to users, nullable) ✅
- registered_by (UUID, FK to users) - Who registered
- participant_name (String) - Team/Player name
- display_name (String) - Display name for brackets
- contact_email, contact_phone (String)
- registration_date (DateTime)
- status (Enum: pending, confirmed, checked_in, withdrawn)
- payment_status (Enum: pending, paid, refunded)
- payment_amount (Decimal)
- payment_date, payment_reference (String)
- seed (Integer, nullable) - For seeding in brackets
- notes (Text)
- player_list (Text) - JSON with team roster ✅
- created_at, updated_at (DateTime)
```

### Indexes & Constraints ✅
```sql
-- Tournaments
CREATE INDEX idx_tournament_club_status ON tournaments(club_id, status);
CREATE INDEX idx_tournament_sport_status ON tournaments(sport_type, status);
CREATE INDEX idx_tournament_dates ON tournaments(start_date, end_date);
CREATE INDEX idx_tournament_registration ON tournaments(registration_start, registration_end);

-- Tournament Participants
CREATE INDEX idx_participant_tournament ON tournament_participants(tournament_id);
CREATE INDEX idx_participant_club ON tournament_participants(participant_club_id);
CREATE INDEX idx_participant_user ON tournament_participants(participant_user_id);
CREATE INDEX idx_participant_status ON tournament_participants(status);
```

---

## 🎯 Sprint 3 - Entwicklungs-Reihenfolge (Completed)

### Phase 1: Models & Schemas ✅
- [x] Tournament Model mit allen Feldern
- [x] TournamentParticipant Model
- [x] 6 Enums (SportType, TournamentType, TournamentStatus, ParticipantType, ParticipantStatus, PaymentStatus)
- [x] 16 Pydantic Schemas

### Phase 2: Services ✅
- [x] TournamentService - CRUD + Lifecycle + Permissions
- [x] TournamentParticipantService - Registration + Management
- [x] Status Transition Validation
- [x] Permission Checks

### Phase 3: API Endpoints ✅
- [x] 8 Tournament CRUD Endpoints
- [x] 7 Participant Management Endpoints
- [x] 2 User Query Endpoints
- [x] 6 Filter & Statistics Endpoints

### Phase 4: Migration & Integration ✅
- [x] Alembic Migration 003
- [x] Integration in main.py
- [x] Router registration
- [x] Dependency updates

### Phase 5: Testing ✅
- [x] Comprehensive Integration Test Suite
- [x] 27 Test Cases covering all endpoints
- [x] Multi-user scenarios
- [x] Permission tests
- [x] 100% Pass Rate

---

## 💡 Wichtige Hinweise für Entwicklung

### Sport Types (Aktuell unterstützt)
```python
class SportType(str, Enum):
    FOOTBALL = "football"      # ⚽ Fußball
    BASKETBALL = "basketball"  # 🏀 Basketball
    VOLLEYBALL = "volleyball"  # 🏐 Volleyball
    HANDBALL = "handball"      # 🤾 Handball
    TENNIS = "tennis"          # 🎾 Tennis (Individual)
    TABLE_TENNIS = "table_tennis"  # 🏓 Tischtennis (Individual)
    BADMINTON = "badminton"    # 🏸 Badminton (Individual/Doppel)
    CHESS = "chess"            # ♟️ Schach (Individual)
```

### Tournament Types
```python
class TournamentType(str, Enum):
    KNOCKOUT = "knockout"           # K.O.-System
    ROUND_ROBIN = "round_robin"     # Jeder gegen jeden
    GROUP_STAGE = "group_stage"     # Gruppen + K.O.
    SWISS = "swiss"                 # Schweizer System (Schach)
```

### Status Lifecycle
```
draft → published → registration_open → active → completed
   ↓         ↓              ↓              ↓
                    cancelled (final state)
```

**Erlaubte Transitions:**
- draft → published, cancelled
- published → registration_open, cancelled
- registration_open → active, cancelled
- active → completed, cancelled
- completed → (final)
- cancelled → (final)

### Permissions
- **Create Tournament:** Club owner/admin (for specific club)
- **Update Tournament:** Tournament creator OR Club owner/admin
- **Delete Tournament:** Tournament creator (only draft/cancelled status)
- **Register Participant:** Any authenticated user
- **Manage Participants:** Tournament creator OR Club owner/admin

---

## 🏗️ Projekt-Struktur (Aktuell)

```
UnserTurnierplan/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_create_users.py ✅
│   │       ├── 002_create_clubs.py ✅
│   │       └── 003_create_tournaments.py ✅
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py ✅
│   │   │   ├── auth.py ✅
│   │   │   ├── users.py ✅
│   │   │   ├── clubs.py ✅
│   │   │   ├── tournaments.py ✅ NEW!
│   │   │   └── dependencies.py ✅
│   │   ├── core/
│   │   │   ├── config.py ✅
│   │   │   └── security.py ✅
│   │   ├── db/
│   │   │   ├── session.py ✅
│   │   │   └── base.py ✅
│   │   ├── models/
│   │   │   ├── __init__.py ✅
│   │   │   ├── base.py ✅
│   │   │   ├── user.py ✅
│   │   │   ├── club.py ✅
│   │   │   ├── club_member.py ✅
│   │   │   ├── tournament.py ✅ NEW!
│   │   │   └── tournament_participant.py ✅ NEW!
│   │   ├── schemas/
│   │   │   ├── __init__.py ✅
│   │   │   ├── user.py ✅
│   │   │   ├── club.py ✅
│   │   │   └── tournament.py ✅ NEW! (16 schemas)
│   │   ├── services/
│   │   │   ├── __init__.py ✅
│   │   │   ├── user_service.py ✅
│   │   │   ├── club_service.py ✅
│   │   │   ├── club_member_service.py ✅
│   │   │   ├── tournament_service.py ✅ NEW!
│   │   │   └── tournament_participant_service.py ✅ NEW!
│   │   ├── main.py ✅
│   │   └── __init__.py
│   ├── tests/ (pytest - optional)
│   ├── .env
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
├── tests/
│   ├── sprint2_tests.sh ✅ (100% Pass)
│   └── sprint3_tests.sh ✅ (100% Pass) NEW!
├── docker-compose.yml ✅
├── .gitignore
└── README.md
```

---

## 📊 API Endpoints Übersicht

### User & Auth (13 Endpoints) - Sprint 1
- POST /api/v1/auth/register
- POST /api/v1/auth/login/json
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET /api/v1/users/me
- PUT /api/v1/users/me
- DELETE /api/v1/users/me
- GET /api/v1/users/{id}
- GET /api/v1/users
- ... (+ 4 weitere)

### Clubs (14 Endpoints) - Sprint 2
- POST /api/v1/clubs
- GET /api/v1/clubs
- GET /api/v1/clubs/{id}
- GET /api/v1/clubs/slug/{slug}
- PUT /api/v1/clubs/{id}
- DELETE /api/v1/clubs/{id}
- GET /api/v1/clubs/count
- GET /api/v1/clubs/{id}/members
- POST /api/v1/clubs/{id}/members
- PUT /api/v1/clubs/{id}/members/{user_id}
- DELETE /api/v1/clubs/{id}/members/{user_id}
- GET /api/v1/clubs/me/memberships
- ... (+ 2 weitere)

### Tournaments (23 Endpoints) - Sprint 3 ✅ NEW!

**Tournament Management (8):**
- POST /api/v1/tournaments - Create tournament
- GET /api/v1/tournaments - List tournaments (with filters)
- GET /api/v1/tournaments/{id} - Get tournament details
- GET /api/v1/tournaments/slug/{slug} - Get by slug
- PUT /api/v1/tournaments/{id} - Update tournament
- DELETE /api/v1/tournaments/{id} - Delete tournament
- PUT /api/v1/tournaments/{id}/status - Update status
- GET /api/v1/tournaments/{id}/statistics - Get statistics

**Participant Management (7):**
- POST /api/v1/tournaments/{id}/register - Register participant
- GET /api/v1/tournaments/{id}/participants - List participants
- GET /api/v1/tournaments/{id}/participants/{pid} - Get participant
- PUT /api/v1/tournaments/{id}/participants/{pid} - Update participant
- DELETE /api/v1/tournaments/{id}/participants/{pid} - Remove participant
- PUT /api/v1/tournaments/{id}/participants/{pid}/status - Update status
- PUT /api/v1/tournaments/{id}/participants/{pid}/payment - Update payment

**User Queries (2):**
- GET /api/v1/tournaments/my/created - My created tournaments
- GET /api/v1/tournaments/my/participating - My participations

**Filter & Search (6 built-in filters):**
- ?sport_type=football
- ?tournament_type=knockout
- ?status=registration_open
- ?city=München
- ?start_date_from=2025-01-01
- ?start_date_to=2025-12-31

**Total: 50 API Endpoints**

---

## 🚀 Wie man lokal entwickelt

```bash
# Projekt starten
cd UnserTurnierplan
docker-compose up -d

# Logs anschauen
docker-compose logs -f backend

# Migration ausführen
docker-compose exec backend alembic upgrade head

# Sprint 2 Tests
tests/sprint2_tests.sh

# Sprint 3 Tests
tests/sprint3_tests.sh

# Code formatieren
docker-compose exec backend black .
docker-compose exec backend isort .

# In Container einloggen
docker-compose exec backend bash

# Neu bauen nach Änderungen
docker-compose build backend
docker-compose up -d
```

---

## 💡 Für Claude: Wie mit diesem Projekt weiterarbeiten

### Bei Fortsetzung einer Session:

1. **Lies diese CONTEXT.md Datei** vollständig
2. **Prüfe den aktuellen Sprint-Status** (Sprint 3 Complete!)
3. **Schaue in Projekt-Struktur** welche Dateien schon existieren
4. **Folge dem SOLID-Prinzip** - der User besteht darauf!
5. **Arbeite iterativ** - erst Models, dann Schemas, dann Services, dann API
6. **Erstelle Tests parallel** zur Feature-Entwicklung
7. **Dokumentiere alle Änderungen** in Code-Kommentaren
8. **Aktualisiere diese CONTEXT.md** bei größeren Änderungen

### Wichtige Prinzipien:

- ✅ **Type Safety** - Überall Type Hints
- ✅ **Async-First** - Konsequent async/await
- ✅ **Service Layer** - Business Logic trennen von Endpoints
- ✅ **Pydantic Validation** - Automatische Input-Validierung
- ✅ **SOLID Principles** - Clean Architecture
- ✅ **DRY** - Don't Repeat Yourself
- ✅ **Tests** - Test-Driven Development wo möglich
- ✅ **Enum Serialization** - IMMER `use_enum_values=True` in Schemas
- ✅ **JSON Parsing** - `jq` in Bash-Scripts statt grep/cut
- ✅ **Response Models** - Explizite response_model in FastAPI Endpoints
- ✅ **URL Encoding** - Umlaute in Tests URL-encoden (M%C3%BCnchen)
- ✅ **Foreign Keys** - Als String in Relationships: `"[Model.column]"`

### Code-Qualität:

```python
# ✅ GUTES Beispiel - Type Hints, Docstrings, Service Layer
async def get_tournament_by_id(
    db: AsyncSession, 
    tournament_id: UUID,
    load_relationships: bool = False
) -> Optional[Tournament]:
    """
    Get tournament by ID.
    
    Args:
        db: Database session
        tournament_id: UUID of the tournament
        load_relationships: Load related data (club, participants)
        
    Returns:
        Tournament object or None if not found
    """
    query = select(Tournament).where(Tournament.id == tournament_id)
    
    if load_relationships:
        query = query.options(
            selectinload(Tournament.club),
            selectinload(Tournament.participants)
        )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

# ❌ SCHLECHTES Beispiel - Keine Types, keine Docs, inline DB
@app.get("/tournaments/{id}")
def get_tournament(id):
    return db.query(Tournament).filter(Tournament.id == id).first()
```

---

## 📞 Wichtige Befehle für Entwicklung

```bash
# Status prüfen
docker-compose ps

# Logs
docker-compose logs -f backend

# Migration erstellen
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Migration ausführen
docker-compose exec backend alembic upgrade head

# Zurückrollen
docker-compose exec backend alembic downgrade -1

# Aktuelle Version
docker-compose exec backend alembic current

# Tests ausführen
tests/sprint2_tests.sh  # Club Management
tests/sprint3_tests.sh  # Tournament Management

# Code-Qualität
docker-compose exec backend black . --check
docker-compose exec backend isort . --check

# Datenbank direkt
docker-compose exec db psql -U postgres -d unserturnierplan
\dt                    # Tabellen auflisten
\d tablename          # Tabellen-Struktur
\dT+                  # Enums auflisten
SELECT * FROM tournaments LIMIT 5;
```

---

## 🏆 Projektziele (Reminder)

- **Zielmarkt:** 90.000 Sportvereine in Deutschland
- **Timeline:** 18 Monate bis Full-Release
- **MVP:** 4 Monate (Sprint 1-8)
- **Target Users:** Mittelgroße Vereine (100-500 Mitglieder)
- **Business Model:** Freemium (Free, Pro, Premium, Enterprise)

**Aktueller Fortschritt:** Sprint 3/23 Complete (≈13%) 🎉  
**Test-Coverage:** 
- Sprint 2: 23/23 Tests (100%) ✅
- Sprint 3: 27/27 Tests (100%) ✅
- **Total: 50/50 Tests (100%)** ✅

---

## 🐛 Bekannte Issues & Lösungen

### Sprint 2 - Enum Serialization Issues (GELÖST)
**Problem:** Pydantic konnte SQLAlchemy Enums nicht serialisieren  
**Lösung:** `use_enum_values=True` in ConfigDict + `values_callable` in SQLAlchemy

### Sprint 2 - URL Encoding Umlaute (GELÖST)
**Problem:** curl konnte Umlaute in Query-Parametern nicht verarbeiten  
**Lösung:** URL-Encoding verwenden: `M%C3%BCnchen` statt `München`

### Sprint 3 - Missing `or_` Import (GELÖST)
**Problem:** `NameError: name 'or_' is not defined` in tournament_participant_service  
**Lösung:** `from sqlalchemy import select, and_, or_, func`

### Sprint 3 - Foreign Keys in Relationships (GELÖST)
**Problem:** `foreign_keys=[column]` funktioniert nicht  
**Lösung:** String verwenden: `foreign_keys="[Tournament.created_by]"`

### Sprint 3 - User Model Relationship (GELÖST)
**Problem:** `User.tournaments references Tournament.club`  
**Lösung:** Korrekte Relationship hinzufügen:
```python
tournaments_created = relationship(
    "Tournament", 
    back_populates="creator",
    foreign_keys="Tournament.created_by"
)
```

### Sprint 3 - Delete Tournament Business Rule (GELÖST)
**Problem:** Tournament im Status `registration_open` kann nicht gelöscht werden  
**Lösung:** Erst auf `cancelled` setzen, dann löschen (Business Rule ist korrekt!)

### Sprint 3 - City Filter URL Encoding (GELÖST)
**Problem:** `city=München` gibt Parse Error  
**Lösung:** URL-Encoding verwenden: `city=M%C3%BCnchen`

### Issue: Migration Enum already exists
**Lösung:** 
```bash
docker-compose exec backend alembic downgrade 001
docker-compose exec db psql -U postgres -d unserturnierplan -c "DROP TYPE IF EXISTS enum_name CASCADE;"
docker-compose exec backend alembic upgrade head
```

### Issue: Kompletter DB Reset (Nuclear Option)
```bash
docker-compose down -v
docker-compose up -d
sleep 30
docker-compose exec backend alembic upgrade head
```

---

## 📝 Sprint 3 - Detaillierte Dokumentation

### Files Created
1. `backend/app/models/tournament.py` (223 lines)
2. `backend/app/models/tournament_participant.py` (154 lines)
3. `backend/app/schemas/tournament.py` (16 schemas, 400+ lines)
4. `backend/app/services/tournament_service.py` (533 lines)
5. `backend/app/services/tournament_participant_service.py` (496 lines)
6. `backend/app/api/tournaments.py` (555 lines)
7. `backend/alembic/versions/003_create_tournaments.py`
8. `tests/sprint3_tests.sh` (631 lines)

### Files Modified
1. `backend/app/models/user.py` - Added `tournaments_created` relationship
2. `backend/app/api/__init__.py` - Registered tournaments router

### Total Lines of Code Added
- Models: ~377 lines
- Schemas: ~400 lines
- Services: ~1029 lines
- API: ~555 lines
- Tests: ~631 lines
- **Total: ~2992 lines of production code**

### Key Features Implemented
- ✅ Complete Tournament CRUD
- ✅ Flexible Participant System (Team & Individual)
- ✅ Status Workflow with Validation
- ✅ Registration Management
- ✅ Payment Tracking
- ✅ Multi-Sport Support
- ✅ Advanced Filtering
- ✅ Permission System
- ✅ Statistics & Analytics
- ✅ Slug-based URLs

---

**Diese Datei wird bei jedem größeren Fortschritt aktualisiert.**  
**Letzte Aktualisierung:** Nach Sprint 3 Completion (14. Nov 2025)