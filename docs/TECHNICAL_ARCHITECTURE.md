# UnserTurnierplan - Technische Architektur

## Systemarchitektur

### High-Level Architektur
```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                          │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Web App    │  iOS App     │  Android App │  PWA       │
│  (React)     │  (Native)    │  (Native)    │            │
└──────────────┴──────────────┴──────────────┴────────────┘
                            │
                    ┌───────▼────────┐
                    │   API Gateway  │
                    │   (Kong/NGINX) │
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│  Auth Service  │  │ API Service │  │ WebSocket Server│
│  (OAuth/JWT)   │  │ (REST/GraphQL)│ │  (Socket.io)   │
└───────┬────────┘  └──────┬──────┘  └────────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│  PostgreSQL    │  │    Redis    │  │   S3/Storage   │
│  (Primary DB)  │  │   (Cache)   │  │   (Files)      │
└────────────────┘  └─────────────┘  └─────────────────┘
```

## Backend-Architektur

### Microservices-Ansatz

#### 1. **User & Auth Service**
- Benutzerregistrierung und -authentifizierung
- OAuth 2.0 / JWT-Token-Management
- 2FA-Implementierung
- Rollen- und Berechtigungsverwaltung
- Profilverwaltung

#### 2. **Club Management Service**
- Vereinsverwaltung
- Vereinsverifizierung
- Mitgliederverwaltung
- Abteilungen und Teams
- Sportstätten-Verwaltung

#### 3. **Tournament Service**
- Turniererstellung und -konfiguration
- Turnierformate und -modi
- Spielplan-Generierung
- Turnierstatus-Verwaltung
- Turnier-Templates

#### 4. **Registration Service**
- Teilnehmer-Anmeldung
- Team-Registrierung
- Wartelisten-Management
- Einladungssystem
- Anmeldeformular-Builder

#### 5. **Match & Results Service**
- Spielverwaltung
- Spielfeld-/Platz-Zuweisung
- Live-Ergebnis-Erfassung
- Spielstatistiken
- Schiedsrichter-Zuweisung

#### 6. **Rundown Service**
- Rundown-Generierung
- Aufgaben-Management
- Zeitplan-Verwaltung
- Template-Management
- Checklisten

#### 7. **Catering Service**
- Menüplanung
- Bestellverwaltung
- Schichtplanung
- Bestandsverwaltung
- Einkaufslisten

#### 8. **Communication Service**
- Push-Benachrichtigungen
- E-Mail-Versand
- SMS-Versand
- In-App-Messaging
- Announcements

#### 9. **Payment Service**
- Zahlungsabwicklung
- Stripe/PayPal-Integration
- Rechnungserstellung
- Startgebühren-Management
- Rückerstattungen

#### 10. **Analytics Service**
- Event-Tracking
- Statistik-Aggregation
- Report-Generierung
- Dashboard-Daten
- KPI-Berechnung

#### 11. **Document Service**
- Dokument-Templates
- PDF-Generierung
- Urkunden-Erstellung
- Archiv-Verwaltung
- Export-Funktionen

#### 12. **Integration Service**
- API-Gateway
- Webhook-Management
- Drittanbieter-Integrationen
- Kalender-Sync
- Social Media-Integration

### Datenbank-Schema (PostgreSQL)

#### Core Tables

**users**
- id (UUID, PK)
- email (unique)
- password_hash
- first_name
- last_name
- phone
- avatar_url
- language
- timezone
- email_verified
- two_factor_enabled
- created_at
- updated_at
- last_login

**clubs**
- id (UUID, PK)
- name
- slug (unique)
- description
- logo_url
- address
- city
- postal_code
- country
- phone
- email
- website
- verification_status (enum: pending, verified, rejected)
- verification_badge_date
- founded_date
- member_count
- created_at
- updated_at

**club_members**
- id (UUID, PK)
- club_id (FK)
- user_id (FK)
- role (enum: owner, admin, manager, member, volunteer)
- department
- position
- joined_at
- created_at

**tournaments**
- id (UUID, PK)
- club_id (FK)
- creator_id (FK)
- name
- slug (unique)
- description
- sport_type
- tournament_format (enum: knockout, round_robin, groups_knockout, swiss, league)
- status (enum: draft, published, registration_open, registration_closed, ongoing, completed, cancelled)
- start_date
- end_date
- location
- max_participants
- registration_deadline
- entry_fee
- prize_money
- rules_text
- visibility (enum: public, private, unlisted)
- banner_url
- created_at
- updated_at

**tournament_participants**
- id (UUID, PK)
- tournament_id (FK)
- participant_type (enum: individual, team)
- participant_id (FK to users or teams)
- registration_date
- payment_status (enum: pending, paid, refunded)
- status (enum: registered, confirmed, checked_in, withdrew, disqualified)
- group_assignment
- seed_number
- notes

**teams**
- id (UUID, PK)
- club_id (FK)
- name
- logo_url
- category
- age_group
- captain_id (FK to users)
- created_at

**team_members**
- id (UUID, PK)
- team_id (FK)
- user_id (FK)
- position
- jersey_number
- joined_at

**matches**
- id (UUID, PK)
- tournament_id (FK)
- round_number
- match_number
- stage (enum: group, round_of_32, round_of_16, quarter_final, semi_final, final, third_place)
- participant_1_id (FK)
- participant_2_id (FK)
- scheduled_time
- venue
- field_number
- referee_id (FK to users)
- status (enum: scheduled, in_progress, completed, postponed, cancelled)
- score_1
- score_2
- winner_id (FK)
- match_data (JSONB) // Sport-spezifische Daten
- created_at
- updated_at

**rundowns**
- id (UUID, PK)
- tournament_id (FK)
- name
- description
- rundown_type (enum: tournament_direction, catering, technical, security, referee, general)
- start_time
- end_time
- template_id (FK)
- created_by (FK to users)
- created_at
- updated_at

**rundown_tasks**
- id (UUID, PK)
- rundown_id (FK)
- title
- description
- assigned_to (FK to users)
- start_time
- end_time
- duration_minutes
- location
- priority (enum: low, medium, high, critical)
- status (enum: todo, in_progress, completed, cancelled)
- depends_on (FK to rundown_tasks) // Task-Abhängigkeit
- checklist_items (JSONB)
- order_index
- created_at
- updated_at

**invitations**
- id (UUID, PK)
- tournament_id (FK)
- inviter_id (FK to users)
- invitee_email
- invitee_user_id (FK to users, nullable)
- token (unique)
- status (enum: sent, opened, accepted, declined, expired)
- sent_at
- opened_at
- responded_at
- expires_at
- message

**catering_menus**
- id (UUID, PK)
- tournament_id (FK)
- name
- description
- available_from
- available_until
- created_at

**catering_items**
- id (UUID, PK)
- menu_id (FK)
- name
- description
- category (enum: food, beverage, snack, dessert)
- price
- allergens (JSONB)
- dietary_flags (JSONB) // vegetarian, vegan, gluten-free, etc.
- available_quantity
- image_url

**catering_orders**
- id (UUID, PK)
- tournament_id (FK)
- user_id (FK)
- order_date
- pickup_time
- status (enum: pending, confirmed, prepared, picked_up, cancelled)
- total_amount
- payment_method
- notes

**catering_order_items**
- id (UUID, PK)
- order_id (FK)
- item_id (FK to catering_items)
- quantity
- unit_price
- subtotal

**payments**
- id (UUID, PK)
- tournament_id (FK)
- payer_id (FK to users)
- amount
- currency
- payment_type (enum: entry_fee, catering, merchandise, refund)
- payment_method (enum: stripe, paypal, sepa, cash)
- payment_provider_id
- status (enum: pending, completed, failed, refunded)
- created_at
- updated_at

**documents**
- id (UUID, PK)
- tournament_id (FK)
- document_type (enum: certificate, protocol, participant_list, report, other)
- title
- file_url
- file_size
- mime_type
- generated_by (FK to users)
- created_at

**notifications**
- id (UUID, PK)
- user_id (FK)
- type (enum: email, push, sms, in_app)
- title
- message
- link
- read
- sent_at
- read_at

**analytics_events**
- id (UUID, PK)
- event_type
- user_id (FK, nullable)
- tournament_id (FK, nullable)
- club_id (FK, nullable)
- metadata (JSONB)
- timestamp

### Caching-Strategie (Redis)

**Cache Keys:**
- `user:{user_id}:profile`
- `club:{club_id}:details`
- `tournament:{tournament_id}:info`
- `tournament:{tournament_id}:participants`
- `tournament:{tournament_id}:matches`
- `tournament:{tournament_id}:standings`
- `tournament:{tournament_id}:live`
- `session:{session_token}`

**Cache-Invalidierung:**
- Time-based expiry (TTL)
- Event-based invalidation bei Datenänderungen
- Cache-warming für häufig abgerufene Daten

