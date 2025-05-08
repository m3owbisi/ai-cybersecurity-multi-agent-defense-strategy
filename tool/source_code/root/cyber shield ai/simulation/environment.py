import logging
import time
import random
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from agents.coordinator import CoordinatorAgent
from agents.defense import DefenseAgent
from agents.offense import OffenseAgent
from agents.detection import DetectionAgent
from simulation.network import NetworkSimulator

logger = logging.getLogger(__name__)

class SimulationEnvironment:
    """
    Simulation environment for running cybersecurity scenarios 
    with coordinated AI agents.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the simulation environment.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        
        # Initialize agents
        self.coordinator = CoordinatorAgent()
        self.defense_agent = DefenseAgent()
        self.offense_agent = OffenseAgent()
        self.detection_agent = DetectionAgent()
        
        # Register agents with coordinator
        self.coordinator.register_agent("coordinator", self.coordinator)
        self.coordinator.register_agent("defense", self.defense_agent)
        self.coordinator.register_agent("offense", self.offense_agent)
        self.coordinator.register_agent("detection", self.detection_agent)
        
        # Network simulator for generating traffic and events
        self.network = NetworkSimulator()
        
        # Current simulation state
        self.current_scenario = None
        self.simulation_running = False
        self.simulation_start_time = None
        self.simulation_results = {}
        self.step_count = 0
        
        # Activate all agents
        self.coordinator.activate()
        self.defense_agent.activate()
        self.offense_agent.activate()
        self.detection_agent.activate()
        
        logger.info("Simulation environment initialized")
    
    def load_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load a simulation scenario.
        
        Args:
            scenario: Dictionary containing scenario details
            
        Returns:
            Dictionary with scenario loading results
        """
        self.current_scenario = scenario
        
        # Reset simulation state
        self.simulation_running = False
        self.simulation_results = {}
        self.step_count = 0
        
        # Reset network simulator with scenario parameters
        self.network.reset(scenario.get("network_params", {}))
        
        # Set scenario in coordinator
        scenario_result = self.coordinator.process({
            "operation": "set_scenario",
            "scenario": scenario
        })
        
        logger.info(f"Loaded scenario: {scenario.get('name', 'Unnamed')}")
        
        return {
            "status": "success",
            "scenario": scenario.get("name", "Unnamed"),
            "coordinator_result": scenario_result
        }
    
    def start_simulation(self, 
                        duration_seconds: Optional[int] = None,
                        step_delay: float = 0.5) -> Dict[str, Any]:
        """
        Start the simulation.
        
        Args:
            duration_seconds: Optional maximum duration in seconds
            step_delay: Delay between simulation steps in seconds
            
        Returns:
            Dictionary with simulation start results
        """
        if not self.current_scenario:
            return {"error": "No scenario loaded"}
        
        self.simulation_running = True
        self.simulation_start_time = time.time()
        self.step_count = 0
        
        logger.info(f"Starting simulation: {self.current_scenario.get('name', 'Unnamed')}")
        
        # Initialize simulation results
        self.simulation_results = {
            "scenario": self.current_scenario.get("name", "Unnamed"),
            "start_time": self.simulation_start_time,
            "status": "running",
            "steps_completed": 0,
            "events": [],
            "metrics": {}
        }
        
        # Run simulation for specified duration or until stopped
        try:
            max_steps = self.current_scenario.get("max_steps", 100)
            
            while self.simulation_running:
                # Check if duration exceeded
                if duration_seconds and time.time() - self.simulation_start_time > duration_seconds:
                    logger.info(f"Simulation reached maximum duration of {duration_seconds} seconds")
                    break
                
                # Check if max steps reached
                if self.step_count >= max_steps:
                    logger.info(f"Simulation reached maximum steps: {max_steps}")
                    break
                
                # Execute a simulation step
                step_result = self._execute_step()
                
                # Add step events to results
                if "events" in step_result:
                    self.simulation_results["events"].extend(step_result["events"])
                
                # Update step count
                self.step_count += 1
                self.simulation_results["steps_completed"] = self.step_count
                
                # Delay between steps
                if step_delay > 0:
                    time.sleep(step_delay)
            
            # Simulation completed
            self.simulation_running = False
            self.simulation_results["status"] = "completed"
            self.simulation_results["end_time"] = time.time()
            self.simulation_results["duration_seconds"] = time.time() - self.simulation_start_time
            
            # Calculate final metrics
            self._calculate_final_metrics()
            
            logger.info(f"Simulation completed with {self.step_count} steps")
            
            return {
                "status": "success",
                "scenario": self.current_scenario.get("name", "Unnamed"),
                "steps_completed": self.step_count,
                "duration_seconds": self.simulation_results["duration_seconds"]
            }
            
        except Exception as e:
            self.simulation_running = False
            self.simulation_results["status"] = "error"
            self.simulation_results["error"] = str(e)
            
            logger.error(f"Simulation error: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def stop_simulation(self) -> Dict[str, Any]:
        """
        Stop the simulation.
        
        Returns:
            Dictionary with simulation stop results
        """
        if not self.simulation_running:
            return {"error": "No simulation is running"}
        
        self.simulation_running = False
        self.simulation_results["status"] = "stopped"
        self.simulation_results["end_time"] = time.time()
        self.simulation_results["duration_seconds"] = time.time() - self.simulation_start_time
        
        # Calculate final metrics
        self._calculate_final_metrics()
        
        logger.info(f"Simulation stopped after {self.step_count} steps")
        
        return {
            "status": "success",
            "steps_completed": self.step_count,
            "duration_seconds": self.simulation_results["duration_seconds"]
        }
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the simulation results.
        
        Returns:
            Dictionary with simulation results
        """
        return self.simulation_results
    
    def _execute_step(self) -> Dict[str, Any]:
        """
        Execute a single simulation step.
        
        Returns:
            Dictionary with step results
        """
        # Generate network traffic
        traffic_data = self.network.generate_traffic(self.step_count)
        
        # Analyze traffic with detection agent
        detection_result = self.detection_agent.process({
            "operation": "analyze_traffic",
            "traffic_data": traffic_data
        })
        
        # Process detected threats with defense agent
        defense_result = None
        if detection_result.get("detected_threats", []):
            defense_result = self.defense_agent.process({
                "event_type": "attack_detected",
                "threats": detection_result["detected_threats"],
                "threat_level": detection_result["threat_level"]
            })
        
        # Execute scenario-specific step logic
        scenario_type = self.current_scenario.get("type", "general")
        
        step_events = []
        
        # Add traffic events
        for traffic in traffic_data:
            step_events.append({
                "type": "network_traffic",
                "timestamp": time.time(),
                "data": traffic
            })
        
        # Add detection events
        if detection_result.get("detected_threats", []):
            for threat in detection_result["detected_threats"]:
                step_events.append({
                    "type": "threat_detected",
                    "timestamp": time.time(),
                    "data": threat
                })
        
        # Add defense events
        if defense_result:
            step_events.append({
                "type": "defense_response",
                "timestamp": time.time(),
                "data": {
                    "recommendations": defense_result.get("recommended_countermeasures", []),
                    "actions_taken": defense_result.get("actions_taken", [])
                }
            })
        
        # Handle specific scenario logic
        if scenario_type == "attack_simulation" and self.step_count == 0:
            # Run a simulated attack at the beginning of attack scenarios
            attack_params = self.current_scenario.get("attack_params", {})
            attack_params["operation"] = "attack_simulation"
            
            attack_result = self.offense_agent.process(attack_params)
            
            step_events.append({
                "type": "attack_simulation",
                "timestamp": time.time(),
                "data": attack_result
            })
        
        logger.debug(f"Executed simulation step {self.step_count} with {len(step_events)} events")
        
        return {
            "step": self.step_count,
            "events": step_events
        }
    
    def _calculate_final_metrics(self) -> None:
        """Calculate final simulation metrics after completion."""
        events = self.simulation_results.get("events", [])
        
        # Count event types
        event_counts = {}
        for event in events:
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Calculate detection effectiveness
        attack_events = [e for e in events if e.get("type") == "attack_simulation"]
        threat_events = [e for e in events if e.get("type") == "threat_detected"]
        
        # Extract attack paths from attack simulation events
        attack_steps = []
        for event in attack_events:
            attack_path = event.get("data", {}).get("attack_path", [])
            attack_steps.extend(attack_path)
        
        # Calculate detection rate
        if attack_steps:
            detected_steps = sum(1 for step in attack_steps if step.get("detected", False))
            detection_rate = detected_steps / len(attack_steps)
        else:
            detection_rate = 0
        
        # Calculate defense effectiveness
        defense_events = [e for e in events if e.get("type") == "defense_response"]
        if threat_events and defense_events:
            # Ratio of defense responses to threats
            defense_coverage = len(defense_events) / len(threat_events)
            
            # Extract defense recommendations
            defense_recommendations = []
            for event in defense_events:
                recs = event.get("data", {}).get("recommendations", [])
                defense_recommendations.extend(recs)
            
            # Unique defense recommendations count
            unique_recommendations = set()
            for rec in defense_recommendations:
                if isinstance(rec, dict) and "action" in rec:
                    unique_recommendations.add(rec["action"])
            
            defense_variety = len(unique_recommendations)
        else:
            defense_coverage = 0
            defense_variety = 0
        
        # Calculate overall metrics
        metrics = {
            "event_counts": event_counts,
            "detection_rate": detection_rate,
            "defense_coverage": defense_coverage,
            "defense_variety": defense_variety,
            "traffic_volume": event_counts.get("network_traffic", 0),
            "threat_count": event_counts.get("threat_detected", 0)
        }
        
        # Add scenario-specific metrics
        scenario_type = self.current_scenario.get("type", "general")
        if scenario_type == "attack_simulation":
            # For attack simulations, include attack success metrics
            for event in attack_events:
                attack_outcome = event.get("data", {}).get("outcome", "unknown")
                attack_metrics = event.get("data", {}).get("metrics", {})
                
                metrics["attack_outcome"] = attack_outcome
                metrics["attack_success_probability"] = attack_metrics.get("overall_success_probability", 0)
                metrics["attack_evasion_rate"] = attack_metrics.get("evasion_success_rate", 0)
                break
        
        self.simulation_results["metrics"] = metrics
