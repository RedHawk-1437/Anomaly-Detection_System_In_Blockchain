// app.js - COMPLETELY UPDATED VERSION WITH ALL FIXES
// Enhanced JavaScript with auto-refresh charts, attacker tracking, and real data

console.log('🔧 app.js loading with enhanced features and auto-refresh...');

// ================================
// GLOBAL VARIABLES & CONFIGURATION
// ================================

/**
 * Manages all Chart.js instances for blockchain visualization
 * @type {Object}
 */
let blockchainCharts = {
    growthChart: null,        // Blockchain growth visualization
    balanceChart: null,       // Wallet balance distribution
    miningChart: null,        // Mining performance analysis
    networkChart: null,       // Network activity over time
    simblockChart: null       // SimBlock network analysis
};

/**
 * Configuration for attack simulation parameters
 * @type {Object}
 */
let attackConfig = {
    successProbability: 0.5,   // Base success probability (0.0 - 1.0)
    attackerHashPower: 30,     // Attacker's hash power percentage (1-100)
    forceSuccess: false,       // Override to force attack success
    forceFailure: false        // Override to force attack failure
};

// ================================
// UTILITY FUNCTIONS
// ================================

/**
 * Display user notification with type-based styling
 * @param {string} message - Notification content to display
 * @param {string} type - Notification type: 'info', 'success', 'error'
 */
function showNotification(message, type = 'info') {
    console.log(`📢 ${type.toUpperCase()} Notification:`, message);

    // Clear existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());

    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';

    // Set background color based on type
    const colors = {
        info: '#3498db',
        success: '#27ae60',
        error: '#e74c3c'
    };

    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${colors[type] || colors.info};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 400px;
        font-weight: bold;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Auto-remove after 5 seconds
    setTimeout(() => notification.remove(), 5000);
}

/**
 * Create formatted HTML output for displaying results
 * @param {string} content - Main content to display
 * @param {string} title - Section title
 * @returns {string} Formatted HTML string
 */
function createUserFriendlyOutput(content, title) {
    return `
        <div class="user-friendly-output">
            <h4>${title}</h4>
            <div class="output-content">${content}</div>
        </div>
    `;
}

// ================================
// ATTACK CONTROL FUNCTIONS
// ================================

/**
 * Update attack success probability and refresh display
 * @param {string} value - New probability value (1-100)
 */
function updateSuccessProbability(value) {
    attackConfig.successProbability = parseFloat(value) / 100;
    document.getElementById('probability-value').textContent = value + '%';
    updateControlStatus();
}

/**
 * Update attacker's hash power percentage
 * @param {string} value - New hash power value (1-100)
 */
function updateHashPower(value) {
    attackConfig.attackerHashPower = parseFloat(value);
    document.getElementById('hashpower-value').textContent = value + '%';
    updateControlStatus();
}

/**
 * Force attack to always succeed (override probability)
 */
function forceAttackSuccess() {
    attackConfig.forceSuccess = true;
    attackConfig.forceFailure = false;

    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');

    successBtn.classList.add('active');
    failureBtn.classList.remove('active');

    updateControlStatus();
    showNotification('🎯 Attack forced to SUCCESS mode', 'success');
}

/**
 * Force attack to always fail (override probability)
 */
function forceAttackFailure() {
    attackConfig.forceFailure = true;
    attackConfig.forceSuccess = false;

    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');

    successBtn.classList.remove('active');
    failureBtn.classList.add('active');

    updateControlStatus();
    showNotification('🚫 Attack forced to FAILURE mode', 'error');
}

/**
 * Reset attack controls to random probability mode
 */
function resetAttackControl() {
    attackConfig.forceSuccess = false;
    attackConfig.forceFailure = false;

    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');

    successBtn.classList.remove('active');
    failureBtn.classList.remove('active');

    updateControlStatus();
    showNotification('🎲 Attack mode set to RANDOM probability', 'info');
}

/**
 * Update display showing current attack control mode
 */
function updateControlStatus() {
    const element = document.getElementById('current-mode');
    if (!element) return;

    if (attackConfig.forceSuccess) {
        element.textContent = 'FORCED SUCCESS';
        element.style.color = '#27ae60';
    } else if (attackConfig.forceFailure) {
        element.textContent = 'FORCED FAILURE';
        element.style.color = '#e74c3c';
    } else {
        element.textContent = `RANDOM (${(attackConfig.successProbability * 100).toFixed(1)}% probability)`;
        element.style.color = '#3498db';
    }
}

// ================================
// CHART MANAGEMENT FUNCTIONS - UPDATED FOR DYNAMIC DATA
// ================================

/**
 * Initialize chart canvases with proper dimensions
 */
function initializeCharts() {
    console.log('📊 Initializing chart canvases...');

    const chartIds = [
        'blockchainGrowthChart',
        'balanceDistributionChart',
        'miningAnalysisChart',
        'networkActivityChart',
        'simblockAnalysisChart'
    ];

    // Set dimensions for each chart canvas
    chartIds.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            const container = canvas.parentElement;
            if (container) {
                canvas.width = container.clientWidth - 40;
                canvas.height = 300;
            }
        }
    });
}

