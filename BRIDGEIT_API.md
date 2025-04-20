# BridgeIT Integration

This document describes how to integrate Agent Provocateur with Cisco's BridgeIT platform, which provides a gateway to Azure OpenAI models.

## Overview

The BridgeIT integration enables your Agent Provocateur project to utilize Cisco's AI platform for:
- Text generation with Azure OpenAI models
- Chat completions with chat-optimized models like GPT-4o
- Consistent authentication with Cisco's OAuth2 service

## Prerequisites

Before using the BridgeIT integration, you need:

- **Cisco BridgeIT account** with access credentials:
  - Client ID
  - Client secret
  - App key
- **Python dependencies**:
  - `openai` (v1.0.0+)
  - `requests`
  - `python-dotenv`

## Installation

Install the BridgeIT dependencies as part of Agent Provocateur:

```bash
# Install with BridgeIT support only
pip install -e ".[bridgeit]"

# Or install with all features including BridgeIT
pip install -e ".[dev,llm,bridgeit,redis,monitoring]"
```

## Environment Configuration

The BridgeIT integration uses environment variables for configuration. Create a `.env` file in your project root with the following settings:

### Required Environment Variables

These variables must be set for the BridgeIT provider to function:

```bash
# Authentication credentials
AZURE_OPENAI_CLIENT_ID=your_client_id
AZURE_OPENAI_CLIENT_SECRET=your_client_secret
BRIDGEIT_APP_KEY=your_app_key
```

### Optional Environment Variables

These variables have default values and can be customized as needed:

```bash
# API settings
BRIDGEIT_API_VERSION=2024-07-01-preview
BRIDGEIT_TOKEN_URL=https://id.cisco.com/oauth2/default/v1/token
BRIDGEIT_LLM_ENDPOINT=https://chat-ai.cisco.com
BRIDGEIT_DEPLOYMENT_NAME=gpt-4o-mini
```

You can set these variables in your environment or in a `.env` file in your project directory.

## Usage Examples

### Python Code Example

Here's how to use BridgeIT in your Python code:

```python
from agent_provocateur.llm_service import LlmService
from agent_provocateur.models import LlmRequest, LlmMessage

async def example():
    # Initialize the LLM service (automatically sets up all available providers)
    service = LlmService()
    
    # Simple prompt-based request
    request = LlmRequest(
        provider="bridgeit",
        prompt="What is the capital of France?",
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
        provider="bridgeit",
        messages=[
            LlmMessage(role="system", content="You are a helpful assistant specialized in geography."),
            LlmMessage(role="user", content="What is the capital of France?")
        ],
        temperature=0.7,
        max_tokens=1024
    )
    
    # Generate text from chat request
    chat_response = await service.generate(chat_request)
    print(f"Chat Answer: {chat_response.text}")
```

### Command Line Usage

The `ap-llm` CLI tool provides easy access to BridgeIT from the command line:

```bash
# List available providers to verify BridgeIT is available
ap-llm --list-providers

# Basic usage with default model
ap-llm --provider bridgeit --prompt "What is the capital of France?"

# Using chat messages format (recommended for best results)
ap-llm --provider bridgeit --messages "system:You are a helpful assistant,user:What is the capital of France?"

# Customizing generation parameters
ap-llm --provider bridgeit --prompt "What is the capital of France?" --temperature 0.3 --max-tokens 500

# Output JSON to inspect the full response
ap-llm --provider bridgeit --prompt "What is the capital of France?" --json
```

## How It Works

### Provider Architecture

The BridgeIT integration follows Agent Provocateur's provider pattern:

1. The `BridgeITProvider` class implements the `LlmProvider` interface
2. The provider is automatically registered in the `LlmService` if dependencies are available
3. Requests are routed to the provider based on the `provider` parameter in the request

### Authentication Flow

BridgeIT uses OAuth2 authentication with Azure OpenAI:

1. Initialization:
   - Reads environment variables for credentials
   - Validates required configuration
   - Sets up a requests session with retry logic
   
2. Token Acquisition:
   - Encodes client ID and secret for basic auth
   - Requests an OAuth2 token from BridgeIT's token endpoint
   - Stores the token for API requests
   
