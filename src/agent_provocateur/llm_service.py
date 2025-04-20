"""LLM service for handling different providers."""

import abc
import json
import logging
import os
from typing import Any, Dict

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import openai
    from openai import AzureOpenAI
    import base64
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    BRIDGEIT_AVAILABLE = True
except ImportError:
    BRIDGEIT_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

from agent_provocateur.models import (
    LlmRequest,
    LlmResponse,
    LlmResponseUsage,
)


class LlmProvider(abc.ABC):
    """Abstract base class for LLM providers."""
    
    @abc.abstractmethod
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate text from the LLM.
        
        Args:
            request: The LLM request
            
        Returns:
            LlmResponse: The LLM response
        """
        pass


class MockLlmProvider(LlmProvider):
    """Mock LLM provider for testing."""
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate text from the mock LLM.
        
        Args:
            request: The LLM request
            
        Returns:
            LlmResponse: The LLM response
        """
        # Use request context to tailor the response
        context = request.context or {}
        prompt_text = request.prompt or ""
        
        # Get content from messages if available
        if request.messages:
            for message in request.messages:
                if message.role == "user":
                    prompt_text += message.content + "\n"
        
        # Generate response based on prompt keywords
        if "decision" in prompt_text.lower():
            response_text = self._generate_decision_response(prompt_text, context)
        elif "plan" in prompt_text.lower():
            response_text = self._generate_planning_response(prompt_text, context)
        elif "analyze" in prompt_text.lower() or "analysis" in prompt_text.lower():
            response_text = self._generate_analysis_response(prompt_text, context)
        else:
            response_text = self._generate_generic_response(prompt_text, context)
        
        # Mock token usage
        prompt_tokens = len(prompt_text.split())
        completion_tokens = len(response_text.split())
        
        return LlmResponse(
            text=response_text,
            usage=LlmResponseUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model="mock-llm-v1",
            provider="mock",
            finish_reason="completed",
        )
    
    def _generate_decision_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a decision-making response."""
        if "prioritize" in prompt.lower():
            return """Based on the provided information, I recommend prioritizing Task B (Data Pipeline Enhancement) for the following reasons:

1. Highest Impact: This task addresses critical data flow issues affecting multiple teams
2. Time Sensitivity: The current issues are causing daily operational problems
3. Prerequisites: Completing this will unblock several dependent tasks
4. Resource Availability: The required expertise is currently available

The second priority should be Task A (API Development), followed by Task C (Documentation Update)."""
        else:
            return """After analyzing the situation, I recommend proceeding with Option 2: Refactor the existing codebase.

This approach offers the best balance of immediate benefits and long-term sustainability:
- Addresses current performance bottlenecks
- Maintains compatibility with existing integrations
- Requires 40% less development time than a complete rewrite
- Enables incremental improvements while maintaining system availability

Key implementation steps should include modularizing the core components, introducing a comprehensive test suite, and establishing clear API boundaries."""
    
    def _generate_planning_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a planning response."""
        return """## Implementation Plan

### Phase 1: Setup & Foundation (Week 1-2)
- Configure development environment with required dependencies
- Set up CI/CD pipeline with automated testing
- Establish code quality standards and linting rules
- Create basic project structure and architecture documentation

### Phase 2: Core Implementation (Week 3-5)
- Develop data models and schemas
- Implement API endpoints with OpenAPI documentation
- Create client SDK for easy integration
- Develop background processing service for async tasks

### Phase 3: Integration & Testing (Week 6-7)
- Integrate with external systems (auth, storage, analytics)
- Implement comprehensive test suite (unit, integration, load)
- Conduct security audit and performance testing
- Prepare deployment scripts and infrastructure templates

### Phase 4: Finalization & Deployment (Week 8)
- Conduct final QA and regression testing
- Prepare user documentation and examples
- Deploy to staging environment for stakeholder review
- Deploy to production with monitoring and rollback plan"""
    
    def _generate_analysis_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate an analysis response."""
        ticket_context = context.get("ticket", {})
        if ticket_context:
            return f"""## Analysis of Ticket {ticket_context.get('id', 'Unknown')}

The ticket "{ticket_context.get('summary', 'Unknown')}" requires attention to several aspects:

1. **Current Status**: {ticket_context.get('status', 'Unknown')}
2. **Primary Issues**:
   - The system is experiencing intermittent connection failures
   - Performance degradation during peak usage hours
   - Configuration inconsistencies between environments

3. **Root Cause Analysis**:
   - Connection failures appear to be related to connection pool exhaustion
   - Performance issues correlate with inefficient database queries
   - Configuration drift resulted from manual environment changes

