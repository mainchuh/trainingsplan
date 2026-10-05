# Onboarding: Fahrrad-Trainingsplan-Tool

Dieses Dokument fasst zusammen, warum dieses Projekt existiert, welche Entscheidungen bereits getroffen wurden und woran als Nächstes gearbeitet werden kann. Gedacht für eine Person (oder eine KI), die neu zum Projekt dazustößt.

## Kontext / Ausgangslage

Ziel ist ein datenbasierter Fahrrad-Trainingsplan, der sich über die Zeit automatisch an Form und Erholung anpasst. Typischer Hintergrund für den Einsatz dieses Tools:

- Allgemeine Fitnessziele (z. B. Grundfitness, Gewichtsreduktion)
- Optional ein persönliches Saisonziel mit festem Termin (z. B. eine Reise oder ein Event), auf das hin trainiert wird
- Möglichkeit spontaner Teilnahme an Rennen/Events – der Plan soll solche Abweichungen verkraften können

Die konkrete Trainingsstruktur ist bewusst **nicht** im Code oder in dieser Doku hinterlegt, sondern pro Person über `.env` konfigurierbar: Pendel-/Grundlagenkilometer (`PENDELSTRECKE_KM`), Anzahl strukturierter Einheiten pro Woche (`TRAININGSEINHEITEN_PRO_WOCHE`), FTP-Ausgangswert (`FTP_STARTWERT`), verfolgte Methodik (`TRAININGSMETHODIK`) sowie ein freies Trainingsziel (`TRAININGSZIEL`). Details dazu in `.env.example` und der README.

Bestehende Datenquellen/Tools: Strava, Wahoo, Zwift, Garmin-Smartwatch (Schlaf/Erholung) – alles läuft bereits in **intervals.icu** zusammen. Das ist der Grund, warum intervals.icu als einzige Integration gewählt wurde (siehe Entscheidungen unten).

Das vollständige Anforderungsdokument liegt eine Ebene höher: `../anforderungen-fahrrad-trainingsplan.md`.

## Was das Tool tut

Ein Python-CLI-Tool (`python main.py review`), das:

1. FTP (aus der Power-Curve/eFTP), CTL/ATL/TSB sowie die durchschnittliche Schlafdauer der letzten 7 Tage aus intervals.icu abruft,
2. daraus eine Formeinschätzung ableitet (`müde` / `neutral` / `frisch`),
3. zwei Sweet-Spot-Workouts für die nächsten strukturierten Einheiten vorschlägt (inkl. grobem Kraft- und Ernährungshinweis),
4. vor jeder Änderung eine Bestätigung verlangt (`[y/N]`) – nur bei „y" werden die Workouts als Events in intervals.icu angelegt.

Gedachter Rhythmus: einmal pro Woche manuell starten.

## Getroffene Entscheidungen (und warum)

- **Nur intervals.icu als Integration**, keine direkte Anbindung an Strava/Wahoo/Zwift/Garmin. Begründung: intervals.icu aggregiert bereits alle relevanten Daten (Aktivitäten, Wellness/Schlaf, FTP/Zonen) und verteilt Workouts selbst an die Trainingsapps weiter.
- **Kein Cron-Job / keine Automatisierung.** Der Review-Lauf ist bewusst manuell (einmal pro Woche vom Nutzer gestartet) und verlangt vor jeder Änderung an intervals.icu eine explizite Bestätigung. Kein automatisches Durchsetzen von Planänderungen ohne Zustimmung.
- **Fail-fast bei fehlender Konfiguration.** `config.py` liest `INTERVALS_ICU_API_KEY` und `INTERVALS_ICU_ATHLETE_ID` über `os.environ[...]` (nicht `.get()`) – ein fehlender Wert führt absichtlich zu einem harten `KeyError` statt einer stillen Fehlkonfiguration.
- **Mehrere Profile über separate `.env`-Dateien.** Es ist immer nur ein Profil gleichzeitig aktiv (`.env`). Für ein zweites Profil existiert z. B. `.env.michael`; zum Wechseln wird die aktive `.env` manuell gesichert (z. B. als `.env.johannes`) und die andere Datei eingesetzt. Alle `.env*`-Dateien außer `.env.example` sind per `.gitignore` von Git ausgeschlossen.
- **Formeinschätzung ist bewusst einfach gehalten:** `TSB < -20` oder Schlaf `< 6h` → „müde"; `TSB > 5` → „frisch"; sonst „neutral". Fehlt die Schlafdauer (z. B. weil Garmin nicht synchronisiert hat), wird nur anhand TSB entschieden.
- **eFTP-Fallback:** Enthält kein Wellness-Record der letzten 42 Tage einen `eftp`-Wert für `Ride`, wird auf den konfigurierten `FTP_STARTWERT` zurückgefallen.
- **Trainingsparameter konfigurierbar statt hartkodiert:** Pendelstrecke, Einheiten/Woche, FTP-Start, Methodik und Trainingsziel liegen in `.env` (mit sinnvollen Defaults in `config.py`), nicht im Code – so bleiben persönliche Werte außerhalb von Code/Doku und sind pro Profil austauschbar.
- **Kraft-/Ernährungshinweise sind bewusst grob** (Zufallsauswahl aus kurzen Textbausteinen in `main.py`), kein vollständiges Programm – nur als leichte, nicht granulare Hinweise gedacht.

## Projektstruktur

- `main.py` – CLI-Einstieg, Formeinschätzung, Workout-Generierung, Review-Flow
- `intervals_client.py` – dünner Wrapper um die intervals.icu-REST-API (Wellness, Activities, Events)
- `config.py` – lädt `.env`, stellt API-Key/Athlete-ID bereit (fail-fast)
- `.env.example` – Vorlage für die Konfiguration (ohne echte Werte)
- `README.md` – Setup- und Ausführungsanleitung (Installation, Konfiguration, Ausführung)

Stand: 3 Commits, Grundgerüst steht, Review-Flow funktioniert end-to-end (Abruf → Vorschlag → optionaler Push).

## Offene Punkte / mögliche nächste Schritte

- Genauere/konfigurierbare Form der Kraft- und Ernährungshinweise (aktuell feste Textbausteine, Zufallsauswahl).
- Ob über die Zeit zusätzliche inhaltliche Trainingsberatung sinnvoll ist, soll sich erst durch Nutzung zeigen – noch offen.
- Umgang mit Planabweichungen (verpasste/spontane Einheiten, spontane Rennen/Events) ist als Anforderung festgehalten, aber im Code noch nicht gezielt behandelt – aktuell wird bei jedem Lauf einfach neu ab „morgen" geplant.
- Darstellungsform des wöchentlichen Vorschlags ist aktuell reine Konsolenausgabe; eine Report-Datei o. Ä. wäre denkbar, ist aber nicht gefordert worden.

## Hinweise für die Arbeit mit einer KI an diesem Projekt

- Sprache im Projekt (Code-Kommentare spärlich, README, Anforderungen) ist Deutsch – das sollte beibehalten werden.
- Vor Änderungen an der Lauflogik lohnt sich ein Blick in `../anforderungen-fahrrad-trainingsplan.md` – dort stehen Nicht-Ziele (z. B. keine Automatisierung, keine zusätzlichen API-Anbindungen), die nicht versehentlich wieder eingeführt werden sollten.
- Sicherheitsrelevant: `.env*`-Dateien enthalten echte API-Keys und dürfen nie committet werden (bis auf `.env.example`).
