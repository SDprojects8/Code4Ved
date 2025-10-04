# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Code4Ved is an code4ved (Life Cycle Management) Automation project with an integrated Agentic Project Management (APM) framework. The project combines lifecycle automation capabilities with a sophisticated multi-agent workflow system designed for managing complex projects with AI assistants.

### Dual Purpose Architecture

1. **code4ved Automation Component**: Python-based CLI tool for managing lifecycle stages and resources
2. **APM Framework**: Multi-agent workflow system with prompts, guides, and schemas for AI-assisted project management

## Development Commands

### Python Package Management
```bash
# Install dependencies
pip install -r requirements.txt

# Install with development dependencies
pip install -e ".[dev]"

# Install with test dependencies
pip install -e ".[test]"
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests

# Run specific test file
pytest tests/01_FUT_functional_unit_tests/test_manager.py
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Type checking with MyPy
mypy src/

# Linting with flake8
flake8 src/ tests/
```

### CLI Usage
```bash
# Show version
code4ved version

# Show status
code4ved status

# Validate configuration
code4ved validate

# Resource management
code4ved resource list
code4ved resource add <id> --name <name> --type <type>
code4ved resource show <id>
code4ved resource remove <id>

# Stage management
code4ved stage add <name> --description <desc> --order <num>
code4ved stage execute <stage_name> <resource_id>
```

## Code Architecture

### Core code4ved Components

**src/code4ved/core/**: Core business logic
- `manager.py`: code4vedManager class coordinating resource and lifecycle management
- `models.py`: Pydantic models for Resource, LifecycleStage, ExecutionPlan with status enums

**src/code4ved/cli/**: CLI interface using Typer and Rich for formatted output

**src/code4ved/config/**: Configuration management using python-dotenv and settings

**src/code4ved/utils/**: Helper utilities for logging and common functions

### APM Framework Structure

**prompts/**: Multi-agent workflow prompts and guides
- `Setup_Agent/`: Project initialization and planning
- `Manager_Agent/`: Task coordination and review
- `Implementation_Agent/`: Task execution
- `ad-hoc/`: Temporary agent delegation guides
- `schemas/`: JSON schema definitions (testing/research preview)
- `guides/`: Process guides for project breakdown, memory management, task assignment

**docs/agents/**: APM framework documentation
- Workflow overviews, agent types, context management
- Token consumption optimization tips
- Visual guides (PDFs) for users

**project-management/**: Template structure with 12 phases
- Structured from 00_inbox through 11_retrospective
- Comprehensive templates for charter, research, specifications, planning, design, implementation, testing, release, operations, documentation, retrospective, and risk management

### Data Flow

1. **code4ved Manager** (`manager.py`) initializes with configuration from settings
2. **Resources** added to manager's internal registry (dict-based storage)
3. **Lifecycle Stages** registered with manager in execution order
4. **Stage Execution** processes resources through ordered stages via `execute_stage()`
5. **Results** returned as structured dicts with status, metadata, timestamps

### APM Multi-Agent Pattern

The APM framework uses separate chat sessions as isolated agent instances:
- **Setup Agent**: Project discovery → Implementation Plan creation → Memory system initialization
- **Manager Agent**: Reads plans/logs → Creates Task Assignment Prompts → Reviews execution
- **Implementation Agents**: Execute focused task assignments → Log outcomes to Memory system
- **Ad-Hoc Agents**: Handle isolated debugging/research in workflow branches

Memory management uses either single-file Memory Bank (≤8 tasks) or Dynamic directory structure (>8 tasks) mapped to Implementation Plan phases.

### Key Design Patterns

- **Pydantic Models**: All data structures use Pydantic BaseModel for validation
- **Enum-based Status**: ResourceStatus, StageStatus, EnvironmentType for type safety
- **Manager Pattern**: Central code4vedManager coordinates all operations
- **CLI Architecture**: Typer groups for resource/stage subcommands
- **Configuration**: Settings class loaded from environment/dotenv files
- **Multi-Agent Coordination**: Handover protocols maintain context continuity across agent instances

## Project-Specific Notes

### PowerShell Scripts
- `001-get_proj_strct.ps1`: Project structure generation script
- `scripts/Generate-UpdatePlan.ps1`: Update plan generation

### External Data
`data/external/`: Contains Obsidian markdown notes (2025-04-* daily notes, Vedas.md) used for project context

### Current Branch Context
Working branch: `001-codex-fill_proj_mgmt_from_obsidian_data`
- Purpose: Populating project management templates from Obsidian data
- Main branch: `main`

### Testing Organization
Tests organized by category in `tests/01_FUT_functional_unit_tests/`

### Package Configuration
- Package name: `code4ved-automation` (pyproject.toml)
- Module import: `from code4ved import ...` or `from code4ved_automation.cli.main import ...`
- Python compatibility: >=3.8
