#!/usr/bin/env python3
"""
Simple script to verify Grafana datasource setup.
"""
import requests
import json
import sys

def check_prometheus():
    """Check if Prometheus is accessible."""
    try:
        response = requests.get("http://localhost:9090/api/v1/query?query=up")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prometheus is running. Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Prometheus returned error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Prometheus: {e}")
        return False

def check_pushgateway():
    """Check if Pushgateway is accessible."""
    try:
        response = requests.get("http://localhost:9091/metrics")
        if response.status_code == 200:
            print(f"✅ Pushgateway is running. Returned {len(response.text.splitlines())} metrics.")
            return True
        else:
            print(f"❌ Pushgateway returned error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Pushgateway: {e}")
        return False

def check_grafana():
    """Check if Grafana is accessible."""
    try:
        # Use basic auth with default credentials
        auth = ("admin", "agent_provocateur")
        response = requests.get("http://localhost:3000/api/health", auth=auth)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Grafana is running. Health status: {json.dumps(data, indent=2)}")
            
            # Check datasources
            ds_response = requests.get("http://localhost:3000/api/datasources", auth=auth)
            if ds_response.status_code == 200:
                datasources = ds_response.json()
                print(f"✅ Found {len(datasources)} datasources in Grafana:")
                for ds in datasources:
                    print(f"  - {ds.get('name')} ({ds.get('type')}): {ds.get('url')}")
                
                # Check if Prometheus datasource exists
                has_prometheus = any(ds.get('name') == 'Prometheus' for ds in datasources)
                if has_prometheus:
                    print("✅ Prometheus datasource is configured in Grafana")
                else:
                    print("❌ Prometheus datasource is NOT configured in Grafana")
                
                return has_prometheus
            else:
                print(f"❌ Error getting Grafana datasources: {ds_response.status_code} - {ds_response.text}")
                return False
        else:
            print(f"❌ Grafana returned error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Grafana: {e}")
        return False

def main():
    """Main function."""
    print("Testing Agent Provocateur monitoring stack...")
    print("\n1. Checking Prometheus...")
    prometheus_ok = check_prometheus()
    
    print("\n2. Checking Pushgateway...")
    pushgateway_ok = check_pushgateway()
    
    print("\n3. Checking Grafana...")
    grafana_ok = check_grafana()
    
    # Summary
    print("\nMonitoring Stack Status:")
    print(f"- Prometheus: {'✅ OK' if prometheus_ok else '❌ FAILED'}")
    print(f"- Pushgateway: {'✅ OK' if pushgateway_ok else '❌ FAILED'}")
    print(f"- Grafana: {'✅ OK' if grafana_ok else '❌ FAILED'}")
    
    if prometheus_ok and pushgateway_ok and grafana_ok:
        print("\n✅ All monitoring services are running properly!")
        print("\nYou can now:")
        print("1. Access Grafana at http://localhost:3000 (login: admin/agent_provocateur)")
        print("2. View metrics in Prometheus at http://localhost:9090")
        print("3. Check the Pushgateway at http://localhost:9091")
        return 0
    else:
        print("\n❌ Some monitoring services are not working properly. See details above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())