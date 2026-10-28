import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_session
from app.main import app
from app.models import Account

load_dotenv()

@pytest.fixture
def sandbox():
    url = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg://odin:odin@localhost:55432/payment_debug_test")
    engine = create_engine(url, pool_pre_ping=True)
    if engine.url.get_backend_name() != "postgresql" or not (engine.url.database or "").endswith("_test"):
        raise RuntimeError("Tests require a dedicated PostgreSQL database ending in _test")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory() as session:
        session.add(Account(id=1, balance_minor=0, currency="NGN"))
        session.commit()
    def sessions():
        with factory() as session:
            yield session
    app.dependency_overrides[get_session] = sessions
    try:
        with TestClient(app) as client:
            yield client, factory
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()
