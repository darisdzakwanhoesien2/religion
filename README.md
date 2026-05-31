# religion

This repo contains a small Streamlit app that parses bullet-style Surah summaries into structured JSON, validates ayah coverage, and (optionally) combines multiple JSON outputs to compute missing ayah ranges.

## Identify bugs, errors, or broken logic

Issues found and addressed:

- **Ayah coverage logic breaks with malformed sections**: `find_missing_ranges` assumed `start_ayah <= end_ayah` and that values were in-bounds. With reversed ranges (e.g. `start_ayah=5, end_ayah=3`) it could produce incorrect/duplicated missing ranges.
- **Potential crash surface from malformed section entries**: one bad section dict could previously raise `KeyError` / `ValueError` in coverage computation.
- **Minor code hygiene**: an unused import existed in `pages/1.py`; JSON path helpers were a bit inconsistent about accepting `Path` objects.

## Fix any issues you find

Fixes implemented:

- `validators/ayah_coverage.py` now **normalizes coverage ranges** before computing gaps:
  - swaps reversed `start/end`,
  - clamps ranges to `[1, total_ayah]`,
  - skips malformed entries instead of crashing.
- `parsers/surah_summary_parser.py` now **normalizes reversed verse ranges** during parsing.
- `utils/file_io.py` now consistently accepts `str` or `pathlib.Path` for JSON paths.

## Clean up the code (remove redundancy, improve readability)

Cleanup/refactors:

- Split coverage normalization into a small helper (`_normalize_covered_ranges`) to keep `find_missing_ranges` readable and testable.
- Removed an unused import in `pages/1.py`.
- Minor import ordering/tidy in `app.py`.

## Add inline comments where the logic is complex

Inline comments were added where the behavior is non-obvious or defensive:

- In `validators/ayah_coverage.py` (normalization rules and why malformed entries are skipped).
- In `app.py` / `pages/1.py` (why missing ranges are computed and that the helper is forgiving).

## Return the fixed version with a summary of what was changed and why

Summary (what/why):

- **More robust missing-range calculation**: prevents incorrect output when section ranges are reversed or out of bounds, and avoids UI breakage from a single malformed section.
- **More forgiving parsing**: makes `parse_sections` resilient to accidental reversed verse ranges.
- **Small readability improvements**: reduces redundancy and makes the code easier to maintain.

## How to run

Prereqs:

- Python 3.12+
- `streamlit` installed (and any other dependencies you use in your environment)

Run the main parser UI:

```bash
streamlit run app.py
```

Run the multi-JSON coverage page:

```bash
streamlit run app.py
```

Then open the “pages” navigation and select `1` (Surah Coverage).

---

# Project Documentation

## 1) Project Overview

This project provides a simple UI for turning **bullet-style Surah summaries** into **structured JSON** and validating whether the summaries cover the full ayah range for the selected Surah.

It solves a common workflow problem when working with LLM-generated summaries or human-authored outlines:

- You start with semi-structured Markdown bullets (easy to write / generate),
- you need clean structured output (JSON) for downstream use (datasets, analysis, knowledge graphs),
- and you want a fast sanity check for coverage gaps (missing ayah ranges).

Key features:

- Parse Markdown bullets like `* **Verses 1–5 (Theme):** Summary...` into JSON sections.
- Compute **missing ayah ranges** from the parsed sections.
- Save parsed results to `data/parsed/` and download JSON from the UI.
- Combine multiple previously-parsed JSON files for the same Surah and recompute missing ranges (multi-file coverage view).

## 2) Tech Stack

- **Language:** Python 3.12+
- **UI framework:** Streamlit
- **Core libraries:** standard library (`re`, `json`, `datetime`, `pathlib`, `typing`)

## 3) Architecture Overview

The app is split into small modules with clear responsibilities:

- `app.py` – Streamlit UI for parsing a pasted summary into JSON and saving/downloading it.
- `parsers/surah_summary_parser.py` – Regex-based parser that converts bullet lines into structured `sections`.
- `validators/ayah_coverage.py` – Coverage logic that normalizes section ranges and computes missing ayah intervals.
- `utils/file_io.py` – JSON read/write helpers.
- `pages/1.py` – Streamlit page that loads multiple JSON outputs from `data/parsed/`, combines sections, and recomputes missing ranges.
- `config/surah_map.json` – Surah metadata used by the UI (`surah_number`, `total_ayah`).

