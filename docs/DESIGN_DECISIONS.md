# Sprint 4 - Design Decisions & Requirements Analysis

## 🎯 Projekt-Kontext

**UnserTurnierplan** - SaaS Platform für Sportvereine zur Turnierorganisation
- **Sprint 1-3:** User Auth, Club Management, Tournament Management (COMPLETE)
- **Sprint 4:** Match Scheduling & Brackets (THIS SPRINT)

---

## 📋 Anforderungsanalyse

### Ausgangsfrage vom User:
> "Ja, wenn wir wirklich alles bedacht haben. Es soll später auch Generatoren geben die z.B. die Teams auf N Gruppen aufteilen, innerhalb dieser jeder gegen jeden spielen und dann die ersten beiden weiterkommen in die KO Phase etc.... Es soll Qualifiings für Rennen geben,,,, Das muss nur vorgesehen sein."

### Erkannte Anforderungen:

#### 1. Multi-Participant Matches (KRITISCH!)
**Problem:** Klassische Tournament-Systeme gehen von 2 Teilnehmern aus
**Anforderung:** Rennen können 20+ Teilnehmer haben
**Lösung:** N:M Junction Table `match_participants` mit `slot_number`

#### 2. Flexible Turnier-Formate
**Benötigt:**
- ✅ Knockout (Single Elimination)
- ✅ Round-Robin (Jeder gegen jeden)
- 🔜 Group Stage → Knockout (WM-Style)
- 🔜 Qualifying → Finals (F1-Style)
- 🔜 Swiss System
- 🔜 Dutch/Hollandturnier

#### 3. Editierbarkeit
**Wichtig:** Generiert, aber per UI anpassbar
**Lösung:** Alle Match-Felder über API editierbar, keine "locked" states

#### 4. Zukunftssicherheit
**Vorbereitet für:**
- Gruppen-Zuteilung
- Qualifying Sessions
- Custom Tournament Rules
- Complex Multi-Phase Tournaments

---

## 🏗️ Design-Entscheidungen

### 1. Match-Participant Relationship

**Entscheidung:** N:M statt 1:N

```python
# ❌ REJECTED: 1:N (home_participant_id, away_participant_id)
# Problem: Kann keine Rennen abbilden

# ✅ CHOSEN: N:M via junction table
match_participants:
  - match_id
  - participant_id
  - slot_number (1, 2, 3, ...)
  - team_side ("home", "away", NULL)
```

**Vorteile:**
- Unterstützt 2-N Teilnehmer
- Flexible für alle Sportarten
- Leicht erweiterbar (Doppel, Staffeln)

### 2. Scoring System

**Entscheidung:** JSONB statt feste Spalten

```python
# ✅ JSONB für Flexibilität
score_data = Column(JSONB)  # Match-level
detailed_score = Column(JSONB)  # Participant-level
```

**Beispiele:**
```json
// Fußball
{"final_score": {"home": 2, "away": 1}, "halftime": {"home": 1, "away": 0}}

// Basketball
{"quarters": [{"home": 25, "away": 22}, ...], "final": {"home": 98, "away": 95}}

// Rennen
{"ranking": [{"participant_id": "...", "position": 1, "time": "1:23.456"}]}

// Tennis
{"sets": [[6,4], [7,5]], "winner_sets": 2}
```

**Vorteile:**
- Sport-agnostic
- Leicht erweiterbar
- Keine Schema-Änderungen für neue Sportarten

### 3. Tournament Format Rules

**Entscheidung:** JSONB Column für komplexe Regeln

```python
format_rules = Column(JSONB, nullable=True)
```

**Ermöglicht:**
```json
// Group Stage + Knockout (WM)
{
  "group_stage": {
    "num_groups": 4,
    "teams_per_group": 4,
    "advance_per_group": 2,
    "advancement_type": "top_n"
  },
  "knockout": {
    "type": "single_elimination",
    "seeding_method": "group_winners_first"
  }
}

// Qualifying (F1)
{
  "qualifying": {
    "sessions": [
      {"name": "Q1", "participants": 20, "advance": 15},
      {"name": "Q2", "participants": 15, "advance": 10},
      {"name": "Q3", "participants": 10, "advance": 10}
    ]
  },
  "final": {
    "grid_by": "best_qualifying_time"
  }
}

// Swiss System
{
  "swiss": {
    "rounds": 7,
    "pairing_method": "top_bottom",
    "tie_breaks": ["buchholz", "head_to_head"]
  }
}
```

