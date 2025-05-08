# Agents package initialization
from agents.base import Agent
from agents.defense import DefenseAgent
from agents.offense import OffenseAgent
from agents.coordinator import CoordinatorAgent
from agents.detection import DetectionAgent

__all__ = [
    'Agent',
    'DefenseAgent',
    'OffenseAgent',
    'CoordinatorAgent',
    'DetectionAgent'
]
