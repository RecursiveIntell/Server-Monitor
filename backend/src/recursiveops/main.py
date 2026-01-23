from __future__ import annotations

import logging
import logging.config

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from recursiveops.api.deps import get_current_user
from recursiveops.api.routers import (
    actions,
    auth,
    changes,
    checks,
    cloudflared_health,
    hostnames,
    inventory,
    llm,
    llm_settings,
    log_bundle,
    logs,
    overview,
    paths_settings,
    products,
    routes_cloudflared,
    setup,
    settings_api,
)
from recursiveops.auth import models as auth_models  # noqa: F401
from recursiveops.db import models as db_models  # noqa: F401
from recursiveops.core.runner import CommandRunner
from recursiveops.db.engine import get_engine, init_db
from recursiveops.logging_conf import LOGGING_CONFIG
from recursiveops.settings import get_settings


def create_app(settings=None, engine=None) -> FastAPI:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("recursiveops")

    if settings is None:
        settings = get_settings()
    if engine is None:
        engine = get_engine(settings)

    init_db(engine)

    app = FastAPI(default_response_class=ORJSONResponse)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.runner = CommandRunner()

    @app.get("/api/health")
    def health(_user=Depends(get_current_user)) -> dict:
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api")
    app.include_router(settings_api.router, prefix="/api")
    app.include_router(inventory.router, prefix="/api")
    app.include_router(hostnames.router, prefix="/api")
    app.include_router(routes_cloudflared.router, prefix="/api")
    app.include_router(checks.router, prefix="/api")
    app.include_router(overview.router, prefix="/api")
    app.include_router(cloudflared_health.router, prefix="/api")
    app.include_router(logs.router, prefix="/api")
    app.include_router(log_bundle.router, prefix="/api")
    app.include_router(actions.router, prefix="/api")
    app.include_router(changes.router, prefix="/api")
    app.include_router(llm.router, prefix="/api")
    app.include_router(llm_settings.router, prefix="/api")
    app.include_router(paths_settings.router, prefix="/api")
    app.include_router(products.router, prefix="/api")
    app.include_router(setup.router, prefix="/api")

    logger.info("RecursiveOps app initialized")
    return app


app = create_app()
