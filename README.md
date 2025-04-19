# Agent Provocateur

Agents for research - A Python library for developing, benchmarking, and deploying AI agents.

## Installation

```bash
# Install in development mode with all dev dependencies
pip install -e ".[dev]"
```

## Project Structure

```
.
├── src/
│   └── agent_provocateur/    # Main package
│       ├── __init__.py
│       └── main.py           # Entry point
├── tests/                    # Test directory
│   ├── __init__.py
│   └── test_main.py          # Tests for main module
├── .github/workflows/        # CI/CD configuration
│   └── ci.yml                # GitHub Actions workflow
├── CLAUDE.md                 # Guide for Claude AI
├── LICENSE                   # MIT License
├── README.md                 # This file
├── pyproject.toml            # Project configuration
└── setup.py                  # Installation script
```

## Development

```bash
# Run tests
python tests/test_main.py  # Run directly (single test)
pytest                     # Run all tests with pytest

# Type checking
mypy src

# Linting
ruff check .
```

## Usage

```python
from agent_provocateur.main import main

# Returns True if execution was successful
result = main()
```

## License

MIT License. See the LICENSE file for details.