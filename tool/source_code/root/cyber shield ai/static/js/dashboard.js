/**
 * dashboard.js - Dashboard specific functionality for the cybersecurity platform
 */

// Initialize dashboard components when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any dashboard specific functionality
    
    // Fetch security status information
    fetchSecurityStatus();
    
    // Set up refresh buttons and intervals
    setupRefreshHandlers();
});

/**
 * Fetch the latest security status from the API
 */
function fetchSecurityStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateAgentStatus(data.agents);
            updateSystemHealth(data.system_health);
        })
        .catch(error => {
            console.error('Error fetching security status:', error);
            showToast('Failed to load system status data. Please refresh.', 'Error', 'danger');
        });
}

/**
 * Update the agent status table with the latest data
 * @param {Object} agents - Agent status data
 */
function updateAgentStatus(agents) {
    if (!agents) return;
    
    // In a full implementation, this would update the agent status table
    console.log('Agent status updated:', agents);
}

/**
 * Update the system health gauge with the latest score
 * @param {number} healthScore - System health score (0-100)
 */
function updateSystemHealth(healthScore) {
    if (healthScore === undefined || healthScore === null) return;
    
    // Update the health score display
    const healthValueEl = document.getElementById('system-health-value');
    if (healthValueEl) {
        healthValueEl.textContent = `${healthScore.toFixed(1)}%`;
        
        // Change color based on score
        if (healthScore >= 90) {
            healthValueEl.className = 'metric-value text-success';
        } else if (healthScore >= 70) {
            healthValueEl.className = 'metric-value text-warning';
        } else {
            healthValueEl.className = 'metric-value text-danger';
        }
    }
    
    // Update the health gauge (if Chart.js is being used)
    const healthGauge = Chart.getChart('healthGauge');
    if (healthGauge) {
        healthGauge.data.datasets[0].data = [healthScore, 100 - healthScore];
        healthGauge.update();
    }
}

/**
 * Set up event handlers for refresh buttons and automatic refresh intervals
 */
function setupRefreshHandlers() {
    // Refresh button for event log
    const refreshButton = document.querySelector('.card-header button.btn-outline-secondary');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Show loading indicator
            this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            this.disabled = true;
            
            // Simulate refresh delay
            setTimeout(() => {
                // Reset button state
                this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
                this.disabled = false;
                
                // Refresh data
                fetchSecurityStatus();
                
                // Show success toast
                showToast('Dashboard data refreshed successfully', 'Refresh', 'success');
            }, 1000);
        });
    }
    
    // Set up automatic refresh interval (every 60 seconds)
    setInterval(fetchSecurityStatus, 60000);
    
    // Event log toggle switches
    document.querySelectorAll('.form-check-input').forEach(toggle => {
        toggle.addEventListener('change', function() {
            const type = this.id.replace('toggle-', '');
            const eventItems = document.querySelectorAll(`.event-type-${type}`);
            
            eventItems.forEach(item => {
                const eventRow = item.closest('.event-item');
                if (eventRow) {
                    if (this.checked) {
                        eventRow.style.display = '';
                    } else {
                        eventRow.style.display = 'none';
                    }
                }
            });
        });
    });
}

/**
 * Generate random traffic data for demo purposes
 * @param {number} hours - Number of hours of data to generate
 * @returns {Object} - Traffic data object with timestamps and values
 */
function generateTrafficData(hours) {
    const data = {
        timestamps: [],
        legitimate: [],
        suspicious: []
    };
    
    const now = new Date();
    
    for (let i = hours; i >= 0; i--) {
        // Generate timestamp
        const timestamp = new Date(now);
        timestamp.setHours(now.getHours() - i);
        data.timestamps.push(timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
        
        // Generate legitimate traffic (500-1500)
        data.legitimate.push(Math.floor(Math.random() * 1000) + 500);
        
        // Generate suspicious traffic (10-150)
        data.suspicious.push(Math.floor(Math.random() * 140) + 10);
    }
    
    return data;
}