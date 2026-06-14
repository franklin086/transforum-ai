from collections import defaultdict
from typing import DefaultDict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: DefaultDict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, meeting_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[meeting_id].append(websocket)

    def disconnect(self, meeting_id: str, websocket: WebSocket) -> None:
        connections = self.active_connections.get(meeting_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and meeting_id in self.active_connections:
            del self.active_connections[meeting_id]

    async def broadcast(self, meeting_id: str, message: dict) -> None:
        connections = list(self.active_connections.get(meeting_id, []))
        stale_connections: list[WebSocket] = []

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                stale_connections.append(websocket)

        for websocket in stale_connections:
            self.disconnect(meeting_id, websocket)


manager = ConnectionManager()
