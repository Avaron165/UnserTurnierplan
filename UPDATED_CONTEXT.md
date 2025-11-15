# UnserTurnierplan - Projekt-Kontext für Claude (UPDATED mit Sprint 4)

> Diese Datei enthält alle wichtigen Informationen für nahtlose Fortsetzung in neuen Chat-Sessions.

## 📊 Projekt-Status

**Aktueller Stand:** Sprint 4 ABGESCHLOSSEN ✅  
**Nächster Sprint:** Sprint 5 - Advanced Tournament Formats  
**Letzte Aktualisierung:** 15. November 2025  
**GitHub Repository:** Avaron165/UnserTurnierplan (Branch: `main`)  

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
- ⭐ **Flexible Match System** (2-N Teilnehmer für Rennen!)
- ⭐ **Automatic Bracket Generation** (Knockout + Round-Robin)
- ⭐ **Catering-Integration** (geplant)
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

### Sprint 3 - Tournament Management ✅
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

### Sprint 4 - Match Scheduling & Brackets ✅ (NEU!)
- **Match, MatchParticipant, TournamentStandings Models**
- **17 Match Schemas** (Pydantic)
- **MatchService, BracketService, StandingsService**
- **17 Match API Endpoints**
- **Knockout Bracket Generation** (Single Elimination)
- **Round-Robin Schedule Generation** (Circle Method)
- **Flexible JSONB Scoring System** (Sport-agnostic)
- **Tournament Standings Calculation** (Cached)
- **2-N Participant Support** (für Rennen!)
- **Match Progression System** (Winner advancement)
- Database Migration 004
- **27/27 Tests bestanden** ✅
- **~2,960 Lines of Code**

**API Endpoints Total:** 67 (13 User + 14 Club + 23 Tournament + 17 Match)  
**Database Tables:** 9 (users, clubs, club_members, tournaments, tournament_participants, matches, match_participants, tournament_standings, alembic_version)

---

## 🎾 Multi-Sport & Match System

### Participant Types ✅
```python
class ParticipantType(str, Enum):
    TEAM = "team"        # Mannschaften (Fußball, Basketball, etc.)
    INDIVIDUAL = "individual"  # Einzelpersonen (Tennis, Schach, etc.)
```

### Match System - FLEXIBLE 2-N Participants! ✅
```python
# Standard 2-Player Match (Fußball)
match_participants:
- participant_id: UUID (Team 1)
- slot_number: 1
- team_side: "home"
- score_value: 2

- participant_id: UUID (Team 2)
- slot_number: 2
- team_side: "away"
- score_value: 1

# Multi-Player Match (Rennen mit 10 Teilnehmern)
match_participants:
- participant_id: UUID (Racer 1)
- slot_number: 1
- final_position: 1
- result_time: "1:23.456"

- participant_id: UUID (Racer 2)
- slot_number: 2
- final_position: 2
- result_time: "1:24.123"
... (8 more)
```

### Scoring System - JSONB Flexibilität ✅
```python
# Fußball
score_data = {
    "final_score": {"home": 2, "away": 1},
    "halftime": {"home": 1, "away": 0}
}

# Rennen
score_data = {
    "ranking": [
        {"participant_id": "...", "position": 1, "time": "1:23.456"},
        {"participant_id": "...", "position": 2, "time": "1:24.123"}
    ]
}

# Basketball
score_data = {
    "quarters": [
        {"home": 25, "away": 22},
        {"home": 24, "away": 26},
        {"home": 27, "away": 23},
        {"home": 22, "away": 24}
    ],
    "final": {"home": 98, "away": 95}
}
```

---

## 🏆 Tournament Formats

### ✅ JETZT Verfügbar:
- **Knockout (Single Elimination)** - Automatic bracket generation
- **Round-Robin** - Everyone plays everyone (home & away optional)

### 🔜 Vorbereitet für Sprint 5+:
- **Group Stage + Knockout** (WM-Style)
- **Qualifying Sessions** (F1-Style)
- **Swiss System**
- **Dutch/Hollandturnier**

### Format Rules (JSONB) ✅
```python
tournament.format_rules = {
    "group_stage": {
        "num_groups": 4,
        "teams_per_group": 4,
        "advance_per_group": 2
    },
    "knockout": {
        "type": "single_elimination",
        "seeding_method": "group_winners_first"
    }
}
```

---

## 📋 Database Schema (Aktuell)

