#!/usr/bin/env python3
"""Basic usage example for LCM Automation."""

import logging
from lcm_automation import LCMManager
from lcm_automation.core.models import Resource, LifecycleStage, ResourceStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Demonstrate basic LCM Automation usage."""
    print("🚀 LCM Automation - Basic Usage Example")
    print("=" * 50)

    # Create LCM Manager
    manager = LCMManager()
    print(f"✅ Created LCM Manager: {manager.config.name}")

    # Create some resources
    resources = [
        Resource(
            id="web-server-1",
            name="Production Web Server",
            type="server",
            status=ResourceStatus.CREATED
        ),
        Resource(
            id="database-1",
            name="Primary Database",
            type="database",
            status=ResourceStatus.CREATED
        ),
        Resource(
            id="load-balancer-1",
            name="Main Load Balancer",
            type="load_balancer",
            status=ResourceStatus.CREATED
        )
    ]

    # Add resources to manager
    for resource in resources:
        manager.add_resource(resource)
        print(f"➕ Added resource: {resource.name} ({resource.id})")

    # Create lifecycle stages
    stages = [
        LifecycleStage(
            name="provision",
            description="Provision infrastructure resources",
            order=1,
            actions=["create_instance", "configure_network", "setup_security"]
        ),
        LifecycleStage(
            name="deploy",
            description="Deploy application code",
            order=2,
            actions=["upload_code", "install_dependencies", "start_services"]
        ),
        LifecycleStage(
            name="test",
            description="Run automated tests",
            order=3,
            actions=["health_check", "integration_test", "performance_test"]
        ),
        LifecycleStage(
            name="monitor",
            description="Setup monitoring and alerting",
            order=4,
            actions=["configure_monitoring", "setup_alerts", "create_dashboards"]
        )
    ]

    # Add stages to manager
    for stage in stages:
        manager.add_stage(stage)
        print(f"🔄 Added stage: {stage.name} (order: {stage.order})")

    print("\n" + "=" * 50)

    # Show current status
    print("📊 Current LCM Status:")
    status = manager.get_status()
    for key, value in status.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\n" + "=" * 50)

    # Execute stages for each resource
    print("🎯 Executing Lifecycle Stages:")
    for stage in sorted(stages, key=lambda s: s.order):
        print(f"\n🔄 Executing stage: {stage.name}")
        for resource in resources:
            try:
                result = manager.execute_stage(stage.name, resource.id)
                print(f"  ✅ {resource.id}: {result['status']}")
            except Exception as e:
                print(f"  ❌ {resource.id}: {e}")

    print("\n" + "=" * 50)

    # List all resources
    print("📋 Final Resource List:")
    all_resources = manager.list_resources()
    for resource in all_resources:
        print(f"  🔹 {resource.id}: {resource.name} ({resource.type}) - {resource.status}")

    print("\n✨ Example completed successfully!")


if __name__ == "__main__":
    main()