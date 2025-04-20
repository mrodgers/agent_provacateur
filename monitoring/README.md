# Agent Provocateur Monitoring

This directory contains the monitoring setup for the Agent Provocateur system using Prometheus and Grafana.

## Quick Start

1. Start the monitoring stack:
   ```
   cd monitoring
   docker-compose up -d
   ```

2. Access the monitoring interfaces:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (login: admin/agent_provocateur)
   - Pushgateway: http://localhost:9091

3. Run the test script to verify Pushgateway access:
   ```
   python test_metrics.py
   ```

## Phase 1: Setup and Verification

1. **Start Monitoring Infrastructure**
   - Launch Prometheus, Pushgateway, and Grafana with Docker Compose
   - Verify all services are running

2. **Test Metrics Pushing**
   - Run `test_metrics.py` to push test metrics to Pushgateway
   - Verify metrics appear in Prometheus (search for "ap_test_")
   - Create a basic Grafana dashboard to visualize test metrics

3. **Integrate with Agent Provocateur**
   - Ensure metrics.py can communicate with Pushgateway
   - Start a simple AP server with metrics enabled
   - Verify basic metrics are pushed and visible

## Phase 2: Core Metrics Integration

Once Phase 1 is verified working, Phase 2 will implement:
- MCP client request metrics
- Agent lifecycle metrics 
- Task processing metrics
- A2A messaging metrics

## Phase 3: Advanced Metrics and Dashboard

The final phase will include:
- LLM-specific metrics
- Complete Grafana dashboard
- Alerting rules
- Performance optimization

## Troubleshooting

Common issues:
- **Network connectivity**: Ensure Docker host can reach agent_provocateur services
- **HTTP 400 errors**: Check grouping keys (must be strings)
- **No metrics showing**: Verify process isolation setup (use Pushgateway)
- **Duplicate metrics**: Use a separate registry when pushing

## References

- [Prometheus Documentation](https://prometheus.io/docs/introduction/overview/)
- [Pushgateway Documentation](https://github.com/prometheus/pushgateway)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/)
- [Python client library](https://github.com/prometheus/client_python)