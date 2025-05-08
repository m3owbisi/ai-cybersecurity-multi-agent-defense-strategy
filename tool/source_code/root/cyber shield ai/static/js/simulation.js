/**
 * simulation.js - Simulation functionality for the cybersecurity platform
 */

let networkInstance = null;
let simulationRunning = false;

// Initialize simulation components when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Set up event handlers for simulation controls
    setupSimulationControls();
});

/**
 * Set up event handlers for the simulation controls
 */
function setupSimulationControls() {
    // Start simulation button
    const startButton = document.getElementById('start-simulation-btn');
    if (startButton) {
        startButton.addEventListener('click', startSimulation);
    }
    
    // Reset simulation button
    const resetButton = document.getElementById('reset-simulation-btn');
    if (resetButton) {
        resetButton.addEventListener('click', resetSimulation);
    }
    
    // View toggle buttons
    document.querySelectorAll('.view-toggle-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.view-toggle-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // Handle view switching logic
            toggleVisualizationView(this.getAttribute('data-view'));
        });
    });
    
    // Scenario selection change
    const scenarioSelect = document.getElementById('scenario-select');
    if (scenarioSelect) {
        scenarioSelect.addEventListener('change', updateSimulationOptions);
    }
}

/**
 * Start the simulation with the selected parameters
 */
function startSimulation() {
    if (simulationRunning) {
        pauseSimulation();
        return;
    }
    
    // Get selected simulation parameters
    const scenario = document.getElementById('scenario-select').value;
    const difficulty = document.getElementById('difficulty-select').value;
    const targets = Array.from(document.getElementById('target-select').selectedOptions).map(option => option.value);
    
    // Validate selections
    if (targets.length === 0) {
        showToast('Please select at least one target system.', 'Validation Error', 'warning');
        return;
    }
    
    // Update UI to show loading state
    const startButton = document.getElementById('start-simulation-btn');
    startButton.disabled = true;
    startButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...';
    
    // Clear previous simulation logs and data
    resetSimulationLogs();
    
    // Initialize the network visualization if not already
    initNetworkVisualization();
    
    // Simulate loading delay
    setTimeout(() => {
        // Update button and state
        startButton.innerHTML = '<i class="bi bi-pause-fill"></i> Pause Simulation';
        startButton.disabled = false;
        document.getElementById('reset-simulation-btn').disabled = false;
        simulationRunning = true;
        
        // Start the simulation sequence
        runSimulation(scenario, difficulty, targets);
        
        // Show toast notification
        showToast(`Starting ${formatScenarioName(scenario)} simulation on ${difficulty} difficulty.`, 'Simulation', 'info');
    }, 1500);
}

/**
 * Pause the current simulation
 */
function pauseSimulation() {
    // Toggle simulation state
    simulationRunning = false;
    
    // Update button
    const startButton = document.getElementById('start-simulation-btn');
    startButton.innerHTML = '<i class="bi bi-play-fill"></i> Resume Simulation';
    
    // Show toast notification
    showToast('Simulation paused. Click Resume to continue.', 'Simulation', 'warning');
}

/**
 * Reset the simulation to its initial state
 */
function resetSimulation() {
    // Stop any running simulation
    simulationRunning = false;
    
    // Reset UI elements
    const startButton = document.getElementById('start-simulation-btn');
    startButton.innerHTML = '<i class="bi bi-play-fill"></i> Start Simulation';
    startButton.disabled = false;
    
    document.getElementById('reset-simulation-btn').disabled = true;
    
    // Reset logs and defense table
    resetSimulationLogs();
    
    // Reset network visualization
    resetNetworkVisualization();
    
    // Show toast notification
    showToast('Simulation reset successfully.', 'Simulation', 'success');
}

/**
 * Initialize the network visualization
 */
