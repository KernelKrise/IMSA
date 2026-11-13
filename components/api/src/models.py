"""Models module"""

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict, Field


class AgentStatus(StrEnum):
    """Agent status enum"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Agent(BaseModel):
    """Model for agent data validation"""

    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, validate_default=True
    )

    # Agent ID
    id_: int | None = None

    # Key
    key: UUID4 = Field(default_factory=uuid4)

    # Name
    name: str = Field(min_length=1, max_length=256)

    # Description
    description: str | None = Field(min_length=1, max_length=1024, default=None)

    # Status
    status: AgentStatus = AgentStatus.INACTIVE

    # Agent last seen
    last_seen: datetime = Field(
        default_factory=lambda: datetime.fromtimestamp(0, tz=timezone.utc)
    )

    # Agent creation time
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentDeletionRequest(BaseModel):
    """Model for agent deletion request data validation"""

    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, validate_default=True
    )

    # Agent ID
    id_: int
