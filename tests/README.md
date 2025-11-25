# Sprint 4 Tests

## Python/Pytest Tests (Empfohlen!)

### Installation
```bash
pip install -r tests/requirements-test.txt
```

### Tests ausführen
```bash
# Alle Tests
pytest tests/test_sprint4_matches.py -v

# Bestimmte Test-Klasse
pytest tests/test_sprint4_matches.py::TestMatchCRUD -v

# Bestimmter Test
pytest tests/test_sprint4_matches.py::TestMatchCRUD::test_create_manual_match -v

# Mit detaillierter Ausgabe
pytest tests/test_sprint4_matches.py -vv -s
```

### Voraussetzungen
- Backend muss laufen auf http://localhost:8000
- Entweder via Docker Compose ODER direkt mit uvicorn

## Bash Tests (Legacy)

Die ursprünglichen Bash-Tests sind weiterhin verfügbar:
```bash
./tests/sprint4_tests.sh
```

Hinweis: Bash-Tests haben JSON-Encoding-Probleme mit curl. Python-Tests sind stabiler.
