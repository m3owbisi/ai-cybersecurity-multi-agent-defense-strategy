/**
 * main.js - Main JavaScript functionality for the cybersecurity platform
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Theme toggle functionality (if present)
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Setup navigation highlighting
    setupActiveNavigation();
    
    // Initialize any components specific to the current page
    initCurrentPage();
});

/**
 * Toggle between dark and light theme (not fully implemented as we use dark theme by default)
 */
function toggleTheme() {
    document.body.classList.toggle('light-theme');
    
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        if (document.body.classList.contains('light-theme')) {
            themeIcon.classList.remove('bi-moon-stars');
            themeIcon.classList.add('bi-sun');
        } else {
            themeIcon.classList.remove('bi-sun');
            themeIcon.classList.add('bi-moon-stars');
        }
    }
}

/**
 * Highlight the active navigation item based on current page
 */
function setupActiveNavigation() {
    // Get current page path
    const currentPath = window.location.pathname;
    
    // Find the matching navigation item and add active class
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || 
            (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
            
            // If inside a dropdown, also mark parent as active
            const dropdownParent = link.closest('.nav-item.dropdown');
            if (dropdownParent) {
                const parentLink = dropdownParent.querySelector('.nav-link');
                if (parentLink) {
                    parentLink.classList.add('active');
                }
            }
        }
    });
}

/**
 * Initialize components specific to the current page
 */
function initCurrentPage() {
    const currentPath = window.location.pathname;
    
    // Dashboard page
    if (currentPath === '/dashboard' || currentPath === '/dashboard/') {
        if (typeof initDashboard === 'function') {
            initDashboard();
        }
    }
    // Simulation page
    else if (currentPath.includes('/simulation')) {
        if (typeof initSimulation === 'function') {
            initSimulation();
        }
    }
    // Training page
    else if (currentPath.includes('/training')) {
        if (typeof initTraining === 'function') {
            initTraining();
        }
    }
}

/**
 * Generic function to show a modal alert
 * @param {string} title - Alert title
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(title, message, type = 'info') {
    // Check if the alert modal exists, if not create it
    let alertModal = document.getElementById('alertModal');
    
    if (!alertModal) {
        const modalHtml = `
            <div class="modal fade" id="alertModal" tabindex="-1" aria-labelledby="alertModalLabel" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content bg-dark text-white">
                        <div class="modal-header">
                            <h5 class="modal-title" id="alertModalLabel">Notification</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div id="alertModalContent"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        const div = document.createElement('div');
        div.innerHTML = modalHtml;
        document.body.appendChild(div);
        
        alertModal = document.getElementById('alertModal');
    }
    
    // Set the modal content
    const alertContent = document.getElementById('alertModalContent');
    alertContent.innerHTML = `
        <div class="alert alert-${type}">
            <h5>${title}</h5>
            <p>${message}</p>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(alertModal);
    modal.show();
}

/**
 * Format a date object to a localized string
 * @param {Date|string} date - Date to format
 * @param {boolean} includeTime - Whether to include the time
 * @returns {string} - Formatted date string
 */
function formatDate(date, includeTime = true) {
    if (!date) return 'N/A';
    
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return dateObj.toLocaleDateString(undefined, options);
}

/**
 * Format a large number with appropriate suffixes (K, M, B)
 * @param {number} num - Number to format
 * @returns {string} - Formatted number string
 */
function formatLargeNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Show a toast notification
 * @param {string} message - Toast message
 * @param {string} title - Toast title
 * @param {string} type - Toast type (success, danger, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showToast(message, title = 'Notification', type = 'info', duration = 5000) {
    // Check if toast container exists, if not create it
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create a unique ID for this toast
    const toastId = 'toast-' + Date.now();
    
    // Create toast element
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <small>${formatDate(new Date(), false)}</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body bg-dark text-white">
                ${message}
            </div>
        </div>
    `;
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        delay: duration
    });
    
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * Create a spinner element for loading states
 * @param {string} size - Size of the spinner (sm, md, lg)
 * @param {string} color - Color of the spinner (text-primary, text-light, etc.)
 * @returns {HTMLElement} - Spinner element
 */
function createSpinner(size = '', color = 'text-light') {
    const spinner = document.createElement('div');
    spinner.className = `spinner-border ${size ? 'spinner-border-' + size : ''} ${color}`;
    spinner.setAttribute('role', 'status');
    
    const span = document.createElement('span');
    span.className = 'visually-hidden';
    span.textContent = 'Loading...';
    
    spinner.appendChild(span);
    return spinner;
}

/**
 * Format bytes to a human-readable string
 * @param {number} bytes - Bytes to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted string
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format a security severity level with appropriate colors
 * @param {string} severity - Severity level (critical, high, medium, low)
 * @returns {string} - HTML string with formatted severity
 */
function formatSeverity(severity) {
    if (!severity) return '<span class="text-secondary">Unknown</span>';
    
    const severityLower = severity.toLowerCase();
    let badgeClass = 'bg-secondary';
    
    switch (severityLower) {
        case 'critical':
            badgeClass = 'bg-danger';
            break;
        case 'high':
            badgeClass = 'bg-danger';
            break;
        case 'medium':
            badgeClass = 'bg-warning';
            break;
        case 'low':
            badgeClass = 'bg-success';
            break;
        case 'info':
            badgeClass = 'bg-info';
            break;
    }
    
    return `<span class="badge ${badgeClass}">${severity.toUpperCase()}</span>`;
}

/**
 * Handle API errors and show appropriate messages
 * @param {Error} error - The error object
 * @param {string} context - Context where the error occurred
 */
function handleApiError(error, context = 'API Request') {
    console.error(`${context} Error:`, error);
    
    let errorMessage = 'An unknown error occurred. Please try again.';
    
    if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response received from server. Please check your connection.';
    } else {
        // Error in setting up the request
        errorMessage = error.message || errorMessage;
    }
    
    showToast(errorMessage, 'Error', 'danger');
}
