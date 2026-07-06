"""
Base Agent Class for All Specialized Agents
Implements common functionality and interface contracts
"""

import asyncio
import time
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import sys
sys.path.insert(0, '/home/ubuntu/rs_bank_agentic_loan_platform')

from core.models import (
    AgentResult, AgentStatus, LoanApplication, AuditEntry
)
from core.event_bus import Event, EventType, event_bus
from core.explainability import ExplanationNode, audit_logger


class BaseAgent(ABC):
    """
    Abstract base class for all loan processing agents.
    Provides common functionality for logging, events, and audit trails.
    """

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.agent_id = str(uuid.uuid4())[:8]
        self.name = name
        self.description = description
        self.version = version
        self.is_active = True

    @abstractmethod
    async def analyze(
        self,
        application: LoanApplication,
        context: Dict[str, Any]
    ) -> AgentResult:
        """
        Analyze the loan application and return results.
        Must be implemented by all specialized agents.
        """
        pass

    @abstractmethod
    def get_explanations(self) -> List[ExplanationNode]:
        """Return explainable factors from the analysis."""
        pass

    async def execute(
        self,
        application: LoanApplication,
        context: Dict[str, Any],
        correlation_id: str
    ) -> AgentResult:
        """
        Execute the agent with full instrumentation.
        Handles events, timing, and audit logging.
        """
        start_time = time.time()

        await self._publish_started(correlation_id, application.application_id)

        try:
            result = await self.analyze(application, context)
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time

            self._log_audit(
                correlation_id,
                "analyze",
                {"application_id": application.application_id},
                {"score": result.score, "status": result.status.value},
                f"Completed analysis with score {result.score:.1f}",
                processing_time
            )

            await self._publish_completed(correlation_id, result)
            return result

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            await self._publish_failed(correlation_id, str(e))

            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                status=AgentStatus.FAILED,
                score=0,
                confidence=0,
                findings=[f"Agent failed: {str(e)}"],
                recommendations=["Manual review required due to processing error"],
                flags=["AGENT_ERROR"],
                explanations=[],
                processing_time_ms=processing_time,
                raw_data={"error": str(e)},
            )

    async def _publish_started(self, correlation_id: str, application_id: str):
        event = Event(
            event_type=EventType.AGENT_STARTED,
            source=self.name,
            correlation_id=correlation_id,
            payload={
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "application_id": application_id,
            },
        )
        await event_bus.publish(event)

    async def _publish_completed(self, correlation_id: str, result: AgentResult):
        event = Event(
            event_type=EventType.AGENT_COMPLETED,
            source=self.name,
            correlation_id=correlation_id,
            payload={
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "score": result.score,
                "status": result.status.value,
                "flags": result.flags,
            },
        )
        await event_bus.publish(event)

    async def _publish_failed(self, correlation_id: str, error: str):
        event = Event(
            event_type=EventType.AGENT_FAILED,
            source=self.name,
            correlation_id=correlation_id,
            payload={
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "error": error,
            },
        )
        await event_bus.publish(event)

    def _log_audit(
        self,
        correlation_id: str,
        action: str,
        input_summary: dict,
        output_summary: dict,
        explanation: str,
        duration_ms: float
    ):
        audit_logger.log(
            correlation_id=correlation_id,
            agent_name=self.name,
            action=action,
            input_summary=input_summary,
            output_summary=output_summary,
            explanation=explanation,
            duration_ms=duration_ms,
        )

    def log(self, message: str):
        print(f"  [{self.name}] {message}")

    def health_check(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": "healthy" if self.is_active else "inactive",
        }
