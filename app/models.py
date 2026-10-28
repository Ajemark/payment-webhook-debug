from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    currency: Mapped[str] = mapped_column(String(3), default="NGN")
    balance_minor: Mapped[int] = mapped_column(BigInteger, default=0)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(100))
    payment_id: Mapped[str] = mapped_column(String(100), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    amount_minor: Mapped[int] = mapped_column(BigInteger)
