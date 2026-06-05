from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

MAIN_FILE = ROOT / "data" / "processed" / "salons_clean.json"
ENRICHED_FILE = ROOT / "data" / "processed" / "salons_enriched_sample.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    salons = load_json(MAIN_FILE)
    enriched = load_json(ENRICHED_FILE)

    enriched_by_osm_id = {
        item["osmId"]: item
        for item in enriched
        if item.get("googleMatch")
    }

    updated = 0

    for salon in salons:
        google = enriched_by_osm_id.get(salon["osmId"])

        if not google:
            continue

        if google.get("googleRating") is not None:
            salon["rating"] = google["googleRating"]

        if google.get("googleReviewsCount") is not None:
            salon["reviewsCount"] = google["googleReviewsCount"]

        if not salon.get("phone") and google.get("googlePhone"):
            salon["phone"] = google["googlePhone"]

        if not salon.get("website") and google.get("googleWebsite"):
            salon["website"] = google["googleWebsite"]

        if not salon.get("address") and google.get("googleFormattedAddress"):
            salon["address"] = google["googleFormattedAddress"]

        updated += 1

    save_json(MAIN_FILE, salons)

    print(f"Updated {updated} salons")


if __name__ == "__main__":
    main()