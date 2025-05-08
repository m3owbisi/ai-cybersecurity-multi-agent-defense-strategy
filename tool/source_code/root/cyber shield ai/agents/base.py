import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Agent(ABC):
    """Base class for all cybersecurity agents in the system."""
    
    def __init__(self, name: str, description: str, capabilities: List[str]):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            description: A brief description of the agent's purpose
            capabilities: A list of the agent's capabilities
        """
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.active = False
        self.state: Dict[str, Any] = {}
        logger.debug(f"Agent {name} initialized with capabilities: {capabilities}")
    
    def activate(self) -> None:
        """Activate the agent."""
        self.active = True
        logger.info(f"Agent {self.name} activated")
    
    def deactivate(self) -> None:
        """Deactivate the agent."""
        self.active = False
        logger.info(f"Agent {self.name} deactivated")
    
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming data and return a result.
        
        Args:
            data: A dictionary of input data for the agent to process
            
        Returns:
            A dictionary containing the processing results
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Return the current status of the agent."""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "active": self.active,
            "state": self.state
        }
    
    def reset(self) -> None:
        """Reset the agent's state."""
        self.state = {}
        logger.debug(f"Agent {self.name} state reset")
    
    def update_state(self, key: str, value: Any) -> None:
        """
        Update a specific key in the agent's state.
        
        Args:
            key: The state key to update
            value: The new value
        """
        self.state[key] = value
