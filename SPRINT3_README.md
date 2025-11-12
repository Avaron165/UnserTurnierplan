# UnserTurnierplan - Sprint 3: Tournament Management ✅

## 🎯 Sprint 3 Status: COMPLETE

All tournament management features implemented including department-based permissions!

### ✅ What's Implemented

#### Models & Database
- ✅ Tournament Model (with department support)
- ✅ TournamentParticipant Model
- ✅ 6 Enums (TournamentType, TournamentStatus, SportType, etc.)
- ✅ Migration 003 with all tables and indexes

#### Business Logic (Services)
- ✅ TournamentService
  - CRUD operations
  - Lifecycle management (status transitions)
  - Department-based permissions
  - Statistics & filtering
- ✅ TournamentParticipantService
  - Registration management
  - Status & payment updates
  - Participant count tracking

#### API Endpoints (17 Endpoints)
- ✅ Tournament CRUD (7 endpoints)
- ✅ Tournament Queries (3 endpoints)
- ✅ Participant Management (7 endpoints)

#### Permissions System
- ✅ **Owner/Admin:** Can manage all tournaments
- ✅ **Manager:** Can manage tournaments in their department only
- ✅ **Department-aware** tournament creation

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Setup

1. **Clone and navigate:**
```bash
cd UnserTurnierplan
```

2. **Copy environment file:**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set SECRET_KEY
```

3. **Start services:**
```bash
docker-compose up -d
```

4. **Run migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Access API:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 API Endpoints Overview

### Tournament CRUD
```
POST   /api/v1/tournaments              Create tournament
GET    /api/v1/tournaments              List tournaments (with filters)
GET    /api/v1/tournaments/{id}         Get tournament details
GET    /api/v1/tournaments/slug/{slug}  Get tournament by slug
PUT    /api/v1/tournaments/{id}         Update tournament
DELETE /api/v1/tournaments/{id}         Delete tournament
PUT    /api/v1/tournaments/{id}/status  Update tournament status
```

### Tournament Queries
```
GET /api/v1/tournaments/my/created       My created tournaments
GET /api/v1/tournaments/my/participating My participations
GET /api/v1/tournaments/{id}/statistics  Tournament statistics
```

### Participant Management
```
POST   /api/v1/tournaments/{id}/register                Register for tournament
GET    /api/v1/tournaments/{id}/participants            List participants
GET    /api/v1/tournaments/{id}/participants/{pid}      Get participant
PUT    /api/v1/tournaments/{id}/participants/{pid}      Update participant
DELETE /api/v1/tournaments/{id}/participants/{pid}      Remove participant
PUT    /api/v1/tournaments/{id}/participants/{pid}/status  Update status
PUT    /api/v1/tournaments/{id}/participants/{pid}/payment Update payment
```

---

## 🏢 Department-Based Permissions

### Club Structure
```
TSV München (Club)
  ├── Fußball (department)
  │   └── Turniere von Fußball-Manager
  ├── Basketball (department)
  │   └── Turniere von Basketball-Manager
  └── Handball (department)
```

### Permission Rules
- **OWNER/ADMIN:** Can create/manage tournaments for ALL departments
- **MANAGER:** Can create/manage tournaments ONLY for their department
- **MEMBER/VOLUNTEER:** Cannot create tournaments

### Example
```json
{
  "name": "U17 Fußball Cup",
  "club_id": "...",
  "department": "Fußball",  // Manager must have department="Fußball"
  "sport_type": "football",
  ...
}
```

---

## 🔄 Tournament Lifecycle

```
DRAFT → PUBLISHED → REGISTRATION_OPEN → ACTIVE → COMPLETED
   ↓                                        ↓
CANCELLED ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### Status Descriptions
- **DRAFT:** Tournament being created, not visible publicly
- **PUBLISHED:** Visible but registration not yet open
- **REGISTRATION_OPEN:** Accepting participant registrations
- **ACTIVE:** Tournament in progress
- **COMPLETED:** Tournament finished
- **CANCELLED:** Tournament cancelled

---

## 🗄️ Database Schema

### tournaments
- Basic info (name, slug, description, banner)
- **department** (NEW!) - Enables department-based permissions
- Tournament classification (sport_type, tournament_type, status)
- Dates (start, end, registration window)
- Location details
- Participant settings (min/max, current count)
- Rules, prizes, entry fee
- Visibility & contact info

### tournament_participants
- Tournament & participant references (club OR user)
- Participant info (name, contact)
- Registration details
- Status (pending, confirmed, cancelled, waitlist)
- Payment management
- Seeding & notes

---

## 🧪 Testing

### Manual Testing with API Docs
1. Go to http://localhost:8000/docs
2. Try creating a tournament
3. Register participants
4. Update statuses

### Database Access
```bash
docker-compose exec db psql -U postgres -d unserturnierplan

# List tables
\dt

# View tournaments
SELECT id, name, department, status FROM tournaments;

# View participants
SELECT id, participant_name, status FROM tournament_participants;
```

---

## 📊 Database Migrations

### View current version
```bash
docker-compose exec backend alembic current
```

### Upgrade to latest
```bash
docker-compose exec backend alembic upgrade head
```

### Downgrade one version
```bash
docker-compose exec backend alembic downgrade -1
```

### View migration history
```bash
docker-compose exec backend alembic history
```

---

## 🔧 Development

### View logs
```bash
docker-compose logs -f backend
```

### Restart backend
```bash
docker-compose restart backend
```

### Run Python shell
```bash
docker-compose exec backend python
>>> from app.models.tournament import Tournament
>>> from app.db.session import AsyncSessionLocal
```

### Format code (when added to requirements)
```bash
docker-compose exec backend black .
docker-compose exec backend isort .
```

---

## 📈 What's Next?

### Sprint 4 - Match Management
- Match Model
- Match scheduling
- Score entry
- Live results

### Sprint 5 - Bracket Generation
- Automatic bracket generation
- Match tree/graph
- Seeding logic

### Sprint 6 - Rundown System
- Event timeline
- Activity scheduling
- Resource allocation

---

## 🐛 Known Issues & Solutions

### Issue: Migration "already exists"
```bash
docker-compose exec backend alembic downgrade 002
docker-compose exec backend alembic upgrade head
```

### Issue: Database connection refused
```bash
docker-compose down -v
docker-compose up -d
# Wait 30 seconds for DB to initialize
docker-compose exec backend alembic upgrade head
```

---

## 📚 Documentation

- [CONTEXT.md](../CONTEXT.md) - Full project context
- [API Docs](http://localhost:8000/docs) - Interactive API documentation
- [ReDoc](http://localhost:8000/redoc) - Alternative API docs

---

## ✨ Key Features

### Tournament Types
- Knockout/Elimination
- Round Robin
- Group Stage
- Swiss System
- Custom

### Sport Types
- Football ⚽
- Basketball 🏀
- Volleyball 🏐
- Handball 🤾
- Hockey 🏑
- Tennis 🎾
- Table Tennis 🏓
- Badminton 🏸
- eSports 🎮
- Other

### Participant Types
- Team-based tournaments
- Individual tournaments

---

**Sprint 3 completed on:** November 12, 2025
**Status:** ✅ Ready for Phase 5 testing
