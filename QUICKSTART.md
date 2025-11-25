# 🚀 Sprint 4 Quick Start Guide

## Option 1: Docker Compose (Empfohlen!)

### Starten
```bash
# 1. Services starten
docker-compose up -d

# 2. Migrations ausführen
docker-compose exec backend alembic upgrade head

# 3. Testen ob es läuft
curl http://localhost:8000/health
```

### Tests ausführen
```bash
# Python Tests (empfohlen)
pip install -r tests/requirements-test.txt
pytest tests/test_sprint4_matches.py -v

# Oder Bash Tests
./tests/sprint4_tests.sh
```

### Logs anschauen
```bash
docker-compose logs -f backend
```

### Stoppen
```bash
docker-compose down
```

---

## Option 2: Lokale Entwicklung (ohne Docker)

### Setup
```bash
# 1. Lokale .env verwenden
cp backend/.env.local backend/.env

# 2. PostgreSQL & Redis starten
service postgresql start
redis-server --daemonize yes

# 3. Dependencies installieren
cd backend
pip install -r requirements.txt

# 4. Migrations ausführen
alembic upgrade head

# 5. Backend starten
uvicorn app.main:app --reload
```

### Tests ausführen
```bash
# Python Tests
pip install -r tests/requirements-test.txt
pytest tests/test_sprint4_matches.py -v
```

---

## 🧪 Was die Tests abdecken

### ✅ 27 Tests für Sprint 4:

1. **Match CRUD** (4 Tests)
   - Create manual match
   - Get match by ID
   - Update match
   - List tournament matches

2. **Knockout Bracket** (2 Tests)
   - Generate full bracket (8 teams → 7 matches)
   - Verify bracket structure (QF, SF, Final)

3. **Round-Robin** (2 Tests)
   - Generate schedule (4 teams → 6 matches)
   - Verify everyone-plays-everyone

4. **Match Scoring** (2 Tests)
   - Update score and set winner
   - Status transitions (scheduled → in_progress)

5. **Standings** (3 Tests)
   - Get standings
   - Verify winner points (3-1-0 system)
   - Recalculate standings

6. **Filtering** (2 Tests)
   - Filter by round
   - Filter by status

7. **Edge Cases** (3 Tests)
   - Empty participants
   - Nonexistent match
   - Unauthorized access

---

## 📊 API Endpoints (Sprint 4)

### Match CRUD
- `POST /api/v1/matches` - Create match
- `GET /api/v1/matches` - List matches (with filters)
- `GET /api/v1/matches/{id}` - Get match
- `PUT /api/v1/matches/{id}` - Update match
- `DELETE /api/v1/matches/{id}` - Delete match

### Match Operations
- `PUT /api/v1/matches/{id}/score` - Update score
- `PUT /api/v1/matches/{id}/status` - Change status

### Bracket Generation
- `POST /api/v1/matches/generate/knockout` - Generate knockout bracket
- `POST /api/v1/matches/generate/round-robin` - Generate round-robin schedule

### Standings
- `GET /api/v1/matches/standings/{tournament_id}` - Get standings
- `POST /api/v1/matches/standings/{tournament_id}/recalculate` - Recalculate

---

## 🎯 Nächste Schritte

1. **Tests ausführen** - Verifiziere dass alles funktioniert
2. **API testen** - Nutze Swagger UI: http://localhost:8000/api/v1/docs
3. **Sprint 5 planen** - Advanced Tournament Formats (Group Stage + Knockout)

---

## ❓ Probleme?

Siehe **DOCKER_SETUP.md** für:
- Troubleshooting
- Detaillierte Anleitung
- Best Practices
