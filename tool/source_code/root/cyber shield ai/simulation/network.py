import logging
import random
import time
import ipaddress
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NetworkSimulator:
    """
    Simulates network traffic and events for cybersecurity training and testing.
    Generates realistic network traffic patterns, including both normal and malicious traffic.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the network simulator.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        
        # Network configuration
        self.internal_network = ipaddress.IPv4Network('192.168.1.0/24')
        self.external_networks = [
            ipaddress.IPv4Network('203.0.113.0/24'),  # TEST-NET-3 (documentation)
            ipaddress.IPv4Network('198.51.100.0/24'), # TEST-NET-2 (documentation)
            ipaddress.IPv4Network('192.0.2.0/24')     # TEST-NET-1 (documentation)
        ]
        
        # Infrastructure components
        self.servers = []
        self.endpoints = []
        self.threat_actors = []
        
        # Traffic parameters
        self.baseline_traffic_rate = 5  # packets per step
        self.traffic_variance = 0.3     # variance in traffic rate
        self.malicious_traffic_ratio = 0.0  # ratio of malicious to normal traffic
        
        # Common protocols and ports
        self.protocols = ['tcp', 'udp', 'http', 'https', 'dns', 'smtp', 'ssh', 'ftp']
        self.common_ports = {
            'http': 80,
            'https': 443,
            'dns': 53,
            'smtp': 25,
            'ssh': 22,
            'ftp': 21,
            'telnet': 23
        }
        
        # Attack patterns (populated during reset)
        self.attack_patterns = []
        
        # Traffic history
        self.traffic_history = []
        self.max_history = 1000
        
        # Initialize with default configuration
        self.reset()
        
        logger.debug("Network simulator initialized")
    
    def reset(self, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Reset the network simulator with new parameters.
        
        Args:
            params: Optional parameters to configure the simulation
        """
        config = params or {}
        
        # Update basic parameters
        self.malicious_traffic_ratio = config.get('malicious_ratio', 0.05)
        self.baseline_traffic_rate = config.get('traffic_rate', 5)
        
        # Generate infrastructure
        self._generate_infrastructure(config)
        
        # Generate attack patterns
        self._generate_attack_patterns(config)
        
        # Reset traffic history
        self.traffic_history = []
        
        logger.info(f"Network simulator reset with malicious ratio: {self.malicious_traffic_ratio}")
    
    def _generate_infrastructure(self, config: Dict[str, Any]) -> None:
        """
        Generate network infrastructure components.
        
        Args:
            config: Configuration parameters
        """
        # Generate servers
        server_count = config.get('server_count', 5)
        self.servers = []
        
        for i in range(server_count):
            ip = str(list(self.internal_network.hosts())[i])
            server = {
                'ip': ip,
                'name': f"server-{i+1}",
                'services': self._generate_services(),
                'os': random.choice(['Linux', 'Windows Server']),
                'vulnerability_count': random.randint(0, 3)
            }
            self.servers.append(server)
        
        # Generate endpoints
        endpoint_count = config.get('endpoint_count', 10)
        self.endpoints = []
        
        for i in range(endpoint_count):
            ip = str(list(self.internal_network.hosts())[i + server_count])
            endpoint = {
                'ip': ip,
                'name': f"endpoint-{i+1}",
                'os': random.choice(['Windows 10', 'Windows 11', 'MacOS', 'Linux']),
                'user': f"user-{i+1}",
                'vulnerability_count': random.randint(0, 2)
            }
            self.endpoints.append(endpoint)
        
        # Generate threat actors
        threat_actor_count = config.get('threat_actor_count', 3)
        self.threat_actors = []
        
        for i in range(threat_actor_count):
            external_net = random.choice(self.external_networks)
            ip = str(random.choice(list(external_net.hosts())))
            actor = {
                'ip': ip,
                'name': f"threat-actor-{i+1}",
                'sophistication': random.uniform(0.3, 0.9),
                'preferred_techniques': random.sample([
                    'reconnaissance', 'exploitation', 'lateral_movement', 
                    'data_exfiltration', 'persistence'
                ], k=random.randint(2, 4))
            }
            self.threat_actors.append(actor)
    
    def _generate_services(self) -> List[Dict[str, Any]]:
        """
        Generate a list of services for a server.
        
        Returns:
            List of service dictionaries
        """
        service_count = random.randint(1, 4)
        available_services = list(self.common_ports.items())
        selected_services = random.sample(available_services, min(service_count, len(available_services)))
        
        services = []
        for name, port in selected_services:
            service = {
                'name': name,
                'port': port,
                'version': f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                'is_vulnerable': random.random() < 0.3
            }
            services.append(service)
        
        return services
    
    def _generate_attack_patterns(self, config: Dict[str, Any]) -> None:
        """
        Generate attack patterns for the simulation.
        
        Args:
            config: Configuration parameters
        """
        # Attack types and their characteristics
        attack_types = {
            'port_scan': {
                'duration': random.randint(3, 8),
                'intensity': random.uniform(0.4, 0.8),
                'target_selection': 'sequential',
                'port_pattern': 'sequential'
            },
            'brute_force': {
                'duration': random.randint(5, 12),
                'intensity': random.uniform(0.5, 0.9),
                'target_selection': 'single',
                'target_service': random.choice(['ssh', 'ftp', 'smtp'])
            },
            'data_exfiltration': {
                'duration': random.randint(2, 5),
                'intensity': random.uniform(0.2, 0.6),
                'target_selection': 'single',
                'data_volume': random.randint(1000, 50000)
            },
            'ddos': {
                'duration': random.randint(4, 10),
                'intensity': random.uniform(0.7, 1.0),
                'target_selection': 'single',
                'attack_vector': random.choice(['syn_flood', 'udp_flood', 'http_flood'])
            }
        }
        
        # Generate attack instances
        attack_probability = config.get('attack_probability', 0.3)
        self.attack_patterns = []
        
        if random.random() < attack_probability:
            # Select one or more attack types
            attack_count = random.randint(1, 3)
            selected_attacks = random.sample(list(attack_types.keys()), min(attack_count, len(attack_types)))
            
            for attack_name in selected_attacks:
                attack_config = attack_types[attack_name]
                
                # Select target(s)
                if attack_config['target_selection'] == 'single':
                    targets = [random.choice(self.servers)]
                elif attack_config['target_selection'] == 'multiple':
                    target_count = random.randint(2, min(4, len(self.servers)))
                    targets = random.sample(self.servers, target_count)
                else:  # sequential
                    targets = self.servers.copy()
                    random.shuffle(targets)
                
                # Create attack pattern
                attack = {
                    'type': attack_name,
                    'start_step': random.randint(10, 30),
                    'duration': attack_config['duration'],
                    'intensity': attack_config['intensity'],
                    'targets': targets,
                    'source': random.choice(self.threat_actors),
                    'config': attack_config
                }
                
                self.attack_patterns.append(attack)
                
                logger.debug(f"Generated attack pattern: {attack_name} targeting {len(targets)} servers")
    
    def generate_traffic(self, step: int) -> List[Dict[str, Any]]:
        """
        Generate network traffic for a simulation step.
        
        Args:
            step: The current simulation step
            
        Returns:
            List of network traffic records
        """
        # Determine baseline traffic amount for this step
        base_amount = self.baseline_traffic_rate
        variance = random.uniform(-self.traffic_variance, self.traffic_variance)
        traffic_amount = max(1, int(base_amount * (1 + variance)))
        
        # Check for active attacks
        active_attacks = [
            a for a in self.attack_patterns 
            if a['start_step'] <= step < (a['start_step'] + a['duration'])
        ]
        
        # Increase traffic for active attacks
        for attack in active_attacks:
            attack_traffic = int(base_amount * attack['intensity'] * random.uniform(0.8, 1.2))
            traffic_amount += attack_traffic
        
        # Generate traffic records
        traffic_records = []
        
        # Generate normal traffic
        normal_amount = traffic_amount
        if active_attacks:
            # Reduce normal traffic slightly during attacks
            normal_amount = max(1, int(normal_amount * 0.8))
        
        for _ in range(normal_amount):
            traffic_records.append(self._generate_normal_traffic())
        
        # Generate attack traffic
        for attack in active_attacks:
            attack_records = self._generate_attack_traffic(attack, step)
            traffic_records.extend(attack_records)
        
        # Add random malicious traffic (outside of specific attack patterns)
        if random.random() < self.malicious_traffic_ratio and not active_attacks:
            malicious_count = max(1, int(traffic_amount * self.malicious_traffic_ratio))
            for _ in range(malicious_count):
                traffic_records.append(self._generate_malicious_traffic())
        
        # Add to history (with size limit)
        self.traffic_history.extend(traffic_records)
        if len(self.traffic_history) > self.max_history:
            self.traffic_history = self.traffic_history[-self.max_history:]
        
        return traffic_records
    
    def _generate_normal_traffic(self) -> Dict[str, Any]:
        """
        Generate a normal (benign) network traffic record.
        
        Returns:
            Dictionary representing a network traffic record
        """
        # Randomly select source and destination
        internal_hosts = self.endpoints + self.servers
        
        if random.random() < 0.7:  # Internal to internal
            source = random.choice(internal_hosts)
            destination = random.choice(internal_hosts)
            while destination == source:
                destination = random.choice(internal_hosts)
            
            source_ip = source['ip']
            dest_ip = destination['ip']
        else:  # External to internal or vice versa
            if random.random() < 0.5:  # External to internal
                external_net = random.choice(self.external_networks)
                source_ip = str(random.choice(list(external_net.hosts())))
                destination = random.choice(internal_hosts)
                dest_ip = destination['ip']
            else:  # Internal to external
                source = random.choice(internal_hosts)
                source_ip = source['ip']
                external_net = random.choice(self.external_networks)
                dest_ip = str(random.choice(list(external_net.hosts())))
        
        # Select protocol and port
        protocol = random.choice(self.protocols)
        port = self.common_ports.get(protocol, random.randint(1024, 65535))
        
        # Generate payload size
        if protocol in ['http', 'https']:
            payload_size = random.randint(200, 8000)
        elif protocol in ['dns']:
            payload_size = random.randint(40, 300)
        else:
            payload_size = random.randint(50, 2000)
        
        # Create traffic record
        traffic = {
            'source_ip': source_ip,
            'destination_ip': dest_ip,
            'protocol': protocol,
            'port': port,
            'payload_size': payload_size,
            'timestamp': datetime.now().isoformat(),
            'is_malicious': False,
            'confidence': 0.0,
            'patterns': []
        }
        
        return traffic
    
    def _generate_malicious_traffic(self) -> Dict[str, Any]:
        """
        Generate a malicious network traffic record.
        
        Returns:
            Dictionary representing a malicious network traffic record
        """
        # Select a threat actor as the source
        threat_actor = random.choice(self.threat_actors)
        source_ip = threat_actor['ip']
        
        # Select a target
        target = random.choice(self.servers + self.endpoints)
        dest_ip = target['ip']
        
        # Select protocol and port based on vulnerability
        if isinstance(target, dict) and 'services' in target:
            # Target is a server
            vulnerable_services = [s for s in target.get('services', []) if s.get('is_vulnerable', False)]
            if vulnerable_services:
                service = random.choice(vulnerable_services)
                protocol = service['name']
                port = service['port']
            else:
                protocol = random.choice(self.protocols)
                port = self.common_ports.get(protocol, random.randint(1024, 65535))
        else:
            # Target is an endpoint or doesn't have services
            protocol = random.choice(self.protocols)
            port = self.common_ports.get(protocol, random.randint(1024, 65535))
        
        # Determine malicious pattern
        pattern_types = ['command_and_control', 'data_exfiltration', 'exploit_attempt', 'reconnaissance']
        pattern = random.choice(pattern_types)
        
        # Generate payload size based on pattern
        if pattern == 'data_exfiltration':
            payload_size = random.randint(5000, 50000)
        elif pattern == 'command_and_control':
            payload_size = random.randint(100, 1000)
        elif pattern == 'exploit_attempt':
            payload_size = random.randint(500, 3000)
        else:  # reconnaissance
            payload_size = random.randint(50, 200)
        
        # Create traffic record
        traffic = {
            'source_ip': source_ip,
            'destination_ip': dest_ip,
            'protocol': protocol,
            'port': port,
            'payload_size': payload_size,
            'timestamp': datetime.now().isoformat(),
            'is_malicious': True,
            'confidence': random.uniform(0.6, 0.95),
            'patterns': [pattern]
        }
        
        return traffic
    
    def _generate_attack_traffic(self, attack: Dict[str, Any], step: int) -> List[Dict[str, Any]]:
        """
        Generate traffic records for a specific attack.
        
        Args:
            attack: Attack configuration
            step: Current simulation step
            
        Returns:
            List of traffic records for the attack
        """
        attack_type = attack['type']
        source = attack['source']
        targets = attack['targets']
        intensity = attack['intensity']
        
        # Determine how many records to generate based on attack intensity and progress
        progress = (step - attack['start_step']) / attack['duration']
        if progress < 0.3:
            # Ramp-up phase
            volume_factor = progress * 3
        elif progress > 0.7:
            # Ramp-down phase
            volume_factor = (1 - progress) * 3
        else:
            # Sustained phase
            volume_factor = 1.0
        
        record_count = max(1, int(intensity * 10 * volume_factor * random.uniform(0.8, 1.2)))
        
        # Generate attack-specific traffic
        records = []
        
        if attack_type == 'port_scan':
            records = self._generate_port_scan_traffic(source, targets, record_count, attack['config'])
        elif attack_type == 'brute_force':
            records = self._generate_brute_force_traffic(source, targets, record_count, attack['config'])
        elif attack_type == 'data_exfiltration':
            records = self._generate_exfiltration_traffic(source, targets, record_count, attack['config'])
        elif attack_type == 'ddos':
            records = self._generate_ddos_traffic(source, targets, record_count, attack['config'])
        
        return records
    
    def _generate_port_scan_traffic(self, source: Dict[str, Any], targets: List[Dict[str, Any]], 
                                   count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate traffic for a port scanning attack."""
        records = []
        
        # Determine port pattern
        port_pattern = config.get('port_pattern', 'sequential')
        
        for _ in range(count):
            target = random.choice(targets)
            
            if port_pattern == 'sequential':
                # Sequential port scanning
                port_base = random.choice([1, 22, 80, 443, 1024, 8080])
                port = port_base + random.randint(0, 20)
            else:
                # Common ports scanning
                port = random.choice(list(self.common_ports.values()))
            
            record = {
                'source_ip': source['ip'],
                'destination_ip': target['ip'],
                'protocol': random.choice(['tcp', 'udp']),
                'port': port,
                'payload_size': random.randint(40, 100),
                'timestamp': datetime.now().isoformat(),
                'is_malicious': True,
                'confidence': 0.7 + random.uniform(0, 0.2),
                'patterns': ['port_scan', 'reconnaissance']
            }
            
            records.append(record)
        
        return records
    
    def _generate_brute_force_traffic(self, source: Dict[str, Any], targets: List[Dict[str, Any]], 
                                     count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate traffic for a brute force attack."""
        records = []
        
        target_service = config.get('target_service', 'ssh')
        port = self.common_ports.get(target_service, 22)
        
        for _ in range(count):
            target = random.choice(targets)
            
            record = {
                'source_ip': source['ip'],
                'destination_ip': target['ip'],
                'protocol': target_service,
                'port': port,
                'payload_size': random.randint(200, 500),
                'timestamp': datetime.now().isoformat(),
                'is_malicious': True,
                'confidence': 0.8 + random.uniform(0, 0.15),
                'patterns': ['brute_force', 'authentication_attack']
            }
            
            records.append(record)
        
        return records
    
    def _generate_exfiltration_traffic(self, source: Dict[str, Any], targets: List[Dict[str, Any]], 
                                      count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate traffic for a data exfiltration attack."""
        records = []
        
        data_volume = config.get('data_volume', 10000)
        
        # Split the data volume across multiple records
        volume_per_record = data_volume / max(1, count)
        
        for _ in range(count):
            target = random.choice(targets)
            
            record = {
                'source_ip': target['ip'],  # Exfiltrating FROM target
                'destination_ip': source['ip'],  # TO attacker
                'protocol': random.choice(['https', 'dns', 'smtp']),
                'port': random.choice([443, 53, 25]),
                'payload_size': int(volume_per_record * random.uniform(0.8, 1.2)),
                'timestamp': datetime.now().isoformat(),
                'is_malicious': True,
                'confidence': 0.75 + random.uniform(0, 0.2),
                'patterns': ['data_exfiltration', 'data_theft']
            }
            
            records.append(record)
        
        return records
    
    def _generate_ddos_traffic(self, source: Dict[str, Any], targets: List[Dict[str, Any]], 
                              count: int, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate traffic for a DDoS attack."""
        records = []
        
        attack_vector = config.get('attack_vector', 'syn_flood')
        
        # For DDoS, generate traffic from multiple sources
        external_nets = self.external_networks.copy()
        
        for _ in range(count):
            target = random.choice(targets)
            
            # Use a different source IP for each record
            external_net = random.choice(external_nets)
            source_ip = str(random.choice(list(external_net.hosts())))
            
            # Set protocol and port based on attack vector
            if attack_vector == 'syn_flood':
                protocol = 'tcp'
                port = random.choice([80, 443, 8080])
                payload_size = random.randint(40, 100)
            elif attack_vector == 'udp_flood':
                protocol = 'udp'
                port = random.randint(1, 65535)
                payload_size = random.randint(300, 1200)
            else:  # http_flood
                protocol = random.choice(['http', 'https'])
                port = 443 if protocol == 'https' else 80
                payload_size = random.randint(800, 2000)
            
            record = {
                'source_ip': source_ip,
                'destination_ip': target['ip'],
                'protocol': protocol,
                'port': port,
                'payload_size': payload_size,
                'timestamp': datetime.now().isoformat(),
                'is_malicious': True,
                'confidence': 0.85 + random.uniform(0, 0.1),
                'patterns': ['ddos', attack_vector]
            }
            
            records.append(record)
        
        return records
    
    def get_infrastructure(self) -> Dict[str, Any]:
        """
        Get information about the simulated infrastructure.
        
        Returns:
            Dictionary with infrastructure details
        """
        return {
            'servers': self.servers,
            'endpoints': self.endpoints,
            'threat_actors': self.threat_actors
        }
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the generated traffic.
        
        Returns:
            Dictionary with traffic statistics
        """
        if not self.traffic_history:
            return {
                'total_traffic': 0,
                'malicious_ratio': 0,
                'protocol_distribution': {},
                'source_ips': 0,
                'destination_ips': 0
            }
        
        # Calculate basic stats
        total_traffic = len(self.traffic_history)
        malicious_count = sum(1 for t in self.traffic_history if t.get('is_malicious', False))
        malicious_ratio = malicious_count / total_traffic if total_traffic > 0 else 0
        
        # Protocol distribution
        protocols = {}
        for traffic in self.traffic_history:
            protocol = traffic.get('protocol', 'unknown')
            protocols[protocol] = protocols.get(protocol, 0) + 1
        
        protocol_distribution = {p: count / total_traffic for p, count in protocols.items()}
        
        # Unique IPs
        source_ips = set(t.get('source_ip', '') for t in self.traffic_history)
        destination_ips = set(t.get('destination_ip', '') for t in self.traffic_history)
        
        return {
            'total_traffic': total_traffic,
            'malicious_count': malicious_count,
            'malicious_ratio': malicious_ratio,
            'protocol_distribution': protocol_distribution,
            'source_ips': len(source_ips),
            'destination_ips': len(destination_ips)
        }
