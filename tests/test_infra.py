"""Phase 11: Unit tests — Infrastructure (Docker, CDK, health checks, monitoring).

Trust, but Verify: test_infra.py
"""

import pytest
from src.infra import DockerBuilder, HealthChecker, MetricsCollector, SupportAgentStack
from src.infra.docker_builder import DockerConfig


class TestDockerBuilder:
    def test_docker_config_full_image_name_without_registry(self):
        config = DockerConfig(
            dockerfile_path="Dockerfile",
            image_name="supportagent",
            image_tag="v1.0",
        )
        assert config.full_image_name == "supportagent:v1.0"

    def test_docker_config_full_image_name_with_registry(self):
        config = DockerConfig(
            dockerfile_path="Dockerfile",
            image_name="supportagent",
            image_tag="v1.0",
            registry="docker.io",
        )
        assert config.full_image_name == "docker.io/supportagent:v1.0"


class TestSupportAgentStack:
    def test_stack_initialization(self):
        stack = SupportAgentStack("test-stack", {"ENV": "dev"})
        assert stack.stack_name == "test-stack"
        assert stack.env_vars == {"ENV": "dev"}

    def test_ecs_task_definition(self):
        stack = SupportAgentStack("test-stack")
        task_def = stack.get_ecs_task_definition()
        assert task_def["family"] == "test-stack"
        assert task_def["requiresCompatibilities"] == ["FARGATE"]


class TestHealthChecker:
    def test_health_checker_init(self):
        checker = HealthChecker("http://localhost:8000")
        assert checker.service_url == "http://localhost:8000"


class TestMetricsCollector:
    def test_increment_counter(self):
        collector = MetricsCollector()
        collector.increment_counter("requests_total", 5)
        assert collector.counters["requests_total"] == 5

    def test_set_gauge(self):
        collector = MetricsCollector()
        collector.set_gauge("cpu_usage", 42.5)
        assert collector.gauges["cpu_usage"] == 42.5

    def test_record_histogram(self):
        collector = MetricsCollector()
        collector.record_histogram("response_time", 100)
        collector.record_histogram("response_time", 150)
        assert len(collector.histograms["response_time"]) == 2

    def test_export_prometheus(self):
        collector = MetricsCollector()
        collector.increment_counter("requests_total", 10)
        collector.set_gauge("cpu_usage", 50.0)
        export = collector.export_prometheus()
        assert "requests_total_total 10" in export
        assert "cpu_usage 50" in export

    def test_get_p95(self):
        collector = MetricsCollector()
        for i in range(100):
            collector.record_histogram("latency", float(i))
        p95 = collector.get_p95("latency")
        assert p95 is not None
        assert 94 <= p95 <= 95


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
