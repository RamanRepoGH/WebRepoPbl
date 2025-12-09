"""
Simple HTTP client for sending events to the backend.
"""
import requests
from .events import InstallEvent, PurchaseEvent


class GameAnalyticsClient:
    def __init__(self, base_url: str, timeout=2):
        self.base_url = base_url
        self.timeout = timeout

    def send_install(self, user_id: str):
        event = InstallEvent(user_id=user_id)
        response = requests.post(
            f"{self.base_url}/events/install",
            json=event.__dict__,
            timeout=self.timeout,
        )
        return response.json()

    def send_purchase(self, user_id: str, product_id: str, currency: str, amount: float):
        event = PurchaseEvent(
            user_id=user_id,
            product_id=product_id,
            currency=currency,
            amount=amount
        )
        response = requests.post(
            f"{self.base_url}/events/purchase",
            json=event.__dict__,
            timeout=self.timeout,
        )

        return response.json()