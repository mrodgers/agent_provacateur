# Changelog

## [Unreleased]

### Added
- Comprehensive test suite with 81.89% statement coverage
- Unit tests for entity extraction functionality
- Tests for RegexDetector and NlpDetector implementations
- API route tests for all endpoints
- Frontend integration tests for error handling and fallback mechanisms
- Utility tests for cache and logger modules
- Detailed test documentation in TESTING.md and tests/README.md
- Automated testing script for CI/CD environments
- XML-specific entity extraction tests

### Changed
- Enhanced error handling in entity detection
- Improved XML entity extraction with specific handling for price, author, and title elements
- Updated README with detailed testing instructions

### Fixed
- Improved frontend integration with fallback mechanism for API errors
- Added service status checking for better error reporting in UI

## [0.1.0] - Initial Release

### Added
- Initial implementation of Entity Detector MCP server
- Support for regex and NLP-based entity detection
- MCP-compliant API endpoints
- Basic caching functionality
- Configuration through environment variables