#!/usr/bin/env python3
"""
Simple test script to verify Prometheus Pushgateway connectivity.
This is part of Phase 1 implementation for metrics monitoring.
"""

import platform
from prometheus_client import Counter, Gauge, push_to_gateway, CollectorRegistry

def main():
    print("Starting Pushgateway test script...")
    
    # Create a new registry for this specific test
    registry = CollectorRegistry()
    
    # Create test metrics
    test_counter = Counter(
        'ap_test_counter_total', 
        'Test counter for verification', 
        registry=registry
    )
    
    test_gauge = Gauge(
        'ap_test_gauge',
        'Test gauge for verification',
        ['instance', 'system'],
        registry=registry
    )
    
    # Increment the counter
    test_counter.inc()
    
    # Set a gauge value
    test_gauge.labels(
        instance=platform.node(),
        system=platform.system()
    ).set(42.0)
    
    # Print metric values
    print(f"Test counter value: {test_counter._value.get()}")
    print("Test gauge value: 42.0")
    
    # Push to Pushgateway
    pushgateway_url = "localhost:9091"
    print(f"Pushing metrics to Pushgateway at {pushgateway_url}...")
    
    try:
        push_to_gateway(
            pushgateway_url, 
            job='ap_test_metrics',
            registry=registry
        )
        print("Successfully pushed metrics to Pushgateway!")
    except Exception as e:
        print(f"Error pushing to Pushgateway: {e}")
        return False
        
    print("\nVerify metrics in Prometheus/Grafana:")
    print("1. Prometheus UI: http://localhost:9090")
    print("   - Check for metrics starting with 'ap_test_'")
    print("2. Grafana: http://localhost:3000/d/dejfjfc93klc0a/agent-provocateur-test-dashboard")
    print("   - Login with admin/agent_provocateur")
    
    return True

if __name__ == "__main__":
    main()