Data flow (single-file parse):

1. User selects a Surah (metadata read from `config/surah_map.json`).
2. User pastes bullet-style text into Streamlit.
3. `parse_sections()` extracts `(start_ayah, end_ayah, theme, summary)` per line.
4. `find_missing_ranges()` calculates gaps vs `total_ayah`.
5. The resulting JSON is displayed, saved to `data/parsed/`, and offered as a download.

Data flow (multi-file coverage):

1. User selects multiple JSON files from `data/parsed/`.
2. The app ensures all selected files belong to the same Surah.
3. Sections are combined + sorted, and missing ayah ranges are recomputed.
4. The integrated JSON is displayed and downloadable.

## 4) Installation & Setup

Prerequisites:

- Python 3.12+ available as `python3`
- `pip` available (or another Python package manager)

Steps:

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies.

   This repo does not currently include a `requirements.txt`. The minimal dependency is Streamlit:

   ```bash
   pip install streamlit
   ```

   Optional (recommended) if you want consistent tooling:

   ```bash
   pip install ruff
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

4. Open the Streamlit URL printed in the terminal (usually `http://localhost:8501`).

## 5) Usage Guide

### Parsing a pasted summary

1. Run `streamlit run app.py`.
2. Select a Surah from the dropdown.
3. Paste bullet-style text into the text area.
4. Review:
   - Parsed JSON (`sections`)
   - Missing ayah ranges (if any)
5. The JSON is automatically saved to `data/parsed/<surah_slug>.json` and can also be downloaded.

Accepted line format (one per bullet):

```text
* **Verses 1–5 (The Righteous):** The Surah begins...
```

Notes:

- The dash can be `–` or `-`.
- If a range is accidentally reversed (e.g. `Verses 5–3`) the parser/validator will normalize it to `3–5`.
- Lines that don’t match the expected format are ignored.

### Multi-JSON coverage (combining outputs)

1. Run `streamlit run app.py`.
2. In the sidebar/pages navigation, open page `1` (“Surah Coverage (Multi-JSON)”).
3. Select one or more JSON files from `data/parsed/`.
4. The page will:
   - combine sections,
   - sort them by `(start_ayah, end_ayah)`,
   - compute missing ayah ranges,
   - and provide an integrated JSON download.

## 6) API Reference (if applicable)

This project does not expose a web API with HTTP endpoints. The “API surface” is the Python functions used internally:

- `parsers.surah_summary_parser.parse_sections(raw_text: str) -> list[dict]`
  - Input: raw pasted text (multi-line string)
  - Output: list of section dicts:
    - `start_ayah` (int)
    - `end_ayah` (int)
    - `theme` (str)
    - `summary` (str)

- `validators.ayah_coverage.find_missing_ranges(sections: Iterable[dict], total_ayah: int) -> list[tuple[int, int]]`
  - Input: `sections` list + total ayah count
  - Output: list of inclusive missing ranges: `[(start, end), ...]`
  - Behavior: normalizes reversed/out-of-bound ranges and skips malformed entries defensively.

## 7) Environment Variables

No `.env` configuration is required by the current codebase.

If you want to add environment-driven configuration later, common candidates would be:

- `RELIGION_DATA_DIR` – override the default `data/` path
- `RELIGION_CONFIG_PATH` – override `config/surah_map.json`

## 8) Contributing Guide

Contributions are welcome. Suggested workflow:

1. Create a feature branch.
2. Keep changes focused and add/update documentation in `README.md` when behavior changes.
3. Run quick checks locally:

   - Syntax check:
     ```bash
     python3 -m compileall -q .
     ```
   - (Optional) Lint/format:
     ```bash
     ruff check .
     ruff format .
     ```

4. Open a PR describing:
   - what changed,
   - why,
   - how to test it.

## 9) License

No license file is currently included in this repository.

If you want, tell me which license you prefer (commonly MIT, Apache-2.0, or GPL-3.0) and I can add a `LICENSE` file and update this section accordingly.