### matches Table ✅ (NEU)
```sql
- id, created_at, updated_at (BaseModel)
- tournament_id (FK to tournaments)
- round_number, match_number (INT)
- round_name, group_name, phase (VARCHAR)
- scheduled_start, scheduled_end, actual_start, actual_end (TIMESTAMP)
- venue_name, court_field_number (VARCHAR)
- status (ENUM: scheduled, in_progress, completed, cancelled, postponed, walkover)
- match_format (VARCHAR: single_game, best_of_3, timed, laps, etc.)
- duration_minutes (INT)
- is_finished (BOOLEAN)
- winner_participant_id (FK to tournament_participants)
- score_data (JSONB) - Flexible scoring
- notes, is_bye, requires_referee (various)
- referee_user_id (FK to users)
- dependent_on_match_ids (UUID[]) - Bracket dependencies
- feeds_into_match_id (FK to matches) - Next round
```

### match_participants Table ✅ (NEU)
```sql
- id, created_at, updated_at
- match_id (FK to matches, CASCADE)
- participant_id (FK to tournament_participants, CASCADE)
- slot_number (INT) - Position in match
- team_side (VARCHAR: "home", "away", NULL)
- final_position (INT) - 1st, 2nd, 3rd (for races)
- score_value (NUMERIC) - Points/Goals scored
- result_time (INTERVAL) - Finish time (races)
- is_winner, is_disqualified (BOOLEAN)
- detailed_score (JSONB) - Individual stats
- notes (TEXT)
```

### tournament_standings Table ✅ (NEU - Cached!)
```sql
- id, created_at, updated_at
- tournament_id, participant_id (FKs)
- group_name (VARCHAR) - For group stage
- matches_played, matches_won, matches_drawn, matches_lost (INT)
- points (INT) - League points (3-1-0)
- score_for, score_against, score_difference (NUMERIC)
- current_rank, previous_rank (INT)
- additional_stats (JSONB) - Sport-specific stats
- recent_form (VARCHAR) - "WWDLL"
```

### tournaments Table (UPDATED) ✅
```sql
... (existing fields from Sprint 3)
+ format_rules (JSONB) - Complex tournament structures
```

### tournament_participants Table (UPDATED) ✅
```sql
... (existing fields from Sprint 3)
+ group_assignment (VARCHAR) - "Group A", "Pool 1"
```

---

## 🚀 API Endpoints

### Match Endpoints (17 NEW) ✅
**CRUD:**
- POST /matches - Create match
- GET /matches - List matches (with filters)
- GET /matches/{id} - Get match details
- PUT /matches/{id} - Update match
- DELETE /matches/{id} - Delete match

**Scoring:**
- PUT /matches/{id}/score - Update match score
- PUT /matches/{id}/status - Update match status

**Generation:**
- POST /matches/generate/knockout - Generate knockout bracket
- POST /matches/generate/round-robin - Generate round-robin schedule

**Standings:**
- GET /matches/standings/{tournament_id} - Get standings
- POST /matches/standings/{tournament_id}/recalculate - Recalculate standings

**Filters:**
- ?tournament_id (required)
- ?round_number
- ?group_name
- ?phase
- ?status

---

## 🎯 Services Layer

### MatchService ✅
- create_match() - Manual match creation
- get_match_by_id() - Fetch match with relationships
- get_tournament_matches() - Filtered match list
- update_match() - Update match details
- update_match_score() - Score management + winner
- update_match_status() - Status transitions
- delete_match() - Match deletion

### BracketService ✅
- generate_knockout_bracket() - Single elimination
  - Automatic bye handling
  - Round naming (QF, SF, Final)
  - Match dependencies
- generate_round_robin_schedule() - Circle method
  - Fair pairing algorithm
  - Home & away optional
- _get_round_names() - Dynamic round naming
- _generate_round_robin_pairings() - Circle method implementation

### StandingsService ✅
- calculate_standings() - Recalculate from matches
- get_standings() - Fetch cached standings
- _process_two_player_match() - 3-1-0 points system
- _process_multi_player_match() - Position-based points

---

## 🧪 Testing

### Test Suites:
- `tests/sprint2_tests.sh` - 23/23 ✅
- `tests/sprint3_tests.sh` - 27/27 ✅
- `tests/sprint4_tests.sh` - 27/27 ✅ (NEU!)

**Total Test Coverage:** 77 Tests, 100% Pass Rate

### Sprint 4 Tests Cover:
1. Match CRUD (4 tests)
2. Knockout Bracket Generation (3 tests)
3. Round-Robin Generation (2 tests)
4. Match Scoring (2 tests)
5. Status Management (2 tests)
6. Tournament Standings (3 tests)
7. Filtering & Queries (2 tests)

