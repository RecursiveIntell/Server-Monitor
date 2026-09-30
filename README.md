# RecursiveOps (Server-Monitor)

RecursiveOps is a local-first Fedora Server control center with a FastAPI/SQLModel backend and a Svelte frontend. It exposes inventory, health checks, logs and reviewable configuration changes. Ollama explanations are optional and advisory; the example configuration enables them, so set `llm.enabled: false` when starting without a model service.

## Implemented surfaces

- systemd, Podman, mount and port inventory
- Cloudflared ingress parsing and route mapping
- HTTP health checks and stored results
- journal and container log views
- patch previews, configuration snapshots and rollback paths
- authenticated administration and a local-only initial-account setup flow

Source ownership lives in `backend/src/recursiveops/`: `settings.py` owns configuration, `auth/` owns login/bootstrap, `api/routers/` owns routes, and `core/runner.py` plus `core/whitelist.py` own command execution. These controls need host-level verification before production use; they are not a guarantee that every action is harmless.

## Local development setup

Use Python 3.11+, Node/npm, and a Linux host with the tools needed by the inventory features. From the repository root:

```bash
git clone https://github.com/RecursiveIntell/Server-Monitor.git
cd Server-Monitor
mkdir -p .secrets
cp deploy/config/recursiveops.example.yml .secrets/config.yml
```

Before starting, edit `.secrets/config.yml`:

- point `security.jwt_secret_file` to an absolute path such as `/absolute/path/to/Server-Monitor/.secrets/jwt.secret`
- keep `security.require_login: true`
- set `security.allow_actions: false` for an initial read-only inspection
- set `llm.enabled: false` unless the configured Ollama service/model is available
- review the Cloudflared and fstab paths for this host

Create the local signing secret without printing it to the terminal, then export the config path before changing directory:

```bash
umask 077
python3 -c 'import secrets; print(secrets.token_urlsafe(48))' > .secrets/jwt.secret
export RECURSIVEOPS_CONFIG="$PWD/.secrets/config.yml"
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
alembic upgrade head
uvicorn recursiveops.main:app --host 127.0.0.1 --port 8844
```

Run secret creation once for a new configuration. Replacing an existing signing secret invalidates existing tokens. `.secrets/` is ignored by Git; keep its contents private. The SQLite database defaults to the configuration directory unless `RECURSIVEOPS_DB_URL` or `database_url` overrides it. Migrations and the server must use the same configuration.

In another terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open the local frontend and complete initial administrator setup. The `/api/setup/status` and `/api/setup/create` routes accept loopback clients only; normal API routes require login. Creating accounts and enabling host actions are operator steps, not automatic consequences of installing the package.

## Host installation and operational boundaries

`/etc/recursiveops/config.yml` is the default system configuration path. For a managed installation, create that directory before copying configuration, and arrange ownership/permissions for the runtime user and its secret/database files. Do not run the whole service as root simply to work around a path error.

The explicit Uvicorn command above binds loopback. Uvicorn command-line binding, reverse-proxy exposure, host filesystem permissions and the configured action policy all matter. LLM prompts/log summaries go to the configured provider; review content before enabling remote/cloud processing. The cloud provider module is a stub, not a completed cloud integration.

## Validation

From `backend/` with development dependencies installed:

```bash
python -m pytest src/recursiveops/tests
```

From `frontend/`:

```bash
npm run check
npm run build
```

These checks do not replace a controlled Fedora/systemd/Podman/Cloudflared smoke test. Test changes against copies of configuration and verify recovery before enabling actions on a live server.
