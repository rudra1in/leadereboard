from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    payment_key: str = Field(min_length=1)
    registration_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = "INR"


class PaymentResponse(BaseModel):
    id: int
    payment_key: str
    registration_id: str
    order_id: str | None
    amount: float
    currency: str
    status: str
    provider_reference: str | None

    class Config:
        from_attributes = True