### Real-Time Communication (WebSocket)

**Channels:**
- `tournament:{id}:live` - Live-Updates für Turnier
- `tournament:{id}:chat` - Chat für Organisatoren
- `match:{id}:live` - Live-Updates für einzelnes Spiel
- `user:{id}:notifications` - Persönliche Benachrichtigungen
- `rundown:{id}:updates` - Rundown-Änderungen

## Frontend-Architektur

### Web Application (React/Next.js)

**Verzeichnisstruktur:**
```
/src
  /components
    /common        # Wiederverwendbare UI-Komponenten
    /layout        # Layout-Komponenten
    /tournament    # Turnier-spezifische Komponenten
    /club          # Vereins-Komponenten
    /rundown       # Rundown-Komponenten
    /catering      # Catering-Komponenten
  /pages           # Next.js-Pages/Routes
  /hooks           # Custom React Hooks
  /services        # API-Services
  /store           # State Management (Redux/Zustand)
  /utils           # Utility-Funktionen
  /styles          # Global Styles
  /types           # TypeScript-Typen
  /config          # Konfiguration
```

**State Management:**
- Zustand oder Redux Toolkit
- React Query für Server-State
- Context API für Theme/Auth

**UI-Framework:**
- Tailwind CSS oder Material-UI
- Component Library (Shadcn/ui)
- Responsive Design (Mobile First)

### Mobile Applications (React Native)

**Shared Codebase:**
- React Native für iOS und Android
- Native Modules bei Bedarf
- Expo für schnellere Entwicklung (optional)

**Offline-Funktionalität:**
- AsyncStorage für lokale Daten
- Sync bei Netzwerk-Verfügbarkeit
- Optimistic Updates

## API-Design

### RESTful API Endpoints

**Authentication:**
- POST `/api/v1/auth/register`
- POST `/api/v1/auth/login`
- POST `/api/v1/auth/logout`
- POST `/api/v1/auth/refresh`
- POST `/api/v1/auth/verify-email`
- POST `/api/v1/auth/forgot-password`
- POST `/api/v1/auth/reset-password`

**Clubs:**
- GET `/api/v1/clubs`
- POST `/api/v1/clubs`
- GET `/api/v1/clubs/:id`
- PUT `/api/v1/clubs/:id`
- DELETE `/api/v1/clubs/:id`
- POST `/api/v1/clubs/:id/verify`
- GET `/api/v1/clubs/:id/members`
- POST `/api/v1/clubs/:id/members`

**Tournaments:**
- GET `/api/v1/tournaments`
- POST `/api/v1/tournaments`
- GET `/api/v1/tournaments/:id`
- PUT `/api/v1/tournaments/:id`
- DELETE `/api/v1/tournaments/:id`
- POST `/api/v1/tournaments/:id/publish`
- GET `/api/v1/tournaments/:id/participants`
- POST `/api/v1/tournaments/:id/participants`
- POST `/api/v1/tournaments/:id/generate-schedule`
- GET `/api/v1/tournaments/:id/matches`
- GET `/api/v1/tournaments/:id/standings`

**Matches:**
- GET `/api/v1/matches/:id`
- PUT `/api/v1/matches/:id`
- POST `/api/v1/matches/:id/start`
- POST `/api/v1/matches/:id/result`
- POST `/api/v1/matches/:id/stats`

**Rundowns:**
- GET `/api/v1/tournaments/:id/rundowns`
- POST `/api/v1/tournaments/:id/rundowns`
- GET `/api/v1/rundowns/:id`
- PUT `/api/v1/rundowns/:id`
- DELETE `/api/v1/rundowns/:id`
- GET `/api/v1/rundowns/:id/tasks`
- POST `/api/v1/rundowns/:id/tasks`
- PUT `/api/v1/rundowns/:id/tasks/:taskId`
- POST `/api/v1/rundowns/:id/tasks/:taskId/complete`

**Catering:**
- GET `/api/v1/tournaments/:id/catering/menus`
- POST `/api/v1/tournaments/:id/catering/menus`
- GET `/api/v1/tournaments/:id/catering/orders`
- POST `/api/v1/tournaments/:id/catering/orders`
- PUT `/api/v1/catering/orders/:id/status`

### GraphQL API (Optional/Alternative)

GraphQL für flexiblere Abfragen, besonders nützlich für:
- Mobile Apps (reduzierte Datenmenge)
- Komplexe verschachtelte Abfragen
- Echtzeit-Subscriptions

