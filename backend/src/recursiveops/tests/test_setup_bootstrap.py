from sqlmodel import Session, SQLModel, create_engine

from recursiveops.auth.setup import create_initial_admin, requires_setup


def _make_session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_requires_setup_true_when_no_users() -> None:
    session = _make_session()
    try:
        assert requires_setup(session) is True
    finally:
        session.close()


def test_create_initial_admin_creates_user() -> None:
    session = _make_session()
    try:
        user = create_initial_admin(session, "admin", "changeme")
        assert user.username == "admin"
        assert user.is_admin is True
        assert user.hashed_password != "changeme"
        assert requires_setup(session) is False
    finally:
        session.close()


def test_create_initial_admin_rejects_when_existing_user() -> None:
    session = _make_session()
    try:
        create_initial_admin(session, "admin", "changeme")
        raised = False
        try:
            create_initial_admin(session, "admin2", "other")
        except ValueError:
            raised = True
        assert raised is True
    finally:
        session.close()
