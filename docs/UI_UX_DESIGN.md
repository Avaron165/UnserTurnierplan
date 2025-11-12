# UnserTurnierplan - UI/UX Konzept & Design System

## Design-Philosophie

### Leitprinzipien
1. **Klarheit**: Intuitive Bedienung ohne Erklärungen
2. **Effizienz**: Schnelle Workflows für wiederkehrende Aufgaben
3. **Flexibilität**: Anpassbar an verschiedene Sportarten und Vereinsgrößen
4. **Zugänglichkeit**: WCAG 2.1 AA-konform
5. **Responsivität**: Perfekte Darstellung auf allen Geräten

### Zielgruppen & Use Cases

**Primär:**
- Turnierorganisatoren (30-60 Jahre, mittlere Tech-Affinität)
- Vereinsvorstände (40-70 Jahre, niedrig-mittlere Tech-Affinität)
- Helfer/Volunteers (18-50 Jahre, gemischte Tech-Affinität)

**Sekundär:**
- Teilnehmer/Sportler (15-50 Jahre, hohe Tech-Affinität)
- Schiedsrichter (25-60 Jahre, mittlere Tech-Affinität)
- Zuschauer (alle Altersgruppen)

---

## Design System

### Farbpalette

**Primary Colors (Hauptfarben):**
- **Primary Blue**: #0066CC (Vertrauen, Sport, Professionalität)
  - Light: #3385DB
  - Dark: #004999
- **Secondary Green**: #00A859 (Erfolg, Wachstum, Sport)
  - Light: #33BA7C
  - Dark: #008044

**Neutrals (Grautöne):**
- Gray 900: #1A1A1A (Haupttext)
- Gray 800: #333333
- Gray 700: #4D4D4D
- Gray 600: #666666
- Gray 500: #808080
- Gray 400: #999999
- Gray 300: #CCCCCC
- Gray 200: #E6E6E6
- Gray 100: #F5F5F5
- White: #FFFFFF

**Semantic Colors:**
- Success: #00A859
- Warning: #FFA500
- Error: #E63946
- Info: #0066CC

**Sport-Specific Accents (optional):**
- Soccer: #00A859 (Grün)
- Basketball: #FF6B35 (Orange)
- Tennis: #FFD700 (Gelb)
- Volleyball: #4169E1 (Blau)

### Typografie

**Font Family:**
- **Primär**: Inter oder Source Sans Pro (Sans-Serif)
- **Sekundär**: Roboto Mono (für Codes, Zeiten)
- **Fallback**: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial

**Type Scale:**
```
H1: 32px / 2rem    - Bold - 40px line-height
H2: 28px / 1.75rem - Bold - 36px line-height
H3: 24px / 1.5rem  - SemiBold - 32px line-height
H4: 20px / 1.25rem - SemiBold - 28px line-height
H5: 18px / 1.125rem - Medium - 26px line-height
Body: 16px / 1rem  - Regular - 24px line-height
Small: 14px / 0.875rem - Regular - 20px line-height
Tiny: 12px / 0.75rem - Regular - 18px line-height
```

**Font Weights:**
- Regular: 400
- Medium: 500
- SemiBold: 600
- Bold: 700

### Spacing System

**8px Grid System:**
```
xs:  4px  / 0.25rem
sm:  8px  / 0.5rem
md:  16px / 1rem
lg:  24px / 1.5rem
xl:  32px / 2rem
2xl: 48px / 3rem
3xl: 64px / 4rem
```

### Border Radius
```
none: 0px
sm:   4px
md:   8px
lg:   12px
xl:   16px
full: 9999px (circles)
```

### Shadows
```
sm:   0 1px 2px rgba(0,0,0,0.05)
md:   0 4px 6px rgba(0,0,0,0.07)
lg:   0 10px 15px rgba(0,0,0,0.1)
xl:   0 20px 25px rgba(0,0,0,0.15)
```

### Breakpoints (Responsive)
```
mobile:  < 640px
tablet:  640px - 1024px
desktop: > 1024px
wide:    > 1440px
```

---

## Component Library

### Buttons

