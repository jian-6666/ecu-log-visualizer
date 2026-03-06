// ECU Log Visualizer - Frontend Application

class ECULogVisualizer {
    constructor() {
        this.currentFileId = null;
        this.currentFilters = {
            startTime: null,
            endTime: null,
            sensors: []
        };
        this.availableSensors = [];
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });
        
        // Filter controls
        document.getElementById('applyFilters').addEventListener('click', () => this.applyFilters());
        document.getElementById('clearFilters').addEventListener('click', () => this.clearFilters());
        
        // Export buttons
        document.getElementById('exportCSV').addEventListener('click', () => this.exportData('csv'));
        document.getElementById('exportJSON').addEventListener('click', () => this.exportData('json'));
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        // Validate file
        const validExtensions = ['.csv', '.json'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!validExtensions.includes(fileExtension)) {
            this.showMessage('请上传 CSV 或 JSON 格式的文件', 'error');
            return;
        }
        
        if (file.size > 50 * 1024 * 1024) {
            this.showMessage('文件大小不能超过 50MB', 'error');
            return;
        }
        
        // Show progress
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        progressContainer.style.display = 'block';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || '上传失败');
            }
            
            const data = await response.json();
            this.currentFileId = data.file_id;
            
            progressFill.style.width = '100%';
            progressText.textContent = '100%';
            
            this.showMessage(`文件上传成功！文件 ID: ${data.file_id}`, 'success');
            
            // Load data
            await this.loadData();
            
        } catch (error) {
            this.showMessage(`上传失败: ${error.message}`, 'error');
            console.error('Upload error:', error);
        } finally {
            this.showLoading(false);
            setTimeout(() => {
                progressContainer.style.display = 'none';
                progressFill.style.width = '0%';
            }, 2000);
        }
    }

    async loadData() {
        if (!this.currentFileId) return;
        
        try {
            this.showLoading(true);
            
            // Load statistics and chart in parallel
            await Promise.all([
                this.loadStatistics(),
                this.loadChart()
            ]);
            
            // Show sections
            document.getElementById('filterSection').style.display = 'block';
            document.getElementById('statsSection').style.display = 'block';
            document.getElementById('chartSection').style.display = 'block';
            document.getElementById('exportSection').style.display = 'block';
            
        } catch (error) {
            this.showMessage(`加载数据失败: ${error.message}`, 'error');
            console.error('Load data error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    async loadStatistics() {
        const params = new URLSearchParams();
        if (this.currentFilters.startTime) {
            params.append('start_time', this.currentFilters.startTime);
        }
        if (this.currentFilters.endTime) {
            params.append('end_time', this.currentFilters.endTime);
        }
        if (this.currentFilters.sensors.length > 0) {
            params.append('sensors', this.currentFilters.sensors.join(','));
        }
        
        const url = `/api/stats/${this.currentFileId}${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || '获取统计信息失败');
        }
        
        const data = await response.json();
        this.displayStatistics(data);
        
        // Update available sensors
        this.availableSensors = Object.keys(data.sensors);
        this.updateSensorSelect();
    }

    displayStatistics(data) {
        const tbody = document.getElementById('statsTableBody');
        tbody.innerHTML = '';
        
        for (const [sensorName, stats] of Object.entries(data.sensors)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${sensorName}</strong></td>
                <td>${stats.min.toFixed(2)}</td>
                <td>${stats.max.toFixed(2)}</td>
                <td>${stats.mean.toFixed(2)}</td>
                <td>${stats.std.toFixed(2)}</td>
                <td>${stats.count}</td>
            `;
            tbody.appendChild(row);
        }
    }

    async loadChart() {
        const params = new URLSearchParams();
        if (this.currentFilters.startTime) {
            params.append('start_time', this.currentFilters.startTime);
        }
        if (this.currentFilters.endTime) {
            params.append('end_time', this.currentFilters.endTime);
        }
        if (this.currentFilters.sensors.length > 0) {
            params.append('sensors', this.currentFilters.sensors.join(','));
        }
        
        const url = `/api/chart/${this.currentFileId}${params.toString() ? '?' + params.toString() : ''}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail?.message || '获取图表数据失败');
        }
        
        const chartData = await response.json();
        this.displayChart(chartData);
    }

    displayChart(chartData) {
        const container = document.getElementById('chartContainer');
        
        const layout = {
            ...chartData.layout,
            autosize: true,
            margin: { l: 60, r: 30, t: 40, b: 60 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false
        };
        
        Plotly.newPlot(container, chartData.data, layout, config);
    }

    updateSensorSelect() {
        const select = document.getElementById('sensorSelect');
        select.innerHTML = '';
        
        this.availableSensors.forEach(sensor => {
            const option = document.createElement('option');
            option.value = sensor;
            option.textContent = sensor;
            if (this.currentFilters.sensors.includes(sensor)) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    }

    async applyFilters() {
        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        const sensorSelect = document.getElementById('sensorSelect');
        const selectedSensors = Array.from(sensorSelect.selectedOptions).map(opt => opt.value);
        
        // Update filters
        this.currentFilters.startTime = startTime || null;
        this.currentFilters.endTime = endTime || null;
        this.currentFilters.sensors = selectedSensors;
        
        // Reload data with filters
        try {
            this.showLoading(true);
            await Promise.all([
                this.loadStatistics(),
                this.loadChart()
            ]);
            this.showMessage('过滤器已应用', 'success');
        } catch (error) {
            this.showMessage(`应用过滤器失败: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    clearFilters() {
        // Clear filter inputs
        document.getElementById('startTime').value = '';
        document.getElementById('endTime').value = '';
        document.getElementById('sensorSelect').selectedIndex = -1;
        
        // Reset filters
        this.currentFilters = {
            startTime: null,
            endTime: null,
            sensors: []
        };
        
        // Reload data without filters
        this.applyFilters();
    }

    async exportData(format) {
        if (!this.currentFileId) {
            this.showMessage('请先上传文件', 'error');
            return;
        }
        
        const params = new URLSearchParams({ format });
        if (this.currentFilters.startTime) {
            params.append('start_time', this.currentFilters.startTime);
        }
        if (this.currentFilters.endTime) {
            params.append('end_time', this.currentFilters.endTime);
        }
        if (this.currentFilters.sensors.length > 0) {
            params.append('sensors', this.currentFilters.sensors.join(','));
        }
        
        const url = `/api/export/${this.currentFileId}?${params.toString()}`;
        
        try {
            this.showLoading(true);
            
            const response = await fetch(url);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail?.message || '导出失败');
            }
            
            // Get filename from Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `export_${this.currentFileId}.${format}`;
            if (contentDisposition) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
                if (matches && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }
            
            // Download file
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
            
            this.showMessage(`数据已导出为 ${format.toUpperCase()} 格式`, 'success');
            
        } catch (error) {
            this.showMessage(`导出失败: ${error.message}`, 'error');
            console.error('Export error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    showMessage(message, type) {
        const messageEl = document.getElementById('uploadMessage');
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.style.display = 'block';
        
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 5000);
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ECULogVisualizer();
});
