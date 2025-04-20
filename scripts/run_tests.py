#!/usr/bin/env python3
"""
Test harness script for running comprehensive test suite for Agent Provocateur.

This script runs unit tests, integration tests, and validates both frontend and backend.
It offers various options to customize the testing process.

Usage examples:
  ./scripts/run_tests.py                   # Run all tests
  ./scripts/run_tests.py --type frontend   # Only run frontend tests
  ./scripts/run_tests.py --type backend    # Only run backend tests
  ./scripts/run_tests.py --module xml      # Only run XML-related tests
  ./scripts/run_tests.py --coverage        # Generate coverage report
  ./scripts/run_tests.py --failfast        # Stop on first failure
  
  # Combine options
  ./scripts/run_tests.py --type backend --module xml --coverage
"""

import os
import sys
import argparse
import subprocess
import time
import re
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Define test categories and related files
TEST_CATEGORIES = {
    "frontend": ["test_frontend_server.py"],
    "backend": ["test_backend_api.py"],
    "integration": ["test_integration.py"],
    "xml": ["test_xml_parser.py", "test_xml_agent.py", "test_xml_integration.py", 
            "test_xml_agent_enhanced.py"],
    "messaging": ["test_a2a_messaging.py"],
    "agent": ["test_agent_base.py", "test_agent_basic.py"],
    "document": ["test_document_processing.py", "test_document_loader.py", "test_doc_agent.py"],
    "cli": ["test_cli_research.py"],
    "research": ["test_research_supervisor.py"],
}


def run_command(command, cwd=None, env=None):
    """Run a command and print its output."""
    print(f"\n$ {command}")
    
    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd or PROJECT_ROOT,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    
    return result.returncode == 0


def run_pytest(test_path, options=None, coverage=False):
    """Run pytest on a specific test path."""
    if options is None:
        options = []
    
    if coverage:
        options.extend([
            "--cov=agent_provocateur",
            "--cov-report=term",
            "--cov-report=html"
        ])
    
    # Construct the command
    command = [
        "python -m pytest",
        test_path,
        " ".join(options),
        "-v"
    ]
    
    return run_command(" ".join(command))


def run_category_tests(category, options=None, coverage=False):
    """Run tests for a specific category."""
    if category not in TEST_CATEGORIES:
        print(f"Unknown category: {category}")
        return False
        
    test_files = TEST_CATEGORIES[category]
    test_paths = [f"tests/{test_file}" for test_file in test_files]
    test_path_str = " ".join(test_paths)
    
    print(f"\n==== Running {category.title()} Tests ====")
    return run_pytest(test_path_str, options, coverage=coverage)


def run_module_tests(module, options=None, coverage=False):
    """Run tests for a specific module (like 'xml', 'document', etc.)."""
    if module not in TEST_CATEGORIES:
        print(f"Unknown module: {module}")
        return False
        
    test_files = TEST_CATEGORIES[module]
    test_paths = [f"tests/{test_file}" for test_file in test_files]
    test_path_str = " ".join(test_paths)
    
    print(f"\n==== Running {module.title()} Related Tests ====")
    return run_pytest(test_path_str, options, coverage=coverage)


def run_all_tests(options=None, coverage=False, exclude_patterns=None):
    """Run all tests."""
    print("\n==== Running All Tests ====")
    
    # Base command to run all tests
    cmd = "tests/"
    
    # Add exclusion patterns if specified
    if exclude_patterns:
        exclusion_expr = " and ".join([f"not {pattern}" for pattern in exclude_patterns])
        cmd = f"{cmd} -k '{exclusion_expr}'"
    else:
        # By default, exclude the tests that require actual servers
        cmd = f"{cmd} -k 'not TestFrontendBackendIntegration'"
    
    return run_pytest(cmd, options, coverage=coverage)