**Primary Button:**
- Background: Primary Blue
- Text: White
- Hover: Primary Dark
- Border-Radius: 8px
- Padding: 12px 24px
- Font: SemiBold 16px

**Secondary Button:**
- Background: Transparent
- Border: 2px Primary Blue
- Text: Primary Blue
- Hover: Light Blue Background

**Tertiary/Ghost Button:**
- Background: Transparent
- Text: Primary Blue
- Hover: Gray 100 Background

**Icon Buttons:**
- Square/Circle
- Size: 40px × 40px
- Icon: 20px × 20px

**Button States:**
- Default
- Hover
- Active/Pressed
- Disabled (50% opacity)
- Loading (Spinner)

### Form Elements

**Input Fields:**
- Border: 1px Gray 300
- Border-Radius: 8px
- Padding: 12px 16px
- Focus: 2px Primary Blue border
- Error: 2px Error border
- Label: Above input, Gray 700, 14px
- Helper Text: Below input, Gray 600, 12px
- Placeholder: Gray 400

**Select Dropdowns:**
- Same style as Input
- Chevron-Icon rechts
- Dropdown: White, Shadow lg
- Options: Hover Gray 100

**Checkboxes & Radio Buttons:**
- Size: 20px × 20px
- Border: 2px Gray 400
- Checked: Primary Blue background
- Checkmark/Dot: White

**Switches/Toggles:**
- Width: 44px, Height: 24px
- Off: Gray 400
- On: Primary Blue
- Animated transition

**Date/Time Pickers:**
- Calendar-Dropdown
- Time-Selector (Stunden/Minuten)
- Range-Auswahl möglich

### Cards

**Standard Card:**
- Background: White
- Border: 1px Gray 200
- Border-Radius: 12px
- Padding: 24px
- Shadow: sm
- Hover: Shadow md (bei klickbar)

**Tournament Card:**
- Header: Sport-Icon + Titel
- Body: Datum, Ort, Teilnehmer
- Footer: Status-Badge + Action-Button
- Image optional (Banner)

**Stats Card:**
- Icon/Number groß
- Label klein darunter
- Background: Light Gradient optional

### Navigation

**Top Navigation Bar:**
- Height: 64px
- Background: White
- Border-Bottom: 1px Gray 200
- Logo links
- Menu-Items center/right
- User-Avatar rechts
- Search-Bar (optional)

**Sidebar Navigation:**
- Width: 256px (expandable/collapsible)
- Background: Gray 100 oder White
- Active Item: Primary Blue left border + Light Blue background
- Icons: 20px × 20px
- Collapsible zu Icon-Only (64px)

**Mobile Navigation:**
- Bottom Tab Bar (5 Items)
- Hamburger Menu alternative
- Swipe-Gesten

### Modals & Overlays

**Modal:**
- Background: White
- Max-Width: 600px (small), 900px (large)
- Border-Radius: 16px
- Padding: 32px
- Backdrop: rgba(0,0,0,0.5)
- Close-Button (X) top-right

**Drawer/Sidebar:**
- Full-Height
- Width: 400px
- Slide-in von rechts/links
- Backdrop optional

**Toast Notifications:**
- Position: Top-Right oder Bottom-Center
- Width: 350px
- Auto-Dismiss: 5 Sekunden
- Types: Success, Warning, Error, Info
- Icon + Message + Close-Button

### Tables

**Data Table:**
- Header: Bold, Gray 700, Background Gray 100
- Rows: Zebra-Striping (optional)
- Hover: Gray 50 Background
- Border: 1px Gray 200
- Sortable columns (Arrow-Icons)
- Pagination footer
- Responsive: Scroll horizontal auf Mobile

**Tournament Bracket:**
- Visuelle Baum-Darstellung
- Lines connecting matches
- Match-Cards enthalten Teams + Score
- Responsive: Horizontal scroll

### Badges & Tags

**Status Badges:**
- Pill-Shape (Border-Radius: full)
- Padding: 4px 12px
- Font: 12px Medium
- Colors:
  - Draft: Gray
  - Active/Ongoing: Primary Blue
  - Completed: Success Green
  - Cancelled: Error Red

