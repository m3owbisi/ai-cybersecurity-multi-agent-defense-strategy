import logging
import json
import random
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Predefined scenarios for security training and simulation
DEFAULT_SCENARIOS = [
    {
        "id": "basic_reconnaissance",
        "name": "Basic Reconnaissance",
        "description": "Simulation of basic reconnaissance activities against network infrastructure",
        "type": "attack_simulation",
        "difficulty": "easy",
        "max_steps": 50,
        "network_params": {
            "server_count": 5,
            "endpoint_count": 10,
            "malicious_ratio": 0.05,
            "traffic_rate": 3,
            "attack_probability": 1.0
        },
        "attack_params": {
            "attack_type": "reconnaissance",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "http", "port": 80}, {"name": "ssh", "port": 22}]},
                {"type": "server", "os": "Windows Server", "services": [{"name": "https", "port": 443}]}
            ],
            "defense_measures": {
                "firewall_rules": 0.5,
                "ids_configuration": 0.3
            }
        },
        "learning_objectives": [
            "Identify reconnaissance patterns",
            "Understand basic network traffic analysis",
            "Practice configuring alerts for scanning activity"
        ]
    },
    {
        "id": "ransomware_attack",
        "name": "Ransomware Attack Simulation",
        "description": "Simulation of a ransomware attack from initial access to encryption",
        "type": "attack_simulation",
        "difficulty": "medium",
        "max_steps": 75,
        "network_params": {
            "server_count": 8,
            "endpoint_count": 15,
            "malicious_ratio": 0.1,
            "traffic_rate": 5,
            "attack_probability": 1.0
        },
        "attack_params": {
            "attack_type": "ransomware",
            "target_systems": [
                {"type": "server", "os": "Windows Server", "services": [{"name": "smb", "port": 445}, {"name": "rdp", "port": 3389}]},
                {"type": "endpoint", "os": "Windows 10", "services": []}
            ],
            "defense_measures": {
                "firewall_rules": 0.6,
                "ids_configuration": 0.5,
                "patch_management": 0.4,
                "endpoint_protection": 0.3
            }
        },
        "learning_objectives": [
            "Understand ransomware attack progression",
            "Identify indicators of compromise",
            "Practice incident response for ransomware"
        ]
    },
    {
        "id": "data_exfiltration",
        "name": "Data Exfiltration Attack",
        "description": "Simulation of targeted data theft through sophisticated exfiltration techniques",
        "type": "attack_simulation",
        "difficulty": "hard",
        "max_steps": 100,
        "network_params": {
            "server_count": 10,
            "endpoint_count": 20,
            "malicious_ratio": 0.15,
            "traffic_rate": 8,
            "attack_probability": 1.0
        },
        "attack_params": {
            "attack_type": "data_exfiltration",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "database", "port": 5432}, {"name": "http", "port": 80}]},
                {"type": "server", "os": "Windows Server", "services": [{"name": "file_share", "port": 445}]}
            ],
            "defense_measures": {
                "firewall_rules": 0.7,
                "ids_configuration": 0.6,
                "data_encryption": 0.4,
                "network_segmentation": 0.5
            }
        },
        "learning_objectives": [
            "Detect data exfiltration attempts",
            "Understand covert channels",
            "Implement data loss prevention measures"
        ]
    },
    {
        "id": "web_application_attack",
        "name": "Web Application Attack",
        "description": "Simulation of attacks targeting web applications including SQL injection and XSS",
        "type": "attack_simulation",
        "difficulty": "medium",
        "max_steps": 60,
        "network_params": {
            "server_count": 6,
            "endpoint_count": 12,
            "malicious_ratio": 0.08,
            "traffic_rate": 6,
            "attack_probability": 0.9
        },
        "attack_params": {
            "attack_type": "web_app_attack",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "http", "port": 80}, {"name": "https", "port": 443}]}
            ],
            "defense_measures": {
                "firewall_rules": 0.6,
                "ids_configuration": 0.5,
                "web_application_firewall": 0.4
            }
        },
        "learning_objectives": [
            "Identify web application vulnerabilities",
            "Understand SQL injection and XSS attacks",
            "Configure web application security controls"
        ]
    },
    {
        "id": "ddos_simulation",
        "name": "DDoS Attack Simulation",
        "description": "Simulation of distributed denial of service attacks against network services",
        "type": "attack_simulation",
        "difficulty": "medium",
        "max_steps": 70,
        "network_params": {
            "server_count": 5,
            "endpoint_count": 8,
            "malicious_ratio": 0.2,
            "traffic_rate": 15,
            "attack_probability": 1.0
        },
        "attack_params": {
            "attack_type": "ddos",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "http", "port": 80}]}
            ],
            "defense_measures": {
                "firewall_rules": 0.7,
                "ids_configuration": 0.6,
                "ddos_protection": 0.5
            }
        },
        "learning_objectives": [
            "Recognize DDoS attack patterns",
            "Implement traffic filtering strategies",
            "Configure rate limiting and traffic scrubbing"
        ]
    },
    {
        "id": "insider_threat",
        "name": "Insider Threat Simulation",
        "description": "Simulation of malicious activities from privileged internal users",
        "type": "attack_simulation",
        "difficulty": "hard",
        "max_steps": 90,
        "network_params": {
            "server_count": 8,
            "endpoint_count": 18,
            "malicious_ratio": 0.07,
            "traffic_rate": 7,
            "attack_probability": 0.8
        },
        "attack_params": {
            "attack_type": "insider",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "database", "port": 5432}]},
                {"type": "server", "os": "Windows Server", "services": [{"name": "file_share", "port": 445}]}
            ],
            "defense_measures": {
                "access_control": 0.5,
                "user_monitoring": 0.4,
                "data_encryption": 0.6
            }
        },
        "learning_objectives": [
            "Detect unusual user behavior",
            "Implement least privilege access controls",
            "Configure data access monitoring"
        ]
    },
    {
        "id": "phishing_campaign",
        "name": "Phishing Campaign",
        "description": "Simulation of a phishing campaign targeting organization users",
        "type": "training_session",
        "difficulty": "easy",
        "max_steps": 40,
        "network_params": {
            "server_count": 4,
            "endpoint_count": 20,
            "malicious_ratio": 0.1,
            "traffic_rate": 4,
            "attack_probability": 0.7
        },
        "attack_params": {
            "attack_type": "phishing",
            "target_systems": [
                {"type": "endpoint", "os": "Windows 10", "services": []}
            ],
            "defense_measures": {
                "email_filtering": 0.5,
                "user_training": 0.3,
                "endpoint_protection": 0.4
            }
        },
        "learning_objectives": [
            "Identify phishing attempts",
            "Configure email security filters",
            "Educate users on security awareness"
        ]
    },
    {
        "id": "advanced_persistent_threat",
        "name": "Advanced Persistent Threat (APT)",
        "description": "Simulation of a sophisticated APT campaign with multiple attack stages",
        "type": "attack_simulation",
        "difficulty": "expert",
        "max_steps": 150,
        "network_params": {
            "server_count": 12,
            "endpoint_count": 25,
            "malicious_ratio": 0.12,
            "traffic_rate": 10,
            "attack_probability": 1.0
        },
        "attack_params": {
            "attack_type": "apt",
            "target_systems": [
                {"type": "server", "os": "Linux", "services": [{"name": "http", "port": 80}, {"name": "ssh", "port": 22}]},
                {"type": "server", "os": "Windows Server", "services": [{"name": "database", "port": 1433}]},
                {"type": "endpoint", "os": "Windows 10", "services": []}
            ],
            "defense_measures": {
                "firewall_rules": 0.8,
                "ids_configuration": 0.7,
                "endpoint_protection": 0.6,
                "network_segmentation": 0.5,
                "patch_management": 0.6,
                "data_encryption": 0.7
            }
        },
        "learning_objectives": [
            "Understand sophisticated attack chains",
            "Detect stealthy persistence techniques",
            "Implement defense-in-depth strategies",
            "Practice comprehensive incident response"
        ]
    }
]

