"""
Base Agent class for SentinelMesh multi-agent platform.
Provides shared state management, event bus emitting, and lifecycle hooks.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.event_bus import bus
from backend.llm.base import LLMProvider


class AgentState:
    IDLE = "IDLE"
    THINKING = "THINKING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BaseAgent(ABC):
    def __init__(self, name: str, llm: LLMProvider):
        self.name = name
        self.llm = llm
        self.state = AgentState.IDLE

    async def set_state(self, run_id: str, new_state: str, details: Optional[str] = None):
        self.state = new_state
        await bus.publish(
            run_id=run_id,
            event_type="agent_state",
            agent_name=self.name,
            data={
                "state": new_state,
                "details": details or f"Agent {self.name} transitioned to {new_state}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            level="INFO"
        )

    async def log(self, run_id: str, message: str, level: str = "INFO", meta: Optional[Dict[str, Any]] = None):
        data = {"message": message}
        if meta:
            data.update(meta)
        await bus.publish(
            run_id=run_id,
            event_type="log",
            agent_name=self.name,
            data=data,
            level=level
        )

    async def emit_telemetry(self, run_id: str, key: str, value: Any):
        await bus.publish(
            run_id=run_id,
            event_type="telemetry",
            agent_name=self.name,
            data={"key": key, "value": value},
            level="INFO"
        )

    @abstractmethod
    async def run(self, run_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's responsibilities given the shared pipeline context."""
        pass
