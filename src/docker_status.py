"""
Docker Status Monitoring Module

This module provides functionality to monitor Docker container status and health.
It uses subprocess to execute Docker CLI commands and parse their output.
"""

import subprocess
import json
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime


@dataclass
class ContainerStatus:
    """Docker container status information"""
    name: str
    status: str  # running, stopped, building, error
    image: str
    created: datetime
    ports: Dict[str, str]
    health: Optional[str] = None  # healthy, unhealthy, starting


@dataclass
class ImageInfo:
    """Docker image information"""
    id: str
    tags: List[str]
    created: datetime
    size: int  # bytes


class DockerMonitor:
    """Monitor Docker container status and health"""
    
    def __init__(self):
        """Initialize Docker monitor"""
        self._docker_available = None
    
    def is_docker_available(self) -> bool:
        """
        Check if Docker daemon is accessible
        
        Returns:
            bool: True if Docker is available, False otherwise
        """
        if self._docker_available is not None:
            return self._docker_available
        
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self._docker_available = result.returncode == 0
            return self._docker_available
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            self._docker_available = False
            return False
    
    def get_container_status(self, container_name: str = "ecu-log-visualizer") -> Optional[ContainerStatus]:
        """
        Get status of application container
        
        Args:
            container_name: Name of the container to check
            
        Returns:
            ContainerStatus object if container exists, None otherwise
        """
        if not self.is_docker_available():
            return None
        
        try:
            # Get container information using docker inspect
            result = subprocess.run(
                ['docker', 'inspect', container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Container doesn't exist
                return None
            
            # Parse JSON output
            containers = json.loads(result.stdout)
            if not containers:
                return None
            
            container = containers[0]
            state = container.get('State', {})
            config = container.get('Config', {})
            network_settings = container.get('NetworkSettings', {})
            
            # Determine status
            if state.get('Running'):
                status = 'running'
            elif state.get('Paused'):
                status = 'paused'
            elif state.get('Restarting'):
                status = 'restarting'
            else:
                status = 'stopped'
            
            # Parse ports
            ports = {}
            port_bindings = network_settings.get('Ports', {})
            for container_port, host_bindings in port_bindings.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_port = binding.get('HostPort', '')
                        if host_port:
                            ports[container_port] = host_port
            
            # Get health status if available
            health = None
            health_info = state.get('Health')
            if health_info:
                health = health_info.get('Status', 'unknown')
            
            # Parse created timestamp
            created_str = container.get('Created', '')
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                created = datetime.now()
            
            return ContainerStatus(
                name=container.get('Name', '').lstrip('/'),
                status=status,
                image=config.get('Image', 'unknown'),
                created=created,
                ports=ports,
                health=health
            )
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            # Return error status
            return ContainerStatus(
                name=container_name,
                status='error',
                image='unknown',
                created=datetime.now(),
                ports={},
                health=None
            )
    
    def get_image_info(self, image_name: str = "ecu-log-visualizer") -> Optional[ImageInfo]:
        """
        Get Docker image information
        
        Args:
            image_name: Name of the image to check
            
        Returns:
            ImageInfo object if image exists, None otherwise
        """
        if not self.is_docker_available():
            return None
        
        try:
            # Get image information using docker inspect
            result = subprocess.run(
                ['docker', 'inspect', image_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Image doesn't exist
                return None
            
            # Parse JSON output
            images = json.loads(result.stdout)
            if not images:
                return None
            
            image = images[0]
            
            # Parse created timestamp
            created_str = image.get('Created', '')
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                created = datetime.now()
            
            # Get tags
            tags = image.get('RepoTags', [])
            if not tags:
                tags = ['<none>']
            
            # Get size
            size = image.get('Size', 0)
            
            return ImageInfo(
                id=image.get('Id', 'unknown'),
                tags=tags,
                created=created,
                size=size
            )
            
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
            return None