def setup_env():
    """Set up the environment for testing."""
    print("\n==== Setting Up Test Environment ====")
    
    # Create necessary directories
    directories = [
        PROJECT_ROOT / "frontend" / "uploads",
        PROJECT_ROOT / "tests" / "test_data",
        PROJECT_ROOT / "tests" / "test_data" / "xml_documents",
        PROJECT_ROOT / "tests" / "test_data" / "documents",
        PROJECT_ROOT / "tests" / "test_data" / "xml_scripts",
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)
        print(f"Ensured directory exists: {directory.relative_to(PROJECT_ROOT)}")
    
    # Check if required XML test files exist and create if missing
    xml_docs_dir = PROJECT_ROOT / "tests" / "test_data" / "xml_documents"
    
    sample_xml_files = {
        "simple.xml": """<?xml version="1.0" encoding="UTF-8"?>
<research>
    <metadata>
        <title>Sample Research Paper</title>
        <author>John Doe</author>
        <date>2023-01-15</date>
    </metadata>
    <abstract>
        This is a sample abstract that contains statements requiring verification.
    </abstract>
    <findings>
        <finding id="f1">
            <statement>The global temperature has risen by 1.1°C since pre-industrial times.</statement>
            <confidence>high</confidence>
        </finding>
        <finding id="f2">
            <statement>Renewable energy adoption increased by 45% in the last decade.</statement>
            <confidence>medium</confidence>
        </finding>
    </findings>
    <references>
        <reference id="r1">IPCC Climate Report 2022</reference>
        <reference id="r2">Energy Statistics Quarterly, Vol 12</reference>
    </references>
</research>""",
        "complex.xml": """<?xml version="1.0" encoding="UTF-8"?>
<product-catalog xmlns:prod="http://example.com/product" xmlns:mfg="http://example.com/manufacturer">
    <prod:product id="p1">
        <prod:name>Eco-friendly Water Bottle</prod:name>
        <prod:description>Sustainable water bottle made from recycled materials.</prod:description>
        <prod:price currency="USD">24.99</prod:price>
        <prod:sustainability-score>9.5</prod:sustainability-score>
        <prod:claims>
            <prod:claim id="c1">Made from 100% recycled ocean plastic</prod:claim>
            <prod:claim id="c2">Carbon-neutral manufacturing process</prod:claim>
        </prod:claims>
        <mfg:details>
            <mfg:manufacturer>EcoGoods Inc.</mfg:manufacturer>
            <mfg:country>Canada</mfg:country>
            <mfg:certification>ISO 14001</mfg:certification>
        </mfg:details>
    </prod:product>
</product-catalog>"""
    }
    
    # Create test XML files if they don't exist
    for filename, content in sample_xml_files.items():
        file_path = xml_docs_dir / filename
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created test file: {file_path.relative_to(PROJECT_ROOT)}")
        else:
            print(f"Test file exists: {file_path.relative_to(PROJECT_ROOT)}")
    
    # Create sample text document if it doesn't exist
    text_doc_path = PROJECT_ROOT / "tests" / "test_data" / "documents" / "text_document.md"
    if not text_doc_path.exists():
        with open(text_doc_path, "w", encoding="utf-8") as f:
            f.write("""# Sample Text Document
            
This is a sample text document for testing document processing.

## Features
- Markdown format
- Multiple sections
- Test content

## Usage
Use this document to test the document processing system.
""")
        print(f"Created test file: {text_doc_path.relative_to(PROJECT_ROOT)}")
    
    # Create sample code document if it doesn't exist
    code_doc_path = PROJECT_ROOT / "tests" / "test_data" / "documents" / "code_document.py"
    if not code_doc_path.exists():
        with open(code_doc_path, "w", encoding="utf-8") as f:
            f.write("""# Sample code document for testing
def sample_function():
    \"\"\"This is a sample function for testing code documents.\"\"\"
    return "Sample result"

class SampleClass:
    \"\"\"A sample class for testing.\"\"\"
    
    def __init__(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
""")
        print(f"Created test file: {code_doc_path.relative_to(PROJECT_ROOT)}")
    
    # Create sample JSON document if it doesn't exist
    json_doc_path = PROJECT_ROOT / "tests" / "test_data" / "documents" / "structured_data.json"
    if not json_doc_path.exists():
        with open(json_doc_path, "w", encoding="utf-8") as f:
            f.write("""
{
    "document_type": "structured_data",
    "metadata": {
        "title": "Sample JSON Data",
        "version": "1.0",
        "date": "2023-01-01"
    },
    "data": {
        "items": [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300}
        ],
        "total_count": 3,
        "total_value": 600
    }
}
""")
        print(f"Created test file: {json_doc_path.relative_to(PROJECT_ROOT)}")
    
    print("\nEnvironment setup complete")
    return True


