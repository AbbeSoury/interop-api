# src/gateway/__init__.py
"""
Core gateway package
"""

from .core import HealthcareGateway
from .config import GatewayConfig

__all__ = ['HealthcareGateway', 'GatewayConfig']
