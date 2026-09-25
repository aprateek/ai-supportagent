"""Phase 11: Service health checks."""

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """Health check result."""
    healthy: bool
    service: str
    timestamp: datetime
    details: dict


class HealthChecker:
    """Monitor service health."""

    def __init__(self, service_url: str = "http://localhost:8000"):
        self.service_url = service_url

    def check_api_health(self) -> HealthStatus:
        """Check if API is responding."""
        import requests
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            is_healthy = response.status_code == 200
            return HealthStatus(
                healthy=is_healthy,
                service="api",
                timestamp=datetime.utcnow(),
                details={"status_code": response.status_code, "response_time_ms": response.elapsed.total_seconds() * 1000},
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthStatus(
                healthy=False,
                service="api",
                timestamp=datetime.utcnow(),
                details={"error": str(e)},
            )

    def check_bedrock_connectivity(self) -> HealthStatus:
        """Check if Bedrock is accessible."""
        import boto3
        try:
            client = boto3.client("bedrock-runtime")
            # Lightweight call to verify connectivity
            client.list_foundation_models()
            return HealthStatus(
                healthy=True,
                service="bedrock",
                timestamp=datetime.utcnow(),
                details={"region": "us-east-1"},
            )
        except Exception as e:
            logger.error(f"Bedrock connectivity check failed: {e}")
            return HealthStatus(
                healthy=False,
                service="bedrock",
                timestamp=datetime.utcnow(),
                details={"error": str(e)},
            )
