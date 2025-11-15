# Sprint 4 - Match Scheduling & Brackets - INTEGRATION GUIDE

## 📦 Was wurde erstellt?

Sprint 4 fügt ein komplettes Match-System mit Bracket-Generierung und Standings hinzu.

### Neue Files:
```
backend/app/models/
├── match.py                          # Match Model (2-N participants)
├── match_participant.py              # Match-Participant Junction
└── tournament_standings.py           # Cached Standings

backend/app/schemas/
└── match.py                          # Match Schemas (umfangreich!)

backend/app/services/
├── match_service.py                  # Match CRUD + Scoring
├── bracket_service.py                # Knockout + Round-Robin Generation
└── standings_service.py              # Standings Calculation

backend/app/api/
└── matches.py                        # Match API Endpoints

backend/alembic/versions/
└── 004_create_matches.py             # Database Migration

tests/
└── sprint4_tests.sh                  # Comprehensive Test Suite
```

### Modified Files (manuelle Änderungen erforderlich):
```
backend/app/models/tournament.py      # + matches relationship + format_rules
backend/app/models/tournament_participant.py  # + group_assignment
backend/app/models/__init__.py        # + Import neue Models
backend/app/schemas/__init__.py       # + Import Match Schemas
backend/app/api/__init__.py           # + Register matches router
```

---

## 🔧 INTEGRATION STEPS

### Step 1: Copy neue Files

```bash
# Von deinem Downloads-Ordner (wo du die Files gespeichert hast)
cd /path/to/sprint4

# Copy Models
cp backend/app/models/*.py /path/to/UnserTurnierplan/backend/app/models/

# Copy Schemas
cp backend/app/schemas/match.py /path/to/UnserTurnierplan/backend/app/schemas/

# Copy Services
cp backend/app/services/*.py /path/to/UnserTurnierplan/backend/app/services/

# Copy API
cp backend/app/api/matches.py /path/to/UnserTurnierplan/backend/app/api/

# Copy Migration
cp backend/alembic/versions/004_create_matches.py /path/to/UnserTurnierplan/backend/alembic/versions/

# Copy Tests
cp tests/sprint4_tests.sh /path/to/UnserTurnierplan/tests/
chmod +x /path/to/UnserTurnierplan/tests/sprint4_tests.sh
```

---

### Step 2: Update Tournament Model

**File:** `backend/app/models/tournament.py`

**ADD** nach den bestehenden Imports (wenn nicht schon vorhanden):
```python
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
```

**ADD** nach den bestehenden Feldern (vor relationships, ca. Zeile 190):
```python
    # Tournament Format Rules (JSONB for complex structures)
    format_rules = Column(JSONB, nullable=True)
```

**ADD** in der relationships section (ca. Zeile 204):
```python
    matches = relationship(
        "Match",
        back_populates="tournament",
        cascade="all, delete-orphan"
    )
```

---

### Step 3: Update TournamentParticipant Model

**File:** `backend/app/models/tournament_participant.py`

**ADD** nach den bestehenden participant fields (ca. Zeile 45):
```python
    # Group Assignment (for multi-group tournaments)
    group_assignment = Column(String(50), nullable=True, index=True)
```

---

### Step 4: Update Models __init__.py

**File:** `backend/app/models/__init__.py`

**ADD** zu den Imports:
```python
from app.models.match import Match, MatchStatus, MatchFormat
from app.models.match_participant import MatchParticipant
from app.models.tournament_standings import TournamentStandings

__all__ = [
    # ... existing exports ...
    "Match", "MatchStatus", "MatchFormat",
    "MatchParticipant",
    "TournamentStandings",
]
```

---

### Step 5: Update Schemas __init__.py

**File:** `backend/app/schemas/__init__.py`

**ADD** zu den Imports:
```python
from app.schemas.match import (
    MatchCreate, MatchUpdate, MatchResponse, MatchDetail,
    MatchListItem, MatchScoreUpdate, MatchStatusUpdate,
    MatchParticipantCreate, MatchParticipantUpdate,
    MatchParticipantResponse, MatchParticipantDetail,
    BracketGenerationRequest, RoundRobinGenerationRequest,
    StandingsResponse, StandingsDetail
)

__all__ = [
    # ... existing exports ...
    "MatchCreate", "MatchUpdate", "MatchResponse", "MatchDetail",
    "MatchListItem", "MatchScoreUpdate", "MatchStatusUpdate",
    "MatchParticipantCreate", "MatchParticipantUpdate",
    "MatchParticipantResponse", "MatchParticipantDetail",
    "BracketGenerationRequest", "RoundRobinGenerationRequest",
    "StandingsResponse", "StandingsDetail",
]
```

---

### Step 6: Register Matches Router

**File:** `backend/app/api/__init__.py`

