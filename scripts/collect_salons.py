from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RAW_SALONS_PATH = RAW_DIR / "salons_raw.json"
RAW_DISTRICTS_PATH = RAW_DIR / "district_boundaries_raw.json"
CLEAN_JSON_PATH = PROCESSED_DIR / "salons_clean.json"
CLEAN_CSV_PATH = PROCESSED_DIR / "salons_clean.csv"
QUALITY_REPORT_PATH = PROCESSED_DIR / "data_quality_report.json"

OVERPASS_URL = os.environ.get("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
WARSAW_BBOX = (52.097, 20.851, 52.368, 21.271)  # south, west, north, east

DISTRICT_NAMES = [
    "Bemowo",
    "Bia\u0142o\u0142\u0119ka",
    "Bielany",
    "Mokot\u00f3w",
    "Ochota",
    "Praga-Po\u0142udnie",
    "Praga-P\u00f3\u0142noc",
    "Rembert\u00f3w",
    "\u015ar\u00f3dmie\u015bcie",
    "Targ\u00f3wek",
    "Ursus",
    "Ursyn\u00f3w",
    "Wawer",
    "Weso\u0142a",
    "Wilan\u00f3w",
    "W\u0142ochy",
    "Wola",
    "\u017boliborz",
]

DISTRICT_CENTERS = {
    "Bemowo": (52.2500, 20.9130),
    "Bia\u0142o\u0142\u0119ka": (52.3200, 20.9750),
    "Bielany": (52.2850, 20.9300),
    "Mokot\u00f3w": (52.1900, 21.0100),
    "Ochota": (52.2120, 20.9720),
    "Praga-Po\u0142udnie": (52.2400, 21.0850),
    "Praga-P\u00f3\u0142noc": (52.2550, 21.0350),
    "Rembert\u00f3w": (52.2600, 21.1600),
    "\u015ar\u00f3dmie\u015bcie": (52.2320, 21.0100),
    "Targ\u00f3wek": (52.2750, 21.0550),
    "Ursus": (52.1950, 20.8850),
    "Ursyn\u00f3w": (52.1400, 21.0450),
    "Wawer": (52.2050, 21.1700),
    "Weso\u0142a": (52.2350, 21.2250),
    "Wilan\u00f3w": (52.1650, 21.0950),
    "W\u0142ochy": (52.1900, 20.9400),
    "Wola": (52.2350, 20.9600),
    "\u017boliborz": (52.2700, 20.9850),
}

FIELDNAMES = [
    "osmId",
    "osmType",
    "name",
    "address",
    "district",
    "phone",
    "website",
    "services",
    "priceRange",
    "rating",
    "reviewsCount",
    "latitude",
    "longitude",
    "source",
    "sourceUrl",
    "openingHours",
]


@dataclass(frozen=True)
class DistrictPolygon:
    name: str
    rings: list[list[tuple[float, float]]]


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect and clean Warsaw salon data from Overpass API.")
    parser.add_argument("--skip-fetch", action="store_true", help="Reuse existing raw JSON files.")
    parser.add_argument("--min-records", type=int, default=100, help="Minimum cleaned records required.")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not args.skip_fetch:
        salons_raw = fetch_overpass(build_salons_query(), "salon POIs")
        write_json(RAW_SALONS_PATH, salons_raw)
        districts_raw = fetch_overpass(build_district_query(), "Warsaw district boundaries")
        write_json(RAW_DISTRICTS_PATH, districts_raw)
    else:
        salons_raw = read_json(RAW_SALONS_PATH)
        districts_raw = read_json(RAW_DISTRICTS_PATH) if RAW_DISTRICTS_PATH.exists() else {"elements": []}

    district_polygons = parse_district_polygons(districts_raw)
    cleaned_before_dedupe = clean_records(salons_raw.get("elements", []), district_polygons)
    cleaned = deduplicate(cleaned_before_dedupe)
    cleaned.sort(key=lambda record: (record.get("district") or "", record["name"].casefold()))

    write_json(CLEAN_JSON_PATH, cleaned)
    write_csv(CLEAN_CSV_PATH, cleaned)

    report = build_quality_report(
        salons_raw=salons_raw,
        cleaned_before_dedupe=cleaned_before_dedupe,
        cleaned=cleaned,
        district_polygons=district_polygons,
    )
    write_json(QUALITY_REPORT_PATH, report)
    print_quality_report(report)

    if report["totalCleaned"] < args.min_records:
        print(
            f"ERROR: cleaned dataset has {report['totalCleaned']} records, "
            f"expected at least {args.min_records}.",
            file=sys.stderr,
        )
        return 1
    if report["recordsMissingName"] > 0:
        print("ERROR: cleaned dataset contains records without names.", file=sys.stderr)
        return 1
    if report["recordsWithCoordinates"] < report["totalCleaned"]:
        print("ERROR: cleaned dataset contains records without coordinates.", file=sys.stderr)
        return 1

    return 0


def build_salons_query() -> str:
    south, west, north, east = WARSAW_BBOX
    bbox = f"({south},{west},{north},{east})"
    selectors = [
        'nwr["shop"="hairdresser"]',
        'nwr["shop"="beauty"]',
        'nwr["shop"="cosmetics"]',
        'nwr["shop"="massage"]',
        'nwr["shop"="nail_salon"]',
        'nwr["amenity"="spa"]',
        'nwr["leisure"="spa"]',
        'nwr["craft"="beautician"]',
        'nwr["craft"="nails"]',
        'nwr["beauty"]',
        'nwr["hairdresser"]',
    ]
    body = "\n  ".join(f"{selector}{bbox};" for selector in selectors)
    return f"""
[out:json][timeout:180];
(
  {body}
);
out center tags;
"""


def build_district_query() -> str:
    south, west, north, east = WARSAW_BBOX
    bbox = f"({south},{west},{north},{east})"
    escaped_names = "|".join(re.escape(name) for name in DISTRICT_NAMES)
    return f"""
[out:json][timeout:180];
(
  relation["boundary"="administrative"]["name"~"^({escaped_names})$"]{bbox};
);
out geom;
"""


def fetch_overpass(query: str, label: str) -> dict[str, Any]:
    payload = urllib.parse.urlencode({"data": query}).encode("utf-8")
    request = urllib.request.Request(
        OVERPASS_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "warsaw-beauty-salon-explorer/1.0",
        },
        method="POST",
    )

    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            print(f"Fetching {label} from Overpass (attempt {attempt})...")
            with urllib.request.urlopen(request, timeout=240) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < 3:
                time.sleep(5 * attempt)

    raise RuntimeError(f"Failed to fetch {label} from Overpass: {last_error}") from last_error