/**
 * Update blockchain growth chart with transaction data
 * @param {Object} chartData - Chart data from API
 */
function updateBlockchainGrowthChart(chartData) {
    const ctx = document.getElementById('blockchainGrowthChart');
    if (!ctx) return;

    // Destroy existing chart
    if (blockchainCharts.growthChart) {
        blockchainCharts.growthChart.destroy();
    }

    try {
        const labels = chartData.labels || [];
        const data = chartData.datasets?.[0]?.data || [];

        if (labels.length === 0) {
            console.log('No data for blockchain growth chart');
            return;
        }

        blockchainCharts.growthChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Transactions per Block',
                    data: data,
                    backgroundColor: '#2a5298',
                    borderColor: '#1e3c72',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Number of Transactions', font: { weight: 'bold' } }
                    },
                    x: {
                        title: { display: true, text: 'Block Number', font: { weight: 'bold' } }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Blockchain Growth Analysis',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
        console.log('✅ Blockchain growth chart updated');
    } catch (error) {
        console.error('Error creating growth chart:', error);
    }
}

/**
 * Update balance distribution pie chart with ALL wallets
 * @param {Object} chartData - Balance data from API
 */
function updateBalanceDistributionChart(chartData) {
    const ctx = document.getElementById('balanceDistributionChart');
    if (!ctx) return;

    if (blockchainCharts.balanceChart) {
        blockchainCharts.balanceChart.destroy();
    }

    try {
        const labels = chartData.labels || [];
        const data = chartData.datasets?.[0]?.data || [];

        // Show informative message when no data
        if (labels.length === 0 || data.length === 0 || labels[0] === 'No Data') {
            // Create empty state chart
            blockchainCharts.balanceChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['No Balance Data'],
                    datasets: [{
                        data: [1],
                        backgroundColor: ['#C9CBCF']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Wallet Balance Distribution - No Data',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: { position: 'right' }
                    }
                }
            });
            return;
        }

        blockchainCharts.balanceChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                        '#9966FF', '#FF9F40', '#9b59b6', '#34495e'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Wallet Balance Distribution (All Wallets)',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'right',
                        labels: {
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label}: ${value} coins`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} coins (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        console.log('✅ Balance distribution chart updated with enhanced data');
    } catch (error) {
        console.error('Error creating balance chart:', error);
    }
}

/**
 * Update mining analysis line chart
 * @param {Object} chartData - Mining data from API
 */
function updateMiningAnalysisChart(chartData) {
    const ctx = document.getElementById('miningAnalysisChart');
    if (!ctx) return;

    if (blockchainCharts.miningChart) {
        blockchainCharts.miningChart.destroy();
    }

    try {
        const labels = chartData.labels || [];
        const data = chartData.datasets?.[0]?.data || [];

        if (labels.length < 2) {
            console.log('Insufficient data for mining analysis');
            return;
        }

        blockchainCharts.miningChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Mining Time (seconds)',
                    data: data,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Mining Time (seconds)', font: { weight: 'bold' } }
                    },
                    x: {
                        title: { display: true, text: 'Block Index', font: { weight: 'bold' } }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Mining Time Analysis',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
        console.log('✅ Mining analysis chart updated');
    } catch (error) {
        console.error('Error creating mining chart:', error);
    }
}

/**
 * Update network activity area chart with dynamic data
 * @param {Object} chartData - Network activity data from API
 */
function updateNetworkActivityChart(chartData) {
    const ctx = document.getElementById('networkActivityChart');
    if (!ctx) return;

    if (blockchainCharts.networkChart) {
        blockchainCharts.networkChart.destroy();
    }

    try {
        const labels = chartData.labels || [];
        const data = chartData.datasets?.[0]?.data || [];

        // Show empty state message when no data
        if (labels.length === 0 || data.length === 0) {
            blockchainCharts.networkChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['No Data'],
                    datasets: [{
                        label: 'Network Activity Level',
                        data: [0],
                        borderColor: '#C9CBCF',
                        backgroundColor: 'rgba(201, 203, 207, 0.3)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Activity Level',
                                font: { weight: 'bold' }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Run attacks to see network activity',
                                font: { weight: 'bold' }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Network Activity - No Data Available',
                            font: { size: 16, weight: 'bold' }
                        },
                        legend: {
                            display: false
                        }
                    }
                }
            });
            return;
        }

        blockchainCharts.networkChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Network Activity Level',
                    data: data,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.3)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Activity Level',
                            font: { weight: 'bold' }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Attack Sequence',
                            font: { weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Network Activity During Attacks',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
        console.log('✅ Network activity chart updated with dynamic data');
    } catch (error) {
        console.error('Error creating network chart:', error);
    }
}

/**
 * Update SimBlock network analysis chart with dynamic data
 */
async function updateSimBlockAnalysisChart() {
    const ctx = document.getElementById('simblockAnalysisChart');
    if (!ctx) return;

    if (blockchainCharts.simblockChart) {
        blockchainCharts.simblockChart.destroy();
    }

    try {
        // Get dynamic SimBlock data from API
        const response = await fetch('/api/charts/simblock-analysis');
        let chartData = {
            labels: ['Network Latency', 'Node Health', 'Message Delivery', 'Attack Resistance'],
            datasets: [{
                label: 'Network Performance',
                data: [0, 0, 0, 0],
                backgroundColor: ['#C9CBCF', '#C9CBCF', '#C9CBCF', '#C9CBCF'],
                borderColor: ['#7f8c8d', '#7f8c8d', '#7f8c8d', '#7f8c8d'],
                borderWidth: 2
            }]
        };

        if (response.ok) {
            const apiData = await response.json();

            // Check if we have real data (not all zeros)
            const hasData = apiData.datasets && apiData.datasets[0] &&
                           apiData.datasets[0].data.some(val => val > 0);

            if (hasData) {
                chartData = apiData;
            } else {
                // Show empty state with message
                chartData.datasets[0].backgroundColor = ['#C9CBCF', '#C9CBCF', '#C9CBCF', '#C9CBCF'];
                chartData.datasets[0].borderColor = ['#7f8c8d', '#7f8c8d', '#7f8c8d', '#7f8c8d'];
            }
        }

        blockchainCharts.simblockChart = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Performance Score (%)',
                            font: { weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: chartData.datasets[0].data.every(val => val === 0)
                            ? 'SimBlock Network - No Data Available'
                            : 'SimBlock P2P Network Analysis',
                        font: { size: 16, weight: 'bold' }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed.y;
                                if (value === 0) {
                                    return 'No data - run attacks to see metrics';
                                }
                                return `${context.dataset.label}: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
        console.log('✅ SimBlock analysis chart updated with dynamic data');
    } catch (error) {
        console.error('Error creating SimBlock chart:', error);
    }
}

