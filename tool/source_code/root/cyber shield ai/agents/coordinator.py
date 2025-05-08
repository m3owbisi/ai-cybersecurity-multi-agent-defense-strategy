import logging
import time
from typing import Dict, Any, List, Optional
from agents.base import Agent

logger = logging.getLogger(__name__)

class CoordinatorAgent(Agent):
    """
    Coordinator Agent responsible for orchestrating the multi-agent system,
    managing interactions between agents, and ensuring coherent operation.
    """
    
    def __init__(self, name: str = "Coordinator Agent", description: str = "Coordinates agent activities and workflows"):
        capabilities = [
            "agent_management",
            "workflow_orchestration",
            "conflict_resolution",
            "scenario_management",
            "resource_allocation"
        ]
        super().__init__(name, description, capabilities)
        
        # Registered agents
        self.agents: Dict[str, Agent] = {}
        
        # Current scenario/context
        self.current_scenario: Optional[Dict[str, Any]] = None
        
        # Operation history
        self.operation_history: List[Dict[str, Any]] = []
        
        # Workflow definitions
        self.workflows: Dict[str, List[Dict[str, Any]]] = {
            "threat_detection": [
                {"agent": "detection", "operation": "analyze_traffic", "params": {}},
                {"agent": "defense", "operation": "process", "params": {"event_type": "attack_detected"}}
            ],
            "vulnerability_assessment": [
                {"agent": "offense", "operation": "vulnerability_assessment", "params": {}},
                {"agent": "defense", "operation": "process", "params": {"event_type": "vulnerability_scan"}}
            ],
            "attack_simulation": [
                {"agent": "offense", "operation": "attack_simulation", "params": {}},
                {"agent": "detection", "operation": "detect_simulation", "params": {}},
                {"agent": "defense", "operation": "process", "params": {"event_type": "attack_detected"}}
            ],
            "training_session": [
                {"agent": "offense", "operation": "attack_simulation", "params": {}},
                {"agent": "detection", "operation": "detect_simulation", "params": {}},
                {"agent": "defense", "operation": "process", "params": {"event_type": "attack_detected"}},
                {"agent": "coordinator", "operation": "evaluate_training", "params": {}}
            ]
        }
        
        # Initialize state
        self.state = {
            "active_workflow": None,
            "workflow_status": {},
            "agent_statuses": {},
            "system_readiness": 0.0,
            "last_operation_time": None
        }
        
        logger.debug(f"CoordinatorAgent {name} initialized")
    
    def register_agent(self, agent_id: str, agent: Agent) -> None:
        """
        Register an agent with the coordinator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: The agent instance to register
        """
        self.agents[agent_id] = agent
        self.state["agent_statuses"][agent_id] = {
            "active": agent.active,
            "capabilities": agent.capabilities
        }
        logger.info(f"Agent '{agent_id}' registered with coordinator")
        
        # Update system readiness
        self._update_system_readiness()
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process coordinator operations.
        
        Args:
            data: Dictionary containing operation details
            
        Returns:
            Dictionary with operation results
        """
        if not self.active:
            return {"error": "Coordinator agent is not active"}
        
        operation = data.get("operation", "")
        
        # Update last operation time
        self.state["last_operation_time"] = time.time()
        
        # Process based on operation type
        if operation == "start_workflow":
            return self._start_workflow(data.get("workflow", ""), data.get("params", {}))
        elif operation == "check_status":
            return self._check_status(data.get("agent_id", None))
        elif operation == "set_scenario":
            return self._set_scenario(data.get("scenario", {}))
        elif operation == "evaluate_training":
            return self._evaluate_training(data.get("training_data", {}))
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _start_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a predefined workflow.
        
        Args:
            workflow_name: Name of the workflow to start
            params: Parameters for the workflow
            
        Returns:
            Dictionary with workflow start results
        """
        if workflow_name not in self.workflows:
            return {"error": f"Unknown workflow: {workflow_name}"}
        
        # Check if all required agents are registered
        workflow_steps = self.workflows[workflow_name]
        required_agents = set(step["agent"] for step in workflow_steps)
        missing_agents = required_agents - set(self.agents.keys())
        
        if missing_agents:
            return {
                "error": f"Missing required agents: {', '.join(missing_agents)}",
                "status": "failed",
                "workflow": workflow_name
            }
        
        # Set active workflow
        self.state["active_workflow"] = workflow_name
        self.state["workflow_status"] = {
            "name": workflow_name,
            "start_time": time.time(),
            "steps_completed": 0,
            "total_steps": len(workflow_steps),
            "current_step": 0,
            "status": "in_progress",
            "results": {}
        }
        
        # Log workflow start
        operation_record = {
            "type": "workflow_start",
            "workflow": workflow_name,
            "timestamp": time.time(),
            "params": params
        }
        self.operation_history.append(operation_record)
        
        logger.info(f"Started workflow: {workflow_name}")
        
        # Execute first step immediately
        workflow_results = self._execute_workflow(workflow_name, params)
        
        return {
            "status": "success",
            "workflow": workflow_name,
            "steps_completed": self.state["workflow_status"]["steps_completed"],
            "total_steps": self.state["workflow_status"]["total_steps"],
            "results": workflow_results
        }
    
    def _execute_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow step by step.
        
        Args:
            workflow_name: Name of the workflow to execute
            params: Parameters for the workflow
            
        Returns:
            Dictionary with workflow execution results
        """
        workflow_steps = self.workflows[workflow_name]
        workflow_results = {}
        
        current_step = self.state["workflow_status"]["current_step"]
        steps_completed = 0
        
        while current_step < len(workflow_steps):
            step = workflow_steps[current_step]
            agent_id = step["agent"]
            operation = step["operation"]
            
            # Combine step params with workflow params
            step_params = {**step["params"], **params}
            
            # Execute step
            try:
                if agent_id == "coordinator":
                    # Self-referential operation
                    step_results = self.process({"operation": operation, **step_params})
                else:
                    agent = self.agents.get(agent_id)
                    if agent:
                        step_params["operation"] = operation
                        step_results = agent.process(step_params)
                    else:
                        step_results = {"error": f"Agent {agent_id} not found"}
                
                workflow_results[f"step_{current_step}"] = {
                    "agent": agent_id,
                    "operation": operation,
                    "status": "error" if "error" in step_results else "success",
                    "results": step_results
                }
                
                # Update step counter
                current_step += 1
                steps_completed += 1
                
                logger.debug(f"Workflow {workflow_name}: Completed step {current_step} using agent {agent_id}")
                
            except Exception as e:
                error_msg = f"Error executing workflow step: {str(e)}"
                logger.error(error_msg)
                workflow_results[f"step_{current_step}"] = {
                    "agent": agent_id,
                    "operation": operation,
                    "status": "error",
                    "error": error_msg
                }
                break
        
        # Update workflow status
        self.state["workflow_status"].update({
            "steps_completed": steps_completed,
            "current_step": current_step,
            "status": "completed" if current_step >= len(workflow_steps) else "in_progress",
            "end_time": time.time() if current_step >= len(workflow_steps) else None,
            "results": workflow_results
        })
        
        # Log workflow completion if finished
        if current_step >= len(workflow_steps):
            operation_record = {
                "type": "workflow_complete",
                "workflow": workflow_name,
                "timestamp": time.time(),
                "results_summary": {k: v["status"] for k, v in workflow_results.items()}
            }
            self.operation_history.append(operation_record)
            
            logger.info(f"Completed workflow: {workflow_name}")
        
        return workflow_results
    
    def _check_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check status of agents or a specific agent.
        
        Args:
            agent_id: Optional ID of the agent to check
            
        Returns:
            Dictionary with status information
        """
        if agent_id:
            if agent_id not in self.agents:
                return {"error": f"Agent {agent_id} not found"}
            
            agent = self.agents[agent_id]
            agent_status = agent.get_status()
            
            self.state["agent_statuses"][agent_id] = {
                "active": agent.active,
                "capabilities": agent.capabilities
            }
            
            return {
                "agent_id": agent_id,
                "status": agent_status
            }
        else:
            # Update all agent statuses
            for aid, agent in self.agents.items():
                self.state["agent_statuses"][aid] = {
                    "active": agent.active,
                    "capabilities": agent.capabilities
                }
            
            active_workflow = self.state.get("active_workflow")
            workflow_status = self.state.get("workflow_status", {})
            
            return {
                "system_status": {
                    "active_agents": sum(1 for a in self.agents.values() if a.active),
                    "total_agents": len(self.agents),
                    "system_readiness": self.state["system_readiness"],
                    "active_workflow": active_workflow,
                    "workflow_progress": (
                        f"{workflow_status.get('steps_completed', 0)}/{workflow_status.get('total_steps', 0)}"
                        if active_workflow else "N/A"
                    )
                },
                "agent_statuses": {aid: {"active": a.active, "capabilities": a.capabilities} 
                                  for aid, a in self.agents.items()}
            }
    
    def _set_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the current operational scenario.
        
        Args:
            scenario: Dictionary containing scenario details
            
        Returns:
            Dictionary with scenario set results
        """
        self.current_scenario = scenario
        
        # Reset agent states to prepare for new scenario
        for agent in self.agents.values():
            agent.reset()
        
        scenario_type = scenario.get("type", "unknown")
        logger.info(f"Set new scenario: {scenario_type}")
        
        # Log scenario change
        operation_record = {
            "type": "scenario_change",
            "scenario": scenario_type,
            "timestamp": time.time()
        }
        self.operation_history.append(operation_record)
        
        return {
            "status": "success",
            "scenario": scenario_type,
            "agents_reset": len(self.agents)
        }
    
    def _evaluate_training(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate training session results.
        
        Args:
            training_data: Data about the training session
            
        Returns:
            Dictionary with evaluation results
        """
        # Get workflow results if not provided
        if not training_data and self.state["active_workflow"] == "training_session":
            workflow_results = self.state["workflow_status"].get("results", {})
            
            # Extract relevant data from workflow results
            attack_results = workflow_results.get("step_0", {}).get("results", {})
            defense_results = workflow_results.get("step_2", {}).get("results", {})
            
            training_data = {
                "attack_simulation": attack_results,
                "defense_response": defense_results
            }
        
        # If still no training data, return error
        if not training_data:
            return {"error": "No training data available"}
        
        # Extract metrics
        attack_metrics = training_data.get("attack_simulation", {}).get("metrics", {})
        attack_path = training_data.get("attack_simulation", {}).get("attack_path", [])
        defense_recommendations = training_data.get("defense_response", {}).get("recommendations", [])
        
        # Calculate detection rate
        detected_steps = sum(1 for step in attack_path if step.get("detected", False))
        total_steps = len(attack_path)
        detection_rate = detected_steps / total_steps if total_steps > 0 else 0
        
        # Calculate response effectiveness
        critical_findings = training_data.get("attack_simulation", {}).get("critical_findings", [])
        addressed_findings = 0
        
        for finding in critical_findings:
            finding_type = finding.get("type", "")
            # Check if defense recommendations address this finding
            for rec in defense_recommendations:
                if self._recommendation_addresses_finding(rec, finding):
                    addressed_findings += 1
                    break
        
        response_effectiveness = addressed_findings / len(critical_findings) if critical_findings else 1.0
        
        # Calculate overall score
        attack_success = attack_metrics.get("overall_success_probability", 0.5)
        # A lower attack success rate is better for defense
        defense_score = (1 - attack_success) * 0.4 + detection_rate * 0.3 + response_effectiveness * 0.3
        defense_score = min(1.0, max(0.0, defense_score))  # Clamp between 0 and 1
        
        # Generate evaluation
        evaluation = {
            "metrics": {
                "detection_rate": detection_rate,
                "response_effectiveness": response_effectiveness,
                "defense_score": defense_score,
                "attack_steps_detected": f"{detected_steps}/{total_steps}"
            },
            "strengths": self._identify_strengths(training_data, defense_score, detection_rate, response_effectiveness),
            "weaknesses": self._identify_weaknesses(training_data, defense_score, detection_rate, response_effectiveness),
            "improvement_areas": self._identify_improvement_areas(training_data)
        }
        
        # Log training evaluation
        operation_record = {
            "type": "training_evaluation",
            "score": defense_score,
            "timestamp": time.time()
        }
        self.operation_history.append(operation_record)
        
        logger.info(f"Training evaluation completed. Score: {defense_score:.2f}")
        
        return evaluation
    
    def _recommendation_addresses_finding(self, recommendation: Dict[str, Any], finding: Dict[str, Any]) -> bool:
        """
        Check if a recommendation addresses a critical finding.
        
        Args:
            recommendation: The defense recommendation
            finding: The critical finding
            
        Returns:
            Boolean indicating if the recommendation addresses the finding
        """
        finding_type = finding.get("type", "")
        
        # Different ways a recommendation might address a finding
        if finding_type == "detection_gap" and "monitoring" in str(recommendation).lower():
            return True
        elif finding_type == "privilege_escalation" and "access control" in str(recommendation).lower():
            return True
        elif finding_type == "missing_defenses" and finding.get("description", "") in str(recommendation):
            return True
        elif finding_type == "data_leak" and "data" in str(recommendation).lower() and "prevention" in str(recommendation).lower():
            return True
            
        return False
    
    def _identify_strengths(self, training_data: Dict[str, Any], defense_score: float, 
                           detection_rate: float, response_effectiveness: float) -> List[str]:
        """Identify strengths based on training results."""
        strengths = []
        
        if detection_rate > 0.7:
            strengths.append("Strong threat detection capabilities")
        
        if response_effectiveness > 0.8:
            strengths.append("Effective incident response measures")
        
        if defense_score > 0.75:
            strengths.append("Well-rounded cybersecurity posture")
        
        # Look for specific defensive strengths
        defense_response = training_data.get("defense_response", {})
        defense_status = defense_response.get("current_defense_status", {})
        
        implemented_measures = defense_status.get("implemented_measures", [])
        
        if "patch_management" in implemented_measures:
            strengths.append("Strong vulnerability management through patching")
        
        if "data_encryption" in implemented_measures:
            strengths.append("Good data protection measures")
        
        if "ids_configuration" in implemented_measures and detection_rate > 0.6:
            strengths.append("Well-configured intrusion detection system")
        
        return strengths
    
    def _identify_weaknesses(self, training_data: Dict[str, Any], defense_score: float, 
                            detection_rate: float, response_effectiveness: float) -> List[str]:
        """Identify weaknesses based on training results."""
        weaknesses = []
        
        if detection_rate < 0.4:
            weaknesses.append("Poor threat detection capabilities")
        
        if response_effectiveness < 0.5:
            weaknesses.append("Ineffective incident response")
        
        # Look for specific attack successes
        attack_simulation = training_data.get("attack_simulation", {})
        attack_path = attack_simulation.get("attack_path", [])
        
        # Check for successful critical steps
        for step in attack_path:
            if not step.get("detected", False) and step.get("phase") in ["impact", "exfiltration"]:
                weaknesses.append(f"Critical {step.get('phase')} phase went undetected")
        
        # Check for defense gaps
        defense_response = training_data.get("defense_response", {})
        defense_status = defense_response.get("current_defense_status", {})
        
        missing_measures = defense_status.get("missing_measures", [])
        
        critical_missing = [m for m in missing_measures if m in ["patch_management", "access_control", "endpoint_protection"]]
        if critical_missing:
            weaknesses.append(f"Missing critical defense measures: {', '.join(critical_missing)}")
        
        return weaknesses
    
    def _identify_improvement_areas(self, training_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement based on training results."""
        improvements = []
        
        # Look for specific recommendations from defense agent
        defense_response = training_data.get("defense_response", {})
        recommendations = defense_response.get("recommendations", [])
        
        # Select high priority recommendations
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        for rec in high_priority_recs[:3]:  # Take top 3 high priority
            measure = rec.get("measure", "")
            if measure:
                improvements.append(f"Implement {measure.replace('_', ' ')}")
        
        # Check for specific attack types that were successful
        attack_simulation = training_data.get("attack_simulation", {})
        attack_type = attack_simulation.get("attack_type", "")
        outcome = attack_simulation.get("outcome", "")
        
        if outcome == "successful":
            improvements.append(f"Improve defenses against {attack_type.replace('_', ' ')} attacks")
        
        # Add general improvements based on metrics
        attack_metrics = attack_simulation.get("metrics", {})
        evasion_rate = attack_metrics.get("evasion_success_rate", 0)
        
        if evasion_rate > 0.7:
            improvements.append("Enhance security monitoring to detect evasion techniques")
        
        return improvements
    
    def _update_system_readiness(self) -> None:
        """Update the system readiness score based on agent statuses."""
        if not self.agents:
            self.state["system_readiness"] = 0.0
            return
        
        # Calculate based on registered and active agents
        essential_agents = {"detection", "defense", "offense"}
        registered_essential = sum(1 for a in essential_agents if a in self.agents)
        active_essential = sum(1 for a in essential_agents if a in self.agents and self.agents[a].active)
        
        # Weigh essential agents more heavily
        essential_weight = 0.7
        general_weight = 0.3
        
        essential_score = active_essential / max(1, len(essential_agents)) * essential_weight
        
        # All other agents
        registered_others = sum(1 for a in self.agents if a not in essential_agents)
        active_others = sum(1 for a in self.agents if a not in essential_agents and self.agents[a].active)
        
        general_score = (active_others / max(1, registered_others)) * general_weight if registered_others else 0
        
        # Combine scores
        self.state["system_readiness"] = essential_score + general_score
