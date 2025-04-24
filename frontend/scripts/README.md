# Frontend Scripts

This directory contains utility scripts for the Agent Provocateur frontend.

## Build Number Management

To help track versions and deployments, the system uses a `build_number.txt` file in the frontend directory. This file contains a build identifier in the format `YYYYMMDD.n` where:

- `YYYYMMDD` is the date of the build
- `n` is a sequential revision number for builds on the same day

### Scripts

- `increment_build.py`: Python script that increments the build number
  - If the date has changed since the last build, reset the revision to 1
  - If the date is the same, increment the revision number

- `increment_build.sh`: Shell script version of the same functionality
  - Better for CI/CD integrations and automation

- `update_ui.sh`: Comprehensive script that:
  - Increments the build number
  - (Could run any asset compilation steps if needed)
  - Restarts the UI server (unless --no-restart flag is used)

### Usage

```bash
# Manually increment the build number (Python version)
python scripts/increment_build.py

# Manually increment the build number (Shell version)
./scripts/increment_build.sh

# Update the UI with a new build number and restart
./scripts/update_ui.sh

# Update the UI with a new build number without restarting server
./scripts/update_ui.sh --no-restart

# CI/CD integration
# In your CI/CD pipeline, add a step to increment the build number before deployment
```

### Examples

- `20250423.1` = First build on April 23, 2025
- `20250423.2` = Second build on April 23, 2025
- Next day: `20250424.1` = First build on April 24, 2025

## Integration with UI

The build number is displayed in the UI footer and in the system information modal. This allows users and developers to easily identify which version they are using, which is helpful for:

- Troubleshooting
- Support requests
- Confirming deployment status
- Tracking changes across environments