def clean_records(elements: list[dict[str, Any]], district_polygons: list[DistrictPolygon]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for element in elements:
        tags = element.get("tags") or {}
        name = clean_text(first_text(tags, "name", "brand", "operator"))
        latitude, longitude = extract_coordinates(element)
        if not name or latitude is None or longitude is None:
            continue
        if not is_inside_warsaw_bbox(latitude, longitude):
            continue

        address = build_address(tags)
        phone = normalize_phone(first_text(tags, "contact:phone", "phone", "mobile"))
        website = normalize_website(first_text(tags, "contact:website", "website", "url"))
        services = build_services(tags)
        district = map_district(latitude, longitude, tags, district_polygons)
        osm_type = element.get("type")
        osm_id = element.get("id")

        records.append(
            {
                "osmId": osm_id,
                "osmType": osm_type,
                "name": name,
                "address": address,
                "district": district,
                "phone": phone,
                "website": website,
                "services": services,
                "priceRange": normalize_price_range(tags),
                "rating": None,
                "reviewsCount": None,
                "latitude": round(latitude, 7),
                "longitude": round(longitude, 7),
                "source": "OpenStreetMap / Overpass API",
                "sourceUrl": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
                "openingHours": clean_text(first_text(tags, "opening_hours")),
            }
        )
    return records


def extract_coordinates(element: dict[str, Any]) -> tuple[float | None, float | None]:
    if "lat" in element and "lon" in element:
        return float(element["lat"]), float(element["lon"])
    center = element.get("center")
    if isinstance(center, dict) and "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None, None


def first_text(tags: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = tags.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def build_address(tags: dict[str, Any]) -> str | None:
    full = clean_text(first_text(tags, "addr:full"))
    if full:
        return full

    street = clean_text(first_text(tags, "addr:street", "addr:place"))
    house_number = clean_text(first_text(tags, "addr:housenumber"))
    postcode = clean_text(first_text(tags, "addr:postcode"))
    city = clean_text(first_text(tags, "addr:city"))

    line_1 = " ".join(part for part in [street, house_number] if part)
    line_2 = " ".join(part for part in [postcode, city] if part)
    address = ", ".join(part for part in [line_1, line_2] if part)
    return address or None


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    value = re.split(r"[;/|]", value)[0]
    value = value.removeprefix("tel:")
    value = re.sub(r"[^0-9+]", "", value)
    if value.startswith("00"):
        value = "+" + value[2:]
    if value.startswith("48") and len(value) == 11:
        value = "+" + value
    if value.startswith("0") and len(value) == 10:
        value = "+48" + value[1:]
    if len(value) == 9 and value.isdigit():
        value = "+48" + value
    if not re.fullmatch(r"\+?[0-9]{7,15}", value):
        return None
    return value


def normalize_website(value: str | None) -> str | None:
    if not value:
        return None
    value = re.split(r"\s+", value.strip())[0].rstrip(".,")
    if "@" in value and not value.startswith(("http://", "https://")):
        return None
    if not value.startswith(("http://", "https://")):
        value = "https://" + value
    parsed = urllib.parse.urlparse(value)
    if not parsed.netloc or "." not in parsed.netloc:
        return None
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    rebuilt = urllib.parse.urlunparse((parsed.scheme.lower(), netloc, path, "", "", ""))
    return rebuilt


def build_services(tags: dict[str, Any]) -> str:
    services: list[str] = []
    add_service(services, tags.get("shop"), {
        "hairdresser": "Hairdresser",
        "beauty": "Beauty salon",
        "cosmetics": "Cosmetics",
        "massage": "Massage",
        "nail_salon": "Nail salon",
    })
    add_service(services, tags.get("amenity"), {"spa": "Spa"})
    add_service(services, tags.get("leisure"), {"spa": "Spa"})
    add_service(services, tags.get("craft"), {
        "beautician": "Beautician",
        "nails": "Nail salon",
        "hairdresser": "Hairdresser",
    })

    beauty_tag = clean_text(str(tags.get("beauty"))) if tags.get("beauty") else None
    if beauty_tag and beauty_tag.lower() not in {"yes", "salon"}:
        services.append(beauty_tag.replace("_", " ").title())

    hairdresser_tag = clean_text(str(tags.get("hairdresser"))) if tags.get("hairdresser") else None
    if hairdresser_tag and hairdresser_tag.lower() not in {"yes", "salon"}:
        services.append(hairdresser_tag.replace("_", " ").title())

    deduped = list(dict.fromkeys(services))
    return "; ".join(deduped) if deduped else "Beauty services"


def add_service(services: list[str], raw_value: Any, mapping: dict[str, str]) -> None:
    if not isinstance(raw_value, str):
        return
    for part in re.split(r"[;,]", raw_value):
        service = mapping.get(part.strip().lower())
        if service:
            services.append(service)


def normalize_price_range(tags: dict[str, Any]) -> str:
    raw = first_text(tags, "price_range", "payment:price_range")
    return clean_text(raw) or "Unknown"


def parse_district_polygons(raw: dict[str, Any]) -> list[DistrictPolygon]:
    rings_by_name: dict[str, list[list[tuple[float, float]]]] = {}
    for element in raw.get("elements", []):
        tags = element.get("tags") or {}
        name = tags.get("name")
        if name not in DISTRICT_NAMES:
            continue
        rings = relation_to_rings(element)
        if rings:
            rings_by_name.setdefault(name, []).extend(rings)
    return [DistrictPolygon(name=name, rings=rings_by_name[name]) for name in DISTRICT_NAMES if name in rings_by_name]


def relation_to_rings(element: dict[str, Any]) -> list[list[tuple[float, float]]]:
    segments: list[list[tuple[float, float]]] = []
    for member in element.get("members", []):
        if member.get("role") != "outer":
            continue
        geometry = member.get("geometry") or []
        points = [(float(point["lon"]), float(point["lat"])) for point in geometry if "lat" in point and "lon" in point]
        if len(points) > 1:
            segments.append(points)

    rings: list[list[tuple[float, float]]] = []
    while segments:
        ring = segments.pop(0)
        changed = True
        while changed:
            changed = False
            for index, segment in enumerate(segments):
                stitched = stitch_segments(ring, segment)
                if stitched is not None:
                    ring = stitched
                    segments.pop(index)
                    changed = True
                    break
        if not same_point(ring[0], ring[-1]):
            ring.append(ring[0])
        if len(ring) >= 4:
            rings.append(ring)
    if not rings:
        bounds_ring = bounds_to_ring(element.get("bounds"))
        if bounds_ring:
            rings.append(bounds_ring)
    return rings


def bounds_to_ring(bounds: Any) -> list[tuple[float, float]] | None:
    if not isinstance(bounds, dict):
        return None
    try:
        min_lat = float(bounds["minlat"])
        min_lon = float(bounds["minlon"])
        max_lat = float(bounds["maxlat"])
        max_lon = float(bounds["maxlon"])
    except (KeyError, TypeError, ValueError):
        return None
    return [
        (min_lon, min_lat),
        (max_lon, min_lat),
        (max_lon, max_lat),
        (min_lon, max_lat),
        (min_lon, min_lat),
    ]


def stitch_segments(
    ring: list[tuple[float, float]],
    segment: list[tuple[float, float]],
) -> list[tuple[float, float]] | None:
    if same_point(ring[-1], segment[0]):
        return ring + segment[1:]
    if same_point(ring[-1], segment[-1]):
        return ring + list(reversed(segment[:-1]))
    if same_point(ring[0], segment[-1]):
        return segment[:-1] + ring
    if same_point(ring[0], segment[0]):
        return list(reversed(segment[1:])) + ring
    return None


def same_point(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return round(a[0], 7) == round(b[0], 7) and round(a[1], 7) == round(b[1], 7)


def map_district(
    latitude: float,
    longitude: float,
    tags: dict[str, Any],
    district_polygons: list[DistrictPolygon],
) -> str:
    point = (longitude, latitude)
    for district in district_polygons:
        if any(point_in_polygon(point, ring) for ring in district.rings):
            return district.name

    tagged = clean_text(first_text(tags, "addr:district", "is_in:suburb", "addr:suburb"))
    if tagged:
        normalized = normalize_for_match(tagged)
        for district_name in DISTRICT_NAMES:
            if normalized == normalize_for_match(district_name):
                return district_name

    return nearest_district(latitude, longitude)


def point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, current in enumerate(polygon):
        xi, yi = current
        xj, yj = polygon[j]
        intersects = (yi > y) != (yj > y) and x < ((xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def nearest_district(latitude: float, longitude: float) -> str:
    return min(
        DISTRICT_CENTERS,
        key=lambda name: haversine_meters(latitude, longitude, DISTRICT_CENTERS[name][0], DISTRICT_CENTERS[name][1]),
    )


def deduplicate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    for record in records:
        duplicate_index = find_duplicate(record, deduped)
        if duplicate_index is None:
            deduped.append(record)
        else:
            deduped[duplicate_index] = merge_records(deduped[duplicate_index], record)
    return deduped


def find_duplicate(record: dict[str, Any], records: list[dict[str, Any]]) -> int | None:
    record_name = normalize_for_match(record["name"])
    record_address = normalize_for_match(record.get("address") or "")
    record_phone = record.get("phone")

    for index, candidate in enumerate(records):
        candidate_name = normalize_for_match(candidate["name"])
        candidate_address = normalize_for_match(candidate.get("address") or "")
        candidate_phone = candidate.get("phone")
        distance = haversine_meters(
            record["latitude"],
            record["longitude"],
            candidate["latitude"],
            candidate["longitude"],
        )

        if record_phone and candidate_phone and record_phone == candidate_phone:
            return index
        if record_name == candidate_name and record_address and record_address == candidate_address:
            return index
        if record_name == candidate_name and distance <= 35:
            return index
    return None


def merge_records(preferred: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    left_score = completeness_score(preferred)
    right_score = completeness_score(other)
    base, filler = (preferred.copy(), other) if left_score >= right_score else (other.copy(), preferred)
    for key in FIELDNAMES:
        if base.get(key) in (None, "") and filler.get(key) not in (None, ""):
            base[key] = filler[key]
    return base


def completeness_score(record: dict[str, Any]) -> int:
    return sum(1 for key in FIELDNAMES if record.get(key) not in (None, ""))


def normalize_for_match(value: str) -> str:
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


def is_inside_warsaw_bbox(latitude: float, longitude: float) -> bool:
    south, west, north, east = WARSAW_BBOX
    return south <= latitude <= north and west <= longitude <= east


def build_quality_report(
    salons_raw: dict[str, Any],
    cleaned_before_dedupe: list[dict[str, Any]],
    cleaned: list[dict[str, Any]],
    district_polygons: list[DistrictPolygon],
) -> dict[str, Any]:
    total = len(cleaned)
    district_known = sum(1 for record in cleaned if record.get("district") and record.get("district") != "Unknown")
    report = {
        "source": "OpenStreetMap via Overpass API",
        "overpassUrl": OVERPASS_URL,
        "totalCollected": len(salons_raw.get("elements", [])),
        "totalCleanedBeforeDedupe": len(cleaned_before_dedupe),
        "totalCleaned": total,
        "totalDeduplicated": len(cleaned_before_dedupe) - total,
        "districtBoundaryPolygons": len(district_polygons),
        "districtCoveragePercent": round((district_known / total) * 100, 2) if total else 0,
        "recordsWithAddress": count_present(cleaned, "address"),
        "recordsWithPhone": count_present(cleaned, "phone"),
        "recordsWithWebsite": count_present(cleaned, "website"),
        "recordsWithRating": count_present(cleaned, "rating"),
        "recordsWithCoordinates": sum(
            1 for record in cleaned if record.get("latitude") is not None and record.get("longitude") is not None
        ),
        "recordsMissingName": sum(1 for record in cleaned if not record.get("name")),
        "districtCounts": district_counts(cleaned),
        "files": {
            "rawSalons": str(RAW_SALONS_PATH.relative_to(ROOT)),
            "rawDistricts": str(RAW_DISTRICTS_PATH.relative_to(ROOT)),
            "cleanJson": str(CLEAN_JSON_PATH.relative_to(ROOT)),
            "cleanCsv": str(CLEAN_CSV_PATH.relative_to(ROOT)),
        },
    }
    return report


def count_present(records: list[dict[str, Any]], key: str) -> int:
    return sum(1 for record in records if record.get(key) not in (None, ""))


def district_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        district = record.get("district") or "Unknown"
        counts[district] = counts.get(district, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
    tmp_path.replace(path)


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)
    tmp_path.replace(path)


def print_quality_report(report: dict[str, Any]) -> None:
    print("\nData quality report")
    print("-------------------")
    for key in [
        "totalCollected",
        "totalCleanedBeforeDedupe",
        "totalCleaned",
        "totalDeduplicated",
        "districtBoundaryPolygons",
        "districtCoveragePercent",
        "recordsWithAddress",
        "recordsWithPhone",
        "recordsWithWebsite",
        "recordsWithRating",
    ]:
        print(f"{key}: {report[key]}")


if __name__ == "__main__":
    raise SystemExit(main())
