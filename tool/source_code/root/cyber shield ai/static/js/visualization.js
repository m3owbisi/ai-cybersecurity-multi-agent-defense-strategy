/**
 * visualization.js - Network and data visualization functions for cybersecurity platform
 */

// Core visualization settings
const visualizationSettings = {
    network: {
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -8000,
                centralGravity: 0.6,
                springLength: 120,
                springConstant: 0.05,
                damping: 0.09
            },
            stabilization: {
                enabled: true,
                iterations: 200,
                updateInterval: 25
            }
        },
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#ffffff'
            },
            borderWidth: 2,
            shadow: true
        },
        edges: {
            width: 2,
            color: {
                color: '#848484',
                highlight: '#1778F2',
                hover: '#1778F2'
            },
            arrows: {
                to: { enabled: true, scaleFactor: 0.5 }
            },
            smooth: {
                enabled: true,
                type: 'continuous',
                roundness: 0.5
            }
        },
        groups: {
            server: {
                shape: 'dot',
                color: { background: '#0d6efd', border: '#0a58ca' },
                size: 25
            },
            client: {
                shape: 'dot',
                color: { background: '#6c757d', border: '#495057' },
                size: 18
            },
            internet: {
                shape: 'diamond',
                color: { background: '#6610f2', border: '#520dc2' },
                size: 25
            },
            attacker: {
                shape: 'triangle',
                color: { background: '#dc3545', border: '#b02a37' },
                size: 25
            },
            firewall: {
                shape: 'square',
                color: { background: '#fd7e14', border: '#d63384' },
                size: 22
            },
            router: {
                shape: 'dot',
                color: { background: '#0dcaf0', border: '#0aa2c0' },
                size: 20
            },
            database: {
                shape: 'database',
                color: { background: '#20c997', border: '#198754' },
                size: 25
            },
            iot: {
                shape: 'dot',
                color: { background: '#d63384', border: '#ab296a' },
                size: 16
            },
            malicious: {
                color: { background: '#dc3545', border: '#b02a37' }
            }
        }
    },
    timeline: {
        minHeight: '300px',
        maxHeight: '600px',
        stack: true,
        verticalScroll: true,
        zoomKey: 'ctrlKey',
        orientation: 'both'
    }
};

// Active visualization instances
const visualizationInstances = {
    networks: {},
    timelines: {},
    charts: {}
};

/**
 * Initialize a network visualization
 * @param {string} containerId - DOM element ID for the visualization container
 * @param {Object} options - Custom options to override defaults
 * @returns {vis.Network|null} - The created network instance or null on failure
 */
function initNetworkVisualization(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return null;
    }
    
    // Create datasets
    const nodes = new vis.DataSet();
    const edges = new vis.DataSet();
    
    // Merge default options with custom options
    const networkOptions = {
        ...visualizationSettings.network,
        ...options
    };
    
    try {
        // Create network
        const network = new vis.Network(container, { nodes, edges }, networkOptions);
        
        // Store the instance
        visualizationInstances.networks[containerId] = {
            network,
            nodes,
            edges
        };
        
        // Add event listeners
        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                if (node) {
                    showNodeTooltip(node, params.pointer.DOM, containerId);
                }
            }
        });
        
        network.on('hoverNode', function(params) {
            const node = nodes.get(params.node);
            if (node && node.title) {
                network.canvas.body.container.title = node.title;
            }
        });
        
        network.on('blurNode', function() {
            network.canvas.body.container.title = '';
        });
        
        return network;
    } catch (error) {
        console.error('Error initializing network visualization:', error);
        container.innerHTML = `
            <div class="alert alert-danger m-3">
                Error initializing network visualization: ${error.message}
            </div>
        `;
        return null;
    }
}

/**
 * Render a network visualization with provided nodes and edges
 * @param {string} containerId - DOM element ID for the visualization container
 * @param {Array} nodeData - Array of node objects
 * @param {Array} edgeData - Array of edge objects
 * @param {Object} options - Custom options to override defaults
 */
