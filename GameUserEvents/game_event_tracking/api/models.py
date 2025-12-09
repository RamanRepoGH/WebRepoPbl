from pydantic import BaseModel, Field


class InstallEventModel(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    user_id: str


class PurchaseEventModel(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    user_id: str
    product_id: str
    currency: str
    amount: float
