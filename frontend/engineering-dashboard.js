/**
 * Engineering Dashboard JavaScript
 * 
 * This script handles fetching and rendering engineering dashboard data
 * including Git activity, CI/CD status, Docker status, test results, and API health.
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
 * Initialize the dashboard
 */
function initDashboard() {
    console.log('Initializing Engineering Dashboard...');
    
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
        
        // Update pipeline flow visualization
        updatePipelineFlow(data);
        
        // Render all sections
        renderGitActivity(data.git_stats, data.recent_commits);
        renderCICDStatus(data.github_status, data.jenkins_status);
        renderDockerStatus(data.docker_status);
        renderTestResults(data.test_results);
        renderAPIHealth(data.api_health);
        
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showError('Failed to fetch dashboard data. Please check your connection.');
    }
}

/**
 * Update pipeline flow visualization
 */
function updatePipelineFlow(data) {
    // Stage 1: Developer Commit
    updateFlowStage('commit', 
        data.recent_commits && data.recent_commits.length > 0 ? 'success' : 'pending',
        data.recent_commits && data.recent_commits.length > 0 ? 
            formatTime(data.recent_commits[0].timestamp) : '--'
    );
    
    // Stage 2: Git
    updateFlowStage('git',
        data.git_stats && data.git_stats.total_commits > 0 ? 'success' : 'pending',
        data.git_stats && data.git_stats.total_commits > 0 ? 
            `${data.git_stats.total_commits} commits` : '--'
    );
    
    // Stage 3: GitHub
    updateFlowStage('github',
        data.git_stats && data.git_stats.remote_url ? 'success' : 'pending',
        data.git_stats && data.git_stats.remote_url ? 'Connected' : 'Not configured'
    );
    
    // Stage 4: CI/CD Build
    let cicdStatus = 'pending';
    let cicdTime = '--';
    if (data.github_status && data.github_status.latest_run) {
        const run = data.github_status.latest_run;
        if (run.status === 'completed') {
            cicdStatus = run.conclusion === 'success' ? 'success' : 'failure';
        } else {
            cicdStatus = 'warning';
        }
        cicdTime = formatTime(run.updated_at);
    }
    updateFlowStage('cicd', cicdStatus, cicdTime);
    
    // Stage 5: Docker Image
    let dockerImageStatus = 'pending';
    let dockerImageTime = '--';
    if (data.docker_status && data.docker_status.image) {
        dockerImageStatus = 'success';
        dockerImageTime = formatTime(data.docker_status.created);
    }
    updateFlowStage('docker', dockerImageStatus, dockerImageTime);
    
    // Stage 6: Jenkins Test
    let jenkinsStatus = 'pending';
    let jenkinsTime = '--';
    if (data.jenkins_status && data.jenkins_status.latest_build) {
        const build = data.jenkins_status.latest_build;
        if (build.status === 'SUCCESS') {
            jenkinsStatus = 'success';
        } else if (build.status === 'IN_PROGRESS') {
            jenkinsStatus = 'warning';
        } else {
            jenkinsStatus = 'failure';
        }
        jenkinsTime = formatTime(build.timestamp);
    }
    updateFlowStage('jenkins', jenkinsStatus, jenkinsTime);
    
    // Stage 7: Running Service
    let serviceStatus = 'pending';
    let serviceTime = '--';
    if (data.api_health && data.api_health.status === 'healthy') {
        serviceStatus = 'success';
        serviceTime = 'Running';
    } else if (data.docker_status && data.docker_status.status === 'running') {
        serviceStatus = 'success';
        serviceTime = 'Running';
    }
    updateFlowStage('service', serviceStatus, serviceTime);
}

/**
 * Update individual flow stage
 */
function updateFlowStage(stageName, status, timeText) {
    const stageElement = document.getElementById(`stage-${stageName}`);
    const statusElement = document.getElementById(`status-${stageName}`);
    const timeElement = document.getElementById(`time-${stageName}`);
    
    if (!stageElement || !statusElement || !timeElement) return;
    
    // Update stage class
    stageElement.className = 'flow-stage';
    stageElement.classList.add(status);
    
    // Update status indicator
    statusElement.className = 'stage-status';
    statusElement.classList.add(status);
    
    // Set status symbol
    switch (status) {
        case 'success':
            statusElement.textContent = '✓';
            break;
        case 'failure':
            statusElement.textContent = '✗';
            break;
        case 'warning':
            statusElement.textContent = '⚠';
            break;
        default:
            statusElement.textContent = '●';
    }
    
    // Update time text
    timeElement.textContent = timeText;
}

