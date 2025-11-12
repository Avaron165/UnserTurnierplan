# UnserTurnierplan - Development Started! 🚀

Die All-in-One-Plattform für perfekt organisierte Sportturniere

## ✅ Sprint 1: Projekt-Setup & Infrastruktur - ABGESCHLOSSEN!

Wir haben erfolgreich die komplette Backend-Infrastruktur mit FastAPI aufgesetzt!

## 🎯 Was ist fertig?

### ✅ Projekt-Struktur
- [x] FastAPI Backend mit Best Practices
- [x] Modular aufgebaute Architektur
- [x] Docker-Compose für lokale Entwicklung
- [x] PostgreSQL 16 & Redis 7 Integration

### ✅ Core Funktionalität
- [x] User-Management (CRUD)
- [x] JWT-basierte Authentifizierung
- [x] Access & Refresh Tokens
- [x] Passwort-Hashing (bcrypt)
- [x] Async SQLAlchemy mit PostgreSQL
- [x] Pydantic-Validierung

### ✅ API Endpoints
- [x] `POST /api/v1/auth/register` - Registrierung
- [x] `POST /api/v1/auth/login` - Login (OAuth2 & JSON)
- [x] `POST /api/v1/auth/refresh` - Token erneuern
- [x] `GET /api/v1/auth/me` - Aktueller User
- [x] `GET /api/v1/users/me` - Eigenes Profil
- [x] `PUT /api/v1/users/me` - Profil bearbeiten
- [x] `DELETE /api/v1/users/me` - Account löschen

### ✅ Infrastruktur
- [x] Docker & Docker-Compose Setup
- [x] Alembic für Datenbank-Migrationen
- [x] Pytest Setup für Testing
- [x] Auto-generierte API-Dokumentation (Swagger)
- [x] CORS-Konfiguration
- [x] Health-Check-Endpoint

## 🚀 Quick Start

```bash
# 1. Repository klonen / Dateien kopieren
cd UnserTurnierplan

# 2. Docker Container starten
docker-compose up -d

# 3. Datenbank-Migrationen ausführen
docker-compose exec backend alembic upgrade head

# 4. API testen
curl http://localhost:8000/health

# 5. API-Dokumentation öffnen
# Browser: http://localhost:8000/api/v1/docs
```

## 📁 Projekt-Struktur

```
UnserTurnierplan/
├── backend/                      # FastAPI Backend ✅
│   ├── app/
│   │   ├── api/                 # API Endpoints
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── users.py         # User Management
│   │   │   └── dependencies.py  # Auth Dependencies
│   │   ├── core/                # Core Module
│   │   │   ├── config.py        # Konfiguration
│   │   │   └── security.py      # JWT & Hashing
│   │   ├── db/                  # Database
│   │   │   └── session.py       # SQLAlchemy Setup
│   │   ├── models/              # DB Models
│   │   │   ├── base.py          # Base Model
│   │   │   └── user.py          # User Model
│   │   ├── schemas/             # Pydantic Schemas
│   │   │   └── user.py          # User Schemas
│   │   ├── services/            # Business Logic
│   │   │   └── user_service.py  # User Service
│   │   └── main.py              # FastAPI App
│   ├── alembic/                 # DB Migrations
│   ├── .env                     # Environment Variables
│   ├── Dockerfile               # Docker Image
│   └── requirements.txt         # Python Dependencies
├── frontend/                     # React Frontend (TODO)
├── docker-compose.yml            # Docker Services ✅
├── .gitignore                    # Git Ignore ✅
└── README.md                     # This file
```

## 🔧 Technologie-Stack

### Backend
- **FastAPI** - Modernes Python Web Framework
- **SQLAlchemy** - Async ORM für PostgreSQL
- **Alembic** - Database Migrations
- **Pydantic** - Data Validation
- **python-jose** - JWT Tokens
- **passlib** - Password Hashing

### Database
- **PostgreSQL 16** - Primary Database
- **Redis 7** - Caching & Sessions

### DevOps
- **Docker & Docker-Compose** - Containerization
- **pytest** - Testing Framework
- **Uvicorn** - ASGI Server

## 📊 API-Dokumentation

Die API-Dokumentation wird automatisch von FastAPI generiert:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Schema**: http://localhost:8000/api/v1/openapi.json

## 🧪 API Testen

### 1. User registrieren
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "max@example.com",
    "password": "Secure123!",
    "first_name": "Max",
    "last_name": "Mustermann",
    "phone": "+49 123 456789"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "max@example.com",
    "password": "Secure123!"
  }'
```

### 3. Profil abrufen (mit Token)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🎯 Nächste Schritte (Sprint 2)

### Club Management
- [ ] Club Model erstellen
- [ ] Club-Service implementieren
- [ ] Club API Endpoints
- [ ] Club-Mitglieder-Verwaltung
- [ ] Rollen & Permissions System

### Tests
- [ ] User-Service Tests
- [ ] Auth-Endpoint Tests
- [ ] Integration Tests
- [ ] Test Coverage > 80%

## 📚 Dokumentation

- [Backend README](./backend/README.md) - Detaillierte Backend-Dokumentation
- [Project Overview](./PROJECT_OVERVIEW.md) - Vollständige Projektübersicht
- [Technical Architecture](./TECHNICAL_ARCHITECTURE.md) - Technische Architektur
- [Development Roadmap](./DEVELOPMENT_ROADMAP.md) - Entwicklungs-Roadmap
- [UI/UX Design](./UI_UX_DESIGN.md) - Design-System
- [Marketing Strategy](./MARKETING_STRATEGY.md) - Go-to-Market

## 🐛 Troubleshooting

### Port bereits belegt
```bash
docker-compose down
# Oder anderen Port in docker-compose.yml verwenden
```

### Database Connection Error
```bash
docker-compose logs db
docker-compose restart db
```

### Backend neu bauen
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

## 🤝 Contributing

1. Branch erstellen: `git checkout -b feature/amazing-feature`
2. Änderungen committen: `git commit -m 'Add amazing feature'`
3. Push zum Branch: `git push origin feature/amazing-feature`
4. Pull Request erstellen

## 📝 Code-Qualität

```bash
# In backend/ Verzeichnis
cd backend

# Code formatieren
black .

# Imports sortieren
isort .

# Linting
flake8

# Tests ausführen
pytest
```

## 🎉 Erfolge

- ✅ **Sprint 1 abgeschlossen!** (Projekt-Setup & User-Management)
- ✅ **Vollständig funktionierende API** mit Authentifizierung
- ✅ **Docker-Entwicklungsumgebung** ready
- ✅ **Auto-generierte API-Dokumentation**
- ✅ **Production-ready Code-Struktur**

---

**Status**: 🟢 Aktiv in Entwicklung  
**Version**: 1.0.0  
**Letzte Aktualisierung**: November 2025
