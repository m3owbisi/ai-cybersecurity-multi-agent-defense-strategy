import logging
import random
import time
from collections import deque
from typing import Dict, Any, List, Optional, Tuple, Deque
import numpy as np
from agents.base import Agent

logger = logging.getLogger(__name__)

class DetectionAgent(Agent):
    """
    Detection Agent responsible for monitoring network traffic and system events
    to identify potential threats and anomalies.
    """
    
    def __init__(self, name: str = "Detection Agent", description: str = "Monitors for threats and anomalies"):
        capabilities = [
            "traffic_analysis",
            "anomaly_detection",
            "pattern_recognition",
            "threat_intelligence",
            "behavioral_analysis"
        ]
        super().__init__(name, description, capabilities)
        
        # History window for baseline calculation
        self.traffic_history: Deque[Dict[str, Any]] = deque(maxlen=100)
        
        # Detection models (simplified for demo)
        self.detection_thresholds = {
            "connection_rate": 0.75,  # Connections per second threshold multiplier
            "packet_size": 0.8,       # Packet size deviation threshold
            "connection_diversity": 0.7,  # Unique endpoints threshold
            "protocol_anomaly": 0.8,  # Protocol behavior anomaly threshold
            "payload_anomaly": 0.85   # Payload content anomaly threshold
        }
        
        # Recent alerts cache
        self.recent_alerts: Deque[Dict[str, Any]] = deque(maxlen=20)
        
        # Initialize state
        self.state = {
            "baseline_established": False,
            "baseline_stats": {},
            "current_threat_level": "low",
            "anomaly_scores": {},
            "recent_detections": [],
            "false_positive_rate": 0.0
        }
        
        logger.debug(f"DetectionAgent {name} initialized")
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming data for threat detection.
        
        Args:
            data: Dictionary containing operation details
            
        Returns:
            Dictionary with detection results
        """
        if not self.active:
            return {"error": "Detection agent is not active"}
        
        operation = data.get("operation", "")
        
        # Process based on operation type
        if operation == "analyze_traffic":
            return self._analyze_traffic(data.get("traffic_data", []))
        elif operation == "check_baseline":
            return self._check_baseline()
        elif operation == "detect_simulation":
            return self._detect_simulation(data.get("attack_data", {}))
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def _analyze_traffic(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze network traffic data for anomalies and potential threats.
        
        Args:
            traffic_data: List of network traffic records
            
        Returns:
            Dictionary with analysis results
        """
        if not traffic_data:
            return {"error": "No traffic data provided"}
        
        # Add traffic to history
        for traffic in traffic_data:
            self.traffic_history.append(traffic)
        
        # Establish baseline if not already done
        if not self.state["baseline_established"] and len(self.traffic_history) >= 30:
            self._establish_baseline()
        
        # Calculate anomaly scores
        anomaly_scores = self._calculate_anomaly_scores(traffic_data)
        self.state["anomaly_scores"] = anomaly_scores
        
        # Identify threats based on anomaly scores
        detected_threats = self._identify_threats(traffic_data, anomaly_scores)
        
        # Update state with recent detections
        self.state["recent_detections"] = detected_threats
        
        # Determine overall threat level
        overall_threat_level = self._determine_threat_level(detected_threats)
        self.state["current_threat_level"] = overall_threat_level
        
        # Log significant findings
        if detected_threats:
            logger.info(f"Detected {len(detected_threats)} potential threats. Threat level: {overall_threat_level}")
            for threat in detected_threats:
                logger.debug(f"Threat detected: {threat['type']} with confidence {threat['confidence']:.2f}")
        
        return {
            "analysis_time": time.time(),
            "records_analyzed": len(traffic_data),
            "baseline_established": self.state["baseline_established"],
            "threat_level": overall_threat_level,
            "detected_threats": detected_threats,
            "anomaly_summary": self._summarize_anomalies(anomaly_scores)
        }
    
    def _establish_baseline(self) -> None:
        """Establish a baseline from historical traffic for anomaly detection."""
        if len(self.traffic_history) < 30:
            logger.warning("Not enough traffic history to establish baseline")
            return
        
        # Extract key metrics
        connection_rates = []
        packet_sizes = []
        unique_destinations = set()
        protocols = {}
        
        for traffic in self.traffic_history:
            # Calculate connection rate (simplified)
            connection_rates.append(1)  # Each entry counts as one connection
            
            # Track packet sizes
            packet_sizes.append(traffic.get("payload_size", 0))
            
            # Track unique destinations
            unique_destinations.add(traffic.get("destination_ip", "unknown"))
            
            # Track protocol distribution
            protocol = traffic.get("protocol", "unknown")
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        # Calculate baseline statistics
        baseline_stats = {
            "avg_connection_rate": len(connection_rates) / max(1, len(self.traffic_history)),
            "avg_packet_size": np.mean(packet_sizes) if packet_sizes else 0,
            "std_packet_size": np.std(packet_sizes) if packet_sizes else 0,
            "unique_destinations_count": len(unique_destinations),
            "protocol_distribution": {p: count / len(self.traffic_history) for p, count in protocols.items()}
        }
        
        self.state["baseline_stats"] = baseline_stats
        self.state["baseline_established"] = True
        
        logger.info("Traffic baseline established")
    
    def _calculate_anomaly_scores(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate anomaly scores for different traffic characteristics.
        
        Args:
            traffic_data: List of network traffic records
            
        Returns:
            Dictionary with anomaly scores for different metrics
        """
        # If baseline not established, use simplified detection
        if not self.state["baseline_established"]:
            return {
                "connection_rate": 0.0,
                "packet_size": 0.0,
                "connection_diversity": 0.0,
                "protocol_anomaly": 0.0,
                "payload_anomaly": 0.5  # Default mid-range value
            }
        
        baseline = self.state["baseline_stats"]
        
        # Current metrics
        current_connection_rate = len(traffic_data)
        
        packet_sizes = [t.get("payload_size", 0) for t in traffic_data]
        current_avg_packet_size = np.mean(packet_sizes) if packet_sizes else 0
        
        unique_destinations = set(t.get("destination_ip", "") for t in traffic_data)
        current_unique_destinations = len(unique_destinations)
        
        # Protocol distribution
        current_protocols = {}
        for traffic in traffic_data:
            protocol = traffic.get("protocol", "unknown")
            current_protocols[protocol] = current_protocols.get(protocol, 0) + 1
        
        # Calculate anomaly scores (0-1 scale, higher is more anomalous)
        
        # Connection rate anomaly (compare to baseline)
        connection_rate_anomaly = (
            min(1.0, current_connection_rate / (baseline["avg_connection_rate"] * self.detection_thresholds["connection_rate"]))
            if baseline["avg_connection_rate"] > 0 else 0.5
        )
        
        # Packet size anomaly (compare to baseline using z-score)
        if baseline["std_packet_size"] > 0:
            z_score = abs(current_avg_packet_size - baseline["avg_packet_size"]) / baseline["std_packet_size"]
            packet_size_anomaly = min(1.0, z_score / self.detection_thresholds["packet_size"])
        else:
            packet_size_anomaly = 0.0
        
        # Connection diversity anomaly
        expected_unique = baseline["unique_destinations_count"] * (len(traffic_data) / max(1, len(self.traffic_history)))
        if expected_unique > 0:
            diversity_ratio = current_unique_destinations / expected_unique
            connection_diversity_anomaly = abs(1 - diversity_ratio) * self.detection_thresholds["connection_diversity"]
        else:
            connection_diversity_anomaly = 0.0
        
        # Protocol anomaly (compare distributions)
        protocol_anomaly = 0.0
        baseline_protocols = baseline["protocol_distribution"]
        
        for protocol, count in current_protocols.items():
            current_ratio = count / len(traffic_data)
            baseline_ratio = baseline_protocols.get(protocol, 0)
            protocol_anomaly = max(protocol_anomaly, abs(current_ratio - baseline_ratio))
        
        # Payload anomaly (simplified)
        # In a real system, this would involve deep packet inspection or content analysis
        payload_patterns = sum(1 for t in traffic_data if self._check_payload_anomaly(t))
        payload_anomaly = min(1.0, payload_patterns / max(1, len(traffic_data)))
        
        return {
            "connection_rate": connection_rate_anomaly,
            "packet_size": packet_size_anomaly,
            "connection_diversity": connection_diversity_anomaly,
            "protocol_anomaly": protocol_anomaly,
            "payload_anomaly": payload_anomaly
        }
    
    def _identify_threats(self, traffic_data: List[Dict[str, Any]], anomaly_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Identify potential threats based on anomaly scores.
        
        Args:
            traffic_data: List of network traffic records
            anomaly_scores: Dictionary with anomaly scores
            
        Returns:
            List of detected threats
        """
        threats = []
        
        # Calculate overall anomaly score
        overall_score = sum(anomaly_scores.values()) / len(anomaly_scores)
        
        # Set detection threshold (can be adjusted)
        detection_threshold = 0.6
        
        # Check for specific threat patterns
        for traffic in traffic_data:
            # Look for indicators of compromise
            is_malicious = traffic.get("is_malicious", False)  # For simulation data that's prelabeled
            confidence = 0.0
            threat_type = "unknown"
            
            # Determine threat type and confidence based on traffic characteristics and anomaly scores
            if is_malicious or overall_score > detection_threshold:
                # Analyze the specific type of threat
                threat_type, confidence = self._determine_threat_type(traffic, anomaly_scores)
                
                # Only report if confidence is sufficient
                if confidence > 0.5:
                    threat = {
                        "id": str(int(time.time() * 1000)) + str(random.randint(1000, 9999)),
                        "source_ip": traffic.get("source_ip", "unknown"),
                        "destination_ip": traffic.get("destination_ip", "unknown"),
                        "protocol": traffic.get("protocol", "unknown"),
                        "timestamp": traffic.get("timestamp", time.time()),
                        "type": threat_type,
                        "confidence": confidence,
                        "anomaly_factors": [k for k, v in anomaly_scores.items() if v > 0.7],
                        "description": self._generate_threat_description(threat_type, traffic)
                    }
                    
                    # Check if this is a duplicate of a recent alert
                    if not self._is_duplicate_alert(threat):
                        threats.append(threat)
                        self.recent_alerts.append(threat)
        
        return threats
    
    def _determine_threat_type(self, traffic: Dict[str, Any], anomaly_scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Determine the specific type of threat and confidence level.
        
        Args:
            traffic: A network traffic record
            anomaly_scores: Dictionary with anomaly scores
            
        Returns:
            Tuple of (threat_type, confidence)
        """
        # Extract relevant features
        port = traffic.get("port", 0)
        protocol = traffic.get("protocol", "unknown")
        payload_size = traffic.get("payload_size", 0)
        
        # Initialize confidence tracking
        confidence = 0.0
        threat_type = "unknown"
        
        # DOS attack detection
        if (anomaly_scores["connection_rate"] > 0.8 and 
            anomaly_scores["connection_diversity"] < 0.3):
            threat_type = "dos_attack"
            confidence = anomaly_scores["connection_rate"]
        
        # Port scan detection
        elif port in [21, 22, 23, 25, 53, 80, 443, 445, 3389] and anomaly_scores["connection_diversity"] > 0.8:
            threat_type = "port_scan"
            confidence = anomaly_scores["connection_diversity"]
        
        # Data exfiltration detection
        elif payload_size > 10000 and anomaly_scores["packet_size"] > 0.7:
            threat_type = "data_exfiltration"
            confidence = anomaly_scores["packet_size"]
        
        # Command and control traffic
        elif protocol in ["tcp", "https"] and anomaly_scores["protocol_anomaly"] > 0.7:
            threat_type = "command_and_control"
            confidence = anomaly_scores["protocol_anomaly"]
        
        # Malware or exploit payload
        elif anomaly_scores["payload_anomaly"] > 0.8:
            threat_type = "malicious_payload"
            confidence = anomaly_scores["payload_anomaly"]
        
        # Brute force attempt
        elif protocol in ["ssh", "ftp", "smtp"] and anomaly_scores["connection_rate"] > 0.7:
            threat_type = "brute_force"
            confidence = anomaly_scores["connection_rate"]
        
        # Unknown but suspicious
        else:
            threat_type = "suspicious_activity"
            confidence = overall_score = sum(anomaly_scores.values()) / len(anomaly_scores)
        
        return threat_type, confidence
    
    def _generate_threat_description(self, threat_type: str, traffic: Dict[str, Any]) -> str:
        """Generate a human-readable description of the threat."""
        descriptions = {
            "dos_attack": f"Potential DoS attack detected from {traffic.get('source_ip', 'unknown')}",
            "port_scan": f"Port scanning activity detected from {traffic.get('source_ip', 'unknown')}",
            "data_exfiltration": f"Unusual data transfer to {traffic.get('destination_ip', 'unknown')}",
            "command_and_control": f"Potential C2 communication with {traffic.get('destination_ip', 'unknown')}",
            "malicious_payload": f"Suspicious payload detected in traffic to {traffic.get('destination_ip', 'unknown')}",
            "brute_force": f"Possible brute force attempt on {traffic.get('protocol', 'unknown').upper()} service",
            "suspicious_activity": f"Anomalous traffic pattern detected between {traffic.get('source_ip', 'unknown')} and {traffic.get('destination_ip', 'unknown')}"
        }
        
        return descriptions.get(threat_type, f"Unknown threat type detected in traffic")
    
    def _is_duplicate_alert(self, threat: Dict[str, Any]) -> bool:
        """Check if an alert is a duplicate of a recently generated alert."""
        for recent in self.recent_alerts:
            if (recent["source_ip"] == threat["source_ip"] and
                recent["destination_ip"] == threat["destination_ip"] and
                recent["type"] == threat["type"] and
                abs(recent["timestamp"] - threat["timestamp"]) < 300):  # Within 5 minutes
                return True
        return False
    
    def _check_baseline(self) -> Dict[str, Any]:
        """Return the current baseline statistics and status."""
        return {
            "baseline_established": self.state["baseline_established"],
            "baseline_stats": self.state["baseline_stats"],
            "traffic_history_size": len(self.traffic_history)
        }
    
    def _detect_simulation(self, attack_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze simulated attack data to test detection capabilities.
        
        Args:
            attack_data: Data about a simulated attack
            
        Returns:
            Dictionary with detection results for the simulation
        """
        # Extract attack path from simulation data
        attack_path = attack_data.get("attack_path", [])
        
        if not attack_path:
            return {"error": "No attack path provided in simulation data"}
        
        # Process each step in the attack path
        detected_steps = []
        missed_steps = []
        
        for i, step in enumerate(attack_path):
            # Determine if step would be detected
            technique = step.get("technique", "unknown")
            purpose = step.get("purpose", "unknown")
            phase = step.get("phase", "unknown")
            
            # Calculate detection probability based on technique and phase
            base_detection_prob = {
                "reconnaissance": 0.3,
                "vulnerability_scanning": 0.5,
                "exploitation": 0.7,
                "privilege_escalation": 0.6,
                "lateral_movement": 0.65,
                "data_exfiltration": 0.8,
                "persistence": 0.4,
                "evasion": 0.3
            }.get(technique, 0.5)
            
            # Adjust based on phase
            phase_modifier = {
                "reconnaissance": 0.9,
                "initial_access": 1.1,
                "execution": 1.2,
                "persistence": 0.8,
                "privilege_escalation": 1.1,
                "defense_evasion": 0.7,
                "credential_access": 1.0,
                "discovery": 0.9,
                "lateral_movement": 1.1,
                "collection": 1.0,
                "exfiltration": 1.2,
                "impact": 1.3
            }.get(phase, 1.0)
            
            # Calculate final detection probability
            detection_prob = min(0.95, base_detection_prob * phase_modifier)
            
            # Determine if detected
            is_detected = step.get("detected", random.random() < detection_prob)
            
            # Update step with detection information
            step["detected"] = is_detected
            step["detection_difficulty"] = 1 - detection_prob
            
            if is_detected:
                detected_steps.append({
                    "step_index": i,
                    "phase": phase,
                    "technique": technique,
                    "detection_time": "real-time" if detection_prob > 0.7 else "delayed",
                    "confidence": detection_prob * random.uniform(0.8, 1.0)
                })
            else:
                missed_steps.append({
                    "step_index": i,
                    "phase": phase,
                    "technique": technique,
                    "reason": self._get_missed_detection_reason(technique)
                })
        
        # Calculate detection metrics
        detection_rate = len(detected_steps) / len(attack_path)
        early_detection = any(d["step_index"] <= 1 for d in detected_steps)
        critical_steps_detected = sum(1 for d in detected_steps 
                                     if attack_path[d["step_index"]].get("phase") in ["execution", "impact", "exfiltration"])
        critical_steps_total = sum(1 for s in attack_path 
                                  if s.get("phase") in ["execution", "impact", "exfiltration"])
        critical_detection_rate = critical_steps_detected / max(1, critical_steps_total)
        
        return {
            "detection_summary": {
                "attack_steps": len(attack_path),
                "detected_steps": len(detected_steps),
                "missed_steps": len(missed_steps),
                "detection_rate": detection_rate,
                "early_detection": early_detection,
                "critical_detection_rate": critical_detection_rate
            },
            "detected_steps": detected_steps,
            "missed_steps": missed_steps,
            "recommendations": self._generate_detection_recommendations(missed_steps)
        }
    
    def _get_missed_detection_reason(self, technique: str) -> str:
        """Generate a reason why a particular technique was not detected."""
        reasons = {
            "reconnaissance": "Low-volume scanning activity below detection threshold",
            "vulnerability_scanning": "Scanning activity disguised as normal traffic",
            "exploitation": "Exploit used an unknown vulnerability or evasion technique",
            "privilege_escalation": "Legitimate credentials were used for escalation",
            "lateral_movement": "Movement used authorized access channels",
            "data_exfiltration": "Data was exfiltrated using encrypted channels",
            "persistence": "Persistence mechanism mimicked legitimate system processes",
            "evasion": "Advanced evasion techniques bypassed detection mechanisms"
        }
        
        return reasons.get(technique, "Detection failed due to technique sophistication")
    
    def _generate_detection_recommendations(self, missed_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommendations to improve detection capabilities."""
        recommendations = []
        
        # Group missed steps by technique
        techniques = {}
        for step in missed_steps:
            technique = step["technique"]
            techniques[technique] = techniques.get(technique, 0) + 1
        
        # Generate recommendations based on most common missed techniques
        for technique, count in sorted(techniques.items(), key=lambda x: x[1], reverse=True):
            recommendation = {
                "focus_area": technique,
                "description": self._get_detection_improvement(technique),
                "priority": "high" if count > 2 else "medium" if count > 1 else "low"
            }
            recommendations.append(recommendation)
        
        # Add general recommendations if needed
        if len(recommendations) < 3:
            general_recs = [
                {
                    "focus_area": "baseline_tuning",
                    "description": "Refine baseline traffic patterns to improve anomaly detection",
                    "priority": "medium"
                },
                {
                    "focus_area": "endpoint_visibility",
                    "description": "Enhance endpoint monitoring to detect exploitation attempts",
                    "priority": "high"
                },
                {
                    "focus_area": "threat_intelligence",
                    "description": "Incorporate additional threat intelligence feeds",
                    "priority": "medium"
                }
            ]
            
            # Add general recommendations not already covered
            for rec in general_recs:
                if not any(r["focus_area"] == rec["focus_area"] for r in recommendations):
                    recommendations.append(rec)
                    if len(recommendations) >= 3:
                        break
        
        return recommendations
    
    def _get_detection_improvement(self, technique: str) -> str:
        """Get a specific recommendation to improve detection for a technique."""
        improvements = {
            "reconnaissance": "Implement network traffic baselining and enhance perimeter monitoring",
            "vulnerability_scanning": "Deploy honeypots and scanning detection rules",
            "exploitation": "Update IDS signatures and implement behavior-based detection",
            "privilege_escalation": "Monitor privilege changes and implement just-in-time access",
            "lateral_movement": "Enhance network segmentation monitoring and authentication logging",
            "data_exfiltration": "Implement DLP solutions and monitor for unusual data transfers",
            "persistence": "Increase endpoint monitoring for registry and startup modifications",
            "evasion": "Deploy advanced behavioral analytics and sandboxing technology"
        }
        
        return improvements.get(technique, "Enhance detection mechanisms with behavior analytics")
    
    def _determine_threat_level(self, detected_threats: List[Dict[str, Any]]) -> str:
        """Determine the overall threat level based on detected threats."""
        if not detected_threats:
            return "low"
        
        # Count threats by confidence level
        high_confidence = sum(1 for t in detected_threats if t["confidence"] > 0.8)
        medium_confidence = sum(1 for t in detected_threats if 0.6 <= t["confidence"] <= 0.8)
        
        # Count threats by type severity
        critical_types = ["command_and_control", "malicious_payload", "data_exfiltration"]
        high_types = ["brute_force", "dos_attack"]
        
        critical_count = sum(1 for t in detected_threats if t["type"] in critical_types)
        high_count = sum(1 for t in detected_threats if t["type"] in high_types)
        
        # Determine overall threat level
        if critical_count > 0 and high_confidence > 0:
            return "critical"
        elif critical_count > 0 or high_confidence > 2:
            return "high"
        elif high_count > 0 or medium_confidence > 2:
            return "medium"
        else:
            return "low"
    
    def _check_payload_anomaly(self, traffic: Dict[str, Any]) -> bool:
        """
        Check for anomalies in the payload.
        In a real system, this would involve deeper analysis.
        
        Args:
            traffic: A network traffic record
            
        Returns:
            Boolean indicating if payload appears anomalous
        """
        # For simulation, use the pre-labeled malicious flag if available
        if "is_malicious" in traffic:
            return traffic["is_malicious"]
        
        # For demo purposes, generate a simple heuristic
        payload_size = traffic.get("payload_size", 0)
        port = traffic.get("port", 0)
        
        # Unusual combinations that might indicate malicious traffic
        suspicious_patterns = [
            (port in [80, 443] and payload_size > 50000),  # Unusually large HTTP(S) payload
            (port in [22, 23] and payload_size > 5000),    # Unusually large SSH/Telnet payload
            (port in [53] and payload_size > 1000),        # Unusually large DNS payload
            (port in [25] and payload_size > 10000)        # Unusually large SMTP payload
        ]
        
        return any(suspicious_patterns)
    
    def _summarize_anomalies(self, anomaly_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Summarize anomaly scores for reporting.
        
        Args:
            anomaly_scores: Dictionary with anomaly scores
            
        Returns:
            Dictionary with summarized anomaly information
        """
        # Average anomaly score
        avg_score = sum(anomaly_scores.values()) / len(anomaly_scores)
        
        # Find top anomalies
        top_anomalies = sorted(
            [(k, v) for k, v in anomaly_scores.items()], 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Classify overall anomaly level
        if avg_score > 0.8:
            anomaly_level = "critical"
        elif avg_score > 0.6:
            anomaly_level = "high"
        elif avg_score > 0.4:
            anomaly_level = "medium"
        else:
            anomaly_level = "low"
        
        return {
            "overall_score": avg_score,
            "anomaly_level": anomaly_level,
            "top_anomalies": [{"type": k, "score": v} for k, v in top_anomalies if v > 0.3]
        }
