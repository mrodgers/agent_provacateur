# Agent Provocateur Frontend

This directory contains the web user interface for Agent Provocateur.

## Quick Start

To run the frontend:

```bash
# Install dependencies
uv pip install -e ".[frontend]"

# Method 1: Using automated scripts (recommended)
# Start the backend API server in one terminal
./scripts/ap.sh start mcp_server

# Start the frontend server with automatic port detection
./scripts/start_frontend.sh

# Method 2: Manual startup
# Start the backend API server in one terminal
ap-server --host 127.0.0.1 --port 8000

# Start the frontend server in another terminal
python frontend/server.py --host 127.0.0.1 --port 3001

# Access the web UI in your browser
open http://localhost:3001
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
5. Use our debugging scripts for detailed diagnostics:

```bash
# Run the frontend with debugging enabled
./scripts/start_frontend.sh --debug

# Check port conflicts specifically
./scripts/start_frontend.sh --debug --port 3001

# Restart frontend server
./scripts/stop_frontend.sh && ./scripts/start_frontend.sh
```

All debug output is saved to `logs/frontend_debug.log` for troubleshooting.

### Port Usage

The frontend server uses the following ports:
- **Frontend UI**: port 3001 (to avoid conflicts with Grafana on 3000)
- **Backend API**: port 8000
- **Grafana**: port 3000 (if monitoring is running)

#### Port Conflicts

If you encounter port conflicts (such as "405 Method Not Allowed" errors), try:

1. Check if another service is using port 3001:
   ```bash
   lsof -i :3001  # On macOS/Linux
   netstat -ano | findstr :3001  # On Windows
   ```

2. Use a different port:
   ```bash
   python server.py --host 127.0.0.1 --port 3002
   ```

3. View system information from the UI:
   - Look at the footer to see version and port info
   - Click "Check Ports" to see detailed system information
   
4. Always use explicit URLs with port number:
   ```
   http://localhost:3001/
   ```

## Future Plans

See the [Frontend Architecture](../docs/architecture/frontend_architecture.md) document for details on the planned development roadmap.

## License

MIT License. See the LICENSE file for details.