/**
 * Reset all chart data to initial state
 */
async function resetAllCharts() {
    try {
        const response = await fetch('/api/charts/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            showNotification('🔄 All charts reset to initial state', 'info');
            // Reload charts to show empty state
            setTimeout(() => {
                loadNetworkActivityChart();
                loadSimBlockAnalysisChart();
            }, 500);
        } else {
            showNotification('❌ Failed to reset charts', 'error');
        }
    } catch (error) {
        console.error('Failed to reset charts:', error);
        showNotification('❌ Failed to reset charts', 'error');
    }
}

// ================================
// SIMBLOCK INTEGRATION FUNCTIONS
// ================================

/**
 * Display current SimBlock network conditions
 */
async function displaySimBlockNetwork() {
    try {
        const response = await fetch('/api/simblock/network');
        if (!response.ok) throw new Error('Network request failed');

        const networkData = await response.json();

        // Create or update network display
        let networkDisplay = document.getElementById('simblock-network-display');
        if (!networkDisplay) {
            networkDisplay = document.createElement('div');
            networkDisplay.id = 'simblock-network-display';
            networkDisplay.className = 'section-box';
            networkDisplay.innerHTML = `
                <h4>🌐 SimBlock P2P Network</h4>
                <div id="network-conditions"></div>
                <div class="chart-actions">
                    <button class="primary-btn" onclick="startSimBlockSimulation()">Start Network Simulation</button>
                    <button class="primary-btn" onclick="calculateEnhancedProbability()">Calculate Enhanced Probability</button>
                </div>
            `;

            // Insert after attack section
            const attackSection = document.querySelector('.section-box:has(#run-attack-btn)');
            if (attackSection) {
                attackSection.parentNode.insertBefore(networkDisplay, attackSection);
            }
        }

        // Update network conditions display
        const conditionsDiv = document.getElementById('network-conditions');
        const healthClass = networkData.status === 'good' ? 'health-good' :
                           networkData.status === 'congested' ? 'health-congested' : 'health-poor';

        conditionsDiv.innerHTML = `
            <div class="network-stats">
                <p><strong>Network Status:</strong>
                   <span class="network-health-indicator ${healthClass}"></span>
                   <span class="${networkData.status === 'good' ? 'positive' : 'negative'}">
                   ${networkData.status || 'default'}</span>
                </p>
                <p><strong>Average Latency:</strong> ${networkData.latency || '100ms'}</p>
                <p><strong>Active Nodes:</strong> ${networkData.nodes || 4}</p>
                <p><strong>Attacker Present:</strong> ${networkData.attacker_present ? 'Yes' : 'No'}</p>
                <p><strong>Simulation Ready:</strong> ${networkData.simulation_ready ? '✅' : '❌'}</p>
            </div>
        `;

    } catch (error) {
        console.error('Failed to load SimBlock network:', error);
        showNotification('Failed to load SimBlock network data', 'error');
    }
}

/**
 * Start SimBlock network simulation
 */
