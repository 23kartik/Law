# Evidence-Driven Legal Advocacy Platform (MVP)

Two modules, per the requirement doc:

1. **Legal Research** — validate case input → fetch real precedents from court sources →
   compare against the case → confidence-scored research report, every claim tagged
   `VERIFIED_COURT` / `EXTRACTED` / `AI_ANALYSIS`.
2. **Legal Drafting** — pick a target court → re-validate → pull precedents → generate a
   court-specific draft with missing facts bracketed as placeholders and anything needing
   verification flagged, never fabricated.

MVP covers one fully-built court + proceeding: **Delhi High Court — Habeas Corpus writ
petition (Article 226)**, matching the structure of the sample draft. Adding another
court/proceeding is a new YAML file in `backend/app/templates/`, not a code change.

## Setup

### Backend

```bash
cd backend
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in the keys below
uvicorn app.main:app --reload --port 8000
```

**`GEMINI_API_KEY` (required)** — free at https://aistudio.google.com/apikey. Nothing in
this app works without it; extraction, validation, research analysis, and drafting all run
through Gemini.

**`INDIAN_KANOON_API_KEY` (optional but strongly recommended)** — free tier (200
credits/month) at https://api.indiankanoon.org/signup/. Without it, the research module
falls back to the `kanoon.dev` pilot API (zero setup, no key) — but as of this build that
pilot only indexes ~27 documents total across a handful of courts and **does not cover the
Supreme Court's or Delhi High Court's real case law** (e.g. *D.K. Basu*, *Pankaj Bansal*
won't be found). The Indian Kanoon key is what makes the research module actually useful for
a demo; both sources are combined automatically once the key is set.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens on http://localhost:5173 (or the next free port) and proxies `/api` to the backend on
`:8000` — run both at once.

## Verifying it works

```bash
cd backend && source venv/bin/activate && pytest   # 10 tests, no API keys needed
```

Then, with both servers running and `GEMINI_API_KEY` set, walk through the wizard in the
browser: paste the example narrative ("My brother has been detained by Karlobag Police…") or
upload a PDF → review/complete the extracted facts → run research → pick Delhi HC / Habeas
Corpus → generate the draft → download the `.docx`.

## What's deliberately out of scope for this MVP

- Only one court + proceeding template is built out (see `backend/app/templates/`).
- No auth, single-user, local SQLite (`backend/law.db`).
- DOCX export matches the structure, not exact court-mandated pagination/margin rules.
- `kanoon.dev` coverage is a pilot sample — treat it as a bonus source, not primary, until
  you're on the paid Indian Kanoon tier.
