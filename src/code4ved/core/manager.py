"""Core LCM Manager implementation."""

import logging
from typing import Any, Dict, List, Optional

from ..config import settings
from ..exceptions import LCMError, LCMConfigError
from .models import LCMConfig, LifecycleStage, Resource

logger = logging.getLogger(__name__)


class LCMManager:
    """Main LCM Manager for lifecycle automation."""

    def __init__(self, config: Optional[LCMConfig] = None):
        """Initialize LCM Manager.

        Args:
            config: Optional LCM configuration object
        """
        self.config = config or LCMConfig.from_settings()
        self.resources: Dict[str, Resource] = {}
        self.stages: List[LifecycleStage] = []

        logger.info(f"LCM Manager initialized with config: {self.config.name}")

    def add_resource(self, resource: Resource) -> None:
        """Add a resource to be managed.

        Args:
            resource: Resource to add

        Raises:
            LCMError: If resource already exists
        """
        if resource.id in self.resources:
            raise LCMError(f"Resource {resource.id} already exists")

        self.resources[resource.id] = resource
        logger.info(f"Added resource: {resource.id}")

    def remove_resource(self, resource_id: str) -> None:
        """Remove a resource from management.

        Args:
            resource_id: ID of resource to remove

        Raises:
            LCMError: If resource not found
        """
        if resource_id not in self.resources:
            raise LCMError(f"Resource {resource_id} not found")

        del self.resources[resource_id]
        logger.info(f"Removed resource: {resource_id}")

    def get_resource(self, resource_id: str) -> Resource:
        """Get a resource by ID.

        Args:
            resource_id: ID of resource to get

        Returns:
            Resource object

        Raises:
            LCMError: If resource not found
        """
        if resource_id not in self.resources:
            raise LCMError(f"Resource {resource_id} not found")

        return self.resources[resource_id]

    def list_resources(self) -> List[Resource]:
        """List all managed resources.

        Returns:
            List of Resource objects
        """
        return list(self.resources.values())

    def add_stage(self, stage: LifecycleStage) -> None:
        """Add a lifecycle stage.

        Args:
            stage: Lifecycle stage to add
        """
        self.stages.append(stage)
        logger.info(f"Added lifecycle stage: {stage.name}")

    def execute_stage(self, stage_name: str, resource_id: str) -> Dict[str, Any]:
        """Execute a lifecycle stage for a resource.

        Args:
            stage_name: Name of stage to execute
            resource_id: ID of resource to process

        Returns:
            Execution result

        Raises:
            LCMError: If stage or resource not found
        """
        # Find stage
        stage = None
        for s in self.stages:
            if s.name == stage_name:
                stage = s
                break

        if not stage:
            raise LCMError(f"Stage {stage_name} not found")

        # Get resource
        resource = self.get_resource(resource_id)

        # Execute stage
        logger.info(f"Executing stage {stage_name} for resource {resource_id}")

        try:
            result = stage.execute(resource)
            logger.info(f"Stage {stage_name} completed successfully for {resource_id}")
            return result
        except Exception as e:
            logger.error(f"Stage {stage_name} failed for {resource_id}: {e}")
            raise LCMError(f"Stage execution failed: {e}")

    def validate_config(self) -> bool:
        """Validate the current configuration.

        Returns:
            True if configuration is valid

        Raises:
            LCMConfigError: If configuration is invalid
        """
        try:
            # Validate configuration
            if not self.config.name:
                raise LCMConfigError("Configuration name is required")

            if not self.config.environment:
                raise LCMConfigError("Environment is required")

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            raise LCMConfigError(f"Configuration validation failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of LCM Manager.

        Returns:
            Status information
        """
        return {
            "config_name": self.config.name,
            "environment": self.config.environment,
            "resource_count": len(self.resources),
            "stage_count": len(self.stages),
            "resources": [r.id for r in self.resources.values()],
            "stages": [s.name for s in self.stages]
        }