function renderNetworkVisualization(containerId, nodeData, edgeData, options = {}) {
    // Check if we already have a network instance
    let instance = visualizationInstances.networks[containerId];
    
    if (!instance) {
        // Initialize a new network
        const network = initNetworkVisualization(containerId, options);
        if (!network) return;
        
        instance = visualizationInstances.networks[containerId];
    }
    
    // Clear existing data
    instance.nodes.clear();
    instance.edges.clear();
    
    // Add new data
    instance.nodes.add(nodeData);
    instance.edges.add(edgeData);
    
    // Fit the network to view all nodes
    instance.network.fit();
}

/**
 * Update an existing network visualization
 * @param {string} containerId - DOM element ID for the visualization container
 * @param {Array} nodeData - Array of node objects to add or update
 * @param {Array} edgeData - Array of edge objects to add or update
 * @param {Array} removeNodeIds - Array of node IDs to remove
 * @param {Array} removeEdgeIds - Array of edge IDs to remove
 */
function updateNetworkVisualization(containerId, nodeData = [], edgeData = [], removeNodeIds = [], removeEdgeIds = []) {
    const instance = visualizationInstances.networks[containerId];
    if (!instance) {
        console.error(`Network instance not found for container: ${containerId}`);
        return;
    }
    
    // Remove nodes and edges if specified
    if (removeNodeIds.length > 0) {
        instance.nodes.remove(removeNodeIds);
    }
    
    if (removeEdgeIds.length > 0) {
        instance.edges.remove(removeEdgeIds);
    }
    
    // Update or add nodes and edges
    if (nodeData.length > 0) {
        instance.nodes.update(nodeData);
    }
    
    if (edgeData.length > 0) {
        instance.edges.update(edgeData);
    }
}

/**
 * Show a tooltip for a node
 * @param {Object} node - The node object
 * @param {Object} position - Position {x, y} for the tooltip
 * @param {string} containerId - The container ID for the network
 */
function showNodeTooltip(node, position, containerId) {
    // Check if a tooltip already exists and remove it
    const existingTooltip = document.getElementById('network-node-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // Create a tooltip element
    const tooltip = document.createElement('div');
    tooltip.id = 'network-node-tooltip';
    tooltip.className = 'network-tooltip';
    tooltip.style.position = 'absolute';
    tooltip.style.left = `${position.x + 10}px`;
    tooltip.style.top = `${position.y + 10}px`;
    tooltip.style.backgroundColor = 'rgba(40, 40, 40, 0.9)';
    tooltip.style.color = 'white';
    tooltip.style.padding = '10px';
    tooltip.style.borderRadius = '5px';
    tooltip.style.zIndex = '1000';
    tooltip.style.maxWidth = '300px';
    tooltip.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.3)';
    
    // Generate tooltip content
    let content = `<h6>${node.label || node.id}</h6>`;
    
    if (node.group) {
        content += `<div><strong>Type:</strong> ${node.group}</div>`;
    }
    
    if (node.id) {
        content += `<div><strong>ID:</strong> ${node.id}</div>`;
    }
    
    if (node.title) {
        content += `<div>${node.title}</div>`;
    }
    
    // Add custom properties
    for (const key in node) {
        if (!['id', 'label', 'group', 'title', 'x', 'y', 'shape', 'color', 'size', 'font'].includes(key)) {
            if (typeof node[key] !== 'object' && typeof node[key] !== 'function') {
                content += `<div><strong>${key}:</strong> ${node[key]}</div>`;
            }
        }
    }
    
    // Add close button
    content += `<div class="mt-2 text-center">
        <button class="btn btn-sm btn-secondary" onclick="document.getElementById('network-node-tooltip').remove()">
            Close
        </button>
    </div>`;
    
    tooltip.innerHTML = content;
    document.body.appendChild(tooltip);
    
    // Auto-close after 5 seconds
    setTimeout(() => {
        if (document.getElementById('network-node-tooltip')) {
            document.getElementById('network-node-tooltip').remove();
        }
    }, 5000);
}