/**
 * Format timestamp for display
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
 * Render Git activity section
 */
function renderGitActivity(gitStats, recentCommits) {
    const content = document.getElementById('gitContent');
    const status = document.getElementById('gitStatus');
    
    if (!gitStats || !recentCommits) {
        content.innerHTML = '<div class="error-message">Git data unavailable</div>';
        setStatusIndicator(status, 'unknown');
        return;
    }
    
    setStatusIndicator(status, 'success');
    
    let html = '<div class="git-stats">';
    html += `<div class="stat-item"><strong>Total Commits:</strong> ${gitStats.total_commits}</div>`;
    html += `<div class="stat-item"><strong>Current Branch:</strong> ${gitStats.current_branch}</div>`;
    html += `<div class="stat-item"><strong>Contributors:</strong> ${gitStats.contributors}</div>`;
    html += '</div>';
    
    if (recentCommits && recentCommits.length > 0) {
        html += '<div class="commits-list"><h3>Recent Commits</h3>';
        recentCommits.slice(0, 5).forEach(commit => {
            const date = new Date(commit.timestamp).toLocaleString();
            html += `
                <div class="commit-item">
                    <div class="commit-hash">${commit.short_hash}</div>
                    <div class="commit-message">${escapeHtml(commit.message)}</div>
                    <div class="commit-meta">
                        <span class="commit-author">${escapeHtml(commit.author)}</span>
                        <span class="commit-date">${date}</span>
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    content.innerHTML = html;
}

/**
 * Render CI/CD status section
 */
function renderCICDStatus(githubStatus, jenkinsStatus) {
    const content = document.getElementById('cicdContent');
    const status = document.getElementById('cicdStatus');
    
    let html = '<div class="cicd-pipelines">';
    
    // GitHub Actions
    html += '<div class="pipeline-section">';
    html += '<h3>GitHub Actions</h3>';
    
    if (githubStatus && githubStatus.latest_run) {
        const run = githubStatus.latest_run;
        const statusClass = getStatusClass(run.conclusion || run.status);
        const successRate = (githubStatus.success_rate * 100).toFixed(1);
        
        html += `
            <div class="pipeline-status ${statusClass}">
                <div class="status-badge">${run.conclusion || run.status}</div>
                <div class="pipeline-info">
                    <div><strong>Workflow:</strong> ${escapeHtml(run.name)}</div>
                    <div><strong>Success Rate:</strong> ${successRate}%</div>
                    <div><strong>Last Run:</strong> ${new Date(run.updated_at).toLocaleString()}</div>
                </div>
            </div>
        `;
        
        setStatusIndicator(status, run.conclusion === 'success' ? 'success' : 'failure');
    } else {
        html += '<div class="status-unavailable">Status unavailable</div>';
    }
    
    html += '</div>';
    
    // Jenkins
    html += '<div class="pipeline-section">';
    html += '<h3>Jenkins</h3>';
    
    if (jenkinsStatus && jenkinsStatus.latest_build) {
        const build = jenkinsStatus.latest_build;
        const statusClass = getStatusClass(build.status);
        const successRate = (jenkinsStatus.success_rate * 100).toFixed(1);
        
        html += `
            <div class="pipeline-status ${statusClass}">
                <div class="status-badge">${build.status}</div>
                <div class="pipeline-info">
                    <div><strong>Build #:</strong> ${build.number}</div>
                    <div><strong>Success Rate:</strong> ${successRate}%</div>
                    <div><strong>Duration:</strong> ${(build.duration / 1000).toFixed(1)}s</div>
                </div>
            </div>
        `;
    } else {
        html += '<div class="status-unavailable">Status unavailable</div>';
    }
    
    html += '</div>';
    html += '</div>';
    
    content.innerHTML = html;
}

/**
 * Render Docker status section
 */
function renderDockerStatus(dockerStatus) {
    const content = document.getElementById('dockerContent');
    const status = document.getElementById('dockerStatus');
    
    if (!dockerStatus) {
        content.innerHTML = '<div class="error-message">Docker status unavailable</div>';
        setStatusIndicator(status, 'unknown');
        return;
    }
    
    const statusClass = getStatusClass(dockerStatus.status);
    setStatusIndicator(status, dockerStatus.status === 'running' ? 'success' : 'warning');
    
    let html = `
        <div class="docker-info ${statusClass}">
            <div class="status-badge">${dockerStatus.status}</div>
            <div class="docker-details">
                <div class="detail-item"><strong>Container:</strong> ${escapeHtml(dockerStatus.name)}</div>
                <div class="detail-item"><strong>Image:</strong> ${escapeHtml(dockerStatus.image)}</div>
                <div class="detail-item"><strong>Created:</strong> ${new Date(dockerStatus.created).toLocaleString()}</div>
    `;
    
    if (dockerStatus.health) {
        html += `<div class="detail-item"><strong>Health:</strong> ${dockerStatus.health}</div>`;
    }
    
    if (dockerStatus.ports && Object.keys(dockerStatus.ports).length > 0) {
        html += '<div class="detail-item"><strong>Ports:</strong> ';
        const portMappings = Object.entries(dockerStatus.ports)
            .map(([container, host]) => `${host} → ${container}`)
            .join(', ');
        html += escapeHtml(portMappings);
        html += '</div>';
    }
    
    html += '</div></div>';
    
    content.innerHTML = html;
}

/**
 * Render test results section
 */
function renderTestResults(testResults) {
    const content = document.getElementById('testContent');
    const status = document.getElementById('testStatus');
    
    if (!testResults) {
        content.innerHTML = '<div class="info-message">No test results available</div>';
        setStatusIndicator(status, 'unknown');
        return;
    }
    
    // This would be populated with actual test results
    // For now, show a placeholder
    content.innerHTML = `
        <div class="test-summary">
            <div class="info-message">Test results will be displayed here when available</div>
        </div>
    `;
    setStatusIndicator(status, 'unknown');
}

/**
 * Render API health section
 */
function renderAPIHealth(apiHealth) {
    const content = document.getElementById('apiContent');
    const status = document.getElementById('apiStatus');
    
    if (!apiHealth) {
        content.innerHTML = '<div class="error-message">API health unavailable</div>';
        setStatusIndicator(status, 'failure');
        return;
    }
    
    const isHealthy = apiHealth.status === 'healthy';
    setStatusIndicator(status, isHealthy ? 'success' : 'failure');
    
    let html = `
        <div class="api-health ${isHealthy ? 'status-success' : 'status-failure'}">
            <div class="status-badge">${apiHealth.status}</div>
            <div class="api-details">
                <div class="detail-item"><strong>Service:</strong> ${escapeHtml(apiHealth.service || 'Unknown')}</div>
            </div>
        </div>
    `;
    
    content.innerHTML = html;
}

/**
 * Set status indicator color
 */
function setStatusIndicator(element, status) {
    if (!element) return;
    
    element.className = 'status-indicator';
    
    switch (status) {
        case 'success':
            element.classList.add('status-success');
            element.title = 'Healthy';
            break;
        case 'failure':
        case 'error':
            element.classList.add('status-failure');
            element.title = 'Failed';
            break;
        case 'warning':
        case 'in_progress':
            element.classList.add('status-warning');
            element.title = 'Warning';
            break;
        default:
            element.classList.add('status-unknown');
            element.title = 'Unknown';
    }
}

/**
 * Get CSS class for status
 */
function getStatusClass(status) {
    if (!status) return 'status-unknown';
    
    const statusLower = status.toLowerCase();
    
    if (statusLower === 'success' || statusLower === 'running' || statusLower === 'completed') {
        return 'status-success';
    } else if (statusLower === 'failure' || statusLower === 'failed' || statusLower === 'error') {
        return 'status-failure';
    } else if (statusLower === 'in_progress' || statusLower === 'queued' || statusLower === 'unstable') {
        return 'status-warning';
    } else {
        return 'status-unknown';
    }
}

/**
 * Show error message
 */
function showError(message) {
    console.error(message);
    // Could add a toast notification here
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
