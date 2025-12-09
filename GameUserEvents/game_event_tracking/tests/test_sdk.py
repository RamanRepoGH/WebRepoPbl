import unittest
from unittest.mock import patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SDK.client import GameAnalyticsClient


class TestSDK(unittest.TestCase):
    @patch('requests.post')
    def test_track_purchase(self, mock_post):
        # Setup mock
        mock_post.return_value.status_code = 201

        client = GameAnalyticsClient("http://localhost")
        result = client.send_purchase("u1", "p1", "USD",10.0)

        self.assertTrue(result)
        # Verify correct payload structure
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        self.assertEqual(payload['currency'], "USD")
        self.assertEqual(payload['event_type'], "purchase")


if __name__ == '__main__':
    unittest.main()