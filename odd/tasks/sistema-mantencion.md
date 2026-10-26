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
- [ ] T5 Docs: `sistema/README.md` (setup, run, default users, RF mapping) and root README update. Route: inline (mechanical).

## Acceptance criteria

- Each RF has at least one passing test covering its main flow and its error flow from the case.
- Unauthenticated users are redirected to login; technicians cannot access admin-only pages.
- `pytest` passes; app starts with documented commands.

## Progress / Evidence

(Updated after each task.)

- T1 done: `venv/bin/python -m pytest sistema/tests -q`: 9 passed; `flask --app sistema init-db` smoke OK (instance removed afterwards).  step

T2.
