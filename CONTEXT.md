# UnserTurnierplan - Projekt-Kontext für Claude

> Diese Datei enthält alle wichtigen Informationen, damit Claude in neuen Chat-Sessions nahtlos weiterarbeiten kann.

## 📊 Projekt-Status

**Aktueller Stand:** Sprint 2 ABGESCHLOSSEN ✅  
**Nächster Sprint:** Sprint 3 - Tournament Management  
**Letzte Aktualisierung:** 12. November 2025  
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
- ⭐ **Multi-Sport-Support**
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

**API Endpoints Total:** 27 (13 User + 14 Club)  
**Database Tables:** 4 (users, clubs, club_members, alembic_version)

---

## 🚀 Sprint 3 - Tournament Management (NÄCHSTER SCHRITT)

### Ziele
Sprint 3 fokussiert sich auf die Kern-Funktionalität: Turniere erstellen und verwalten.

### Features
- **Tournament CRUD** - Turniere erstellen, bearbeiten, löschen
- **Tournament Types** - Verschiedene Turnierformate (Knockout, Round-Robin, Group Stage)
- **Registration** - Teilnehmer-Anmeldung
- **Schedule** - Spielplan-Generierung
- **Status Management** - Tournament Lifecycle (Draft, Published, Active, Completed)

### Aufgaben (Todo-Liste)

#### 1. Database Models
- [ ] Tournament Model
  - Basic Info (name, description, dates)
  - Tournament Type (knockout, round_robin, group_stage, etc.)
  - Status (draft, published, registration_open, active, completed, cancelled)
  - Sport Type (football, basketball, volleyball, etc.)
  - Participant Settings (min/max teams, registration deadline)
  - Relationships (club_id, created_by)
  
- [ ] TournamentParticipant Model (Many-to-Many)
  - Team/Participant Info
  - Registration Date
  - Status (pending, confirmed, cancelled)
  - Payment Status (if applicable)

#### 2. Schemas (Pydantic)
- [ ] TournamentBase, TournamentCreate, TournamentUpdate
- [ ] TournamentResponse, TournamentDetail
- [ ] TournamentParticipantBase, TournamentParticipantCreate
- [ ] TournamentParticipantResponse
- [ ] Tournament List/Filter Schemas

#### 3. Services
- [ ] TournamentService
  - CRUD operations
  - Tournament lifecycle management
  - Registration management
  - Schedule generation (basic)
  
- [ ] TournamentParticipantService
  - Registration handling
  - Participant management

#### 4. API Endpoints (~12 Endpoints)
**Tournament Management:**
- [ ] POST /api/v1/tournaments - Create tournament
- [ ] GET /api/v1/tournaments - List tournaments (with filters)
- [ ] GET /api/v1/tournaments/{id} - Get tournament details
- [ ] PUT /api/v1/tournaments/{id} - Update tournament
- [ ] DELETE /api/v1/tournaments/{id} - Delete tournament
- [ ] PUT /api/v1/tournaments/{id}/status - Change status (publish, start, end)

**Registration:**
- [ ] POST /api/v1/tournaments/{id}/register - Register team/participant
- [ ] GET /api/v1/tournaments/{id}/participants - List participants
- [ ] PUT /api/v1/tournaments/{id}/participants/{participant_id} - Update participant
- [ ] DELETE /api/v1/tournaments/{id}/participants/{participant_id} - Remove participant

**Query:**
- [ ] GET /api/v1/tournaments/my - My tournaments (as organizer)
- [ ] GET /api/v1/tournaments/participating - Tournaments I'm participating in

#### 5. Enums
- [ ] TournamentType (knockout, round_robin, group_stage, swiss, custom)
- [ ] TournamentStatus (draft, published, registration_open, active, completed, cancelled)
- [ ] SportType (football, basketball, volleyball, handball, hockey, tennis, etc.)
- [ ] ParticipantStatus (pending, confirmed, cancelled, waitlist)

#### 6. Business Rules
- [ ] Only club owners/admins can create tournaments
- [ ] Tournament creator has full control
- [ ] Registration only when status = registration_open
- [ ] Can't delete tournament with matches/results
- [ ] Status transitions (draft -> published -> active -> completed)

#### 7. Migration
- [ ] Alembic Migration 003
  - tournaments table
  - tournament_participants table
  - Enums
  - Indexes & Foreign Keys

#### 8. Tests
- [ ] TournamentService unit tests
- [ ] TournamentParticipantService unit tests
- [ ] Tournament API endpoint tests
- [ ] Permission tests

---

## 📋 Database Schema (Geplant für Sprint 3)

