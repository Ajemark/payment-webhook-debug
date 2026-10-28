from .database import Base, engine, SessionLocal
from .models import Account

def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.get(Account, 1) is None:
            session.add(Account(id=1, currency="NGN", balance_minor=0))
            session.commit()
    print("Schema ready. Synthetic account 1 exists; existing balances are preserved.")

if __name__ == "__main__":
    main()