### 4. Group Assignment

**Entscheidung:** Group auf Participant-Level

```python
# tournament_participants
group_assignment = Column(String(50), nullable=True)  # "Group A", "Pool 1"
```

**Warum hier statt in Match?**
- Teilnehmer werden VOR Match-Generierung zugeteilt
- Ein Teilnehmer = eine Gruppe
- Matches erben dann group_name

### 5. Match Phase

**Entscheidung:** Optionales `phase` Feld

```python
phase = Column(String(50), nullable=True)
# "group_stage", "knockout", "qualifying", "final"
```

**Vorteil:** Klarere Trennung bei Multi-Phase Turnieren

### 6. Bracket Progression

**Entscheidung:** Bidirektionale Links

```python
# Match kennt seine Dependencies
dependent_on_match_ids = Column(ARRAY(UUID))  # [match1_id, match2_id]
feeds_into_match_id = Column(UUID)  # next_round_match_id
```

**Ermöglicht:**
- Winner auto-progression
- Bracket-Visualisierung
- Dependency-Checks

### 7. Standings Cache

**Entscheidung:** Separate `tournament_standings` Table

**Warum nicht on-the-fly berechnen?**
- ❌ Performance: N matches = N queries
- ❌ Komplexe Sortierung (points, goal diff, head-to-head)
- ✅ Cache: Update nach jedem Match
- ✅ Schnelle Abfragen

---

## 🎨 Algorithmen

### Knockout Bracket Generation

**Problem:** 8 Teams → 3 Runden (4+2+1 Matches)

**Algorithmus:**
```python
1. Calculate rounds: ceil(log2(n_participants))
2. Calculate byes: next_power_of_2 - n_participants
3. Generate first round:
   - Regular matches für Teilnehmer-Paare
   - Bye-Matches für ungerade Anzahl
4. Generate empty subsequent rounds
5. Link via feeds_into_match_id
```

**Round Names:**
- 5 Rounds: "Round of 32", "Round of 16", "QF", "SF", "Final"
- 4 Rounds: "Round of 16", "QF", "SF", "Final"
- 3 Rounds: "QF", "SF", "Final"
- 2 Rounds: "SF", "Final"
- 1 Round: "Final"

### Round-Robin Schedule

**Problem:** Faire Spielplan-Erstellung

**Algorithmus:** Circle Method (Classic)
```
For n participants (make even):
1. Arrange in circle: [1, 2, 3, 4, 5, 6]
2. Fix position 1, rotate others
3. Pair opposite: (1,6), (2,5), (3,4)
4. Rotate: [1, 6, 2, 3, 4, 5]
5. Repeat for n-1 rounds

Result: Everyone plays everyone once, fair distribution
```

**Vorteile:**
- Mathematisch fair
- Keine Team spielt zweimal hintereinander gegen dasselbe Team
- Optimal für Heim-/Auswärtsspiele

---

## 🚧 Was ist JETZT, was ist SPÄTER?

### ✅ JETZT Implementiert (Sprint 4):

**Core Infrastructure:**
- Match Model mit N-Participant Support
- MatchParticipant Junction
- TournamentStandings Cache
- Flexible JSONB Scoring

**Tournament Types:**
- Knockout Bracket Generation
- Round-Robin Schedule Generation

**Features:**
- Match CRUD
- Score Management
- Status Workflow
- Standings Calculation

**Vorbereitet für Zukunft:**
- `format_rules` JSONB
- `group_assignment` auf Participants
- `phase` auf Matches
- Bracket progression links

### 🔜 SPÄTER (Sprint 5+):

**Advanced Generators:**
- Group Stage + Knockout Generator
- Qualifying Sessions Generator
- Swiss System Generator
- Dutch System Generator

**Scheduling:**
- Court/Field Assignment
- Time Slot Allocation
- Conflict Detection
- Auto-Scheduling

**Additional Features:**
- Match Notifications
- Live Score Updates (WebSockets)
- Referee Portal
- Statistics & Analytics

---

## 🎯 SOLID Principles Anwendung

### Single Responsibility
- `MatchService` → CRUD only
- `BracketService` → Generation only
- `StandingsService` → Calculation only

### Open/Closed
- JSONB scoring → erweiterbar ohne Code-Änderung
- `format_rules` → neue Formate ohne Schema-Änderung

### Liskov Substitution
- Alle Tournament Types nutzen dieselben Interfaces
- Match-Participant funktioniert für 2-N Teilnehmer