3. API Integration:
   - Initializes an Azure OpenAI client with the token
   - Formats requests according to the OpenAI API
   - Includes the BridgeIT app key with each request

### Error Handling and Fallbacks

The BridgeIT provider includes robust error handling:

```python
try:
    # Attempt to generate with BridgeIT
    response = await service.generate(request)
except Exception as e:
    print(f"Error: {e}")
    # The service automatically falls back to the mock provider
    # when BridgeIT is unavailable or encounters an error
```

## Advanced Usage

### Content Filtering Handling

The BridgeIT provider includes robust handling for Azure OpenAI content filtering responses. When content filtering occurs:

1. The provider detects the filtered response
2. Instead of failing, it returns a graceful error message
3. The proper usage statistics and finish reason are preserved

Example response when content filtering occurs:
```json
{
  "text": "No content returned from the model.",
  "usage": {
    "prompt_tokens": 33,
    "completion_tokens": 356,
    "total_tokens": 389
  },
  "model": "gpt-4o-mini",
  "provider": "bridgeit",
  "finish_reason": "content_filter"
}
```

This ensures your application continues to function even when content filtering occurs.

### Integration with LangChain

The reference `bridgeit.py` file includes a `BridgeITLangChainWrapper` class for LangChain compatibility. While we've integrated the core functionality into the Agent Provocateur architecture, you can still use the LangChain wrapper by importing it directly from the file:

```python
from langchain.llms.base import LLM
from bridgeit import BridgeITClient, BridgeITLangChainWrapper

# Initialize the BridgeIT client
client = BridgeITClient()

# Create a LangChain-compatible wrapper
langchain_llm = BridgeITLangChainWrapper(client)

# Use with LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template("What is the capital of {country}?")
chain = LLMChain(llm=langchain_llm, prompt=prompt)
result = chain.run(country="France")
print(result)
```

Note: The LangChain wrapper is not part of the main Agent Provocateur package. If you need this functionality, you should either:
1. Keep the original `bridgeit.py` file in your project for direct import
2. Create a dedicated adapter class in your own codebase

## Security Considerations

- **Credential Management**:
  - Store credentials in environment variables or `.env` files
  - Never commit credentials to version control
  - Consider using a secrets manager for production deployments

- **Token Handling**:
  - Tokens are stored in memory only
  - No token caching to disk is implemented
  - The provider automatically obtains a fresh token on initialization

- **Error Logging**:
  - Authentication errors are logged at warning level
  - Request errors are logged but sensitive data is not included
  - The fallback to mock provider ensures system availability

## Troubleshooting

### Common Issues

If you encounter issues with the BridgeIT integration:

1. **Authentication Errors**:
   - Verify your environment variables are set correctly
   - Check that your BridgeIT credentials are valid and have not expired
   - Ensure your client has the necessary permissions

2. **Content Filtering**:
   - If you receive "No content returned from the model" with a "content_filter" finish reason, your prompt may have triggered Azure OpenAI's content filter
   - Try rephrasing your prompt to avoid sensitive topics
   - Check the Azure OpenAI content filtering documentation for guidelines

3. **Connection Issues**:
   - Confirm your network allows connections to the BridgeIT endpoints
   - Check firewall settings if behind a corporate network
   - Verify that the BridgeIT service is operational

4. **Response Processing Errors**:
   - The provider now includes robust error handling for unexpected response formats
   - If you still encounter issues, please report them with the error message

### Debug Mode

For detailed diagnostics, increase the logging level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about requests, responses, and any errors that occur.

## API Reference

### Source Code References

For complete API details, refer to the source code:
- `src/agent_provocateur/llm_service.py`: Contains the `BridgeITProvider` implementation
- `src/agent_provocateur/models.py`: Contains the data models used for requests and responses

### Recent Improvements

The BridgeIT integration has been enhanced with:

1. **Robust Response Processing**:
   - Improved error handling for various response formats
   - Graceful handling of content filtering
   - Prevention of None values in response text

2. **Better Error Reporting**:
   - Detailed logging of authentication and API errors
   - Fallback to mock provider when errors occur
   - Clear error messages for debugging

3. **Type Safety**:
   - Full type annotations for mypy compatibility
   - Proper null handling throughout the codebase
   - Consistent return types for all methods