async function startSimBlockSimulation() {
    try {
        showNotification('🚀 Starting SimBlock network simulation...', 'info');

        const response = await fetch('/api/simblock/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showNotification('✅ SimBlock simulation completed successfully!', 'success');
            displaySimBlockNetwork(); // Refresh display
            // Auto-refresh charts after simulation
            setTimeout(loadAllCharts, 1000);
        } else {
            showNotification('❌ SimBlock simulation failed', 'error');
        }

    } catch (error) {
        showNotification('💥 SimBlock simulation failed: ' + error.message, 'error');
    }
}

/**
 * Calculate enhanced attack probability using SimBlock
 */
async function calculateEnhancedProbability() {
    try {
        const baseProb = attackConfig.successProbability * 100;
        const hashPower = attackConfig.attackerHashPower;

        const response = await fetch('/api/simblock/attack-probability', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                base_probability: baseProb,
                hash_power: hashPower,
                latency: 100
            })
        });

        const data = await response.json();

        showNotification(
            `🎲 Enhanced probability: ${data.enhanced_probability.toFixed(1)}% (Base: ${data.base_probability}%)`,
            'info'
        );

    } catch (error) {
        console.error('Failed to calculate enhanced probability:', error);
        showNotification('Failed to calculate enhanced probability', 'error');
    }
}

// ================================
// CHART DASHBOARD FUNCTIONS
// ================================

/**
 * Load all charts with data from blockchain API
 */
async function loadAllCharts() {
    try {
        showNotification('📊 Loading all charts...', 'info');
        console.log('Loading comprehensive chart data...');

        // Use Promise.allSettled to handle individual chart failures
        const chartPromises = [
            loadBlockchainGrowthChart(),
            loadBalanceDistributionChart(),
            loadMiningAnalysisChart(),
            loadNetworkActivityChart(),
            loadSimBlockAnalysisChart()
        ];

        const results = await Promise.allSettled(chartPromises);

        // Check which charts loaded successfully
        const successfulCharts = results.filter(result => result.status === 'fulfilled').length;

        if (successfulCharts > 0) {
            showNotification(`✅ ${successfulCharts}/5 charts loaded successfully!`, 'success');
        } else {
            showNotification('⚠️ Some charts failed to load', 'error');
        }

        console.log(`Charts loaded: ${successfulCharts}/5 successful`);

    } catch (error) {
        console.error('Error loading charts:', error);
        showNotification('Failed to load some charts: ' + error.message, 'error');
    }
}

/**
 * Load blockchain growth chart data from API
 */
async function loadBlockchainGrowthChart() {
    try {
        const response = await fetch('/api/charts/blockchain-growth');
        if (response.ok) {
            const data = await response.json();
            updateBlockchainGrowthChart(data);
        } else {
            console.warn('Blockchain growth chart API failed');
        }
    } catch (error) {
        console.error('Error loading blockchain growth chart:', error);
    }
}

/**
 * Load balance distribution chart data from API
 */
async function loadBalanceDistributionChart() {
    try {
        const response = await fetch('/api/charts/balance-distribution');
        if (response.ok) {
            const data = await response.json();
            updateBalanceDistributionChart(data);
        } else {
            console.warn('Balance distribution chart API failed');
        }
    } catch (error) {
        console.error('Error loading balance distribution chart:', error);
    }
}

/**
 * Load mining analysis chart data from API
 */
async function loadMiningAnalysisChart() {
    try {
        const response = await fetch('/api/charts/mining-analysis');
        if (response.ok) {
            const data = await response.json();
            updateMiningAnalysisChart(data);
        } else {
            console.warn('Mining analysis chart API failed');
        }
    } catch (error) {
        console.error('Error loading mining analysis chart:', error);
    }
}

/**
 * Load network activity chart data from API
 */
async function loadNetworkActivityChart() {
    try {
        const response = await fetch('/api/charts/network-activity');
        if (response.ok) {
            const data = await response.json();
            updateNetworkActivityChart(data);
        } else {
            console.warn('Network activity chart API failed');
        }
    } catch (error) {
        console.error('Error loading network activity chart:', error);
    }
}

/**
 * Load SimBlock analysis chart with real data
 */
async function loadSimBlockAnalysisChart() {
    try {
        const response = await fetch('/api/charts/simblock-analysis');
        if (response.ok) {
            const data = await response.json();
            // Use the updated function that fetches real data
            await updateSimBlockAnalysisChart();
        }
    } catch (error) {
        console.error('Failed to load SimBlock chart:', error);
    }
}

/**
 * Toggle charts dashboard visibility
 * @param {string} sectionId - ID of section to toggle
 */
function toggleChartSection(sectionId) {
    const section = document.getElementById(sectionId);
    const button = document.querySelector(`[onclick="toggleChartSection('${sectionId}')"]`);

    if (section.style.display === 'none' || !section.style.display) {
        section.style.display = 'block';
        button.textContent = 'Hide Analytics Dashboard';
        setTimeout(() => {
            initializeCharts();
            loadAllCharts();
        }, 100);
    } else {
        section.style.display = 'none';
        button.textContent = 'Show Analytics Dashboard';
    }
}

