import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.main import app, firehose
#from api.models import InstallEventModel, PurchaseEventModel

@pytest.fixture(autouse=True)
def mock_firehose(monkeypatch):
    mock_client = MagicMock()
    firehose.client = mock_client
    return mock_client

def test_install_event_endpoint(mock_firehose):
    client = TestClient(app)
    payload = {"event_id":"evt-123","event_type":"install","timestamp":"2025-12-09T12:00:00","user_id":"user1"}
    response = client.post("/events/install", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "event_id": "evt-123"}
    assert mock_firehose.put_record.called

def test_purchase_event_endpoint(mock_firehose):
    client = TestClient(app)
    payload = {"event_id":"evt-456","event_type":"purchase","timestamp":"2025-12-09T12:01:00",
               "user_id":"user2","product_id":"prod-001","currency":"USD","amount":9.99}
    response = client.post("/events/purchase", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "event_id": "evt-456"}
    assert mock_firehose.put_record.called