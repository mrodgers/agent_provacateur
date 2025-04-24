# Deprecated Scripts

This directory contains scripts that have been deprecated and are no longer part of the recommended workflow. They are kept here for backward compatibility and reference.

## XML Scripts (2025-04-23)

The following XML-related scripts have been consolidated into new unified tools:

- **`xml_cli.py`** - Use `unified_xml_cli.py` instead
  ```bash
  # Old way
  ./scripts/deprecated/xml/xml_cli.py list
  
  # New way
  ./scripts/unified_xml_cli.py list
  ```

- **`xml_agent_cli.py`** - Use `unified_xml_cli.py` instead
  ```bash
  # Old way
  ./scripts/deprecated/xml/xml_agent_cli.py identify --file file.xml
  
  # New way
  ./scripts/unified_xml_cli.py analyze file.xml
  ```

- **`xml_command_agent.py`** - Use `cisco_xml_agent.py` instead
  ```bash
  # Old way
  ./scripts/deprecated/xml/xml_command_agent.py
  
  # New way
  ./scripts/cisco_xml_agent.py extract DOC_ID
  ```

- **`extract_cisco_commands.py`** - Use `unified_xml_cli.py` or `cisco_xml_agent.py` instead
  ```bash
  # Old way
  ./scripts/deprecated/xml/extract_cisco_commands.py DOC_ID
  
  # New way (simple)
  ./scripts/unified_xml_cli.py commands DOC_ID
  
  # New way (advanced)
  ./scripts/cisco_xml_agent.py extract DOC_ID
  ```

## Web Search Scripts

The following web search scripts have been consolidated:

- **`run_web_search_mcp.sh`** - Use `manage_web_search.sh` instead
  ```bash
  # Old way
  ./scripts/deprecated/run_web_search_mcp.sh
  
  # New way
  ./scripts/manage_web_search.sh start
  ```

- **`start_with_web_search.sh`** - Use `start_ap.sh` instead
  ```bash
  # Old way
  ./scripts/deprecated/start_with_web_search.sh
  
  # New way
  ./scripts/start_ap.sh start web_search_mcp
  ```

- **`ap_web_search.sh`** - Use the main ap.sh tool instead
  ```bash
  # Old way
  ./scripts/deprecated/ap_web_search.sh "search query"
  
  # New way
  ./scripts/ap.sh web-search --query "search query"
  ```

## Service Names

Service names have also been updated for clarity:
- `mcp_server` is now `document_service` (Document Service API)
- `graphrag_mcp_py` is now `graphrag_service` (GraphRAG Service)
- The TypeScript GraphRAG implementation has been removed in favor of the Python version

## Why These Scripts Were Deprecated

- The functionality has been consolidated into more comprehensive tools
- The newer scripts provide better error handling and more options
- Having fewer scripts with more features reduces confusion and maintenance burden
- The unified approach allows for better integration with other services
- Better naming conventions improve code clarity and maintainability

## Transition Plan

1. These scripts will remain in this directory until the next major version update (August 2025)
2. Users should update their workflows to use the replacement scripts
3. In June 2025, warning notices will be added when using deprecated scripts
4. After the transition period, these scripts will be removed entirely