function initNetworkVisualization() {
    const container = document.getElementById('network-visualization');
    if (!container) return;
    
    // Clear any existing content
    container.innerHTML = '';
    
    // Only initialize if not already initialized
    if (!networkInstance) {
        // Sample nodes and edges for the network
        const nodes = new vis.DataSet([
            { id: 1, label: 'Internet', shape: 'cloud', color: { background: '#6c757d', border: '#495057' } },
            { id: 2, label: 'Firewall', shape: 'box', color: { background: '#0d6efd', border: '#0a58ca' } },
            { id: 3, label: 'Web Server', shape: 'server', color: { background: '#198754', border: '#146c43' } },
            { id: 4, label: 'App Server', shape: 'server', color: { background: '#198754', border: '#146c43' } },
            { id: 5, label: 'Database', shape: 'database', color: { background: '#198754', border: '#146c43' } },
            { id: 6, label: 'Admin', shape: 'icon', icon: { face: 'FontAwesome', code: '\uf007', color: '#0dcaf0' } },
            { id: 7, label: 'Workstation 1', shape: 'desktop', color: { background: '#198754', border: '#146c43' } },
            { id: 8, label: 'Workstation 2', shape: 'desktop', color: { background: '#198754', border: '#146c43' } }
        ]);
        
        const edges = new vis.DataSet([
            { from: 1, to: 2 },
            { from: 2, to: 3 },
            { from: 2, to: 4 },
            { from: 3, to: 5 },
            { from: 4, to: 5 },
            { from: 2, to: 6 },
            { from: 6, to: 7 },
            { from: 6, to: 8 }
        ]);
        
        // Network configuration
        const data = { nodes, edges };
        const options = {
            nodes: {
                font: {
                    color: '#ffffff',
                    face: 'Roboto'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                color: { color: '#495057', highlight: '#0d6efd' },
                smooth: { type: 'continuous' }
            },
            physics: {
                enabled: true,
                hierarchicalRepulsion: {
                    centralGravity: 0.0,
                    springLength: 150,
                    springConstant: 0.01,
                    nodeDistance: 200,
                    damping: 0.09
                },
                solver: 'hierarchicalRepulsion'
            },
            interaction: {
                hover: true,
                navigationButtons: true,
                keyboard: {
                    enabled: true,
                    bindToWindow: false
                }
            }
        };
        
        // Create the network
        networkInstance = new vis.Network(container, data, options);
        
        // Network events
        networkInstance.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                showToast(`Selected: ${node.label}`, 'Node Information', 'info');
            }
        });
    }
}

/**
 * Reset the network visualization to its initial state
 */
function resetNetworkVisualization() {
    if (!networkInstance) return;
    
    // Get all nodes and edges
    const nodes = networkInstance.body.data.nodes;
    const edges = networkInstance.body.data.edges;
    
    // Reset node colors
    nodes.forEach(node => {
        if (node.id !== 1 && node.id !== 2) { // Skip internet and firewall
            if (node.shape === 'server' || node.shape === 'desktop' || node.shape === 'database') {
                nodes.update({
                    id: node.id,
                    color: { background: '#198754', border: '#146c43' }
                });
            } else if (node.shape === 'icon') {
                nodes.update({
                    id: node.id,
                    color: { background: '#ffffff', border: '#0dcaf0' }
                });
            }
        }
    });
    
    // Reset edge colors
    edges.forEach(edge => {
        edges.update({
            id: edge.id,
            color: { color: '#495057' },
            dashes: false
        });
    });
}

/**
 * Toggle between different visualization views (network, tree, etc.)
 * @param {string} viewType - Type of view to display
 */
function toggleVisualizationView(viewType) {
    // Implementation for switching views
    if (viewType === 'tree') {
        showToast('Attack tree view is not implemented in this demo.', 'View Change', 'info');
    }
}

/**
 * Reset the simulation logs and defense table
 */
function resetSimulationLogs() {
    const log = document.getElementById('simulation-log');
    if (log) {
        log.innerHTML = `<div class="p-4 text-center">
            <i class="bi bi-clock-history text-muted mb-2" style="font-size: 2rem;"></i>
            <p>Events will appear here once simulation starts</p>
        </div>`;
    }
    
    const defenseTable = document.getElementById('defense-table');
    if (defenseTable) {
        const tbody = defenseTable.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = `<tr>
                <td colspan="4" class="text-center">
                    <p class="my-4 text-muted">Defense actions will appear here during simulation</p>
                </td>
            </tr>`;
        }
    }
    
    const eventCounter = document.getElementById('event-counter');
    if (eventCounter) {
        eventCounter.textContent = '0';
    }
}

/**
 * Update simulation options based on the selected scenario
 */
