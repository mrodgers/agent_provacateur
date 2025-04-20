"""Prometheus metrics collection for Agent Provocateur.

This module provides Prometheus metric collectors for tracking the performance
and health of the Agent Provocateur system. Metrics are exposed via a HTTP server
on a configurable port and can be pushed to a Prometheus Pushgateway.
"""

from typing import Dict, Optional, Any, Callable, TypeVar, Awaitable
from prometheus_client import (
    Counter, Gauge, Histogram, start_http_server, push_to_gateway, REGISTRY
)

T = TypeVar('T')

# Use the default registry to ensure metrics appear in the HTTP endpoint
# This is important because prometheus_client.start_http_server uses the default registry

# PushGateway configuration
PUSHGATEWAY_URL = "localhost:9091"  # Default URL

# MCP Client metrics
MCP_REQUEST_COUNT = Counter(
    'ap_mcp_request_total', 
    'Total count of MCP requests',
    ['endpoint', 'status']
)
MCP_REQUEST_LATENCY = Histogram(
    'ap_mcp_request_duration_seconds',
    'MCP request duration in seconds',
    ['endpoint']
)

# A2A messaging metrics
MESSAGE_COUNT = Counter(
    'ap_message_total',
    'Total count of A2A messages',
    ['message_type', 'source', 'target']
)
MESSAGE_LATENCY = Histogram(
    'ap_message_duration_seconds',
    'A2A message processing duration in seconds',
    ['message_type']
)

# Agent metrics
AGENT_TASK_COUNT = Counter(
    'ap_agent_task_total',
    'Total count of agent tasks',
    ['agent_id', 'intent', 'status']
)
AGENT_ACTIVE = Gauge(
    'ap_agent_active',
    'Number of active agents',
    ['agent_id']
)
AGENT_TASK_DURATION = Histogram(
    'ap_agent_task_duration_seconds',
    'Agent task processing duration in seconds',
    ['agent_id', 'intent']
)

# LLM metrics
LLM_REQUEST_COUNT = Counter(
    'ap_llm_request_total',
    'Total count of LLM requests',
    ['provider', 'model', 'status']
)
LLM_REQUEST_LATENCY = Histogram(
    'ap_llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['provider', 'model']
)
LLM_TOKEN_COUNT = Counter(
    'ap_llm_token_total',
    'Total count of tokens processed by LLMs',
    ['provider', 'model', 'direction']  # direction: input or output
)

# System metrics
SYSTEM_INFO = Gauge(
    'ap_system_info',
    'System information with version labels',
    ['version', 'python_version']
)


def start_metrics_server(port: int = 8001) -> None:
    """Start a Prometheus metrics server on the specified port.
    
    Args:
        port: The port to listen on (default: 8001)
    """
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}")


def instrument_mcp_client(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Decorator to instrument MCP client methods with Prometheus metrics.
    
    Args:
        func: The function to instrument
        
    Returns:
        The instrumented function
    """
    import time
    import functools

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Extract endpoint name from function name
        endpoint = func.__name__
        start_time = time.time()
        status = "success"
        
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            raise e
        finally:
            duration = time.time() - start_time
            MCP_REQUEST_COUNT.labels(endpoint=endpoint, status=status).inc()
            MCP_REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    
    return wrapper


# Dictionary to store agent metric gauges
_agent_metric_gauges = {}

def record_agent_metrics(agent_id: str, metrics: Dict[str, Any]) -> None:
    """Record agent metrics from heartbeat.
    
    Args:
        agent_id: The ID of the agent
        metrics: Dictionary of metrics to record
    """
    # Set a gauge for each numeric metric
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            # Use existing gauge or create a new one
            metric_name = f"ap_agent_{key}"
            
            if metric_name not in _agent_metric_gauges:
                _agent_metric_gauges[metric_name] = Gauge(
                    metric_name, 
                    f"Agent {key} metric", 
                    ["agent_id"]
                )
                
            _agent_metric_gauges[metric_name].labels(agent_id=agent_id).set(value)
    
    # Push metrics to Pushgateway - pass a simple grouping key
    push_metrics(job_name="agent_metrics", grouping_key={"agent_id": agent_id})


def push_metrics(job_name: str = "agent_provocateur", grouping_key: Optional[Dict[str, str]] = None) -> None:
    """Push metrics to Prometheus Pushgateway.
    
    Args:
        job_name: The name of the job
        grouping_key: Optional grouping key (e.g., {'instance': 'myhost'})
    """
    # Ensure grouping key only contains strings
    safe_grouping_key = {}
    if grouping_key:
        for key, value in grouping_key.items():
            safe_grouping_key[key] = str(value)
    
    # Try to push metrics to Pushgateway
    try:
        push_to_gateway(
            PUSHGATEWAY_URL,
            job=job_name,
            registry=REGISTRY,
            grouping_key=safe_grouping_key
        )
    except Exception as e:
        print(f"Error pushing metrics to Pushgateway: {e}")


def configure_pushgateway(url: str) -> None:
    """Configure the Pushgateway URL.
    
    Args:
        url: The URL of the Pushgateway (e.g., 'localhost:9091')
    """
    global PUSHGATEWAY_URL
    PUSHGATEWAY_URL = url