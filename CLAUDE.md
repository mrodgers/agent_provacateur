# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Install dependencies: `pip install -e ".[dev]"`
- Run application: `python -m agent_provocateur.main`
- Run linting: `ruff check .`
- Run type checking: `mypy src`
- Run tests: `pytest`
- Run single test: `python tests/test_main.py`

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