---

# Scaling Guide

This project is currently a single-process Streamlit app that reads/writes JSON on local disk. Scaling it means separating concerns (UI vs API vs storage), adding shared persistence, and making compute/stateless layers horizontally scalable.

## 1) Current Bottlenecks (What breaks first under load?)

- **Single-process Streamlit runtime**: Streamlit apps typically run as one Python process per container/VM. Under concurrent usage, CPU-bound parsing and repeated JSON serialization will increase latency quickly.
- **Local filesystem as a “database”** (`data/parsed/`): Writing files locally is not safe for multi-instance deployments (instances won’t share state). It can also become slow with large directories and frequent reads.
- **No request isolation / job queue**: If you later add heavier processing (e.g., embeddings, NLP enrichment), long-running tasks will block the UI thread.
- **Cold starts and memory**: If deployed on serverless/container auto-scaling, frequent cold starts will increase latency; caching in-process will be wiped on restart.
- **Unvalidated/unbounded inputs**: A very large pasted payload (or many selected JSON files) can cause memory spikes and slow down the app.

## 2) Database Scaling (Indexing, caching, sharding, read replicas)

Today: JSON files on disk.

Recommended next step: move parsed outputs + metadata into a database, and store large blobs separately.

Suggested data model:

- `surah` table: name, number, total_ayah
- `parse_run` table: id, surah_id, created_at, user/session id, input_hash, source (manual/llm), etc.
- `section` table: parse_run_id, start_ayah, end_ayah, theme, summary

Indexing:

- Index `section(surah_id, start_ayah, end_ayah)` or at minimum `(parse_run_id, start_ayah)`
- Index `parse_run(surah_id, created_at)` for listing history
- If you add search, consider full-text indexes on `summary` and `theme`

Caching:

- Cache “surah map” and other static metadata in-memory (Redis) and/or CDN (if served via API).
- Cache computed missing ranges for a given `(surah_id, parse_run_id)` since it’s deterministic.

Read replicas:

- If you introduce analytics or heavy read traffic (search/browse), add a read replica so writes don’t contend with reads.

Sharding:

- Not needed early. If you ever need it, shard by `surah_id` or by `parse_run_id` ranges/tenant, but only after exhausting simpler scaling options.

Blob storage:

- If you want to keep original raw inputs or output JSON snapshots, store them in object storage (S3/GCS/Azure Blob) and reference by URL/key in the DB.

## 3) Backend Scaling (Load balancing, horizontal vs vertical scaling)

Streamlit isn’t designed to be your primary backend at scale. A common evolution path:

1. Keep Streamlit as the UI.
2. Add a separate API service (FastAPI/Flask) for parsing, validation, and persistence.
3. Make the API stateless and scale horizontally behind a load balancer.

Horizontal vs vertical:

- **Vertical scaling** (bigger VM) is simplest for early growth; good until CPU or memory costs get silly.
- **Horizontal scaling** (multiple replicas) is the long-term answer, but requires:
  - shared persistence (DB/object storage),
  - shared cache (Redis),
  - stateless app servers,
  - idempotent job execution.

Load balancing:

- Use a managed L7 load balancer (ALB / GCLB / Azure Application Gateway).
- Terminate TLS at the LB, forward to app containers.

Background jobs:

- For expensive enrichment workflows, use a queue + workers:
  - Redis-backed queue (RQ/Celery) or managed queue (SQS/PubSub/Service Bus).
  - Worker autoscaling separate from web autoscaling.

Rate limiting:

- Add per-IP or per-user request limits at the edge (WAF/CDN) once public.

## 4) Frontend Scaling (CDN, lazy loading, SSR/SSG options)

Today: Streamlit renders the UI server-side and sends deltas to the browser.

If you need a “real” web frontend:

- **CDN**: put static assets behind a CDN (CloudFront/Cloud CDN/Azure CDN).
- **Lazy loading**: paginate and lazy-load large JSON responses; avoid rendering huge `st.json(...)` payloads.
- **SSR/SSG**: if you add marketing/docs pages, use Next.js/Remix/Astro for SSR/SSG and keep the app as a separate “tool” behind auth.
- **Client-side rendering**: for interactive browsing/searching of sections, a React frontend calling an API will scale better than pushing everything through Streamlit.

