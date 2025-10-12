"""Test configuration and fixtures."""

import pytest

from Code4Ved_automation.core import Code4VedManager
from Code4Ved_automation.core.models import Code4VedConfig, Resource, LifecycleStage, ResourceStatus


@pytest.fixture
def sample_config():
    """Sample Code4Ved configuration for testing."""
    return Code4VedConfig(
        name="test-config",
        environment="test",
        debug=True,
        log_level="DEBUG"
    )


@pytest.fixture
def Code4Ved_manager(sample_config):
    """Code4Ved Manager instance for testing."""
    return Code4VedManager(config=sample_config)


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
def populated_manager(Code4Ved_manager, sample_resource, sample_stage):
    """Code4Ved Manager with sample data for testing."""
    Code4Ved_manager.add_resource(sample_resource)
    Code4Ved_manager.add_stage(sample_stage)
    return Code4Ved_manager