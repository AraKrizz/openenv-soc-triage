from pydantic import BaseModel, Field
from typing import List

class Observation(BaseModel):
    logs: List[str] = Field(description="Recent security logs from the system")
    alert_status: str = Field(description="Current status of the security alert")
    available_tools: List[str] = Field(description="List of commands the agent can run")

class Action(BaseModel):
    command: str = Field(description="The tool to use: 'analyze_log', 'block_ip', 'ignore_alert'")
    target: str = Field(description="The IP address or UserID to act upon")

class Reward(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Progress toward resolving the threat")