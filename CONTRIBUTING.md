# Contributing to UnserTurnierplan

Vielen Dank für Ihr Interesse an UnserTurnierplan! 🎉

## 🚀 Getting Started

1. **Fork das Repository**
2. **Clone dein Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/UnserTurnierplan.git
   cd UnserTurnierplan
   ```
3. **Setup Development Environment**
   ```bash
   docker-compose up -d
   docker-compose exec backend alembic upgrade head
   ```

## 📋 Entwicklungs-Workflow

### Branch-Strategie

- `main` - Production-ready Code
- `develop` - Development Branch
- `feature/*` - Feature Branches
- `bugfix/*` - Bug Fixes
- `hotfix/*` - Hotfixes für Production

### Feature entwickeln

```bash
# Branch erstellen
git checkout -b feature/my-amazing-feature

# Änderungen machen
# ... code, code, code ...

# Tests ausführen
docker-compose exec backend pytest

# Code formatieren
docker-compose exec backend black .
docker-compose exec backend isort .

# Committen
git add .
git commit -m "feat: Add amazing feature"

# Pushen
git push origin feature/my-amazing-feature

# Pull Request erstellen auf GitHub
```

## 📝 Commit-Konventionen

Wir verwenden [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - Neues Feature
- `fix:` - Bug Fix
- `docs:` - Dokumentation
- `style:` - Code-Formatierung
- `refactor:` - Code-Refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Beispiele:**
```
feat: Add tournament creation endpoint
fix: Resolve user authentication bug
docs: Update API documentation
test: Add user service tests
```

## 🧪 Testing

```bash
# Alle Tests
docker-compose exec backend pytest

# Mit Coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Spezifische Tests
docker-compose exec backend pytest app/tests/test_auth.py
```

## 📏 Code-Standards

### Python (Backend)
- **Style Guide**: PEP 8
- **Formatter**: Black
- **Import Sorting**: isort
- **Type Hints**: Verwenden Sie Type Hints überall
- **Docstrings**: Google-Style Docstrings

```python
def calculate_tournament_score(
    team_id: UUID, 
    matches: List[Match]
) -> int:
    """
    Calculate total score for a team.
    
    Args:
        team_id: UUID of the team
        matches: List of matches to calculate from
        
    Returns:
        Total score as integer
        
    Raises:
        ValueError: If team_id not found
    """
    # Implementation
    pass
```

### Code-Formatierung

```bash
# Backend formatieren
cd backend
black .
isort .
flake8
mypy .
```

## 🔍 Code Review

Alle Pull Requests müssen reviewed werden:

- ✅ Code folgt Standards
- ✅ Tests sind vorhanden
- ✅ Dokumentation ist aktualisiert
- ✅ Keine Breaking Changes (oder dokumentiert)
- ✅ Performance-Impact berücksichtigt

## 📦 Pull Request Template

```markdown
## Beschreibung
Kurze Beschreibung der Änderungen

## Art der Änderung
- [ ] Bug Fix
- [ ] Neues Feature
- [ ] Breaking Change
- [ ] Dokumentation

## Wie wurde getestet?
Beschreiben Sie Ihre Tests

## Checklist
- [ ] Code folgt Style Guidelines
- [ ] Selbst-Review durchgeführt
- [ ] Code kommentiert (komplexe Stellen)
- [ ] Dokumentation aktualisiert
- [ ] Keine neuen Warnings
- [ ] Tests hinzugefügt
- [ ] Alle Tests bestanden
```

## 🐛 Bug Reports

Beim Erstellen von Bug Reports bitte folgende Informationen:

- **Beschreibung**: Was ist das Problem?
- **Schritte zum Reproduzieren**: Wie kann man den Bug auslösen?
- **Erwartetes Verhalten**: Was sollte passieren?
- **Aktuelles Verhalten**: Was passiert stattdessen?
- **Screenshots**: Falls relevant
- **Umgebung**: OS, Browser, Docker Version, etc.
- **Zusätzlicher Kontext**: Weitere Informationen

## 💡 Feature Requests

Für Feature Requests:

- **Problem**: Welches Problem löst das Feature?
- **Lösung**: Wie würde das Feature aussehen?
- **Alternativen**: Andere Lösungsansätze?
- **Use Cases**: Wann würde man das Feature nutzen?

## 📚 Dokumentation

Dokumentation ist wichtig! Bitte aktualisieren Sie:

- README.md bei Feature-Änderungen
- API-Dokumentation (Docstrings)
- Technische Dokumentation bei Architektur-Änderungen
- Setup-Guides bei Abhängigkeits-Änderungen

## 🎯 Entwicklungs-Tipps

### Backend Development

```bash
# Hot Reload ist aktiv
# Änderungen werden automatisch erkannt

# Logs anschauen
docker-compose logs -f backend

# Shell im Container
docker-compose exec backend bash

# Python Shell mit App Context
docker-compose exec backend python
>>> from app.db.session import AsyncSessionLocal
```

### Debugging

```python
# pdb verwenden
import pdb; pdb.set_trace()

# Oder ipdb (interaktiver)
import ipdb; ipdb.set_trace()
```

## ❓ Fragen?

- **GitHub Issues**: Für Bugs und Features
- **GitHub Discussions**: Für Fragen und Diskussionen
- **Email**: Für private Anfragen

## 📜 License

Durch Beiträge akzeptieren Sie, dass Ihr Code unter der gleichen Lizenz wie das Projekt steht.

---

Vielen Dank für Ihre Beiträge! 🙏
