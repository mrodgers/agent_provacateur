#!/usr/bin/env python3
"""
Unified service manager for Agent Provocateur.
Starts, stops, and checks status of all required services.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import platform
import json
import psutil
import threading
import socket

# Define the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Process tracking
PROCESSES = {}
SERVICE_INFO = {}
STATUS_INTERVAL = 5  # seconds between status checks

# Known port conflicts and solutions
PORT_CONFLICT_INFO = {
    3000: {
        "common_services": ["Grafana (monitoring)", "Frontend server", "React development servers"],
        "solutions": [
            "Use port 3001 for the frontend server instead",
            "Stop the monitoring service if Grafana is not needed",
            "Change the Grafana port in monitoring/docker-compose.yml"
        ]
    },
    8000: {
        "common_services": ["MCP Server", "Django development servers", "Other backend services"],
        "solutions": [
            "Stop other development servers running on this port",
            "Use a different port for the MCP server with --port option" 
        ]
    },
    9090: {
        "common_services": ["Prometheus (monitoring)", "Webpack development servers"],
        "solutions": [
            "Stop the monitoring service if Prometheus is not needed",
            "Change the Prometheus port in monitoring/docker-compose.yml"
        ]
    }
}


class ServiceStatus(Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    DISABLED = "DISABLED"  # New status for services that can't be run due to missing dependencies


class Service:
    def __init__(self, name, start_cmd, check_cmd=None, check_port=None, depends_on=None, cwd=None, required_commands=None):
        self.name = name
        self.start_cmd = start_cmd
        self.check_cmd = check_cmd
        self.check_port = check_port
        self.depends_on = depends_on or []
        self.cwd = cwd or PROJECT_ROOT
        self.process = None
        self.status = ServiceStatus.STOPPED
        self.start_time = None
        self.pid = None
        self.stdout_file = None
        self.stderr_file = None
        self.required_commands = required_commands or []  # New: list of commands that must be available
        self.missing_dependencies = []  # New: Track missing dependencies

    def __str__(self):
        return f"{self.name} ({self.status.value})"

    def check_dependencies(self):
        """Check if all required dependencies for this service are available"""
        missing = []
        for cmd in self.required_commands:
            if not is_command_available(cmd):
                missing.append(cmd)
        self.missing_dependencies = missing
        return len(missing) == 0


def is_command_available(command):
    """Check if a command is available in the system path"""
    try:
        subprocess.run(
            ["which" if platform.system() != "Windows" else "where", command.split()[0]],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception:
        return False


def is_port_in_use(port):
    """Check if a port is in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0
    except Exception:
        return False


def check_service_port(service):
    """Check if a service's port is open"""
    if service.check_port:
        try:
            # For monitoring service, check all expected ports
            if service.name == "monitoring":
                # Check Prometheus, Pushgateway, and Grafana ports
                prometheus_port = is_port_in_use(9090)
                pushgateway_port = is_port_in_use(9091)
                grafana_port = is_port_in_use(3000)
                # Return True if any of the services are running
                return prometheus_port or pushgateway_port or grafana_port
            else:
                return is_port_in_use(service.check_port)
        except Exception:
            return False
    return None


def check_service_process(service):
    """Check if a service's process is running"""
    if service.process and service.process.poll() is None:
        return True
    return False


def check_service_custom(service):
    """Execute a custom check command for a service"""
    if not service.check_cmd:
        return None

    try:
        # In case the check is for a process, try to directly find it by name first
        if "ps aux" in service.check_cmd and "grep" in service.check_cmd:
            # Extract the search string between the grep commands
            search_terms = service.check_cmd.split('grep')[1].split('|')[0].strip("'\"")
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if any(search_terms in ' '.join(cmd).lower() for cmd in [proc.info['cmdline']] if cmd):
                    return True
        
        # Fallback to running the command
        result = subprocess.run(
            service.check_cmd,
            shell=True,
            check=False,  # Don't raise an exception if the command fails
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=service.cwd,
        )
        return result.returncode == 0
    except Exception as e:
        return False


