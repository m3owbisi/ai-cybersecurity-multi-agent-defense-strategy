from dataclasses import dataclass, field
from typing import List, Dict, Any
import datetime
import uuid

# Since we're using in-memory storage for this demo, we'll use dataclasses
# instead of SQLAlchemy models

@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    is_active: bool = True
    is_admin: bool = False

@dataclass
class Alert:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: str = "low"  # low, medium, high, critical
    source: str = ""
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    is_resolved: bool = False
    resolution_notes: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkTraffic:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_ip: str = ""
    destination_ip: str = ""
    protocol: str = ""
    port: int = 0
    payload_size: int = 0
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    is_malicious: bool = False
    confidence: float = 0.0
    patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""  # intrusion, data_leak, malware, etc.
    description: str = ""
    source: str = ""
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    severity: str = "low"  # low, medium, high, critical
    affected_systems: List[str] = field(default_factory=list)
    is_resolved: bool = False
    resolution_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimulationResult:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scenario_name: str = ""
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    duration_seconds: int = 0
    success_rate: float = 0.0
    vulnerabilities_found: List[str] = field(default_factory=list)
    defense_effectiveness: float = 0.0
    offense_effectiveness: float = 0.0
    network_stats: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TrainingSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    completed_at: datetime.datetime = None
    difficulty: str = "medium"  # easy, medium, hard, expert
    scenario_type: str = ""  # phishing, ransomware, ddos, etc.
    completed_steps: List[str] = field(default_factory=list)
    score: float = 0.0
    feedback: str = ""