### tournaments Table
```sql
- id (UUID, PK)
- club_id (UUID, FK to clubs) - Hosting club
- created_by (UUID, FK to users) - Tournament organizer
- name (String, 200)
- slug (String, 200, unique, indexed)
- description (Text)
- banner_url (String)
- sport_type (Enum: football, basketball, etc.)
- tournament_type (Enum: knockout, round_robin, etc.)
- status (Enum: draft, published, etc.)
- start_date, end_date (DateTime)
- registration_start, registration_end (DateTime)
- location (String)
- min_participants, max_participants (Integer)
- participant_type (Enum: team, individual)
- rules (Text/JSON)
- prize_info (Text)
- entry_fee (Decimal, optional)
- is_public (Boolean) - Public or invite-only
- created_at, updated_at (DateTime)
```

### tournament_participants Table
```sql
- id (UUID, PK)
- tournament_id (UUID, FK to tournaments)
- participant_id (UUID, FK to clubs or users) - Depends on participant_type
- participant_name (String) - Team/Player name
- registration_date (DateTime)
- status (Enum: pending, confirmed, cancelled, waitlist)
- payment_status (Enum: pending, paid, refunded)
- notes (Text)
- seed (Integer, optional) - For seeding
- created_at, updated_at (DateTime)
```

---

## 🎯 Sprint 3 - Entwicklungs-Reihenfolge

### Phase 1: Models & Schemas (Tag 1)
1. Tournament Model mit allen Feldern
2. TournamentParticipant Model
3. Enums (TournamentType, TournamentStatus, SportType)
4. Alle Pydantic Schemas

### Phase 2: Services (Tag 2)
1. TournamentService - CRUD + Lifecycle
2. TournamentParticipantService
3. Permission-Checker

### Phase 3: API Endpoints (Tag 2-3)
1. Tournament CRUD Endpoints
2. Registration Endpoints
3. Query Endpoints
4. Status Management

### Phase 4: Migration & Integration (Tag 3)
1. Alembic Migration 003
2. Integration in main.py
3. Dependencies erweitern

### Phase 5: Testing (Tag 4)
1. Unit Tests
2. Integration Tests
3. Manual API Testing

---

## 💡 Wichtige Hinweise für Sprint 3

### Sport Types
Unterstützte Sportarten (initial):
- Football (Fußball) ⚽
- Basketball 🏀
- Volleyball 🏐
- Handball 🤾
- Hockey 🏑
- Tennis 🎾
- Table Tennis 🏓
- Badminton 🏸

### Tournament Types
- **Knockout/Elimination:** Klassisches K.O.-System
- **Round Robin:** Jeder gegen jeden
- **Group Stage:** Gruppenphase + K.O.-Runde
- **Swiss System:** Schweizer System (Chess-Style)
- **Custom:** Benutzerdefiniert

### Status Lifecycle
```
draft → published → registration_open → active → completed
                                    ↓
                                cancelled
```

### Permissions
- **Create Tournament:** Club owner/admin
- **Edit Tournament:** Tournament creator + Club owner/admin
- **Delete Tournament:** Tournament creator (only if no matches)
- **Register:** Any authenticated user (if registration_open)
- **Manage Participants:** Tournament creator + Club owner/admin

---

## 🔄 Was nach Sprint 3 kommt

### Sprint 4 - Match Management
- Match Model (Tournament -> Matches)
- Match Scheduling
- Score Entry
- Live Results

### Sprint 5 - Bracket Generation
- Automatic bracket generation
- Match tree/graph
- Seeding logic

### Sprint 6 - Rundown System
- Event timeline
- Activity scheduling
- Resource allocation

---

## 📁 Projekt-Struktur

