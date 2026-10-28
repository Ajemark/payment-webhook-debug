# Payment webhook debugging starter

A synthetic FastAPI/PostgreSQL exercise for an approved Odin debugging recording.
This is the intentionally buggy starting state. No solution is included.
All names, events, payments, and amounts are fictional. No payment provider connects to this app.
The endpoint has no authentication or signature verification; run on localhost only.

## Requirements

Python 3.11–3.13, Docker Desktop with Compose (running), and VS Code.
All commands below work in VS Code's integrated terminal, opened in this folder.
Alternatively use an existing PostgreSQL 17 installation and create two dedicated databases.

## Set up

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d --wait
python -m app.seed
```

The Docker initialization creates `payment_debug` and `payment_debug_test` on port 55432.
If you use an existing PostgreSQL instance, create both databases and adjust both URLs in `.env`.
The supplied Docker credentials are for this local exercise only.
`app.seed` creates tables and account 1 with a zero balance if it does not already exist.
It preserves existing data. The test suite resets its separate test database on every test.
Never point TEST_DATABASE_URL at valuable data: it drops and recreates the exercise tables.
Tests require a PostgreSQL database whose name ends with `_test`; run tests serially.

## Reproduce before recording

```sh
pytest -q
```

The baseline should produce **4 passed, 1 failed**. The failure should show a balance of
1,000,000 minor units and two payment rows for one payment of 500,000 minor units.
In NGN, that means a ₦5,000 payment incorrectly credited ₦10,000.
The failure is intentional and is not marked xfail or skipped.

```sh
pytest -q tests/test_webhooks.py::test_concurrent_duplicate_credits_once
```

The concurrency harness uses two separate requests and database sessions, coordinated
through an otherwise inert test checkpoint. It uses a barrier, not sleep or random timing.
The checkpoint does not change balances or create records. A timeout is a harness error,
not the expected defect. When making the fix, review whether the checkpoint placement
still makes sense: a correct implementation may serialize requests before this point.
Do not remove or weaken the one-credit assertion to obtain a passing test.

## Explore the running API

```sh
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs to inspect the API.
From another integrated terminal in the same folder:

```sh
curl -s http://127.0.0.1:8000/accounts/1
curl -s -X POST http://127.0.0.1:8000/webhooks/payments \
  -H 'Content-Type: application/json' --data-binary @data/payment.json
curl -s http://127.0.0.1:8000/accounts/1
```

A sequential replay is already handled. Use the coordinated test for reliable concurrent
reproduction; manually sending two requests is timing-dependent. Tests use their own database
and do not change the account shown by the running API.

## Recording brief

Investigate why concurrent deliveries of the same payment can credit an account twice.
Preserve correct single-payment, sequential-replay, and distinct-payment behavior.
Implement your own correction, add appropriate regression coverage, and verify it with
PostgreSQL. Review the final diff and explain the root cause and evidence.
Use VS Code for code inspection, editing, and its integrated terminal for setup and tests.
Follow the approved task's rules for independent work during recording.

## Preserve and publish the baseline

The folder is a local Git repository with a `buggy-baseline` tag. Before recording,
publish it to a repository you control and put its URL plus the baseline commit in
Starting Materials. Publishing has not been done automatically.

```sh
git log -1 --oneline
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
git push origin buggy-baseline
git switch -c recording-fix
```

Keep the tag unchanged. Do not publish the solution before the recording.
No assertion is made here about Mercor policy or Studio upload requirements; use the
approval and instructions supplied by your program. This starter was AI-assisted.

## Stop the local database

```sh
docker compose stop
```

This preserves the Docker data volume for the next session.
