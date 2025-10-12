# Cursor APM Implementation Guide - Code4Ved Project

This guide provides detailed implementation instructions for using APM agents specifically optimized for Cursor IDE in the Code4Ved project.

## Prerequisites

### Cursor IDE Setup
- **Cursor IDE**: Latest version with Composer and Auto mode enabled
- **APM Framework**: Access to APM prompts and guides
- **Project Workspace**: Code4Ved project directory with proper structure
- **Model Access**: Cursor Pro or equivalent for optimal performance

### Required Extensions
- **APM Extension**: Custom APM workflow extension (if available)
- **Git Integration**: Enhanced Git integration for version control
- **Terminal Integration**: Advanced terminal capabilities
- **File Operations**: Enhanced file operation capabilities

## Cursor-Specific Setup

### 1. Workspace Configuration

**Project Structure Setup:**
```bash
# Navigate to Code4Ved project directory
cd /path/to/Code4Ved

# Verify APM assets are accessible
ls -la prompts/
ls -la docs/agents/

# Create APM session directory
mkdir -p apm/
```

**Cursor Workspace Settings:**
```json
{
  "cursor.general.enableComposer": true,
  "cursor.general.enableAutoMode": true,
  "cursor.general.enableAdvancedIndexing": true,
  "cursor.general.enableRealTimeCollaboration": true,
  "cursor.general.enableContextVisualization": true
}
```

### 2. APM Asset Verification

**Verify APM Assets:**
- Check `prompts/` directory for all required prompts
- Verify `docs/agents/` directory for agent documentation
- Confirm `schemas/` directory for JSON schemas (if using JSON format)
- Validate `guides/` directory for workflow guides

**Cursor-Specific Asset Access:**
```markdown
# Cursor Setup Agent Asset Verification

## Asset Verification Checklist
- [ ] APM prompts accessible via Cursor's file system
- [ ] Agent documentation available in docs/agents/
- [ ] Workflow guides accessible for reference
- [ ] JSON schemas available (if using JSON format)
- [ ] Cursor-specific optimizations enabled

## Cursor-Specific Features
- [ ] Composer integration enabled
- [ ] Auto mode optimization active
- [ ] Advanced codebase understanding enabled
- [ ] Real-time collaboration features available
- [ ] Context visualization enabled
```

## Cursor Setup Agent Implementation

### 1. Initialization

**Create Setup Agent Session:**
1. Open new chat session in Cursor
2. Name session: "Cursor Setup Agent"
3. Enable Composer and Auto mode
4. Provide Cursor-specific initiation prompt

**Cursor-Specific Initiation Prompt:**
```markdown
# Cursor Setup Agent Initiation

You are the Cursor Setup Agent for the Code4Ved project operating under APM v0.4.

## Cursor-Specific Capabilities
- **Composer Integration**: Use Composer for multi-file project analysis
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective operations
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Enhanced Workflow
1. **Asset Verification** - Verify Cursor workspace and APM asset access
2. **Context Synthesis** - Use Cursor's codebase understanding for discovery
3. **Project Breakdown** - Leverage Composer for Implementation Plan creation
4. **Implementation Plan Review** - Use Cursor's diff capabilities
5. **Enhancement & Memory Root Creation** - Create structured memory system
6. **Manager Bootstrap Prompt Creation** - Generate Cursor-optimized bootstrap

## Cursor-Specific Features
- **Multi-file Operations**: Use Composer for simultaneous file operations
- **Context Preservation**: Leverage Cursor's context management
- **Model Optimization**: Utilize Auto mode for cost-effective planning
- **Real-time Validation**: Use Cursor's built-in validation
```

### 2. Context Synthesis

