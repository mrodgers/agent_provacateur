# Agent Provocateur Frontend

This directory contains the web user interface for Agent Provocateur.

## Quick Start

To run the frontend:

```bash
# Install dependencies
uv pip install -e ".[frontend]"

# Start the backend API server in one terminal
ap-server --host 127.0.0.1 --port 8000

# Start the frontend server in another terminal
python frontend/server.py --host 127.0.0.1 --port 3000

# Access the web UI in your browser
open http://localhost:3000
```

## Features

The current frontend prototype provides:

- Document management and listing
- XML document content viewing
- Researchable nodes exploration
- Simulated research workflow

## Directory Structure

```
frontend/
├── static/              # Static assets
│   └── js/              # JavaScript files
│       ├── app.js       # Main React application
│       └── main.js      # Simpler test implementation
├── templates/           # HTML templates
│   ├── index.html       # Main application template
│   └── fallback.html    # Simple fallback page
├── server.py            # FastAPI frontend server
└── README.md            # This file
```

## Development Notes

The current implementation is a simple prototype using:
- FastAPI to serve the frontend
- Vanilla JavaScript with minimal React (loaded via CDN)
- Tailwind CSS for styling (via CDN)

### Backend Integration

The frontend connects to the Agent Provocateur backend API, which provides:
- Document listing and retrieval
- XML content and node extraction
- Research workflow orchestration

### Debugging

If you encounter issues:
1. Check the browser's developer console for error messages
2. Use the fallback page at `/fallback` for basic functionality
3. Make sure both the frontend and backend servers are running
4. Check the server logs for any backend errors

## Future Plans

See the [Frontend Architecture](../docs/architecture/frontend_architecture.md) document for details on the planned development roadmap.

## License

MIT License. See the LICENSE file for details.