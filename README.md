# RootCause — Smart Guided Troubleshooting Engine

Samsung PRISM Generative AI Hackathon 2026–27 — Theme 02

Team: rootcause · VIT Vellore

Members
- Dev Raj — 24BDS0080
- Sarang Raj — 24BDS0091
- Antony Roy — 24BCE0920

## Problem
Customers describe symptoms in vague language. RootCause converts that complaint into a structured troubleshooting plan with ordered steps and exact in-app Settings deeplinks.

## Pipeline
Query enrichment → SIIS retrieval → structured step extraction → catalog deeplink mapping → contract validation → intent-aware cache.

## API
POST /v1/troubleshoot
Request example: {"query":"My screen is laggy and touch inputs are delayed."}

GET /health
GET /metrics

## Run
pip install -r requirements.txt
uvicorn app.main:app --reload

Docker:
docker build -t rootcause .
docker run --rm -p 8000:8000 rootcause

## Data
The starter SIIS cases, deeplink catalog, test inputs and sample output are included under data/. Actionable URIs are accepted only when present in the supplied catalog. HTTP URLs are rejected by the final hygiene pass.

## Demo
The UI is in static/index.html. The 5-minute flow is in docs/DEMO_SCRIPT.md.

## Submission
See docs/SUBMISSION_CHECKLIST.md. The hackathon requires the final judging tag PRISM_GENAI_HACKATHON_Y2026 on the final commit, with referenced submission artifacts included in that tagged commit.