/**
 * Initialize a timeline visualization
 * @param {string} containerId - DOM element ID for the visualization container
 * @param {Object} options - Custom options to override defaults
 * @returns {vis.Timeline|null} - The created timeline instance or null on failure
 */
function initTimelineVisualization(containerId, options = {}) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return null;
    }
    
    // Create dataset
    const items = new vis.DataSet();
    
    // Merge default options with custom options
    const timelineOptions = {
        ...visualizationSettings.timeline,
        ...options
    };
    
    try {
        // Create timeline
        const timeline = new vis.Timeline(container, items, timelineOptions);
        
        // Store the instance
        visualizationInstances.timelines[containerId] = {
            timeline,
            items
        };
        
        return timeline;
    } catch (error) {
        console.error('Error initializing timeline visualization:', error);
        container.innerHTML = `
            <div class="alert alert-danger m-3">
                Error initializing timeline visualization: ${error.message}
            </div>
        `;
        return null;
    }
}

/**
 * Render a timeline visualization with provided events
 * @param {string} containerId - DOM element ID for the visualization container
 * @param {Array} events - Array of event objects
 * @param {Object} options - Custom options to override defaults
 */
function renderTimelineVisualization(containerId, events, options = {}) {
    // Check if we already have a timeline instance
    let instance = visualizationInstances.timelines[containerId];
    
    if (!instance) {
        // Initialize a new timeline
        const timeline = initTimelineVisualization(containerId, options);
        if (!timeline) return;
        
        instance = visualizationInstances.timelines[containerId];
    }
    
    // Clear existing data
    instance.items.clear();
    
    // Process events for timeline
    const timelineItems = events.map((event, index) => {
        // Determine item style based on event type
        let className = 'vis-item-cybersec';
        let title = event.description || '';
        
        switch (event.type) {
            case 'network_traffic':
                className = 'vis-item-traffic';
                break;
            case 'threat_detected':
                className = 'vis-item-threat';
                break;
            case 'defense_response':
                className = 'vis-item-defense';
                break;
            case 'attack_simulation':
                className = 'vis-item-attack';
                break;
        }
        
        // Create timeline item
        return {
            id: event.id || `event-${index}`,
            content: event.title || formatEventTitle(event),
            start: event.timestamp || new Date(),
            className: className,
            title: title
        };
    });
    
    // Add to timeline
    instance.items.add(timelineItems);
    
    // Fit timeline to all items
    instance.timeline.fit();
}

/**
 * Format an event title for the timeline
 * @param {Object} event - The event object
 * @returns {string} - Formatted title
 */
function formatEventTitle(event) {
    if (event.title) return event.title;
    
    switch (event.type) {
        case 'network_traffic':
            return `Traffic: ${event.source} → ${event.destination}`;
        case 'threat_detected':
            return `Threat: ${event.threat_type || 'Unknown'}`;
        case 'defense_response':
            return 'Defense Response';
        case 'attack_simulation':
            return `Attack: ${event.attack_type || 'Simulation'}`;
        default:
            return event.type || 'Event';
    }
}

/**
 * Create a bar chart for security data
 * @param {string} canvasId - Canvas element ID
 * @param {Array} labels - X-axis labels
 * @param {Array} data - Data values
 * @param {Object} options - Chart options
 * @returns {Chart} - The Chart.js instance
 */
function createBarChart(canvasId, labels, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }
    
    // Destroy existing chart
    if (visualizationInstances.charts[canvasId]) {
        visualizationInstances.charts[canvasId].destroy();
    }
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        },
        plugins: {
            legend: {
                display: false
            }
        }
    };
    
    // Create chart
    const chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: options.colors || [
                    '#0d6efd', '#dc3545', '#ffc107', '#198754',
                    '#6610f2', '#fd7e14', '#0dcaf0', '#d63384'
                ],
                borderWidth: 1
            }]
        },
        options: {...defaultOptions, ...options}
    });
    
    // Store the instance
    visualizationInstances.charts[canvasId] = chart;
    
    return chart;
}

