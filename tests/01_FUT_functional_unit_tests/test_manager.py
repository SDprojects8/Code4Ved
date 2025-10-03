"""Unit tests for Code4Ved Manager."""

import pytest

from Code4Ved_automation.core.models import Resource, LifecycleStage, ResourceStatus
from Code4Ved_automation.exceptions import Code4VedError


class TestCode4VedManager:
    """Test cases for Code4Ved Manager."""

    def test_manager_initialization(self, Code4Ved_manager):
        """Test manager initialization."""
        assert Code4Ved_manager.config.name == "test-config"
        assert Code4Ved_manager.config.environment == "test"
        assert len(Code4Ved_manager.resources) == 0
        assert len(Code4Ved_manager.stages) == 0

    def test_add_resource(self, Code4Ved_manager, sample_resource):
        """Test adding a resource."""
        Code4Ved_manager.add_resource(sample_resource)

        assert len(Code4Ved_manager.resources) == 1
        assert sample_resource.id in Code4Ved_manager.resources
        assert Code4Ved_manager.resources[sample_resource.id] == sample_resource

    def test_add_duplicate_resource(self, Code4Ved_manager, sample_resource):
        """Test adding duplicate resource raises error."""
        Code4Ved_manager.add_resource(sample_resource)

        with pytest.raises(Code4VedError, match="already exists"):
            Code4Ved_manager.add_resource(sample_resource)

    def test_remove_resource(self, Code4Ved_manager, sample_resource):
        """Test removing a resource."""
        Code4Ved_manager.add_resource(sample_resource)
        Code4Ved_manager.remove_resource(sample_resource.id)

        assert len(Code4Ved_manager.resources) == 0
        assert sample_resource.id not in Code4Ved_manager.resources

    def test_remove_nonexistent_resource(self, Code4Ved_manager):
        """Test removing nonexistent resource raises error."""
        with pytest.raises(Code4VedError, match="not found"):
            Code4Ved_manager.remove_resource("nonexistent")

    def test_get_resource(self, Code4Ved_manager, sample_resource):
        """Test getting a resource."""
        Code4Ved_manager.add_resource(sample_resource)
        retrieved = Code4Ved_manager.get_resource(sample_resource.id)

        assert retrieved == sample_resource

    def test_get_nonexistent_resource(self, Code4Ved_manager):
        """Test getting nonexistent resource raises error."""
        with pytest.raises(Code4VedError, match="not found"):
            Code4Ved_manager.get_resource("nonexistent")

    def test_list_resources(self, Code4Ved_manager, sample_resource):
        """Test listing resources."""
        assert Code4Ved_manager.list_resources() == []

        Code4Ved_manager.add_resource(sample_resource)
        resources = Code4Ved_manager.list_resources()

        assert len(resources) == 1
        assert resources[0] == sample_resource

    def test_add_stage(self, Code4Ved_manager, sample_stage):
        """Test adding a stage."""
        Code4Ved_manager.add_stage(sample_stage)

        assert len(Code4Ved_manager.stages) == 1
        assert Code4Ved_manager.stages[0] == sample_stage

    def test_execute_stage(self, populated_manager):
        """Test executing a stage."""
        result = populated_manager.execute_stage("test-stage", "test-resource-1")

        assert result["stage"] == "test-stage"
        assert result["resource_id"] == "test-resource-1"
        assert result["status"] == "completed"

    def test_execute_nonexistent_stage(self, populated_manager):
        """Test executing nonexistent stage raises error."""
        with pytest.raises(Code4VedError, match="Stage nonexistent not found"):
            populated_manager.execute_stage("nonexistent", "test-resource-1")

    def test_execute_stage_nonexistent_resource(self, populated_manager):
        """Test executing stage with nonexistent resource raises error."""
        with pytest.raises(Code4VedError, match="Resource nonexistent not found"):
            populated_manager.execute_stage("test-stage", "nonexistent")

    def test_validate_config(self, Code4Ved_manager):
        """Test configuration validation."""
        assert Code4Ved_manager.validate_config() is True

    def test_get_status(self, populated_manager):
        """Test getting manager status."""
        status = populated_manager.get_status()

        assert status["config_name"] == "test-config"
        assert status["environment"] == "test"
        assert status["resource_count"] == 1
        assert status["stage_count"] == 1
        assert "test-resource-1" in status["resources"]
        assert "test-stage" in status["stages"]