# Sprint 3 - Nur NEUE Dateien

## ⚠️ WICHTIG: Diese Dateien überschreiben NICHTS!

Diese sind die **brandneuen** Dateien für Sprint 3, die noch nicht in deinem Repo existieren.

## 📁 Neue Dateien (Sprint 3)

### Models (2 neue Dateien)
```
backend/app/models/tournament.py                    ← NEU
backend/app/models/tournament_participant.py        ← NEU
```

### Schemas (1 neue Datei)
```
backend/app/schemas/tournament.py                   ← NEU
```

### Services (2 neue Dateien)
```
backend/app/services/tournament_service.py          ← NEU
backend/app/services/tournament_participant_service.py  ← NEU
```

### API (1 neue Datei)
```
backend/app/api/tournaments.py                      ← NEU
```

### Migration (1 neue Datei)
```
backend/alembic/versions/003_create_tournaments.py  ← NEU
```

## 📝 Dateien die ANGEPASST werden müssen

Diese Dateien existieren schon, müssen aber ergänzt werden:

### 1. backend/app/models/user.py
**Hinzufügen:**
```python
# In den Relationships
tournaments_created = relationship("Tournament", back_populates="creator", foreign_keys="Tournament.created_by")
```

### 2. backend/app/models/club.py
**Hinzufügen:**
```python
# In den Relationships
tournaments = relationship("Tournament", back_populates="club", cascade="all, delete-orphan")
```

### 3. backend/app/models/__init__.py
**Hinzufügen:**
```python
from app.models.tournament import Tournament, TournamentType, TournamentStatus, SportType, ParticipantType
from app.models.tournament_participant import TournamentParticipant, ParticipantStatus, PaymentStatus

# Im __all__ ergänzen:
"Tournament", "TournamentType", "TournamentStatus", "SportType", "ParticipantType",
"TournamentParticipant", "ParticipantStatus", "PaymentStatus",
```

### 4. backend/app/schemas/__init__.py
**Hinzufügen:**
```python
from app.schemas.tournament import (
    TournamentBase, TournamentCreate, TournamentUpdate, TournamentResponse,
    TournamentDetail, TournamentListItem, TournamentStatusUpdate, TournamentFilters,
    TournamentParticipantBase, TournamentParticipantCreate, TournamentParticipantUpdate,
    TournamentParticipantResponse, TournamentParticipantDetail,
    ParticipantStatusUpdate, ParticipantPaymentUpdate
)

# Im __all__ ergänzen
```

### 5. backend/app/main.py
**Hinzufügen:**
```python
from app.api.tournaments import router as tournaments_router

# Router einbinden
app.include_router(tournaments_router, prefix=settings.API_PREFIX)
```

### 6. backend/requirements.txt
**Hinzufügen:**
```
python-slugify==8.0.1  # Für URL-friendly slugs
```

### 7. backend/alembic/env.py
**Hinzufügen:**
```python
# Im Import-Bereich
from app.models.tournament import Tournament
from app.models.tournament_participant import TournamentParticipant
```

## ✅ Installation Schritte

### Option A: Manuelle Integration (SICHER)
1. Kopiere nur die 7 neuen Dateien in dein Repo
2. Passe die 7 existierenden Dateien manuell an (siehe oben)
3. Teste die Änderungen

### Option B: Automatisch (mit Backup!)
1. **Backup erstellen:**
   ```bash
   git commit -am "backup before sprint3"
   ```

2. Neue Dateien kopieren
3. Existierende Dateien anpassen
4. Testen mit Docker

5. **Falls Probleme:**
   ```bash
   git reset --hard HEAD
   ```

## 🔍 Was überschrieben werden KÖNNTE

Falls diese Dateien bei dir anders aussehen:
- `backend/Dockerfile` - Prüf ob deine Version spezielle Anpassungen hat
- `backend/docker-compose.yml` - Ports, Volumes könnten anders sein
- `backend/.env.example` - Deine Keys könnten anders sein
- `backend/alembic.ini` - Deine Alembic-Config könnte anders sein

## 💡 Empfehlung

**SICHERSTER WEG:**
1. Kopiere nur die 7 NEUEN Dateien
2. Passe die existierenden Dateien manuell an (ich gebe dir die Snippets)
3. So überschreibst du NICHTS

Soll ich dir die Snippets zum manuellen Einfügen geben?
