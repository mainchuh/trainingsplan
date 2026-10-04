import argparse
import random
import sys
from datetime import date, timedelta

from intervals_client import IntervalsClient

STRENGTH_TIPS = [
    "Oberkörper & Core: 2x15 Liegestütze, 3x45s Plank, 2x12 Rudern am Kabelzug.",
    "Beine ergänzend: 3x10 Kniebeugen, 3x10 Ausfallschritte je Seite, 2x15 Wadenheben.",
    "Ganzkörper leicht: Mobility/Stretching, 2x12 Klimmzüge oder Latzug, 3x12 Rumpfrotation.",
]

NUTRITION_TIPS = [
    "Sweet-Spot-Woche: auf ausreichend Kohlenhydrate rund ums Training achten (vor/nach der Einheit).",
    "Erholungswoche: Eiweißzufuhr im Blick behalten, Alkohol eher meiden.",
    "Allgemein: genug trinken, besonders an Pendel-Tagen mit viel Volumen.",
]


def extract_eftp(wellness_records, fallback=280):
    for record in reversed(wellness_records):
        for sport in record.get("sportInfo") or []:
            if sport.get("type") == "Ride" and sport.get("eftp"):
                return round(sport["eftp"])
    return fallback


def fetch_wellness_history(client, days=42):
    today = date.today()
    oldest = today - timedelta(days=days)
    records = client.get_wellness(oldest.isoformat(), today.isoformat())
    return [r for r in records if r.get("ctl") is not None]


def recent_sleep_hours(records, days=7):
    recent = records[-days:]
    secs = [r["sleepSecs"] for r in recent if r.get("sleepSecs") is not None]
    return (sum(secs) / len(secs)) / 3600 if secs else None


def classify_form(tsb, sleep_hours):
    if tsb is None:
        return "neutral"
    if tsb < -20 or (sleep_hours is not None and sleep_hours < 6):
        return "muede"
    if tsb > 5:
        return "frisch"
    return "neutral"


def build_sweet_spot_workouts(form):
    if form == "muede":
        return [
            {
                "name": "Sweet Spot - reduziert",
                "steps": [(10, "55-65")] + [(10, "88-93"), (3, "50")] * 2 + [(10, "55-65")],
            },
            {
                "name": "Grundlage locker",
                "steps": [(60, "60-70")],
            },
        ]
    if form == "frisch":
        return [
            {
                "name": "Sweet Spot",
                "steps": [(10, "55-65")] + [(14, "90-95"), (4, "50")] * 3 + [(10, "55-65")],
            },
            {
                "name": "Sweet Spot",
                "steps": [(10, "55-65")] + [(12, "90-95"), (3, "50")] * 4 + [(10, "55-65")],
            },
        ]
    return [
        {
            "name": "Sweet Spot",
            "steps": [(10, "55-65")] + [(12, "88-94"), (3, "50")] * 3 + [(10, "55-65")],
        },
        {
            "name": "Sweet Spot",
            "steps": [(10, "55-65")] + [(10, "88-94"), (3, "50")] * 3 + [(10, "55-65")],
        },
    ]


def steps_to_description(steps):
    return "\n".join(f"- {minutes}m {pct}% FTP" for minutes, pct in steps)


def steps_duration_seconds(steps):
    return sum(minutes for minutes, _ in steps) * 60


def next_workout_dates(count, gap_days=3):
    start = date.today() + timedelta(days=1)
    return [start + timedelta(days=i * gap_days) for i in range(count)]


def run_weekly_review():
    client = IntervalsClient()

    wellness_records = fetch_wellness_history(client)
    ftp = extract_eftp(wellness_records)
    latest = wellness_records[-1] if wellness_records else {}
    ctl = latest.get("ctl")
    atl = latest.get("atl")
    tsb = (ctl - atl) if ctl is not None and atl is not None else None
    sleep_hours = recent_sleep_hours(wellness_records)
    form = classify_form(tsb, sleep_hours)

    sleep_display = f"{sleep_hours:.1f}h" if sleep_hours is not None else "keine Daten"
    print(f"FTP: {ftp}W")
    print(f"CTL (Fitness): {ctl}")
    print(f"ATL (Fatigue): {atl}")
    print(f"TSB (Form): {tsb}")
    print(f"Schlafdauer (7-Tage-Schnitt): {sleep_display}")
    print(f"Einschätzung: {form}\n")

    workouts = build_sweet_spot_workouts(form)
    dates = next_workout_dates(len(workouts))

    print("Vorschlag für die nächsten strukturierten Einheiten:\n")
    for workout, workout_date in zip(workouts, dates):
        duration_min = steps_duration_seconds(workout["steps"]) // 60
        print(f"{workout_date.isoformat()} - {workout['name']} (~{duration_min} min, FTP {ftp}W)")
        print(steps_to_description(workout["steps"]))
        print()

    print(f"Krafttraining-Hinweis: {random.choice(STRENGTH_TIPS)}")
    print(f"Ernährungs-Hinweis: {random.choice(NUTRITION_TIPS)}\n")

    answer = input("Vorschlag in intervals.icu übernehmen? [y/N]: ").strip().lower()
    if answer != "y":
        print("Abgebrochen, es wurde nichts in intervals.icu verändert.")
        return

    for workout, workout_date in zip(workouts, dates):
        event = {
            "category": "WORKOUT",
            "start_date_local": f"{workout_date.isoformat()}T00:00:00",
            "type": "Ride",
            "name": workout["name"],
            "description": steps_to_description(workout["steps"]),
            "moving_time": steps_duration_seconds(workout["steps"]),
        }
        client.create_event(event)
        print(f"Workout für {workout_date.isoformat()} angelegt.")


def main():
    parser = argparse.ArgumentParser(description="Fahrrad-Trainingsplan-Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("review", help="Wöchentlichen Trainingsplan-Review starten")

    args = parser.parse_args()

    if args.command == "review":
        run_weekly_review()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