**Sport Tags:**
- Rounded Rectangle
- Sport-Icon + Name
- Background: Light variant of sport color

### Icons

**Icon Library:** Lucide Icons oder Heroicons
**Sizes:**
- Small: 16px × 16px
- Medium: 20px × 20px
- Large: 24px × 24px

**Common Icons:**
- Home, Dashboard, Calendar
- Users, Team, Trophy
- Settings, Bell (Notifications)
- Plus, Edit, Trash
- Check, X, Info, Alert
- Download, Upload, Share
- Menu, Search, Filter

---

## Key Screens & Layouts

### 1. Dashboard (Vereins-Übersicht)

**Layout:**
```
┌─────────────────────────────────────────────┐
│ Top Navigation                               │
├──────┬──────────────────────────────────────┤
│      │ Welcome, [Club Name]!                │
│      ├──────────────────────────────────────┤
│ Side │ [KPI Cards: Turniere, Teilnehmer]   │
│ bar  ├──────────────────────────────────────┤
│      │ Upcoming Tournaments (List/Grid)     │
│      │ [Card] [Card] [Card]                 │
│      ├──────────────────────────────────────┤
│      │ Quick Actions                        │
│      │ [Create Tournament] [Manage Teams]   │
└──────┴──────────────────────────────────────┘
```

**Elemente:**
- KPI-Cards: Anzahl aktive Turniere, Gesamtteilnehmer, Nächstes Event
- Turnier-Cards mit Thumbnail, Titel, Datum, Quick-Actions
- Recent Activity Feed (optional)
- Notifications Dropdown

---

### 2. Turnier erstellen/bearbeiten

**Wizard-Flow (Multi-Step):**

**Step 1: Basis-Informationen**
- Turniername (Input)
- Sportart (Dropdown mit Icons)
- Beschreibung (Textarea)
- Banner-Upload (Image-Uploader)

**Step 2: Format & Regeln**
- Turnier-Format (Radio: K.O., Rundenturnier, Gruppen, etc.)
- Anzahl Teilnehmer (Number Input)
- Gruppengröße (wenn Gruppen-Modus)
- Spieldauer (Time Input)
- Pausen/Puffer (Time Input)

**Step 3: Datum & Ort**
- Startdatum (Date Picker)
- Enddatum (Date Picker)
- Anmeldeschluss (Date Picker)
- Veranstaltungsort (Input + Map-Integration)
- Spielfelder/Plätze (Number + Namen)

**Step 4: Anmeldung**
- Anmeldeformular-Builder (Drag & Drop)
- Startgebühr (Optional)
- Max. Teilnehmer
- Warteliste aktivieren (Checkbox)

**Step 5: Überprüfung**
- Zusammenfassung aller Eingaben
- [Zurück] [Als Draft speichern] [Veröffentlichen]

---

### 3. Turnier-Detail-Seite

**Tabs-Layout:**
```
┌─────────────────────────────────────────────┐
│ Banner-Image                                 │
│ [Tournament Name] [Edit] [Share]             │
│ 📅 Datum | 📍 Ort | 👥 Teilnehmer           │
├─────────────────────────────────────────────┤
│ [Übersicht] [Spielplan] [Teilnehmer]        │
│ [Rundown] [Catering] [Ergebnisse]           │
├─────────────────────────────────────────────┤
│                                              │
│ [Tab-Content]                                │
│                                              │
└─────────────────────────────────────────────┘
```

**Übersicht Tab:**
- Turnier-Informationen
- Status-Timeline
- Nächste Spiele
- Quick-Stats

**Spielplan Tab:**
- Turnierbaum (bei K.O.)
- Tabelle (bei Rundenturnier)
- Spielliste mit Filter
- Export-Button

**Teilnehmer Tab:**
- Liste/Grid der Teilnehmer
- Search & Filter
- Check-in Status
- Bulk-Actions

**Rundown Tab:**
- Rundown-Liste (verschiedene Typen)
- Timeline-Ansicht
- Aufgaben-Status-Übersicht
- [Neuer Rundown] Button

