// app.js - Complete with Charts & Analytics - FIXED VERSION
// This is the main JavaScript file that handles all frontend functionality
// including blockchain interactions, chart visualizations, and attack simulations.

console.log('🔧 app.js loading with charts...');

// Global variables for chart management
let chainChart = null;           // Main blockchain chart instance
let simblockChart = null;        // SimBlock simulation chart instance

// Object to store all blockchain chart instances
let blockchainCharts = {
    growthChart: null,        // Blockchain growth chart
    balanceChart: null,       // Balance distribution chart
    miningChart: null,        // Mining analysis chart
    networkChart: null        // Network activity chart
};

// Attack Configuration Object
// Stores current attack simulation settings
let attackConfig = {
    successProbability: 0.5,   // Default 50% success probability
    attackerHashPower: 30,     // Default 30% hash power
    forceSuccess: false,       // Force attack success flag
    forceFailure: false        // Force attack failure flag
};

// ----------------------------
// Core Helper Functions
// ----------------------------

/**
 * Display a notification message to the user
 * @param {string} message - The message to display
 * @param {string} type - Type of notification ('info', 'success', 'error')
 */
function showNotification(message, type = 'info') {
    console.log('📢 Notification:', message);

    // Remove existing notifications to avoid clutter
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    // Create new notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;

    // Set background color based on notification type
    let bgColor = '#1e90ff'; // default blue for info
    if (type === 'error') bgColor = '#ff4757';    // red for errors
    if (type === 'success') bgColor = '#2ed573';  // green for success

    // Apply CSS styles to notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${bgColor};
        color: white;
        border-radius: 8px;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 400px;
        font-weight: bold;
    `;

    // Add notification to page
    document.body.appendChild(notification);

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Create user-friendly HTML output for displaying results
 * @param {string} data - The content to display
 * @param {string} title - Title for the output section
 * @returns {string} HTML string for the output
 */
function createUserFriendlyOutput(data, title) {
    return `
        <div class="user-friendly-output">
            <h4>${title}</h4>
            <div class="output-content">${data}</div>
        </div>
    `;
}

// ----------------------------
// Attack Control Functions
// ----------------------------

/**
 * Update the success probability for attacks
 * @param {string} value - New probability value (1-100)
 */
function updateSuccessProbability(value) {
    // Convert to decimal (0.0 - 1.0)
    attackConfig.successProbability = parseFloat(value) / 100;

    // Update display value
    const element = document.getElementById('probability-value');
    if (element) element.textContent = value + '%';

    // Update control status display
    updateControlStatus();
}

/**
 * Update the attacker's hash power percentage
 * @param {string} value - New hash power value (1-100)
 */
function updateHashPower(value) {
    attackConfig.attackerHashPower = parseFloat(value);

    // Update display value
    const element = document.getElementById('hashpower-value');
    if (element) element.textContent = value + '%';

    // Update control status display
    updateControlStatus();
}

/**
 * Force the attack to always succeed (override probability)
 */
function forceAttackSuccess() {
    attackConfig.forceSuccess = true;
    attackConfig.forceFailure = false;

    // Update button visual states
    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');
    if (successBtn) successBtn.classList.add('active');
    if (failureBtn) failureBtn.classList.remove('active');

    updateControlStatus();
    showNotification('Attack forced to SUCCESS', 'success');
}

/**
 * Force the attack to always fail (override probability)
 */
function forceAttackFailure() {
    attackConfig.forceFailure = true;
    attackConfig.forceSuccess = false;

    // Update button visual states
    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');
    if (successBtn) successBtn.classList.remove('active');
    if (failureBtn) failureBtn.classList.add('active');

    updateControlStatus();
    showNotification('Attack forced to FAIL', 'error');
}

/**
 * Reset attack controls to random mode (use probability)
 */
function resetAttackControl() {
    attackConfig.forceSuccess = false;
    attackConfig.forceFailure = false;

    // Reset button visual states
    const successBtn = document.getElementById('force-success-btn');
    const failureBtn = document.getElementById('force-failure-btn');
    if (successBtn) successBtn.classList.remove('active');
    if (failureBtn) failureBtn.classList.remove('active');

    updateControlStatus();
    showNotification('Attack mode set to RANDOM', 'info');
}

/**
 * Update the display showing current attack control mode
 */
function updateControlStatus() {
    const element = document.getElementById('current-mode');
    if (!element) return;

    // Set text and color based on current mode
    if (attackConfig.forceSuccess) {
        element.textContent = 'FORCED SUCCESS';
        element.style.color = '#27ae60'; // Green
    } else if (attackConfig.forceFailure) {
        element.textContent = 'FORCED FAILURE';
        element.style.color = '#e74c3c'; // Red
    } else {
        element.textContent = 'RANDOM (' + (attackConfig.successProbability * 100) + '% probability)';
        element.style.color = '#3498db'; // Blue
    }
}

// ----------------------------
// Chart Functions (FIXED)
// ----------------------------

/**
 * Initialize chart canvases with proper dimensions
 */
function initializeCharts() {
    console.log('📊 Initializing charts...');

    // Wait for DOM to be fully ready before initializing charts
    setTimeout(() => {
        const canvases = [
            'blockchainGrowthChart',
            'balanceDistributionChart',
            'miningAnalysisChart',
            'networkActivityChart',
            'simblockChart'
        ];

        // Set dimensions for each chart canvas
        canvases.forEach(canvasId => {
            const canvas = document.getElementById(canvasId);
            if (canvas) {
                const container = canvas.parentElement;
                if (container) {
                    // Set canvas size based on container
                    canvas.width = container.clientWidth - 40;
                    canvas.height = 300;
                }
            }
        });
    }, 100);
}

/**
 * Update the blockchain growth chart with new data
 * @param {Object} chainData - Blockchain data from API
 */
function updateBlockchainGrowthChart(chainData) {
    const ctx = document.getElementById('blockchainGrowthChart');
    if (!ctx) {
        console.log('Blockchain growth chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (blockchainCharts.growthChart) {
        blockchainCharts.growthChart.destroy();
    }

    try {
        // Ensure we have valid data
        const labels = chainData.labels || [];
        const data = chainData.tx_counts || [];

        if (labels.length === 0 || data.length === 0) {
            console.log('No data available for blockchain growth chart');
            return;
        }

        // Create new Chart.js bar chart
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
                        title: {
                            display: true,
                            text: 'Number of Transactions',
                            font: { weight: 'bold' }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Block Number',
                            font: { weight: 'bold' }
                        }
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
        console.log('✅ Blockchain growth chart updated successfully');
    } catch (error) {
        console.error('Error creating blockchain growth chart:', error);
    }
}

/**
 * Update the balance distribution pie chart
 * @param {Object} balances - Balance data from API
 */
function updateBalanceDistributionChart(balances) {
    const ctx = document.getElementById('balanceDistributionChart');
    if (!ctx) {
        console.log('Balance distribution chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (blockchainCharts.balanceChart) {
        blockchainCharts.balanceChart.destroy();
    }

    try {
        // Filter only positive balances for pie chart (negative don't make sense in pie)
        const positiveBalances = Object.entries(balances).filter(([_, value]) => value > 0);
        if (positiveBalances.length === 0) {
            console.log('No positive balances available for chart');
            return;
        }

        const labels = positiveBalances.map(([key, _]) => key);
        const values = positiveBalances.map(([_, value]) => value);

        // Create new Chart.js pie chart
        blockchainCharts.balanceChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
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
                        text: 'Wallet Balance Distribution (Positive Balances)',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
        console.log('✅ Balance distribution chart updated successfully');
    } catch (error) {
        console.error('Error creating balance distribution chart:', error);
    }
}

/**
 * Update the mining analysis line chart
 * @param {Object} chainData - Blockchain data from API
 */
function updateMiningAnalysisChart(chainData) {
    const ctx = document.getElementById('miningAnalysisChart');
    if (!ctx) {
        console.log('Mining analysis chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (blockchainCharts.miningChart) {
        blockchainCharts.miningChart.destroy();
    }

    try {
        // Check if we have enough data for meaningful analysis
        if (!chainData.chain || chainData.chain.length < 2) {
            console.log('Insufficient data for mining analysis chart');
            return;
        }

        const blockIndices = chainData.chain.map(block => block.index);
        // Simulate mining times (in real system this would be actual times)
        const miningTimes = blockIndices.map((_, index) => index * 2.5);

        // Create new Chart.js line chart
        blockchainCharts.miningChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: blockIndices,
                datasets: [{
                    label: 'Mining Time (seconds)',
                    data: miningTimes,
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
                        title: {
                            display: true,
                            text: 'Mining Time (seconds)',
                            font: { weight: 'bold' }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Block Index',
                            font: { weight: 'bold' }
                        }
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
        console.log('✅ Mining analysis chart updated successfully');
    } catch (error) {
        console.error('Error creating mining analysis chart:', error);
    }
}

/**
 * Update the network activity area chart
 */
function updateNetworkActivityChart() {
    const ctx = document.getElementById('networkActivityChart');
    if (!ctx) {
        console.log('Network activity chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (blockchainCharts.networkChart) {
        blockchainCharts.networkChart.destroy();
    }

    try {
        // Simulate 24 hours of network activity
        const timestamps = Array.from({length: 24}, (_, i) => `Hour ${i}`);
        const activityLevels = timestamps.map((_, i) => Math.max(5, 20 + 10 * Math.sin(i/3)));

        // Create new Chart.js line chart with area fill
        blockchainCharts.networkChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: timestamps,
                datasets: [{
                    label: 'Network Activity Level',
                    data: activityLevels,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.3)',
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Activity Level',
                            font: { weight: 'bold' }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time (Hours)',
                            font: { weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Network Activity Over Time',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
        console.log('✅ Network activity chart updated successfully');
    } catch (error) {
        console.error('Error creating network activity chart:', error);
    }
}

/**
 * Update the SimBlock simulation results chart
 * @param {Object} simulationData - SimBlock simulation results
 */
function updateSimblockChart(simulationData) {
    const canvas = document.getElementById('simblockChart');
    if (!canvas) {
        console.log('Simblock chart canvas not found');
        return;
    }

    // Destroy existing chart if it exists
    if (simblockChart) {
        simblockChart.destroy();
    }

    try {
        let chartData = simulationData.chart_data;

        // If no chart data provided, create it from simulation results
        if (!chartData) {
            chartData = {
                labels: ['Attack Probability', 'Total Blocks', 'Avg Block Time', 'Forks Detected', 'Total Miners'],
                values: [
                    (simulationData.attack_probability || 0) * 100,
                    simulationData.total_blocks || 0,
                    simulationData.avg_block_time || 0,
                    simulationData.forks_detected || 0,
                    simulationData.total_miners || 0
                ],
                colors: ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
            };
        }

        // Create new Chart.js bar chart for SimBlock metrics
        simblockChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Simulation Metrics',
                    data: chartData.values,
                    backgroundColor: chartData.colors,
                    borderColor: chartData.colors.map(color => color + 'CC'),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Values',
                            font: { weight: 'bold' }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Simulation Metrics',
                            font: { weight: 'bold' }
                        }
                    }
                },
                plugins: {
                    legend: { display: false }, // Hide legend for single dataset
                    title: {
                        display: true,
                        text: 'SimBlock Simulation Summary',
                        font: { size: 16, weight: 'bold' }
                    }
                }
            }
        });
        console.log('✅ Simblock chart updated successfully');

    } catch (error) {
        console.error('Error creating SimBlock chart:', error);
    }
}

// ----------------------------
// Chart Dashboard Functions
// ----------------------------

/**
 * Load all charts with data from the blockchain API
 */
async function loadAllCharts() {
    try {
        showNotification('Loading charts...', 'info');
        console.log('📊 Loading all charts...');

        // Load blockchain growth chart data
        const chainRes = await fetch("/api/chain");
        if (!chainRes.ok) throw new Error('Failed to load chain data');
        const chainData = await chainRes.json();
        updateBlockchainGrowthChart(chainData.chart_data);

        // Load balance distribution chart data
        const balanceRes = await fetch("/api/balances");
        if (!balanceRes.ok) throw new Error('Failed to load balance data');
        const balances = await balanceRes.json();
        updateBalanceDistributionChart(balances);

        // Load mining analysis chart data
        updateMiningAnalysisChart(chainData);

        // Load network activity chart data
        updateNetworkActivityChart();

        showNotification('All charts loaded successfully!', 'success');
        console.log('✅ All charts loaded successfully');

    } catch (error) {
        console.error('Error loading charts:', error);
        showNotification('Failed to load some charts: ' + error.message, 'error');
    }
}

/**
 * Toggle the visibility of the charts dashboard section
 * @param {string} sectionId - ID of the section to toggle
 */
function toggleChartSection(sectionId) {
    const section = document.getElementById(sectionId);
    const button = document.querySelector(`[onclick="toggleChartSection('${sectionId}')"]`);

    // Toggle section visibility
    if (section.style.display === 'none' || !section.style.display) {
        section.style.display = 'block';
        button.textContent = 'Hide Analytics Dashboard';
        // Small delay to ensure DOM is ready before initializing charts
        setTimeout(() => {
            initializeCharts();
            loadAllCharts();
        }, 100);
    } else {
        section.style.display = 'none';
        button.textContent = 'Show Analytics Dashboard';
    }
}

// ----------------------------
// Blockchain Functions
// ----------------------------

/**
 * Submit a new transaction to the blockchain
 */
async function submitTransaction() {
    // Get form values
    const sender = document.getElementById('tx-sender').value.trim();
    const receiver = document.getElementById('tx-receiver').value.trim();
    const amount = parseFloat(document.getElementById('tx-amount').value);

    // Validate form inputs
    if (!sender || !receiver || !amount || amount <= 0) {
        showNotification('Please fill all transaction fields with valid values', 'error');
        return;
    }

    try {
        showNotification('Sending transaction...', 'info');

        // Send transaction to backend API
        const response = await fetch('/api/tx/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, receiver, amount })
        });

        const data = await response.json();

        // Display transaction result
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
                showNotification('Transaction added successfully!', 'success');

                // Refresh charts and balances after successful transaction
                setTimeout(() => {
                    loadAllCharts();
                    refreshBalances();
                }, 500);

                // Clear form fields
                document.getElementById('tx-sender').value = '';
                document.getElementById('tx-receiver').value = '';
                document.getElementById('tx-amount').value = '';
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Transaction Failed</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Transaction Error');
                showNotification('Transaction failed: ' + (data.error || 'Unknown error'), 'error');
            }
        }

    } catch (error) {
        showNotification('Transaction failed: ' + error.message, 'error');
    }
}

/**
 * Mine a new block with pending transactions
 */
async function mineBlock() {
    const miner = document.getElementById('miner-name').value.trim() || 'DefaultMiner';

    try {
        showNotification('Mining block...', 'info');

        // Send mining request to backend
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
                showNotification('Block mined successfully!', 'success');

                // Refresh data after successful mining
                setTimeout(() => {
                    loadAllCharts();
                    refreshChain();
                    refreshBalances();
                }, 500);
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Mining Failed</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Mining Error');
                showNotification('Mining failed: ' + (data.error || 'Unknown error'), 'error');
            }
        }

    } catch (error) {
        showNotification('Mining failed: ' + error.message, 'error');
    }
}

/**
 * Refresh and display current wallet balances
 */
async function refreshBalances() {
    try {
        const response = await fetch('/api/balances');
        if (!response.ok) throw new Error('Failed to fetch balances');

        const data = await response.json();
        const output = document.getElementById('balances-output');

        if (output) {
            // Create HTML table for balances
            let html = '<div class="balances-table"><h4>💰 Current Balances</h4><table>';
            html += '<tr><th>User</th><th>Balance</th></tr>';

            // Add each balance to table with color coding
            for (const [user, balance] of Object.entries(data)) {
                const cls = balance >= 0 ? 'positive' : 'negative';
                html += `<tr><td>${user}</td><td class="${cls}">${balance.toFixed(2)} coins</td></tr>`;
            }

            html += '</table></div>';
            output.innerHTML = html;
        }

        // Update balance distribution chart
        updateBalanceDistributionChart(data);
        console.log('✅ Balances refreshed');

    } catch (error) {
        console.error('Failed to load balances:', error);
        showNotification('Failed to load balances', 'error');
    }
}

/**
 * Refresh and display the blockchain data
 */
async function refreshChain() {
    try {
        const response = await fetch('/api/chain');
        if (!response.ok) throw new Error('Failed to fetch chain data');

        const data = await response.json();
        const output = document.getElementById('chain-output');

        if (output) {
            // Create blockchain overview
            let html = '<div class="chain-view"><h4>⛓️ Blockchain Overview</h4>';
            html += `<p>Total blocks: <strong>${data.chain.length}</strong></p>`;
            html += `<p>Pending transactions: <strong>${data.mempool.length}</strong></p>`;
            html += `<p>Difficulty: <strong>${data.difficulty}</strong></p>`;

            // Create block cards for each block
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

        // Update charts with new chain data
        if (data.chart_data) {
            updateBlockchainGrowthChart(data.chart_data);
            updateMiningAnalysisChart(data);
        }
        console.log('✅ Blockchain refreshed');

    } catch (error) {
        console.error('Failed to load blockchain:', error);
        showNotification('Failed to load blockchain', 'error');
    }
}

// ----------------------------
// Attack Function
// ----------------------------

/**
 * Run a double-spending attack simulation
 */
async function runAttack() {
    // Get attack parameters from form
    const attacker = document.getElementById('attack-attacker').value.trim() || 'Attacker';
    const blocks = parseInt(document.getElementById('attack-blocks').value) || 1;
    const amount = parseFloat(document.getElementById('attack-amount').value) || 5;

    // Validate inputs
    if (blocks <= 0 || amount <= 0) {
        showNotification('Please enter valid values for blocks and amount', 'error');
        return;
    }

    try {
        showNotification('Starting attack simulation...', 'info');

        // Prepare attack payload
        const payload = {
            attacker: attacker,
            blocks: blocks,
            amount: amount,
            frontend_config: attackConfig
        };

        console.log('Sending attack config:', payload);

        // Send attack request to backend
        const response = await fetch('/api/attack/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Attack request failed');

        const data = await response.json();
        console.log('Attack response:', data);

        const box = document.getElementById('attack-output');

        if (box) {
            box.style.display = 'block';

            // Create detailed attack report HTML
            let attackHTML = `
                <p>🎯 <strong>Double-Spending Attack Results</strong></p>
                <div class="attack-steps">
            `;

            // Add each attack step to the report
            data.steps.forEach((step, index) => {
                attackHTML += `<div class="attack-step"><strong>Step ${index + 1}:</strong> ${step.action}`;
                if (step.result) attackHTML += ` - Success`;
                if (step.error) attackHTML += ` - Error: ${step.error}`;
                if (step.mining_success !== undefined) attackHTML += ` - Mining: ${step.mining_success ? '✅' : '❌'}`;
                attackHTML += `</div>`;
            });

            const attackSuccessful = data.successful;

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
                    <p>Success Rate: <strong>${(data.success_rate * 100 || 0).toFixed(1)}%</strong></p>
                    <p>Blocks Mined: <strong>${data.steps.find(s => s.action === 'private_mined_blocks')?.count || 0}</strong></p>
                </div>
            `;

            box.innerHTML = createUserFriendlyOutput(attackHTML, 'Attack Simulation Complete');
            showNotification(`Attack ${attackSuccessful ? 'successful' : 'failed'} (${(data.success_rate * 100).toFixed(1)}% success rate)`,
                           attackSuccessful ? 'success' : 'error');
        }

    } catch (error) {
        showNotification('Attack simulation failed: ' + error.message, 'error');
    }
}

