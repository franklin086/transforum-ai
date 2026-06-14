import asyncio
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api import realtime as realtime_api
from main import app
from websocket.connection_manager import manager


class RealtimeWebSocketTest(unittest.TestCase):
    def tearDown(self):
        manager.active_connections.clear()

    def test_websocket_receives_subtitle_update_broadcast(self):
        message = {
            "type": "subtitle_update",
            "meeting_id": "meeting_ws_test",
            "chinese": "大家好，欢迎参加测试会议。",
            "english": "Hello everyone, welcome to the test meeting.",
            "provider": "gemini",
            "translation_latency_ms": 1234,
            "timestamp": "2026-06-09T10:00:00",
        }

        with patch.object(realtime_api, "get_meeting", return_value=object()):
            with TestClient(app) as client:
                with client.websocket_connect(
                    "/ws/realtime/meeting_ws_test"
                ) as websocket:
                    asyncio.run(manager.broadcast("meeting_ws_test", message))
                    received = websocket.receive_json()

        self.assertEqual(received, message)


if __name__ == "__main__":
    unittest.main()
