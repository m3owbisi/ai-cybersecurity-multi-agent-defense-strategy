/**
 * training.js - Training functionality for the cybersecurity platform
 */

// Initialize training components when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Setup training module navigation
    setupTrainingNavigation();
    
    // Initialize the skills radar chart
    initSkillsChart();
});

/**
 * Set up event handlers for training navigation
 */
function setupTrainingNavigation() {
    // Module selection
    document.querySelectorAll('#training-modules a').forEach(module => {
        module.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get selected module information
            const moduleId = this.getAttribute('data-module');
            const moduleName = this.querySelector('div').textContent.trim();
            
            // Update active state
            document.querySelectorAll('#training-modules a').forEach(m => {
                m.classList.remove('active');
            });
            this.classList.add('active');
            
            // Load the module content
            loadModuleContent(moduleId, moduleName);
        });
    });
    
    // Next/previous navigation
    const nextButton = document.querySelector('.training-navigation .btn-primary');
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            // In a real app, this would navigate to the next section
            showToast('Navigating to next section', 'Training', 'info');
        });
    }
    
    // Module completion button (dynamic binding)
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'complete-lesson') {
            handleLessonCompletion();
        }
        
        if (e.target && e.target.id === 'start-lesson-btn') {
            showLessonContent();
        }
        
        if (e.target && e.target.id === 'back-to-overview') {
            showModuleOverview();
        }
        
        if (e.target && e.target.id === 'submit-quiz') {
            evaluateQuiz();
        }
    });
}

/**
 * Load content for a selected training module
 * @param {string} moduleId - ID of the selected module
 * @param {string} moduleName - Name of the selected module
 */
