# Docker Compose Setup für UnserTurnierplan

## Warum wurde Docker Compose temporär nicht genutzt?

In der Claude-Code-Umgebung war `docker` nicht verfügbar, deshalb musste ich temporär:
- PostgreSQL direkt starten (`service postgresql start`)
- Redis direkt starten (`redis-server`)
- Backend direkt mit Python starten (`python3 -m uvicorn`)

**Für dich lokal sollte Docker Compose aber perfekt funktionieren!**

---

## ✅ Empfohlene Nutzung: Docker Compose

### Alle Services starten
```bash
docker-compose up -d
```

Dies startet:
- ✅ **PostgreSQL 16** (Port 5432)
- ✅ **Redis 7** (Port 6379)
- ✅ **FastAPI Backend** (Port 8000)

### Datenbank-Migrationen ausführen
```bash
docker-compose exec backend alembic upgrade head
```

### Backend-Logs anschauen
```bash
docker-compose logs -f backend
```

### Services neustarten
```bash
docker-compose restart backend
```

### Services stoppen
```bash
docker-compose down
```

### Services komplett neu bauen
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🧪 Tests ausführen (mit Docker Compose)

### Option 1: Python/Pytest Tests (Empfohlen!)
```bash
# Backend muss laufen
docker-compose up -d

# Tests installieren und ausführen
pip install -r tests/requirements-test.txt
pytest tests/test_sprint4_matches.py -v
```

### Option 2: Bash Tests
```bash
# Backend muss laufen
docker-compose up -d

# Tests ausführen
./tests/sprint4_tests.sh
```

---

## 🔧 Troubleshooting

### Problem: "Port already in use"
```bash
# Alte Container stoppen
docker-compose down

# Oder Port checken
sudo lsof -i :8000
sudo lsof -i :5432
```

### Problem: "Database connection failed"
```bash
# Datenbank-Logs checken
docker-compose logs db

# Container neustarten
docker-compose restart db
docker-compose restart backend
```

### Problem: Backend startet nicht
```bash
# Fehler anzeigen
docker-compose logs backend

# Migrations checken
docker-compose exec backend alembic current

# Migrations ausführen
docker-compose exec backend alembic upgrade head
```

### Backend neu bauen (nach Code-Änderungen)
```bash
docker-compose down
docker-compose build backend
docker-compose up -d
```

---

## 📊 Datenbank zugreifen

### Via psql (Docker)
```bash
docker-compose exec db psql -U postgres -d unserturnierplan
```

### Via pgAdmin (Optional)
```bash
# pgAdmin starten (mit profile)
docker-compose --profile tools up -d pgadmin

# Browser öffnen: http://localhost:5050
# Email: admin@unserturnierplan.de
# Passwort: admin
```

---

## 🎯 Best Practice Workflow

### Entwicklung starten
```bash
# 1. Services starten
docker-compose up -d

# 2. Migrations ausführen (falls nötig)
docker-compose exec backend alembic upgrade head

# 3. Backend-Logs verfolgen
docker-compose logs -f backend
```

### Nach Code-Änderungen
```bash
# Backend hat auto-reload aktiviert (--reload)
# Änderungen werden automatisch erkannt!

# Nur bei Dependency-Änderungen neu bauen:
docker-compose restart backend
```

### Tests ausführen
```bash
# Pytest (empfohlen)
pytest tests/test_sprint4_matches.py -v

# Oder Bash
./tests/sprint4_tests.sh
```

### Entwicklung beenden
```bash
# Services stoppen (Daten bleiben erhalten)
docker-compose stop

# Oder komplett entfernen
docker-compose down
```

---

## 🔐 Environment-Variablen

Die `.env` Datei im backend/ Ordner steuert die Konfiguration:

```bash
# Wichtig für Docker:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/unserturnierplan
REDIS_URL=redis://redis:6379/0

# Für lokale Entwicklung ohne Docker:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/unserturnierplan
REDIS_URL=redis://localhost:6379/0
```

**Aktuell ist `localhost` in der `.env` konfiguriert, weil ich ohne Docker getestet habe.**

### Für Docker Compose zurück ändern:
```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/unserturnierplan
REDIS_URL=redis://redis:6379/0
```

---

## ✨ Vorteile von Docker Compose

- ✅ **Isoliert**: Keine Konflikte mit System-Services
- ✅ **Reproduzierbar**: Gleiche Umgebung überall
- ✅ **Einfach**: Ein Befehl startet alles
- ✅ **Clean**: `docker-compose down` räumt auf
- ✅ **Production-ready**: Ähnlich zu Deployment-Setup