// ================================
// AUTO-REFRESH SETUP
// ================================

/**
 * Setup automatic chart refresh after blockchain actions
 */
function setupChartAutoRefresh() {
    console.log('🔄 Setting up chart auto-refresh...');

    // Store original functions
    const originalSubmitTransaction = window.submitTransaction;
    const originalMineBlock = window.mineBlock;
    const originalRunAttack = window.runAttack;

    // Override submitTransaction with auto-refresh
    window.submitTransaction = async function() {
        await originalSubmitTransaction?.();
        setTimeout(() => {
            loadAllCharts();
            refreshEnhancedBalances();
        }, 1000);
    };

    // Override mineBlock with auto-refresh
    window.mineBlock = async function() {
        await originalMineBlock?.();
        setTimeout(() => {
            loadAllCharts();
            refreshEnhancedBalances();
            refreshChain();
        }, 1000);
    };

    // Override runAttack with auto-refresh
    window.runAttack = async function() {
        await originalRunAttack?.();
        setTimeout(() => {
            loadAllCharts();
            refreshEnhancedBalances();
        }, 1500);
    };

    console.log('✅ Chart auto-refresh setup completed');
}

// ================================
// BLOCKCHAIN CORE FUNCTIONS
// ================================

/**
 * Submit new transaction to blockchain
 */
async function submitTransaction() {
    const sender = document.getElementById('tx-sender').value.trim();
    const receiver = document.getElementById('tx-receiver').value.trim();
    const amount = parseFloat(document.getElementById('tx-amount').value);

    // Validation
    if (!sender || !receiver || !amount || amount <= 0) {
        showNotification('❌ Please fill all fields with valid values', 'error');
        return;
    }

    try {
        showNotification('💸 Sending transaction...', 'info');

        const response = await fetch('/api/tx/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, receiver, amount })
        });

        const data = await response.json();
        const box = document.getElementById('tx-response');

        if (box) {
            box.style.display = 'block';
            if (data.status === 'ok') {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>✅ <strong>Transaction Successful!</strong></p>
                    <p>Transaction ID: <code>${data.txid}</code></p>
                    <p>From: <strong>${sender}</strong></p>
                    <p>To: <strong>${receiver}</strong></p>
                    <p>Amount: <strong>${amount} coins</strong></p>
                    <p>Pending transactions: ${data.mempool_size}</p>
                `, 'Transaction Details');
                showNotification('✅ Transaction added successfully!', 'success');

                // Clear form
                document.getElementById('tx-sender').value = '';
                document.getElementById('tx-receiver').value = '';
                document.getElementById('tx-amount').value = '';
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Transaction Failed</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Transaction Error');
                showNotification('❌ Transaction failed', 'error');
            }
        }

    } catch (error) {
        showNotification('💥 Transaction failed: ' + error.message, 'error');
    }
}

/**
 * Mine new block with pending transactions
 */
async function mineBlock() {
    const miner = document.getElementById('miner-name').value.trim() || 'DefaultMiner';

    try {
        showNotification('⛏️ Mining block...', 'info');

        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ miner })
        });

        const data = await response.json();
        const box = document.getElementById('mine-response');

        if (box) {
            box.style.display = 'block';
            if (data.status === 'ok') {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>✅ <strong>Block Mined Successfully!</strong></p>
                    <p>Miner: <strong>${miner}</strong></p>
                    <p>Block Index: <strong>${data.block.index}</strong></p>
                    <p>Block Hash: <code>${data.block.hash.substring(0, 20)}...</code></p>
                    <p>Transactions in block: <strong>${data.block.transactions.length}</strong></p>
                    <p>Total chain length: <strong>${data.chain_length} blocks</strong></p>
                `, 'Mining Results');
                showNotification('✅ Block mined successfully!', 'success');
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Mining Failed</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Mining Error');
                showNotification('❌ Mining failed', 'error');
            }
        }

    } catch (error) {
        showNotification('💥 Mining failed: ' + error.message, 'error');
    }
}

/**
 * Enhanced balance display with attacker information
 */