/**
 * Create a line chart for security data
 * @param {string} canvasId - Canvas element ID
 * @param {Array} labels - X-axis labels
 * @param {Array} datasets - Array of dataset objects
 * @param {Object} options - Chart options
 * @returns {Chart} - The Chart.js instance
 */
function createLineChart(canvasId, labels, datasets, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }
    
    // Destroy existing chart
    if (visualizationInstances.charts[canvasId]) {
        visualizationInstances.charts[canvasId].destroy();
    }
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        },
        plugins: {
            legend: {
                position: 'top'
            },
            tooltip: {
                mode: 'index',
                intersect: false
            }
        }
    };
    
    // Create chart
    const chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {...defaultOptions, ...options}
    });
    
    // Store the instance
    visualizationInstances.charts[canvasId] = chart;
    
    return chart;
}

/**
 * Create a doughnut chart for security data
 * @param {string} canvasId - Canvas element ID
 * @param {Array} labels - Data labels
 * @param {Array} data - Data values
 * @param {Object} options - Chart options
 * @returns {Chart} - The Chart.js instance
 */
function createDoughnutChart(canvasId, labels, data, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }
    
    // Destroy existing chart
    if (visualizationInstances.charts[canvasId]) {
        visualizationInstances.charts[canvasId].destroy();
    }
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    boxWidth: 12
                }
            }
        }
    };
    
    // Create chart
    const chart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: options.colors || [
                    '#0d6efd', '#dc3545', '#ffc107', '#198754',
                    '#6610f2', '#fd7e14', '#0dcaf0', '#d63384'
                ],
                borderWidth: 1
            }]
        },
        options: {...defaultOptions, ...options}
    });
    
    // Store the instance
    visualizationInstances.charts[canvasId] = chart;
    
    return chart;
}

/**
 * Create a security score gauge chart
 * @param {string} canvasId - Canvas element ID
 * @param {number} score - Security score (0-100)
 * @param {Object} options - Chart options
 * @returns {Chart} - The Chart.js instance
 */
function createSecurityGauge(canvasId, score, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }
    
    // Destroy existing chart
    if (visualizationInstances.charts[canvasId]) {
        visualizationInstances.charts[canvasId].destroy();
    }
    
    // Clamp score to valid range
    score = Math.max(0, Math.min(100, score));
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        circumference: 180,
        rotation: 270,
        cutout: '75%',
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: false
            }
        }
    };
    
    // Determine color based on score
    let scoreColor = '#dc3545'; // Danger (red)
    if (score >= 80) {
        scoreColor = '#198754'; // Success (green)
    } else if (score >= 60) {
        scoreColor = '#ffc107'; // Warning (yellow)
    } else if (score >= 40) {
        scoreColor = '#fd7e14'; // Orange
    }
    
    // Create chart
    const chart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [
                    scoreColor,
                    'rgba(255, 255, 255, 0.1)' // Transparent background
                ],
                borderWidth: 0
            }]
        },
        options: {...defaultOptions, ...options}
    });
    
    // Store the instance
    visualizationInstances.charts[canvasId] = chart;
    
    return chart;
}

/**
 * Create a heatmap chart for displaying alert severity patterns
 * @param {string} canvasId - Canvas element ID
 * @param {Array} data - 2D array of data values
 * @param {Array} xLabels - X-axis labels 
 * @param {Array} yLabels - Y-axis labels
 * @param {Object} options - Chart options
 * @returns {Chart} - The Chart.js instance
 */
