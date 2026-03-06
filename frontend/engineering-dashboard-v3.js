// ===== DevOps Pipeline Dashboard V3 - Complete Redesign =====

// Configuration
const CONFIG = {
    refreshInterval: 30000,
    apiBaseUrl: '/api/engineering',
    repoOwner: 'jian-6666',
    repoName: 'ecu-log-visualizer',
    containerName: 'ecu-log-visualizer'
};

// State
const state = {
    gitData: null,
    githubData: null,
    dockerData: null,
    lastUpdate: null,
    refreshTimer: null
};

// Utility Functions
const utils = {
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ago`;
        if (hours > 0) return `${hours}h ago`;
        if (minutes > 0) return `${minutes}m ago`;
        return 'just now';
    },

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    truncate(str, length = 50) {
        return str.length > length ? str.substring(0, length) + '...' : str;
    }
};

// API Functions
const api = {
    async fetchGitCommits() {
        try {
            const response = await fetch(`${CONFIG.apiBaseUrl}/git/commits?limit=10`);
            if (!response.ok) return [];
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch git commits:', error);
            return [];
        }
    },

    async fetchGitStats() {
        try {
            const response = await fetch(`${CONFIG.apiBaseUrl}/git/stats`);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch git stats:', error);
            return null;
        }
    },

    async fetchGitHubStatus() {
        try {
            const url = `${CONFIG.apiBaseUrl}/cicd/github?repo_owner=${CONFIG.repoOwner}&repo_name=${CONFIG.repoName}`;
            const response = await fetch(url);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch GitHub status:', error);
            return null;
        }
    },

    async fetchDockerStatus() {
        try {
            const url = `${CONFIG.apiBaseUrl}/docker/status?container_name=${CONFIG.containerName}`;
            const response = await fetch(url);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch Docker status:', error);
            return null;
        }
    }
};

// Render Functions
const render = {
    // Update key metrics
    updateMetrics(gitData, githubData, dockerData) {
        // Success Rate
        if (githubData) {
            const rate = Math.round(githubData.success_rate * 100);
            document.getElementById('successRate').textContent = `${rate}%`;
        }

        // Latest Build
        if (githubData?.latest_run) {
            const status = githubData.latest_run.conclusion || githubData.latest_run.status;
            document.getElementById('latestBuild').textContent = status.toUpperCase();
        }

        // Docker Status
        if (dockerData) {
            document.getElementById('dockerStatus').textContent = dockerData.status.toUpperCase();
        } else {
            document.getElementById('dockerStatus').textContent = 'NOT RUNNING';
        }

        // Deployment Status
        if (dockerData?.status === 'running') {
            document.getElementById('deploymentStatus').textContent = 'LIVE';
        } else {
            document.getElementById('deploymentStatus').textContent = 'STOPPED';
        }
    },

    // Render detailed pipeline with all CI/CD steps
    pipelineFlow(gitData, githubData, dockerData) {
        const latestCommit = gitData && gitData.length > 0 ? gitData[0] : null;
        const latestRun = githubData?.latest_run;
        
        // Define all pipeline steps
        const steps = [
            {
                name: 'Commit',
                icon: '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>',
                status: latestCommit ? 'success' : 'pending',
                statusText: latestCommit ? 'Committed' : 'No commits',
                time: latestCommit ? utils.formatDate(latestCommit.timestamp) : ''
            },
            {
                name: 'Push',
                icon: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
                status: latestCommit ? 'success' : 'pending',
                statusText: latestCommit ? 'Pushed' : 'Waiting',
                time: latestCommit ? utils.formatDate(latestCommit.timestamp) : ''
            },
            {
                name: 'CI Trigger',
                icon: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
                status: latestRun ? (latestRun.status === 'completed' ? 'success' : 'running') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? 'Triggered' : 'Running') : 'Waiting',
                time: latestRun ? utils.formatDate(latestRun.created_at) : ''
            },
            {
                name: 'Install Deps',
                icon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
                status: latestRun ? (latestRun.status === 'completed' ? 'success' : latestRun.status === 'in_progress' ? 'running' : 'pending') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? 'Installed' : latestRun.status === 'in_progress' ? 'Installing' : 'Waiting') : 'Waiting',
                time: ''
            },
            {
                name: 'Lint',
                icon: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
                status: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'success' : 'failure') : latestRun.status === 'in_progress' ? 'running' : 'pending') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'Passed' : 'Failed') : 'Running') : 'Waiting',
                time: ''
            },
            {
                name: 'Unit Tests',
                icon: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
                status: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'success' : 'failure') : latestRun.status === 'in_progress' ? 'running' : 'pending') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'Passed' : 'Failed') : 'Running') : 'Waiting',
                time: ''
            },
            {
                name: 'Integration Tests',
                icon: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
                status: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'success' : 'failure') : latestRun.status === 'in_progress' ? 'running' : 'pending') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? (latestRun.conclusion === 'success' ? 'Passed' : 'Failed') : 'Running') : 'Waiting',
                time: ''
            },
            {
                name: 'Build App',
                icon: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>',
                status: latestRun ? (latestRun.status === 'completed' ? 'success' : latestRun.status === 'in_progress' ? 'running' : 'pending') : 'pending',
                statusText: latestRun ? (latestRun.status === 'completed' ? 'Built' : 'Building') : 'Waiting',
                time: ''
            },
            {
                name: 'Docker Build',
                icon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
                status: dockerData ? 'success' : (latestRun && latestRun.status === 'completed' ? 'success' : 'pending'),
                statusText: dockerData ? 'Built' : 'Waiting',
                time: dockerData ? utils.formatDate(dockerData.created) : ''
            },
            {
                name: 'Deploy',
                icon: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
                status: dockerData?.status === 'running' ? 'success' : 'pending',
                statusText: dockerData?.status === 'running' ? 'Running' : 'Not deployed',
                time: dockerData?.status === 'running' ? utils.formatDate(dockerData.created) : ''
            }
        ];

        const html = steps.map(step => `
            <div class="pipeline-step">
                <div class="step-icon-wrapper status-${step.status}">
                    <svg class="step-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${step.icon}
                    </svg>
                </div>
                <div class="step-info">
                    <div class="step-name">${step.name}</div>
                    <span class="step-status ${step.status}">${step.statusText}</span>
                    ${step.time ? `<div class="step-time">${step.time}</div>` : ''}
                </div>
            </div>
        `).join('');

        document.getElementById('pipelineFlow').innerHTML = html;
    },

    // Render rich engineering activity log
    activityLog(gitData, githubData, dockerData) {
        const activities = [];

        // Add git commits with details
        if (gitData && gitData.length > 0) {
            gitData.slice(0, 8).forEach(commit => {
                activities.push({
                    type: 'commit',
                    time: commit.timestamp,
                    title: '📝 Code Committed',
                    details: utils.truncate(commit.message, 100),
                    meta: [
                        { label: 'SHA', value: commit.short_hash },
                        { label: 'Author', value: commit.author },
                        { label: 'Branch', value: commit.branch },
                        { label: 'Files', value: `${commit.files_changed || 'N/A'} changed` }
                    ]
                });
            });
        }

        // Add GitHub Actions runs
        if (githubData?.recent_runs) {
            githubData.recent_runs.slice(0, 5).forEach(run => {
                const status = run.status === 'completed' ? 
                    (run.conclusion === 'success' ? 'success' : 'failure') : 'running';
                
                const icon = status === 'success' ? '✅' : status === 'failure' ? '❌' : '⏳';
                
                activities.push({
                    type: 'ci',
                    time: run.updated_at,
                    title: `${icon} CI Pipeline ${run.status === 'completed' ? 'Completed' : 'Running'}`,
                    details: `${run.name} - Result: ${run.conclusion || run.status}`,
                    meta: [
                        { label: 'Run ID', value: `#${run.id}` },
                        { label: 'Status', value: run.conclusion || run.status },
                        { label: 'Started', value: utils.formatDateTime(run.created_at) },
                        { label: 'Duration', value: utils.formatDate(run.created_at) }
                    ]
                });
            });
        }

        // Add Docker events
        if (dockerData) {
            activities.push({
                type: 'docker',
                time: dockerData.created,
                title: `🐳 Docker Container ${dockerData.status === 'running' ? 'Running' : 'Stopped'}`,
                details: `Container ${dockerData.name} - Image: ${dockerData.image}`,
                meta: [
                    { label: 'Image', value: dockerData.image },
                    { label: 'Status', value: dockerData.status },
                    { label: 'Created', value: utils.formatDateTime(dockerData.created) },
                    { label: 'Ports', value: Object.keys(dockerData.ports).join(', ') || 'None' }
                ]
            });
        }

        // Sort by time (most recent first)
        activities.sort((a, b) => new Date(b.time) - new Date(a.time));

        // Update count
        document.getElementById('eventCount').textContent = `${activities.length} events`;

        // Render
        const html = activities.length > 0 ? activities.map(activity => `
            <div class="activity-item">
                <div class="activity-header">
                    <span class="activity-type ${activity.type}">${activity.type}</span>
                    <span class="activity-time">${utils.formatDateTime(activity.time)}</span>
                </div>
                <div class="activity-title">${activity.title}</div>
                <div class="activity-details">${activity.details}</div>
                <div class="activity-meta">
                    ${activity.meta.map(m => `<span class="meta-tag">${m.label}: ${m.value}</span>`).join('')}
                </div>
            </div>
        `).join('') : '<div class="loading-state">No activity to display</div>';

        document.getElementById('activityLogContent').innerHTML = html;
    },

    // Render build status card
    buildStatus(githubData) {
        const latestRun = githubData?.latest_run;
        
        if (!latestRun) {
            document.getElementById('buildStatusBadge').textContent = 'Unknown';
            document.getElementById('buildStatusBadge').className = 'status-badge pending';
            document.getElementById('buildStatusContent').innerHTML = '<div class="loading-state">No build data available</div>';
            return;
        }

        const status = latestRun.status === 'completed' ? 
            (latestRun.conclusion === 'success' ? 'success' : 'failure') : 'running';
        
        document.getElementById('buildStatusBadge').textContent = latestRun.conclusion || latestRun.status;
        document.getElementById('buildStatusBadge').className = `status-badge ${status}`;

        const html = `
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Workflow</div>
                    <div class="info-value">${latestRun.name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Run ID</div>
                    <div class="info-value mono">#${latestRun.id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Started</div>
                    <div class="info-value">${utils.formatDateTime(latestRun.created_at)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Updated</div>
                    <div class="info-value">${utils.formatDateTime(latestRun.updated_at)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Success Rate</div>
                    <div class="info-value">${Math.round(githubData.success_rate * 100)}%</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Recent Runs</div>
                    <div class="info-value">${githubData.recent_runs.length}</div>
                </div>
            </div>
        `;

        document.getElementById('buildStatusContent').innerHTML = html;
    },

    // Render Docker card
    dockerCard(dockerData, gitData) {
        if (!dockerData) {
            document.getElementById('dockerCardContent').innerHTML = `
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Status</div>
                        <div class="info-value">
                            <span class="status-badge failure">NOT RUNNING</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Container</div>
                        <div class="info-value mono">${CONFIG.containerName}</div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-border); font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.6;">
                    <strong style="color: var(--color-text-primary);">🐳 Why Docker?</strong><br>
                    • <strong>Consistency:</strong> Same environment everywhere (dev, test, prod)<br>
                    • <strong>Isolation:</strong> Dependencies packaged with application<br>
                    • <strong>Portability:</strong> Run anywhere Docker is installed<br>
                    • <strong>Reproducibility:</strong> Exact same build every time<br>
                    • <strong>Efficiency:</strong> Fast startup, minimal overhead
                </div>
            `;
            return;
        }

        const latestCommit = gitData && gitData.length > 0 ? gitData[0] : null;

        const html = `
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Image</div>
                    <div class="info-value mono">${dockerData.image}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Container</div>
                    <div class="info-value mono">${dockerData.name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Status</div>
                    <div class="info-value">
                        <span class="status-badge ${dockerData.status === 'running' ? 'success' : 'failure'}">
                            ${dockerData.status.toUpperCase()}
                        </span>
                    </div>
                </div>
                <div class="info-item">
                    <div class="info-label">Created</div>
                    <div class="info-value">${utils.formatDateTime(dockerData.created)}</div>
                </div>
                ${latestCommit ? `
                <div class="info-item">
                    <div class="info-label">Built from Commit</div>
                    <div class="info-value mono">${latestCommit.short_hash}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Commit Message</div>
                    <div class="info-value">${utils.truncate(latestCommit.message, 40)}</div>
                </div>
                ` : ''}
                <div class="info-item">
                    <div class="info-label">Ports</div>
                    <div class="info-value mono">${Object.entries(dockerData.ports).map(([k, v]) => `${k}→${v}`).join(', ') || 'None'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Uptime</div>
                    <div class="info-value">${utils.formatDate(dockerData.created)}</div>
                </div>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-border); font-size: 0.8125rem; color: var(--color-text-secondary); line-height: 1.6;">
                <strong style="color: var(--color-text-primary);">🐳 Why Docker?</strong><br>
                • <strong>Consistency:</strong> Same environment everywhere (dev, test, prod)<br>
                • <strong>Isolation:</strong> Dependencies packaged with application<br>
                • <strong>Portability:</strong> Run anywhere Docker is installed<br>
                • <strong>Reproducibility:</strong> Exact same build every time<br>
                • <strong>Efficiency:</strong> Fast startup, minimal overhead
            </div>
        `;

        document.getElementById('dockerCardContent').innerHTML = html;
    },

    // Render deployment card
    deploymentCard(dockerData, gitData) {
        const isDeployed = dockerData?.status === 'running';
        const latestCommit = gitData && gitData.length > 0 ? gitData[0] : null;

        document.getElementById('deploymentStatusBadge').textContent = isDeployed ? 'Running' : 'Stopped';
        document.getElementById('deploymentStatusBadge').className = `status-badge ${isDeployed ? 'success' : 'failure'}`;

        const html = `
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Environment</div>
                    <div class="info-value">Production</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Service</div>
                    <div class="info-value">ECU Log Visualizer</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Endpoint</div>
                    <div class="info-value mono">http://localhost:8000</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Health Check</div>
                    <div class="info-value">/health</div>
                </div>
                ${latestCommit ? `
                <div class="info-item">
                    <div class="info-label">Deployed Version</div>
                    <div class="info-value mono">${latestCommit.short_hash}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Deployed</div>
                    <div class="info-value">${utils.formatDateTime(latestCommit.timestamp)}</div>
                </div>
                ` : ''}
            </div>
        `;

        document.getElementById('deploymentCardContent').innerHTML = html;
    },

    // Render repository stats
    repoStats(gitStats) {
        if (!gitStats) {
            document.getElementById('repoStatsGrid').innerHTML = '<div class="loading-state">No repository data available</div>';
            return;
        }

        const html = `
            <div class="stat-item">
                <div class="stat-label">Total Commits</div>
                <div class="stat-value">${gitStats.total_commits}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Contributors</div>
                <div class="stat-value">${gitStats.contributors}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Branches</div>
                <div class="stat-value">${gitStats.branches.length}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Current Branch</div>
                <div class="stat-value">${gitStats.current_branch}</div>
            </div>
        `;

        document.getElementById('repoStatsGrid').innerHTML = html;
    }
};