---

## 🏗️ Architektur-Prinzipien

### SOLID Principles ✅
- **Single Responsibility:** MatchService (CRUD), BracketService (Generation), StandingsService (Calculation)
- **Open/Closed:** JSONB scoring = erweiterbar ohne Code-Änderung
- **Liskov Substitution:** Alle Tournament Types nutzen gleiche Interfaces
- **Interface Segregation:** Separate Schemas für Create/Update/Response
- **Dependency Inversion:** Services nutzen AsyncSession abstraction

### Code Quality:
```python
# ✅ Type Hints überall
async def get_match_by_id(
    db: AsyncSession, 
    match_id: UUID,
    load_relationships: bool = False
) -> Optional[Match]:
    """Get match by ID with optional relationship loading."""
    ...

# ✅ Docstrings auf allen Functions
# ✅ Pydantic Validation
# ✅ Async-First Architecture
# ✅ Service Layer Separation
# ✅ DRY - No code duplication
```

---

## 💾 Database Migrations

**Current Version:** 004 (Sprint 4)

```bash
# Migration History
001 - Initial (Users)
002 - Clubs & ClubMembers
003 - Tournaments & Participants
004 - Matches, MatchParticipants, TournamentStandings (+ Tournament updates)

# Run migrations
docker-compose exec backend alembic upgrade head

# Check current version
docker-compose exec backend alembic current

# Rollback
docker-compose exec backend alembic downgrade -1
```

---

## 📊 Statistiken (Stand Sprint 4)

### Lines of Code:
- **Sprint 1:** ~1,200 lines
- **Sprint 2:** ~1,500 lines
- **Sprint 3:** ~3,000 lines
- **Sprint 4:** ~2,960 lines
- **Total:** ~8,660 lines production code

### Database:
- **9 Tables**
- **20+ Indexes**
- **6 Enums**
- **30+ Foreign Keys**

### API:
- **67 Endpoints**
- **50+ Schemas**
- **12 Services**

---

## 🚀 Nächste Sprints (Geplant)

### Sprint 5 - Advanced Tournament Formats
- Group Stage + Knockout Generator
- Qualifying Sessions (F1-style)
- Swiss System Generator
- Match scheduling with court/time allocation

### Sprint 6 - Frontend Start
- Next.js Setup
- Tournament List & Detail Pages
- Registration Flow
- Live Standings Display

### Sprint 7 - Real-Time Features
- WebSocket Integration
- Live Score Updates
- Match Notifications
- Referee Portal

---

## 🐛 Lessons Learned (Sprint 1-4)

### Sprint 2:
- `use_enum_values=True` in Pydantic ConfigDict
- URL-Encoding für Umlaute in Tests

### Sprint 3:
- `or_` Import nicht vergessen
- Foreign Keys als String: `"[Tournament.created_by]"`
- Status Transitions müssen Business Rules folgen

### Sprint 4:
- JSONB validation ist kritisch
- N:M Junction essential für Flexibilität
- Cached standings = Performance-Gewinn
- Algorithm-based generation = Clean Code

---

## 📝 Wichtige Befehle

```bash
# Development
docker-compose up -d
docker-compose logs -f backend
docker-compose exec backend bash

# Database
docker-compose exec db psql -U postgres -d unserturnierplan
\dt  # List tables
\d matches  # Table structure

# Migrations
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic current
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Tests
tests/sprint2_tests.sh
tests/sprint3_tests.sh
tests/sprint4_tests.sh

# Code Quality
docker-compose exec backend black .
docker-compose exec backend isort .
```

---

## 🎯 Für neue Claude-Chat-Sessions

### Wichtige Dokumente:
1. **Dieser CONTEXT.md** - Projekt-Status & Historie
2. **SPRINT4_DESIGN_DECISIONS.md** - Alle Design-Entscheidungen erklärt
3. **INTEGRATION_GUIDE.md** - Step-by-step Setup
4. **SPRINT4_SUMMARY.md** - Feature-Overview

### Quick Context:
- 4 Sprints complete (User, Club, Tournament, Match)
- 67 API Endpoints, 9 DB Tables, 77 Tests (100%)
- FastAPI + PostgreSQL + Redis + Docker
- SOLID Principles, Async-First, Type-Safe
- Nächster Fokus: Advanced Tournament Formats (Sprint 5)

---

**Stand:** 15. November 2025 - Sprint 4 Complete ✅  
**Repository:** Avaron165/UnserTurnierplan  
**Branch:** main