**Cursor-Enhanced Discovery:**
```markdown
# Cursor Context Synthesis

## Cursor-Specific Discovery Questions
1. **Codebase Analysis**: Use Cursor's advanced indexing to analyze existing codebase
2. **Dependency Analysis**: Leverage Cursor's dependency analysis capabilities
3. **Project Structure**: Use Cursor's project structure understanding
4. **Technology Stack**: Analyze current technology stack and requirements

## Cursor-Specific Capabilities
- **Composer Integration**: Use Composer for multi-file analysis
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective discovery
- **Real-time Collaboration**: Use Cursor's collaboration features
- **Context Visualization**: Leverage Cursor's context visualization
```

### 3. Project Breakdown

**Cursor-Optimized Breakdown:**
```markdown
# Cursor Project Breakdown

## Cursor-Specific Breakdown Process
1. **Composer Analysis**: Use Composer for comprehensive project analysis
2. **Multi-file Operations**: Use Composer for simultaneous file operations
3. **Context Preservation**: Leverage Cursor's context management
4. **Real-time Validation**: Use Cursor's built-in validation

## Cursor-Specific Features
- **Composer Integration**: Use Composer for complex project operations
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective operations
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features
```

## Cursor Manager Agent Implementation

### 1. Initialization

**Create Manager Agent Session:**
1. Open new chat session in Cursor
2. Name session: "Cursor Manager Agent"
3. Enable Composer and Auto mode
4. Provide Cursor-specific initiation prompt

**Cursor-Specific Initiation Prompt:**
```markdown
# Cursor Manager Agent Initiation

You are the Cursor Manager Agent for the Code4Ved project operating under APM v0.4.

## Cursor-Specific Capabilities
- **Composer Integration**: Use Composer for complex task assignments
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective coordination
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Enhanced Coordination
- **Session Management**: Optimized for Cursor's multi-session workflow
- **Context Monitoring**: Leverage Cursor's context visualization
- **Composer Integration**: Use Composer for complex task assignments
- **Auto Mode Coordination**: Optimize model selection for different task types

## Cursor-Specific Features
- **Multi-file Operations**: Use Composer for complex task assignments
- **Context Preservation**: Leverage Cursor's context management
- **Model Optimization**: Utilize Auto mode for cost-effective coordination
- **Real-time Validation**: Use Cursor's built-in validation
```

### 2. Task Assignment

**Cursor-Optimized Task Assignment:**
```markdown
# Cursor Task Assignment

## Cursor-Specific Task Assignment
- **Composer Integration**: Use Composer for complex task assignments
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective execution
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Cursor-Specific Features
- **Multi-file Operations**: Use Composer for complex implementations
- **Context Preservation**: Leverage Cursor's context management
- **Model Optimization**: Utilize Auto mode for cost-effective execution
- **Real-time Validation**: Use Cursor's built-in validation
```

## Cursor Implementation Agent Implementation

### 1. Initialization

**Create Implementation Agent Session:**
1. Open new chat session in Cursor
2. Name session: "Cursor Implementation Agent"
3. Enable Composer and Auto mode
4. Provide Cursor-specific initiation prompt

**Cursor-Specific Initiation Prompt:**
```markdown
# Cursor Implementation Agent Initiation

You are a Cursor Implementation Agent for the Code4Ved project operating under APM v0.4.

## Cursor-Specific Capabilities
- **Composer Integration**: Use Composer for multi-file implementations
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective execution
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Enhanced Execution
- **Multi-file Operations**: Use Composer for complex implementations
- **Context Awareness**: Leverage Cursor's codebase understanding
- **Real-time Feedback**: Use Cursor's real-time collaboration features
- **Integrated Debugging**: Leverage Cursor's debugging capabilities

## Cursor-Specific Features
- **Composer Integration**: Use Composer for complex implementations
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective execution
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features
```

### 2. Task Execution

**Cursor-Optimized Execution:**
```markdown
# Cursor Task Execution

## Cursor-Specific Execution
- **Composer Integration**: Use Composer for multi-file implementations
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective execution
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Cursor-Specific Features
- **Multi-file Operations**: Use Composer for complex implementations
- **Context Preservation**: Leverage Cursor's context management
- **Model Optimization**: Utilize Auto mode for cost-effective execution
- **Real-time Validation**: Use Cursor's built-in validation
```