async function refreshEnhancedBalances() {
    try {
        // Use detailed balances endpoint
        const response = await fetch('/api/balances/detailed');
        if (!response.ok) throw new Error('Failed to fetch balances');

        const data = await response.json();
        const balances = data.balances || {};
        const attackInfo = data.attack_info || {};

        const output = document.getElementById('balances-output');

        if (output) {
            let html = '<div class="balances-table"><h4>💰 Current Balances</h4>';

            // Show attack information if available
            if (Object.keys(attackInfo).length > 0) {
                html += '<div class="attack-alert">';
                html += '<h5>🚨 Recent Attack Activity</h5>';
                for (const [attacker, info] of Object.entries(attackInfo)) {
                    if (info.success) {
                        html += `<p>🦹 <strong>${attacker}</strong> stole <strong>${info.amount} coins</strong> from 😱 <strong>${info.victim}</strong></p>`;
                    } else {
                        html += `<p>🦹 <strong>${attacker}</strong>'s attack failed - no coins stolen</p>`;
                    }
                }
                html += '</div>';
            }

            html += '<table>';
            html += '<tr><th>Wallet Address</th><th>Balance</th><th>Status</th><th>Role</th></tr>';

            for (const [user, balance] of Object.entries(balances)) {
                const cls = balance >= 0 ? 'positive' : 'negative';
                const status = balance > 0 ? '💰' : balance < 0 ? '⚠️' : '➖';

                // Determine role
                let role = 'User';
                if (user in attackInfo) {
                    role = '🦹 Attacker';
                } else if (Object.values(attackInfo).some(info => info.victim === user)) {
                    role = '😱 Victim';
                } else if (balance > 50) {
                    role = '💰 Rich';
                } else if (balance < -10) {
                    role = '💸 Debt';
                }

                html += `<tr>
                    <td>${user}</td>
                    <td class="${cls}">${balance.toFixed(2)} coins</td>
                    <td>${status}</td>
                    <td>${role}</td>
                </tr>`;
            }

            html += '</table>';
            html += `<p class="summary">Total Wallets: ${data.total_wallets} | Active Attacks: ${data.active_attacks}</p>`;
            html += '</div>';

            output.innerHTML = html;
        }

        console.log('✅ Enhanced balances refreshed with attack info');

        // AUTO-REFRESH: Update balance chart
        setTimeout(() => {
            loadBalanceDistributionChart();
        }, 500);

    } catch (error) {
        console.error('Failed to load balances:', error);
        showNotification('❌ Failed to load balances', 'error');
    }
}

/**
 * Compatibility function for original refreshBalances
 */
async function refreshBalances() {
    await refreshEnhancedBalances();
}

/**
 * Refresh and display blockchain data
 */
async function refreshChain() {
    try {
        const response = await fetch('/api/chain');
        if (!response.ok) throw new Error('Failed to fetch chain data');

        const data = await response.json();
        const output = document.getElementById('chain-output');

        if (output) {
            let html = '<div class="chain-view"><h4>⛓️ Blockchain Overview</h4>';
            html += `<p>Total blocks: <strong>${data.chain.length}</strong></p>`;
            html += `<p>Pending transactions: <strong>${data.mempool.length}</strong></p>`;
            html += `<p>Difficulty: <strong>${data.difficulty}</strong></p>`;

            html += '<div class="blocks-container">';
            data.chain.forEach(block => {
                html += `
                    <div class="block-card">
                        <h5>Block #${block.index}</h5>
                        <p>Hash: <code>${block.hash.substring(0, 15)}...</code></p>
                        <p>Previous: <code>${block.previous_hash.substring(0, 15)}...</code></p>
                        <p>Transactions: ${block.transactions.length}</p>
                        <p>Nonce: ${block.nonce}</p>
                    </div>
                `;
            });
            html += '</div></div>';
            output.innerHTML = html;
        }

        console.log('✅ Blockchain refreshed');

    } catch (error) {
        console.error('Failed to load blockchain:', error);
        showNotification('❌ Failed to load blockchain', 'error');
    }
}

/**
 * Run double-spending attack simulation
 */