**ADD** Import:
```python
from app.api.matches import router as matches_router
```

**ADD** Router Registration (in der `create_api_router()` Funktion):
```python
api_router.include_router(matches_router)
```

---

### Step 7: Run Migration

```bash
cd UnserTurnierplan

# Start containers
docker-compose up -d

# Wait for DB
sleep 10

# Run migration
docker-compose exec backend alembic upgrade head

# Verify migration
docker-compose exec backend alembic current
# Should show: 004 (head)
```

---

### Step 8: Rebuild Backend

```bash
# Rebuild to ensure all imports work
docker-compose build backend
docker-compose up -d backend

# Check logs
docker-compose logs -f backend
```

---

### Step 9: Run Tests

```bash
# Make test script executable
chmod +x tests/sprint4_tests.sh

# Run tests
./tests/sprint4_tests.sh
```

---

## ✅ Verification Checklist

- [ ] All neue Files kopiert
- [ ] `tournament.py` updated (`format_rules` + `matches` relationship)
- [ ] `tournament_participant.py` updated (`group_assignment`)
- [ ] `models/__init__.py` updated
- [ ] `schemas/__init__.py` updated
- [ ] `api/__init__.py` updated (router registration)
- [ ] Migration 004 erfolgreich (verify with `alembic current`)
- [ ] Backend startet ohne Fehler
- [ ] API Docs zeigen neue `/matches` Endpoints: http://localhost:8000/docs
- [ ] Tests laufen erfolgreich (27/27 tests passed)

---

## 🎯 Quick Test

Nach der Integration teste schnell ob alles funktioniert:

```bash
# 1. Check API Docs
curl http://localhost:8000/docs
# Should show /api/v1/matches endpoints

# 2. Quick health check
curl http://localhost:8000/health

# 3. Run full test suite
./tests/sprint4_tests.sh
```

---

## 🚀 Was kannst Du jetzt machen?

### Knockout Tournament
1. Tournament erstellen (tournament_type: "knockout")
2. Participants registrieren & bestätigen
3. `POST /api/v1/matches/generate/knockout` → Bracket wird generiert!
4. Matches spielen und Scores eintragen
5. Winner progression automatisch

### Round-Robin Tournament
1. Tournament erstellen (tournament_type: "round_robin")
2. Participants registrieren
3. `POST /api/v1/matches/generate/round-robin` → Schedule generiert!
4. Scores eintragen
5. `GET /api/v1/matches/standings/{tournament_id}` → Live Tabelle!

### Manual Matches
1. `POST /api/v1/matches` → Custom Match erstellen
2. Für Rennen: 3+ participants möglich!
3. Flexible Scoring mit JSONB

---

## 📊 Database Schema

### Neue Tables:
- `matches` - Match information
- `match_participants` - N:M junction (2-N participants pro Match!)
- `tournament_standings` - Cached standings

### Updated Tables:
- `tournaments` + `format_rules` (JSONB)
- `tournament_participants` + `group_assignment` (String)

---

## 🐛 Troubleshooting

### Migration fails with "relation already exists"
```bash
# Reset migration
docker-compose exec backend alembic downgrade 003
docker-compose exec backend alembic upgrade head
```

### Import errors
```bash
# Verify __init__.py files are updated
# Rebuild container
docker-compose build backend
docker-compose up -d
```

### Tests fail
```bash
# Check backend logs
docker-compose logs backend

# Verify database
docker-compose exec db psql -U postgres -d unserturnierplan
\dt  # Should show matches, match_participants, tournament_standings
```

---

## 📝 Git Workflow

```bash
cd UnserTurnierplan

# Create feature branch
git checkout -b feature/sprint-4-matches

# Add all new files
git add .

# Commit
git commit -m "Sprint 4: Match Scheduling & Brackets

- Add Match, MatchParticipant, TournamentStandings models
- Add Match CRUD service
- Add Knockout & Round-Robin bracket generation
- Add Standings calculation service
- Add Match API endpoints
- Add database migration 004
- Add comprehensive test suite (27 tests)
- Update Tournament model with format_rules
- Update TournamentParticipant with group_assignment

Features:
- 2-N participants per match (for races!)
- Automatic bracket generation
- Flexible JSONB scoring
- Cached standings
- Match progression (knockout)
"

# Push to GitHub
git push origin feature/sprint-4-matches

# Merge to main (oder create PR)
git checkout main
git merge feature/sprint-4-matches
git push origin main
```

---

## 🎉 Next Steps (Sprint 5+)

- Group Stage → Knockout Generator
- Qualifying Sessions (F1-style)
- Swiss System
- Court/Time Scheduling
- Match Notifications
- Live Score Updates (WebSockets)

---

**Bei Fragen oder Problemen: Melde dich!** 🚀
