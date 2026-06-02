# Warsaw Beauty Salon Explorer

A full-stack application for discovering beauty and hair salons in Warsaw — built as a home assignment for the SumUp Warsaw Accelerator Program.

Covers the complete pipeline: data collection → cleaning → backend API → frontend UI → map visualization → containerized deployment.

---

## Live Stats

| Salons | Districts | Phone numbers | Websites |
|:------:|:---------:|:-------------:|:--------:|
| **2 716** | **18 / 18** | **602** | **391** |

All 18 official Warsaw districts covered. Dataset collected from OpenStreetMap — no mocked or synthetic records.

---

## Screenshots

<img width="1561" height="972" alt="image" src="https://github.com/user-attachments/assets/4cef0362-b265-425a-a31e-5dd8fceb1cf4" />


---

## Features

### Data Collection
- Source: **OpenStreetMap via Overpass API** — free, no API key, community-verified data
- 2 716 real salons with coordinates, addresses, and service types
- Automated deduplication and district assignment via geographic coordinates
- Python pipeline: fetch → clean → normalize → validate → seed

### Backend API
- Full salon listing with filtering by district and service
- Individual salon detail endpoint
- Manual edits via PATCH with persistence
- Dataset statistics endpoint

### Frontend
- Search by name
- Filter by district and service type
- Sortable results
- Interactive OpenStreetMap (Leaflet) with salon pins
- Salon detail view
- Inline editing with save to backend
- Statistics dashboard

> **Map note:** The map renders up to **500 pins** by default for smooth performance with Leaflet. This limit is configurable in `frontend/src/components/SalonMap.tsx` (`.slice(0, 500)`). Raising it is possible but for datasets above ~1 000 visible markers, replacing individual `<Marker>` components with [Leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) gives a significantly better UX — clusters collapse at lower zoom levels and expand on click.

### Infrastructure
- Dockerized — single `docker compose up` to run the full stack

---

## Architecture

```
OpenStreetMap (Overpass API)
            │
            ▼
   Python Data Pipeline
   fetch → clean → normalize → validate
            │
            ▼
    salons_final.json (2 716 records)
            │
            ▼
 Spring Boot 3 — REST API (port 8080)
 H2 in-memory DB, seeded on startup
            │
            ▼
 React + TypeScript Frontend (port 5173)
 Vite, Leaflet, Lucide Icons
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Java 21, Spring Boot 3, Spring Data JPA |
| Database | H2 (in-memory, seeded from JSON) |
| Frontend | React 18, TypeScript, Vite |
| Map | Leaflet.js + OpenStreetMap tiles |
| Data pipeline | Python 3, Overpass API |
| Infrastructure | Docker, Docker Compose |
| Build | Maven |

---

## Quick Start

### Option A — Docker (recommended)

```bash
docker compose build
docker compose up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8080 |

---

### Option B — Local

**Prerequisites:** Java 21+, Maven 3.8+, Node.js 18+

**Backend:**
```bash
cd backend
mvn spring-boot:run
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## API Reference

```
GET   /api/salons          List all salons (supports ?district=X&service=Y)
GET   /api/salons/{id}     Full salon details
PATCH /api/salons/{id}     Update salon fields
GET   /api/stats           Dataset statistics and coverage metrics
```

**Example — filter by district:**
```bash
curl "http://localhost:8080/api/salons?district=Mokotów"
```

**Example — update a record:**
```bash
curl -X PATCH http://localhost:8080/api/salons/42 \
  -H "Content-Type: application/json" \
  -d '{"phone": "+48 123 456 789", "priceRange": "€€"}'
