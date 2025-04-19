# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands
- Install dependencies: `pip install -e .`
- Run application: `python main.py`
- Run linting: `ruff check .`
- Run type checking: `mypy .`
- Run tests: `pytest`
- Run single test: `pytest tests/test_file.py::test_function`

## Code Style Guidelines
- **Formatting**: Black with 88 character line length
- **Imports**: Group imports (stdlib, third-party, local) with blank lines between groups
- **Types**: Use type hints for all function parameters and return values
- **Naming**: 
  - snake_case for variables and functions
  - PascalCase for classes
- **Error handling**: Use explicit exception handling with specific exception types
- **Documentation**: Docstrings for all public functions, classes, and methods
- **Testing**: Write tests for all new functionality