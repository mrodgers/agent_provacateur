## Product Requirements Document (PRD): Multi-Agent Research System

**Summary:** This PRD now incorporates a new XML‑driven research use case: agents must parse input XML documentation, extract domain entities via an LLM, and dynamically research each entity’s definition by invoking Search, JIRA, Doc, and PDF agents. The output is a validated XML with `<entity>` and `<definition>` elements. Success metrics are extended to include definition accuracy and XML schema compliance, and a new Phase 3 is introduced to deliver parsing, extraction, research orchestration, and XML generation. ([docs.anthropic.com](https://docs.anthropic.com/en/docs/agents-and-tools/mcp?utm_source=chatgpt.com), [developers.googleblog.com](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com), [learn.microsoft.com](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview?utm_source=chatgpt.com), [developer.atlassian.com](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/?utm_source=chatgpt.com))

---

### 1. Overview & Scope
The Multi-Agent Research System enables modular agents to collaboratively perform end-to-end research tasks against structured and unstructured data sources. The system leverages:

- **Model Context Protocol (MCP)** for standardized, context-rich interactions via JSON-RPC 2.0. ([modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-03-26?utm_source=chatgpt.com))  
- **Agent-to-Agent (A2A)** communication for dynamic task delegation via a pub/sub layer. ([developers.googleblog.com](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/?utm_source=chatgpt.com))  

**Success Metrics:**
- Handle **5 concurrent agent workflows** end-to-end with **<1 s** average inter-agent message latency.  
- Mock tool accuracy ≥ 95% for simulated responses.  
- ≥ 80% pass rate on automated integration tests.  
- **Entity Definition Accuracy ≥ 90%** against a curated reference set.  
- Final XML output must validate against the DocBook XSD/DTD. ([docbook.org](https://docbook.org/schemas/?utm_source=chatgpt.com))

---

### 2. Goals & User Stories
**Personas:**
- **Research Manager:** Orchestrates high-level research tasks.  
- **Developer:** Implements and tests agent behaviors and protocols.  
- **QA Engineer:** Validates protocol compliance and system reliability.

**User Stories:**
1. **As a Research Manager**, I want to submit a free-text query via CLI so that a manager agent coordinates JIRA, Doc, and Search agents to return a consolidated report.  
2. **As a Developer**, I want a mocked MCP server that simulates JIRA, PDF, and Web Search tools so I can test agent logic without external dependencies.  
3. **As a QA Engineer**, I want scenario scripts that inject errors and latency so I can validate agent robustness under failure conditions.  
4. **As a Research Manager**, I want to supply an XML document containing technical content so that agents can extract entities, research definitions, and produce a validated output XML. ([reddit.com](https://www.reddit.com/r/MachineLearning/comments/1dwbcp5/d_entity_extraction_with_llms/?utm_source=chatgpt.com), [reddit.com](https://www.reddit.com/r/OpenAIDev/comments/14j9svf/how_do_i_implement_named_entity_recognition_with/?utm_source=chatgpt.com))

---

### 3. Phase 1: MCP Tools Development
**Objective:** Build and validate a mock MCP client–server architecture with simulated data sources.

**Deliverables:**
- **MCP Server Mock:** Supports `GET_DOC`, `FETCH_TICKET`, `SEARCH_WEB`, with configurable latency and error injection.
- **MCP Client SDK:** Python package exposing typed methods for tool calls (`get_doc`, `fetch_ticket`, `search_web`).
- **CLI Demo:** Basic CLI application demonstrating a multi-tool research workflow.
- **Documentation:** SDK reference and JSON-RPC schema. ([modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-03-26?utm_source=chatgpt.com))

**Acceptance Criteria:**
- Mock server responds within **0–500 ms** by default; latency simulation configurable up to **60 s** to model delayed agent behavior.
- SDK methods return deserialized objects matching OpenAPI schemas.
- CLI demo executes a complete workflow and prints a formatted report.
- ≥ 90% line coverage on unit tests.

---

### 4. Phase 2: A2A Communication Development
**Objective:** Enable structured, reliable communication and task delegation between agents.

**Deliverables:**
- **Message Schema:** JSON/Protobuf definitions for `TaskRequest`, `TaskResult`, and `Heartbeat` messages.  
- **Pub/Sub Infrastructure:** Choice of Redis Pub/Sub or Kafka with deployment scripts.  
- **Agent Messaging Module:** Python library for sending, receiving, retrying, and deduplicating messages.  
- **Sample Workflow:** Demo where JIRA → Doc → Search → Synthesis agents collaborate on a query.  

**Acceptance Criteria:**
- Agents exchange messages with < 1 s delivery latency under nominal load.  
- Guaranteed-at-least-once delivery semantics with deduplication.  
- Demo workflow completes in ≤ 10 s.  
- ≥ 80% pass rate on fault-injection tests.

---

### 5. Phase 3: XML‑Driven Entity Research
**Objective:** Parse XML, extract entities, orchestrate definition research across agents, and generate a validated output XML.

**Deliverables:**
- **XML Parser Agent:** Parses input XML and emits raw entity candidates.  
- **Entity Extraction Agent:** Uses LLM to refine entity list.  
- **Definition Orchestrator:** Fans out `ResearchEntity` intents to LLM, Search, JIRA, Doc, PDF agents and aggregates results.  
- **Output XML Generator:** Produces a DocBook‑compliant XML with `<entity>` and `<definition>` tags.  
- **CLI Integration:** Extend CLI to accept XML input and return output XML.  

**Acceptance Criteria:**
- Parse and extract up to 50 entities in < 2 s.  
- Complete definition research in < 10 s with ≥ 90% accuracy.  
- Generated XML validates against the DocBook schema (XSD/DTD) with zero errors.  
- Fan‑out research calls maintain consistency and deduplication. ([modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-03-26?utm_source=chatgpt.com), [langchain.com](https://www.langchain.com/langgraph?utm_source=chatgpt.com))

---

### 6. Testing & Validation
| Scenario                    | Description                                | Expected Outcome                                             |
|-----------------------------|--------------------------------------------|--------------------------------------------------------------|
| Happy Path                  | Full MCP + A2A + XML research workflow     | Definitions accuracy ≥ 90%; XML valid                         |
| Tool Error Injection        | Mock server or Search/JIRA returns errors  | Agents retry; fallback to LLM-only definition                 |
| Malformed XML               | Invalid or missing tags in input XML       | Parser Agent raises clear error; CLI exits gracefully         |
| Fan‑Out Concurrency         | 20 parallel `ResearchEntity` calls         | All definitions succeed or retry within timeout               |
| Schema Validation           | Final XML against DocBook XSD/DTD          | Zero validation errors                                        |

---

### 7. Future Considerations
- **Real API Integration:** Adapter layers for Jira Cloud API, enterprise PDFs, and search engines like Bing Web Search API. ([developer.atlassian.com](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/?utm_source=chatgpt.com), [learn.microsoft.com](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/overview?utm_source=chatgpt.com))  
- **Security & Permissions:** OAuth2 scopes per agent; TLS encryption in transit.  
- **Scalability:** Kubernetes deployment for MCP server and broker; auto‑scaling agents.  
- **Observability:** Prometheus metrics, OpenTelemetry tracing, ELK‑based logging.  

---

*End of Updated PRD*

