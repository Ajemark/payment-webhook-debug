from typing import Annotated, Callable
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from .database import get_session
from .models import Account, Payment

app = FastAPI(title="Synthetic payment webhook sandbox")

class PaymentEvent(BaseModel):
    event_id: str = Field(min_length=1, max_length=100)
    payment_id: str = Field(min_length=1, max_length=100)
    account_id: int = Field(gt=0)
    amount_minor: int = Field(gt=0)
    currency: str = Field(pattern="^NGN$")

def processing_checkpoint() -> Callable[[], None]:
    """No-op in normal use; tests can coordinate provider deliveries here."""
    return lambda: None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/accounts/{account_id}")
def account(account_id: int, session: Annotated[Session, Depends(get_session)]):
    row = session.get(Account, account_id)
    if row is None:
        raise HTTPException(404, "Account not found")
    return {"id": row.id, "balance_minor": row.balance_minor, "currency": row.currency}

@app.post("/webhooks/payments")
def webhook(event: PaymentEvent, session: Annotated[Session, Depends(get_session)],
            checkpoint: Annotated[Callable[[], None], Depends(processing_checkpoint)]):
    account = session.get(Account, event.account_id)
    if account is None:
        raise HTTPException(404, "Account not found")
    existing = session.scalar(select(Payment).where(Payment.payment_id == event.payment_id))
    if existing:
        return {"status": "already_processed"}
    checkpoint()
    session.add(Payment(event_id=event.event_id, payment_id=event.payment_id,
                        account_id=event.account_id, amount_minor=event.amount_minor))
    session.execute(update(Account).where(Account.id == event.account_id).values(
        balance_minor=Account.balance_minor + event.amount_minor))
    session.commit()
    return {"status": "processed"}