def get_all_scenarios() -> List[Dict[str, Any]]:
    """
    Get all available simulation scenarios.
    
    Returns:
        List of scenario dictionaries
    """
    return DEFAULT_SCENARIOS

def load_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a specific scenario by ID.
    
    Args:
        scenario_id: The ID of the scenario to load
        
    Returns:
        Scenario dictionary or None if not found
    """
    for scenario in DEFAULT_SCENARIOS:
        if scenario.get("id") == scenario_id:
            return scenario
    
    logger.warning(f"Scenario with ID '{scenario_id}' not found")
    return None

def get_scenario_by_difficulty(difficulty: str) -> Optional[Dict[str, Any]]:
    """
    Get a random scenario of the specified difficulty.
    
    Args:
        difficulty: Difficulty level (easy, medium, hard, expert)
        
    Returns:
        Scenario dictionary or None if none available
    """
    matching_scenarios = [s for s in DEFAULT_SCENARIOS if s.get("difficulty") == difficulty]
    
    if not matching_scenarios:
        logger.warning(f"No scenarios found with difficulty '{difficulty}'")
        return None
    
    return random.choice(matching_scenarios)

def get_training_scenarios() -> List[Dict[str, Any]]:
    """
    Get scenarios specifically designed for training sessions.
    
    Returns:
        List of training scenario dictionaries
    """
    return [s for s in DEFAULT_SCENARIOS if s.get("type") == "training_session"]

def generate_custom_scenario(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a custom scenario based on provided parameters.
    
    Args:
        params: Parameters for scenario generation
        
    Returns:
        Generated scenario dictionary
    """
    scenario_type = params.get("type", "attack_simulation")
    attack_type = params.get("attack_type", "reconnaissance")
    difficulty = params.get("difficulty", "medium")
    
    # Base scenario template
    scenario = {
        "id": f"custom_{scenario_type}_{attack_type}_{int(random.random() * 10000)}",
        "name": params.get("name", f"Custom {attack_type.title()} Scenario"),
        "description": params.get("description", f"Custom scenario simulating {attack_type} activities"),
        "type": scenario_type,
        "difficulty": difficulty,
        "max_steps": params.get("max_steps", 100),
        "network_params": {},
        "attack_params": {},
        "learning_objectives": params.get("learning_objectives", [
            f"Practice responding to {attack_type} scenarios",
            "Improve detection and mitigation capabilities"
        ])
    }
    
    # Set network parameters based on difficulty
    if difficulty == "easy":
        scenario["network_params"] = {
            "server_count": random.randint(3, 6),
            "endpoint_count": random.randint(5, 12),
            "malicious_ratio": random.uniform(0.05, 0.1),
            "traffic_rate": random.randint(3, 5),
            "attack_probability": random.uniform(0.7, 0.9)
        }
    elif difficulty == "medium":
        scenario["network_params"] = {
            "server_count": random.randint(6, 10),
            "endpoint_count": random.randint(12, 20),
            "malicious_ratio": random.uniform(0.1, 0.15),
            "traffic_rate": random.randint(5, 8),
            "attack_probability": random.uniform(0.8, 1.0)
        }
    elif difficulty == "hard":
        scenario["network_params"] = {
            "server_count": random.randint(8, 15),
            "endpoint_count": random.randint(15, 30),
            "malicious_ratio": random.uniform(0.15, 0.2),
            "traffic_rate": random.randint(8, 12),
            "attack_probability": 1.0
        }
    else:  # expert
        scenario["network_params"] = {
            "server_count": random.randint(10, 20),
            "endpoint_count": random.randint(20, 40),
            "malicious_ratio": random.uniform(0.2, 0.3),
            "traffic_rate": random.randint(10, 15),
            "attack_probability": 1.0
        }
    
    # Override with any provided network params
    if "network_params" in params:
        scenario["network_params"].update(params["network_params"])
    
    # Set attack parameters
    target_systems = params.get("target_systems", [
        {"type": "server", "os": "Linux", "services": [{"name": "http", "port": 80}, {"name": "ssh", "port": 22}]},
        {"type": "endpoint", "os": "Windows 10", "services": []}
    ])
    
    # Generate defense measures based on difficulty
    defense_level = {"easy": 0.3, "medium": 0.5, "hard": 0.7, "expert": 0.8}.get(difficulty, 0.5)
    
    defense_measures = {
        "firewall_rules": defense_level * random.uniform(0.8, 1.2),
        "ids_configuration": defense_level * random.uniform(0.8, 1.2),
        "patch_management": defense_level * random.uniform(0.7, 1.1),
        "endpoint_protection": defense_level * random.uniform(0.7, 1.1)
    }
    
    # Add attack-specific defenses
    if attack_type == "ransomware":
        defense_measures["backup_systems"] = defense_level * random.uniform(0.8, 1.2)
    elif attack_type == "data_exfiltration":
        defense_measures["data_encryption"] = defense_level * random.uniform(0.8, 1.2)
        defense_measures["network_segmentation"] = defense_level * random.uniform(0.8, 1.2)
    elif attack_type == "ddos":
        defense_measures["ddos_protection"] = defense_level * random.uniform(0.8, 1.2)
    elif attack_type == "web_app_attack":
        defense_measures["web_application_firewall"] = defense_level * random.uniform(0.8, 1.2)
    
    scenario["attack_params"] = {
        "attack_type": attack_type,
        "target_systems": target_systems,
        "defense_measures": defense_measures
    }
    
    # Override with any provided attack params
    if "attack_params" in params:
        scenario["attack_params"].update(params["attack_params"])
    
    logger.info(f"Generated custom scenario: {scenario['name']}")
    
    return scenario