## 5) Infrastructure (Recommended cloud setup)

Below are pragmatic “good default” stacks. Pick one cloud; avoid multi-cloud early.

### AWS (common default)

- **Compute**: ECS Fargate (containers) or EKS (Kubernetes, later)
- **Load balancer**: ALB
- **Database**: RDS Postgres
- **Cache**: ElastiCache Redis
- **Object storage**: S3
- **Queue**: SQS (and optionally EventBridge for orchestration)
- **Secrets**: Secrets Manager or SSM Parameter Store
- **Observability**: CloudWatch + X-Ray (or Grafana/Prometheus if on EKS)
- **Auth** (optional): Cognito or an external IdP (Auth0/Clerk)

### GCP (great managed services)

- **Compute**: Cloud Run (containers)
- **Load balancer**: Cloud Load Balancing
- **Database**: Cloud SQL Postgres
- **Cache**: Memorystore Redis
- **Object storage**: GCS
- **Queue**: Pub/Sub or Cloud Tasks
- **Secrets**: Secret Manager
- **Observability**: Cloud Logging + Cloud Trace

### Azure (enterprise-friendly)

- **Compute**: Container Apps
- **Load balancer**: Application Gateway / Front Door
- **Database**: Azure Database for PostgreSQL
- **Cache**: Azure Cache for Redis
- **Object storage**: Blob Storage
- **Queue**: Service Bus / Storage Queues
- **Secrets**: Key Vault
- **Observability**: Azure Monitor / Application Insights

## 6) Cost Estimate (very rough)

These are order-of-magnitude estimates assuming:

- A small authenticated web app
- Mostly reads, light parsing compute
- Managed Postgres + Redis (once you add them)
- CDN + load balancer

Actual cost depends heavily on traffic patterns (requests per user per day), payload sizes, and whether you add expensive NLP/LLM steps.

### ~1k users

- Likely **$25–$150/month**
  - 1 small container/VM
  - managed Postgres (small)
  - basic logging/metrics

### ~10k users

- Likely **$150–$800/month**
  - 2–4 app replicas behind a LB
  - larger Postgres instance or storage
  - Redis cache
  - CDN egress starts to matter

### ~100k users

- Likely **$800–$5,000+/month**
  - autoscaling web + workers
  - read replicas for Postgres (or heavier caching)
  - higher egress/CDN costs
  - stronger observability + WAF

If you add LLM calls (summarization/embedding) into the critical path, that will dominate cost and should be isolated behind quotas, async jobs, and caching.

## 7) Roadmap (MVP → production-grade)

MVP (current):

1. Streamlit app parses text → saves JSON locally.

V1 (shared persistence + repeatability):

2. Add `requirements.txt` and basic CI checks (lint + `compileall`).
3. Introduce a Postgres DB for `parse_run` and `section`.
4. Store raw inputs / output snapshots in object storage (S3/GCS/Blob).

V2 (stateless services + horizontal scaling):

5. Split into:
   - UI (Streamlit or web frontend)
   - API (FastAPI) for parsing/validation/persistence
6. Add Redis for caching and rate limiting.
7. Containerize and deploy behind a managed load balancer; run 2+ replicas.

V3 (heavy workloads + reliability):

8. Add a job queue + worker pool for enrichment tasks.
9. Add observability: structured logs, metrics, tracing, alerting.
10. Add auth + RBAC if multi-user; add quotas to protect costs.

V4 (scale + product polish):

11. Add read replicas and/or optimize queries/indexes.
12. Add CDN/WAF at the edge; tune caching.
13. Add backups, disaster recovery, and a documented incident runbook.

---

# Similar Products & Niche Positioning

Below are 10 products in the broader space of **turning unstructured/semi-structured documents into structured data** (and validating/operationalizing it). This project is much smaller and more focused today, but the same patterns apply.

Notes:

- “Tech stack” is only included when it’s publicly known. Many commercial vendors don’t disclose internals.
- “Scale” is described qualitatively unless there are stable, public numbers.

