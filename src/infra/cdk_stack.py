"""Phase 11: AWS CDK stack definition for ECS Fargate deployment."""

import logging

logger = logging.getLogger(__name__)


class SupportAgentStack:
    """AWS CDK Stack for SupportAgent on ECS Fargate."""

    def __init__(self, stack_name: str, env_vars: dict = None):
        self.stack_name = stack_name
        self.env_vars = env_vars or {}
        logger.info(f"Initialized CDK stack: {stack_name}")

    def get_ecs_task_definition(self) -> dict:
        """Generate ECS task definition."""
        return {
            "family": self.stack_name,
            "networkMode": "awsvpc",
            "requiresCompatibilities": ["FARGATE"],
            "cpu": "256",
            "memory": "512",
            "containerDefinitions": [
                {
                    "name": self.stack_name,
                    "image": f"supportagent:latest",
                    "portMappings": [{"containerPort": 8000, "hostPort": 8000}],
                    "environment": [{"name": k, "value": v} for k, v in self.env_vars.items()],
                    "logConfiguration": {
                        "logDriver": "awslogs",
                        "options": {
                            "awslogs-group": f"/ecs/{self.stack_name}",
                            "awslogs-region": "us-east-1",
                            "awslogs-stream-prefix": "ecs",
                        },
                    },
                }
            ],
        }

    def get_service_definition(self) -> dict:
        """Generate ECS service definition."""
        return {
            "serviceName": f"{self.stack_name}-service",
            "cluster": self.stack_name,
            "taskDefinition": self.stack_name,
            "desiredCount": 1,
            "launchType": "FARGATE",
            "networkConfiguration": {
                "awsvpcConfiguration": {
                    "subnets": ["subnet-xxxxx"],
                    "securityGroups": ["sg-xxxxx"],
                    "assignPublicIp": "ENABLED",
                }
            },
        }
