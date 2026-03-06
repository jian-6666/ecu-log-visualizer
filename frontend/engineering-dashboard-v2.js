/**
 * Engineering Dashboard V2 - JavaScript
 * Professional DevOps Demonstration Dashboard
 */

// Configuration
const CONFIG = {
    API_BASE_URL: window.location.origin,
    REFRESH_INTERVAL: 30000, // 30 seconds
    REPO_OWNER: 'jian-6666',
    REPO_NAME: 'ecu-log-visualizer',
};

// State
let refreshTimer = null;
let lastUpdateTime = null;

/**
 * Initialize dashboard
 */
function initDashboard() {
    console.log('Initializing Engineering Dashboard V2...');
    
    // Set up refresh button
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            console.log('Manual refresh triggered');
            fetchDashboardData();
        });
    }
    
    // Initial data fetch
    fetchDashboardData();
    
    // Set up auto-refresh
    startAutoRefresh();
}

/**
 * Start auto-refresh timer
 */
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    
    refreshTimer = setInterval(() => {
        console.log('Auto-refresh triggered');
        fetchDashboardData();
    }, CONFIG.REFRESH_INTERVAL);
}

/**
 * Fetch all dashboard data
 */
async function fetchDashboardData() {
    console.log('Fetching dashboard data...');
    
    try {
        const response = await fetch(
            `${CONFIG.API_BASE_URL}/api/engineering/dashboard?` +
            `repo_owner=${CONFIG.REPO_OWNER}&repo_name=${CONFIG.REPO_NAME}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Dashboard data received:', data);
        
        // Update last update time
        lastUpdateTime = new Date();
        updateLastUpdateDisplay();
        
        // Render all sections
        renderPipelineFlow(data);
        renderActivityTimeline(data);
        renderCICDCard(data);
        renderDockerCard(data);
        renderJenkinsCard(data);
        renderServiceCard(data);
        
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showError('Failed to fetch dashboard data');
    }
}

/**
 * Update last update time display
 */
function updateLastUpdateDisplay() {
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement && lastUpdateTime) {
        const timeString = lastUpdateTime.toLocaleTimeString();
        lastUpdateElement.textContent = `Last updated: ${timeString}`;
    }
}

/**
 * Render pipeline flow
 */
function renderPipelineFlow(data) {
    const container = document.getElementById('pipelineFlow');
    if (!container) return;
    
    const stages = [
        {
            id: 'commit',
            name: 'Developer Commit',
            icon: '👨‍💻',
            status: data.recent_commits && data.recent_commits.length > 0 ? 'success' : 'pending',
            time: data.recent_commits && data.recent_commits.length > 0 ? 
                formatTime(data.recent_commits[0].timestamp) : '--'
        },
        {
            id: 'push',
            name: 'Push to GitHub',
            icon: '📤',
            status: data.git_stats && data.git_stats.remote_url ? 'success' : 'pending',
            time: data.git_stats && data.git_stats.remote_url ? 'Connected' : '--'
        },
        {
            id: 'cicd',
            name: 'CI/CD Build',
            icon: '⚙️',
            status: getCICDStatus(data.github_status),
            time: data.github_status && data.github_status.latest_run ? 
                formatTime(data.github_status.latest_run.updated_at) : '--'
        },
        {
            id: 'docker',
            name: 'Docker Build',
            icon: '🐳',
            status: data.docker_status && data.docker_status.status === 'running' ? 'success' : 'pending',
            time: data.docker_status ? formatTime(data.docker_status.created) : '--'
        },
        {
            id: 'jenkins',
            name: 'Jenkins Test',
            icon: '🔧',
            status: getJenkinsStatus(data.jenkins_status),
            time: data.jenkins_status && data.jenkins_status.latest_build ? 
                formatTime(data.jenkins_status.latest_build.timestamp) : '--'
        },
        {
            id: 'deploy',
            name: 'Running Service',
            icon: '🚀',
            status: data.api_health && data.api_health.status === 'healthy' ? 'success' : 'pending',
            time: data.api_health && data.api_health.status === 'healthy' ? 'Live' : '--'
        }
    ];
    
    let html = '';
    stages.forEach((stage, index) => {
        html += `
            <div class="pipeline-stage ${stage.status}">
                <div class="stage-icon">${stage.icon}</div>
                <div class="stage-name">${stage.name}</div>
                <div class="stage-status ${stage.status}">${getStatusSymbol(stage.status)}</div>
                <div class="stage-time">${stage.time}</div>
            </div>
        `;
        
        if (index < stages.length - 1) {
            html += '<div class="pipeline-arrow">→</div>';
        }
    });
    
    container.innerHTML = html;
}

/**
 * Render activity timeline
 */
function renderActivityTimeline(data) {
    const container = document.getElementById('timelineContent');
    const countElement = document.getElementById('activityCount');
    
    if (!container) return;
    
    const events = [];
    
    // Add commit events
    if (data.recent_commits && data.recent_commits.length > 0) {
        data.recent_commits.slice(0, 10).forEach(commit => {
            events.push({
                type: 'commit',
                timestamp: commit.timestamp,
                commit: commit,
                status: 'success'
            });
        });
    }
    
    // Sort by timestamp (newest first)
    events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    // Update count
    if (countElement) {
        countElement.textContent = `${events.length} events`;
    }
    
    // Render events
    if (events.length === 0) {
        container.innerHTML = '<div class="text-muted" style="padding: var(--space-4); text-align: center;">No recent activity</div>';
        return;
    }
    
    let html = '';
    events.forEach(event => {
        html += renderActivityEvent(event);
    });
    
    container.innerHTML = html;
}

/**
 * Render single activity event
 */
function renderActivityEvent(event) {
    const commit = event.commit;
    const statusClass = event.status || 'success';
    
    return `
        <div class="activity-event ${statusClass}">
            <div class="event-header">
                <div class="event-type">
                    <span>📝</span>
                    <span>Commit</span>
                </div>
                <div class="event-time">${formatTime(event.timestamp)}</div>
            </div>
            <div class="event-commit">
                <span class="commit-sha" title="${commit.hash}">${commit.short_hash}</span>
                <div class="commit-message">${escapeHtml(commit.message)}</div>
            </div>
            <div class="event-meta">
                <div class="meta-item">
                    <span>👤</span>
                    <span>${escapeHtml(commit.author)}</span>
                </div>
                <div class="meta-item">
                    <span>🌿</span>
                    <span>${escapeHtml(commit.branch)}</span>
                </div>
            </div>
            <div class="event-status ${statusClass}">
                <span>${getStatusSymbol(statusClass)}</span>
                <span>Committed</span>
            </div>
        </div>
    `;
}

/**
 * Render CI/CD card
 */
function renderCICDCard(data) {
    const container = document.getElementById('cicdContent');
    if (!container) return;
    
    if (!data.github_status || !data.github_status.latest_run) {
        container.innerHTML = '<div class="text-muted">No CI/CD data available</div>';
        return;
    }
    
    const run = data.github_status.latest_run;
    const status = run.conclusion || run.status;
    const statusClass = getStatusClass(status);
    const successRate = (data.github_status.success_rate * 100).toFixed(0);
    
    container.innerHTML = `
        <div class="metric-large">
            <div class="status-indicator ${statusClass}">
                <span>${getStatusSymbol(statusClass)}</span>
                <span>${status.toUpperCase()}</span>
            </div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Workflow</div>
            <div class="metric-value">${escapeHtml(run.name)}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">${successRate}%</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Last Run</div>
            <div class="metric-value">${formatTime(run.updated_at)}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Triggered By</div>
            <div class="metric-value">${escapeHtml(run.name)}</div>
        </div>
    `;
}

/**
 * Render Docker card
 */
function renderDockerCard(data) {
    const container = document.getElementById('dockerContent');
    if (!container) return;
    
    // Docker explanation
    let html = `
        <div class="docker-explanation">
            <div class="explanation-title">Why Docker?</div>
            <div class="explanation-text">
                Docker ensures consistent deployment environments across development, testing, and production. 
                It packages the application with all dependencies, making deployments reproducible and reliable.
            </div>
        </div>
    `;
    
    if (!data.docker_status) {
        html += '<div class="text-muted">Docker status unavailable</div>';
        container.innerHTML = html;
        return;
    }
    
    const docker = data.docker_status;
    const statusClass = docker.status === 'running' ? 'success' : 'pending';
    
    html += `
        <div class="metric-large">
            <div class="status-indicator ${statusClass}">
                <span>${getStatusSymbol(statusClass)}</span>
                <span>${docker.status.toUpperCase()}</span>
            </div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Container</div>
            <div class="metric-value">${escapeHtml(docker.name)}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Image</div>
            <div class="metric-value">${escapeHtml(docker.image)}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Created</div>
            <div class="metric-value">${formatTime(docker.created)}</div>
        </div>
    `;
    
    if (docker.ports && Object.keys(docker.ports).length > 0) {
        const portMappings = Object.entries(docker.ports)
            .map(([container, host]) => `${host}→${container}`)
            .join(', ');
        html += `
            <div class="metric-row">
                <div class="metric-label">Ports</div>
                <div class="metric-value">${escapeHtml(portMappings)}</div>
            </div>
        `;
    }
    
    if (docker.health) {
        html += `
            <div class="metric-row">
                <div class="metric-label">Health</div>
                <div class="metric-value">${docker.health}</div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

/**
 * Render Jenkins card
 */
function renderJenkinsCard(data) {
    const container = document.getElementById('jenkinsContent');
    if (!container) return;
    
    if (!data.jenkins_status || !data.jenkins_status.latest_build) {
        container.innerHTML = '<div class="text-muted">Jenkins data unavailable</div>';
        return;
    }
    
    const build = data.jenkins_status.latest_build;
    const statusClass = getStatusClass(build.status);
    const successRate = (data.jenkins_status.success_rate * 100).toFixed(0);
    
    container.innerHTML = `
        <div class="metric-large">
            <div class="status-indicator ${statusClass}">
                <span>${getStatusSymbol(statusClass)}</span>
                <span>${build.status}</span>
            </div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Build Number</div>
            <div class="metric-value">#${build.number}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">${successRate}%</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Duration</div>
            <div class="metric-value">${(build.duration / 1000).toFixed(1)}s</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Started</div>
            <div class="metric-value">${formatTime(build.timestamp)}</div>
        </div>
    `;
}

/**
 * Render service health card
 */
function renderServiceCard(data) {
    const container = document.getElementById('serviceContent');
    const badge = document.getElementById('serviceBadge');
    
    if (!container) return;
    
    if (!data.api_health) {
        container.innerHTML = '<div class="text-muted">Service health unavailable</div>';
        return;
    }
    
    const health = data.api_health;
    const statusClass = health.status === 'healthy' ? 'success' : 'failure';
    
    if (badge) {
        badge.textContent = health.status === 'healthy' ? 'Running' : 'Down';
        badge.className = `card-badge status-indicator ${statusClass}`;
    }
    
    container.innerHTML = `
        <div class="metric-large">
            <div class="status-indicator ${statusClass}">
                <span>${getStatusSymbol(statusClass)}</span>
                <span>${health.status.toUpperCase()}</span>
            </div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Service</div>
            <div class="metric-value">${escapeHtml(health.service || 'ECU Log Visualizer')}</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Endpoint</div>
            <div class="metric-value">/health</div>
        </div>
        
        <div class="metric-row">
            <div class="metric-label">Status</div>
            <div class="metric-value">${health.status}</div>
        </div>
    `;
}

/**
 * Helper: Get CI/CD status
 */
function getCICDStatus(githubStatus) {
    if (!githubStatus || !githubStatus.latest_run) return 'pending';
    const run = githubStatus.latest_run;
    if (run.status === 'completed') {
        return run.conclusion === 'success' ? 'success' : 'failure';
    }
    return 'running';
}

/**
 * Helper: Get Jenkins status
 */
function getJenkinsStatus(jenkinsStatus) {
    if (!jenkinsStatus || !jenkinsStatus.latest_build) return 'pending';
    const build = jenkinsStatus.latest_build;
    if (build.status === 'SUCCESS') return 'success';
    if (build.status === 'IN_PROGRESS') return 'running';
    return 'failure';
}

/**
 * Helper: Get status class
 */
function getStatusClass(status) {
    if (!status) return 'pending';
    const statusLower = status.toLowerCase();
    
    if (statusLower === 'success' || statusLower === 'running' || statusLower === 'completed' || statusLower === 'healthy') {
        return 'success';
    } else if (statusLower === 'failure' || statusLower === 'failed' || statusLower === 'error' || statusLower === 'unhealthy') {
        return 'failure';
    } else if (statusLower === 'in_progress' || statusLower === 'queued' || statusLower === 'unstable') {
        return 'running';
    }
    return 'pending';
}

/**
 * Helper: Get status symbol
 */
function getStatusSymbol(status) {
    switch (status) {
        case 'success': return '✓';
        case 'failure': return '✗';
        case 'running': return '⟳';
        case 'pending': return '○';
        default: return '○';
    }
}

/**
 * Helper: Format timestamp
 */
function formatTime(timestamp) {
    if (!timestamp) return '--';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
}

/**
 * Helper: Escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Helper: Show error
 */
function showError(message) {
    console.error(message);
    // Could add toast notification here
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
