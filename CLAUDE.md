# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Install dependencies: `pip install -e ".[dev]"`
- Run MCP server: `python -m agent_provocateur.main --host 127.0.0.1 --port 8000`
- Run CLI client: `python -m agent_provocateur.cli [command] [options]`
- Run linting: `ruff check .`
- Run type checking: `mypy src`
- Run tests: `pytest`
- Run tests with coverage: `python -m pytest --cov=src.agent_provocateur`

## Project Overview
This project implements a multi-agent research system with:
1. MCP Server Mock for simulated tool interactions
2. MCP Client SDK for standardized tool access
3. A2A Messaging Layer (planned) for agent coordination
4. LangGraph Orchestration (planned) for workflow execution

## Code Style Guidelines
- **Formatting**: 88 character line length (enforced by ruff)
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups
- **Types**: Use type hints for all function parameters and return values
- **Naming**: 
  - snake_case for variables and functions
  - PascalCase for classes
- **Error handling**: Use explicit exception handling with specific exception types
- **Documentation**: Docstrings for all public functions, classes, and methods
- **Testing**: Write tests for all new functionality

## Project Structure
- Keep code organized in the `src/agent_provocateur` directory
- Place tests in the `tests` directory
- Follow Python package best practices
- Use type annotations for all functions
- Update documentation when making significant changes

## Current Project Status
- Phase 1 (MCP Tools Development) - Complete
  - MCP Server Mock
  - MCP Client SDK
  - CLI Demo

- Phase 2 (A2A Communication Development) - Planned
  - Message Schema
  - Pub/Sub Infrastructure
  - Agent Messaging Module
  - Sample Workflow