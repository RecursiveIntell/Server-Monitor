# RecursiveOps backend

FastAPI, SQLModel and Alembic backend for the Server-Monitor repository.

Use the [repository README](../README.md) for the canonical setup instructions, shared configuration, initial administrator setup, secret/database paths and operational boundaries. Run backend commands from this directory after installing `.[dev]` and selecting `RECURSIVEOPS_CONFIG`.

```bash
python -m pytest src/recursiveops/tests
```

The implementation is under [`src/recursiveops/`](src/recursiveops/). The example configuration enables host actions and Ollama; review those settings before launching against a real host.
