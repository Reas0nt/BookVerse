# Feature: sistema-mantencion

## Objective

Simple web system for BookVerse office equipment maintenance that covers RF-06 to RF-09 of the Stage 2 case.

## Problem / Why

The group is unsure whether the course expects a software system or only documents. Guidelines (S7-S11) point to documents, but the case writes RF-06..RF-09 as system use cases (authentication, database errors). The group decided to deliver both: documents plus a small working system.

## Scope

- RF-06: register preventive/corrective maintenance per equipment (authenticated technician).
- RF-07: software catalog + update records (previous/new version, date, method); unregistered software shows a "must be registered" message.
- RF-08: maintenance history query with filters (date range, type, equipment code / serial number) and detail view of each entry; database error message.
- RF-09 (case): validate software after maintenance (OK / failure); failure flags the equipment for a new intervention.
- RF-09 (S10 guideline): spare parts inventory with stock entries/exits and part status; stock never negative.
- Roles: technician (registers) and administrator (queries history, validates, manages users/catalog).

Out of scope: deployment, MySQL, external integrations.

## Constraints

- Python 3.12, Flask, SQLite via stdlib `sqlite3` (no ORM), Jinja templates, local CSS (lab may be offline).
- Code, identifiers, comments in English; UI copy in Spanish (end users are Chilean staff).
- Runs with `flask --app sistema run` after `pip install -r requirements.txt`.
- Planning heuristic ~400 authored lines per task (advisory only).

## TDD

- Mode: off (no project/session TDD configuration; not requested). Source: default.
- Functional checks: `venv/bin/python -m pytest sistema/tests -q` (pytest, Flask test client, temporary DB).

## Delivery

- Strategy: ask-on-risk. Forecast ~1,200 authored lines across tasks.
- No git remote exists, so there are no PRs; work units are commits on `feat/sistema-mantencion`.
- RDD: global on. Each work-unit commit is assessed with `gentle-ai review assess`.

## Tasks

- [x] T1 Base: app factory, SQLite schema, init-db command with seed users, login/logout, role guard, equipment CRUD (list/create), layout + CSS, tests. Route: delegated writer (writer trigger: 2+ non-trivial files).
- [x] T2 RF-06 maintenance registration + RF-08 history query (filters, detail, DB error message), tests. Route: delegated writer.
- [x] T3 RF-07 software catalog + update records, unregistered software message, tests. Route: delegated writer.
- [x] T4 RF-09 software validation after maintenance + spare parts inventory (entries/exits/status, non-negative stock), tests. Route: delegated writer.
- [x] T5 Docs: `sistema/README.md` (setup, run, default users, RF mapping) and root README update. Route: inline (mechanical).

## Acceptance criteria

- Each RF has at least one passing test covering its main flow and its error flow from the case.
- Unauthenticated users are redirected to login; technicians cannot access admin-only pages.
- `pytest` passes; app starts with documented commands.

## Progress / Evidence

(Updated after each task.)

- T1 done (047045e): `venv/bin/python -m pytest sistema/tests -q`: 9 passed; `flask --app sistema init-db` smoke OK (instance removed afterwards).
- T2 done (0c5f441): pytest 20 passed. History query/detail open to both roles; DB error returns 503 page (test monkeypatches get_db).
- T3 done (890539a): pytest 28 passed. Update form takes software name; unknown name shows "must be registered first"; update sets current version.
- T4 done (4ceb489): pytest 44 passed. Validation requires a prior maintenance; "Falla" requires observations and flags equipment "requiere nueva intervención". Salida > stock rejected ("Stock insuficiente"). Part creation/status change admin-only.
- Parent spot check: `venv/bin/python -m pytest sistema/tests -q`: 44 passed.
- RDD: assess on 9a603ab..HEAD → risk high (hot paths: auth, update). Consent granted; 4-lens review approved and acknowledged (lineage review-29ef608be569ef45, authority burned). 14 non-blocking advisory findings (no CSRF, default creds/secret key, open-redirect backslash, unicode digit quantity crash, DB error page reachability, destructive init-db, readability items) kept as optional follow-ups.
- T5 done: sistema/README.md + root README; smoke test with admin login: all main pages 200.

- Follow-up (5bdb32e): equipment registration admin-only (user decision, case RF-06 alt flow implies prior registration); RF-06/RF-08 alternate-flow messages aligned with case wording. pytest 45 passed. RDD high: consent granted, 4-lens review approved and acknowledged (review-1558753bddc2985d). Advisory: empty-history message is misleading when filters are applied.
- Follow-up (e676847): history shows "No hay mantenimientos realizados." only when no filters are applied; with filters and no matches it shows "Ningún mantenimiento coincide con la búsqueda." pytest 46 passed. RDD assess: medium, under_budget (23 lines) → pending in slice, no review yet.
- Port 5110 documented (71bf809) because port 5000 is used by another service.

Open questions (product):
- Should software updates be linked to a maintenance record? (Currently standalone.)

## Next step

Feature complete. Optional: hardening follow-ups from advisory findings; merge feat/sistema-mantencion into main (user decision).
