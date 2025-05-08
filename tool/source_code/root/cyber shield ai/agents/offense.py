import logging
import random
from typing import Dict, Any, List
import numpy as np
from agents.base import Agent

logger = logging.getLogger(__name__)

class OffenseAgent(Agent):
    """
    Offensive Agent responsible for simulating attacks and identifying vulnerabilities.
    This agent is designed for ethical use in training and simulation environments only.
    """
    
    def __init__(self, name: str = "Offense Agent", description: str = "Simulates attack scenarios for training"):
        capabilities = [
            "vulnerability_scanning",
            "attack_simulation",
            "penetration_testing",
            "social_engineering_simulation",
            "exploit_identification"
        ]
        super().__init__(name, description, capabilities)
        
        # Attack techniques with complexity ratings (0-1)
        self.attack_techniques = {
            "reconnaissance": 0.3,
            "vulnerability_scanning": 0.4,
            "exploitation": 0.7,
            "privilege_escalation": 0.8,
            "lateral_movement": 0.6,
            "data_exfiltration": 0.5,
            "persistence": 0.7,
            "evasion": 0.9
        }
        
        # Common vulnerabilities with exploitability ratings (0-1)
        self.vulnerability_types = {
            "unpatched_software": 0.8,
            "weak_credentials": 0.6,
            "misconfiguration": 0.7,
            "sql_injection": 0.5,
            "xss": 0.5,
            "csrf": 0.4,
            "open_ports": 0.6,
            "default_credentials": 0.8,
            "outdated_cryptography": 0.7
        }
        
        # Initialize state
        self.state = {
            "current_scenario": None,
            "attack_path": [],
            "discovered_vulnerabilities": {},
            "exploitation_success_rate": 0.0,
            "detection_evasion_rate": 0.0
        }
        
        logger.debug(f"OffenseAgent {name} initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming data and perform offensive security operations.
        
        Args:
            data: Dictionary containing scenario details
            
        Returns:
            Dictionary with offensive operation results
        """
        if not self.active:
            return {"error": "Offense agent is not active"}
        
        operation_type = data.get("operation", "")
        
        # Process based on operation type
        if operation_type == "vulnerability_assessment":
            return self._perform_vulnerability_assessment(data)
        elif operation_type == "attack_simulation":
            return self._simulate_attack(data)
        elif operation_type == "penetration_test":
            return self._perform_penetration_test(data)
        else:
            return {"error": f"Unknown operation type: {operation_type}"}
    
    def _perform_vulnerability_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a vulnerability assessment on target systems.
        
        Args:
            data: Dictionary containing target system details
            
        Returns:
            Dictionary with discovered vulnerabilities
        """
        target_systems = data.get("target_systems", [])
        scan_depth = data.get("scan_depth", "medium")
        
        # Depth affects thoroughness and number of vulnerabilities found
        depth_factor = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(scan_depth, 0.6)
        
        discovered_vulnerabilities = []
        
        for system in target_systems:
            system_vulnerabilities = self._discover_system_vulnerabilities(system, depth_factor)
            discovered_vulnerabilities.extend(system_vulnerabilities)
        
        # Update state
        self.state["discovered_vulnerabilities"] = {v["name"]: v for v in discovered_vulnerabilities}
        
        return {
            "operation": "vulnerability_assessment",
            "target_systems": target_systems,
            "scan_depth": scan_depth,
            "vulnerabilities": discovered_vulnerabilities,
            "summary": {
                "total_vulnerabilities": len(discovered_vulnerabilities),
                "critical_count": sum(1 for v in discovered_vulnerabilities if v["severity"] == "critical"),
                "high_count": sum(1 for v in discovered_vulnerabilities if v["severity"] == "high"),
                "medium_count": sum(1 for v in discovered_vulnerabilities if v["severity"] == "medium"),
                "low_count": sum(1 for v in discovered_vulnerabilities if v["severity"] == "low")
            }
        }
    
    def _simulate_attack(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an attack scenario against target systems.
        
        Args:
            data: Dictionary containing attack scenario details
            
        Returns:
            Dictionary with attack simulation results
        """
        attack_type = data.get("attack_type", "general")
        target_systems = data.get("target_systems", [])
        defense_measures = data.get("defense_measures", {})
        
        # Set current scenario
        self.state["current_scenario"] = {
            "type": attack_type,
            "targets": target_systems,
            "defenses": defense_measures
        }
        
        # Generate attack path
        attack_path = self._generate_attack_path(attack_type, target_systems, defense_measures)
        self.state["attack_path"] = attack_path
        
        # Calculate success probabilities for each step
        success_probabilities = []
        for step in attack_path:
            step_type = step.get("technique", "")
            # Base probability from technique complexity
            base_prob = 1 - self.attack_techniques.get(step_type, 0.5)
            
            # Adjust for defense measures
            applicable_defenses = [d for d in defense_measures 
                                  if self._defense_counters_technique(d, step_type)]
            defense_factor = sum(defense_measures.get(d, 0) for d in applicable_defenses) / max(1, len(applicable_defenses))
            
            # Final probability calculation
            step_success_prob = max(0.1, min(0.95, base_prob * (1 - defense_factor * 0.8)))
            step["success_probability"] = step_success_prob
            success_probabilities.append(step_success_prob)
        
        # Calculate overall success and evasion rates
        overall_success_rate = np.prod(success_probabilities) if success_probabilities else 0
        evasion_techniques = [s for s in attack_path if s.get("purpose") == "evasion"]
        evasion_rate = sum(s.get("success_probability", 0) for s in evasion_techniques) / max(1, len(evasion_techniques))
        
        self.state["exploitation_success_rate"] = overall_success_rate
        self.state["detection_evasion_rate"] = evasion_rate
        
        # Determine overall outcome
        outcome = "successful" if overall_success_rate > 0.5 else "partially_successful" if overall_success_rate > 0.2 else "failed"
        
        return {
            "operation": "attack_simulation",
            "attack_type": attack_type,
            "attack_path": attack_path,
            "outcome": outcome,
            "metrics": {
                "overall_success_probability": overall_success_rate,
                "evasion_success_rate": evasion_rate,
                "steps_count": len(attack_path),
                "detected_steps": sum(1 for s in attack_path if s.get("detected", False))
            },
            "critical_findings": self._generate_critical_findings(attack_path, defense_measures)
        }
    
    def _perform_penetration_test(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a penetration test on target systems.
        
        Args:
            data: Dictionary containing penetration test parameters
            
        Returns:
            Dictionary with penetration test results
        """
        target_scope = data.get("scope", {})
        test_parameters = data.get("parameters", {})
        
        # First discover vulnerabilities
        vuln_data = {
            "target_systems": target_scope.get("systems", []),
            "scan_depth": "high"
        }
        vuln_results = self._perform_vulnerability_assessment(vuln_data)
        
        # Then attempt exploitation of discovered vulnerabilities
        exploitable_vulns = [v for v in vuln_results["vulnerabilities"] 
                            if v["severity"] in ["critical", "high"]]
        
        exploitations = []
        for vuln in exploitable_vulns:
            exploitation_success = random.random() < self.vulnerability_types.get(vuln.get("type", ""), 0.5)
            exploitation = {
                "vulnerability": vuln["name"],
                "success": exploitation_success,
                "technique": self._get_exploitation_technique(vuln["type"]),
                "impact": vuln["severity"],
                "post_exploitation": [] if not exploitation_success else self._get_post_exploitation_steps()
            }
            exploitations.append(exploitation)
        
        # Calculate overall metrics
        successful_exploits = sum(1 for e in exploitations if e["success"])
        exploitation_rate = successful_exploits / max(1, len(exploitations))
        
        return {
            "operation": "penetration_test",
            "scope": target_scope,
            "vulnerabilities_discovered": len(vuln_results["vulnerabilities"]),
            "exploitation_attempts": len(exploitations),
            "successful_exploits": successful_exploits,
            "exploitation_rate": exploitation_rate,
            "detailed_exploitations": exploitations,
            "recommendations": self._generate_security_recommendations(vuln_results["vulnerabilities"], exploitations)
        }
    
    def _discover_system_vulnerabilities(self, system: Dict[str, Any], depth_factor: float) -> List[Dict[str, Any]]:
        """
        Discover vulnerabilities on a target system.
        
        Args:
            system: Dictionary containing system details
            depth_factor: Factor that influences scan thoroughness
            
        Returns:
            List of discovered vulnerabilities
        """
        system_type = system.get("type", "generic")
        os_info = system.get("os", "unknown")
        services = system.get("services", [])
        
        vulnerabilities = []
        
        # Base number of vulnerabilities to discover depends on system complexity and scan depth
        service_count = len(services)
        base_vuln_count = int(1 + service_count * depth_factor * random.uniform(0.7, 1.3))
        
        # Generate system-specific vulnerabilities
        for _ in range(base_vuln_count):
            # Select a random vulnerability type with higher probability for common types
            vuln_type = random.choices(
                list(self.vulnerability_types.keys()),
                weights=[self.vulnerability_types[vt] for vt in self.vulnerability_types],
                k=1
            )[0]
            
            # Determine severity based on vulnerability type and random factor
            base_severity = self.vulnerability_types[vuln_type]
            severity_score = base_severity * random.uniform(0.8, 1.2)
            severity = "critical" if severity_score > 0.8 else "high" if severity_score > 0.6 else "medium" if severity_score > 0.4 else "low"
            
            # Create vulnerability description
            if vuln_type == "unpatched_software" and services:
                service = random.choice(services)
                vuln_name = f"Unpatched {service['name']} {service.get('version', '')}"
                description = f"Missing security patches for {service['name']} could allow remote code execution"
            elif vuln_type == "weak_credentials":
                vuln_name = "Weak or default credentials"
                description = "Weak password policy enforcement allows brute force attacks"
            elif vuln_type == "misconfiguration":
                vuln_name = "Security misconfiguration"
                description = "System is configured with insecure settings"
            elif vuln_type == "open_ports" and services:
                service = random.choice(services)
                vuln_name = f"Unnecessary open port: {service.get('port', 'unknown')}"
                description = f"Port {service.get('port', 'unknown')} ({service['name']}) is exposed unnecessarily"
            else:
                vuln_name = f"{vuln_type.replace('_', ' ').title()} vulnerability"
                description = f"System is vulnerable to {vuln_type.replace('_', ' ')} attacks"
            
            vulnerability = {
                "name": vuln_name,
                "type": vuln_type,
                "severity": severity,
                "description": description,
                "affected_system": system.get("name", "unknown"),
                "exploitation_difficulty": 1 - self.vulnerability_types.get(vuln_type, 0.5),
                "remediation_available": random.random() > 0.1  # Most vulnerabilities have remediation
            }
            
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _generate_attack_path(self, attack_type: str, target_systems: List[Dict[str, Any]], 
                             defense_measures: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate a simulated attack path for a specific attack type and target systems.
        
        Args:
            attack_type: Type of attack to simulate
            target_systems: List of target systems
            defense_measures: Dictionary of defense measures and their strengths
            
        Returns:
            List of attack steps forming an attack path
        """
        attack_path = []
        
        # Initial reconnaissance
        attack_path.append({
            "phase": "reconnaissance",
            "technique": "reconnaissance",
            "description": "Gather information about target systems",
            "purpose": "information_gathering",
            "detected": random.random() < 0.3  # Low chance of detection
        })
        
        # Vulnerability scanning
        attack_path.append({
            "phase": "reconnaissance",
            "technique": "vulnerability_scanning",
            "description": "Scan for exploitable vulnerabilities",
            "purpose": "vulnerability_identification",
            "detected": random.random() < 0.5  # Medium chance of detection
        })
        
        # Add attack-specific path elements
        if attack_type == "ransomware":
            # Ransomware attack path
            attack_path.extend([
                {
                    "phase": "initial_access",
                    "technique": "exploitation",
                    "description": "Exploit vulnerable service for initial access",
                    "purpose": "system_access",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "execution",
                    "technique": "privilege_escalation",
                    "description": "Escalate privileges to gain administrative access",
                    "purpose": "higher_privileges",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "persistence",
                    "technique": "persistence",
                    "description": "Establish persistence mechanisms",
                    "purpose": "maintain_access",
                    "detected": random.random() < 0.5
                },
                {
                    "phase": "lateral_movement",
                    "technique": "lateral_movement",
                    "description": "Move laterally to access additional systems",
                    "purpose": "expand_access",
                    "detected": random.random() < 0.7
                },
                {
                    "phase": "impact",
                    "technique": "exploitation",
                    "description": "Deploy ransomware payload and encrypt files",
                    "purpose": "data_encryption",
                    "detected": random.random() < 0.8
                }
            ])
        elif attack_type == "data_exfiltration":
            # Data exfiltration attack path
            attack_path.extend([
                {
                    "phase": "initial_access",
                    "technique": "exploitation",
                    "description": "Exploit vulnerable web application",
                    "purpose": "system_access",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "execution",
                    "technique": "privilege_escalation",
                    "description": "Escalate privileges to access sensitive data",
                    "purpose": "higher_privileges",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "discovery",
                    "technique": "lateral_movement",
                    "description": "Discover location of valuable data",
                    "purpose": "data_discovery",
                    "detected": random.random() < 0.5
                },
                {
                    "phase": "collection",
                    "technique": "exploitation",
                    "description": "Collect and stage sensitive data",
                    "purpose": "data_collection",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "exfiltration",
                    "technique": "data_exfiltration",
                    "description": "Exfiltrate data through encrypted channel",
                    "purpose": "data_theft",
                    "detected": random.random() < 0.7
                },
                {
                    "phase": "covering_tracks",
                    "technique": "evasion",
                    "description": "Clear logs and remove evidence",
                    "purpose": "evasion",
                    "detected": random.random() < 0.5
                }
            ])
        else:
            # Default attack path
            attack_path.extend([
                {
                    "phase": "initial_access",
                    "technique": "exploitation",
                    "description": "Exploit vulnerability for initial access",
                    "purpose": "system_access",
                    "detected": random.random() < 0.6
                },
                {
                    "phase": "execution",
                    "technique": "exploitation",
                    "description": "Execute malicious code on target system",
                    "purpose": "code_execution",
                    "detected": random.random() < 0.7
                },
                {
                    "phase": "persistence",
                    "technique": "persistence",
                    "description": "Establish persistence mechanism",
                    "purpose": "maintain_access",
                    "detected": random.random() < 0.5
                }
            ])
        
        return attack_path
    
    def _defense_counters_technique(self, defense: str, technique: str) -> bool:
        """
        Determine if a specific defense measure counters an attack technique.
        
        Args:
            defense: The defense measure
            technique: The attack technique
            
        Returns:
            Boolean indicating if the defense counters the technique
        """
        defense_effectiveness = {
            "firewall_rules": ["reconnaissance", "exploitation", "lateral_movement"],
            "ids_configuration": ["reconnaissance", "vulnerability_scanning", "exploitation", "lateral_movement"],
            "patch_management": ["exploitation"],
            "access_control": ["privilege_escalation", "lateral_movement"],
            "data_encryption": ["data_exfiltration"],
            "network_segmentation": ["lateral_movement", "data_exfiltration"],
            "endpoint_protection": ["exploitation", "persistence", "evasion"],
            "backup_systems": ["exploitation"]
        }
        
        return technique in defense_effectiveness.get(defense, [])
    
    def _generate_critical_findings(self, attack_path: List[Dict[str, Any]], defense_measures: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate critical findings from an attack simulation.
        
        Args:
            attack_path: The simulated attack path
            defense_measures: The applied defense measures
            
        Returns:
            List of critical findings
        """
        findings = []
        
        # Check for undetected critical steps
        undetected_critical = [s for s in attack_path 
                              if not s.get("detected", False) and s.get("phase") in ["execution", "impact", "exfiltration"]]
        if undetected_critical:
            findings.append({
                "type": "detection_gap",
                "severity": "critical",
                "description": f"Critical attack steps went undetected: {', '.join(s['phase'] for s in undetected_critical)}",
                "recommendation": "Enhance monitoring and detection capabilities"
            })
        
        # Check for successful privilege escalation
        priv_esc_steps = [s for s in attack_path if s.get("technique") == "privilege_escalation"]
        if any(s.get("success_probability", 0) > 0.6 for s in priv_esc_steps):
            findings.append({
                "type": "privilege_escalation",
                "severity": "high",
                "description": "Privilege escalation techniques have high success probability",
                "recommendation": "Implement stronger access controls and privilege management"
            })
        
        # Check for missing key defenses
        critical_defenses = ["patch_management", "access_control", "endpoint_protection"]
        missing_critical = [d for d in critical_defenses if d not in defense_measures]
        if missing_critical:
            findings.append({
                "type": "missing_defenses",
                "severity": "high",
                "description": f"Critical defense measures not implemented: {', '.join(missing_critical)}",
                "recommendation": f"Implement missing defense measures: {', '.join(missing_critical)}"
            })
        
        # Check for successful data exfiltration
        exfil_steps = [s for s in attack_path if s.get("purpose") == "data_theft"]
        if any(s.get("success_probability", 0) > 0.5 for s in exfil_steps):
            findings.append({
                "type": "data_leak",
                "severity": "critical",
                "description": "Data exfiltration techniques have high success probability",
                "recommendation": "Implement data loss prevention and enhanced monitoring of outbound traffic"
            })
        
        return findings
    
    def _get_exploitation_technique(self, vuln_type: str) -> str:
        """Get an appropriate exploitation technique for a vulnerability type."""
        techniques = {
            "unpatched_software": "Remote code execution exploit",
            "weak_credentials": "Password brute forcing",
            "misconfiguration": "Security bypass exploitation",
            "sql_injection": "SQL query manipulation",
            "xss": "Client-side script injection",
            "csrf": "Cross-site request forgery",
            "open_ports": "Unauthorized service access",
            "default_credentials": "Default credential usage",
            "outdated_cryptography": "Cryptographic attack"
        }
        
        return techniques.get(vuln_type, "Generic exploitation technique")
    
    def _get_post_exploitation_steps(self) -> List[Dict[str, Any]]:
        """Generate post-exploitation steps for a successful exploitation."""
        possible_steps = [
            {"action": "Credential harvesting", "success": random.random() < 0.7},
            {"action": "Privilege escalation", "success": random.random() < 0.6},
            {"action": "Lateral movement", "success": random.random() < 0.5},
            {"action": "Persistence establishment", "success": random.random() < 0.8},
            {"action": "Data exfiltration", "success": random.random() < 0.4}
        ]
        
        # Select a random subset of steps
        selected_count = random.randint(1, len(possible_steps))
        return random.sample(possible_steps, selected_count)
    
    def _generate_security_recommendations(self, vulnerabilities: List[Dict[str, Any]], 
                                         exploitations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate security recommendations based on penetration test results."""
        recommendations = []
        
        # Prioritize recommendations for successfully exploited vulnerabilities
        exploited_vulns = [e["vulnerability"] for e in exploitations if e["success"]]
        
        for vuln in vulnerabilities:
            priority = "critical" if vuln["name"] in exploited_vulns else vuln["severity"]
            
            recommendation = {
                "vulnerability": vuln["name"],
                "priority": priority,
                "recommendation": self._get_remediation_for_vulnerability(vuln["type"]),
                "exploitation_status": "Successfully exploited" if vuln["name"] in exploited_vulns else "Not exploited"
            }
            
            recommendations.append(recommendation)
        
        # Sort by priority (critical first)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 4))
        
        return recommendations
    
    def _get_remediation_for_vulnerability(self, vuln_type: str) -> str:
        """Get remediation steps for a specific vulnerability type."""
        remediations = {
            "unpatched_software": "Apply security patches and implement automated patch management",
            "weak_credentials": "Enforce strong password policy and implement multi-factor authentication",
            "misconfiguration": "Follow security hardening guidelines and implement secure configuration baselines",
            "sql_injection": "Use parameterized queries and implement input validation",
            "xss": "Implement content security policy and output encoding",
            "csrf": "Implement anti-CSRF tokens and same-site cookie attributes",
            "open_ports": "Close unnecessary ports and implement network segmentation",
            "default_credentials": "Change default credentials and implement secure credential management",
            "outdated_cryptography": "Update to modern cryptographic algorithms and protocols"
        }
        
        return remediations.get(vuln_type, "Follow vendor-specific security recommendations")