```
UnserTurnierplan/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          ✅ Sprint 1 (7 Endpoints)
│   │   │   ├── users.py         ✅ Sprint 1 (6 Endpoints)
│   │   │   ├── clubs.py         ✅ Sprint 2 (14 Endpoints)
│   │   │   ├── tournaments.py   ⏳ Sprint 3 TODO
│   │   │   └── dependencies.py  ✅ Fertig + Club Permissions
│   │   ├── core/
│   │   │   ├── config.py        ✅ Fertig
│   │   │   └── security.py      ✅ Fertig
│   │   ├── db/
│   │   │   └── session.py       ✅ Fertig
│   │   ├── models/
│   │   │   ├── base.py          ✅ Fertig
│   │   │   ├── user.py          ✅ Sprint 1
│   │   │   ├── club.py          ✅ Sprint 2
│   │   │   ├── club_member.py   ✅ Sprint 2
│   │   │   └── tournament.py    ⏳ Sprint 3 TODO
│   │   ├── schemas/
│   │   │   ├── user.py          ✅ Sprint 1
│   │   │   ├── club.py          ✅ Sprint 2
│   │   │   └── tournament.py    ⏳ Sprint 3 TODO
│   │   ├── services/
│   │   │   ├── user_service.py  ✅ Sprint 1
│   │   │   ├── club_service.py  ✅ Sprint 2
│   │   │   ├── club_member_service.py  ✅ Sprint 2
│   │   │   └── tournament_service.py   ⏳ Sprint 3 TODO
│   │   ├── tests/               ⏳ TODO (alle Sprints)
│   │   └── main.py              ✅ Fertig (User + Club Routers)
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial_migration.py    ✅ Sprint 1
│   │       ├── 002_create_clubs.py         ✅ Sprint 2
│   │       └── 003_create_tournaments.py   ⏳ Sprint 3 TODO
│   ├── .env                     ✅ Fertig
│   ├── requirements.txt         ✅ Fertig (inkl. email-validator)
│   └── Dockerfile               ✅ Fertig
├── frontend/                    ⏳ TODO später (Sprint 10+)
├── docs/                        ✅ Fertig (9 Dateien)
├── .github/                     ✅ Fertig (Templates)
├── docker-compose.yml           ✅ Fertig
├── CONTEXT.md                   ✅ Fertig (diese Datei)
└── README.md                    ✅ Fertig
```

---

## 🔧 Wichtige Technische Details

### Database Schema (Aktuell - Sprint 2 Complete)

**users** Tabelle:
```sql
- id (UUID, PK)
- email (String, unique, indexed)
- password_hash (String)
- first_name, last_name (String)
- phone (String, optional)
- avatar_url (String, optional)
- language, timezone (String)
- email_verified, is_active, is_superuser (Boolean)
- two_factor_enabled (Boolean)
- last_login (DateTime)
- created_at, updated_at (DateTime)
```

**clubs** Tabelle:
```sql
- id (UUID, PK)
- name (String, unique, indexed)
- slug (String, unique, indexed)
- description (Text)
- logo_url, banner_url (String)
- address, city, postal_code, country (String)
- phone, email, website (String)
- verification_status (Enum: pending, verified, rejected)
- verification_badge_date (Date)
- verification_notes (String)
- founded_date (Date)
- member_count (Integer)
- is_active (Boolean)
- created_at, updated_at (DateTime)
```

**club_members** Tabelle (Many-to-Many):
```sql
- id (UUID, PK)
- club_id (UUID, FK to clubs)
- user_id (UUID, FK to users)
- role (Enum: owner, admin, manager, member, volunteer)
- department (String, optional)
- position (String, optional)
- notes (String)
- created_at, updated_at (DateTime)
- UNIQUE(club_id, user_id)
```

### Environment Variables (.env)
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/unserturnierplan
REDIS_URL=redis://redis:6379/0
SECRET_KEY=<generierter-key>
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

---

## 🐛 Bekannte Issues & Fixes

### Issue 1: Docker Healthcheck (GELÖST)
**Problem:** `CMD-BASH` statt `CMD-SHELL`  
**Lösung:** In docker-compose.yml geändert

### Issue 2: Alembic Import-Fehler (GELÖST)
**Problem:** `ModuleNotFoundError: No module named 'app'`  
**Lösung:** `sys.path.insert` in alembic/env.py hinzugefügt

### Issue 3: Email-Validator fehlt (GELÖST)
**Problem:** `ImportError: email-validator is not installed`  
**Lösung:** `email-validator==2.1.0` zu requirements.txt hinzugefügt

---

## 🎨 Code-Style & Best Practices

### Python Backend
- **PEP 8** Style Guide
- **Black** für Formatierung
- **isort** für Import-Sortierung
- **Type Hints** überall
- **Google-Style Docstrings**
- **Async/Await** konsequent nutzen

### Git Commit Messages
Verwende Conventional Commits:
- `feat:` - Neues Feature
- `fix:` - Bug Fix
- `docs:` - Dokumentation
- `test:` - Tests
- `refactor:` - Code-Refactoring
- `chore:` - Maintenance

### Testing
- **pytest** für alle Tests
- **pytest-asyncio** für async Tests
- **Ziel:** >80% Code Coverage
- Test-Struktur: `backend/app/tests/`

---

## 📚 Wichtige Dokumentations-Dateien

- **PROJECT_OVERVIEW.md** - Vollständige Feature-Liste
- **TECHNICAL_ARCHITECTURE.md** - System-Design & Architektur
- **DEVELOPMENT_ROADMAP.md** - 18-Monats-Plan, alle 23 Sprints
- **UI_UX_DESIGN.md** - Design-System & Component Library
- **MARKETING_STRATEGY.md** - Go-to-Market Plan
- **CONTRIBUTING.md** - Contribution Guidelines

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