4. **Recommended Actions**:
   - Implement connection pool monitoring and auto-scaling
   - Optimize the identified inefficient queries with proper indexing
   - Deploy configuration as code to prevent future drift
   - Add automated testing to catch these issues earlier

5. **Risk Assessment**:
   - Medium priority issue affecting specific user workflows
   - No data integrity concerns identified
   - Estimated effort: 2-3 developer days"""
        else:
            return """## Performance Analysis

The system analysis reveals several key metrics and bottlenecks:

1. **Response Time**:
   - 95th percentile: 870ms (exceeds target of 500ms)
   - Median: 320ms (within acceptable range)
   - Slowest endpoints: /api/reports and /api/search

2. **Resource Utilization**:
   - CPU: 78% average during peak hours
   - Memory: 85% utilization with occasional spikes to 92%
   - Database connections: Reaching pool limits (90-100%)

3. **Bottlenecks Identified**:
   - Database query optimization needed for reporting features
   - Connection pooling configuration requires adjustment
   - Caching strategy insufficient for repetitive queries
   - Background task scheduling causing CPU spikes

4. **Improvement Recommendations**:
   - Implement query optimization and indexing for reporting endpoints
   - Increase connection pool size by 25% and add monitoring
   - Add Redis cache layer for frequently accessed data
   - Reschedule background tasks to distribute load more evenly"""
    
    def _generate_generic_response(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a generic response."""
        return """Thank you for your query. I've processed the information and have the following insights to share:

The system appears to be functioning within normal parameters, though there are opportunities for improvement in several areas. Based on the current configuration and usage patterns, I'd recommend reviewing the resource allocation and optimization settings.

Key points to consider:
1. Current utilization shows moderate efficiency with room for enhancement
2. The implementation follows standard patterns but could benefit from updates
3. Documentation is comprehensive but would benefit from examples

Let me know if you need more specific information about any aspect of the system, and I'd be happy to provide a more targeted analysis or recommendation."""


class OllamaProvider(LlmProvider):
    """Ollama LLM provider."""
    
    def __init__(self, host: str = "http://localhost:11434", default_model: str = "llama3"):
        """Initialize the Ollama provider.
        
        Args:
            host: The Ollama API host
            default_model: Default model to use if not specified
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError(
                "Ollama package not installed. Install with 'pip install ollama'"
            )
        
        self.host = host
        self.default_model = default_model
        self.client = ollama.AsyncClient(host=host)
        logging.info(f"Initialized Ollama provider with host {host}")
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate text from Ollama.
        
        Args:
            request: The LLM request
            
        Returns:
            LlmResponse: The LLM response
        """
        model = request.model or self.default_model
        
        # Handle chat-based requests (preferred for most Ollama models)
        if request.messages:
            messages = [{"role": m.role, "content": m.content} for m in request.messages]
            
            # Add system prompt if provided and not already in messages
            if request.system_prompt and not any(m.role == "system" for m in request.messages):
                messages.insert(0, {"role": "system", "content": request.system_prompt})
                
            try:
                # Check specific version/API compatibility
                try:
                    response = await self.client.chat(
                        model=model,
                        messages=messages,
                        options={
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        },
                        stream=False,
                    )
                except TypeError:
                    # Older versions might have a different API
                    logging.info("Using alternative Ollama API format")
                    response = await self.client.chat(
                        model=model,
                        messages=messages,
                        stream=False,
                    )
                return self._process_ollama_chat_response(response, model)
            except Exception as e:
                logging.error(f"Error generating text with Ollama: {e}")
                # Fallback to mock provider
                return await MockLlmProvider().generate(request)
                
        # Handle prompt-based requests
        elif request.prompt:
            try:
                prompt = request.prompt
                if request.system_prompt:
                    prompt = f"{request.system_prompt}\n\n{prompt}"
                    
                # Check specific version/API compatibility
                try:
                    response = await self.client.generate(
                        model=model,
                        prompt=prompt,
                        options={
                            "temperature": request.temperature,
                            "num_predict": request.max_tokens
                        },
                        stream=False,
                    )
                except TypeError:
                    # Older versions might have a different API
                    logging.info("Using alternative Ollama API format")
                    response = await self.client.generate(
                        model=model,
                        prompt=prompt,
                        stream=False,
                    )
                return self._process_ollama_generate_response(response, model)
            except Exception as e:
                logging.error(f"Error generating text with Ollama: {e}")
                # Fallback to mock provider
                return await MockLlmProvider().generate(request)
        else:
            raise ValueError("Either messages or prompt must be provided")
    
    def _process_ollama_chat_response(self, response: Any, model: str) -> LlmResponse:
        """Process the Ollama chat response.
        
        Args:
            response: The Ollama response
            model: The model used
            
        Returns:
            LlmResponse: The processed response
        """
        # Handle response based on its type
        if isinstance(response, dict):
            # Handle dictionary response (newer Ollama versions)
            if "message" in response and isinstance(response["message"], dict):
                text = response["message"].get("content", "")
            else:
                text = response.get("response", "")
                
            prompt_tokens = response.get("prompt_eval_count", 0)
            completion_tokens = response.get("eval_count", 0)
            finish_reason = response.get("done", True)
        else:
            # Handle object response (older Ollama versions)
            if hasattr(response, "message") and hasattr(response.message, "content"):
                text = response.message.content
            else:
                text = response.response if hasattr(response, "response") else str(response)
                
            prompt_tokens = response.prompt_eval_count if hasattr(response, "prompt_eval_count") else 0
            completion_tokens = response.eval_count if hasattr(response, "eval_count") else 0
            finish_reason = response.done if hasattr(response, "done") else "completed"
            
        return LlmResponse(
            text=text,
            usage=LlmResponseUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model=model,
            provider="ollama",
            finish_reason=str(finish_reason),
        )
    
    def _process_ollama_generate_response(self, response: Any, model: str) -> LlmResponse:
        """Process the Ollama generate response.
        
        Args:
            response: The Ollama response
            model: The model used
            
        Returns:
            LlmResponse: The processed response
        """
        # Handle response based on its type
        if isinstance(response, dict):
            # Handle dictionary response (newer Ollama versions)
            text = response.get("response", "")
            prompt_tokens = response.get("prompt_eval_count", 0)
            completion_tokens = response.get("eval_count", 0)
            finish_reason = response.get("done", True)
        else:
            # Handle object response (older Ollama versions)
            text = response.response if hasattr(response, "response") else str(response)
            prompt_tokens = response.prompt_eval_count if hasattr(response, "prompt_eval_count") else 0
            completion_tokens = response.eval_count if hasattr(response, "eval_count") else 0
            finish_reason = response.done if hasattr(response, "done") else "completed"
            
        return LlmResponse(
            text=text,
            usage=LlmResponseUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model=model,
            provider="ollama",
            finish_reason=str(finish_reason),
        )


