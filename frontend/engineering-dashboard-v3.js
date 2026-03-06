// ===== DevOps Pipeline Dashboard V3 - Complete Implementation =====

// Configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    apiBaseUrl: '/api/engineering',
    repoOwner: 'your-org',
    repoName: 'ecu-log-visualizer',
    jenkinsUrl: 'http://localhost:8080',
    jenkinsJob: 'ecu-log-visualizer',
    containerName: 'ecu-log-visualizer'
};

// State Management
const state = {
    gitData: null,
    githubData: null,
    jenkinsData: null,
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

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

    async fetchJenkinsStatus() {
        try {
            const url = `${CONFIG.apiBaseUrl}/cicd/jenkins?jenkins_url=${encodeURIComponent(CONFIG.jenkinsUrl)}&job_name=${CONFIG.jenkinsJob}`;
            const response = await fetch(url);
            if (!response.ok) return null;
            return await response.json();
        } catch (error) {
            console.error('Failed to fetch Jenkins status:', error);
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
    pipelineStages(gitData, githubData, dockerData, jenkinsData) {
        const stages = [
            {
                name: 'Code Commit',
                icon: '<path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>',
                status: gitData && gitData.length > 0 ? 'success' : 'pending',
                statusText: gitData && gitData.length > 0 ? 'Committed' : 'No commits'
            },
            {
                name: 'GitHub Actions',
                icon: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
                status: githubData?.latest_run ? 
                    (githubData.latest_run.status === 'completed' ? 
                        (githubData.latest_run.conclusion === 'success' ? 'success' : 'failure') 
                        : 'running') 
                    : 'pending',
                statusText: githubData?.latest_run ? 
                    (githubData.latest_run.status === 'completed' ? 
                        (githubData.latest_run.conclusion === 'success' ? 'Passed' : 'Failed') 
                        : 'Running') 
                    : 'Waiting'
            },
            {
                name: 'Docker Build',
                icon: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
                status: dockerData ? 'success' : 'pending',
                statusText: dockerData ? 'Built' : 'Waiting'
            },
            {
                name: 'Jenkins Validation',
                icon: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
                status: jenkinsData?.latest_build ? 
                    (jenkinsData.latest_build.status === 'SUCCESS' ? 'success' : 
                        jenkinsData.latest_build.status === 'IN_PROGRESS' ? 'running' : 'failure') 
                    : 'pending',
                statusText: jenkinsData?.latest_build ? 
                    (jenkinsData.latest_build.status === 'SUCCESS' ? 'Passed' : 
                        jenkinsData.latest_build.status === 'IN_PROGRESS' ? 'Running' : 'Failed') 
                    : 'Waiting'
            },
            {
                name: 'Deployment',
                icon: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
                status: dockerData?.status === 'running' ? 'success' : 'pending',
                statusText: dockerData?.status === 'running' ? 'Running' : 'Not deployed'
            }
        ];

        const stagesHtml = stages.map((stage, index) => `
            <div class="pipeline-stage">
                ${index < stages.length - 1 ? `<div class="stage-connector ${stage.status === 'success' ? 'active' : ''}"></div>` : ''}
                <div class="stage-icon-wrapper status-${stage.status}">
                    <svg class="stage-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${stage.icon}
                    </svg>
                </div>
                <div class="stage-info">
                    <div class="stage-name">${stage.name}</div>
                    <span class="stage-status ${stage.status}">${stage.statusText}</span>
                </div>
            </div>
        `).join('');

        document.getElementById('pipelineStages').innerHTML = stagesHtml;
    },

    pipelineSummary(gitData, githubData, dockerData) {
        const summary = {
            commits: gitData?.length || 0,
            successRate: githubData?.success_rate ? Math.round(githubData.success_rate * 100) : 0,
            uptime: dockerData?.status === 'running' ? '99.9%' : 'N/A',
            deployments: dockerData ? 1 : 0
        };

        const summaryHtml = `
            <div class="summary-item">
                <div class="summary-label">Total Commits</div>
                <div class="summary-value">${summary.commits}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">CI Success Rate</div>
                <div class="summary-value">${summary.successRate}%</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Service Uptime</div>
                <div class="summary-value">${summary.uptime}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Active Deployments</div>
                <div class="summary-value">${summary.deployments}</div>
            </div>
        `;

        document.getElementById('pipelineSummary').innerHTML = summaryHtml;
    },

    activityTimeline(gitData, githubData, jenkinsData, dockerData) {
        const events = [];

        // Add git commits
        if (gitData && gitData.length > 0) {
            gitData.slice(0, 5).forEach(commit => {
                events.push({
                    time: commit.timestamp,
                    type: 'success',
                    title: 'Code Committed',
                    description: utils.truncate(commit.message, 60),
                    meta: [
                        { label: 'SHA', value: commit.short_hash },
                        { label: 'Author', value: commit.author },
                        { label: 'Branch', value: commit.branch }
                    ]
                });
            });
        }

        // Add GitHub Actions runs
        if (githubData?.recent_runs) {
            githubData.recent_runs.slice(0, 3).forEach(run => {
                events.push({
                    time: run.updated_at,
                    type: run.status === 'completed' ? 
                        (run.conclusion === 'success' ? 'success' : 'failure') : 'running',
                    title: run.status === 'completed' ? 'CI Pipeline Completed' : 'CI Pipeline Running',
                    description: `${run.name} - ${run.conclusion || run.status}`,
                    meta: [
                        { label: 'Workflow', value: run.name },
                        { label: 'Status', value: run.conclusion || run.status }
                    ]
                });
            });
        }

        // Add Jenkins builds
        if (jenkinsData?.recent_builds) {
            jenkinsData.recent_builds.slice(0, 3).forEach(build => {
                events.push({
                    time: build.timestamp,
                    type: build.status === 'SUCCESS' ? 'success' : 
                        build.status === 'IN_PROGRESS' ? 'running' : 'failure',
                    title: 'Jenkins Validation',
                    description: `Build #${build.number} - ${build.status}`,
                    meta: [
                        { label: 'Build', value: `#${build.number}` },
                        { label: 'Status', value: build.status }
                    ]
                });
            });
        }

        // Add Docker status
        if (dockerData) {
            events.push({
                time: dockerData.created,
                type: dockerData.status === 'running' ? 'success' : 'failure',
                title: 'Container Status',
                description: `Container ${dockerData.name} is ${dockerData.status}`,
                meta: [
                    { label: 'Image', value: dockerData.image },
                    { label: 'Status', value: dockerData.status }
                ]
            });
        }

        // Sort by time (most recent first)
        events.sort((a, b) => new Date(b.time) - new Date(a.time));

        // Update event count
        document.getElementById('eventCount').textContent = `${events.length} events`;

        // Render timeline
        const timelineHtml = events.length > 0 ? events.map(event => `
            <div class="timeline-event event-${event.type}">
                <div class="event-time">${utils.formatDateTime(event.time)}</div>
                <div class="event-title">${event.title}</div>
                <div class="event-description">${event.description}</div>
                <div class="event-meta">
                    ${event.meta.map(m => `<span class="event-tag">${m.label}: ${m.value}</span>`).join('')}
                </div>
            </div>
        `).join('') : '<div class="empty-state"><div class="empty-state-text">No activity to display</div></div>';

        document.getElementById('timelineContent').innerHTML = timelineHtml;
    },

    githubPanel(gitData, gitStats) {
        if (!gitData || gitData.length === 0) {
            document.getElementById('githubContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">No Git repository data available</div>
                </div>
            `;
            return;
        }

        const recentCommits = gitData.slice(0, 5);
        const remoteUrl = gitStats?.remote_url || '';
        const isGitHub = remoteUrl.includes('github.com');

        const html = `
            <div class="commit-list">
                ${recentCommits.map(commit => `
                    <div class="commit-item">
                        <div class="commit-header">
                            <div class="commit-message">${utils.truncate(commit.message, 50)}</div>
                            <span class="commit-sha">${commit.short_hash}</span>
                        </div>
                        <div class="commit-meta">
                            <span class="commit-author">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                                    <circle cx="12" cy="7" r="4"/>
                                </svg>
                                ${commit.author}
                            </span>
                            <span class="commit-time">${utils.formatDate(commit.timestamp)}</span>
                            <span class="commit-branch">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="6" y1="3" x2="6" y2="15"/>
                                    <circle cx="18" cy="6" r="3"/>
                                    <circle cx="6" cy="18" r="3"/>
                                    <path d="M18 9a9 9 0 0 1-9 9"/>
                                </svg>
                                ${commit.branch}
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${gitStats ? `
                <div class="workflow-details" style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--color-border);">
                    <div class="detail-item">
                        <div class="detail-label">Total Commits</div>
                        <div class="detail-value">${gitStats.total_commits}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Contributors</div>
                        <div class="detail-value">${gitStats.contributors}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Current Branch</div>
                        <div class="detail-value mono">${gitStats.current_branch}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Total Branches</div>
                        <div class="detail-value">${gitStats.branches.length}</div>
                    </div>
                </div>
            ` : ''}
        `;

        document.getElementById('githubContent').innerHTML = html;
    },

    cicdPanel(githubData, jenkinsData) {
        let html = '';

        // GitHub Actions Section
        if (githubData?.latest_run) {
            const run = githubData.latest_run;
            const status = run.status === 'completed' ? 
                (run.conclusion === 'success' ? 'success' : 'failure') : 'running';

            html += `
                <div class="workflow-status">
                    <div class="workflow-header">
                        <div class="workflow-name">GitHub Actions</div>
                        <span class="workflow-badge ${status}">${run.conclusion || run.status}</span>
                    </div>
                    <div class="workflow-details">
                        <div class="detail-item">
                            <div class="detail-label">Workflow</div>
                            <div class="detail-value">${run.name}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Run ID</div>
                            <div class="detail-value mono">#${run.id}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Started</div>
                            <div class="detail-value">${utils.formatDateTime(run.created_at)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Updated</div>
                            <div class="detail-value">${utils.formatDateTime(run.updated_at)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Success Rate</div>
                            <div class="detail-value">${Math.round(githubData.success_rate * 100)}%</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Recent Runs</div>
                            <div class="detail-value">${githubData.recent_runs.length}</div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Jenkins Section
        if (jenkinsData?.latest_build) {
            const build = jenkinsData.latest_build;
            const status = build.status === 'SUCCESS' ? 'success' : 
                build.status === 'IN_PROGRESS' ? 'running' : 'failure';

            html += `
                <div class="workflow-status" style="margin-top: 1.5rem;">
                    <div class="workflow-header">
                        <div class="workflow-name">Jenkins Pipeline</div>
                        <span class="workflow-badge ${status}">${build.status}</span>
                    </div>
                    <div class="workflow-details">
                        <div class="detail-item">
                            <div class="detail-label">Build Number</div>
                            <div class="detail-value mono">#${build.number}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Duration</div>
                            <div class="detail-value">${Math.round(build.duration / 1000)}s</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Started</div>
                            <div class="detail-value">${utils.formatDateTime(build.timestamp)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Success Rate</div>
                            <div class="detail-value">${Math.round(jenkinsData.success_rate * 100)}%</div>
                        </div>
                    </div>
                </div>
            `;
        }

        if (!html) {
            html = '<div class="empty-state"><div class="empty-state-text">No CI/CD data available</div></div>';
        }

        document.getElementById('cicdContent').innerHTML = html;
    },

    dockerPanel(dockerData) {
        if (!dockerData) {
            document.getElementById('dockerContent').innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-text">Docker container not found or Docker daemon not accessible</div>
                </div>
            `;
            return;
        }

        const html = `
            <div class="docker-info">
                <div class="docker-section">
                    <div class="docker-section-title">Container Packaging</div>
                    <div class="docker-description">
                        Docker packages the application with all dependencies into a reproducible, 
                        portable container image. This ensures consistent behavior across development, 
                        testing, and production environments.
                    </div>
                    <div class="docker-stats">
                        <div class="detail-item">
                            <div class="detail-label">Image</div>
                            <div class="detail-value mono">${dockerData.image}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Container</div>
                            <div class="detail-value mono">${dockerData.name}</div>
                        </div>
                    </div>
                </div>

                <div class="docker-section">
                    <div class="docker-section-title">Runtime Status</div>
                    <div class="docker-description">
                        The containerized application is currently ${dockerData.status}. 
                        Docker provides isolation, resource management, and easy deployment 
                        across different infrastructure platforms.
                    </div>
                    <div class="docker-stats">
                        <div class="detail-item">
                            <div class="detail-label">Status</div>
                            <div class="detail-value">
                                <span class="workflow-badge ${dockerData.status === 'running' ? 'success' : 'failure'}">
                                    ${dockerData.status.toUpperCase()}
                                </span>
                            </div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Health</div>
                            <div class="detail-value">${dockerData.health || 'N/A'}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Created</div>
                            <div class="detail-value">${utils.formatDateTime(dockerData.created)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Ports</div>
                            <div class="detail-value mono">${Object.entries(dockerData.ports).map(([k, v]) => `${k}→${v}`).join(', ') || 'None'}</div>
                        </div>
                    </div>
                </div>

                <div class="docker-section">
                    <div class="docker-section-title">Deployment Benefits</div>
                    <div class="docker-description">
                        • <strong>Reproducibility:</strong> Same image runs identically everywhere<br>
                        • <strong>Isolation:</strong> Application dependencies don't conflict with host<br>
                        • <strong>Scalability:</strong> Easy to replicate and scale horizontally<br>
                        • <strong>Version Control:</strong> Image tags enable rollback and versioning
                    </div>
                </div>
            </div>
        `;

        document.getElementById('dockerContent').innerHTML = html;
    },

    deploymentPanel(dockerData, gitData) {
        const isDeployed = dockerData?.status === 'running';
        const latestCommit = gitData && gitData.length > 0 ? gitData[0] : null;

        const html = `
            <div class="deployment-info">
                <div class="deployment-status-card ${!isDeployed ? 'error' : ''}">
                    <div class="deployment-header">
                        <div class="deployment-title">Service Status</div>
                        <span class="workflow-badge ${isDeployed ? 'success' : 'failure'}">
                            ${isDeployed ? 'RUNNING' : 'STOPPED'}
                        </span>
                    </div>
                    <div class="deployment-stats">
                        <div class="detail-item">
                            <div class="detail-label">Environment</div>
                            <div class="detail-value">Production</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Service</div>
                            <div class="detail-value">ECU Log Visualizer</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Endpoint</div>
                            <div class="detail-value mono">http://localhost:8000</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">Health Check</div>
                            <div class="detail-value">/health</div>
                        </div>
                    </div>
                </div>

                ${latestCommit ? `
                    <div class="docker-section">
                        <div class="docker-section-title">Deployed Version</div>
                        <div class="docker-stats">
                            <div class="detail-item">
                                <div class="detail-label">Commit SHA</div>
                                <div class="detail-value mono">${latestCommit.short_hash}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Branch</div>
                                <div class="detail-value mono">${latestCommit.branch}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Author</div>
                                <div class="detail-value">${latestCommit.author}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-label">Deployed</div>
                                <div class="detail-value">${utils.formatDateTime(latestCommit.timestamp)}</div>
                            </div>
                        </div>
                        <div class="docker-description" style="margin-top: 1rem;">
                            ${utils.truncate(latestCommit.message, 100)}
                        </div>
                    </div>
                ` : ''}

                <div class="docker-section">
                    <div class="docker-section-title">Deployment Pipeline</div>
                    <div class="docker-description">
                        The complete DevOps pipeline ensures code quality and reliability:<br><br>
                        <strong>1. Developer Commit:</strong> Code changes pushed to GitHub<br>
                        <strong>2. GitHub Actions CI:</strong> Automated tests and quality checks<br>
                        <strong>3. Docker Build:</strong> Application packaged into container image<br>
                        <strong>4. Jenkins Validation:</strong> Integration tests and security scans<br>
                        <strong>5. Deployment:</strong> Container deployed to production environment
                    </div>
                </div>
            </div>
        `;

        document.getElementById('deploymentContent').innerHTML = html;
    }
};

// Main Dashboard Controller
const dashboard = {
    async loadAllData() {
        try {
            // Show loading state
            this.showLoading();

            // Fetch all data in parallel
            const [gitCommits, gitStats, githubStatus, jenkinsStatus, dockerStatus] = await Promise.all([
                api.fetchGitCommits(),
                api.fetchGitStats(),
                api.fetchGitHubStatus(),
                api.fetchJenkinsStatus(),
                api.fetchDockerStatus()
            ]);

            // Update state
            state.gitData = gitCommits;
            state.githubData = githubStatus;
            state.jenkinsData = jenkinsStatus;
            state.dockerData = dockerStatus;
            state.lastUpdate = new Date();

            // Render all components
            render.pipelineStages(gitCommits, githubStatus, dockerStatus, jenkinsStatus);
            render.pipelineSummary(gitCommits, githubStatus, dockerStatus);
            render.activityTimeline(gitCommits, githubStatus, jenkinsStatus, dockerStatus);
            render.githubPanel(gitCommits, gitStats);
            render.cicdPanel(githubStatus, jenkinsStatus);
            render.dockerPanel(dockerStatus);
            render.deploymentPanel(dockerStatus, gitCommits);

            // Update last update time
            this.updateLastUpdateTime();

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError();
        }
    },

    showLoading() {
        const loadingHtml = '<div class="loading-state">Loading...</div>';
        document.getElementById('pipelineStages').innerHTML = loadingHtml;
        document.getElementById('timelineContent').innerHTML = loadingHtml;
        document.getElementById('githubContent').innerHTML = loadingHtml;
        document.getElementById('cicdContent').innerHTML = loadingHtml;
        document.getElementById('dockerContent').innerHTML = loadingHtml;
        document.getElementById('deploymentContent').innerHTML = loadingHtml;
    },

    showError() {
        const errorHtml = '<div class="empty-state"><div class="empty-state-text">Failed to load data. Please try again.</div></div>';
        document.getElementById('timelineContent').innerHTML = errorHtml;
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
        // Clear existing timer
        if (state.refreshTimer) {
            clearInterval(state.refreshTimer);
        }

        // Set up new timer
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
    // Refresh button
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            dashboard.loadAllData();
        });
    }

    // Handle visibility change to pause/resume auto-refresh
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            dashboard.stopAutoRefresh();
        } else {
            dashboard.startAutoRefresh();
            dashboard.loadAllData();
        }
    });
}

// Initialize Dashboard
function init() {
    console.log('Initializing DevOps Pipeline Dashboard V3...');
    
    // Setup event handlers
    setupEventHandlers();
    
    // Load initial data
    dashboard.loadAllData();
    
    // Start auto-refresh
    dashboard.startAutoRefresh();
    
    console.log('Dashboard initialized successfully');
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
