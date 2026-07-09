from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal

class CreateScheduledTaskArgs(BaseModel):
    taskType: str
    platforms: List[str] = Field(default_factory=list)
    topic: str
    language: Optional[str] = "en"
    scheduleAt: Optional[str] = None
    timezone: Optional[str] = "UTC"
    constraints: Optional[Dict[str, Any]] = None

class ToolCall(BaseModel):
    toolCallId: str
    function: Dict[str, Any]  # { name, arguments }

class VapiToolCallsMessage(BaseModel):
    type: Literal["tool-calls"]
    toolCallList: List[ToolCall]
    call: Optional[Dict[str, Any]] = None

class VapiToolCallsEnvelope(BaseModel):
    message: VapiToolCallsMessage
