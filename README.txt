# 📦 UnserTurnierplan - Sprint 2 Package

## 🎉 Was ist drin?

Diese ZIP-Datei enthält **alle Dateien für Sprint 2 - Club Management**.

**Inhalt:**
- ✅ Komplettes Backend (alle Dateien)
- ✅ 8 neue Dateien (Models, Schemas, Services, API, Migration)
- ✅ 4 aktualisierte Dateien (User Model, Dependencies, main.py, alembic env)
- ✅ 4 Dokumentations-Dateien
- ✅ Alle Konfigurationsdateien

**Dateigröße:** ~45 KB (komprimiert)

---

## 🚀 Quick Start

### 1. Entpacken

```bash
# ZIP entpacken
unzip UnserTurnierplan_Sprint2.zip

# Verzeichnisstruktur:
# UnserTurnierplan_Sprint2/
# ├── backend/               (komplettes Backend)
# ├── CONTEXT.md             (Projektkontext)
# ├── SPRINT_2_INSTALLATION.md (ANLEITUNG!)
# ├── SPRINT_2_FILES.md      (Dateiliste)
# └── SPRINT_2_PROGRESS.md   (Status)
```

### 2. Installation

**⚠️ WICHTIG: Lesen Sie zuerst SPRINT_2_INSTALLATION.md!**

```bash
cd ~/UnserTurnierplan

# Option A: Einzelne Dateien kopieren (empfohlen)
# Siehe: SPRINT_2_INSTALLATION.md Schritt 1-10

# Option B: Komplettes Backend ersetzen (schnell)
# ACHTUNG: Backup erstellen!
cp -r backend backend.backup
cp -r UnserTurnierplan_Sprint2/backend/* backend/
cp backend.backup/.env backend/.env  # WICHTIG!

# CONTEXT.md ins Root
cp UnserTurnierplan_Sprint2/CONTEXT.md .
```

### 3. Backend starten

```bash
# Backend neu bauen
docker-compose build backend
docker-compose up -d

# Migration ausführen
docker-compose exec backend alembic upgrade head

# Testen
curl http://localhost:8000/health
firefox http://localhost:8000/api/v1/docs
```

---

## 📚 Dokumentation

**START HIER:** 
- **SPRINT_2_INSTALLATION.md** - Vollständige Anleitung

**Weitere Docs:**
- **CONTEXT.md** - Für neue Chat-Sessions mit Claude
- **SPRINT_2_FILES.md** - Dateiliste & Änderungen
- **SPRINT_2_PROGRESS.md** - Status & Code-Statistiken

---

## ✨ Neue Features in Sprint 2

### 14 neue API Endpoints:

**Club Management:**
- `POST   /api/v1/clubs` - Club erstellen
- `GET    /api/v1/clubs` - Clubs auflisten
- `GET    /api/v1/clubs/{club_id}` - Club by ID
- `PUT    /api/v1/clubs/{club_id}` - Club bearbeiten
- `DELETE /api/v1/clubs/{club_id}` - Club löschen

**Member Management:**
- `GET    /api/v1/clubs/{club_id}/members` - Mitglieder
- `POST   /api/v1/clubs/{club_id}/members` - Mitglied hinzufügen
- `PUT    /api/v1/clubs/{club_id}/members/{user_id}` - Rolle ändern
- `DELETE /api/v1/clubs/{club_id}/members/{user_id}` - Entfernen
- `GET    /api/v1/clubs/me/memberships` - Meine Clubs

**+ 4 weitere Endpoints (Verification, Count, Slug)**

### Permission-System:
- 5 Rollen: OWNER, ADMIN, MANAGER, MEMBER, VOLUNTEER
- Rollen-Hierarchie mit Permission-Checkern
- Automatische Rechteverwaltung

---

## 🧪 Schnell-Test

```bash
# 1. User erstellen & einloggen
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!","first_name":"Max","last_name":"Muster"}'

# Login & Token kopieren
curl -X POST http://localhost:8000/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}'

# 2. Club erstellen
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/clubs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FC Test",
    "description": "Test Verein",
    "city": "München"
  }'

# 3. Clubs auflisten
curl http://localhost:8000/api/v1/clubs

# 4. API-Docs öffnen
firefox http://localhost:8000/api/v1/docs
```

---

## 📊 Statistiken

**Code:**
- Neue Dateien: 8
- Geänderte Dateien: 4
- Zeilen Code: ~3.500
- API Endpoints: 27 total (13 User + 14 Club)

**Features:**
- Models: 3 (User, Club, ClubMember)
- Schemas: 21
- Services: 3 (User, Club, ClubMember)
- Database Tables: 4

---

## ⚠️ Wichtige Hinweise

1. **Backup erstellen** vor der Installation!
   ```bash
   cp -r backend backend.backup
   ```

2. **.env Datei behalten!**
   - Die .env aus der ZIP ist nur ein Beispiel
   - Behalten Sie Ihre eigene .env mit SECRET_KEY

3. **Backend neu bauen** nach Kopieren!
   ```bash
   docker-compose build backend
   ```

4. **Migration ausführen!**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

---

## 🐛 Troubleshooting

### Backend startet nicht
```bash
docker-compose logs backend | tail -50
docker-compose build --no-cache backend
```

### Migration schlägt fehl
```bash
docker-compose exec backend alembic current
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Kompletter Neustart
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

**Vollständiges Troubleshooting:** Siehe SPRINT_2_INSTALLATION.md

---

## 📞 Support

**Dokumentation:**
- SPRINT_2_INSTALLATION.md - Vollständige Anleitung
- CONTEXT.md - Projektkontext für neue Sessions

**Bei Problemen:**
1. Logs prüfen: `docker-compose logs backend`
2. Siehe Troubleshooting in SPRINT_2_INSTALLATION.md
3. Neue Chat-Session mit CONTEXT.md starten

---

## ✅ Erfolgskriterien

Nach Installation sollte funktionieren:
- [x] Backend startet ohne Fehler
- [x] API-Docs zeigen 27 Endpoints
- [x] Clubs können erstellt werden
- [x] Mitglieder können hinzugefügt werden
- [x] Permissions funktionieren (403 bei unerlaubten Aktionen)
- [x] 4 Datenbank-Tabellen existieren

---

## 🎯 Nächste Schritte

Nach erfolgreicher Installation von Sprint 2:

1. **Testen** - Alle Endpoints durchprobieren
2. **Git Commit** - Sprint 2 committen & pushen
3. **Sprint 3** - Tournament Management (nächster Sprint)

---

**Version:** Sprint 2 Complete  
**Datum:** November 2025  
**Status:** ✅ Production Ready

**Viel Erfolg!** 🚀
