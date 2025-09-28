"""Unit tests for LCM Manager."""

import pytest

from lcm_automation.core.models import Resource, LifecycleStage, ResourceStatus
from lcm_automation.exceptions import LCMError


class TestLCMManager:
    """Test cases for LCM Manager."""

    def test_manager_initialization(self, lcm_manager):
        """Test manager initialization."""
        assert lcm_manager.config.name == "test-config"
        assert lcm_manager.config.environment == "test"
        assert len(lcm_manager.resources) == 0
        assert len(lcm_manager.stages) == 0

    def test_add_resource(self, lcm_manager, sample_resource):
        """Test adding a resource."""
        lcm_manager.add_resource(sample_resource)

        assert len(lcm_manager.resources) == 1
        assert sample_resource.id in lcm_manager.resources
        assert lcm_manager.resources[sample_resource.id] == sample_resource

    def test_add_duplicate_resource(self, lcm_manager, sample_resource):
        """Test adding duplicate resource raises error."""
        lcm_manager.add_resource(sample_resource)

        with pytest.raises(LCMError, match="already exists"):
            lcm_manager.add_resource(sample_resource)

    def test_remove_resource(self, lcm_manager, sample_resource):
        """Test removing a resource."""
        lcm_manager.add_resource(sample_resource)
        lcm_manager.remove_resource(sample_resource.id)

        assert len(lcm_manager.resources) == 0
        assert sample_resource.id not in lcm_manager.resources

    def test_remove_nonexistent_resource(self, lcm_manager):
        """Test removing nonexistent resource raises error."""
        with pytest.raises(LCMError, match="not found"):
            lcm_manager.remove_resource("nonexistent")

    def test_get_resource(self, lcm_manager, sample_resource):
        """Test getting a resource."""
        lcm_manager.add_resource(sample_resource)
        retrieved = lcm_manager.get_resource(sample_resource.id)

        assert retrieved == sample_resource

    def test_get_nonexistent_resource(self, lcm_manager):
        """Test getting nonexistent resource raises error."""
        with pytest.raises(LCMError, match="not found"):
            lcm_manager.get_resource("nonexistent")

    def test_list_resources(self, lcm_manager, sample_resource):
        """Test listing resources."""
        assert lcm_manager.list_resources() == []

        lcm_manager.add_resource(sample_resource)
        resources = lcm_manager.list_resources()

        assert len(resources) == 1
        assert resources[0] == sample_resource

    def test_add_stage(self, lcm_manager, sample_stage):
        """Test adding a stage."""
        lcm_manager.add_stage(sample_stage)

        assert len(lcm_manager.stages) == 1
        assert lcm_manager.stages[0] == sample_stage

    def test_execute_stage(self, populated_manager):
        """Test executing a stage."""
        result = populated_manager.execute_stage("test-stage", "test-resource-1")

        assert result["stage"] == "test-stage"
        assert result["resource_id"] == "test-resource-1"
        assert result["status"] == "completed"

    def test_execute_nonexistent_stage(self, populated_manager):
        """Test executing nonexistent stage raises error."""
        with pytest.raises(LCMError, match="Stage nonexistent not found"):
            populated_manager.execute_stage("nonexistent", "test-resource-1")

    def test_execute_stage_nonexistent_resource(self, populated_manager):
        """Test executing stage with nonexistent resource raises error."""
        with pytest.raises(LCMError, match="Resource nonexistent not found"):
            populated_manager.execute_stage("test-stage", "nonexistent")

    def test_validate_config(self, lcm_manager):
        """Test configuration validation."""
        assert lcm_manager.validate_config() is True

    def test_get_status(self, populated_manager):
        """Test getting manager status."""
        status = populated_manager.get_status()

        assert status["config_name"] == "test-config"
        assert status["environment"] == "test"
        assert status["resource_count"] == 1
        assert status["stage_count"] == 1
        assert "test-resource-1" in status["resources"]
        assert "test-stage" in status["stages"]