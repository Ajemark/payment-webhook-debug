from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from sqlalchemy import func, select
from app.main import app, processing_checkpoint
from app.models import Account, Payment

EVENT = dict(event_id="evt_demo_001", payment_id="pay_demo_001", account_id=1,
             amount_minor=500000, currency="NGN")

def state(factory):
    with factory() as session:
        return (session.get(Account, 1).balance_minor,
                session.scalar(select(func.count()).select_from(Payment)))

def test_single_delivery(sandbox):
    client, factory = sandbox
    assert client.post("/webhooks/payments", json=EVENT).status_code == 200
    assert state(factory) == (500000, 1)

def test_sequential_duplicate(sandbox):
    client, factory = sandbox
    client.post("/webhooks/payments", json=EVENT)
    response = client.post("/webhooks/payments", json=EVENT)
    assert response.json() == {"status": "already_processed"}
    assert state(factory) == (500000, 1)

def test_distinct_payments(sandbox):
    client, factory = sandbox
    for number in range(2):
        payload = {**EVENT, "payment_id": f"pay_{number}", "event_id": f"evt_{number}"}
        assert client.post("/webhooks/payments", json=payload).status_code == 200
    assert state(factory) == (1000000, 2)

def test_invalid_amount(sandbox):
    client, factory = sandbox
    assert client.post("/webhooks/payments", json={**EVENT, "amount_minor": -1}).status_code == 422
    assert state(factory) == (0, 0)

def test_concurrent_duplicate_credits_once(sandbox):
    client, factory = sandbox
    barrier = Barrier(2, timeout=10)
    app.dependency_overrides[processing_checkpoint] = lambda: barrier.wait
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: client.post("/webhooks/payments", json=EVENT), range(2)))
    assert all(response.status_code == 200 for response in responses)
    balance, count = state(factory)
    assert (balance, count) == (500000, 1), (
        f"One NGN 5,000 payment must produce one credit; got balance_minor={balance}, payment_rows={count}"
    )
