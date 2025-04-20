## Design Document: Multi-Agent Research System

### 1. Introduction & PRD Alignment
This design implements the PRD requirements and extends the existing architecture to support XML‑driven technical‑documentation workflows with deep entity research.

- **PRD Success Metrics**
  - Handle 5 concurrent agent workflows with < 1 s inter‑agent latency.
  - ≥ 95% accuracy on mocked tool responses.
  - ≥ 80% pass rate on automated integration tests.
- **New Use Case**
  - Input: XML document with technical documentation.
  - Process: Extract entities, research definitions via LLM and existing agents (Search, JIRA, Doc, PDF), generate new XML with `<entity>` and `<definition>` elements.
- **Key User Stories**
  1. **Research Manager** supplies an XML file; manager agent orchestrates entity extraction and definition research.
  2. **Developer** builds agents that parse XML, identify entities, and call LLM and tool agents to gather definitions.
  3. **QA Engineer** validates error handling for missing tags, ambiguous entities, and tool failures.

---

### 2. Component Overview (Extended)
- **Agents**: Modular agents, including XML Parser, Entity Extraction, Definition (which may call external agents), Search, and Synthesis.
- **MCP Server & Client SDK**: JSON‑RPC for tool and agent calls, extended for XML and research workflows.
- **A2A Messaging Layer**: Pub/Sub for agent coordination with new research intent.
- **LangGraph Orchestrator**: Drives extraction, research fan‑out, and output assembly.

---

### 3. Agents & Interfaces (Updated)
| Agent                   | Responsibility                                                                                   | Input/Output Schema                                                |
|-------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| XML Parser Agent        | Parses input XML; extracts text nodes and raw entity candidates                                  | `{doc_id, xml_raw, entities:[{tag, text, path}]}`                  |
| Entity Extraction Agent | Refines raw candidates via LLM to filter and classify entities                                    | `{entities:[{name, type, context, path}]}`                         |
| Definition Agent        | Coordinates research for each entity: invokes LLM, then optionally calls Search, JIRA, Doc, or PDF agents for verification and context | `{definitions:[{entity, definition, sources:[{tool, details, url}]}]}`     |
| Search Agent            | Performs web searches for external validation                                                    | `[{title, snippet, url}]`                                           |
| JIRA Agent              | Queries ticket data for entity context (if relevant)                                            | `{id, status, assignee, summary, description}`                     |
| Doc Agent               | Retrieves and parses structured docs for entity context                                          | `{doc_id, markdown, html}`                                          |
| PDF Agent               | Handles PDF retrieval and parsing for entity context                                            | `{url, pages:[{text, page_number}]}`                                |
| Synthesis Agent         | Aggregates entity definitions into final output XML                                              | `{xml_output}`                                                     |

**MCP Protocol Extensions:**
- `PARSE_XML(doc_id: str, xml_raw: str) → ParsedXmlObject`
- `REFINE_ENTITIES(raw_entities: List[RawEntity]) → List[Entity]`
- `RESEARCH_ENTITY(entity: Entity) → DefinitionObject`  *(internal: LLM + downstream agents)*
- `GENERATE_XML(entitiesWithDefs: List[EntityDef]) → str  # XML string`

---

### 4. MCP Client–Server Design (Extended)
- **New RPC Methods**:
  ```json
  {
    "parseXml": {"params": ["doc_id","xml_raw"]},
    "refineEntities": {"params": ["raw_entities"]},
    "researchEntity": {"params": ["entity"]},
    "generateXml": {"params": ["entities_with_defs"]}
  }
  ```
- **Server Behavior**:
  - Routes parsing to XML Parser Agent mock.
  - Executes `researchEntity` by: 
    1. Invoking LLM for base definition.
    2. Fan‑out A2A calls to Search, JIRA, Doc, PDF agents for corroborative context.
    3. Merging responses into a unified `DefinitionObject`.
- **Client SDK Additions**:
  ```python
  mcp_client.parse_xml(doc_id, xml_raw)
  mcp_client.refine_entities(raw_entities)
  mcp_client.research_entity(entity)
  mcp_client.generate_xml(entities_with_defs)
  ```

---

### 5. A2A Messaging Layer (Updated)
- **New Intents**:
  - `ExtractEntities`
  - `DefineEntity`
  - `ResearchEntity`  *(Definition Agent → Search/JIRA/Doc/PDF Agents)*
  - `AssembleXml`
- **Transport & Guarantees** unchanged: Redis Pub/Sub or Kafka, at‑least‑once delivery with deduplication.

---

### 6. LangGraph Orchestration (Extended)
Define a multi‑stage workflow with fan‑out for research:
```yaml
graph:
  - name: parseInputXml
    agent: xml_parser_agent
    next: extractEntities
  - name: extractEntities
    agent: entity_extraction_agent
    fork:
      - researchEntities
  - name: researchEntities
    agent: definition_agent
    next: assembleOutputXml
  - name: assembleOutputXml
    agent: synthesis_agent
```
- **Fan‑Out & Parallelism**: `definition_agent` internally fans out A2A `ResearchEntity` calls, potentially in parallel per entity.
- **State Passing**: Maintains `entityList → definitionsMap → finalXml`.

**Acceptance Criteria (PRD)**:
- Complete XML extraction & research for ≤ 50 entities in < 10 s.
- Definitions accuracy ≥ 90% against reference.
- Final XML validates against XSD with zero errors.

---

### 7. Data Flow & Sequence Diagram
1. **CLI** → Manager Agent invokes `PARSE_XML` → XML Parser Agent returns raw entities.
2. Manager invokes `REFINE_ENTITIES` → Entity Extraction Agent returns cleaned list.
3. Manager invokes `RESEARCH_ENTITY` per entity → Definition Agent fans out to LLM & tool agents and aggregates.
4. Manager invokes `GENERATE_XML` → Synthesis Agent returns final XML.

---

### 8. Testing & Observability (Updated)
- **Additional Testing Scenarios**:
  | Scenario                | Description                            | Expected Outcome                         |
  |-------------------------|----------------------------------------|------------------------------------------|
  | Entity Research Errors  | Search/JIRA returns no data or errors  | Definition Agent flags source; continues with LLM-only definition |
  | Fan‑Out Concurrency     | 20 parallel `ResearchEntity` calls     | All definitions succeed or retry within timeout |

- **New Observability Metrics**:
  - Count & success rate of `RESEARCH_ENTITY` calls.
  - Latency breakdown: LLM vs. each tool agent.
  - Error rates per agent type.

---

### 9. Future Considerations (Extended)
- Integrate real XML schemas (DITA/DocBook) & validation.
- Plug real service adapters for JIRA and other enterprise APIs.
- Implement human‑in‑the‑loop corrections for ambiguous entities.
- Horizontal scaling of Definition Agent for large corpora.

*End of Updated Design Document*

