# GitHub Setup Anleitung

## 🚀 Repository auf GitHub erstellen

### Schritt 1: Repository erstellen

1. Gehe zu [github.com](https://github.com) und logge dich ein
2. Klicke auf "New" oder "+" → "New repository"
3. **Repository Name**: `UnserTurnierplan`
4. **Description**: "Die All-in-One-Plattform für perfekt organisierte Sportturniere"
5. **Visibility**: 
   - ✅ Private (empfohlen während Entwicklung)
   - ❌ Public (später möglich)
6. **NICHT anklicken**:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
7. Klicke auf "Create repository"

### Schritt 2: Lokales Projekt mit GitHub verbinden

```bash
# 1. Tar-Datei entpacken
tar -xzf UnserTurnierplan.tar.gz
cd UnserTurnierplan

# 2. Git Remote hinzufügen (ERSETZE YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/UnserTurnierplan.git

# 3. Branch umbenennen (falls nötig)
git branch -M main

# 4. Ersten Commit erstellen
git add .
git commit -m "Initial commit: Sprint 1 - Backend Setup"

# 5. Auf GitHub pushen
git push -u origin main
```

**Alternative mit SSH** (empfohlen für häufiges Pushen):

```bash
# SSH-Key generieren (falls noch nicht vorhanden)
ssh-keygen -t ed25519 -C "your_email@example.com"

# SSH-Key zu GitHub hinzufügen
# 1. Key kopieren: cat ~/.ssh/id_ed25519.pub
# 2. GitHub → Settings → SSH and GPG keys → New SSH key
# 3. Key einfügen und speichern

# Remote mit SSH
git remote add origin git@github.com:YOUR_USERNAME/UnserTurnierplan.git
git push -u origin main
```

## 📝 GitHub Repository konfigurieren

### Branch Protection Rules einrichten

1. Gehe zu: **Settings** → **Branches** → **Add rule**
2. **Branch name pattern**: `main`
3. Aktiviere:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
4. Klicke auf "Create"

### Entwicklungs-Branch erstellen

```bash
# Develop-Branch erstellen
git checkout -b develop
git push -u origin develop

# Auf GitHub: Settings → Branches → Default branch → develop
```

## 🏷️ Empfohlene GitHub Labels

Gehe zu **Issues** → **Labels** und erstelle:

- `bug` (rot) - Etwas funktioniert nicht
- `enhancement` (grün) - Neues Feature / Verbesserung
- `documentation` (blau) - Dokumentation
- `good first issue` (lila) - Gut für Einsteiger
- `help wanted` (orange) - Hilfe benötigt
- `question` (pink) - Weitere Informationen benötigt
- `wontfix` (grau) - Wird nicht bearbeitet
- `duplicate` (grau) - Duplikat eines anderen Issues
- `sprint-1`, `sprint-2`, etc. (gelb) - Sprint-Zuordnung
- `backend` (cyan) - Backend-bezogen
- `frontend` (cyan) - Frontend-bezogen
- `database` (cyan) - Datenbank-bezogen

## 📊 GitHub Projects einrichten (optional)

1. Gehe zu **Projects** → **New project**
2. Wähle "Board" Template
3. Benenne es "UnserTurnierplan Development"
4. Erstelle Spalten:
   - 📋 Backlog
   - 🎯 To Do
   - 🚧 In Progress
   - 👀 In Review
   - ✅ Done

## 🔐 Secrets konfigurieren (für CI/CD)

Später für GitHub Actions:

1. **Settings** → **Secrets and variables** → **Actions**
2. Klicke auf "New repository secret"
3. Füge hinzu (später):
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `DATABASE_URL`
   - etc.

## 📌 Repository Topics hinzufügen

1. Gehe zur Repository-Hauptseite
2. Klicke auf das Zahnrad neben "About"
3. Füge Topics hinzu:
   - `fastapi`
   - `python`
   - `postgresql`
   - `docker`
   - `tournament-management`
   - `sports`
   - `react`
   - `typescript`
   - `nextjs`

## 🎉 Fertig!

Dein Repository ist jetzt bereit! 

### Nächste Schritte:

```bash
# Feature-Branch erstellen
git checkout -b feature/club-management

# Entwickeln...
# ... code, code, code ...

# Committen
git add .
git commit -m "feat: Add club management endpoints"

# Pushen
git push origin feature/club-management

# Auf GitHub: Pull Request erstellen
```

## 📚 Weitere GitHub Features

### GitHub Actions (später)

Erstelle `.github/workflows/ci.yml` für automatische Tests:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend pytest
```

### GitHub Pages (für Dokumentation)

Später kannst du die Dokumentation als Website hosten:
1. **Settings** → **Pages**
2. Source: `main` branch → `/docs` folder

## ⚠️ Wichtige Hinweise

- ✅ `.env` Datei ist in `.gitignore` → wird NICHT auf GitHub hochgeladen
- ✅ `SECRET_KEY` muss für Production neu generiert werden
- ✅ Sensible Daten NIE committen
- ✅ Vor dem Pushen immer `.gitignore` prüfen

## 🆘 Probleme?

**Push funktioniert nicht:**
```bash
# Credentials prüfen
git config --global user.name "Dein Name"
git config --global user.email "deine@email.com"

# Oder SSH verwenden (siehe oben)
```

**Repository URL ändern:**
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/UnserTurnierplan.git
```

**Branch-Fehler:**
```bash
git branch -M main
git push -u origin main
```