// ----------------------------
// Other Functions
// ----------------------------

/**
 * Add a new peer to the network
 */
async function addPeer() {
    const peerAddress = document.getElementById('peer-address').value.trim();

    if (!peerAddress) {
        showNotification('Please enter a valid peer address', 'error');
        return;
    }

    try {
        showNotification('Adding peer...', 'info');

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
                showNotification('Peer added successfully!', 'success');
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>❌ <strong>Failed to Add Peer</strong></p>
                    <p>Error: ${data.error || 'Unknown error'}</p>
                `, 'Network Error');
                showNotification('Failed to add peer', 'error');
            }
        }

    } catch (error) {
        showNotification('Failed to add peer: ' + error.message, 'error');
    }
}

/**
 * Resolve blockchain conflicts with network consensus
 */
async function resolveConflicts() {
    try {
        showNotification('Checking network consensus...', 'info');

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
                showNotification('Chain replaced with longer chain', 'success');

                // Refresh data after chain replacement
                setTimeout(() => {
                    refreshChain();
                    refreshBalances();
                    loadAllCharts();
                }, 500);
            } else {
                box.innerHTML = createUserFriendlyOutput(`
                    <p>✅ <strong>Chain is Authoritative</strong></p>
                    <p>Our chain is the longest and most valid chain in the network.</p>
                    <p>Current chain length: ${data.chain.length} blocks</p>
                `, 'Consensus Results');
                showNotification('Our chain is authoritative', 'success');
            }
        }

    } catch (error) {
        showNotification('Failed to run consensus: ' + error.message, 'error');
    }
}

/**
 * Run SimBlock analysis simulation
 */
async function runAnalysis() {
    const spinner = document.getElementById('loading-spinner');
    const summaryBox = document.getElementById('simulation-summary');

    try {
        spinner.style.display = 'inline';
        summaryBox.style.display = 'none';
        showNotification('Running simulation analysis...', 'info');

        const response = await fetch('/api/analyze');
        if (!response.ok) throw new Error('Analysis failed');

        const data = await response.json();
        spinner.style.display = 'none';
        summaryBox.style.display = 'block';

        // Update summary table with simulation results
        const tableBody = document.getElementById('summary-table').getElementsByTagName('tbody')[0];
        if (tableBody) {
            tableBody.innerHTML = '';

            const metrics = {
                'Attack Probability': `${((data.attack_probability || 0) * 100).toFixed(1)}%`,
                'Total Blocks': data.total_blocks || 0,
                'Average Block Time': data.avg_block_time ? `${data.avg_block_time.toFixed(2)} ms` : 'N/A',
                'Forks Detected': data.forks_detected || 0,
                'Total Miners': data.total_miners || 0
            };

            // Add each metric to the table
            for (const [key, value] of Object.entries(metrics)) {
                const row = tableBody.insertRow();
                row.innerHTML = `<td><strong>${key}</strong></td><td>${value}</td>`;
            }
        }

        // Update SimBlock chart with results
        setTimeout(() => updateSimblockChart(data), 100);
        showNotification('Simulation completed successfully!', 'success');

    } catch (error) {
        spinner.style.display = 'none';
        showNotification('Simulation failed: ' + error.message, 'error');
    }
}

/**
 * Download comprehensive PDF report
 */
async function downloadPDF() {
    const spinner = document.getElementById('pdf-spinner');

    try {
        spinner.style.display = 'inline';
        showNotification('Generating PDF report...', 'info');

        const response = await fetch('/api/report/pdf');
        if (!response.ok) throw new Error('PDF generation failed');

        // Create download link for PDF
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Blockchain-Report.pdf';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        showNotification('PDF report downloaded successfully!', 'success');
    } catch (error) {
        showNotification('PDF generation failed: ' + error.message, 'error');
    } finally {
        spinner.style.display = 'none';
    }
}

// ----------------------------
// Chart Dashboard Creation
// ----------------------------

/**
 * Create the charts dashboard section dynamically
 */
function createChartsDashboard() {
    const chartsSection = document.createElement('div');
    chartsSection.id = 'charts-dashboard';
    chartsSection.style.display = 'none';
    chartsSection.innerHTML = `
        <div class="section-box">
            <h3>📊 Blockchain Analytics Dashboard</h3>
            <p>Comprehensive visualization of blockchain data and network analytics</p>

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
            </div>

            <div class="chart-actions">
                <button class="primary-btn" onclick="loadAllCharts()">Refresh All Charts</button>
                <button class="primary-btn" onclick="toggleChartSection('charts-dashboard')">Hide Dashboard</button>
            </div>
        </div>
    `;

    // Insert charts dashboard after the introduction section
    const introSection = document.querySelector('.header-text');
    if (introSection) {
        introSection.parentNode.insertBefore(chartsSection, introSection.nextSibling);
    }

    console.log('✅ Charts dashboard created successfully');
}

// ----------------------------
// Event Listener Initialization
// ----------------------------

/**
 * Initialize all event listeners for buttons and interactions
 */
function initializeEventListeners() {
    console.log('🔧 Initializing event listeners...');

    // Add charts dashboard toggle button to header
    const header = document.querySelector('.header-text');
    if (header) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'primary-btn';
        toggleBtn.style.margin = '10px';
        toggleBtn.textContent = 'Show Analytics Dashboard';
        toggleBtn.onclick = function() { toggleChartSection('charts-dashboard'); };
        header.appendChild(toggleBtn);
    }

    // Define all buttons and their corresponding functions
    const buttons = [
        { id: 'submit-tx-btn', func: submitTransaction, name: 'Transaction' },
        { id: 'mine-btn', func: mineBlock, name: 'Mine Block' },
        { id: 'refresh-balances-btn', func: refreshBalances, name: 'Refresh Balances' },
        { id: 'refresh-chain-btn', func: refreshChain, name: 'Refresh Chain' },
        { id: 'run-attack-btn', func: runAttack, name: 'Run Attack' },
        { id: 'add-peer-btn', func: addPeer, name: 'Add Peer' },
        { id: 'resolve-conflicts-btn', func: resolveConflicts, name: 'Resolve Conflicts' },
        { id: 'run-analysis-btn', func: runAnalysis, name: 'Run Analysis' },
        { id: 'download-report-btn', func: downloadPDF, name: 'Download PDF' }
    ];

    // Add event listeners to all buttons
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

// ----------------------------
// DOM Ready
// ----------------------------

/**
 * Initialize the application when DOM is fully loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM fully loaded!');

    // Initialize attack controls
    updateControlStatus();

    // Create charts dashboard
    createChartsDashboard();

    // Initialize charts
    initializeCharts();

    // Initialize event listeners
    initializeEventListeners();

    // Load initial data after short delay
    setTimeout(() => {
        refreshBalances();
        refreshChain();
        showNotification('✅ Blockchain UI with Charts Ready!', 'success');
    }, 2000);
});

console.log('✅ app.js with charts loaded successfully!');