**Catering Tab:**
- Menü-Übersicht
- Bestellungen-Dashboard
- Schichtplan
- Einkaufsliste

**Ergebnisse Tab:**
- Live-Scores
- Abgeschlossene Spiele
- Statistiken
- Tabellenstände

---

### 4. Spielplan-Ansicht

**K.O.-System (Bracket):**
```
Round 1    Quarter    Semi      Final
┌────┐
│ T1 │─┐
└────┘ │ ┌────┐
       ├─│ W1 │─┐
┌────┐ │ └────┘ │
│ T2 │─┘        │ ┌────┐
└────┘          ├─│ W5 │─┐
                │ └────┘ │
┌────┐          │        │ ┌──────┐
│ T3 │─┐        │        ├─│Winner│
└────┘ │ ┌────┐ │        │ └──────┘
       ├─│ W2 │─┘        │
┌────┐ │ └────┘          │
│ T4 │─┘                 │
└────┘                   │
       ...               │
                        ...
```

**Rundenturnier (Table):**
```
┌────────────────────────────────────────────┐
│ #  | Team    | Sp | S | U | N | Tore | Pkt│
├────┼─────────┼────┼───┼───┼───┼──────┼────┤
│ 1  | Team A  | 5  | 4 | 1 | 0 | 12:3 | 13 │
│ 2  | Team B  | 5  | 3 | 1 | 1 | 10:5 | 10 │
│ 3  | Team C  | 5  | 2 | 2 | 1 |  8:7 |  8 │
│ ...                                        │
└────────────────────────────────────────────┘

Upcoming Matches:
[Team A vs Team C] - 14:00 Uhr, Feld 1
[Team B vs Team D] - 14:30 Uhr, Feld 2
```

---

### 5. Live-Ergebnis-Eingabe

**Match-Scorecard:**
```
┌─────────────────────────────────────────────┐
│ Match #5 - Viertelfinale                    │
│ Feld 2 | 14:00 Uhr                          │
├─────────────────────────────────────────────┤
│                                              │
│  Team A                    [  2  ]          │
│  [Logo] FC Example                          │
│                                              │
│  Team B                    [  1  ]          │
│  [Logo] SV Beispiel                         │
│                                              │
├─────────────────────────────────────────────┤
│ Spielzeit: [Dropdown: Halbzeit, Vollzeit]   │
│                                              │
│ ⚽ Tore | 🟨 Karten | 📊 Statistik          │
│                                              │
│ [Tor hinzufügen] [Spieler] [Minute]         │
│                                              │
│ [Spiel beenden] [Abbrechen]                 │
└─────────────────────────────────────────────┘
```

**Live-Updates:**
- Automatische Push an alle Zuschauer
- Timeline der Events (Tore, Karten, Wechsel)
- Real-time Tabellen-Aktualisierung

---

### 6. Rundown-Editor

**Timeline-View:**
```
08:00 ─────────────────────────────────────
      │ Aufbau beginnen
      │ ✓ Team Technik (Max, Lisa)
09:00 ─
      │ Catering Vorbereitung
      │ ⏳ Team Catering (Anna, Tom)
10:00 ─
      │ Turniereröffnung
      │ ⏳ Turnierleitung (Julia)
10:30 ─
      │ Spiel 1: Team A vs Team B
      │ ⏳ Schiedsrichter (Peter)
11:00 ─
      ...
```

**Task-Card (Detail):**
```
┌─────────────────────────────────────────────┐
│ [X] Aufbau beginnen                         │
│ ⏰ 08:00 - 09:00 Uhr | 📍 Haupthalle       │
│                                              │
│ Verantwortlich: Max Mustermann, Lisa Meier  │
│                                              │
│ Checkliste:                                  │
│ ☑ Tische aufbauen                           │
│ ☑ Technik testen                            │
│ ☐ Banner aufhängen                          │
│                                              │
│ [Bearbeiten] [Status ändern]                │
└─────────────────────────────────────────────┘
```

---

### 7. Mobile-Optimierung

