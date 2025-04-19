import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union

from agent_provocateur.a2a_messaging import AgentMessaging, InMemoryMessageBroker
from agent_provocateur.a2a_models import (
    Message,
    MessageType,
    TaskRequest,
    TaskResult,
    TaskStatus,
)
from agent_provocateur.mcp_client import McpClient, SyncMcpClient


class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: str,
        broker: Optional[InMemoryMessageBroker] = None,
        mcp_url: str = "http://localhost:8000",
    ) -> None:
        """Initialize the base agent.
        
        Args:
            agent_id: The ID of this agent
            broker: Optional message broker to use
            mcp_url: URL of the MCP server
        """
        self.agent_id = agent_id
        self.messaging = AgentMessaging(agent_id, broker)
        self.mcp_client = SyncMcpClient(mcp_url)
        self.async_mcp_client = McpClient(mcp_url)
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Set up task handler
        self.messaging.register_message_handler(
            MessageType.TASK_REQUEST,
            self._on_task_request,
        )
        
        # Set up heartbeat timer
        self.heartbeat_interval_sec = 30
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.running = False
    
    def _on_task_request(self, message: Message) -> None:
        """Handle incoming task requests.
        
        Args:
            message: The incoming message
        """
        if message.message_type != MessageType.TASK_REQUEST:
            return
        
        task_request = message.payload
        if not isinstance(task_request, TaskRequest):
            return
            
        self.logger.info(
            f"Received task request: {task_request.task_id} - {task_request.intent}"
        )
        
        # Start task processing
        asyncio.create_task(self._process_task(task_request))
    
    async def _process_task(self, task_request: TaskRequest) -> None:
        """Process a task request.
        
        Args:
            task_request: The task request to process
        """
        # Send in-progress status
        self.messaging.send_task_result(
            task_id=task_request.task_id,
            target_agent=task_request.source_agent,
            status=TaskStatus.IN_PROGRESS,
            output={},
        )
        
        try:
            # Find and call the appropriate task handler
            handler_name = f"handle_{task_request.intent}"
            handler = getattr(self, handler_name, None)
            
            if handler:
                # Call the handler
                result = await handler(task_request)
                
                # Send success result
                print(f"DEBUG: Sending COMPLETED result for task: {task_request.task_id}")
                self.messaging.send_task_result(
                    task_id=task_request.task_id,
                    target_agent=task_request.source_agent,
                    status=TaskStatus.COMPLETED,
                    output=result,
                )
            else:
                # No handler found
                self.logger.error(
                    f"No handler found for intent: {task_request.intent}"
                )
                print(f"DEBUG: Sending FAILED result for task: {task_request.task_id} (no handler)")
                self.messaging.send_task_result(
                    task_id=task_request.task_id,
                    target_agent=task_request.source_agent,
                    status=TaskStatus.FAILED,
                    output={},
                    error=f"No handler found for intent: {task_request.intent}",
                )
        except Exception as e:
            # Send error result
            self.logger.exception(f"Error processing task: {e}")
            print(f"DEBUG: Sending FAILED result for task: {task_request.task_id} (exception: {e})")
            self.messaging.send_task_result(
                task_id=task_request.task_id,
                target_agent=task_request.source_agent,
                status=TaskStatus.FAILED,
                output={},
                error=str(e),
            )
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats."""
        while self.running:
            try:
                # Collect metrics
                metrics = self._get_metrics()
                
                # Send heartbeat
                self.messaging.send_heartbeat(metrics)
                
                # Wait for next interval
                await asyncio.sleep(self.heartbeat_interval_sec)
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(5)  # Back off on error
    
    def _get_metrics(self) -> Dict[str, Union[int, float]]:
        """Get agent metrics for heartbeat.
        
        Returns:
            Dict[str, Union[int, float]]: Agent metrics
        """
        # Default implementation - override in subclasses
        return {
            "uptime_sec": time.time() - self.start_time,
        }
    
    async def start(self) -> None:
        """Start the agent."""
        self.logger.info(f"Starting agent: {self.agent_id}")
        self.running = True
        self.start_time = time.time()
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Call startup method if defined in subclass
        if hasattr(self, "on_startup"):
            await self.on_startup()
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.logger.info(f"Stopping agent: {self.agent_id}")
        self.running = False
        
        # Stop heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        # Close MCP client
        await self.async_mcp_client.close()
        
        # Call shutdown method if defined in subclass
        if hasattr(self, "on_shutdown"):
            await self.on_shutdown()
    
    async def send_request_and_wait(
        self,
        target_agent: str,
        intent: str,
        payload: Dict[str, Any],
        timeout_sec: int = 60,
    ) -> Optional[TaskResult]:
        """Send a task request and wait for the result.
        
        Args:
            target_agent: The target agent ID
            intent: The intent of the task
            payload: The task payload
            timeout_sec: The timeout in seconds
            
        Returns:
            Optional[TaskResult]: The task result if available
        """
        task_id = self.messaging.send_task_request(
            target_agent=target_agent,
            intent=intent,
            payload=payload,
            timeout_sec=timeout_sec,
        )
        
        return await self.messaging.wait_for_task_result(
            task_id=task_id,
            timeout_sec=timeout_sec,
        )