```

---

## Testing

Integration tests cover the core API behaviour using MockMvc with an isolated in-memory database (separate `test` profile, `@BeforeEach` setup):

```
✔ GET /api/salons — returns all salons and supports district filter
✔ GET /api/salons/{id} — returns full salon details
✔ PATCH /api/salons/{id} — persists field updates
✔ GET /api/salons/{id} (missing) — returns 404 with structured error body
```

Run:
```bash
cd backend && mvn test
```

---

## Data Quality

This project prioritizes **correctness over completeness**. Fields unavailable in OpenStreetMap are stored empty rather than populated with potentially inaccurate data.

| Field | Coverage | Notes |
|-------|----------|-------|
| Name | 100% | Required — filtered during collection |
| District | 100% | Mapped via coordinates + OSM admin boundaries |
| Services | 100% | Inferred from shop type tags |
| Coordinates | 100% | Required — filtered during collection |
| Phone | ~22% (602 / 2 716) | OSM community contribution varies by area |
| Website | ~14% (391 / 2 716) | Expected low coverage for OSM beauty data |
| Rating / Reviews | — | Not in OSM; planned via Google Places enrichment |
| Price range | — | Not in OSM; editable via UI |

Low phone/website coverage is an honest reflection of the data source, not a processing gap.

---

## Why OpenStreetMap?

- **Free and open** — no API key, no rate limits for reasonable use
- **Real data** — community-verified, not algorithmically generated
- **Full coverage** — Warsaw is well-mapped; all 18 districts returned results
- **Coordinates included** — enables map display and geographic filtering out of the box
- **Scalable** — same pipeline works for any Polish city with a one-line query change

---

## Scaling to All of Poland

Current query targets Warsaw:
```
area["name"="Warszawa"]["admin_level"="6"]
```

Replacing with:
```
area["name"="Polska"]["admin_level"="2"]
```

returns ~20 000+ salons nationally. Scaling would require:
- PostgreSQL + PostGIS for geospatial queries
- Cursor-based pagination in the API
- Batch processing in the Python pipeline
- Scheduled weekly refresh via GitHub Actions cron or a dedicated job

---

## In Progress: Google Places Enrichment

Google Places API key is obtained and integration is in active development. The current OSM dataset is strong on location data but sparse on ratings, reviews, and photos — Google Places fills exactly that gap.

**Enrichment pipeline:**

```
OSM Salon (name + coordinates)
           │
           ▼
Google Places Text Search
"{name} Warsaw {district}"
           │
           ▼
 Confidence scoring per match
 ├── Geographic distance < 200m  → +0.5
 ├── Name contains / is contained → +0.3
 └── Name exact match (lowercase) → +0.2
           │
     Score ≥ 0.7?
     │             │
    Yes            No
     │             │
     ▼             ▼
  Merge fields   Keep OSM record as-is
  - rating
  - userRatingCount
  - nationalPhoneNumber
  - websiteUri
  - priceLevel (maps to €/€€/€€€)
  - photos (first thumbnail URL)
  - dataSource: "osm+google"
```

Matching uses geographic proximity as the primary signal — name similarity alone is unreliable for salons (many share generic names). Only records where the Places result is within ~200m of the OSM coordinates are considered for merge.

Expected outcome: ratings and review counts for the majority of the 2 716 records currently showing `—`.

---

## What I Would Build Next

### CI/CD via GitHub Actions

Automated pipeline on every push and pull request:

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { java-version: '21', distribution: 'temurin' }
      - run: cd backend && mvn test --no-transfer-progress

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '18' }
      - run: cd frontend && npm ci && npm run build
```

CD extension: on merge to `main`, build and push Docker image to GitHub Container Registry, then trigger a deploy hook on Railway/Render. The whole chain — push code → tests pass → live in ~3 minutes.

---

### "Salons Near Me" Geospatial Search

Replace H2 with PostgreSQL + PostGIS and add a radius endpoint:

```sql
-- Salons within 1 km of a point
SELECT * FROM salons
WHERE ST_DWithin(
  ST_MakePoint(longitude, latitude)::geography,
  ST_MakePoint(:lon, :lat)::geography,
  1000  -- metres
)
ORDER BY ST_Distance(...);
```

Frontend: browser geolocation API → `GET /api/salons/nearby?lat=52.22&lon=21.01&radius=1000`. Pins on the map sorted by walking distance. This is the feature that makes a directory actually useful on mobile.

---

### Automated Data Freshness

Weekly cron job via GitHub Actions that re-runs the Python collection pipeline and opens a PR with the diff — new salons added, closed ones flagged. The team reviews and merges. No stale data, no manual work, full audit trail.

```yaml
on:
  schedule:
    - cron: '0 3 * * 1'  # every Monday at 3am
```

---

### Marker Clustering on the Map

Currently the map renders up to 500 individual pins (configurable in `SalonMap.tsx`). With Leaflet.markercluster, all 2 716 salons can be shown simultaneously — clusters at low zoom, individual pins when zoomed in. One dependency, ~20 lines of code change, significantly better UX at city scale.

---

### Google Places Enrichment Pipeline

Already in progress (see [In Progress](#in-progress-google-places-enrichment) section above). Implementation on the backend side: a Spring Batch job that processes salons in pages of 50, calls the Places API, applies the confidence scoring, and writes merged records back to the database. Adds ratings and review counts to the ~78% of records currently without them.

---

### Production Deployment

| Component | Target | Notes |
|-----------|--------|-------|
| Frontend | Vercel | Auto-deploy from GitHub, CDN, free tier |
| Backend | Railway | Dockerfile-based, free tier, env vars UI |
| Database | PostgreSQL (Railway) | Persistent, replaces H2 |

Docker Compose is already in place — Railway reads it directly.

---

## Author

Built for the SumUp Warsaw Accelerator Program — Software Engineer Intern recruitment assignment.