**Bottom Tab Navigation:**
```
┌─────────────────────────────────────────────┐
│                                              │
│        [Main Content Area]                   │
│                                              │
│                                              │
├─────────────────────────────────────────────┤
│ [🏠] [📅] [➕] [🔔] [👤]                    │
│ Home Events  New  Notify Profile            │
└─────────────────────────────────────────────┘
```

**Mobile-Spezifische Anpassungen:**
- Größere Touch-Targets (min. 44px × 44px)
- Swipe-Gesten (z.B. Swipe zum Löschen)
- Pull-to-Refresh
- Burger-Menu für sekundäre Navigation
- Bottom-Sheet-Modals statt Center-Modals
- Sticky-Headers bei Scroll

---

## Accessibility (Barrierefreiheit)

### WCAG 2.1 AA Compliance

**Farb-Kontrast:**
- Text zu Background min. 4.5:1
- Large Text (18px+) min. 3:1
- UI-Komponenten min. 3:1

**Keyboard Navigation:**
- Alle Funktionen per Tastatur erreichbar
- Focus-Indikatoren sichtbar
- Logische Tab-Order
- Skip-Links für Hauptinhalte

**Screen Reader Support:**
- Semantisches HTML (Headings, Landmarks)
- ARIA-Labels für Icons/Buttons
- Alt-Text für alle Bilder
- Fehlermeldungen klar und konkret

**Responsive Text:**
- Min. Font-Size: 14px
- Zoombar bis 200% ohne Funktionsverlust
- Line-Height min. 1.5

**Weitere Features:**
- Dark Mode (Option)
- Anpassbare Font-Größe
- Reduzierte Animationen (prefers-reduced-motion)
- Untertitel für Videos

---

## Animation & Microinteractions

**Prinzipien:**
- Subtil und funktional
- Performance-optimiert
- Deaktivierbar (Accessibility)

**Standard-Transitions:**
- Fade: 200ms
- Slide: 300ms
- Scale: 150ms
- Easing: ease-in-out

**Microinteractions:**
- Button-Hover: Scale 1.02 + Shadow erhöhen
- Input-Focus: Border-Glow-Animation
- Success-Action: Check-Icon mit Scale-Animation
- Loading: Spinner oder Skeleton Screens
- Toast-Notification: Slide-in from top/right

**Page-Transitions:**
- Fade between routes
- Slide für Mobile-Navigation
- Keine Transitions bei langsamer Verbindung

---

## Responsive Design Patterns

### Desktop (> 1024px)
- Sidebar Navigation sichtbar
- Multi-Column-Layouts
- Data Tables vollständig
- Hover-States aktiv

### Tablet (640px - 1024px)
- Collapsible Sidebar oder Top Nav
- 2-Column-Layouts
- Größere Touch-Targets
- Tables horizontal scrollbar

### Mobile (< 640px)
- Bottom Tab Navigation
- Single-Column-Layouts
- Cards statt Tables
- Hamburger-Menu
- Full-Width-Buttons

---

## Design Deliverables

### Phase 1 (MVP)
- [ ] Design-System-Dokumentation
- [ ] Component Library (Figma/Sketch)
- [ ] Wireframes für alle Key Screens
- [ ] High-Fidelity Mockups (Desktop + Mobile)
- [ ] Interactive Prototypes
- [ ] Icon-Set

### Phase 2+
- [ ] Advanced Components
- [ ] Animation-Guidelines
- [ ] Dark Mode Variant
- [ ] Marketing-Materialien
- [ ] Brand-Guidelines

---

## Tools & Workflow

**Design:**
- Figma (Design & Prototyping)
- FigJam (Brainstorming)
- Adobe Illustrator (Icons)

**Handoff:**
- Figma Dev Mode
- Zeplin (optional)
- Style-Guide exportiert

**User Testing:**
- UserTesting.com
- Hotjar (Heatmaps)
- Google Analytics (Behavior)

---

## Nächste Schritte

1. Feedback zu diesem Konzept einholen
2. Design-System in Figma aufsetzen
3. Component Library entwickeln
4. Wireframes für MVP-Screens
5. Usability-Tests mit Vereinsvertretern
6. High-Fidelity-Designs erstellen
7. Developer-Handoff vorbereiten
