# RecursiveOps - Agent Rules

## Primary Goal
Build a reliable Fedora server control center with optional LLM summaries. The app must work without LLM.

## Non-Negotiables
1. Deterministic core: inventory, checks, parsing, diffing, applying patches.
2. LLM is advisory-only. It never executes actions automatically.
3. All LLM outputs must be strict JSON validated by Pydantic schemas.
4. Route changes must be patch-based with preview, snapshot, and rollback support.
5. Backend binds to 127.0.0.1 by default. Must require auth.

## Coding Standards
- Python: FastAPI + SQLModel + Alembic, async where appropriate.
- All system interactions go through core/runner.py and core/whitelist.py.
- Prefer machine-readable command outputs (JSON) when available.
- Add tests for all parsers and patch logic.

## Deliverables Checklist
- Working inventory endpoints
- Hostname checks with stored results
- Logs endpoints (systemd + podman)
- LLM analysis endpoints (Ollama)
- Cloudflared ingress parser + routes UI
- Add-route wizard (diff preview + apply + verify)
- Snapshot + diff view + rollback

## Safety
- Redact secrets before any cloud LLM call.
- Never run arbitrary shell commands from user input.
