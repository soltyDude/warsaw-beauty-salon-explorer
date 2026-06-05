from __future__ import annotations

import argparse
import difflib
import json
import math
import os
import re
import time
import unicodedata
import urllib.parse
import urllib.request
import requests
from pathlib import Path
from typing import Any


GOOGLE_API_KEY = os.environ["GOOGLE_PLACES_API_KEY"]
BASE_URL = "https://places.googleapis.com/v1"
SEARCH_URL = f"{BASE_URL}/places:searchText"

ROOT = Path(__file__).resolve().parents[1]
INPUT_DEFAULT = ROOT / "data" / "processed" / "salons_clean.json"
OUTPUT_DEFAULT = ROOT / "data" / "processed" / "salons_enriched_sample.json"

FIELD_MASK_SEARCH = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.primaryType",
    "places.businessStatus",
])

FIELD_MASK_DETAILS = ",".join([
    "id",
    "displayName",
    "formattedAddress",
    "location",
    "nationalPhoneNumber",
    "internationalPhoneNumber",
    "websiteUri",
    "rating",
    "userRatingCount",
    "priceLevel",
    "currentOpeningHours",
    "businessStatus",
])

def main() -> int:
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUTPUT_DEFAULT)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=0.25)
    args = parser.parse_args()

    salons = json.loads(args.input.read_text(encoding="utf-8"))
    sample = salons[: args.limit]

    results: list[dict[str, Any]] = []
    matched = 0

    for idx, salon in enumerate(sample, start=1):
        print(f"[{idx}/{len(sample)}] {salon.get('name')}")

        search_result = search_place(salon)
        if not search_result:
            print("  -> no search result")
            results.append({**salon, "googleMatch": None})
            continue

        details = fetch_details(search_result["id"])
        if not details:
            print("  -> no details")
            results.append({**salon, "googleMatch": None})
            continue

        merged = merge_google_fields(salon, search_result, details)
        results.append(merged)
        matched += 1
        print(
            f"  -> matched: {details.get('displayName', {}).get('text')} | "
            f"rating={details.get('rating')} | reviews={details.get('userRatingCount')}"
        )
        time.sleep(args.sleep)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\nDone")
    print(f"Matched {matched}/{len(sample)}")
    print(f"Saved to {args.output}")
    return 0

def _build_search_queries(name: str, district: str | None) -> list[str]:
    queries: list[str] = []
    safe_name = name.strip()
    safe_district = (district or "").strip()

    candidates = [
        f"{safe_name} {safe_district} Warsaw",
        f"{safe_name} Warsaw",
        f"{safe_name} {safe_district}",
        safe_name,
    ]

    seen: set[str] = set()
    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate and candidate not in seen:
            seen.add(candidate)
            queries.append(candidate)

    return queries


def search_place(salon: dict[str, Any]) -> dict[str, Any] | None:
    name = (salon.get("name") or "").strip()
    district = (salon.get("district") or "").strip()
    lat = salon.get("latitude")
    lon = salon.get("longitude")

    if not GOOGLE_API_KEY:
        print("ERROR: GOOGLE_PLACES_API_KEY is missing")
        return None

    queries = [
        f"{name} {district} Warsaw",
        f"{name} Warsaw",
        f"{name} {district}",
        name,
    ]

    seen: set[str] = set()
    queries = [q for q in queries if q and not (q in seen or seen.add(q))]

    print("\n" + "=" * 100)
    print("SALON")
    print("Name:", name)
    print("District:", district)
    print("Latitude:", lat)
    print("Longitude:", lon)
    print("API key prefix:", GOOGLE_API_KEY[:12])
    print("API key length:", len(GOOGLE_API_KEY))
    print("Search URL:", SEARCH_URL)
    print("=" * 100)

    best_place = None
    best_score = -1.0

    for query in queries:
        payload: dict[str, Any] = {
            "textQuery": query,
            "languageCode": "en",
            "regionCode": "pl",
        }

        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            payload["locationBias"] = {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lon,
                    },
                    "radius": 800.0,
                }
            }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": FIELD_MASK_SEARCH,
        }

        print("\n")
        print("-" * 100)
        print("QUERY:", query)
        print("-" * 100)

        print("\nHEADERS:")
        print("Content-Type:", headers["Content-Type"])
        print("X-Goog-Api-Key:", GOOGLE_API_KEY[:12] + "...")
        print("X-Goog-FieldMask:", FIELD_MASK_SEARCH)

        print("\nPAYLOAD:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        try:
            response = requests.post(
                SEARCH_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
        except Exception as exc:
            print("\nREQUEST FAILED")
            print(type(exc).__name__)
            print(str(exc))
            continue

        print("\nRESPONSE STATUS:")
        print(response.status_code)

        print("\nRESPONSE HEADERS:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")

        print("\nRESPONSE BODY:")
        print(response.text[:5000])

        if response.status_code == 403:
            print("\n403 PERMISSION_DENIED")
            print("Query:", query)
            print("FieldMask:", FIELD_MASK_SEARCH)
            continue

        if response.status_code == 429:
            print("\n429 RATE LIMITED")
            time.sleep(2)
            continue

        if not response.ok:
            print("\nHTTP ERROR")
            continue

        try:
            body = response.json()
        except Exception as exc:
            print("\nJSON PARSE ERROR")
            print(type(exc).__name__)
            print(str(exc))
            continue

        places = body.get("places") or []

        print("\nPLACES FOUND:", len(places))

        if not places:
            continue

        for place in places[:5]:
            try:
                score = score_candidate(salon, place)
            except Exception as exc:
                print("SCORING ERROR:", exc)
                continue

            display_name = (
                place.get("displayName", {})
                .get("text", "<unknown>")
            )

            print(
                f"Candidate: {display_name} | score={score:.3f}"
            )

            if score > best_score:
                best_score = score
                best_place = place

        if best_place and best_score >= 0.45:
            print(
                f"\nBEST MATCH FOUND score={best_score:.3f}"
            )
            return best_place

        if place.get("businessStatus") == "CLOSED_PERMANENTLY":
            print(f"  Skipping CLOSED_PERMANENTLY: {place.get('displayName', {}).get('text')}")
            continue

    print("\nNO MATCH FOUND")
    return None

def fetch_details(place_id: str) -> dict[str, Any] | None:
    url = f"{BASE_URL}/places/{urllib.parse.quote(place_id)}"
    headers = {
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": FIELD_MASK_DETAILS,
    }

    try:
        response = requests.get(url, headers=headers, timeout=60)
    except Exception as exc:
        print(f"  fetch_details request failed: {exc}")
        return None

    if not response.ok:
        print(f"  fetch_details error: {response.status_code} {response.text[:200]}")
        return None

    return response.json()

def merge_google_fields(
    salon: dict[str, Any],
    search_place: dict[str, Any],
    details: dict[str, Any],
) -> dict[str, Any]:
    location = details.get("location") or {}
    display_name = details.get("displayName") or {}

    google_price_level = details.get("priceLevel")
    google_price_range = price_level_to_range(google_price_level)

    return {
        **salon,
        "googlePlaceId": details.get("id"),
        "googleName": display_name.get("text"),
        "googleFormattedAddress": details.get("formattedAddress"),
        "googlePhone": details.get("nationalPhoneNumber") or details.get("internationalPhoneNumber"),
        "googleWebsite": details.get("websiteUri"),
        "googleRating": details.get("rating"),
        "googleReviewsCount": details.get("userRatingCount"),
        "googlePriceLevel": google_price_level,
        "googlePriceRange": google_price_range,
        "googleBusinessStatus": details.get("businessStatus"),
        "googleLatitude": location.get("latitude"),
        "googleLongitude": location.get("longitude"),
        "googleMatch": {
            "searchPlaceId": search_place.get("id"),
            "searchName": (search_place.get("displayName") or {}).get("text"),
        },
    }

def score_candidate(salon: dict[str, Any], place: dict[str, Any]) -> float:
    name = salon.get("name") or ""
    district = salon.get("district") or ""
    lat = salon.get("latitude")
    lon = salon.get("longitude")

    place_name = (place.get("displayName") or {}).get("text") or ""
    place_location = place.get("location") or {}
    place_lat = place_location.get("latitude")
    place_lon = place_location.get("longitude")

    name_score = difflib.SequenceMatcher(
        None,
        normalize(name),
        normalize(place_name),
    ).ratio()

    district_score = 0.15 if district and normalize(district) in normalize(place_name) else 0.0
    distance_score = 0.0
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and isinstance(place_lat, (int, float)) and isinstance(place_lon, (int, float)):
        distance_m = haversine_meters(lat, lon, place_lat, place_lon)
        distance_score = max(0.0, 1.0 - (distance_m / 500.0))

    return (name_score * 0.7) + (district_score * 0.15) + (distance_score * 0.15)

def price_level_to_range(price_level: Any) -> str | None:
    mapping = {
        "PRICE_LEVEL_FREE": "Free",
        "PRICE_LEVEL_INEXPENSIVE": "$",
        "PRICE_LEVEL_MODERATE": "$$",
        "PRICE_LEVEL_EXPENSIVE": "$$$",
        "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$",
    }
    return mapping.get(str(price_level)) if price_level is not None else None

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.casefold()
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value

def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

if __name__ == "__main__":
    raise SystemExit(main())