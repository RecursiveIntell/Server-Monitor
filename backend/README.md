# RecursiveOps

RecursiveOps is a local-first Fedora Server control center with optional LLM summaries. The core app works without any LLM enabled.

## Features
- System inventory (systemd services, Podman containers, mounts, ports)
- Cloudflared ingress parser and route mapping
- HTTP health checks with history
- Logs (systemd journal + podman logs)
- Patch-based config changes with diff preview, snapshots, and rollback
- Optional LLM explanations (advisory-only)

## Quick start

### Backend
1. Copy and edit the config:
   ```bash
   cp deploy/config/recursiveops.example.yml /etc/recursiveops/config.yml
   ```
2. Ensure a JWT secret file exists:
   ```bash
   sudo mkdir -p /etc/recursiveops
   sudo sh -c 'head -c 48 /dev/urandom | base64 > /etc/recursiveops/jwt.secret'
   ```
3. Create a virtualenv and install:
   ```bash
   cd backend
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
4. Run migrations:
   ```bash
   alembic upgrade head
   ```
5. Start the API:
   ```bash
   uvicorn recursiveops.main:app --host 127.0.0.1 --port 8844
   ```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Notes
- The backend binds to 127.0.0.1 by default.
- All system interactions are restricted by a command whitelist.
- LLM integration is optional and advisory-only.