function updateSimulationOptions() {
    const scenario = document.getElementById('scenario-select').value;
    
    // Set default targets based on scenario
    const targetSelect = document.getElementById('target-select');
    if (targetSelect) {
        // Reset selections
        Array.from(targetSelect.options).forEach(option => {
            option.selected = false;
        });
        
        // Select appropriate targets based on scenario
        switch (scenario) {
            case 'ransomware':
                selectOptionsByValues(targetSelect, ['endpoints', 'databases']);
                break;
            case 'phishing':
                selectOptionsByValues(targetSelect, ['endpoints']);
                break;
            case 'ddos':
                selectOptionsByValues(targetSelect, ['web_servers', 'network']);
                break;
            case 'data_exfiltration':
                selectOptionsByValues(targetSelect, ['databases', 'endpoints']);
                break;
            case 'supply_chain':
                selectOptionsByValues(targetSelect, ['web_servers', 'endpoints']);
                break;
        }
    }
}

/**
 * Helper function to select options in a select element by their values
 * @param {HTMLSelectElement} selectElement - The select element
 * @param {Array<string>} values - Array of values to select
 */
function selectOptionsByValues(selectElement, values) {
    if (!selectElement || !values) return;
    
    Array.from(selectElement.options).forEach(option => {
        if (values.includes(option.value)) {
            option.selected = true;
        }
    });
}

/**
 * Format a scenario ID into a human-readable name
 * @param {string} scenarioId - The scenario ID
 * @returns {string} - Formatted scenario name
 */