def update_service_status(service):
    """Update the status of a service based on various checks"""
    # Don't update disabled services
    if service.status == ServiceStatus.DISABLED:
        return
        
    if service.status == ServiceStatus.STARTING:
        # For starting services, we check if it's now running
        process_running = check_service_process(service)
        port_open = check_service_port(service)
        custom_check = check_service_custom(service)

        # If any check is positive, consider it running (more lenient)
        if (port_open is True or custom_check is True or process_running):
            service.status = ServiceStatus.RUNNING
        # Only mark as error if we're sure it's not running
        elif port_open is False and (custom_check is False or custom_check is None) and not process_running:
            service.status = ServiceStatus.ERROR
    elif service.status == ServiceStatus.RUNNING:
        # For running services, we check if they're still running
        process_running = check_service_process(service)
        port_open = check_service_port(service)
        custom_check = check_service_custom(service)

        # If any check is positive, the service is still running
        if process_running or port_open is True or custom_check is True:
            service.status = ServiceStatus.RUNNING
        else:
            service.status = ServiceStatus.ERROR
    
    # Update service info
    SERVICE_INFO[service.name] = {
        "status": service.status.value,
        "start_time": service.start_time.isoformat() if service.start_time else None,
        "uptime": (datetime.now() - service.start_time).total_seconds() if service.start_time else None,
        "pid": service.pid,
        "missing_dependencies": service.missing_dependencies
    }


def start_service(service_name, services, logs_dir):
    """Start a specific service and its dependencies"""
    if service_name not in services:
        print(f"Unknown service: {service_name}")
        return False

    service = services[service_name]
    
    # Check if already running
    if service.status == ServiceStatus.RUNNING:
        print(f"{service.name} is already running")
        return True
        
    # Check dependencies first
    if not service.check_dependencies():
        dep_list = ", ".join(service.missing_dependencies)
        print(f"Cannot start {service.name}: missing required commands: {dep_list}")
        service.status = ServiceStatus.DISABLED
        return False
        
    # Check for port conflicts if this service uses a specific port
    if service.check_port:
        # Skip port check for monitoring since it's expected to use multiple ports
        port = service.check_port
        if service.name != "monitoring" and is_port_in_use(port):
            print(f"\nERROR: Cannot start {service.name}: port {port} is already in use by another process")
            
            # Provide helpful information about common port conflicts
            if port in PORT_CONFLICT_INFO:
                info = PORT_CONFLICT_INFO[port]
                print(f"\nPort {port} is commonly used by: {', '.join(info['common_services'])}")
                print("\nPossible solutions:")
                for i, solution in enumerate(info['solutions'], 1):
                    print(f"  {i}. {solution}")
                    
                # If this is the frontend server and port is 3000, provide specific help
                if service.name == "frontend" and port == 3000:
                    print("\nRecommended: Use the frontend server on port 3001 instead:")
                    print("  cd frontend && python server.py --host 127.0.0.1 --port 3001")
            else:
                print("Try stopping the conflicting process or using a different port")
                
            # Provide command to check what's using the port
            if platform.system() == "Windows":
                print(f"\nTo see what's using port {port}, run:")
                print(f"  netstat -ano | findstr :{port}")
            else:
                print(f"\nTo see what's using port {port}, run:")
                print(f"  lsof -i :{port}")
                
            service.status = ServiceStatus.ERROR
            return False

    # Check and start dependencies first
    for dep_name in service.depends_on:
        if dep_name not in services:
            print(f"Unknown dependency: {dep_name}")
            return False
        
        dep_service = services[dep_name]
        
        # Skip disabled dependencies
        if dep_service.status == ServiceStatus.DISABLED:
            print(f"Dependency {dep_name} is disabled. Making {service.name} optional.")
            continue
            
        if dep_service.status != ServiceStatus.RUNNING:
            success = start_service(dep_name, services, logs_dir)
            if not success:
                print(f"Failed to start dependency: {dep_name}")
                # Don't fail if monitoring dependency fails, just make it optional
                if dep_name == "monitoring" or dep_name == "redis":
                    print(f"Making {dep_name} optional for {service.name}")
                    continue
                else:
                    return False
    
    # Start the service
    print(f"Starting {service.name}...")
    
    # Create logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)
    
    # Open log files
    stdout_path = os.path.join(logs_dir, f"{service.name}.out.log")
    stderr_path = os.path.join(logs_dir, f"{service.name}.err.log")
    
    service.stdout_file = open(stdout_path, "a")
    service.stderr_file = open(stderr_path, "a")
    
    # Log the start time
    service.stdout_file.write(f"\n\n--- Service start at {datetime.now().isoformat()} ---\n\n")
    service.stdout_file.flush()
    
    try:
        service.process = subprocess.Popen(
            service.start_cmd,
            shell=True,
            stdout=service.stdout_file,
            stderr=service.stderr_file,
            cwd=service.cwd,
            start_new_session=True,
        )
        service.pid = service.process.pid
        service.start_time = datetime.now()
        service.status = ServiceStatus.STARTING
        
        # Wait for service to be ready
        max_wait_seconds = 30
        wait_interval = 0.5
        for _ in range(int(max_wait_seconds / wait_interval)):
            update_service_status(service)
            if service.status == ServiceStatus.RUNNING:
                print(f"{service.name} started successfully (PID: {service.pid})")
                return True
            elif service.status == ServiceStatus.ERROR:
                print(f"Error starting {service.name}")
                return False
            time.sleep(wait_interval)
        
        # If we get here, service didn't start in time
        print(f"Timed out waiting for {service.name} to start")
        service.status = ServiceStatus.ERROR
        return False
    
    except Exception as e:
        print(f"Error starting {service.name}: {e}")
        service.status = ServiceStatus.ERROR
        return False