## Cursor Ad-Hoc Agent Implementation

### 1. Initialization

**Create Ad-Hoc Agent Session:**
1. Open new chat session in Cursor
2. Name session: "Cursor Ad-Hoc Agent"
3. Enable Composer and Auto mode
4. Provide Cursor-specific initiation prompt

**Cursor-Specific Initiation Prompt:**
```markdown
# Cursor Ad-Hoc Agent Initiation

You are a Cursor Ad-Hoc Agent for the Code4Ved project operating under APM v0.4.

## Cursor-Specific Capabilities
- **Composer Integration**: Use Composer for complex delegation tasks
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective delegation
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Enhanced Delegation
- **Temporary Sessions**: Optimized for Cursor's temporary session workflow
- **Advanced Research**: Leverage Cursor's web search and analysis capabilities
- **Integrated Tools**: Use Cursor's built-in tools for delegation tasks
- **Context Isolation**: Maintain proper context isolation in temporary sessions

## Cursor-Specific Features
- **Composer Integration**: Use Composer for complex delegation tasks
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective delegation
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features
```

### 2. Delegation Workflow

**Cursor-Optimized Delegation:**
```markdown
# Cursor Delegation Workflow

## Cursor-Specific Delegation
- **Composer Integration**: Use Composer for complex delegation tasks
- **Auto Mode Optimization**: Leverage Auto mode for cost-effective delegation
- **Advanced Codebase Understanding**: Utilize Cursor's indexing capabilities
- **Real-time Collaboration**: Use Cursor's collaboration features

## Cursor-Specific Features
- **Multi-file Operations**: Use Composer for complex delegation tasks
- **Context Preservation**: Leverage Cursor's context management
- **Model Optimization**: Utilize Auto mode for cost-effective delegation
- **Real-time Validation**: Use Cursor's built-in validation
```

## Cursor-Specific Best Practices

### 1. Session Management
- **Clear Naming**: Use descriptive session names for different agent types
- **Context Preservation**: Leverage Cursor's context management features
- **Session Organization**: Organize sessions for optimal workflow
- **Handover Optimization**: Optimize handovers for Cursor's capabilities

### 2. Model Selection
- **Auto Mode Usage**: Leverage Auto mode for cost-effective operations
- **Task-specific Models**: Use appropriate models for different task types
- **Context Optimization**: Optimize for Cursor's context handling
- **Performance Monitoring**: Monitor model performance and costs

### 3. File Operations
- **Composer Integration**: Use Composer for multi-file operations
- **Real-time Validation**: Use Cursor's built-in validation
- **Context Awareness**: Leverage Cursor's codebase understanding
- **Integrated Tools**: Use Cursor's built-in tools and features

### 4. Error Handling
- **Composer Debugging**: Use Composer for complex debugging
- **Auto Mode Debugging**: Leverage Auto mode for cost-effective debugging
- **Integrated Tools**: Use Cursor's built-in debugging capabilities
- **Real-time Collaboration**: Leverage Cursor's collaboration features

## Cursor-Specific Troubleshooting

### Common Issues
1. **Context Window Management**: Monitor Cursor's context window usage
2. **Session Continuity**: Maintain continuity across sessions
3. **Model Switching**: Optimize for Cursor's Auto mode capabilities
4. **File Operations**: Use Cursor's built-in file operations

### Solutions
1. **Context Optimization**: Optimize context usage for Cursor's capabilities
2. **Session Management**: Use Cursor's session management features
3. **Model Selection**: Leverage Auto mode for optimal model selection
4. **Tool Integration**: Use Cursor's built-in tools and features

## Conclusion

This Cursor-specific APM implementation guide provides enhanced capabilities for the Code4Ved project, leveraging Cursor IDE's unique features including Composer, Auto mode, and advanced codebase understanding. The implementation is optimized for Cursor's workflow and provides enhanced productivity and efficiency for complex project management tasks.
