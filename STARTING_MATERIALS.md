# Starting materials draft

A local Python FastAPI backend with PostgreSQL account and payment models, synthetic
NGN payment events, pinned dependencies, Docker database setup, and pytest coverage.
The baseline contains an intentionally seeded duplicate-credit concurrency defect.
A synchronized two-request test demonstrates the failure without relying on random timing.

Application: Visual Studio Code, including its integrated terminal.

Baseline repository URL: add after publishing.
Baseline reference: `buggy-baseline` (record the commit SHA from `git rev-parse buggy-baseline`).
Setup and reproduction: follow README.md; run `pytest -q`.
Expected baseline result: four passing tests and one failing concurrency regression test.

Expected final deliverable: corrected payment processing, relevant regression coverage,
passing PostgreSQL test results, a reviewable diff, and a root-cause explanation.