### Interface Segregation
- Separate Schemas für Create/Update/Response
- Services haben klare, fokussierte APIs

### Dependency Inversion
- Services nutzen Abstractions (AsyncSession)
- API Layer hängt von Service Layer ab

---

## 🔍 Edge Cases Berücksichtigt

### 1. Odd Number of Participants
**Problem:** 7 Teams im Knockout
**Lösung:** Bye-Matches mit `is_bye=True`, winner already set

### 2. Non-Power-of-2 Brackets
**Problem:** 6 Teams benötigen 3 Runden (nicht 2)
**Lösung:** Dynamische Berechnung via `ceil(log2(n))`

### 3. Multi-Winner Scenarios
**Problem:** Rennen haben keinen klaren "Winner"
**Lösung:** `final_position` statt nur `is_winner`

### 4. Draw Handling
**Problem:** Unentschieden im Round-Robin
**Lösung:** Score comparison, 1 point für draw

### 5. Match Deletion
**Problem:** Was passiert mit dependent matches?
**Lösung:** CASCADE delete via FK constraints

### 6. Empty Tournaments
**Problem:** Bracket Generation mit 0 participants
**Lösung:** Validation: "Need at least 2 participants"

---

## 📊 Performance Considerations

### Indexes
```sql
-- Match Queries
idx_match_tournament           (tournament_id)
idx_match_tournament_round     (tournament_id, round_number)
idx_match_tournament_status    (tournament_id, status)
idx_match_schedule             (scheduled_start, scheduled_end)

-- Standings Queries
idx_standings_tournament       (tournament_id)
idx_standings_tournament_group (tournament_id, group_name)
idx_standings_rank            (tournament_id, current_rank)
```

### Caching Strategy
- ✅ Standings: Cached in DB, update on score change
- ✅ Bracket: Generated once, stored
- 🔜 Future: Redis cache for live scores

### Query Optimization
- `selectinload()` für N+1 prevention
- Filtered queries mit indexes
- Pagination auf list endpoints

---

## 🔐 Security Considerations

### Permissions (Ready, not yet enforced):
- Tournament Creator → Full access
- Club Admin → Full access
- Referee → Score update only
- Public → Read-only for public tournaments

### Input Validation:
- Pydantic schemas validate all inputs
- JSONB fields validated at application level
- Foreign key constraints prevent orphans

### Data Integrity:
- Unique constraints prevent duplicate matches
- Status transitions validated
- CASCADE deletes prevent orphans

---

## 📚 Warum diese Entscheidungen?

### JSONB statt Relational
**Pro JSONB:**
- Sport-specific data varies drastically
- No schema migrations for new sports
- Flexible for future requirements

**Con JSONB:**
- Harder to query (but we don't need complex queries on score details)
- No type safety at DB level (but Pydantic validates)

**Entscheidung:** JSONB - Flexibilität wichtiger als strikte Typisierung

### Cache Standings statt Real-Time
**Pro Cache:**
- Performance: O(1) read vs O(n) calculation
- Consistency: Same ranking for all users
- Simpler queries

**Con Cache:**
- Eventual consistency (but we update immediately on score change)
- Extra storage

**Entscheidung:** Cache - Performance wichtiger als real-time 100%

### N:M Junction statt 1:N
**Pro N:M:**
- Supports unlimited participants
- Cleaner model
- Future-proof

**Con N:M:**
- Extra table
- More complex queries

**Entscheidung:** N:M - Flexibilität essentiell für Rennen

---

## 🎓 Lessons für zukünftige Sprints

### Was gut funktioniert:
✅ JSONB für flexible Data
✅ Service Layer Separation
✅ Comprehensive Schemas
✅ Algorithm-based Generation

### Was zu beachten ist:
⚠️ JSONB validation muss streng sein
⚠️ Permissions müssen noch implementiert werden
⚠️ WebSocket für live updates kommt später
⚠️ UI muss JSONB gut rendern können

---

## 🔗 Referenzen

**Algorithmen:**
- Round-Robin: "Circle Method" (Standard-Algorithmus seit 1800s)
- Knockout: Binary Tree Structure

**Standards:**
- REST API: FastAPI best practices
- Database: PostgreSQL JSONB standard
- Migration: Alembic standard workflow

---

**Dieses Dokument fasst ALLE Design-Entscheidungen zusammen.**  
**Ein neuer Claude sollte hiermit den kompletten Kontext haben.**