function formatScenarioName(scenarioId) {
    if (!scenarioId) return 'Unknown';
    
    // Split by underscore and capitalize each word
    return scenarioId
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Run the simulation with the selected parameters
 * @param {string} scenario - Selected scenario
 * @param {string} difficulty - Selected difficulty
 * @param {Array<string>} targets - Selected targets
 */
function runSimulation(scenario, difficulty, targets) {
    // In a real implementation, this would call the API to start a simulation
    console.log('Running simulation with:', { scenario, difficulty, targets });
    
    // For the demo, we'll simulate the events
    
    // Different events based on scenario
    const events = getScenarioEvents(scenario);
    
    // Add events to the log with a delay between each
    let eventCount = 0;
    let i = 0;
    
    const interval = setInterval(() => {
        if (!simulationRunning) {
            // Pause the simulation if paused
            return;
        }
        
        if (i >= events.length) {
            clearInterval(interval);
            
            // Show completion
            setTimeout(() => {
                simulationCompleted();
            }, 1000);
            return;
        }
        
        // Add the event
        addSimulationEvent(events[i], eventCount);
        
        // Update event counter
        eventCount++;
        const eventCounter = document.getElementById('event-counter');
        if (eventCounter) {
            eventCounter.textContent = eventCount;
        }
        
        i++;
    }, 500);
    
    // Update the network visualization based on scenario
    updateNetworkForScenario(scenario);
}

/**
 * Add a simulation event to the log
 * @param {Object} event - Event data
 * @param {number} eventCount - Current event count
 */
function addSimulationEvent(event, eventCount) {
    const log = document.getElementById('simulation-log');
    if (!log) return;
    
    // Create event item
    const eventItem = document.createElement('div');
    eventItem.className = 'event-item';
    
    // Format based on event type
    let typeClass = '';
    switch (event.type) {
        case 'attack':
            typeClass = 'event-type-attack';
            break;
        case 'defense':
            typeClass = 'event-type-defense';
            break;
        case 'network':
            typeClass = 'event-type-network';
            break;
        default:
            typeClass = 'event-type-alert';
    }
    
    eventItem.innerHTML = `
        <span class="event-time">[${event.time}]</span>
        <span class="${typeClass}">${event.type.toUpperCase()}:</span> ${event.message}
    `;
    
    log.appendChild(eventItem);
    log.scrollTop = log.scrollHeight;
    
    // If defense event, also add to defense table
    if (event.type === 'defense' && event.defense) {
        addDefenseAction(event);
    }
}

/**
 * Add a defense action to the defense table
 * @param {Object} event - Defense event data
 */
function addDefenseAction(event) {
    const defenseTable = document.getElementById('defense-table');
    if (!defenseTable) return;
    
    const tbody = defenseTable.querySelector('tbody');
    if (!tbody) return;
    
    // Remove placeholder row if present
    if (tbody.querySelector('td[colspan="4"]')) {
        tbody.innerHTML = '';
    }
    
    // Create new row
    const row = document.createElement('tr');
    
    // Determine effectiveness badge color
    let badgeClass = 'bg-warning';
    if (event.effectiveness === 'High') {
        badgeClass = 'bg-success';
    } else if (event.effectiveness === 'Low') {
        badgeClass = 'bg-danger';
    }
    
    row.innerHTML = `
        <td>${event.time}</td>
        <td>${determineAttackVector(event.message)}</td>
        <td>${event.defense}</td>
        <td><span class="badge ${badgeClass}">${event.effectiveness}</span></td>
    `;
    
    tbody.appendChild(row);
}

/**
 * Determine attack vector based on message
 * @param {string} message - Event message
 * @returns {string} - Attack vector
 */
function determineAttackVector(message) {
    if (message.includes('phishing')) return 'Phishing';
    if (message.includes('malicious attachment')) return 'Malicious Attachment';
    if (message.includes('command and control')) return 'C2 Communication';
    if (message.includes('escalate privileges')) return 'Privilege Escalation';
    if (message.includes('lateral movement')) return 'Lateral Movement';
    if (message.includes('file access')) return 'Unauthorized Access';
    if (message.includes('encryption')) return 'Encryption';
    if (message.includes('DDoS')) return 'DDoS';
    if (message.includes('SQL')) return 'SQL Injection';
    if (message.includes('exfiltration')) return 'Data Exfiltration';
    return 'Unknown';
}

/**
 * Get events for a specific scenario
 * @param {string} scenario - Scenario ID
 * @returns {Array<Object>} - Array of events
 */
function getScenarioEvents(scenario) {
    // Default to ransomware events if scenario not found
    switch (scenario) {
        case 'ransomware':
            return [
                { time: '00:00', type: 'attack', message: 'Initial access attempt detected via phishing email with malicious attachment' },
                { time: '00:05', type: 'defense', message: 'Email filtering identified suspicious attachment pattern', defense: 'Email scanning', effectiveness: 'Medium' },
                { time: '00:10', type: 'attack', message: 'User opened malicious attachment on Workstation 2' },
                { time: '00:12', type: 'attack', message: 'Malware establishes connection to command and control server' },
                { time: '00:15', type: 'defense', message: 'Unusual network connection attempt detected', defense: 'Network monitoring', effectiveness: 'High' },
                { time: '00:18', type: 'defense', message: 'Connection to known malicious IP blocked', defense: 'Firewall rule', effectiveness: 'High' },
                { time: '00:25', type: 'attack', message: 'Malware attempting to escalate privileges on Workstation 2' },
                { time: '00:30', type: 'attack', message: 'Lateral movement attempt detected from Workstation 2 to Admin machine' },
                { time: '00:35', type: 'defense', message: 'Lateral movement partially blocked', defense: 'Network segmentation', effectiveness: 'Medium' },
                { time: '00:40', type: 'attack', message: 'Ransomware payload trying to access file shares' },
                { time: '00:42', type: 'defense', message: 'Abnormal file access pattern detected', defense: 'Behavior analysis', effectiveness: 'High' },
                { time: '00:45', type: 'defense', message: 'File encryption attempt blocked on network shares', defense: 'Access control', effectiveness: 'High' },
                { time: '00:50', type: 'attack', message: 'Encryption of local files in progress on Workstation 2' },
                { time: '00:55', type: 'defense', message: 'Process terminated based on behavior pattern', defense: 'Endpoint protection', effectiveness: 'Medium' },
                { time: '01:00', type: 'network', message: 'Isolating Workstation 2 from network to prevent further spread' },
                { time: '01:05', type: 'defense', message: 'System restoration from backup initiated for Workstation 2', defense: 'Recovery protocol', effectiveness: 'High' }
            ];
            
        case 'ddos':
            return [
                { time: '00:00', type: 'network', message: 'Unusual increase in traffic detected on external interfaces' },
                { time: '00:05', type: 'attack', message: 'Potential DDoS attack starting - SYN flood pattern detected' },
                { time: '00:08', type: 'defense', message: 'Rate limiting applied to suspicious traffic sources', defense: 'Traffic shaping', effectiveness: 'Medium' },
                { time: '00:12', type: 'attack', message: 'Attack ramping up - multiple attack vectors detected' },
                { time: '00:15', type: 'network', message: 'Web servers experiencing increased load' },
                { time: '00:18', type: 'defense', message: 'Traffic analysis identifies botnet sources', defense: 'Threat intelligence', effectiveness: 'High' },
                { time: '00:22', type: 'attack', message: 'Layer 7 attack targeting authentication endpoints' },
                { time: '00:25', type: 'defense', message: 'Web application firewall rules updated', defense: 'WAF rules', effectiveness: 'High' },
                { time: '00:30', type: 'network', message: 'Activating additional capacity to absorb attack' },
                { time: '00:35', type: 'defense', message: 'DDoS mitigation service engaged', defense: 'Cloud mitigation', effectiveness: 'High' },
                { time: '00:40', type: 'attack', message: 'Attack shifting to DNS amplification' },
                { time: '00:45', type: 'defense', message: 'DNS filtering implemented', defense: 'DNS protection', effectiveness: 'Medium' },
                { time: '00:50', type: 'network', message: 'Traffic levels beginning to normalize' },
                { time: '00:55', type: 'defense', message: 'Blocking traffic from 150 identified attack sources', defense: 'IP blocking', effectiveness: 'High' },
                { time: '01:00', type: 'network', message: 'Service availability restored to normal levels' },
                { time: '01:05', type: 'defense', message: 'Post-attack analysis and rule optimization initiated', defense: 'Forensics', effectiveness: 'High' }
            ];
            
        case 'data_exfiltration':
            return [
                { time: '00:00', type: 'attack', message: 'Suspicious login detected from unusual location' },
                { time: '00:05', type: 'defense', message: 'Multi-factor authentication challenge issued', defense: 'MFA', effectiveness: 'High' },
                { time: '00:10', type: 'attack', message: 'Authentication bypass attempt detected' },
                { time: '00:15', type: 'attack', message: 'Privilege escalation observed via service account compromise' },
                { time: '00:20', type: 'defense', message: 'Unusual account behavior detected', defense: 'Behavior monitoring', effectiveness: 'Medium' },
                { time: '00:25', type: 'attack', message: 'Database query with excessive data retrieval executed' },
                { time: '00:30', type: 'defense', message: 'Database activity monitoring alert triggered', defense: 'DAM', effectiveness: 'High' },
                { time: '00:35', type: 'attack', message: 'Data staging observed in temporary directory' },
                { time: '00:40', type: 'network', message: 'Unusual outbound connection established to unknown external IP' },
                { time: '00:45', type: 'defense', message: 'Data Loss Prevention system blocked file transfer', defense: 'DLP', effectiveness: 'High' },
                { time: '00:50', type: 'attack', message: 'Attempt to compress and encrypt sensitive data detected' },
                { time: '00:55', type: 'defense', message: 'File integrity monitoring alert triggered', defense: 'FIM', effectiveness: 'Medium' },
                { time: '01:00', type: 'network', message: 'Suspicious DNS queries detected - potential covert channel' },
                { time: '01:05', type: 'defense', message: 'DNS exfiltration blocked via pattern matching', defense: 'DNS filters', effectiveness: 'High' },
                { time: '01:10', type: 'defense', message: 'Account access revoked and investigation initiated', defense: 'Access control', effectiveness: 'High' },
                { time: '01:15', type: 'defense', message: 'Security team performed isolation of affected systems', defense: 'Containment', effectiveness: 'High' }
            ];
            
        default:
            // Default to ransomware scenario
            return [
                { time: '00:00', type: 'attack', message: 'Initial access attempt detected via phishing email with malicious attachment' },
                { time: '00:05', type: 'defense', message: 'Email filtering identified suspicious attachment pattern', defense: 'Email scanning', effectiveness: 'Medium' },
                { time: '00:10', type: 'attack', message: 'User opened malicious attachment on Workstation 2' },
                { time: '00:15', type: 'defense', message: 'Endpoint protection blocked initial execution', defense: 'Endpoint protection', effectiveness: 'High' }
            ];
    }
}

/**
 * Update the network visualization based on the selected scenario
 * @param {string} scenario - Scenario ID
 */
function updateNetworkForScenario(scenario) {
    if (!networkInstance) return;
    
    // Different visualization updates based on the scenario
    switch (scenario) {
        case 'ransomware':
            simulateRansomwareAttack();
            break;
        case 'ddos':
            simulateDDoSAttack();
            break;
        case 'data_exfiltration':
            simulateDataExfiltration();
            break;
        default:
            simulateGenericAttack();
            break;
    }
}

/**
 * Simulate a ransomware attack on the network visualization
 */
function simulateRansomwareAttack() {
    if (!networkInstance) return;
    
    // Get nodes and edges
    const nodes = networkInstance.body.data.nodes;
    const edges = networkInstance.body.data.edges;
    
    // Style for compromised nodes
    const compromisedStyle = {
        background: '#dc3545',
        border: '#b02a37'
    };
    
    // Style for at-risk nodes
    const atRiskStyle = {
        background: '#fd7e14',
        border: '#ca6510'
    };
    
    // Simulate infection progression
    setTimeout(() => {
        // Step 1: Compromise Workstation 2
        nodes.update({ id: 8, color: compromisedStyle });
    }, 2000);
    
    setTimeout(() => {
        // Step 2: Connection attempt to Admin
        edges.update([
            { id: edges.get()[6].id, color: { color: '#dc3545' } }
        ]);
        
        // Admin at risk
        nodes.update({ id: 6, color: atRiskStyle });
    }, 6000);
    
    setTimeout(() => {
        // Step 3: Partial compromise of Admin
        nodes.update({ id: 6, color: compromisedStyle });
        
        // Workstation 1 at risk
        nodes.update({ id: 7, color: atRiskStyle });
    }, 9000);
    
    setTimeout(() => {
        // Step 4: Trying to access servers
        edges.update([
            { id: edges.get()[2].id, color: { color: '#fd7e14' } },
            { id: edges.get()[3].id, color: { color: '#fd7e14' } }
        ]);
        
        // Servers at risk
        nodes.update([
            { id: 3, color: atRiskStyle },
            { id: 4, color: atRiskStyle }
        ]);
    }, 12000);
    
    setTimeout(() => {
        // Step 5: Defense response - isolate workstation 2
        edges.update([
            { id: edges.get()[6].id, color: { color: '#495057', dashes: [5, 5] } }
        ]);
    }, 15000);
    
    setTimeout(() => {
        // Step 6: Defense response - protect servers
        nodes.update([
            { id: 3, color: { background: '#198754', border: '#146c43' } },
            { id: 4, color: { background: '#198754', border: '#146c43' } }
        ]);
        
        edges.update([
            { id: edges.get()[2].id, color: { color: '#495057' } },
            { id: edges.get()[3].id, color: { color: '#495057' } }
        ]);
    }, 18000);
}

/**
 * Simulate a DDoS attack on the network visualization
 */
function simulateDDoSAttack() {
    if (!networkInstance) return;
    
    // Get nodes and edges
    const nodes = networkInstance.body.data.nodes;
    const edges = networkInstance.body.data.edges;
    
    // Style for under attack
    const underAttackStyle = {
        background: '#fd7e14',
        border: '#ca6510'
    };
    
    // Update Internet and firewall
    setTimeout(() => {
        // Step 1: Attack starts from internet
        nodes.update({ id: 1, color: { background: '#dc3545', border: '#b02a37' } });
        edges.update([{ id: edges.get()[0].id, color: { color: '#dc3545' } }]);
    }, 2000);
    
    setTimeout(() => {
        // Step 2: Firewall under pressure
        nodes.update({ id: 2, color: underAttackStyle });
    }, 4000);
    
    setTimeout(() => {
        // Step 3: Web servers impacted
        nodes.update({ id: 3, color: underAttackStyle });
        edges.update([{ id: edges.get()[1].id, color: { color: '#dc3545' } }]);
    }, 6000);
    
    setTimeout(() => {
        // Step 4: Firewall filtering attack
        edges.update([{ id: edges.get()[0].id, width: 6 }]);
    }, 9000);
    
    setTimeout(() => {
        // Step 5: Defense kicking in
        nodes.update({ id: 2, color: { background: '#0d6efd', border: '#0a58ca' } });
        edges.update([{ id: edges.get()[0].id, width: 2, color: { color: '#0d6efd' } }]);
    }, 12000);
    
    setTimeout(() => {
        // Step 6: Recovery
        nodes.update({ id: 3, color: { background: '#198754', border: '#146c43' } });
        edges.update([{ id: edges.get()[1].id, color: { color: '#495057' } }]);
    }, 15000);
}

/**
 * Simulate a data exfiltration attack on the network visualization
 */
function simulateDataExfiltration() {
    if (!networkInstance) return;
    
    // Get nodes and edges
    const nodes = networkInstance.body.data.nodes;
    const edges = networkInstance.body.data.edges;
    
    // Styles
    const compromisedStyle = {
        background: '#dc3545',
        border: '#b02a37'
    };
    
    const dataFlowStyle = {
        color: '#fd7e14',
        width: 3,
        arrows: { to: { enabled: true } }
    };
    
    // Update visualization
    setTimeout(() => {
        // Step 1: Initial access to workstation
        nodes.update({ id: 7, color: compromisedStyle });
    }, 2000);
    
    setTimeout(() => {
        // Step 2: Moving to database
        edges.update([
            { id: edges.get()[5].id, color: dataFlowStyle }
        ]);
        nodes.update({ id: 6, color: compromisedStyle });
    }, 5000);
    
    setTimeout(() => {
        // Step 3: Database access
        edges.update([
            { id: edges.get()[3].id, color: dataFlowStyle }
        ]);
        nodes.update({ id: 4, color: compromisedStyle });
    }, 8000);
    
    setTimeout(() => {
        // Step 4: Database compromise
        edges.update([
            { id: edges.get()[4].id, color: dataFlowStyle }
        ]);
        nodes.update({ id: 5, color: compromisedStyle });
    }, 11000);
    
    setTimeout(() => {
        // Step 5: Data exfiltration
        edges.update([
            { id: edges.get()[2].id, color: dataFlowStyle },
            { id: edges.get()[1].id, color: dataFlowStyle },
            { id: edges.get()[0].id, color: dataFlowStyle }
        ]);
    }, 14000);
    
    setTimeout(() => {
        // Step 6: Detection and blocking
        edges.update([
            { id: edges.get()[0].id, color: { color: '#495057' }, dashes: [5, 5] }
        ]);
        
        // Show defense happening at firewall
        nodes.update({ id: 2, color: { background: '#0d6efd', border: '#0a58ca' } });
    }, 17000);
}

/**
 * Simulate a generic attack on the network visualization
 */
function simulateGenericAttack() {
    if (!networkInstance) return;
    
    // Get nodes and edges
    const nodes = networkInstance.body.data.nodes;
    const edges = networkInstance.body.data.edges;
    
    // Compromise workstation
    setTimeout(() => {
        nodes.update({ id: 8, color: { background: '#dc3545', border: '#b02a37' } });
    }, 3000);
    
    // Defense activation
    setTimeout(() => {
        nodes.update({ id: 2, color: { background: '#0d6efd', border: '#0a58ca' } });
    }, 6000);
    
    // Restore
    setTimeout(() => {
        nodes.update({ id: 8, color: { background: '#198754', border: '#146c43' } });
    }, 9000);
}

/**
 * Called when the simulation is completed
 */
function simulationCompleted() {
    // Update UI
    simulationRunning = false;
    
    const startButton = document.getElementById('start-simulation-btn');
    if (startButton) {
        startButton.innerHTML = '<i class="bi bi-play-fill"></i> Start New Simulation';
    }
    
    // Show results
    showSimulationResults();
}

/**
 * Show the simulation results modal
 */
function showSimulationResults() {
    // Get the selected scenario for results
    const scenarioSelect = document.getElementById('scenario-select');
    const scenarioName = scenarioSelect ? scenarioSelect.options[scenarioSelect.selectedIndex].text : 'Simulation';
    
    // Calculate simulated scores
    const defenseScore = Math.floor(Math.random() * 30) + 65; // 65-95
    const attackScore = Math.floor(Math.random() * 50) + 20;  // 20-70
    
    // Update result fields
    document.getElementById('result-scenario-name').textContent = scenarioName;
    document.getElementById('result-duration').textContent = '1 minute 15 seconds';
    
    // Defense score
    document.getElementById('result-defense-progress').style.width = `${defenseScore}%`;
    document.getElementById('result-defense-score').textContent = `${defenseScore}%`;
    
    // Attack score
    document.getElementById('result-attack-progress').style.width = `${attackScore}%`;
    document.getElementById('result-attack-score').textContent = `${attackScore}%`;
    
    // Show modal
    const resultsModal = new bootstrap.Modal(document.getElementById('simulationResultsModal'));
    resultsModal.show();
}