function loadModuleContent(moduleId, moduleName) {
    // Update module title
    const moduleTitle = document.querySelector('.card-header h5');
    if (moduleTitle) {
        moduleTitle.textContent = moduleName + ' Training';
    }
    
    // Show loading state
    const contentArea = document.querySelector('.training-module-content');
    if (!contentArea) return;
    
    contentArea.innerHTML = `
        <div class="d-flex justify-content-center align-items-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Simulate content loading
    setTimeout(() => {
        if (moduleId === 'ransomware') {
            showModuleOverview();
        } else {
            // For other modules, show a placeholder
            contentArea.innerHTML = `
                <div class="alert alert-info">
                    <div class="d-flex">
                        <div class="flex-shrink-0">
                            <i class="bi bi-info-circle-fill me-2"></i>
                        </div>
                        <div>
                            The <strong>${moduleName}</strong> training module is currently under development.
                            Please check back later or select another module.
                        </div>
                    </div>
                </div>
                
                <div class="text-center py-4">
                    <i class="bi bi-tools display-1 text-secondary mb-3"></i>
                    <h4>Coming Soon</h4>
                    <p class="text-muted">Our team is working hard to develop this training content.</p>
                    <button class="btn btn-primary mt-3" id="return-to-ransomware">
                        Return to Ransomware Defense Module
                    </button>
                </div>
            `;
            
            // Add event listener to return button
            document.getElementById('return-to-ransomware').addEventListener('click', function() {
                document.querySelector('[data-module="ransomware"]').click();
            });
        }
    }, 1000);
}

/**
 * Show the module overview content
 */
function showModuleOverview() {
    const contentArea = document.querySelector('.training-module-content');
    if (!contentArea) return;
    
    contentArea.innerHTML = `
        <div class="mb-4">
            <h4>Module Overview</h4>
            <p>
                Ransomware attacks have become increasingly sophisticated, targeting organizations of all sizes and across all sectors. 
                This advanced training module will prepare you to use our multi-agent cybersecurity platform to defend against, detect, 
                and respond to ransomware threats.
            </p>
        </div>
        
        <div class="mb-4">
            <h5>Learning Objectives</h5>
            <ul>
                <li>Understand the ransomware attack lifecycle and common attack vectors</li>
                <li>Configure the Defense Agent for optimal ransomware protection</li>
                <li>Set up the Detection Agent to identify signs of ransomware activity</li>
                <li>Utilize the Coordinator Agent to orchestrate rapid response</li>
                <li>Develop and test a comprehensive ransomware response plan</li>
            </ul>
        </div>
        
        <div class="mb-4">
            <h5>Training Modules</h5>
            <div class="accordion" id="trainingAccordion">
                <div class="accordion-item bg-dark text-white">
                    <h2 class="accordion-header" id="headingOne">
                        <button class="accordion-button bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                            <i class="bi bi-1-circle me-2"></i> Ransomware Fundamentals
                        </button>
                    </h2>
                    <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#trainingAccordion">
                        <div class="accordion-body">
                            <p>This section covers the basics of ransomware, including:</p>
                            <ul>
                                <li>Common ransomware variants and their behaviors</li>
                                <li>Attack vectors and initial access techniques</li>
                                <li>Encryption methods and data exfiltration tactics</li>
                                <li>Recent trends in ransomware campaigns</li>
                            </ul>
                            <button class="btn btn-primary mt-2" id="start-lesson-btn">Start Lesson</button>
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item bg-dark text-white">
                    <h2 class="accordion-header" id="headingTwo">
                        <button class="accordion-button collapsed bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                            <i class="bi bi-2-circle me-2"></i> Defense Agent Configuration
                        </button>
                    </h2>
                    <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#trainingAccordion">
                        <div class="accordion-body">
                            <p>Learn to configure the Defense Agent for ransomware protection:</p>
                            <ul>
                                <li>Configuring file system monitoring and protection</li>
                                <li>Setting up behavior-based detection rules</li>
                                <li>Implementing application whitelisting</li>
                                <li>Configuring backup protection mechanisms</li>
                            </ul>
                            <button class="btn btn-secondary mt-2">Locked (Complete Previous Module)</button>
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item bg-dark text-white">
                    <h2 class="accordion-header" id="headingThree">
                        <button class="accordion-button collapsed bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                            <i class="bi bi-3-circle me-2"></i> Detection & Early Warning
                        </button>
                    </h2>
                    <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#trainingAccordion">
                        <div class="accordion-body">
                            <p>Configure the Detection Agent to identify ransomware activities:</p>
                            <ul>
                                <li>Identifying indicators of compromise (IOCs)</li>
                                <li>Monitoring for suspicious encryption activities</li>
                                <li>Detecting unusual file access patterns</li>
                                <li>Setting up alert thresholds and notifications</li>
                            </ul>
                            <button class="btn btn-secondary mt-2">Locked (Complete Previous Module)</button>
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item bg-dark text-white">
                    <h2 class="accordion-header" id="headingFour">
                        <button class="accordion-button collapsed bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
                            <i class="bi bi-4-circle me-2"></i> Incident Response Workflows
                        </button>
                    </h2>
                    <div id="collapseFour" class="accordion-collapse collapse" aria-labelledby="headingFour" data-bs-parent="#trainingAccordion">
                        <div class="accordion-body">
                            <p>Learn to use the Coordinator Agent for incident response:</p>
                            <ul>
                                <li>Configuring automated response workflows</li>
                                <li>Setting up containment and isolation procedures</li>
                                <li>Orchestrating system recovery processes</li>
                                <li>Designing notification and escalation paths</li>
                            </ul>
                            <button class="btn btn-secondary mt-2">Locked (Complete Previous Module)</button>
                        </div>
                    </div>
                </div>
                
                <div class="accordion-item bg-dark text-white">
                    <h2 class="accordion-header" id="headingFive">
                        <button class="accordion-button collapsed bg-dark text-white" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFive" aria-expanded="false" aria-controls="collapseFive">
                            <i class="bi bi-5-circle me-2"></i> Live Simulation Exercise
                        </button>
                    </h2>
                    <div id="collapseFive" class="accordion-collapse collapse" aria-labelledby="headingFive" data-bs-parent="#trainingAccordion">
                        <div class="accordion-body">
                            <p>Put your knowledge to the test in a live ransomware simulation:</p>
                            <ul>
                                <li>Simulated ransomware attack scenario</li>
                                <li>Real-time detection and response</li>
                                <li>Performance assessment and feedback</li>
                                <li>Improvement recommendations</li>
                            </ul>
                            <button class="btn btn-secondary mt-2">Locked (Complete Previous Module)</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="training-navigation d-flex justify-content-between mt-4">
            <button class="btn btn-outline-secondary" disabled>
                <i class="bi bi-arrow-left"></i> Previous
            </button>
            <button class="btn btn-primary">
                Next <i class="bi bi-arrow-right"></i>
            </button>
        </div>
    `;
}

/**
 * Show the lesson content
 */
function showLessonContent() {
    const contentArea = document.querySelector('.training-module-content');
    if (!contentArea) return;
    
    contentArea.innerHTML = `
        <div class="alert alert-warning">
            <div class="d-flex">
                <div class="flex-shrink-0">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                </div>
                <div>
                    <strong>Training Mode:</strong> This is a simulated environment. No actual systems will be affected during this training.
                </div>
            </div>
        </div>
        
        <div class="mb-4">
            <h4>Ransomware Fundamentals</h4>
            <p>Ransomware is a type of malicious software designed to block access to a computer system or data until a sum of money (ransom) is paid. Ransomware attacks typically involve:</p>
            
            <div class="card bg-dark mb-3">
                <div class="card-header">
                    <h5 class="mb-0">Ransomware Attack Lifecycle</h5>
                </div>
                <div class="card-body">
                    <ol>
                        <li class="mb-2">
                            <strong>Initial Access:</strong> Phishing emails, compromised credentials, or exploiting vulnerabilities
                        </li>
                        <li class="mb-2">
                            <strong>Execution & Persistence:</strong> Malware installation and ensuring persistence across reboots
                        </li>
                        <li class="mb-2">
                            <strong>Privilege Escalation:</strong> Gaining higher-level permissions to maximize impact
                        </li>
                        <li class="mb-2">
                            <strong>Lateral Movement:</strong> Spreading throughout the network to affect more systems
                        </li>
                        <li class="mb-2">
                            <strong>Data Exfiltration:</strong> Many ransomware groups now steal data before encryption
                        </li>
                        <li class="mb-2">
                            <strong>Encryption:</strong> Locking files and systems using strong encryption algorithms
                        </li>
                        <li class="mb-2">
                            <strong>Ransom Demand:</strong> Notification to victims with payment instructions
                        </li>
                    </ol>
                </div>
            </div>
            
            <p>During this training, we'll focus on configuring our AI agents to detect and respond to each step in this lifecycle.</p>
        </div>
        
        <div class="mb-4">
            <h5>Common Attack Vectors</h5>
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>Attack Vector</th>
                            <th>Description</th>
                            <th>Prevalence</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Phishing Emails</td>
                            <td>Malicious links or attachments sent via email</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: 85%"></div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>RDP/Remote Access</td>
                            <td>Exploitation of poorly secured remote access points</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: 75%"></div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>Software Vulnerabilities</td>
                            <td>Exploiting unpatched security flaws</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: 65%"></div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>Supply Chain Attacks</td>
                            <td>Compromising software vendors to distribute malware</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-warning" role="progressbar" style="width: 45%"></div>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td>Malicious Websites</td>
                            <td>Drive-by downloads and watering hole attacks</td>
                            <td>
                                <div class="progress" style="height: 10px;">
                                    <div class="progress-bar bg-success" role="progressbar" style="width: 35%"></div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="alert alert-info">
            <h5><i class="bi bi-lightbulb me-2"></i> Did You Know?</h5>
            <p class="mb-0">According to recent security reports, ransomware attacks increased by over 150% in the past year, with average ransom demands exceeding $200,000 per incident.</p>
        </div>
        
        <div class="mb-4">
            <h5>Knowledge Check</h5>
            <form id="knowledge-check-form">
                <div class="mb-3">
                    <label class="form-label">Which of the following is NOT typically a stage in the ransomware attack lifecycle?</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q1" id="q1a" value="a">
                        <label class="form-check-label" for="q1a">Initial Access</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q1" id="q1b" value="b">
                        <label class="form-check-label" for="q1b">Lateral Movement</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q1" id="q1c" value="c">
                        <label class="form-check-label" for="q1c">Blockchain Validation</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q1" id="q1d" value="d">
                        <label class="form-check-label" for="q1d">Data Exfiltration</label>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Which attack vector is currently the most common initial access point for ransomware?</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q2" id="q2a" value="a">
                        <label class="form-check-label" for="q2a">Phishing Emails</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q2" id="q2b" value="b">
                        <label class="form-check-label" for="q2b">USB Drives</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q2" id="q2c" value="c">
                        <label class="form-check-label" for="q2c">Social Media Links</label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="q2" id="q2d" value="d">
                        <label class="form-check-label" for="q2d">QR Codes</label>
                    </div>
                </div>
                
                <div class="d-grid">
                    <button type="button" class="btn btn-primary" id="submit-quiz">Submit Answers</button>
                </div>
            </form>
        </div>
        
        <div class="training-navigation d-flex justify-content-between mt-4">
            <button class="btn btn-outline-secondary" id="back-to-overview">
                <i class="bi bi-arrow-left"></i> Back to Overview
            </button>
            <button class="btn btn-success" id="complete-lesson" disabled>
                Complete Lesson <i class="bi bi-check-circle"></i>
            </button>
        </div>
    `;
}

/**
 * Evaluate the quiz submissions
 */
function evaluateQuiz() {
    // Get answers
    const q1Answer = document.querySelector('input[name="q1"]:checked')?.value;
    const q2Answer = document.querySelector('input[name="q2"]:checked')?.value;
    
    // Check if all questions are answered
    if (!q1Answer || !q2Answer) {
        showToast('Please answer all questions.', 'Quiz', 'warning');
        return;
    }
    
    // Check answers (correct answers: q1=c, q2=a)
    const correctAnswers = {q1: 'c', q2: 'a'};
    const score = [
        q1Answer === correctAnswers.q1,
        q2Answer === correctAnswers.q2
    ].filter(Boolean).length;
    
    // Calculate percentage
    const percentage = Math.round((score / 2) * 100);
    
    // Hide submit button
    document.getElementById('submit-quiz').style.display = 'none';
    
    // Show result
    document.getElementById('knowledge-check-form').insertAdjacentHTML('beforeend', `
        <div class="alert alert-${percentage >= 50 ? 'success' : 'danger'} mt-3">
            <strong>${percentage >= 50 ? 'Correct!' : 'Try Again!'}</strong> 
            You got ${score} out of 2 questions right (${percentage}%).
            ${percentage >= 50 ? 'You can now proceed to the next section.' : 'Please review the material and try again.'}
        </div>
    `);
    
    // Enable/disable complete button based on score
    document.getElementById('complete-lesson').disabled = percentage < 50;
}

/**
 * Handle lesson completion
 */
function handleLessonCompletion() {
    // Update progress indicator
    const progressBadge = document.querySelector('.card-header .badge');
    if (progressBadge) {
        progressBadge.textContent = 'Progress: 20%';
    }
    
    // Update module name in modal
    document.getElementById('completed-module-name').textContent = 'Ransomware Fundamentals';
    
    // Show completion modal
    const modal = new bootstrap.Modal(document.getElementById('trainingCompletionModal'));
    modal.show();
    
    // Add event listener to "Next Module" button in modal
    const nextModuleButton = document.querySelector('#trainingCompletionModal .btn-primary');
    if (nextModuleButton) {
        // Remove any existing listeners
        const newButton = nextModuleButton.cloneNode(true);
        nextModuleButton.parentNode.replaceChild(newButton, nextModuleButton);
        
        // Add new listener
        newButton.addEventListener('click', function() {
            // Hide modal
            modal.hide();
            
            // Return to module overview
            showModuleOverview();
            
            // Update module 1 button to show completed
            setTimeout(() => {
                const moduleOneButton = document.querySelector('#collapseOne button.btn-primary');
                if (moduleOneButton) {
                    moduleOneButton.className = 'btn btn-success mt-2';
                    moduleOneButton.innerHTML = '<i class="bi bi-check-circle"></i> Completed';
                }
                
                // Update module 2 button to be available
                const moduleTwoButton = document.querySelector('#collapseTwo button.btn-secondary');
                if (moduleTwoButton) {
                    moduleTwoButton.className = 'btn btn-primary mt-2';
                    moduleTwoButton.textContent = 'Start Lesson';
                }
            }, 500);
        });
    }
}

/**
 * Initialize the skills radar chart
 */
function initSkillsChart() {
    const ctx = document.getElementById('skillsRadarChart');
    if (!ctx) return;
    
    const skillsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: [
                'Threat Detection',
                'Incident Response',
                'Defense Configuration',
                'Compliance',
                'Network Security',
                'Risk Assessment'
            ],
            datasets: [{
                label: 'Your Skills',
                data: [85, 60, 70, 90, 80, 75],
                backgroundColor: 'rgba(13, 110, 253, 0.2)',
                borderColor: 'rgba(13, 110, 253, 0.8)',
                pointBackgroundColor: 'rgba(13, 110, 253, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(13, 110, 253, 1)',
                borderWidth: 2
            }, {
                label: 'Team Average',
                data: [75, 68, 65, 75, 82, 70],
                backgroundColor: 'rgba(108, 117, 125, 0.2)',
                borderColor: 'rgba(108, 117, 125, 0.8)',
                pointBackgroundColor: 'rgba(108, 117, 125, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(108, 117, 125, 1)',
                borderWidth: 2
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: '#e9ecef'
                    },
                    ticks: {
                        backdropColor: 'transparent',
                        color: '#e9ecef'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e9ecef'
                    }
                }
            }
        }
    });
}