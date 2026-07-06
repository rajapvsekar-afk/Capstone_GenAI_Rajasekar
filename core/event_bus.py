"""
Event Bus for Loosely Coupled Agent Communication
Implements publish-subscribe pattern for microservices architecture
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum
import uuid


class EventType(Enum):
    APPLICATION_SUBMITTED = "application.submitted"
    APPLICATION_UPDATED = "application.updated"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    EVALUATION_STARTED = "evaluation.started"
    EVALUATION_COMPLETED = "evaluation.completed"
    DECISION_MADE = "decision.made"
    MANUAL_REVIEW_REQUIRED = "manual_review.required"
    AUDIT_LOG = "audit.log"


@dataclass
class Event:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.AUDIT_LOG
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = ""
    payload: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "payload": self.payload,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class EventBus:
    """
    In-memory event bus for agent communication.
    In production, replace with Kafka, RabbitMQ, or Redis Streams.
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._lock = asyncio.Lock()

    def subscribe(self, event_type: EventType, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event: Event):
        async with self._lock:
            self._event_history.append(event)

        handlers = self._subscribers.get(event.event_type, [])
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(asyncio.create_task(handler(event)))
            else:
                handler(event)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_events_by_correlation(self, correlation_id: str) -> List[Event]:
        return [e for e in self._event_history if e.correlation_id == correlation_id]

    def get_audit_trail(self, correlation_id: str) -> List[dict]:
        events = self.get_events_by_correlation(correlation_id)
        return [e.to_dict() for e in sorted(events, key=lambda x: x.timestamp)]


class MessageQueue:
    """
    Simple async message queue for task distribution.
    In production, use Celery, AWS SQS, or similar.
    """

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def get_queue(self, name: str) -> asyncio.Queue:
        if name not in self._queues:
            self._queues[name] = asyncio.Queue()
        return self._queues[name]

    async def enqueue(self, queue_name: str, message: Any):
        queue = self.get_queue(queue_name)
        await queue.put(message)

    async def dequeue(self, queue_name: str, timeout: float = None) -> Any:
        queue = self.get_queue(queue_name)
        try:
            if timeout:
                return await asyncio.wait_for(queue.get(), timeout)
            return await queue.get()
        except asyncio.TimeoutError:
            return None


event_bus = EventBus()
message_queue = MessageQueue()
