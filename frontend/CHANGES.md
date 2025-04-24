# Frontend Changes Log

## 2025-04-23

### Added
- Build number system for easily tracking UI deployments
  - Added build_number.txt to store current build number in YYYYMMDD.n format
  - Added build number display in UI footer and system info modal
  - Created scripts/increment_build.py to increment the build number (Python)
  - Created scripts/increment_build.sh to increment the build number (Bash)
  - Created scripts/update_ui.sh for incrementation and server restart

### Changed
- Updated system info endpoint (/api/info) to include build number
- Added MCP service port checks to monitor Entity Detector, Web Search, and GraphRAG MCPs
- Enhanced system information display with additional port information
- Updated landing page to show build number in amber color for visibility