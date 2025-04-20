# Agent Provocateur Monitoring - Phase 1 Implementation

This document details the Phase 1 implementation of the monitoring system for Agent Provocateur using Prometheus and Grafana.

## Overview

Phase 1 focuses on setting up the basic monitoring infrastructure and validating the Pushgateway approach for metrics collection. The main goal is to establish a working monitoring stack and verify that metrics can be pushed from any process to the Prometheus Pushgateway.

## Components Implemented

1. **Monitoring Infrastructure**
   - Docker Compose configuration for Prometheus, Pushgateway, and Grafana
   - Prometheus configuration to scrape metrics from Pushgateway
   - Basic Grafana dashboard for test metrics visualization

2. **Metrics Module Enhancement**
   - Improved Pushgateway integration in `metrics.py`
   - Added error handling and grouping key sanitization 
   - Enhanced debug output for troubleshooting

3. **Testing Tools**
   - Standalone test script `metrics_test.py` for Pushgateway verification
   - CLI integration with a new `metrics` command
   - Test metrics (counter, gauge, histogram) for validation

4. **Documentation**
   - Updated README.md with monitoring information
   - Created monitoring-specific README with detailed instructions
   - Added startup script for the monitoring stack

## Files Created/Modified

### New Files
- `/monitoring/docker-compose.yml` - Docker Compose configuration
- `/monitoring/prometheus.yml` - Prometheus scraping configuration
- `/monitoring/test_metrics.py` - Standalone test script
- `/monitoring/start.sh` - Startup script for monitoring services
- `/monitoring/PHASE1.md` - Phase 1 implementation documentation
- `/monitoring/grafana/dashboards/agent_provocateur_dashboard.json` - Grafana dashboard
- `/monitoring/grafana/provisioning/dashboards/dashboard.yml` - Grafana provisioning

### Modified Files
- `/src/agent_provocateur/metrics.py` - Enhanced Pushgateway integration
- `/src/agent_provocateur/cli.py` - Added metrics test command
- `/README.md` - Updated with monitoring information

## Usage Instructions

### Start the Monitoring Stack

```bash
cd monitoring
./start.sh
```

This will:
1. Start Prometheus, Pushgateway, and Grafana with Docker Compose
2. Run a simple test to verify Pushgateway connectivity
3. Display URLs for accessing the monitoring services

### Test Metrics Manually

```bash
# Using the CLI
ap-client metrics --pushgateway localhost:9091 --iterations 3

# Using the standalone script
python src/agent_provocateur/metrics_test.py --pushgateway localhost:9091
```

### Start Server with Metrics

```bash
ap-server --pushgateway localhost:9091
```

## Verification

1. Check Prometheus for test metrics:
   - Open http://localhost:9090
   - Search for metrics starting with `ap_test_`

2. Check Grafana dashboard:
   - Open http://localhost:3000/d/dejfjfc93klc0a/agent-provocateur-test-dashboard (login: admin/agent_provocateur)
   - The dashboard should show the test metrics including counter and gauge values

## Next Steps

Phase 2 will build on this foundation by:
1. Implementing MCP client request metrics
2. Adding agent lifecycle metrics
3. Integrating task processing metrics
4. Implementing A2A messaging metrics

## Troubleshooting

If you encounter issues:

1. **Docker/Podman Issues**
   - Check if the containers are running: `docker ps` or `podman ps`
   - View container logs: `docker logs prometheus` or `podman logs prometheus`

2. **Pushgateway Connection Issues**
   - Ensure Pushgateway is running and accessible at http://localhost:9091
   - Check for network/firewall issues if using remote hosts

3. **Missing Metrics**
   - Check the Pushgateway UI to see if metrics are being received
   - Verify metrics are properly registered and pushed with debugging output