def stop_service(service_name, services):
    """Stop a specific service and dependent services"""
    if service_name not in services:
        print(f"Unknown service: {service_name}")
        return False

    service = services[service_name]
    
    # Skip if already stopped or disabled
    if service.status in [ServiceStatus.STOPPED, ServiceStatus.DISABLED]:
        return True
    
    # Stop dependent services first (services that depend on this one)
    for other_name, other_service in services.items():
        if service_name in other_service.depends_on:
            stop_service(other_name, services)
    
    # Stop the service
    print(f"Stopping {service.name}...")
    
    # Special handling for monitoring service to ensure clean container removal
    if service.name == "monitoring":
        try:
            # Get container command 
            compose_cmd, _ = detect_container_tools()
            container_cmd = "podman" if "podman" in compose_cmd else "docker"
            
            # First try compose down
            print(f"Stopping monitoring containers with {compose_cmd}...")
            subprocess.run(
                f"cd {PROJECT_ROOT}/monitoring && {compose_cmd} down",
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Force remove any lingering containers
            print("Cleaning up any remaining monitoring containers...")
            for container in ["prometheus", "pushgateway", "grafana"]:
                subprocess.run(
                    f"{container_cmd} rm -f {container} 2>/dev/null",
                    shell=True,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Clean up volumes
            subprocess.run(
                f"{container_cmd} volume rm monitoring_grafana-storage 2>/dev/null",
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if containers are gone (for reporting purposes)
            remaining = subprocess.run(
                f"{container_cmd} ps -a | grep -E 'prometheus|pushgateway|grafana' | wc -l",
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if remaining.stdout.strip() and int(remaining.stdout.strip()) > 0:
                print(f"Warning: Some monitoring containers could not be removed")
        except Exception as e:
            print(f"Error stopping monitoring containers: {e}")
    elif service.process and service.process.poll() is None:
        # For normal processes, try graceful shutdown
        try:
            if platform.system() != "Windows":
                # On Unix-like systems, we can use SIGTERM
                os.killpg(os.getpgid(service.process.pid), signal.SIGTERM)
            else:
                # On Windows, terminate() is the best we can do
                service.process.terminate()
            
            # Wait for process to terminate
            for _ in range(10):
                if service.process.poll() is not None:
                    break
                time.sleep(0.5)
            
            # Force kill if still running
            if service.process.poll() is None:
                if platform.system() != "Windows":
                    os.killpg(os.getpgid(service.process.pid), signal.SIGKILL)
                else:
                    service.process.kill()
        except Exception as e:
            print(f"Error stopping {service.name}: {e}")
    
    # Close log files
    if service.stdout_file:
        service.stdout_file.close()
        service.stdout_file = None
    
    if service.stderr_file:
        service.stderr_file.close()
        service.stderr_file = None
    
    service.status = ServiceStatus.STOPPED
    service.process = None
    service.pid = None
    service.start_time = None
    
    print(f"{service.name} stopped")
    return True


def get_service_status(service_name, services):
    """Get the status of a specific service"""
    if service_name not in services:
        return f"Unknown service: {service_name}"
    
    service = services[service_name]
    update_service_status(service)
    
    status_str = f"{service.name}: {service.status.value}"
    
    if service.status == ServiceStatus.RUNNING:
        uptime = datetime.now() - service.start_time
        
        # Special handling for monitoring status
        if service.name == "monitoring":
            # Check specific monitoring components
            components = []
            if is_port_in_use(9090):
                components.append("prometheus:9090")
            if is_port_in_use(9091):
                components.append("pushgateway:9091") 
            if is_port_in_use(3000):
                components.append("grafana:3000")
                
            if components:
                component_str = ", ".join(components)
                status_str += f" (Components: {component_str}, Up: {format_timedelta(uptime)})"
            else:
                status_str += f" (Up: {format_timedelta(uptime)})"
        else:
            # Standard status for other services
            port_info = f", Port: {service.check_port}" if service.check_port else ""
            status_str += f" (PID: {service.pid}{port_info}, Up: {format_timedelta(uptime)})"
    elif service.status == ServiceStatus.DISABLED:
        missing_deps = ", ".join(service.missing_dependencies)
        status_str += f" (missing: {missing_deps})"
    elif service.status == ServiceStatus.ERROR:
        if service.check_port and is_port_in_use(service.check_port):
            status_str += f" (Port {service.check_port} conflict)"
    
    # Add warning for potential port conflicts even if service is running
    if service.name == "frontend" and service.status == ServiceStatus.RUNNING:
        if service.check_port == 3000 and is_port_in_use(3000):
            # Check if both frontend and grafana might be running on 3000
            if is_port_in_use(9090):  # If Prometheus is running, Grafana might be too
                status_str += " ⚠️ Port conflict with Grafana possible"
    
    return status_str


def format_timedelta(td):
    """Format a timedelta as a readable string"""
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def monitor_services(services, interval=STATUS_INTERVAL):
    """Continuously monitor services and update their status"""
    while True:
        for service in services.values():
            update_service_status(service)
        time.sleep(interval)


def check_port_conflicts():
    """Check for port conflicts across all services and report them"""
    conflicts = {}
    
    # Check common ports used by our services
    ports_to_check = [3000, 3001, 8000, 9090, 9091]
    
    for port in ports_to_check:
        if is_port_in_use(port):
            # Try to get more information about what's using the port
            process_info = None
            try:
                if platform.system() != "Windows":
                    cmd = f"lsof -i :{port} | grep LISTEN | head -1"
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.stdout.strip():
                        # Parse the lsof output to get process name and PID
                        parts = result.stdout.strip().split()
                        if len(parts) > 1:
                            process_info = f"{parts[0]} (PID {parts[1]})"
                else:
                    cmd = f"netstat -ano | findstr :{port} | findstr LISTENING"
                    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    if result.stdout.strip():
                        # Parse netstat output to get PID
                        parts = result.stdout.strip().split()
                        if len(parts) > 4:
                            pid = parts[4]
                            process_info = f"PID {pid}"
            except:
                pass
            
            conflicts[port] = {
                "in_use": True,
                "process": process_info,
                "common_services": PORT_CONFLICT_INFO.get(port, {}).get("common_services", ["Unknown service"]),
                "solutions": PORT_CONFLICT_INFO.get(port, {}).get("solutions", ["Stop the conflicting process"])
            }
    
    return conflicts


def print_status_report(services):
    """Print a status report for all services"""
    print("\n=== Service Status Report ===")
    print(f"Time: {datetime.now().isoformat()}")
    print("-----------------------------")
    
    for service_name in sorted(services.keys()):
        status_str = get_service_status(service_name, services)
        print(status_str)
    
    # Check for port conflicts
    conflicts = check_port_conflicts()
    if conflicts:
        print("\n=== Potential Port Conflicts ===")
        for port, info in conflicts.items():
            process_info = f" - Used by: {info['process']}" if info['process'] else ""
            print(f"Port {port}: IN USE{process_info}")
            print(f"  Commonly used by: {', '.join(info['common_services'])}")
            
            # If this is port 3000 and the frontend is configured to use port 3000, highlight it
            if port == 3000 and services.get('frontend', None) and services['frontend'].check_port == 3000:
                print("  ⚠️  WARNING: Frontend server is configured to use port 3000, which may conflict with Grafana")
    
    print("=============================\n")


def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = {
        "docker": "Docker or Podman for monitoring services",
        "docker-compose": "Docker Compose for monitoring services",
        "podman": "Podman container engine",
        "podman-compose": "Podman Compose for monitoring services",
        "redis-cli": "Redis client for checking Redis server",
    }
    
    missing = []
    for cmd, description in dependencies.items():
        if not is_command_available(cmd):
            missing.append(f"{cmd} ({description})")
    
    if missing:
        print("Warning: The following dependencies are missing:")
        for dep in missing:
            print(f"  - {dep}")
        print("Some services may not start or function correctly.\n")


def detect_container_tools():
    """Detect available container tools and return the best command to use"""
    if is_command_available("podman-compose"):
        return "podman-compose", ["podman", "podman-compose"]
    elif is_command_available("docker-compose"):
        return "docker-compose", ["docker", "docker-compose"]
    elif is_command_available("docker") and subprocess.run("docker compose version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
        return "docker compose", ["docker"]
    else:
        return "echo 'No container tool found. Please install docker-compose or podman-compose'", ["docker-compose"]

def get_service_definitions():
    """Define all services and their dependencies"""
    # Choose docker or podman
    compose_cmd, compose_required = detect_container_tools()
    
    # Define all services
    services = {
        "monitoring": Service(
            name="monitoring",
            # Fixed start command with proper cleanup
            start_cmd=f"cd {PROJECT_ROOT}/monitoring && "
                     f"{compose_cmd} down || true && "
                     f"{compose_cmd.split()[0]} rm -f prometheus pushgateway grafana || true && "
                     f"{compose_cmd.split()[0]} volume rm monitoring_grafana-storage || true && "
                     f"{compose_cmd} up -d",
            check_cmd=f"cd {PROJECT_ROOT}/monitoring && {compose_cmd} ps | grep -E -q 'prometheus|grafana|pushgateway'",
            check_port=9090,  # Prometheus port
            cwd=os.path.join(PROJECT_ROOT, "monitoring"),
            required_commands=compose_required
        ),
        "redis": Service(
            name="redis",
            start_cmd="redis-server --daemonize yes",
            check_cmd="redis-cli ping | grep -q 'PONG'",
            check_port=6379,
            required_commands=["redis-server", "redis-cli"]
        ),
        "mcp_server": Service(
            name="mcp_server",
            start_cmd=f"cd {PROJECT_ROOT} && ap-server --host 127.0.0.1 --port 8000",
            check_port=8000,
            check_cmd="ps aux | grep 'ap-server' | grep -v grep",
            depends_on=["monitoring", "redis"],
            required_commands=[]  # No external dependencies, part of our package
        ),
        "web_search_mcp": Service(
            name="web_search_mcp",
            start_cmd=f"cd {PROJECT_ROOT}/web_search_mcp && ./scripts/start.sh",
            check_cmd="ps aux | grep -E 'node.*dist/index.js' | grep -v grep",
            depends_on=[],  # Independent service
            cwd=os.path.join(PROJECT_ROOT, "web_search_mcp"),
            # Requires Node.js to be installed
            required_commands=["node", "npm"]
        ),
        "frontend": Service(
            name="frontend",
            start_cmd=f"cd {PROJECT_ROOT}/frontend && python server.py --host 127.0.0.1 --port 3001 --backend-url http://localhost:8000",
            check_port=3001,
            check_cmd="ps aux | grep 'server.py.*port 3001' | grep -v grep",
            depends_on=["mcp_server"],
            cwd=os.path.join(PROJECT_ROOT, "frontend"),
            required_commands=[]  # No external dependencies, part of our package
        ),
    }
    
    # Check dependencies for each service
    for service in services.values():
        service.check_dependencies()
    
    return services


def get_running_services():
    """Find running services by directly checking processes and ports"""
    result = {}
    
    # Check for ap-server (MCP server)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_info = proc.info
            cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
            
            # Check for MCP server
            if 'ap-server' in cmdline:
                result['mcp_server'] = {
                    'pid': proc_info['pid'],
                    'cmdline': cmdline
                }
            
            # Check for frontend server
            if 'server.py' in cmdline and 'frontend' in cmdline:
                result['frontend'] = {
                    'pid': proc_info['pid'],
                    'cmdline': cmdline
                }
                
            # Check for Redis
            if 'redis-server' in cmdline and not 'grep' in cmdline:
                result['redis'] = {
                    'pid': proc_info['pid'],
                    'cmdline': cmdline
                }
                
            # Check for Web Search MCP
            if ('node' in cmdline and 'dist/index.js' in cmdline) or ('web-search-mcp' in cmdline):
                result['web_search_mcp'] = {
                    'pid': proc_info['pid'],
                    'cmdline': cmdline
                }
        except:
            pass
    
    # Use additional methods to detect monitoring services (could be in containers)
    if not 'monitoring' in result:
        # Check for expected monitoring services ports
        prometheus_running = is_port_in_use(9090)
        pushgateway_running = is_port_in_use(9091)
        grafana_running = is_port_in_use(3000)
        
        if prometheus_running or pushgateway_running or grafana_running:
            result['monitoring'] = {
                'pid': 0,  # Placeholder for container PID
                'components': []
            }
            
            if prometheus_running:
                result['monitoring']['components'].append({'name': 'prometheus', 'port': 9090})
            if pushgateway_running:
                result['monitoring']['components'].append({'name': 'pushgateway', 'port': 9091})
            if grafana_running:
                result['monitoring']['components'].append({'name': 'grafana', 'port': 3000})
    
    # Try container detection as a fallback
    try:
        compose_cmd, _ = detect_container_tools()
        if compose_cmd and not 'monitoring' in result:
            # Check if monitoring containers are running using the appropriate compose command
            cmd = f"cd {PROJECT_ROOT}/monitoring && {compose_cmd} ps | grep -E 'prometheus|pushgateway|grafana' | grep -v 'Exit'"
            output = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if output.returncode == 0 and output.stdout.strip():
                result.setdefault('monitoring', {'components': []})
                for line in output.stdout.strip().split('\n'):
                    if 'prometheus' in line.lower():
                        result['monitoring']['components'].append({'name': 'prometheus', 'container': True})
                    elif 'pushgateway' in line.lower():
                        result['monitoring']['components'].append({'name': 'pushgateway', 'container': True})
                    elif 'grafana' in line.lower():
                        result['monitoring']['components'].append({'name': 'grafana', 'container': True})
    except:
        pass
            
    return result


def main():
    parser = argparse.ArgumentParser(description="Agent Provocateur Service Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start services")
    start_parser.add_argument("services", nargs="*", help="Services to start (default: all)")
    start_parser.add_argument("--force", "-f", action="store_true", help="Ignore dependency checks")
    
    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop services")
    stop_parser.add_argument("services", nargs="*", help="Services to stop (default: all)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check service status")
    status_parser.add_argument("--watch", "-w", action="store_true", help="Continuously watch status")
    status_parser.add_argument("--interval", "-i", type=int, default=5, help="Status check interval in seconds")
    
    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart services")
    restart_parser.add_argument("services", nargs="*", help="Services to restart (default: all)")
    
    # Ports command - new command to check port conflicts
    ports_parser = subparsers.add_parser("ports", help="Check port conflicts")
    ports_parser.add_argument("--check", "-c", type=int, help="Check if a specific port is in use")
    
    args = parser.parse_args()
    
    # Log directory
    logs_dir = os.path.join(PROJECT_ROOT, "logs")
    
    # Create services
    services = get_service_definitions()
    
    # Check dependencies
    check_dependencies()
    
    # Check for already running processes
    running_procs = get_running_services()
    for service_name, service in services.items():
        if service_name in running_procs:
            service.status = ServiceStatus.RUNNING
            service.pid = running_procs[service_name].get('pid')
            service.start_time = datetime.now() - timedelta(seconds=60)  # Approximate
            
    # Start the status monitoring thread
    monitor_thread = threading.Thread(
        target=monitor_services, 
        args=(services,), 
        daemon=True
    )
    monitor_thread.start()
    
    if args.command == "start":
        service_list = args.services if args.services else ["mcp_server", "frontend", "web_search_mcp"]  # Default: Start core services including web_search_mcp
        for service_name in service_list:
            start_service(service_name, services, logs_dir)
        print_status_report(services)
    
    elif args.command == "stop":
        service_list = args.services if args.services else list(services.keys())
        for service_name in service_list:
            stop_service(service_name, services)
        print_status_report(services)
    
    elif args.command == "restart":
        service_list = args.services if args.services else ["mcp_server", "frontend", "web_search_mcp"]
        for service_name in service_list:
            stop_service(service_name, services)
            start_service(service_name, services, logs_dir)
        print_status_report(services)
    
    elif args.command == "status" or args.command is None:
        if args.watch:
            try:
                while True:
                    os.system("clear" if platform.system() != "Windows" else "cls")
                    print_status_report(services)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nStopping status monitor...")
        else:
            print_status_report(services)
            
    elif args.command == "ports":
        print("\n=== Port Conflict Checker ===")
        
        if args.check:
            # Check a specific port
            port = args.check
            in_use = is_port_in_use(port)
            print(f"Port {port}: {'IN USE' if in_use else 'AVAILABLE'}")
            
            if in_use:
                # Try to get process information
                try:
                    if platform.system() != "Windows":
                        cmd = f"lsof -i :{port} | grep LISTEN"
                        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.stdout.strip():
                            print("\nProcesses using this port:")
                            print(result.stdout)
                        else:
                            print("Could not identify process using this port.")
                    else:
                        cmd = f"netstat -ano | findstr :{port} | findstr LISTENING"
                        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        if result.stdout.strip():
                            print("\nProcesses using this port:")
                            print(result.stdout)
                        else:
                            print("Could not identify process using this port.")
                except Exception as e:
                    print(f"Error checking port: {e}")
                
                # Check if this port is in our conflict database
                if port in PORT_CONFLICT_INFO:
                    info = PORT_CONFLICT_INFO[port]
                    print(f"\nPort {port} is commonly used by: {', '.join(info['common_services'])}")
                    print("\nPossible solutions:")
                    for i, solution in enumerate(info['solutions'], 1):
                        print(f"  {i}. {solution}")
        else:
            # Check all common ports
            conflicts = check_port_conflicts()
            
            print("Common service ports status:")
            print("---------------------------")
            
            for port in sorted(PORT_CONFLICT_INFO.keys()):
                status = "IN USE" if port in conflicts else "AVAILABLE"
                process = conflicts.get(port, {}).get("process", "")
                process_info = f" - {process}" if process else ""
                print(f"Port {port}: {status}{process_info}")
                
                if port in conflicts:
                    info = PORT_CONFLICT_INFO[port]
                    print(f"  Commonly used by: {', '.join(info['common_services'])}")
                    print("  Possible solutions:")
                    for i, solution in enumerate(info['solutions'], 1):
                        print(f"    {i}. {solution}")
                    print("")
            
            print("\nTo get detailed information about a specific port:")
            print(f"  {sys.argv[0]} ports --check <port_number>")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()