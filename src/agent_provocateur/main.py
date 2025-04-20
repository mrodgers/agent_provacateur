import uvicorn
from argparse import ArgumentParser

from agent_provocateur.metrics import start_metrics_server, SYSTEM_INFO, configure_pushgateway
from prometheus_client import Counter, Gauge

# Test counter that increments on every server start
TEST_COUNTER = Counter('ap_test_server_starts', 'Number of server starts')

# Extra test gauge that we'll set to a specific value for testing
TEST_GAUGE = Gauge('ap_test_gauge', 'Test gauge for verification')
import sys
import platform


def main() -> bool:
    """Main entry point for the application.
    
    Returns:
        bool: True if execution was successful
    """
    parser = ArgumentParser(description="Agent Provocateur MCP Server")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the server to"
    )
    parser.add_argument(
        "--metrics-port", type=int, default=8001, help="Port for Prometheus metrics"
    )
    parser.add_argument(
        "--no-metrics", action="store_true", help="Disable Prometheus metrics"
    )
    parser.add_argument(
        "--pushgateway", default="localhost:9091", help="Prometheus Pushgateway URL"
    )
    
    args = parser.parse_args()
    
    # Start metrics server if enabled
    if not args.no_metrics:
        start_metrics_server(args.metrics_port)
        
        # Configure pushgateway
        configure_pushgateway(args.pushgateway)
        print(f"Configured Pushgateway at {args.pushgateway}")
        
        # Record system info
        SYSTEM_INFO.labels(
            version="0.1.0",  # TODO: Get from package version
            python_version=platform.python_version()
        ).set(1)
        
        # Increment test counter
        TEST_COUNTER.inc()
        
        # Set test gauge to a specific value
        TEST_GAUGE.set(42.0)
        
        # Push metrics to pushgateway as a test
        from agent_provocateur.metrics import push_metrics
        push_metrics(job_name="server_start", grouping_key={"component": "server"})
        print(f"Metrics will be available at http://localhost:{args.metrics_port}/metrics (Pushgateway currently disabled)")
        print(f"Incremented test counter - current value will be visible at http://localhost:{args.metrics_port}/metrics")
    
    print(f"Starting MCP server on {args.host}:{args.port}")
    uvicorn.run(
        "agent_provocateur.mcp_server:create_app",
        host=args.host,
        port=args.port,
        factory=True,
    )
    return True


if __name__ == "__main__":
    main()
