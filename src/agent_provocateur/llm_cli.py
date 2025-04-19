#!/usr/bin/env python3
"""Command-line interface for testing LLM providers."""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from agent_provocateur.llm_service import LlmService
from agent_provocateur.models import LlmMessage, LlmRequest


async def main_async(args: argparse.Namespace) -> int:
    """Run the LLM CLI asynchronously.
    
    Args:
        args: Command-line arguments
        
    Returns:
        int: Exit code
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not args.debug else logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    
    # Initialize LLM service
    llm_service = LlmService()
    
    # Check available providers
    if args.list_providers:
        print("Available LLM providers:")
        for provider_name in llm_service.providers.keys():
            print(f"- {provider_name}")
        return 0
    
    # Use prompt or messages based on input
    if args.prompt:
        request = LlmRequest(
            prompt=args.prompt,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            system_prompt=args.system_prompt,
            provider=args.provider,
            model=args.model,
        )
    elif args.messages:
        # Parse messages from command line (format: "role:content,role:content")
        messages: List[LlmMessage] = []
        for msg_str in args.messages.split(","):
            role, content = msg_str.split(":", 1)
            messages.append(LlmMessage(role=role, content=content))
            
        request = LlmRequest(
            messages=messages,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            provider=args.provider,
            model=args.model,
        )
    else:
        print("Error: Either --prompt or --messages must be provided.")
        return 1
    
    try:
        # Generate text
        response = await llm_service.generate(request)
        
        # Print the response
        if args.json:
            import json
            print(json.dumps(response.dict(), indent=2))
        else:
            print("\n=== LLM Response ===")
            print(response.text)
            print("\n=== Metadata ===")
            print(f"Provider: {response.provider}")
            print(f"Model: {response.model}")
            print(f"Tokens: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


def main() -> int:
    """Entry point for the LLM CLI.
    
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(description="Test LLM providers")
    
    # LLM options
    parser.add_argument("--provider", default="mock", help="LLM provider (mock, ollama)")
    parser.add_argument("--model", help="Model name (provider-specific)")
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--prompt", help="Text prompt for the LLM")
    input_group.add_argument("--messages", help="Chat messages in format 'role:content,role:content'")
    
    # Other options
    parser.add_argument("--system-prompt", help="System prompt for the LLM")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-1.0)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Maximum tokens to generate")
    
    # Utility options
    parser.add_argument("--list-providers", action="store_true", help="List available providers")
    parser.add_argument("--json", action="store_true", help="Output response as JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130


if __name__ == "__main__":
    sys.exit(main())