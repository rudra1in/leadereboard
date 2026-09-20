from sqlalchemy.orm import Session

from .models import Payment, PaymentStatus
from .schemas import PaymentCreate


def create_payment(
    db: Session,
    payment_data: PaymentCreate,
) -> Payment:

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.payment_key == payment_data.payment_key
        )
        .first()
    )

    if existing_payment:
        return existing_payment

    payment = Payment(
        payment_key=payment_data.payment_key,
        registration_id=payment_data.registration_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        status=PaymentStatus.PENDING.value,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment