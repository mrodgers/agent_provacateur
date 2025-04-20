# Ollama Integration

This document describes how to integrate Agent Provocateur with [Ollama](https://github.com/ollama/ollama) for local LLM capabilities.

## Overview

The Ollama integration enables your Agent Provocateur project to utilize local LLMs for:
- Text generation with various open-source models
- Chat completions with optimized models like Llama, Mistral, etc.
- Low-latency inference without external API dependencies
- Private, on-device AI processing

## Prerequisites

Before using the Ollama integration, you need:

- **Ollama** installed and running on your machine:
  - Download from [ollama.com/download](https://ollama.com/download)
  - Available for macOS, Linux, and Windows
- **Models** pulled to your local machine:
  - Run `ollama pull llama3` to download Llama 3
  - Or any other model from [Ollama's model library](https://ollama.com/library)
- **Python dependencies**:
  - `ollama` Python client library

## Installation

Install the Ollama dependencies as part of Agent Provocateur:

```bash
# Install with Ollama support only
pip install -e ".[llm]"

# Or install with all features including Ollama
pip install -e ".[dev,llm,bridgeit,redis,monitoring]"
```

## Usage Examples

### Python Code Example

Here's how to use Ollama in your Python code:

```python
from agent_provocateur.llm_service import LlmService
from agent_provocateur.models import LlmRequest, LlmMessage

async def example():
    # Initialize the LLM service (automatically sets up all available providers)
    service = LlmService()
    
    # Simple prompt-based request
    request = LlmRequest(
        provider="ollama",
        model="llama3",
        prompt="Why is the sky blue?",
        temperature=0.7,
        max_tokens=1024
    )
    
    # Generate text and print response
    response = await service.generate(request)
    print(f"Answer: {response.text}")
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage.prompt_tokens} prompt tokens, " 
          f"{response.usage.completion_tokens} completion tokens")
    
    # Using the chat format for better results with chat models
    chat_request = LlmRequest(
        provider="ollama",
        model="llama3",
        messages=[
            LlmMessage(role="system", content="You are a helpful assistant specializing in physics."),
            LlmMessage(role="user", content="Why is the sky blue?")
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    # Generate text from chat request
    chat_response = await service.generate(chat_request)
    print(f"Chat Answer: {chat_response.text}")
```

### Command Line Usage

The `ap-llm` CLI tool provides easy access to Ollama from the command line:

```bash
# List available providers to verify Ollama is available
ap-llm --list-providers

# Basic usage with a specific model
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?"

# Using chat messages format (recommended for best results)
ap-llm --provider ollama --model llama3 --messages "system:You are a helpful assistant,user:Why is the sky blue?"

# Customizing generation parameters
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?" --temperature 0.3 --max-tokens 500

# Output JSON to inspect the full response
ap-llm --provider ollama --model llama3 --prompt "Why is the sky blue?" --json
```

## How It Works

### Provider Architecture

The Ollama integration follows Agent Provocateur's provider pattern:

1. The `OllamaProvider` class implements the `LlmProvider` interface
2. The provider is automatically registered in the `LlmService` if dependencies are available
3. Requests are routed to the provider based on the `provider` parameter in the request

### Connection to Ollama

The provider connects to your local Ollama instance:

1. Initialization:
   - Attempts to connect to the Ollama server (default: http://localhost:11434)
   - Creates an async client for non-blocking communication
   - Sets up default model and configuration
   
2. API Integration:
   - Supports both chat and completion endpoints
   - Handles different Ollama API versions automatically
   - Formats requests according to the Ollama API specification

### Version Compatibility

The provider includes special handling for different Ollama versions:

```python
try:
    # Try with newer API format
    response = await self.client.chat(
        model=model,
        messages=messages,
        options={"temperature": request.temperature, "num_predict": request.max_tokens},
        stream=False,
    )
except TypeError:
    # Fall back to older API format if needed
    response = await self.client.chat(
        model=model,
        messages=messages,
        stream=False,
    )
```

## Advanced Configuration

### Custom Ollama Provider

You can create a custom Ollama provider with specific settings:

```python
from agent_provocateur.llm_service import OllamaProvider

# Create a custom Ollama provider
provider = OllamaProvider(
    host="http://ollama.internal.network:11434",  # Custom host/port
    default_model="wizardcoder"  # Default model to use
)

# Use the provider directly
response = await provider.generate(request)
```

### Remote Ollama Servers

To connect to a remote Ollama server:

```python
# Initialize LLM service with custom Ollama provider
service = LlmService()
service.providers["ollama"] = OllamaProvider(
    host="http://your.ollama.server:11434"
)
```

## Troubleshooting

If you encounter issues with the Ollama integration:

1. Verify that Ollama is running with `ps aux | grep ollama`
2. Check that your model is available with `ollama list`
3. Test direct Ollama access with `curl http://localhost:11434/api/tags`
4. Ensure network connectivity if using a remote server
5. Increase logging level for more details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

For complete API details, refer to the source code:
- `src/agent_provocateur/llm_service.py`: Contains the `OllamaProvider` implementation
- `src/agent_provocateur/models.py`: Contains the data models used for requests and responses

For more information about the Ollama API, see [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md).