// Dashboard Controller
const dashboard = {
    async loadAllData() {
        try {
            // Fetch all data in parallel
            const [gitCommits, gitStats, githubStatus, dockerStatus] = await Promise.all([
                api.fetchGitCommits(),
                api.fetchGitStats(),
                api.fetchGitHubStatus(),
                api.fetchDockerStatus()
            ]);

            // Update state
            state.gitData = gitCommits;
            state.githubData = githubStatus;
            state.dockerData = dockerStatus;
            state.lastUpdate = new Date();

            // Render all components
            render.updateMetrics(gitCommits, githubStatus, dockerStatus);
            render.pipelineFlow(gitCommits, githubStatus, dockerStatus);
            render.activityLog(gitCommits, githubStatus, dockerStatus);
            render.buildStatus(githubStatus);
            render.dockerCard(dockerStatus, gitCommits);
            render.deploymentCard(dockerStatus, gitCommits);
            render.repoStats(gitStats);

            // Update last update time
            this.updateLastUpdateTime();

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
        }
    },

    updateLastUpdateTime() {
        if (state.lastUpdate) {
            const timeStr = state.lastUpdate.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            document.getElementById('lastUpdate').textContent = `Last update: ${timeStr}`;
        }
    },

    startAutoRefresh() {
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
        }

        state.refreshTimer = setInterval(() => {
            this.loadAllData();
        }, CONFIG.refreshInterval);
    },

    stopAutoRefresh() {
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
            state.refreshTimer = null;
        }
    }
};

// Event Handlers
function setupEventHandlers() {
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            dashboard.loadAllData();
        });
    }

    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            dashboard.stopAutoRefresh();
        } else {
            dashboard.startAutoRefresh();
            dashboard.loadAllData();
        }
    });
}

// Initialize
function init() {
    console.log('Initializing DevOps Pipeline Dashboard V3...');
    setupEventHandlers();
    dashboard.loadAllData();
    dashboard.startAutoRefresh();
    console.log('Dashboard initialized successfully');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