## 1) Similar apps / companies

| Product | What they do | Tech stack (if known) | Business model | Scale | What makes them successful |
|---|---|---|---|---|---|
| **Google Cloud Document AI** | Managed “document AI” service for extracting structured fields from PDFs/images (IDP/OCR + extraction) | Not public (managed GCP service) | Usage-based cloud billing | Very large (major cloud) | Strong accuracy on common doc types, easy integration with GCP ecosystem, enterprise trust/SLAs |
| **Amazon Textract** | Managed OCR + structured extraction for scanned documents and forms | Not public (managed AWS service) | Usage-based cloud billing | Very large (major cloud) | Tight AWS integration, clear “per page” economics, strong infra reliability |
| **Azure AI Document Intelligence (Form Recognizer)** | Managed document extraction with prebuilt + custom models | Not public (managed Azure service) | Usage-based cloud billing | Very large (major cloud) | Enterprise distribution, integrates with Microsoft stack, broad prebuilt models |
| **Diffbot** | “Knowledge as a Service” that extracts structured entities/relations at web scale | Not fully public (ML + KG at scale) | API / enterprise subscription | Large enterprise + developers | Strong focus on knowledge graphs, high leverage for enrichment/search, mature APIs |
| **Rossum** | Intelligent document processing (notably invoices/AP) with human-in-the-loop workflows | Not public | SaaS (enterprise) | Enterprise operations teams | Focus on end-to-end workflow + validation, not just OCR; productized for finance/AP |
| **Nanonets** | Document processing platform (OCR + extraction + workflow steps) | Not public | Usage-based SaaS | Broad SMB → enterprise | Fast time-to-value, flexible workflows, clear pricing structure for automation blocks |
| **Docsumo** | Document AI platform for extraction + validation/workflows | Not public | SaaS tiers (often sales-led for enterprise) | SMB → enterprise | Emphasis on validation and operational workflows, “business-ready” features around extraction |
| **Mindee** | OCR/extraction API with prebuilt endpoints and custom options | Not public (API service) | Subscription plans/credits | Developer-focused SaaS | Simple developer experience (DX), strong API-first approach, predictable plan-based pricing |
| **Label Studio** | Open-source platform to label/annotate data (text/images/audio/etc.) with optional ML-assisted labeling | Open source (implementation details vary by deployment) | OSS + paid/hosted options (varies by provider) | Widely adopted OSS | Big ecosystem, flexible annotation types, teams can own data + workflows |
| **doccano** | Open-source web-based text annotation tool for ML practitioners | Publicly known as Python/Django + web frontend in community docs | OSS (self-hosted) | Widely used in OSS | Lightweight, easy to self-host, focused on practical NLP labeling tasks |

## 2) How your project can differentiate (niche opportunities)

Your current app is not competing head-to-head with enterprise IDP vendors. A better wedge is to be “the best tool” for a narrower workflow where generic document AI is overkill.

High-leverage differentiation angles:

- **Qur’an-/ayah-aware validation**: go beyond “missing ranges” and validate overlaps, duplicates, cross-file conflicts, out-of-order sections, and coverage quality per surah.
- **Gold-standard dataset generation**: make it easy to produce consistent JSON datasets (schema versioning, deterministic exports, changelogs) for research/analysis.
- **LLM-friendly guardrails**: provide prompts/templates + automated checks that catch common LLM formatting issues before they reach downstream systems.
- **Multilingual support**: themes/summaries in multiple languages with consistent structure, plus optional transliteration handling.
- **Tafsir / metadata enrichment**: attach references (tafsir sources, topics, entities) and export to a knowledge-graph-ready format.
- **Privacy-first / offline mode**: a local-first workflow can be a real differentiator for researchers and institutions that can’t upload text to third parties.
- **Explainable “why missing” UI**: show what sections cover which ranges (a coverage timeline), not just the gaps.

## 3) Practical positioning suggestion

Position this as:

> “A lightweight, auditable pipeline for turning Surah summaries into structured, validated datasets — optimized for Qur’an workflows and LLM-generated drafts.”

That message is clearer than “document AI” and avoids competing directly with the big clouds and invoice-focused IDP vendors.
