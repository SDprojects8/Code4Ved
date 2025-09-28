"""Test configuration and fixtures."""

import pytest

from lcm_automation.core import LCMManager
from lcm_automation.core.models import LCMConfig, Resource, LifecycleStage, ResourceStatus


@pytest.fixture
def sample_config():
    """Sample LCM configuration for testing."""
    return LCMConfig(
        name="test-config",
        environment="test",
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def lcm_manager(sample_config):
    """LCM Manager instance for testing."""
    return LCMManager(config=sample_config)


@pytest.fixture
def sample_resource():
    """Sample resource for testing."""
    return Resource(
        id="test-resource-1",
        name="Test Resource",
        type="test",
        status=ResourceStatus.CREATED
    )


@pytest.fixture
def sample_stage():
    """Sample lifecycle stage for testing."""
    return LifecycleStage(
        name="test-stage",
        description="Test stage for unit tests",
        order=1,
        actions=["test_action"]
    )


@pytest.fixture
def populated_manager(lcm_manager, sample_resource, sample_stage):
    """LCM Manager with sample data for testing."""
    lcm_manager.add_resource(sample_resource)
    lcm_manager.add_stage(sample_stage)
    return lcm_manager