## Sicherheit

### Authentifizierung & Autorisierung
- JWT-Tokens (Access + Refresh)
- Token-Rotation
- HTTP-Only Cookies für Web
- Secure Storage für Mobile
- OAuth 2.0 für Drittanbieter

### Datenvalidierung
- Input-Validierung (Backend)
- Schema-Validation (Joi, Yup)
- SQL-Injection-Prävention (ORM)
- XSS-Protection
- CSRF-Tokens

### Rate Limiting
- API-Rate-Limits pro Benutzer/IP
- DDoS-Schutz
- Exponential Backoff

### Verschlüsselung
- TLS 1.3 für alle Verbindungen
- Passwort-Hashing (bcrypt/Argon2)
- Sensible Daten verschlüsselt in DB
- End-to-End für bestimmte Features

## Deployment & Infrastructure

### Cloud-Provider (AWS Beispiel)

**Compute:**
- EC2/ECS für Backend-Services
- Lambda für Event-driven Tasks
- Elastic Beanstalk für einfaches Deployment

**Database:**
- RDS PostgreSQL (Multi-AZ)
- ElastiCache Redis
- Automated Backups

**Storage:**
- S3 für Dateien (Bilder, Dokumente)
- CloudFront CDN

**Monitoring:**
- CloudWatch für Logs und Metriken
- X-Ray für Distributed Tracing
- Sentry für Error Tracking

### CI/CD Pipeline

**Tools:**
- GitHub Actions oder GitLab CI
- Docker für Containerization
- Kubernetes für Orchestration (optional)

**Workflow:**
1. Code Push → Git Repository
2. Automated Tests (Unit, Integration, E2E)
3. Build Docker Images
4. Push to Container Registry
5. Deploy to Staging
6. Smoke Tests
7. Deploy to Production (Blue-Green)

### Monitoring & Logging

**Logging:**
- Strukturiertes Logging (JSON)
- Zentrales Log-Management (ELK-Stack)
- Log-Retention-Policy

**Monitoring:**
- Application Performance Monitoring (APM)
- Uptime-Monitoring
- Resource-Monitoring (CPU, RAM, Disk)
- Custom Business Metrics

**Alerting:**
- PagerDuty/Opsgenie für Incidents
- Slack-Integration
- E-Mail-Alerts

## Skalierung

### Horizontal Scaling
- Load Balancer (ALB/NLB)
- Auto-Scaling Groups
- Stateless Backend-Services
- Session-Management via Redis

### Database Scaling
- Read Replicas
- Connection Pooling
- Query-Optimierung
- Partitionierung bei Bedarf

### Caching-Strategie
- Multi-Level-Caching
- CDN für statische Assets
- Redis für Session/Data
- Browser-Caching

## Backup & Disaster Recovery

### Backup-Strategie
- Automatische tägliche DB-Backups
- Point-in-Time-Recovery
- S3-Versioning für Dateien
- Retention: 30 Tage

### Disaster Recovery
- RTO (Recovery Time Objective): 4 Stunden
- RPO (Recovery Point Objective): 1 Stunde
- Disaster Recovery Plan dokumentiert
- Regelmäßige DR-Tests

## Compliance & Datenschutz

### DSGVO-Anforderungen
- Einwilligung bei Datenerfassung
- Recht auf Auskunft
- Recht auf Löschung
- Recht auf Datenübertragbarkeit
- Privacy by Design/Default
- Datenschutz-Folgenabschätzung
- AV-Verträge mit Dienstleistern

### Audit-Trail
- Alle kritischen Aktionen loggen
- User-Aktivitäten nachverfolgbar
- Unveränderliche Logs
- Compliance-Reports

## Performance-Ziele

- **Page Load Time**: < 2 Sekunden
- **API Response Time**: < 200ms (p95)
- **Uptime**: 99.9%
- **Database Queries**: < 50ms (p95)
- **WebSocket Latency**: < 100ms

## Testing-Strategie

### Test-Pyramide
- Unit Tests (70%)
- Integration Tests (20%)
- E2E Tests (10%)

### Testing-Tools
- Jest für Unit/Integration Tests
- Cypress/Playwright für E2E
- Postman/Newman für API-Tests
- K6 für Load-Tests

### Test Coverage
- Ziel: > 80% Code Coverage
- Kritische Pfade: 100%
- Automated Testing in CI/CD
