#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

API_HOST="127.0.0.1"
API_PORT="8844"
WEB_HOST="127.0.0.1"
WEB_PORT="5173"

CONFIG_PATH_DEFAULT="$ROOT_DIR/deploy/config/recursiveops.example.yml"
CONFIG_PATH="${RECURSIVEOPS_CONFIG:-$CONFIG_PATH_DEFAULT}"

ensure_backend_deps() {
  if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
    python3.11 -m venv "$BACKEND_DIR/.venv"
  fi

  "$BACKEND_DIR/.venv/bin/python" -m pip install --upgrade pip >/dev/null
  "$BACKEND_DIR/.venv/bin/python" -m pip install -e "$BACKEND_DIR"[dev]
}

ensure_jwt_secret() {
  local base_config="$CONFIG_PATH"
  local secret_path

  secret_path="$("$BACKEND_DIR/.venv/bin/python" - <<PY
import pathlib
import yaml

cfg = pathlib.Path("${base_config}")
data = {}
if cfg.exists():
    data = yaml.safe_load(cfg.read_text()) or {}
security = data.get("security") or {}
value = security.get("jwt_secret_file") or ""
print(value)
PY
)"

  if [[ -z "$secret_path" ]]; then
    secret_path="$ROOT_DIR/.secrets/jwt.secret"
  fi

  if [[ -f "$secret_path" ]]; then
    return
  fi

  if [[ "$base_config" == "$CONFIG_PATH_DEFAULT" ]]; then
    mkdir -p "$ROOT_DIR/.secrets"
    head -c 48 /dev/urandom | base64 > "$ROOT_DIR/.secrets/jwt.secret"
    chmod 600 "$ROOT_DIR/.secrets/jwt.secret"
    "$BACKEND_DIR/.venv/bin/python" - <<PY
import pathlib
import yaml

cfg = pathlib.Path("${base_config}")
data = yaml.safe_load(cfg.read_text()) or {}
data.setdefault("security", {})
data["security"]["jwt_secret_file"] = str(pathlib.Path("${ROOT_DIR}/.secrets/jwt.secret"))
runtime_cfg = pathlib.Path("${ROOT_DIR}/.secrets/config.yml")
runtime_cfg.write_text(yaml.safe_dump(data))
PY
    CONFIG_PATH="$ROOT_DIR/.secrets/config.yml"
    export RECURSIVEOPS_CONFIG="$CONFIG_PATH"
    return
  fi

  if [[ ! -d "$(dirname "$secret_path")" ]]; then
    mkdir -p "$(dirname "$secret_path")" 2>/dev/null || true
  fi

  if [[ -w "$(dirname "$secret_path")" ]]; then
    head -c 48 /dev/urandom | base64 > "$secret_path"
    chmod 600 "$secret_path"
    return
  fi

  echo "JWT secret file not found and cannot be created at $secret_path."
  echo "Create the file manually or set RECURSIVEOPS_CONFIG to a writable config."
  exit 1
}

ensure_frontend_deps() {
  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    (cd "$FRONTEND_DIR" && npm install)
  fi
  (cd "$FRONTEND_DIR" && npm run prepare)
}

migrate_db() {
  (cd "$BACKEND_DIR" && RECURSIVEOPS_CONFIG="$CONFIG_PATH" .venv/bin/alembic upgrade head)
}

ensure_admin_user() {
  if [[ -n "${RECURSIVEOPS_ADMIN_USER:-}" && -n "${RECURSIVEOPS_ADMIN_PASS:-}" ]]; then
    (cd "$BACKEND_DIR" && RECURSIVEOPS_CONFIG="$CONFIG_PATH" .venv/bin/python -m recursiveops.auth.bootstrap --username "$RECURSIVEOPS_ADMIN_USER" --password "$RECURSIVEOPS_ADMIN_PASS")
  else
    echo "No admin credentials provided. Set RECURSIVEOPS_ADMIN_USER and RECURSIVEOPS_ADMIN_PASS to create one."
  fi
}
start_backend() {
  (cd "$BACKEND_DIR" && RECURSIVEOPS_CONFIG="$CONFIG_PATH" .venv/bin/uvicorn recursiveops.main:app --host "$API_HOST" --port "$API_PORT") &
  BACKEND_PID=$!
}

start_frontend() {
  (cd "$FRONTEND_DIR" && npm run dev -- --host "$WEB_HOST" --port "$WEB_PORT") &
  FRONTEND_PID=$!
}

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

ensure_backend_deps
ensure_jwt_secret
ensure_frontend_deps
migrate_db
ensure_admin_user
start_backend
start_frontend

echo "Backend: http://$API_HOST:$API_PORT"
echo "Frontend: http://$WEB_HOST:$WEB_PORT"
echo "If this is your first run, visit http://$WEB_HOST:$WEB_PORT/setup"

echo "Press Ctrl+C to stop."
wait
