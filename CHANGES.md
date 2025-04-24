# Service Changes Log

## 2025-04-23

### Architecture Simplification

- **Consolidated GraphRAG Implementations**: Removed the TypeScript implementation of GraphRAG and standardized on the Python implementation, which has been renamed from `graphrag_mcp_py` to `graphrag_service`.

- **Renamed MCP Server**: For better clarity, renamed `mcp_server.py` to `document_service_api.py` and updated all references to use the more descriptive term "Document Service API" instead of the generic "MCP Server".

- **Consolidated XML Scripts**: Created a unified XML CLI (`unified_xml_cli.py`) that combines functionality from multiple scripts:
  - `xml_cli.py`
  - `xml_agent_cli.py`
  - `extract_cisco_commands.py`

- **Specialized Cisco XML Agent**: Created a dedicated `cisco_xml_agent.py` for Cisco command extraction with enhanced functionality.

### Benefits

1. **Reduced Redundancy**: Eliminated duplication of functionality between the TypeScript and Python GraphRAG implementations.

2. **Clearer Service Names**: Service names now more accurately reflect their purpose:
   - `graphrag_service` - Knowledge graph and vector search service
   - `document_service` - Document management and orchestration API

3. **Better Development Experience**: Simplified onboarding by reducing the number of services to understand and maintain.

4. **Improved Code Clarity**: More explicit naming conventions make the codebase easier to comprehend.

### Upcoming Changes

- Rename `enhanced_mcp_server.py` to `enhanced_document_service.py` for consistent naming
- Update command-line entry points to reflect the new naming convention
- Add comprehensive API documentation for GraphRAG service

### Migration Notes

- The service manager (all_services.py) has been updated to use the new service names
- Scripts and dependencies should continue to work with no changes
- In future updates, the '--mcp-server' command line option will be deprecated in favor of '--document-service'