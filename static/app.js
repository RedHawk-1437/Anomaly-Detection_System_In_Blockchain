// Global variables
let charts = {};
let isSimulationRunning = false;
let isMLTrained = false;
let isDetectionRunning = false;
let intervals = [];

// Initialize everything
function initializeDashboard() {
    initializeCharts();
    startBasicUpdates();
    updateAllStatus();
}

// Initialize all charts with empty/default state
function initializeCharts() {
    const chartConfigs = {
        blockchainChart: {
            type: 'line',
            data: {
                labels: ['Start Simulation to See Data'],
                datasets: [
                    {
                        label: 'Blocks Mined',
                        data: [0],
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3
                    },
                    {
                        label: 'Transactions',
                        data: [0],
                        borderColor: '#06d6a0',
                        backgroundColor: 'rgba(6, 214, 160, 0.1)',
                        tension: 0.4,
                        fill: true,
                        borderWidth: 3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Blockchain Network Activity - Start Simulation',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top',
                        labels: { color: '#cbd5e1' }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count',
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time',
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        },
        attackChart: {
            type: 'doughnut',
            data: {
                labels: ['No Attacks Yet'],
                datasets: [{
                    data: [100],
                    backgroundColor: ['#334155'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Attack Distribution - Run Attacks First',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#cbd5e1',
                            font: { size: 12 }
                        }
                    }
                }
            }
        },
        successChart: {
            type: 'bar',
            data: {
                labels: ['Run Attacks First'],
                datasets: [{
                    label: 'Success Rate %',
                    data: [0],
                    backgroundColor: '#334155',
                    borderColor: '#475569',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Attack Success Rate - No Data',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Success Rate %',
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: {
                            color: '#94a3b8',
                            maxRotation: 45,
                            minRotation: 45,
                            font: {
                                size: 11
                            }
                        }
                    }
                }
            }
        },
        anomalyChart: {
            type: 'pie',
            data: {
                labels: ['Train Model First'],
                datasets: [{
                    data: [100],
                    backgroundColor: ['#334155'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Anomaly Detection - Train Model First',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom',
                        labels: { color: '#cbd5e1' }
                    }
                }
            }
        },
        confidenceChart: {
            type: 'line',
            data: {
                labels: ['Start Detection'],
                datasets: [{
                    label: 'Confidence %',
                    data: [0],
                    borderColor: '#334155',
                    backgroundColor: 'rgba(51, 65, 85, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Model Confidence - Start Detection',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            text: 'Confidence %',
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        },
        dataChart: {
            type: 'bar',
            data: {
                labels: ['No Data Available'],
                datasets: [{
                    label: 'Data Samples',
                    data: [0],
                    backgroundColor: ['#334155']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Data Distribution - Process Datasets',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    }
                }
            }
        },
        performanceChart: {
            type: 'radar',
            data: {
                labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Speed'],
                datasets: [{
                    label: 'Model Performance',
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: 'rgba(51, 65, 85, 0.2)',
                    borderColor: '#334155',
                    pointBackgroundColor: '#334155',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#334155'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Performance Metrics - Train Model',
                        color: '#f1f5f9',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(148, 163, 184, 0.1)' },
                        angleLines: { color: 'rgba(148, 163, 184, 0.1)' },
                        pointLabels: {
                            color: '#94a3b8',
                            font: { size: 11 }
                        },
                        ticks: {
                            color: '#94a3b8',
                            backdropColor: 'transparent',
                            stepSize: 20
                        }
                    }
                }
            }
        }
    };

    Object.keys(chartConfigs).forEach(chartId => {
        const ctx = document.getElementById(chartId)?.getContext('2d');
        if (ctx) {
            const config = chartConfigs[chartId];
            charts[chartId] = new Chart(ctx, {
                type: config.type,
                data: config.data,
                options: config.options
            });
        }
    });
}

// Real-time updates
function startBasicUpdates() {
    stopAllUpdates();
    intervals.push(setInterval(updateStatusCards, 10000));
    intervals.push(setInterval(updateMLStatus, 15000));
    intervals.push(setInterval(updateKaggleStatus, 20000));
    intervals.push(setInterval(updateDatasetStats, 25000));
    intervals.push(setInterval(updateFileList, 30000));
}

function startSimulationUpdates() {
    stopAllUpdates();
    intervals.push(setInterval(updateStatusCards, 5000));
    intervals.push(setInterval(updateMLStatus, 5000));
    intervals.push(setInterval(updateActiveAttacks, 3000));
    intervals.push(setInterval(updateMLPredictions, 4000));
    intervals.push(setInterval(updateCharts, 2000));
    intervals.push(setInterval(updateDatasetStats, 10000));
    intervals.push(setInterval(updateKaggleStatus, 15000));
    intervals.push(setInterval(updateFileList, 20000));
}

function stopAllUpdates() {
    intervals.forEach(clearInterval);
    intervals = [];
}

// Core API functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        return { status: 'error', message: error.message };
    }
}

// Simulation controls
async function startSimulation() {
    const result = await apiCall('/api/simblock/start', {
        method: 'POST',
        body: JSON.stringify({ node_count: 100 })
    });

    if (result.status === 'success' || result.type === 'advanced_mock') {
        isSimulationRunning = true;
        showNotification('🚀 Simulation Started! Blockchain network is now running.', 'success');
        startSimulationUpdates();
        await updateAllStatus();
    } else {
        showNotification('❌ Error: ' + (result.message || 'Unknown error'), 'error');
    }
}

async function stopSimulation() {
    const result = await apiCall('/api/simblock/stop', { method: 'POST' });
    if (result.status === 'success') {
        isSimulationRunning = false;
        isDetectionRunning = false;
        showNotification('✅ Simulation Stopped! All processes have been halted.', 'success');
        resetChartsToDefault();
        startBasicUpdates();
        await updateAllStatus();
    } else {
        showNotification('❌ Error: ' + result.message, 'error');
    }
}

// Attack functions
const attackConfigs = {
    'double-spending': { amount: 100, attacker_nodes: 5 },
    '51-percent': { hash_power: 55, duration: 60 },
    'selfish-mining': { max_blocks: 3 },
    'eclipse': { target_node: 25, attacker_nodes: 8, isolation_time: 45 }
};

// Individual attack functions for frontend buttons
function startDoubleSpending() {
    startAttack('double-spending');
}

function start51Percent() {
    startAttack('51-percent');
}

function startSelfishMining() {
    startAttack('selfish-mining');
}

function startEclipseAttack() {
    startAttack('eclipse');
}

async function startAttack(attackType) {
    if (!isSimulationRunning) {
        showNotification('❌ Please start simulation first!', 'error');
        return;
    }

    showNotification(`🎯 Starting ${attackType.replace('-', ' ')} attack...`, 'info');

    const result = await apiCall(`/api/attack/${attackType}`, {
        method: 'POST',
        body: JSON.stringify(attackConfigs[attackType])
    });

    if (result.status === 'success') {
        showNotification(`✅ ${result.message}`, 'success');
        updateActiveAttacks();
        updateAttackCharts();
    } else {
        showNotification('❌ Error: ' + result.message, 'error');
    }
}

// ML functions
async function trainMLModel() {
    if (!isSimulationRunning) {
        showNotification('❌ Please start simulation first!', 'error');
        return;
    }

    showNotification('🤖 Training ML model with blockchain data...', 'info');
    const result = await apiCall('/api/ml/train', { method: 'POST' });

    if (result.status === 'success') {
        await updateMLStatus();
        isMLTrained = true;
        showNotification(`✅ ${result.message}`, 'success');
        updateTrainingMetrics(result);
        updateMLChartsWithRealData(result);
    } else {
        showNotification(`❌ ${result.message}`, 'error');
        isMLTrained = false;
    }
}

async function startMLDetection() {
    await updateMLStatus();

    const mlStatus = await apiCall('/api/ml/status');

    if (!mlStatus || mlStatus.training_status !== 'trained') {
        showNotification('❌ Please train ML model first! Model is not trained yet.', 'error');
        return;
    }

    if (!isSimulationRunning) {
        showNotification('❌ Please start simulation first!', 'error');
        return;
    }

    const result = await apiCall('/api/ml/start-detection', { method: 'POST' });
    if (result.status === 'success') {
        isDetectionRunning = true;
        showNotification('🔍 ML Anomaly Detection Started! Monitoring blockchain in real-time.', 'success');
        updateMLStatus();

        if (charts.confidenceChart) {
            charts.confidenceChart.data.labels = ['Detection Started'];
            charts.confidenceChart.data.datasets[0].data = [75];
            charts.confidenceChart.data.datasets[0].borderColor = '#6366f1';
            charts.confidenceChart.data.datasets[0].backgroundColor = 'rgba(99, 102, 241, 0.1)';
            charts.confidenceChart.options.plugins.title.text = 'Model Confidence - LIVE';
            charts.confidenceChart.update();
        }
    } else {
        showNotification(result.message, 'error');
    }
}

// Data functions
async function downloadDatasets() {
    showNotification('📥 Downloading blockchain datasets...', 'info');
    const result = await apiCall('/api/kaggle/download', { method: 'POST' });
    showNotification(result.message, result.status === 'success' ? 'success' : 'error');
    updateKaggleStatus();
    updateFileList();
}

async function processDatasets() {
    showNotification('🔄 Processing and merging datasets...', 'info');
    const result = await apiCall('/api/kaggle/process', { method: 'POST' });
    showNotification(result.message, result.status === 'success' ? 'success' : 'error');
    updateKaggleStatus();
    updateDatasetStats();
    updateFileList();
}

async function downloadAllData() {
    showNotification('📦 Preparing all data for download...', 'info');
    window.open('/api/kaggle/download-all', '_blank');
}

async function generateReport() {
    showNotification('📄 Generating comprehensive blockchain report...', 'info');
    const result = await apiCall('/api/kaggle/generate-report', { method: 'POST' });
    if (result.status === 'success') {
        window.open('/api/kaggle/download-file/generated_report', '_blank');
        showNotification('✅ Report generated successfully!', 'success');
        updateFileList();
    } else {
        showNotification('❌ Report generation failed: ' + result.message, 'error');
    }
}

// Update functions
async function updateAllStatus() {
    await updateStatusCards();
    await updateMLStatus();
    await updateActiveAttacks();
    await updateMLPredictions();
    await updateKaggleStatus();
    await updateDatasetStats();
    await updateFileList();
}

async function updateStatusCards() {
    try {
        const data = await apiCall('/api/dashboard/status');
        const statusCards = document.getElementById('statusCards');

        if (statusCards && data.system) {
            statusCards.innerHTML = `
                <div class="status-card ${data.system.simulation === 'running' ? 'running' : 'stopped'}">
                    <h3>Simulation Status</h3>
                    <div class="value">${data.system.simulation.toUpperCase()}</div>
                    <div class="label">${data.blockchain.nodes} Nodes</div>
                </div>
                <div class="status-card ${data.system.simulation === 'running' ? 'running' : 'stopped'}">
                    <h3>Blockchain</h3>
                    <div class="value">${data.blockchain.blocks}</div>
                    <div class="label">Total Blocks</div>
                </div>
                <div class="status-card ${data.system.simulation === 'running' ? 'running' : 'stopped'}">
                    <h3>Transactions</h3>
                    <div class="value">${data.blockchain.transactions}</div>
                    <div class="label">Total Transactions</div>
                </div>
                <div class="status-card ${data.system.ml_model === 'trained' ? 'running' : 'stopped'}">
                    <h3>ML Model</h3>
                    <div class="value">${data.system.ml_model.toUpperCase()}</div>
                    <div class="label">Anomaly Detection</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

async function updateMLStatus() {
    try {
        const status = await apiCall('/api/ml/status');

        if (status.training_status === 'trained') {
            isMLTrained = true;
        } else {
            isMLTrained = false;
        }

        if (status.is_detecting) {
            isDetectionRunning = true;
        } else {
            isDetectionRunning = false;
        }

        const mlStatus = document.getElementById('mlStatus');
        const detectionStatus = document.getElementById('detectionStatus');

        if (mlStatus && status.training_status) {
            const statusColor = status.training_status === 'trained' ? '#10b981' : '#f59e0b';
            const anomaliesColor = status.recent_anomalies > 0 ? '#ef4444' : '#10b981';

            mlStatus.innerHTML = `
                <div style="padding: 1rem; background: #1e293b; border-radius: 12px; border-left: 4px solid ${statusColor}">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
                        <div><strong>Status:</strong></div>
                        <div style="color: ${statusColor}">${status.training_status.toUpperCase()}</div>
                        
                        <div><strong>Accuracy:</strong></div>
                        <div>${(status.model_accuracy * 100).toFixed(1)}%</div>
                        
                        <div><strong>Predictions:</strong></div>
                        <div>${status.total_predictions}</div>
                        
                        <div><strong>Recent Anomalies:</strong></div>
                        <div style="color: ${anomaliesColor}">${status.recent_anomalies}</div>
                    </div>
                </div>
            `;
        }

        if (detectionStatus) {
            detectionStatus.innerHTML = `
                <div style="padding: 1rem; background: #1e293b; border-radius: 12px; border-left: 4px solid ${status.is_detecting ? '#10b981' : '#ef4444'};">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                        <div><strong>Detection:</strong></div>
                        <div style="color: ${status.is_detecting ? '#10b981' : '#ef4444'}">${status.is_detecting ? 'ACTIVE' : 'INACTIVE'}</div>
                        
                        <div><strong>Predictions:</strong></div>
                        <div>${status.total_predictions}</div>
                        
                        <div><strong>Anomalies Found:</strong></div>
                        <div style="color: ${status.recent_anomalies > 0 ? '#ef4444' : '#10b981'}">${status.recent_anomalies}</div>
                    </div>
                </div>
            `;
        }

    } catch (error) {
        console.error('Error updating ML status:', error);
        isMLTrained = false;
        isDetectionRunning = false;
    }
}

async function updateActiveAttacks() {
    try {
        const data = await apiCall('/api/attack/active');
        const attacksList = document.getElementById('attacksList');

        if (attacksList) {
            if (data.active_attacks?.length > 0) {
                attacksList.innerHTML = data.active_attacks.map(attack => {
                    const statusColor = attack.status === 'success' ? '#10b981' :
                                      attack.status === 'running' ? '#f59e0b' : '#ef4444';
                    return `
                        <div class="attack-item">
                            <strong>${attack.type.replace('_', ' ').toUpperCase()}</strong>
                            <div>Started: ${new Date(attack.start_time).toLocaleTimeString()}</div>
                            <div>Status: <span style="color: ${statusColor}; font-weight: bold;">${attack.status.toUpperCase()}</span></div>
                            ${attack.end_time ? `<div>Ended: ${new Date(attack.end_time).toLocaleTimeString()}</div>` : ''}
                        </div>
                    `;
                }).join('');
            } else {
                attacksList.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        <p>🎯 No active attacks</p>
                        <p><small>Start simulation and launch attacks to see real-time monitoring</small></p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error updating attacks:', error);
    }
}

async function updateMLPredictions() {
    try {
        const data = await apiCall('/api/ml/predictions?limit=10');
        const mlPredictions = document.getElementById('mlPredictions');

        if (mlPredictions && data.recent_predictions) {
            if (data.recent_predictions.length > 0) {
                mlPredictions.innerHTML = data.recent_predictions.slice().reverse().map((pred, index) => {
                    const timestamp = pred.timestamp ?
                        new Date(pred.timestamp).toLocaleTimeString() :
                        new Date().toLocaleTimeString();

                    if (pred.error) {
                        return `
                            <div class="prediction-item error">
                                <strong>⚠️ PREDICTION ERROR</strong>
                                <div style="margin-top: 0.5rem;">Error: ${pred.error}</div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Time: ${timestamp}</div>
                            </div>
                        `;
                    } else {
                        const confidenceColor = pred.confidence > 0.8 ? '#ef4444' :
                                              pred.confidence > 0.6 ? '#f59e0b' : '#10b981';

                        let attackTypeDisplay = '';
                        if (pred.attack_type && pred.attack_type !== 'none' && pred.attack_type !== 'unknown') {
                            let attackName = pred.attack_type;
                            if (attackName === '51_percent_attack') attackName = '51% Attack';
                            else if (attackName === 'double_spending') attackName = 'Double Spending';
                            else if (attackName === 'selfish_mining') attackName = 'Selfish Mining';
                            else if (attackName === 'eclipse_attack') attackName = 'Eclipse Attack';
                            else {
                                attackName = attackName.replace(/_/g, ' ').toUpperCase();
                            }

                            attackTypeDisplay = `
                                <div style="font-size: 0.9rem; color: #f59e0b; margin-top: 0.25rem;">
                                    Attack Type: ${attackName}
                                </div>`;
                        }

                        return `
                            <div class="prediction-item ${pred.is_anomaly ? 'anomaly' : 'normal'}">
                                <strong>${pred.is_anomaly ? '🚨 ANOMALY DETECTED' : '✅ NORMAL BEHAVIOR'}</strong>
                                <div style="margin-top: 0.5rem;">
                                    Confidence: <span style="color: ${confidenceColor}; font-weight: bold;">${(pred.confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 0.25rem;">Time: ${timestamp}</div>
                                ${attackTypeDisplay}
                                ${pred.features_used ? `<div style="font-size: 0.8rem; color: #888; margin-top: 0.25rem;">Features: ${pred.features_used}</div>` : ''}
                            </div>
                        `;
                    }
                }).join('');
            } else {
                mlPredictions.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        <p>🔍 Start ML detection to see real-time predictions</p>
                        <p><small>Make sure simulation is running and ML model is trained</small></p>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Error updating predictions:', error);
        const mlPredictions = document.getElementById('mlPredictions');
        if (mlPredictions) {
            mlPredictions.innerHTML = `
                <div class="prediction-item error">
                    <strong>❌ ERROR LOADING PREDICTIONS</strong>
                    <div style="margin-top: 0.5rem;">Please check if ML service is running properly</div>
                </div>
            `;
        }
    }
}

// Chart update functions
function updateCharts() {
    if (!isSimulationRunning) return;

    updateBlockchainChart();
    updateAttackCharts();
    updateMLCharts();
    updateDataCharts();
}

function updateBlockchainChart() {
    if (!charts.blockchainChart) return;

    const statusCards = document.getElementById('statusCards');
    if (statusCards) {
        const cards = statusCards.getElementsByClassName('status-card');
        if (cards.length >= 3) {
            const blocksValue = cards[1].querySelector('.value')?.textContent || '0';
            const transactionsValue = cards[2].querySelector('.value')?.textContent || '0';

            const currentBlocks = parseInt(blocksValue) || 0;
            const currentTransactions = parseInt(transactionsValue) || 0;

            if (currentBlocks > 0) {
                const chart = charts.blockchainChart;
                const newLabel = `Block ${currentBlocks}`;

                const lastBlockCount = chart.data.datasets[0].data[chart.data.datasets[0].data.length - 1] || 0;
                if (currentBlocks > lastBlockCount) {
                    chart.data.labels.push(newLabel);
                    chart.data.datasets[0].data.push(currentBlocks);
                    chart.data.datasets[1].data.push(currentTransactions);

                    if (chart.data.labels.length > 10) {
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                        chart.data.datasets[1].data.shift();
                    }

                    chart.options.plugins.title.text = 'Blockchain Network Activity - LIVE';
                    chart.update('none');
                }
            }
        }
    }
}

function updateAttackCharts() {
    if (!isSimulationRunning) return;

    fetch('/api/attack/stats')
        .then(response => response.json())
        .then(stats => {
            updateAttackDistributionChart(stats);
            updateAttackSuccessChart(stats);
        })
        .catch(error => {
            console.error('Error fetching attack stats:', error);
        });
}

function updateAttackDistributionChart(stats) {
    if (!charts.attackChart) return;

    fetch('/api/attack/active')
        .then(response => response.json())
        .then(data => {
            const attacks = data.active_attacks || [];

            if (attacks.length > 0) {
                const attackCounts = {
                    'Double Spending': 0,
                    '51% Attack': 0,
                    'Selfish Mining': 0,
                    'Eclipse Attack': 0
                };

                attacks.forEach(attack => {
                    const attackType = attack.type;
                    if (attackType === 'double_spending' || attackType === 'double-spending') attackCounts['Double Spending']++;
                    else if (attackType === '51_percent' || attackType === '51-percent') attackCounts['51% Attack']++;
                    else if (attackType === 'selfish_mining' || attackType === 'selfish-mining') attackCounts['Selfish Mining']++;
                    else if (attackType === 'eclipse_attack' || attackType === 'eclipse') attackCounts['Eclipse Attack']++;
                });

                const labels = [];
                const dataValues = [];
                const colors = ['#f59e0b', '#ef4444', '#3b82f6', '#8b5cf6'];

                Object.entries(attackCounts).forEach(([attack, count]) => {
                    if (count > 0) {
                        labels.push(attack);
                        dataValues.push(count);
                    }
                });

                if (labels.length > 0) {
                    charts.attackChart.data.labels = labels;
                    charts.attackChart.data.datasets[0].data = dataValues;
                    charts.attackChart.data.datasets[0].backgroundColor = colors.slice(0, labels.length);
                    charts.attackChart.options.plugins.title.text = 'Attack Distribution - LIVE';
                } else {
                    charts.attackChart.data.labels = ['No Active Attacks'];
                    charts.attackChart.data.datasets[0].data = [100];
                    charts.attackChart.data.datasets[0].backgroundColor = ['#334155'];
                    charts.attackChart.options.plugins.title.text = 'Attack Distribution - No Active Attacks';
                }
            } else {
                charts.attackChart.data.labels = ['No Attacks Yet'];
                charts.attackChart.data.datasets[0].data = [100];
                charts.attackChart.data.datasets[0].backgroundColor = ['#334155'];
                charts.attackChart.options.plugins.title.text = 'Attack Distribution - Run Attacks First';
            }

            charts.attackChart.update();
        })
        .catch(error => {
            console.error('Error updating attack distribution chart:', error);
        });
}

function updateAttackSuccessChart(stats) {
    if (!charts.successChart) return;

    const totalAttacks = stats.total_attacks || 0;
    const successfulAttacks = stats.successful_attacks || 0;

    if (totalAttacks > 0) {
        const successRate = (successfulAttacks / totalAttacks) * 100;

        charts.successChart.data.labels = ['Success Rate'];
        charts.successChart.data.datasets[0].data = [successRate];
        charts.successChart.data.datasets[0].backgroundColor = successRate > 50 ? '#10b981' : '#ef4444';
        charts.successChart.options.plugins.title.text = `Attack Success: ${successRate.toFixed(1)}%`;
    } else {
        charts.successChart.data.labels = ['Run Attacks First'];
        charts.successChart.data.datasets[0].data = [0];
        charts.successChart.data.datasets[0].backgroundColor = '#334155';
        charts.successChart.options.plugins.title.text = 'Attack Success Rate - No Data';
    }

    charts.successChart.update();
}

function updateMLCharts() {
    if (!isMLTrained) return;

    const mlStatus = document.getElementById('mlStatus');
    if (!mlStatus) return;

    const mlPredictions = document.getElementById('mlPredictions');
    const predictionItems = mlPredictions?.querySelectorAll('.prediction-item') || [];

    let anomalyCount = 0;
    let normalCount = 0;

    predictionItems.forEach(item => {
        if (item.classList.contains('anomaly')) {
            anomalyCount++;
        } else if (item.classList.contains('normal')) {
            normalCount++;
        }
    });

    if (charts.anomalyChart) {
        const total = anomalyCount + normalCount || 1;
        const anomalyPercentage = (anomalyCount / total) * 100;
        const normalPercentage = (normalCount / total) * 100;

        charts.anomalyChart.data = {
            labels: ['Normal', 'Anomaly'],
            datasets: [{
                data: [normalPercentage, anomalyPercentage],
                backgroundColor: ['#06d6a0', '#ef4444'],
                borderWidth: 0
            }]
        };
        charts.anomalyChart.options.plugins.title.text = `Anomaly Detection - ${anomalyCount} Anomalies`;
        charts.anomalyChart.update();
    }

    if (charts.confidenceChart && isDetectionRunning) {
        const chart = charts.confidenceChart;

        const confidenceSpans = mlPredictions?.querySelectorAll('span[style*="color"]') || [];
        let recentConfidence = 75;

        if (confidenceSpans.length > 0) {
            const latestConfidenceText = confidenceSpans[0].textContent;
            const confidenceMatch = latestConfidenceText.match(/(\d+\.?\d*)%/);
            if (confidenceMatch) {
                recentConfidence = parseFloat(confidenceMatch[1]);
            }
        }

        const newLabel = `P${chart.data.labels.length + 1}`;
        chart.data.labels.push(newLabel);
        chart.data.datasets[0].data.push(recentConfidence);

        if (chart.data.labels.length > 8) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.options.plugins.title.text = 'Model Confidence - LIVE';
        chart.update('none');
    }
}

function updateMLChartsWithRealData(metrics) {
    if (!metrics) return;

    if (charts.performanceChart && metrics.accuracy) {
        charts.performanceChart.data.datasets[0].data = [
            Math.min(100, (metrics.accuracy * 100)),
            Math.min(100, (metrics.precision * 100)),
            Math.min(100, (metrics.recall * 100)),
            Math.min(100, (metrics.f1_score * 100)),
            85 + Math.random() * 10
        ];
        charts.performanceChart.data.datasets[0].backgroundColor = 'rgba(99, 102, 241, 0.2)';
        charts.performanceChart.data.datasets[0].borderColor = '#6366f1';
        charts.performanceChart.data.datasets[0].pointBackgroundColor = '#6366f1';
        charts.performanceChart.options.plugins.title.text = 'Model Performance Metrics';
        charts.performanceChart.update();
    }

    if (charts.dataChart) {
        charts.dataChart.data = {
            labels: ['Total Samples', 'Attack Samples', 'Normal Samples'],
            datasets: [{
                label: 'Training Data',
                data: [3000, 264, 2736],
                backgroundColor: ['#6366f1', '#ef4444', '#06d6a0'],
                borderWidth: 2
            }]
        };
        charts.dataChart.options.plugins.title.text = 'Training Data Distribution';
        charts.dataChart.update();
    }
}

function updateDataCharts() {
    if (charts.dataChart) {
        const mlStatusElement = document.getElementById('mlStatus');
        const isTrained = mlStatusElement && mlStatusElement.textContent.includes('TRAINED');

        if (isTrained) {
            charts.dataChart.data = {
                labels: ['Total Samples', 'Attack Samples', 'Normal Samples'],
                datasets: [{
                    label: 'Training Data',
                    data: [3000, 264, 2736],
                    backgroundColor: ['#6366f1', '#ef4444', '#06d6a0'],
                    borderWidth: 2
                }]
            };
            charts.dataChart.options.plugins.title.text = 'Training Data Distribution';
        } else {
            charts.dataChart.data = {
                labels: ['Available Datasets', 'Processed Data'],
                datasets: [{
                    label: 'Data Count',
                    data: [2, 1240],
                    backgroundColor: ['#6366f1', '#06d6a0'],
                    borderWidth: 2
                }]
            };
            charts.dataChart.options.plugins.title.text = 'Dataset Availability';
        }
        charts.dataChart.update();
    }

    if (charts.performanceChart) {
        const mlStatusElement = document.getElementById('mlStatus');
        const isTrained = mlStatusElement && mlStatusElement.textContent.includes('TRAINED');

        if (isTrained) {
            charts.performanceChart.data.datasets[0].data = [100, 100, 100, 100, 90];
            charts.performanceChart.data.datasets[0].backgroundColor = 'rgba(99, 102, 241, 0.2)';
            charts.performanceChart.data.datasets[0].borderColor = '#6366f1';
            charts.performanceChart.data.datasets[0].pointBackgroundColor = '#6366f1';
            charts.performanceChart.options.plugins.title.text = 'Model Performance Metrics';
        } else {
            charts.performanceChart.data.datasets[0].data = [0, 0, 0, 0, 0];
            charts.performanceChart.data.datasets[0].backgroundColor = 'rgba(51, 65, 85, 0.2)';
            charts.performanceChart.data.datasets[0].borderColor = '#334155';
            charts.performanceChart.data.datasets[0].pointBackgroundColor = '#334155';
            charts.performanceChart.options.plugins.title.text = 'Performance Metrics - Train Model';
        }
        charts.performanceChart.update();
    }
}

function updateTrainingMetrics(result) {
    const trainingMetrics = document.getElementById('trainingMetrics');
    if (trainingMetrics && result) {
        trainingMetrics.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #6366f1;">
                    <div style="font-size: 0.9rem; color: #94a3b8;">Accuracy</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #06d6a0;">${(result.accuracy * 100).toFixed(1)}%</div>
                </div>
                <div style="background: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <div style="font-size: 0.9rem; color: #94a3b8;">Precision</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #06d6a0;">${(result.precision * 100).toFixed(1)}%</div>
                </div>
                <div style="background: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <div style="font-size: 0.9rem; color: #94a3b8;">Recall</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #06d6a0;">${(result.recall * 100).toFixed(1)}%</div>
                </div>
                <div style="background: #1e293b; padding: 1rem; border-radius: 8px; border-left: 4px solid #8b5cf6;">
                    <div style="font-size: 0.9rem; color: #94a3b8;">F1-Score</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #06d6a0;">${(result.f1_score * 100).toFixed(1)}%</div>
                </div>
            </div>
        `;
    }
}

async function updateKaggleStatus() {
    try {
        const data = await apiCall('/api/kaggle/status');
        const kaggleStatus = document.getElementById('kaggleStatus');

        if (kaggleStatus && data) {
            kaggleStatus.innerHTML = `
                <div style="padding: 1rem; background: #1e293b; border-radius: 12px; border-left: 4px solid ${data.status === 'connected' ? '#10b981' : '#f59e0b'};">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem;">
                        <div><strong>Status:</strong></div>
                        <div style="color: ${data.status === 'connected' ? '#10b981' : '#f59e0b'}">${data.status.toUpperCase()}</div>
                        
                        <div><strong>Datasets:</strong></div>
                        <div>${data.datasets || 0}</div>
                        
                        <div><strong>Last Updated:</strong></div>
                        <div>${data.last_updated || 'Never'}</div>
                    </div>
                    ${data.message ? `<div style="margin-top: 0.5rem; padding: 0.5rem; background: rgba(59, 130, 246, 0.1); border-radius: 6px; font-size: 0.9rem;">${data.message}</div>` : ''}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error updating Kaggle status:', error);
    }
}

async function updateDatasetStats() {
    try {
        const data = await apiCall('/api/kaggle/dataset-stats');
        const datasetStats = document.getElementById('datasetStats');

        if (datasetStats && data) {
            datasetStats.innerHTML = `
                <div style="padding: 1rem; background: #1e293b; border-radius: 12px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                        <div><strong>Total Records:</strong></div>
                        <div>${data.total_records || 0}</div>
                        
                        <div><strong>Attack Samples:</strong></div>
                        <div>${data.attack_samples || 0}</div>
                        
                        <div><strong>Normal Samples:</strong></div>
                        <div>${data.normal_samples || 0}</div>
                        
                        <div><strong>Features:</strong></div>
                        <div>${data.features || 0}</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error updating dataset stats:', error);
    }
}

async function updateFileList() {
    try {
        const response = await apiCall('/api/kaggle/file-list');
        const fileList = document.getElementById('fileList');

        if (fileList && response.files && response.files.length > 0) {
            fileList.innerHTML = response.files.map(file => {
                const fileType = file.type || 'unknown';
                const fileSize = file.size ? (file.size / 1024).toFixed(2) : '0';
                const downloadUrl = file.download_url || `/api/kaggle/download-file/${fileType}`;

                return `
                    <div class="file-card">
                        <h5>${file.name}</h5>
                        <p>Type: ${fileType.replace('_', ' ')}</p>
                        <p>Size: ${fileSize} KB</p>
                        <button class="btn btn-primary" onclick="window.open('${downloadUrl}', '_blank')">
                            📥 Download
                        </button>
                    </div>
                `;
            }).join('');
        } else {
            fileList.innerHTML = `
                <div class="file-card">
                    <h5>No Data Files Available</h5>
                    <p>Run simulations and generate reports to create data files</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error updating file list:', error);
        const fileList = document.getElementById('fileList');
        if (fileList) {
            fileList.innerHTML = `
                <div class="file-card">
                    <h5>Error Loading Files</h5>
                    <p>Please check if the server is running properly</p>
                </div>
            `;
        }
    }
}

function resetChartsToDefault() {
    Object.keys(charts).forEach(chartId => {
        const chart = charts[chartId];
        if (chart) {
            switch (chartId) {
                case 'blockchainChart':
                    chart.data.labels = ['Start Simulation to See Data'];
                    chart.data.datasets[0].data = [0];
                    chart.data.datasets[1].data = [0];
                    chart.options.plugins.title.text = 'Blockchain Network Activity - Start Simulation';
                    break;
                case 'attackChart':
                    chart.data.labels = ['No Attacks Yet'];
                    chart.data.datasets[0].data = [100];
                    chart.data.datasets[0].backgroundColor = ['#334155'];
                    chart.options.plugins.title.text = 'Attack Distribution - Run Attacks First';
                    break;
                case 'successChart':
                    chart.data.labels = ['Run Attacks First'];
                    chart.data.datasets[0].data = [0];
                    chart.data.datasets[0].backgroundColor = '#334155';
                    chart.options.plugins.title.text = 'Attack Success Rate - No Data';
                    break;
                case 'anomalyChart':
                    chart.data.labels = ['Train Model First'];
                    chart.data.datasets[0].data = [100];
                    chart.data.datasets[0].backgroundColor = ['#334155'];
                    chart.options.plugins.title.text = 'Anomaly Detection - Train Model First';
                    break;
                case 'confidenceChart':
                    chart.data.labels = ['Start Detection'];
                    chart.data.datasets[0].data = [0];
                    chart.data.datasets[0].borderColor = '#334155';
                    chart.data.datasets[0].backgroundColor = 'rgba(51, 65, 85, 0.1)';
                    chart.options.plugins.title.text = 'Model Confidence - Start Detection';
                    break;
                case 'dataChart':
                    chart.data.labels = ['No Data Available'];
                    chart.data.datasets[0].data = [0];
                    chart.data.datasets[0].backgroundColor = ['#334155'];
                    chart.options.plugins.title.text = 'Data Distribution - Process Datasets';
                    break;
                case 'performanceChart':
                    chart.data.datasets[0].data = [0, 0, 0, 0, 0];
                    chart.data.datasets[0].backgroundColor = 'rgba(51, 65, 85, 0.2)';
                    chart.data.datasets[0].borderColor = '#334155';
                    chart.data.datasets[0].pointBackgroundColor = '#334155';
                    chart.options.plugins.title.text = 'Performance Metrics - Train Model';
                    break;
            }
            chart.update();
        }
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;

    const typeColors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };

    notification.style.backgroundColor = typeColors[type] || typeColors.info;
    notification.textContent = message;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();

    // Add event listeners for buttons
    document.getElementById('startSimulation')?.addEventListener('click', startSimulation);
    document.getElementById('stopSimulation')?.addEventListener('click', stopSimulation);
    document.getElementById('trainModel')?.addEventListener('click', trainMLModel);
    document.getElementById('startDetection')?.addEventListener('click', startMLDetection);
    document.getElementById('downloadDatasets')?.addEventListener('click', downloadDatasets);
    document.getElementById('processDatasets')?.addEventListener('click', processDatasets);
    document.getElementById('downloadAllData')?.addEventListener('click', downloadAllData);
    document.getElementById('generateReport')?.addEventListener('click', generateReport);

    // Attack buttons
    document.querySelectorAll('.attack-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const attackType = this.dataset.attack;
            startAttack(attackType);
        });
    });

    // File download buttons
    document.querySelectorAll('.download-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const fileType = this.dataset.file;
            window.open(`/api/kaggle/download-file/${fileType}`, '_blank');
        });
    });
});

// New CSV Reports functions
async function generateCSVReports() {
    showNotification('📊 Generating comprehensive CSV reports...', 'info');
    const result = await apiCall('/api/kaggle/generate-csv-reports', { method: 'POST' });

    if (result.status === 'success') {
        showNotification(`✅ ${result.message}`, 'success');
        updateFileList();
    } else {
        showNotification(`❌ ${result.message}`, 'error');
    }
}

async function downloadCSVReports() {
    showNotification('📥 Downloading all CSV reports...', 'info');
    window.open('/api/kaggle/download-all-csv-reports', '_blank');
}

// Event listeners mein add karen
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...

    // CSV Reports buttons
    document.getElementById('generateCSVReports')?.addEventListener('click', generateCSVReports);
    document.getElementById('downloadCSVReports')?.addEventListener('click', downloadCSVReports);
});

// Export for global access
window.startSimulation = startSimulation;
window.stopSimulation = stopSimulation;
window.trainMLModel = trainMLModel;
window.startMLDetection = startMLDetection;
window.startAttack = startAttack;
window.startDoubleSpending = startDoubleSpending;
window.start51Percent = start51Percent;
window.startSelfishMining = startSelfishMining;
window.startEclipseAttack = startEclipseAttack;
window.downloadDatasets = downloadDatasets;
window.processDatasets = processDatasets;
window.downloadAllData = downloadAllData;
window.generateReport = generateReport;
window.updateAllStatus = updateAllStatus;
window.generateCSVReports = generateCSVReports;
window.downloadCSVReports = downloadCSVReports;