def main():
    """Main entry point for the test harness."""
    description = """
Run tests for Agent Provocateur

This script provides a unified way to run tests for the Agent Provocateur project.
It supports running different categories of tests, generating coverage reports,
and more.

Basic usage examples:
  ./scripts/run_tests.py                     # Run all tests
  ./scripts/run_tests.py --type frontend     # Run only frontend tests
  ./scripts/run_tests.py --module xml        # Run XML-related tests
  ./scripts/run_tests.py --file parser       # Run test_parser.py
  ./scripts/run_tests.py --coverage          # Generate coverage report
  ./scripts/run_tests.py --list-categories   # List all test categories
  
Advanced usage:
  ./scripts/run_tests.py --module xml --coverage      # XML tests with coverage
  ./scripts/run_tests.py --file xml_parser --verbose  # Detailed output
  ./scripts/run_tests.py --exclude slow               # Skip slow tests
"""
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main testing group - only one of these can be selected
    test_group = parser.add_argument_group("Test Selection")
    group = test_group.add_mutually_exclusive_group()
    group.add_argument(
        "--type",
        choices=["all", "frontend", "backend", "integration"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    group.add_argument(
        "--module",
        choices=list(TEST_CATEGORIES.keys()),
        help="Run tests for a specific module (e.g., xml, document, messaging)"
    )
    group.add_argument(
        "--file",
        help="Run a specific test file or pattern (e.g., test_xml_parser.py)"
    )
    
    # Options for test execution
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--skip-setup",
        action="store_true",
        help="Skip environment setup"
    )
    parser.add_argument(
        "--failfast",
        action="store_true",
        help="Stop on first failure"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Patterns to exclude (e.g., 'slow')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase output verbosity (-v, -vv, etc.)"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available test categories"
    )
    
    args = parser.parse_args()
    
    # If requested, just list the categories and exit
    if args.list_categories:
        print("Available test categories:")
        for category, files in sorted(TEST_CATEGORIES.items()):
            print(f"  {category:12s} - {len(files)} tests ({', '.join(files)})")
        return 0
    
    # Set up test options
    options = []
    if args.failfast:
        options.append("-xvs")
    
    # Add verbosity options
    if args.verbose >= 2:
        options.append("-vv")
    elif args.verbose == 1:
        options.append("-v")
    
    # Prepare the environment
    if not args.skip_setup:
        if not setup_env():
            print("Failed to set up environment")
            return 1
    
    # Run the requested tests
    success = True
    
    if args.file:
        # Run a specific test file or pattern
        print(f"\n==== Running Specific Test: {args.file} ====")
        file_pattern = args.file
        
        # Handle various input patterns
        if os.path.exists(file_pattern):
            # User provided an exact path
            pass
        elif os.path.exists(f"tests/{file_pattern}"):
            # File is in the tests directory
            file_pattern = f"tests/{file_pattern}"
        elif file_pattern.startswith("test_") and os.path.exists(f"tests/{file_pattern}"):
            # File already has test_ prefix
            file_pattern = f"tests/{file_pattern}"
        elif "." not in file_pattern and os.path.exists(f"tests/test_{file_pattern}.py"):
            # File needs test_ prefix and .py extension
            file_pattern = f"tests/test_{file_pattern}.py"
        elif os.path.exists(f"tests/test_{file_pattern}"):
            # File needs test_ prefix
            file_pattern = f"tests/test_{file_pattern}"
        else:
            # Default - assume it's in tests directory with test_ prefix
            file_pattern = f"tests/test_{file_pattern}" if "." not in file_pattern else f"tests/{file_pattern}"
            
        print(f"Using test path: {file_pattern}")
        success = run_pytest(file_pattern, options, coverage=args.coverage)
    
    elif args.module:
        # Run tests for a specific module
        success = run_module_tests(args.module, options, coverage=args.coverage)
    
    else:
        # Run tests by type (default is "all")
        if args.type == "all":
            exclude_patterns = args.exclude or ["TestFrontendBackendIntegration"]
            success = run_all_tests(options, coverage=args.coverage, exclude_patterns=exclude_patterns)
        else:
            category_success = run_category_tests(args.type, options, coverage=args.coverage)
            success = success and category_success
    
    if success:
        print("\n==== All tests passed! ====")
        return 0
    else:
        print("\n==== Some tests failed! ====")
        return 1


if __name__ == "__main__":
    sys.exit(main())