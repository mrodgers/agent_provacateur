# Phase 2: A2A Communication Implementation

This document outlines the implementation details for Phase 2 of the Agent Provocateur project: Agent-to-Agent (A2A) Communication Development.

## Components

### 1. Message Schema
- Implemented in `a2a_models.py`
- Defines structured message types for agent communication:
  - `TaskRequest`: Requests from one agent to another
  - `TaskResult`: Results returned from task execution
  - `Heartbeat`: Status and health updates from agents
- Uses Pydantic for validation and serialization
- Supports message deduplication via unique keys

### 2. Messaging Infrastructure
- In-memory implementation: `InMemoryMessageBroker` (for development/testing)
- Redis implementation: `RedisMessageBroker` (for production)
- Both implementations provide:
  - Publish/subscribe functionality
  - Topic-based message routing
  - Message deduplication
  - Message persistence

### 3. Agent Messaging Module
- `AgentMessaging` class in `a2a_messaging.py`
- Features:
  - Typed methods for sending and receiving messages
  - Task request/response pattern
  - Callback registration for message handlers
  - Retry logic with exponential backoff
  - Deduplication via message IDs
  - Heartbeat mechanism

### 4. Base Agent Framework
- `BaseAgent` class in `agent_base.py`
- Provides:
  - Standard lifecycle (start/stop)
  - Task handling infrastructure
  - Integration with MCP tools
  - Heartbeat functionality
  - Error handling and logging

### 5. Agent Implementations
- Implemented specialized agents:
  - `JiraAgent`: Fetches JIRA tickets
  - `DocAgent`: Retrieves documents
  - `PdfAgent`: Gets PDF content
  - `SearchAgent`: Performs web searches
  - `SynthesisAgent`: Combines results into a report
  - `ManagerAgent`: Orchestrates workflows between agents

### 6. Sample Workflow
- Demonstration of end-to-end agent collaboration
- Features:
  - Multi-agent coordination
  - Error handling
  - Parallel task execution
  - Consolidated reporting

## Testing

The implementation includes comprehensive test coverage:
- Unit tests for message models
- Tests for the messaging broker
- Tests for agent task handling
- End-to-end workflow tests
- Fault injection tests

## Usage Examples

### Basic Agent Communication

```python
# Create a shared broker
broker = InMemoryMessageBroker()

# Create agents
agent1 = BaseAgent("agent1", broker)
agent2 = BaseAgent("agent2", broker)

# Start agents
await agent1.start()
await agent2.start()

# Send a request and wait for response
result = await agent1.send_request_and_wait(
    target_agent="agent2",
    intent="some_task",
    payload={"key": "value"},
)

# Process the result
if result and result.status == TaskStatus.COMPLETED:
    print(f"Task completed: {result.output}")
else:
    print(f"Task failed: {result.error}")
```

### Running the Sample Workflow

```bash
# Start the MCP server
ap-server

# In another terminal, run the sample workflow
ap-workflow "research query" --ticket AP-1 --doc doc1
```

## Success Metrics

Based on the PRD acceptance criteria:

1. ✅ **Message Latency**: Under nominal load, messages are delivered with < 1 s latency 
2. ✅ **Delivery Guarantee**: At-least-once delivery with deduplication
3. ✅ **Workflow Completion**: Sample workflow completes in ≤ 10 s
4. ✅ **Fault Tolerance**: Passes test scenarios with error injection and latency simulation

## Next Steps

1. Integration with real external systems (JIRA, document repositories)
2. Enhanced monitoring and observability
3. Deployment automation
4. Security hardening