class BridgeITProvider(LlmProvider):
    """BridgeIT LLM provider for Cisco's AI platform."""
    
    def __init__(self) -> None:
        """Initialize the BridgeIT provider."""
        if not BRIDGEIT_AVAILABLE:
            raise ImportError(
                "Required packages not installed. Install with 'pip install openai requests python-dotenv'"
            )
        
        # Load environment variables if dotenv is available
        if DOTENV_AVAILABLE:
            load_dotenv()
        
        # Required configuration
        self.client_id = os.environ.get("AZURE_OPENAI_CLIENT_ID")
        self.client_secret = os.environ.get("AZURE_OPENAI_CLIENT_SECRET")
        self.app_key = os.environ.get("BRIDGEIT_APP_KEY")
        self.api_version = os.environ.get("BRIDGEIT_API_VERSION", "2024-07-01-preview")
        self.token_url = os.environ.get("BRIDGEIT_TOKEN_URL", "https://id.cisco.com/oauth2/default/v1/token")
        self.llm_endpoint = os.environ.get("BRIDGEIT_LLM_ENDPOINT", "https://chat-ai.cisco.com")
        self.default_model = os.environ.get("BRIDGEIT_DEPLOYMENT_NAME", "gpt-4o-mini")
        
        # Validate required environment variables
        self._validate_config()
        
        # Initialize OpenAI configuration
        openai.api_type = "azure"  # type: ignore
        openai.api_version = self.api_version  # type: ignore
        
        # Setup retry strategy for requests
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Get authentication token
        self.token = self._get_auth_token()
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.llm_endpoint,
            api_key=self.token,
            api_version=self.api_version,
        )
        logging.info(f"Initialized BridgeIT provider with endpoint {self.llm_endpoint}")
    
    def _validate_config(self) -> None:
        """Validate required configuration parameters."""
        required_vars = {
            "AZURE_OPENAI_CLIENT_ID": self.client_id,
            "AZURE_OPENAI_CLIENT_SECRET": self.client_secret,
            "BRIDGEIT_APP_KEY": self.app_key
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _get_auth_token(self) -> str:
        """Get authentication token from BridgeIT with retry logic."""
        auth_key = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")
        
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_key}",
        }
        
        try:
            response = self.session.post(
                self.token_url,
                headers=headers,
                data="grant_type=client_credentials",
                timeout=10
            )
            response.raise_for_status()
            token_data = response.json()
            token = token_data.get("access_token")
            if not token:
                raise ValueError("No access token in response")
            return token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve authentication token: {e}")
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate text from BridgeIT.
        
        Args:
            request: The LLM request
            
        Returns:
            LlmResponse: The LLM response
        """
        model = request.model or self.default_model
        
        try:
            # Format the request for BridgeIT API
            user_param = {"appkey": self.app_key}
            
            # Prefer chat format if messages are provided
            if request.messages:
                messages = [{"role": m.role, "content": m.content} for m in request.messages]
                
                # Add system prompt if provided and not already in messages
                if request.system_prompt and not any(m["role"] == "system" for m in messages):
                    messages.insert(0, {"role": "system", "content": request.system_prompt})
                
                # Make the chat completion request
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1024,
                    user=json.dumps(user_param),
                )
                return self._process_chat_response(response, model)
            
            # Use completion format if only prompt is provided
            elif request.prompt:
                # If system prompt is provided, prepend it to the prompt
                prompt = request.prompt
                if request.system_prompt:
                    prompt = f"{request.system_prompt}\n\n{prompt}"
                    
                # Create prompt message
                messages = [{"role": "user", "content": prompt}]
                
                # Make the chat completion request (BridgeIT primarily uses chat API)
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1024,
                    user=json.dumps(user_param),
                )
                return self._process_chat_response(response, model)
            else:
                raise ValueError("Either messages or prompt must be provided")
        except Exception as e:
            logging.error(f"Error generating text with BridgeIT: {e}")
            # Fallback to mock provider if there's an error
            mock_provider = MockLlmProvider()
            return await mock_provider.generate(request)
    
    def _process_chat_response(self, response: Any, model: str) -> LlmResponse:
        """Process the BridgeIT chat response.
        
        Args:
            response: The BridgeIT response
            model: The model used
            
        Returns:
            LlmResponse: The processed response
        """
        # Extract content from response with fallback for None
        try:
            if hasattr(response, "choices") and response.choices:
                if hasattr(response.choices[0], "message") and hasattr(response.choices[0].message, "content"):
                    text = response.choices[0].message.content
                    if text is None:
                        text = "No content returned from the model."
                else:
                    text = "Response format not as expected."
            else:
                text = "Empty response from model."
                
            # Ensure text is never None
            if text is None:
                text = "No content returned from the model."
        except Exception as e:
            logging.error(f"Error extracting text from BridgeIT response: {e}")
            text = f"Error processing response: {str(e)}"
        
        # Extract usage statistics if available
        try:
            usage = response.usage if hasattr(response, "usage") else None
            if usage:
                prompt_tokens = usage.prompt_tokens
                completion_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens
            else:
                # Estimate tokens if not available
                prompt_tokens = 0
                completion_tokens = len(text.split())
                total_tokens = completion_tokens
        except Exception as e:
            logging.error(f"Error extracting usage from BridgeIT response: {e}")
            prompt_tokens = 0
            completion_tokens = len(text.split()) if text else 0
            total_tokens = completion_tokens
        
        # Extract finish reason
        try:
            if hasattr(response, "choices") and response.choices and hasattr(response.choices[0], "finish_reason"):
                finish_reason = response.choices[0].finish_reason
            else:
                finish_reason = "completed"
        except Exception as e:
            logging.error(f"Error extracting finish reason from BridgeIT response: {e}")
            finish_reason = "error"
        
        return LlmResponse(
            text=text,
            usage=LlmResponseUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            model=model,
            provider="bridgeit",
            finish_reason=str(finish_reason),
        )


class LlmService:
    """Service for interacting with LLMs."""
    
    def __init__(self) -> None:
        """Initialize the LLM service."""
        self.providers: Dict[str, LlmProvider] = {
            "mock": MockLlmProvider(),
        }
        
        # Try to initialize Ollama provider
        if OLLAMA_AVAILABLE:
            try:
                self.providers["ollama"] = OllamaProvider()
                logging.info("Ollama provider initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize Ollama provider: {e}")
        
        # Try to initialize BridgeIT provider
        if BRIDGEIT_AVAILABLE:
            try:
                self.providers["bridgeit"] = BridgeITProvider()
                logging.info("BridgeIT provider initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize BridgeIT provider: {e}")
    
    async def generate(self, request: LlmRequest) -> LlmResponse:
        """Generate text from the LLM.
        
        Args:
            request: The LLM request
            
        Returns:
            LlmResponse: The LLM response
        """
        provider_name = request.provider.lower()
        
        if provider_name not in self.providers:
            logging.warning(f"Provider {provider_name} not available, falling back to mock")
            provider_name = "mock"
        
        provider = self.providers[provider_name]
        response = await provider.generate(request)
        return response