![CI](https://github.com/soltyDude/warsaw-beauty-salon-explorer/actions/workflows/ci.yml/badge.svg)

# Warsaw Beauty Salon Explorer

## Live Demo

Frontend: https://warsaw-beauty-salon-explorer-beta.vercel.app

Backend API: https://warsaw-beauty-salon-explorer-production.up.railway.app/api/stats

---

## Overview

Warsaw Beauty Salon Explorer is a full-stack application for discovering beauty salons, hairdressers, barbershops, nail studios, and wellness services across Warsaw.

The project was built as a technical assignment for the SumUp Warsaw Accelerator Program and demonstrates the complete data engineering and software development pipeline.

The application currently contains **2,716 real businesses** collected from OpenStreetMap and distributed across all 18 Warsaw districts.

---

## Features

### Data Collection & Processing

- OpenStreetMap + Overpass API data source
- 2,716 real beauty-related businesses
- Geographic district assignment
- Data normalization and validation
- Duplicate detection and cleanup
- Automated import pipeline written in Python

### Backend API

- Spring Boot 3 + Java 21
- RESTful architecture
- Salon listing endpoint
- Filtering by district
- Filtering by service type
- Salon detail endpoint
- Statistics endpoint
- PATCH updates with persistence
- Integration tests using MockMvc

### Frontend

- React 18 + TypeScript
- Search by salon name
- District filtering
- Service filtering
- Sorting options
- Statistics dashboard
- Editable salon details
- Responsive layout
- Interactive Leaflet map

### Infrastructure

- Dockerized backend
- Dockerized frontend
- Docker Compose support
- GitHub repository
- GitHub Actions CI/CD
- Automated backend testing
- Automated frontend build validation
- Railway deployment
- Vercel deployment
- Automatic cloud deployments

---

## Dataset Statistics

| Metric | Value |
|----------|----------|
| Total salons | 2,716 |
| Districts covered | 18 / 18 |
| Phone numbers | 602 |
| Websites | 391 |
| Services classified | 2,716 |

---

## Architecture

```text
OpenStreetMap (Overpass API)
            │
            ▼
   Python Data Pipeline
   fetch → clean → normalize
            │
            ▼
    salons_clean.json
            │
            ▼
 Spring Boot REST API
            │
            ▼
 React + TypeScript
            │
            ▼
 Leaflet + OpenStreetMap
```

## Tech Stack

| Layer | Technology |
|---------|---------|
| Backend | Java 21, Spring Boot 3 |
| Persistence | H2 Database |
| Frontend | React 18, TypeScript |
| Build Tool | Maven |
| Frontend Build | Vite |
| Maps | Leaflet |
| Data Collection | Python |
| Data Source | OpenStreetMap |
| Deployment | Railway + Vercel |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions |

---

## Running Locally

### Docker

```bash
docker compose build
docker compose up
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:8080
```

### Without Docker

Backend:

```bash
cd backend
mvn spring-boot:run
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

```http
GET    /api/salons
GET    /api/salons/{id}
PATCH  /api/salons/{id}
GET    /api/stats
GET    /api/districts
```

Example:

```bash
curl https://warsaw-beauty-salon-explorer-production.up.railway.app/api/stats
```

---

## Testing

The backend contains integration tests covering:

- salon listing
- district filtering
- salon details
- record updates
- statistics endpoint
- error handling

Run tests:

```bash
cd backend
mvn test
```

---

## Continuous Integration & Deployment

The project uses GitHub Actions to automatically validate and deploy every change.

Pipeline:

```text
Push
 ↓
Backend Tests
 ↓
Frontend Build
 ↓
Deploy
```

Automated checks:

- Spring Boot integration tests
- Frontend production build validation
- Pull Request verification

Deployment targets:

- Railway (Backend API)
- Vercel (Frontend Application)

Every push automatically triggers validation and deployment workflows.

---

## Data Quality

The project prioritizes correctness over completeness.

Missing information is never fabricated.

| Field | Coverage |
|---------|---------|
| Name | 100% |
| Coordinates | 100% |
| District | 100% |
| Services | 100% |
| Phone | ~22% |
| Website | ~14% |
| Rating | Google enrichment prototype |
| Reviews | Google enrichment prototype |
| Price Level | Future enhancement |

---

## Google Places Enrichment

A Google Places API enrichment pipeline was implemented and successfully validated.

The enrichment workflow:

```text
OpenStreetMap Dataset
        ↓
Google Places Search
        ↓
Coordinate Validation
        ↓
Candidate Scoring
        ↓
Data Enrichment
```

Matching criteria:

- business name similarity
- geographic proximity
- district context
- coordinate validation

Additional attributes retrieved from Google Places:

- ratings
- review counts
- websites
- phone numbers
- formatted addresses
- business status

### Pilot Run Results

| Metric | Value |
|---------|---------|
| Salons processed | 20 |
| Successful matches | 18 |
| Match rate | 90% |

The pilot run successfully demonstrated reliable entity matching and enrichment.

Due to Google Places API billing limitations, the enrichment process was validated on a representative sample rather than executed for the entire dataset.

The enrichment pipeline remains available and can be executed on the full dataset once API credits become available.

---

## Production Deployment

| Component | Platform |
|---------|---------|
| Frontend | Vercel |
| Backend | Railway |

Deployment flow:

```text
GitHub
│
├── Vercel
│   └── Frontend
│
└── Railway
    └── Backend
```

Both services redeploy automatically after updates to the main branch.

---

## Future Improvements

### Marker Clustering

Replace individual Leaflet markers with clustering to support displaying all 2,716 salons simultaneously without performance degradation.

### PostgreSQL + PostGIS

Migration from H2 to PostgreSQL for:

- persistent storage
- geospatial queries
- scalability

### Nearby Search

```http
GET /api/salons/nearby
```

using browser geolocation and radius-based filtering.

### Automated Dataset Refresh

Scheduled OpenStreetMap synchronization and automated data refresh workflows.

### Full Google Places Enrichment

Execute enrichment against the complete dataset once production API credits become available.

---

## Author

Developed as part of the SumUp Warsaw Accelerator Program technical assignment.

Built with:

- Java
- Spring Boot
- React
- TypeScript
- Leaflet
- Docker
- Railway
- Vercel
- OpenStreetMap
