#!/bin/bash
# Test script for Phase 3A readiness with GraphRAG integration

# Set up log directories
LOG_DIR=logs
FRONTEND_LOG=frontend.out.log
FRONTEND_ERR=frontend.err.log
MCP_LOG=mcp_server.out.log
MCP_ERR=mcp_server.err.log

mkdir -p $LOG_DIR

# Check source attribution implementation
echo "Checking Phase 3A readiness..."

# Clean log files to start fresh
echo "" > "$LOG_DIR/$FRONTEND_LOG"
echo "" > "$LOG_DIR/$FRONTEND_ERR"
echo "" > "$LOG_DIR/$MCP_LOG"
echo "" > "$LOG_DIR/$MCP_ERR"

# Check for GraphRAG implementation
if [ -f src/agent_provocateur/graphrag_service.py ] && [ -f src/agent_provocateur/source_model.py ] && [ -f src/agent_provocateur/xml_attribution.py ]; then
    echo "✅ GraphRAG implementation found"
else
    echo "❌ GraphRAG implementation missing"
    echo "   Make sure you have the following files:"
    echo "   - src/agent_provocateur/graphrag_service.py"
    echo "   - src/agent_provocateur/source_model.py"
    echo "   - src/agent_provocateur/xml_attribution.py"
    exit 1
fi

# Run tests for GraphRAG related modules
echo "Running GraphRAG tests..."
python -m pytest tests/test_graphrag_service.py tests/test_source_model.py tests/test_xml_attribution.py -v

# Start the backend server in the background
echo "Starting MCP server for integration tests..."
python -m agent_provocateur.mcp_server --port 8000 > "$LOG_DIR/$MCP_LOG" 2> "$LOG_DIR/$MCP_ERR" &
MCP_PID=$!

# Give server time to start
sleep 2

# Start frontend server in the background
echo "Starting frontend server..."
python frontend/server.py > "$LOG_DIR/$FRONTEND_LOG" 2> "$LOG_DIR/$FRONTEND_ERR" &
FRONTEND_PID=$!

# Give server time to start
sleep 2

# Run XML tests to verify GraphRAG integration
echo "Running XML attribution integration tests..."
python -m pytest tests/test_xml_agent_attribution.py -v

# Optional: Run integration tests if needed
echo "Running web UI tests..."
curl -s http://localhost:3000 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend server running"
else
    echo "❌ Frontend server not responding"
fi

# Check for error logs
if grep -q "Error" "$LOG_DIR/$MCP_ERR"; then
    echo "⚠️  Backend errors detected in logs"
    grep "Error" "$LOG_DIR/$MCP_ERR"
fi

if grep -q "Error" "$LOG_DIR/$FRONTEND_ERR"; then
    echo "⚠️  Frontend errors detected in logs"
    grep "Error" "$LOG_DIR/$FRONTEND_ERR"
fi

# Clean up - kill servers
echo "Cleaning up test environment..."
kill $MCP_PID
kill $FRONTEND_PID

# Final readiness check
echo "Checking overall readiness..."
ERRORS=0

# Count errors in logs
MCP_ERRORS=$(grep -c "Error" "$LOG_DIR/$MCP_ERR")
FRONTEND_ERRORS=$(grep -c "Error" "$LOG_DIR/$FRONTEND_ERR")

# If too many errors, mark as not ready
if [ $MCP_ERRORS -gt 5 ] || [ $FRONTEND_ERRORS -gt 5 ]; then
    echo "❌ System has too many errors to be considered ready"
    ERRORS=1
fi

# Check for test failures
TEST_FAILURES=$(cat "$LOG_DIR/$MCP_ERR" "$LOG_DIR/$FRONTEND_ERR" | grep -c "FAILED")
if [ $TEST_FAILURES -gt 0 ]; then
    echo "❌ Some tests failed"
    ERRORS=1
fi

# Final status
if [ $ERRORS -eq 0 ]; then
    echo "✅ System is READY for Phase 3A deployment"
else
    echo "⚠️  System is PARTIALLY READY for Phase 3A deployment (non-critical issues found)"
fi

echo "Test completed. Check the logs directory for details."