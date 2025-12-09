"""
Event model classes for the Game Event SDK.
Loose-validation approach: SDK guarantees minimal required fields whereas the other business validations are performed in Snowflake.
"""

from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime, timezone


@dataclass
class BaseEvent:
    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class InstallEvent(BaseEvent):
    event_type: str = "install"
    user_id: str = ""


@dataclass
class PurchaseEvent(BaseEvent):
    event_type: str = "purchase"
    user_id: str = ""
    product_id: str = ""
    currency: str = ""
    amount: float = 0.0