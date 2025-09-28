"""Core data models for LCM Automation."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EnvironmentType(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ResourceStatus(str, Enum):
    """Resource status types."""
    CREATED = "created"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    ERROR = "error"


class StageStatus(str, Enum):
    """Stage execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class LCMConfig(BaseModel):
    """LCM Configuration model."""

    name: str = Field(..., description="Configuration name")
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    max_retries: int = Field(default=3, ge=0)
    timeout_seconds: int = Field(default=300, ge=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_settings(cls) -> "LCMConfig":
        """Create configuration from settings.

        Returns:
            LCMConfig instance
        """
        from ..config import settings

        return cls(
            name=settings.APP_NAME,
            environment=settings.APP_ENV,
            debug=settings.DEBUG,
            log_level=settings.LOG_LEVEL,
        )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class Resource(BaseModel):
    """Resource model."""

    id: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Resource name")
    type: str = Field(..., description="Resource type")
    status: ResourceStatus = Field(default=ResourceStatus.CREATED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)

    def update_status(self, status: ResourceStatus) -> None:
        """Update resource status.

        Args:
            status: New status
        """
        self.status = status
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the resource.

        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the resource.

        Args:
            tag: Tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def set_property(self, key: str, value: Any) -> None:
        """Set a resource property.

        Args:
            key: Property key
            value: Property value
        """
        self.properties[key] = value
        self.updated_at = datetime.utcnow()

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class LifecycleStage(BaseModel):
    """Lifecycle stage model."""

    name: str = Field(..., description="Stage name")
    description: Optional[str] = Field(None, description="Stage description")
    order: int = Field(..., description="Execution order", ge=0)
    required: bool = Field(default=True, description="Whether stage is required")
    timeout_seconds: int = Field(default=300, ge=1)
    retry_count: int = Field(default=0, ge=0)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    actions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def execute(self, resource: Resource) -> Dict[str, Any]:
        """Execute the stage for a resource.

        Args:
            resource: Resource to process

        Returns:
            Execution result
        """
        # This is a placeholder implementation
        # In a real implementation, this would execute the actual stage logic

        result = {
            "stage": self.name,
            "resource_id": resource.id,
            "status": StageStatus.COMPLETED,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "actions_executed": self.actions,
            "metadata": self.metadata
        }

        return result

    def can_execute(self, resource: Resource) -> bool:
        """Check if stage can be executed for a resource.

        Args:
            resource: Resource to check

        Returns:
            True if stage can be executed
        """
        # Check basic conditions
        if resource.status == ResourceStatus.ERROR and self.required:
            return False

        # Check custom conditions
        for condition, expected_value in self.conditions.items():
            if condition in resource.properties:
                if resource.properties[condition] != expected_value:
                    return False

        return True

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ExecutionPlan(BaseModel):
    """Execution plan model."""

    id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Plan name")
    resource_ids: List[str] = Field(..., description="Resources to process")
    stages: List[str] = Field(..., description="Stages to execute")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: StageStatus = Field(default=StageStatus.PENDING)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""
        use_enum_values = True