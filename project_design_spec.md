## Design Document: Multi-Agent Research System

### 1. Introduction & PRD Alignment
This design translates the PRD requirements into system components, interfaces, and validation points.

- **Success Metrics (PRD)**
  - Support 5 concurrent agent workflows with < 1 s inter-agent latency.
  - ≥ 95% accuracy on mocked tool responses.
  - ≥ 80% pass rate on automated integration tests.
- **Key User Stories (PRD)**
  1. **Research Manager** submits a CLI research query; manager agent orchestrates sub-agents and returns report.
  2. **Developer** uses a mocked MCP server (JIRA, PDF, Web Search) to validate agent logic.
  3. **QA Engineer** executes error/latency injection scripts to confirm robustness.

---

### 2. Component Overview
- **Agents**: Specialized modules implementing discrete tasks.
- **MCP Server & Client SDK**: Standardized tool access via JSON-RPC.
- **A2A Messaging Layer**: Pub/Sub infrastructure for agent coordination.
- **LangGraph Orchestrator**: Defines and executes workflow graphs.

---

### 3. Agents & Interfaces
Each agent implements a well-defined interface matching PRD deliverables and acceptance criteria.

| Agent            | Responsibility                                    | Input/Output Schema                         |
|------------------|---------------------------------------------------|---------------------------------------------|
| JIRA Agent       | FETCH_TICKET tool call; returns ticket objects    | `{id, status, assignee, summary}`           |
| Doc Agent        | GET_DOC tool call; returns text content           | `{doc_id, markdown, html}`                  |
| PDF Agent        | GET_DOC(tool="PDF"); returns parsed text        | `{url, pages:[{text, page_number}]}`        |
| Search Agent     | SEARCH_WEB tool call; returns search results      | `[{title, snippet, url}]`                   |
| Synthesis Agent  | Aggregates and formats final report               | `{sections:[{title, content}], summary}`    |

**Interfaces** are defined as JSON-RPC methods in the MCP schema; see `mcp_protocol.json`.

---

### 4. MCP Client–Server Design
- **Protocol**: JSON-RPC over HTTP/2 with session IDs.
- **Server**: Routes `GET_DOC`, `FETCH_TICKET`, `SEARCH_WEB`; supports latency and error configs.
- **Client SDK**: Python package exposing:
  - `mcp_client.get_doc(doc_id: str) → DocObject`
  - `mcp_client.fetch_ticket(ticket_id: str) → TicketObject`
  - `mcp_client.search_web(query: str) → List[SearchResult]`

**Acceptance Criteria (PRD)**:
- Default response latency 0–500 ms; configurable up to 1500 ms.
- Deserialized return types matching OpenAPI schemas.
- Mock server error injection toggle for QA tests.

---

### 5. A2A Messaging Layer
- **Message Schemas** (JSON/Protobuf definitions):
  - `TaskRequest { task_id, intent, payload }`
  - `TaskResult  { task_id, status, output }`
  - `Heartbeat   { agent_id, timestamp }`

- **Transport Options**:
  - Redis Pub/Sub: lightweight, easy to set up.
  - Kafka: durable, scalable for future real API phase.

- **Agent Messaging Module** (Python):
  - `send(request: TaskRequest)`, `receive() → TaskRequest`
  - Retry logic with exponential backoff.
  - Deduplication via `task_id` cache.

**Acceptance Criteria (PRD)**:
- < 1 s average delivery latency under nominal load.
- At-least-once delivery with deduplication.
- Fault injection tests (broker down, network packet loss) pass ≥ 80% scenarios.

---

### 6. LangGraph Orchestration
- **Workflow Definition (YAML)** snippet example:
  ```yaml
  graph:
    - name: fetchTickets
      agent: jira_agent
      next: parseDocs
    - name: parseDocs
      agent: doc_agent
      next: searchContext
    - name: searchContext
      agent: search_agent
      fork:
        - synthesis
    - name: synthesis
      agent: synthesis_agent
  ```
- **Execution Model**:
  - Nodes invoke agent interfaces via MCP.
  - Shared state passed as JSON between nodes.
  - Conditional branching and parallel forks supported.

**Acceptance Criteria (PRD)**:
- End-to-end graph completes in < 10 s under nominal load.
- Parallel tasks correctly merge into a single state for synthesis.

---

### 7. Data Flow & Sequence Diagram
*(Include in separate design artifact)*
1. CLI → Manager Agent → LangGraph.
2. LangGraph nodes → MCP Client → MCP Server → Mocked Tools.
3. Agents publish/subscribe via broker for A2A messages.
4. Synthesis → CLI output.

---

### 8. Testing & Observability
- **Testing Scenarios (PRD)**
  | Scenario             | Description                               | Expected Outcome                      |
  |----------------------|-------------------------------------------|---------------------------------------|
  | Happy Path           | Full MCP + A2A without errors             | Report accuracy ≥ 95%                 |
  | Tool Error Injection | Server returns intermittent 500 errors     | Agents retry and succeed              |
  | High Latency         | Simulate 1500 ms delays                   | Workflow completes in < 15 s          |
  | Message Duplication  | Broker delivers duplicates                | No duplicate side effects             |

- **Observability**:
  - Metrics: Prometheus endpoints on each component.
  - Tracing: OpenTelemetry spans for MCP calls and A2A messages.
  - Logging: Structured JSON logs ingested by ELK.

---

### 9. Future Considerations
- Adapter layers for real JIRA/Confluence APIs.
- OAuth2 authentication and role‑based access controls.
- Kubernetes deployment with auto‑scaling agents & broker.
- Enhanced fault tolerance (circuit breakers, bulkheads).

*End of Design Document*