async function runAttack() {
    const attacker = document.getElementById('attack-attacker').value.trim() || 'Attacker';
    const blocks = parseInt(document.getElementById('attack-blocks').value) || 1;
    const amount = parseFloat(document.getElementById('attack-amount').value) || 5;

    // Validation
    if (blocks <= 0 || amount <= 0) {
        showNotification('❌ Please enter valid values for blocks and amount', 'error');
        return;
    }

    try {
        showNotification('🎯 Starting attack simulation...', 'info');

        // Prepare attack payload with proper frontend_config
        const payload = {
            attacker: attacker,
            blocks: blocks,
            amount: amount,
            frontend_config: {
                hash_power: attackConfig.attackerHashPower,  // Correct key name
                success_probability: attackConfig.successProbability * 100,  // Convert to percentage
                force_success: attackConfig.forceSuccess,
                force_failure: attackConfig.forceFailure,
                latency: 100  // Add latency for SimBlock
            }
        };

        console.log('🔧 Sending attack config:', payload);

        const response = await fetch('/api/attack/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Attack request failed: ${response.status}`);
        }

        const data = await response.json();
        console.log('🎯 Attack response:', data);

        const box = document.getElementById('attack-output');

        if (box) {
            box.style.display = 'block';

            // Create detailed attack report
            let attackHTML = `
                <p>🎯 <strong>Double-Spending Attack Results</strong></p>
                <div class="attack-steps">
            `;

            // Add attack steps
            if (data.steps && Array.isArray(data.steps)) {
                data.steps.forEach((step, index) => {
                    attackHTML += `<div class="attack-step"><strong>Step ${index + 1}:</strong> ${step.action}`;
                    if (step.result !== undefined) attackHTML += ` - ${step.result ? '✅ Success' : '❌ Failed'}`;
                    if (step.mining_success !== undefined) attackHTML += ` - Mining: ${step.mining_success ? '✅' : '❌'}`;
                    if (step.error) attackHTML += ` - Error: ${step.error}`;
                    attackHTML += `</div>`;
                });
            }

            const attackSuccessful = data.successful || false;
            const successRate = data.success_rate || 0;
            const blocksMined = data.blocks_mined || 0;

            attackHTML += `
                </div>
                <div class="attack-config">
                    <p><strong>Attack Configuration:</strong></p>
                    <p>Success Probability: ${(attackConfig.successProbability * 100).toFixed(1)}%</p>
                    <p>Hash Power: ${attackConfig.attackerHashPower}%</p>
                    <p>Mode: ${attackConfig.forceSuccess ? 'FORCED SUCCESS' : attackConfig.forceFailure ? 'FORCED FAILURE' : 'RANDOM'}</p>
                </div>
                <div class="attack-result ${attackSuccessful ? 'success' : 'failure'}">
                    <h4>${attackSuccessful ? '✅ ATTACK SUCCESSFUL!' : '❌ ATTACK FAILED'}</h4>
                    <p>${attackSuccessful ?
                        'The double-spending attack was successful! The private chain was accepted.' :
                        'The attack was prevented by the network.'}
                    </p>
                    <p>Success Rate: <strong>${(successRate * 100).toFixed(1)}%</strong></p>
                    <p>Blocks Mined: <strong>${blocksMined}</strong></p>
                    ${data.message ? `<p>Message: ${data.message}</p>` : ''}
                </div>
            `;

            box.innerHTML = createUserFriendlyOutput(attackHTML, 'Attack Simulation Complete');

            const notificationType = attackSuccessful ? 'success' : 'error';
            showNotification(
                `Attack ${attackSuccessful ? 'successful' : 'failed'} (${(successRate * 100).toFixed(1)}% success rate)`,
                notificationType
            );
        }

    } catch (error) {
        console.error('Attack simulation failed:', error);
        showNotification('💥 Attack simulation failed: ' + error.message, 'error');

        const box = document.getElementById('attack-output');
        if (box) {
            box.style.display = 'block';
            box.innerHTML = createUserFriendlyOutput(`
                <p>❌ <strong>Attack Failed</strong></p>
                <p>Error: ${error.message}</p>
                <p>Please check if the backend server is running.</p>
            `, 'Attack Error');
        }
    }
}

// ================================
// NETWORK MANAGEMENT FUNCTIONS
// ================================

/**
 * Add new peer to the network
 */
