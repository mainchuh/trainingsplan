# Fahrrad-Trainingsplan-Tool

Python-Tool, das auf Basis der in [intervals.icu](https://intervals.icu) aufgezeichneten Trainingsdaten (Aktivitäten, Fitness/Fatigue, Schlaf) einen Vorschlag für die nächsten beiden Sweet-Spot-Einheiten erstellt und diese nach Bestätigung direkt als Workouts in intervals.icu anlegt.

## Voraussetzungen

- Python 3.11 oder neuer
- Ein intervals.icu-Account mit hinterlegter FTP/Power-Curve-Historie
- intervals.icu-API-Key (Settings → Developer Settings → API Key)
- intervals.icu-Athlete-ID (aus der URL, z. B. `intervals.icu/athlete/i123456/...` → `i123456`)

## Installation

```bash
python -m venv .venv
```

Windows (PowerShell):
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Konfiguration

1. `.env.example` nach `.env` kopieren.
2. In `.env` eintragen:
   ```
   INTERVALS_ICU_API_KEY=dein-api-key
   INTERVALS_ICU_ATHLETE_ID=i123456
   ```
3. `.env` niemals committen – sie ist in `.gitignore` ausgeschlossen.

**Mehrere Personen/Profile:** Es ist jeweils nur ein Profil gleichzeitig aktiv. Für ein zweites Profil eine weitere Datei anlegen (z. B. `.env.michael`) und bei Bedarf manuell anstelle von `.env` einsetzen (`.env` vorher sichern, z. B. als `.env.johannes`). Alle `.env*`-Dateien außer `.env.example` sind von Git ausgeschlossen.

## Ausführung

```bash
python main.py review
```

Das Tool:
1. ruft FTP (aus der Power-Curve/eFTP), CTL/ATL/TSB sowie die durchschnittliche Schlafdauer der letzten 7 Tage ab,
2. leitet daraus eine Einschätzung ab (`müde` / `neutral` / `frisch`),
3. schlägt zwei Sweet-Spot-Workouts für die nächsten strukturierten Einheiten vor (inkl. grobem Krafttraining- und Ernährungs-Hinweis),
4. fragt vor jeder Änderung nach Bestätigung (`[y/N]`) – nur bei „y“ werden die Workouts als Events in intervals.icu angelegt.

Empfohlener Rhythmus: einmal pro Woche manuell starten.

## Zu beachten

- Der wöchentliche Review-Lauf ist bewusst **nicht automatisiert** (kein Cron-Job) – er soll manuell gestartet werden.
- Ohne gültige `.env` bricht der Start mit einem `KeyError` ab – das ist beabsichtigt (fail fast statt stiller Fehlkonfiguration).
- Enthält `sportInfo` eines Tages keine `eftp` für `Ride`, wird auf den letzten bekannten Wert bzw. 280W zurückgefallen.
- Fehlt die Schlafdauer (`sleepSecs` nicht aus Garmin synchronisiert), wird die Einschätzung allein anhand von TSB getroffen.
- Nach dem ersten Push lohnt sich ein Blick in den intervals.icu-Kalender, ob das Workout (insbesondere die Intervall-Schritte) korrekt angezeigt wird, bevor es z. B. an Zwift/Wahoo weitergegeben wird.
