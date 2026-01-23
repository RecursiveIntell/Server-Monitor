from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session

from recursiveops.jobs.tasks import run_scheduled_checks


def start_scheduler(app) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    interval = app.state.settings.checks.default_interval_seconds

    def _job() -> None:
        with Session(app.state.engine) as session:
            run_scheduled_checks(session, app.state.settings)

    scheduler.add_job(_job, "interval", seconds=interval, id="health_checks")
    scheduler.start()
    app.state.scheduler = scheduler
    return scheduler


def main() -> None:
    from time import sleep

    from recursiveops.main import create_app

    app = create_app()
    start_scheduler(app)
    while True:
        sleep(60)


if __name__ == "__main__":
    main()