async function addPeer() {
    const peerAddress = document.getElementById('peer-address').value.trim();

    if (!peerAddress) {
        showNotification('❌ Please enter a valid peer address', 'error');
        return;
    }

    try {
        showNotification('🔗 Adding peer...', 'info');

        const response = await fetch('/peers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ address: peerAddress })
        });

        const data = await response.json();
        const box = document.getElementById('peer-response');

        if (box) {
            box.style.display = 'block';
            if (data.message) {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>✅ <strong>Peer Added Successfully!</strong></p>
                    <p>${data.message}</p>
                    <p>Total peers: ${data.peers.length}</p>
                `, 'Network Update');
                showNotification('✅ Peer added successfully!', 'success');
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Failed to Add Peer</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Network Error');
                showNotification('❌ Failed to add peer', 'error');
            }
        }

    } catch (error) {
        showNotification('💥 Failed to add peer: ' + error.message, 'error');
    }
}

/**
 * Resolve blockchain conflicts with network consensus
 */
async function resolveConflicts() {
    try {
        showNotification('🔄 Checking network consensus...', 'info');

        const response = await fetch('/consensus');
        const data = await response.json();
        const box = document.getElementById('consensus-response');

        if (box) {
            box.style.display = 'block';

            if (data.message && data.message.includes('replaced')) {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>🔄 <strong>Chain Replaced!</strong></p>
                    <p>Our chain was replaced by a longer chain from the network.</p>
                    <p>New chain length: ${data.new_chain.length} blocks</p>
                `, 'Consensus Results');
                showNotification('✅ Chain replaced with longer chain', 'success');

                setTimeout(() => {
                    refreshChain();
                    refreshEnhancedBalances();
                    loadAllCharts();
                }, 500);
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>✅ <strong>Chain is Authoritative</strong></p>
                    <p>Our chain is the longest and most valid chain in the network.</p>
                    <p>Current chain length: ${data.chain.length} blocks</p>
                `, 'Consensus Results');
                showNotification('✅ Our chain is authoritative', 'success');
            }
        }

    } catch (error) {
        showNotification('💥 Failed to run consensus: ' + error.message, 'error');
    }
}

/**
 * Download comprehensive PDF report
 */
async function downloadPDF() {
    const spinner = document.getElementById('pdf-spinner');

    try {
        spinner.style.display = 'inline';
        showNotification('📄 Generating PDF report...', 'info');

        const response = await fetch('/api/report/pdf');
        if (!response.ok) throw new Error('PDF generation failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Blockchain-Analysis-Report.pdf';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        showNotification('✅ PDF report downloaded successfully!', 'success');
    } catch (error) {
        showNotification('💥 PDF generation failed: ' + error.message, 'error');
    } finally {
        spinner.style.display = 'none';
    }
}

// ================================
// DASHBOARD CREATION FUNCTIONS - UPDATED WITH RESET BUTTON
// ================================

/**
 * Create charts dashboard section dynamically with reset button
 */
function createChartsDashboard() {
    const chartsSection = document.createElement('div');
    chartsSection.id = 'charts-dashboard';
    chartsSection.style.display = 'none';
    chartsSection.innerHTML = `
        <div class="section-box">
            <h3>📊 Blockchain Analytics Dashboard</h3>
            <p>Comprehensive visualization of blockchain data and network analytics with real-time SimBlock integration</p>

            <div class="chart-info-note">
                <p><strong>Note:</strong> Network Activity and SimBlock charts will show data only after running attack simulations</p>
            </div>

            <div class="charts-grid">
                <div class="chart-container">
                    <h4>Blockchain Growth</h4>
                    <canvas id="blockchainGrowthChart"></canvas>
                </div>

                <div class="chart-container">
                    <h4>Balance Distribution</h4>
                    <canvas id="balanceDistributionChart"></canvas>
                </div>

                <div class="chart-container">
                    <h4>Mining Analysis</h4>
                    <canvas id="miningAnalysisChart"></canvas>
                </div>

                <div class="chart-container">
                    <h4>Network Activity</h4>
                    <canvas id="networkActivityChart"></canvas>
                </div>

                <div class="chart-container">
                    <h4>SimBlock Network</h4>
                    <canvas id="simblockAnalysisChart"></canvas>
                </div>
            </div>

            <div class="chart-actions">
                <button class="primary-btn" onclick="loadAllCharts()">🔄 Refresh All Charts</button>
                <button class="primary-btn" onclick="resetAllCharts()">🗑️ Reset Chart Data</button>
                <button class="primary-btn" onclick="toggleChartSection('charts-dashboard')">📋 Hide Dashboard</button>
            </div>
        </div>
    `;

    // Insert after introduction section
    const introSection = document.querySelector('.header-text');
    if (introSection) {
        introSection.parentNode.insertBefore(chartsSection, introSection.nextSibling);
    }

    console.log('✅ Charts dashboard created successfully with reset functionality');
}

// ================================
// INITIALIZATION FUNCTIONS
// ================================

/**
 * Initialize all event listeners
 */
function initializeEventListeners() {
    console.log('🔧 Initializing event listeners...');

    // Add charts dashboard toggle button
    const header = document.querySelector('.header-text');
    if (header) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'primary-btn';
        toggleBtn.style.margin = '10px';
        toggleBtn.textContent = '📊 Show Analytics Dashboard';
        toggleBtn.onclick = function() { toggleChartSection('charts-dashboard'); };
        header.appendChild(toggleBtn);
    }

    // Define button configurations
    const buttons = [
        { id: 'submit-tx-btn', func: submitTransaction, name: 'Transaction' },
        { id: 'mine-btn', func: mineBlock, name: 'Mine Block' },
        { id: 'refresh-balances-btn', func: refreshEnhancedBalances, name: 'Refresh Balances' },
        { id: 'refresh-chain-btn', func: refreshChain, name: 'Refresh Chain' },
        { id: 'run-attack-btn', func: runAttack, name: 'Run Attack' },
        { id: 'add-peer-btn', func: addPeer, name: 'Add Peer' },
        { id: 'resolve-conflicts-btn', func: resolveConflicts, name: 'Resolve Conflicts' },
        { id: 'download-report-btn', func: downloadPDF, name: 'Download PDF' }
    ];

    // Attach event listeners
    buttons.forEach(btn => {
        const element = document.getElementById(btn.id);
        if (element) {
            element.addEventListener('click', btn.func);
            console.log('✅ ' + btn.name + ' button listener added');
        } else {
            console.log('❌ ' + btn.name + ' button not found');
        }
    });
}

// ================================
// APPLICATION INITIALIZATION
// ================================

/**
 * Initialize application when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM fully loaded! Initializing blockchain application...');

    // Initialize attack controls
    updateControlStatus();

    // Create UI components
    createChartsDashboard();

    // Initialize charts and event listeners
    initializeCharts();
    initializeEventListeners();

    // Setup auto-refresh functionality
    setTimeout(setupChartAutoRefresh, 3000);

    // Load initial data after short delay
    setTimeout(() => {
        refreshEnhancedBalances();
        refreshChain();
        displaySimBlockNetwork();
        showNotification('✅ Blockchain UI with Auto-Refresh Ready!', 'success');
    }, 2000);
});

console.log('✅ app.js with enhanced features and auto-refresh loaded successfully!');