function createHeatmapChart(canvasId, data, xLabels, yLabels, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas not found: ${canvasId}`);
        return null;
    }
    
    // Destroy existing chart
    if (visualizationInstances.charts[canvasId]) {
        visualizationInstances.charts[canvasId].destroy();
    }
    
    // Process data for heatmap
    const datasets = [];
    
    yLabels.forEach((yLabel, yIndex) => {
        const dataset = {
            label: yLabel,
            data: data[yIndex] || [],
            borderWidth: 1,
            borderColor: 'rgba(255, 255, 255, 0.2)'
        };
        datasets.push(dataset);
    });
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return yLabels[value];
                    }
                },
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            },
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.1)'
                }
            }
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    title: function(context) {
                        const index = context[0].dataIndex;
                        return xLabels[index];
                    },
                    label: function(context) {
                        const yIndex = context.datasetIndex;
                        const xIndex = context.dataIndex;
                        return `${yLabels[yIndex]}: ${data[yIndex][xIndex]}`;
                    }
                }
            }
        }
    };
    
    // Create chart
    const chart = new Chart(canvas, {
        type: 'matrix',
        data: {
            datasets: datasets
        },
        options: {...defaultOptions, ...options}
    });
    
    // Store the instance
    visualizationInstances.charts[canvasId] = chart;
    
    return chart;
}

/**
 * Update an existing chart with new data
 * @param {string} canvasId - Canvas element ID
 * @param {Array} labels - New labels (for bar, line, doughnut charts)
 * @param {Array} data - New data (format depends on chart type)
 */
function updateChart(canvasId, labels, data) {
    const chart = visualizationInstances.charts[canvasId];
    if (!chart) {
        console.error(`Chart not found for canvas: ${canvasId}`);
        return;
    }
    
    // Update based on chart type
    if (chart.config.type === 'doughnut') {
        // Update doughnut chart
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
    } else if (chart.config.type === 'bar') {
        // Update bar chart
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
    } else if (chart.config.type === 'line') {
        // Update line chart (data is array of datasets)
        chart.data.labels = labels;
        data.forEach((dataset, i) => {
            if (chart.data.datasets[i]) {
                chart.data.datasets[i].data = dataset.data;
            }
        });
    }
    
    // Update the chart
    chart.update();
}

/**
 * Clean up visualization resources
 */
function cleanupVisualizations() {
    // Clean up network visualizations
    Object.values(visualizationInstances.networks).forEach(instance => {
        if (instance.network) {
            instance.network.destroy();
        }
    });
    
    // Clean up timeline visualizations
    Object.values(visualizationInstances.timelines).forEach(instance => {
        if (instance.timeline) {
            instance.timeline.destroy();
        }
    });
    
    // Clean up charts
    Object.values(visualizationInstances.charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    
    // Reset instances
    visualizationInstances.networks = {};
    visualizationInstances.timelines = {};
    visualizationInstances.charts = {};
}

// Global CSS for visualizations
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for visualizations
    const style = document.createElement('style');
    style.textContent = `
        /* Network visualization styles */
        .network-tooltip {
            transition: opacity 0.3s;
        }
        
        /* Timeline visualization styles */
        .vis-item.vis-item-cybersec {
            background-color: #0d6efd;
            border-color: #0a58ca;
        }
        
        .vis-item.vis-item-traffic {
            background-color: #6c757d;
            border-color: #495057;
        }
        
        .vis-item.vis-item-threat {
            background-color: #dc3545;
            border-color: #b02a37;
        }
        
        .vis-item.vis-item-defense {
            background-color: #198754;
            border-color: #146c43;
        }
        
        .vis-item.vis-item-attack {
            background-color: #fd7e14;
            border-color: #ca6510;
        }
    `;
    document.head.appendChild(style);
});

// Expose functions
window.renderNetworkVisualization = renderNetworkVisualization;
window.renderTimelineVisualization = renderTimelineVisualization;
window.createBarChart = createBarChart;
window.createLineChart = createLineChart;
window.createDoughnutChart = createDoughnutChart;
window.createSecurityGauge = createSecurityGauge;
window.updateChart = updateChart;
window.cleanupVisualizations = cleanupVisualizations;