# Tests ausführen (wenn vorhanden)
docker-compose exec backend pytest

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
2. **Prüfe den aktuellen Sprint-Status** (siehe "Sprint 2" oben)
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

### Code-Qualität:

```python
# ✅ GUTES Beispiel - Type Hints, Docstrings, Service Layer
async def get_club_by_id(
    db: AsyncSession, 
    club_id: UUID
) -> Optional[Club]:
    """
    Get club by ID.
    
    Args:
        db: Database session
        club_id: UUID of the club
        
    Returns:
        Club object or None if not found
    """
    result = await db.execute(
        select(Club).where(Club.id == club_id)
    )
    return result.scalar_one_or_none()

# ❌ SCHLECHTES Beispiel - Keine Types, keine Docs, inline DB
@app.get("/clubs/{id}")
def get_club(id):
    return db.query(Club).filter(Club.id == id).first()
```

---

## 🎯 Nächste konkrete Aufgabe (Sprint 3, Task 1)

**Aufgabe:** Tournament Model & TournamentParticipant Model erstellen

**Dateien zu erstellen:**
1. `backend/app/models/tournament.py`
2. `backend/app/models/tournament_participant.py`
3. `backend/app/schemas/tournament.py`
4. `backend/app/services/tournament_service.py`
5. `backend/app/services/tournament_participant_service.py`
6. `backend/app/api/tournaments.py`
7. `backend/alembic/versions/003_create_tournaments.py`

**Reihenfolge:**
1. Models definieren (mit Relationships & Enums)
2. Schemas erstellen (für API)
3. Service-Layer implementieren
4. API-Endpoints schreiben
5. Migration erstellen
6. Tests schreiben (optional für Sprint 3)

**Wichtige Enums:**
- TournamentType (knockout, round_robin, group_stage, swiss, custom)
- TournamentStatus (draft, published, registration_open, active, completed, cancelled)
- SportType (football, basketball, volleyball, handball, hockey, tennis, etc.)
- ParticipantStatus (pending, confirmed, cancelled, waitlist)

---

## 📞 Wichtige Befehle für Entwicklung

```bash
# Status prüfen
docker-compose ps

# Logs
docker-compose logs -f backend

# Migration erstellen
docker-compose exec backend alembic revision --autogenerate -m "Add tournaments"

# Migration ausführen
docker-compose exec backend alembic upgrade head

# Zurückrollen
docker-compose exec backend alembic downgrade -1

# Aktuelle Version
docker-compose exec backend alembic current

# Tests
docker-compose exec backend pytest -v

# Coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Code-Qualität
docker-compose exec backend black . --check
docker-compose exec backend isort . --check
docker-compose exec backend flake8

# Python Shell (im Container)
docker-compose exec backend python
>>> from app.models.user import User
>>> from app.db.session import AsyncSessionLocal

# Datenbank direkt
docker-compose exec db psql -U postgres -d unserturnierplan
\dt                    # Tabellen auflisten
\d tablename          # Tabellen-Struktur
\dT+                  # Enums auflisten
```

---

## 🏆 Projektziele (Reminder)

- **Zielmarkt:** 90.000 Sportvereine in Deutschland
- **Timeline:** 18 Monate bis Full-Release
- **MVP:** 4 Monate (Sprint 1-8)
- **Target Users:** Mittelgroße Vereine (100-500 Mitglieder)
- **Business Model:** Freemium (Free, Pro, Premium, Enterprise)

**Aktueller Fortschritt:** Sprint 2/23 Complete (≈9%)

---

## 🐛 Bekannte Issues & Lösungen

### Issue 1: Migration Enum already exists
**Problem:** `type "verification_status_enum" already exists`  
**Lösung:** 
```bash
docker-compose exec backend alembic downgrade 001
docker-compose exec db psql -U postgres -d unserturnierplan -c "DROP TYPE IF EXISTS verification_status_enum CASCADE;"
docker-compose exec backend alembic upgrade head
```

### Issue 2: Table already exists
**Problem:** `relation "clubs" already exists`  
**Lösung:** Downgrade zu vorheriger Migration und neu upgraden
```bash
docker-compose exec backend alembic downgrade 001
docker-compose exec backend alembic upgrade head
```

### Issue 3: Kompletter DB Reset (Nuclear Option)
```bash
docker-compose down -v
docker-compose up -d
sleep 30
docker-compose exec backend alembic upgrade head
```

---

**Diese Datei wird bei jedem größeren Fortschritt aktualisiert.**  
**Letzte Aktualisierung:** Nach Sprint 2 Completion (12. Nov 2025)