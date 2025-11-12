# UnserTurnierplan Backend (FastAPI)

Backend API für UnserTurnierplan - Tournament Management Platform

## 🚀 Quick Start

### Voraussetzungen
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 (wenn lokal ohne Docker)
- Redis 7 (wenn lokal ohne Docker)

### Installation mit Docker (Empfohlen)

```bash
# 1. In das Projekt-Verzeichnis wechseln
cd UnserTurnierplan

# 2. Docker Container starten
docker-compose up -d

# 3. Datenbank-Migrationen ausführen
docker-compose exec backend alembic upgrade head

# 4. API ist verfügbar unter: http://localhost:8000
# 5. API-Dokumentation: http://localhost:8000/api/v1/docs
```

### Installation lokal (ohne Docker)

```bash
# 1. Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. .env Datei erstellen
cp .env.example .env
# Dann .env anpassen (DATABASE_URL, SECRET_KEY, etc.)

# 4. PostgreSQL und Redis starten (lokal oder via Docker)
# Siehe docker-compose.yml für Konfiguration

# 5. Datenbank-Migrationen ausführen
alembic upgrade head

# 6. Server starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Projekt-Struktur

```
backend/
├── alembic/                  # Datenbank-Migrationen
│   ├── versions/             # Migration-Dateien
│   └── env.py               # Alembic-Konfiguration
├── app/
│   ├── api/                 # API Endpoints
│   │   ├── auth.py          # Authentication Endpoints
│   │   ├── users.py         # User Endpoints
│   │   └── dependencies.py  # FastAPI Dependencies
│   ├── core/                # Core Module
│   │   ├── config.py        # App Konfiguration
│   │   └── security.py      # Security (JWT, Hashing)
│   ├── db/                  # Database
│   │   └── session.py       # SQLAlchemy Session
│   ├── models/              # SQLAlchemy Models
│   │   ├── base.py          # Base Model
│   │   └── user.py          # User Model
│   ├── schemas/             # Pydantic Schemas
│   │   └── user.py          # User Schemas
│   ├── services/            # Business Logic
│   │   └── user_service.py  # User Service
│   └── main.py              # FastAPI App
├── .env                     # Umgebungsvariablen (lokal)
├── .env.example             # Beispiel für .env
├── alembic.ini              # Alembic Konfiguration
├── Dockerfile               # Docker Image
├── pytest.ini               # Pytest Konfiguration
└── requirements.txt         # Python Dependencies
```

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Neuen User registrieren
- `POST /api/v1/auth/login` - Login (OAuth2)
- `POST /api/v1/auth/login/json` - Login (JSON)
- `POST /api/v1/auth/refresh` - Token erneuern
- `GET /api/v1/auth/me` - Aktueller User
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Eigenes Profil
- `PUT /api/v1/users/me` - Profil bearbeiten
- `DELETE /api/v1/users/me` - Account löschen
- `GET /api/v1/users/{user_id}` - User by ID
- `PUT /api/v1/users/{user_id}` - User bearbeiten (Admin)
- `DELETE /api/v1/users/{user_id}` - User löschen (Admin)

## 🧪 Testing

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=app --cov-report=html

# Einzelne Test-Datei
pytest app/tests/test_auth.py

# Verbose Output
pytest -v
```

## 📊 Datenbank-Migrationen

```bash
# Neue Migration erstellen
alembic revision --autogenerate -m "Description"

# Alle Migrationen anwenden
alembic upgrade head

# Eine Migration zurück
alembic downgrade -1

# Zu spezifischer Revision
alembic upgrade <revision_id>

# History anzeigen
alembic history

# Aktueller Status
alembic current
```

## 🔧 Entwicklung

### Code-Qualität

```bash
# Code formatieren
black .

# Imports sortieren
isort .

# Linting
flake8

# Type checking
mypy .
```

### Hot Reload
Der Development-Server startet automatisch mit `--reload`, sodass Änderungen sofort verfügbar sind.

### Debugging
1. In VS Code: F5 drücken (Launch-Konfiguration vorhanden)
2. Mit pdb: `import pdb; pdb.set_trace()` im Code einfügen

## 🔐 Sicherheit

### SECRET_KEY generieren
```bash
openssl rand -hex 32
```
Dann in `.env` eintragen!

### Password Policy
- Mindestens 8 Zeichen
- Mindestens 1 Ziffer
- Mindestens 1 Großbuchstabe
- Mindestens 1 Kleinbuchstabe

### JWT Tokens
- Access Token: 30 Minuten gültig
- Refresh Token: 7 Tage gültig

## 📝 API-Dokumentation

### Swagger UI
http://localhost:8000/api/v1/docs

### ReDoc
http://localhost:8000/api/v1/redoc

### OpenAPI Schema
http://localhost:8000/api/v1/openapi.json

## 🐛 Troubleshooting

### Port bereits belegt
```bash
# Port 8000 freigeben (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Oder anderen Port verwenden
uvicorn app.main:app --port 8001
```

### Database Connection Error
```bash
# Prüfen ob PostgreSQL läuft
docker-compose ps

# Logs anzeigen
docker-compose logs db

# Database neu erstellen
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

### Import Errors
```bash
# PYTHONPATH setzen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📚 Weitere Ressourcen

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)

## 🎯 Nächste Schritte

- [ ] Tests schreiben
- [ ] Club-Management implementieren
- [ ] Tournament-Service aufbauen
- [ ] Frontend anbinden
- [ ] CI/CD Pipeline einrichten
