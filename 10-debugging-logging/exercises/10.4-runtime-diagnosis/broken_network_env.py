"""
broken_network_env.py - Runtime Diagnosis: Network & External API Failures

Simulates network/service failures (DNS resolution errors, connection timeouts,
and service unreachability) and provides diagnostic routines to differentiate
network infrastructure outages from bad application code.
"""

import socket
import urllib.error
import urllib.request
from typing import Dict, Any


class NetworkServiceError(Exception):
    """Raised when external network requests fail."""
    def __init__(self, message: str, error_type: str):
        super().__init__(message)
        self.error_type = error_type


def fetch_remote_service_data(host: str, port: int, timeout_sec: float = 1.0) -> str:
    """
    Attempts to connect to a remote TCP endpoint.
    Raises NetworkServiceError with explicit classification if unreachable.
    """
    # 1. Test DNS Name Resolution
    try:
        ip_addr = socket.gethostbyname(host)
    except socket.gaierror as e:
        raise NetworkServiceError(
            f"DNS resolution failed for host '{host}': {e}",
            error_type="DNS_FAILURE"
        )

    # 2. Test TCP Connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_sec)
    try:
        sock.connect((ip_addr, port))
        return f"Connected to {host} ({ip_addr}:{port})"
    except socket.timeout:
        raise NetworkServiceError(
            f"Connection timed out reaching {host}:{port} after {timeout_sec}s",
            error_type="TIMEOUT_FAILURE"
        )
    except ConnectionRefusedError as e:
        raise NetworkServiceError(
            f"Connection refused by {host}:{port} (service not listening): {e}",
            error_type="CONNECTION_REFUSED"
        )
    except OSError as e:
        raise NetworkServiceError(
            f"Network unreachable or socket error connecting to {host}:{port}: {e}",
            error_type="SOCKET_ERROR"
        )
    finally:
        sock.close()


def diagnose_network_target(host: str, port: int) -> Dict[str, Any]:
    """
    Diagnoses root cause: Differentiates DNS, Firewall/Routing, and Service Down.
    """
    # Check 1: DNS Lookup
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        return {
            "category": "INFRASTRUCTURE_DNS",
            "symptom": f"Cannot resolve hostname '{host}'",
            "root_cause": "DNS records missing, incorrect nameserver, or internal domain typo.",
            "remediation": "Verify corporate VPN, /etc/hosts, or private DNS resolution."
        }

    # Check 2: Ping/Port Reachability
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((ip, port))
        s.close()
        return {
            "category": "HEALTHY",
            "symptom": f"Successfully connected to {host} ({ip}:{port})",
            "root_cause": "None",
            "remediation": "Endpoint is healthy and responsive."
        }
    except socket.timeout:
        return {
            "category": "INFRASTRUCTURE_NETWORK",
            "symptom": f"Timeout connecting to {ip}:{port}",
            "root_cause": "Firewall dropping packets, security group closed, or network routing partition.",
            "remediation": "Check firewall rules, VPC routing tables, and security groups."
        }
    except ConnectionRefusedError:
        return {
            "category": "INFRASTRUCTURE_SERVICE",
            "symptom": f"Connection refused at {ip}:{port}",
            "root_cause": "Host is online but server process is not running or listening on that port.",
            "remediation": "Restart application service / container on the target host."
        }
    except Exception as e:
        return {
            "category": "GENERAL_NETWORK_ERROR",
            "symptom": str(e),
            "root_cause": "Unknown socket error.",
            "remediation": "Check network interface status."
        }


if __name__ == "__main__":
    print("Testing unreachable DNS:")
    try:
        fetch_remote_service_data("invalid-unresolvable-service-host-xyz.local", 8080)
    except NetworkServiceError as err:
        print("Caught expected network error:", err)
        print("Diagnosis:", diagnose_network_target("invalid-unresolvable-service-host-xyz.local", 8080))
