"""Phase 11: Docker image builder and deployment."""

import logging
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DockerConfig:
    """Docker build configuration."""
    dockerfile_path: str
    image_name: str
    image_tag: str
    registry: str | None = None

    @property
    def full_image_name(self) -> str:
        """Return full image name with registry."""
        base = f"{self.image_name}:{self.image_tag}"
        return f"{self.registry}/{base}" if self.registry else base


class DockerBuilder:
    """Build and push Docker images."""

    def __init__(self, config: DockerConfig):
        self.config = config

    def build(self, context_path: str) -> bool:
        """Build Docker image."""
        cmd = [
            "docker",
            "build",
            "-t", self.config.full_image_name,
            "-f", self.config.dockerfile_path,
            context_path,
        ]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"✅ Built image: {self.config.full_image_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker build failed: {e.stderr}")
            return False

    def push(self) -> bool:
        """Push image to registry."""
        if not self.config.registry:
            logger.warning("No registry configured; skipping push.")
            return False

        cmd = ["docker", "push", self.config.full_image_name]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"✅ Pushed image: {self.config.full_image_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker push failed: {e.stderr}")
            return False
