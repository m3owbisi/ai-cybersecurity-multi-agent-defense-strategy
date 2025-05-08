import logging
import random
from typing import Dict, Any, List, Tuple
import numpy as np
from agents.base import Agent

logger = logging.getLogger(__name__)

class DefenseAgent(Agent):
    """
    Defense Agent responsible for recommending and implementing security measures.
    """
    
    def __init__(self, name: str = "Defense Agent", description: str = "Identifies vulnerabilities and implements defenses"):
        capabilities = [
            "vulnerability_scanning",
            "intrusion_prevention",
            "patch_recommendation",
            "firewall_management",
            "security_hardening"
        ]
        super().__init__(name, description, capabilities)
        
        # Defensive measures with effectiveness ratings (0-1)
        self.defensive_measures = {
            "firewall_rules": 0.8,
            "ids_configuration": 0.75,
            "patch_management": 0.9,
            "access_control": 0.85,
            "data_encryption": 0.95,
            "network_segmentation": 0.7,
            "endpoint_protection": 0.8,
            "backup_systems": 0.6
        }
        
        # Initialize state
        self.state = {
            "current_defenses": {},
            "vulnerability_scores": {},
            "defense_effectiveness": 0.0,
            "recent_attacks": [],
            "recommended_actions": []
        }
        
        logger.debug(f"DefenseAgent {name} initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming security data and recommend defensive actions.
        
        Args:
            data: Dictionary containing security event data
            
        Returns:
            Dictionary with recommended defense actions and vulnerability assessment
        """
        if not self.active:
            return {"error": "Defense agent is not active"}
        
        event_type = data.get("event_type", "")
        
        # Process based on event type
        if event_type == "vulnerability_scan":
            return self._process_vulnerability_scan(data)
        elif event_type == "attack_detected":
            return self._process_attack(data)
        elif event_type == "system_update":
            return self._process_system_update(data)
        else:
            return self._generate_defense_recommendations(data)
    
    def _process_vulnerability_scan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process vulnerability scan results and recommend remediation."""
        vulnerabilities = data.get("vulnerabilities", [])
        
        # Score and sort vulnerabilities by severity
        scored_vulnerabilities = []
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "medium")
            severity_score = {"critical": 0.9, "high": 0.7, "medium": 0.5, "low": 0.3}.get(severity, 0.5)
            exploitation_difficulty = vuln.get("exploitation_difficulty", 0.5)
            
            # Calculate risk score based on severity and difficulty
            risk_score = severity_score * (1 - exploitation_difficulty * 0.5)
            scored_vulnerabilities.append((vuln, risk_score))
        
        # Sort by risk score (highest first)
        scored_vulnerabilities.sort(key=lambda x: x[1], reverse=True)
        
        # Generate recommendations
        recommendations = []
        for vuln, score in scored_vulnerabilities:
            recommendation = {
                "vulnerability": vuln.get("name", "Unknown vulnerability"),
                "risk_score": score,
                "recommended_action": self._get_remediation_action(vuln),
                "priority": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
            }
            recommendations.append(recommendation)
        
        # Update state
        self.state["vulnerability_scores"] = {v[0].get("name", f"vuln_{i}"): v[1] 
                                              for i, v in enumerate(scored_vulnerabilities)}
        self.state["recommended_actions"] = recommendations
        
        return {
            "vulnerability_assessment": {
                "total_vulnerabilities": len(vulnerabilities),
                "critical_count": sum(1 for v, _ in scored_vulnerabilities if v.get("severity") == "critical"),
                "high_count": sum(1 for v, _ in scored_vulnerabilities if v.get("severity") == "high"),
                "medium_count": sum(1 for v, _ in scored_vulnerabilities if v.get("severity") == "medium"),
                "low_count": sum(1 for v, _ in scored_vulnerabilities if v.get("severity") == "low"),
                "average_risk_score": np.mean([s for _, s in scored_vulnerabilities]) if scored_vulnerabilities else 0
            },
            "recommendations": recommendations
        }
    
    def _process_attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process attack information and recommend countermeasures."""
        attack_type = data.get("attack_type", "unknown")
        attack_vector = data.get("attack_vector", "unknown")
        affected_systems = data.get("affected_systems", [])
        
        # Log attack
        self.state["recent_attacks"].append({
            "type": attack_type,
            "vector": attack_vector,
            "timestamp": data.get("timestamp", "unknown"),
            "affected_systems": affected_systems
        })
        
        # Limit recent attacks list to 10 entries
        if len(self.state["recent_attacks"]) > 10:
            self.state["recent_attacks"] = self.state["recent_attacks"][-10:]
        
        # Generate countermeasures based on attack type
        countermeasures = self._get_countermeasures(attack_type, attack_vector)
        
        return {
            "attack_assessment": {
                "attack_type": attack_type,
                "severity": data.get("severity", "medium"),
                "affected_systems": affected_systems,
                "containment_status": "ongoing" if data.get("is_ongoing", True) else "contained"
            },
            "recommended_countermeasures": countermeasures
        }
    
    def _process_system_update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process system update information and adjust defenses accordingly."""
        system_name = data.get("system_name", "unknown")
        updated_components = data.get("updated_components", [])
        
        # Update current defenses based on system updates
        current_defenses = self.state.get("current_defenses", {})
        for component in updated_components:
            if component in self.defensive_measures:
                current_defenses[component] = self.defensive_measures[component]
        
        self.state["current_defenses"] = current_defenses
        
        # Recalculate defense effectiveness
        defense_effectiveness = sum(current_defenses.values()) / len(self.defensive_measures) if current_defenses else 0
        self.state["defense_effectiveness"] = defense_effectiveness
        
        return {
            "system_update_status": "processed",
            "defense_effectiveness": defense_effectiveness,
            "defense_status": {
                "weak_points": [d for d in self.defensive_measures if d not in current_defenses],
                "strong_points": [d for d in current_defenses if current_defenses[d] > 0.7]
            }
        }
    
    def _generate_defense_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate general defense recommendations based on current system state."""
        current_defenses = self.state.get("current_defenses", {})
        
        # Identify defensive gaps
        missing_defenses = [d for d in self.defensive_measures if d not in current_defenses]
        weak_defenses = [d for d in current_defenses if current_defenses[d] < 0.6]
        
        # Prioritize recommendations
        recommendations = []
        
        # First recommend implementing missing defenses
        for defense in missing_defenses:
            recommendations.append({
                "measure": defense,
                "impact": self.defensive_measures[defense],
                "priority": "high" if self.defensive_measures[defense] > 0.8 else "medium",
                "description": self._get_defense_description(defense)
            })
        
        # Then recommend strengthening weak defenses
        for defense in weak_defenses:
            recommendations.append({
                "measure": defense,
                "impact": self.defensive_measures[defense] - current_defenses[defense],
                "priority": "medium",
                "description": f"Strengthen existing {defense.replace('_', ' ')}"
            })
        
        # Sort by impact
        recommendations.sort(key=lambda x: x["impact"], reverse=True)
        
        return {
            "current_defense_status": {
                "effectiveness": self.state.get("defense_effectiveness", 0),
                "implemented_measures": list(current_defenses.keys()),
                "missing_measures": missing_defenses,
                "weak_measures": weak_defenses
            },
            "defense_recommendations": recommendations
        }
    
    def _get_remediation_action(self, vulnerability: Dict[str, Any]) -> str:
        """Generate a remediation action for a specific vulnerability."""
        vuln_type = vulnerability.get("type", "")
        
        remediation_actions = {
            "sql_injection": "Implement prepared statements and parameterized queries for all database interactions",
            "xss": "Implement content security policy and properly escape user inputs",
            "csrf": "Implement anti-CSRF tokens and same-site cookie attributes",
            "authentication": "Strengthen password policies and implement multi-factor authentication",
            "authorization": "Review and enforce proper access control policies",
            "unpatched_software": f"Apply security patch for {vulnerability.get('software_name', 'affected software')}",
            "misconfiguration": "Review and correct configuration settings according to security best practices",
            "default_credentials": "Change all default credentials and implement credential management policy"
        }
        
        return remediation_actions.get(vuln_type, f"Address {vulnerability.get('name', 'the vulnerability')} according to vendor recommendations")
    
    def _get_countermeasures(self, attack_type: str, attack_vector: str) -> List[Dict[str, Any]]:
        """Generate countermeasures for a specific attack type and vector."""
        countermeasures = []
        
        # Common countermeasures based on attack type
        if attack_type == "ddos":
            countermeasures.append({
                "action": "Enable DDoS protection service",
                "priority": "critical",
                "description": "Activate traffic scrubbing and rate limiting through DDoS protection service"
            })
        elif attack_type == "ransomware":
            countermeasures.append({
                "action": "Isolate affected systems",
                "priority": "critical",
                "description": "Disconnect affected systems from the network to prevent spread"
            })
            countermeasures.append({
                "action": "Restore from backups",
                "priority": "high",
                "description": "Initiate data restoration from the most recent clean backup"
            })
        elif attack_type == "phishing":
            countermeasures.append({
                "action": "Block sender domains",
                "priority": "medium",
                "description": "Add detected phishing domains to email block list"
            })
            countermeasures.append({
                "action": "Reset compromised credentials",
                "priority": "high",
                "description": "Force password reset for potentially compromised accounts"
            })
        elif attack_type == "brute_force":
            countermeasures.append({
                "action": "Implement account lockout",
                "priority": "high",
                "description": "Configure account lockout after multiple failed login attempts"
            })
        
        # Add general countermeasures
        countermeasures.append({
            "action": "Update monitoring rules",
            "priority": "medium",
            "description": f"Update detection rules to better identify {attack_type} attacks"
        })
        
        return countermeasures
    
    def _get_defense_description(self, defense: str) -> str:
        """Generate a description for a defensive measure."""
        descriptions = {
            "firewall_rules": "Configure network firewall rules to restrict unauthorized traffic",
            "ids_configuration": "Set up and tune intrusion detection system to identify attack patterns",
            "patch_management": "Implement systematic approach to applying security patches across systems",
            "access_control": "Establish role-based access control with principle of least privilege",
            "data_encryption": "Encrypt sensitive data at rest and in transit",
            "network_segmentation": "Divide network into segments with controlled communication between them",
            "endpoint_protection": "Deploy and configure endpoint security solutions on all systems",
            "backup_systems": "Implement regular backup procedures with offline storage component"
        }
        
        return descriptions.get(defense, f"Implement {defense.replace('_', ' ')}")
