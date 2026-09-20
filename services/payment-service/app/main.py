from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Payment
from .schemas import PaymentCreate, PaymentResponse
from .service import create_payment


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GameX Payment Service",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "service": "payment-service",
        "status": "running",
    }


@app.post(
    "/payments",
    response_model=PaymentResponse,
)
def process_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
):
    return create_payment(
        db,
        payment_data,
    )


@app.get(
    "/payments/{payment_key}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_key: str,
    db: Session = Depends(get_db),
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.payment_key == payment_key
        )
        .first()
    )

    return payment