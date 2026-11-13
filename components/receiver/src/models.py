"""Models module"""

from pydantic import UUID4, BaseModel, ConfigDict


class PingData(BaseModel):
    """Model for ping data validation"""

    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, validate_default=True
    )

    # Agent key
    key: UUID4
