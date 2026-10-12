"""
Asynchronous In-Memory Event Bus and WebSocket Broadcaster with Event-Sourcing.
Enables real-time streaming of agent states, execution telemetry, terminal logs, and debates,
with sequence numbering and event replay for reconnecting clients.
"""

import asyncio
from datetime import datetime, timezone
import json
from typing import Dict, Set, Any, List, Optional
from fastapi import WebSocket
from backend.database import db_session_scope
from backend.models import AgentLog


class EventBus:
    def __init__(self):
        # run_id -> set of active WebSockets
        self._subscribers: Dict[str, Set[WebSocket]] = {}
        # run_id -> list of recent events (buffered for reconnects)
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        # run_id -> current sequence number
        self._seq_counters: Dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def connect(self, run_id: str, websocket: WebSocket, since_seq: Optional[int] = None):
        await websocket.accept()
        async with self._lock:
            if run_id not in self._subscribers:
                self._subscribers[run_id] = set()
            self._subscribers[run_id].add(websocket)

            # Replay missed events if requested or send recent buffer
            if run_id in self._history:
                events_to_replay = self._history[run_id]
                if since_seq is not None:
                    events_to_replay = [e for e in events_to_replay if e.get("seq", 0) > since_seq]
                else:
                    events_to_replay = events_to_replay[-50:]

                for past_event in events_to_replay:
                    try:
                        await websocket.send_text(json.dumps(past_event))
                    except Exception:
                        break

    def get_history_since(self, run_id: str, since_seq: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns buffered event sequence history for reconnecting clients."""
        events = self._history.get(run_id, [])
        if since_seq is not None:
            return [e for e in events if e.get("seq", 0) > since_seq]
        return events[-50:]

    async def disconnect(self, run_id: str, websocket: WebSocket):
        async with self._lock:
            if run_id in self._subscribers and websocket in self._subscribers[run_id]:
                self._subscribers[run_id].remove(websocket)
                if not self._subscribers[run_id]:
                    del self._subscribers[run_id]

    async def publish(
        self,
        run_id: str,
        event_type: str,
        agent_name: str = "orchestrator",
        data: Dict[str, Any] = None,
        level: str = "INFO"
    ):
        """
        Publishes an event with an auto-incrementing sequence number,
        buffers it in memory for replay, and broadcasts to active WebSockets.
        """
        if data is None:
            data = {}

        async with self._lock:
            seq = self._seq_counters.get(run_id, 0) + 1
            self._seq_counters[run_id] = seq

            payload = {
                "run_id": run_id,
                "seq": seq,
                "event_type": event_type,
                "agent_name": agent_name,
                "level": level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }

            if run_id not in self._history:
                self._history[run_id] = []
            self._history[run_id].append(payload)
            if len(self._history[run_id]) > 1000:
                self._history[run_id] = self._history[run_id][-1000:]

            subscribers = list(self._subscribers.get(run_id, set()))

        message_str = json.dumps(payload)
        for ws in subscribers:
            try:
                await ws.send_text(message_str)
            except Exception:
                pass

        # Persist log event asynchronously
        if event_type in ("log", "agent_state", "telemetry"):
            msg = data.get("message", f"Agent {agent_name} event: {event_type}")
            meta = json.dumps(data) if data else None
            asyncio.create_task(self._persist_log(run_id, seq, agent_name, level, msg, meta))

    async def _persist_log(self, run_id: str, seq: int, agent_name: str, level: str, msg: str, meta: str):
        def _save():
            try:
                with db_session_scope() as session:
                    log_entry = AgentLog(
                        run_id=run_id,
                        seq=seq,
                        agent_name=agent_name,
                        level=level,
                        message=msg[:1000],
                        metadata_json=meta
                    )
                    session.add(log_entry)
            except Exception:
                pass

        await asyncio.to_thread(_save)

    def clear_run(self, run_id: str):
        if run_id in self._history:
            del self._history[run_id]
        if run_id in self._seq_counters:
            del self._seq_counters[run_id]


# Global singleton instance
bus = EventBus()
