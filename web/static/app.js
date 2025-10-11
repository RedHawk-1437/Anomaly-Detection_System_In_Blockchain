// app.js - USER-FRIENDLY OUTPUT VERSION WITH ATTACK VISUALIZATION
console.log('🔧 app.js loading with user-friendly outputs and attack visualization...');

// ================================
// GLOBAL VARIABLES
// ================================
let attackConfig = {
    successProbability: 0.5,
    attackerHashPower: 30,
    forceSuccess: false,
    forceFailure: false
};

let networkCharts = {
    activityChart: null,
    blockchainDataChart: null,
    attackAnalysisChart: null,
    nodeDistributionChart: null
};

// Store attack history for analysis
let attackHistory = [];

// ================================
// ATTACK VISUALIZATION FUNCTIONS
// ================================

/**
 * Update attack visualization with transaction details
 */
function updateAttackVisualization(attackData) {
    if (!attackData) return;

    // Step 1: Legitimate Transaction
    updateLegitimateTransaction(attackData);

    // Step 2: Malicious Transaction
    updateMaliciousTransaction(attackData);

    // Step 3: Private Mining
    updatePrivateMining(attackData);

    // Step 4: Network Race
    simulateNetworkRace(attackData); // FIXED: Changed from updateNetworkRace to simulateNetworkRace
}

/**
 * Update legitimate transaction display
 */
function updateLegitimateTransaction(attackData) {
    const sender = attackData.attacker || 'RedHawk';
    const victim = 'Victim_Wallet';
    const amount = attackData.amount || 10;
    const timestamp = new Date().toLocaleString();

    document.getElementById('attack-sender').textContent = sender;
    document.getElementById('attack-victim').textContent = victim;
    document.getElementById('attack-amount-display').textContent = amount;
    document.getElementById('attack-time').textContent = timestamp;

    // Mark step as completed
    document.getElementById('step1').classList.add('completed');
}

/**
 * Update malicious transaction display
 */
function updateMaliciousTransaction(attackData) {
    const sender = attackData.attacker || 'RedHawk';
    const receiver = attackData.attacker || 'RedHawk'; // Sending to self
    const amount = attackData.amount || 10;
    const timestamp = new Date().toLocaleString();

    document.getElementById('malicious-sender').textContent = sender;
    document.getElementById('malicious-receiver').textContent = receiver;
    document.getElementById('malicious-amount').textContent = amount;
    document.getElementById('malicious-time').textContent = timestamp;

    // Mark step as completed
    document.getElementById('step2').classList.add('completed');
}

/**
 * Update private mining visualization
 */
function updatePrivateMining(attackData) {
    const blocksToMine = attackData.blocks || 1;
    const miningStatus = document.getElementById('mining-status');
    const progressFill = document.getElementById('mining-progress');
    const progressText = document.getElementById('mining-text');
    const privateBlocksList = document.getElementById('private-blocks-list');

    // Clear previous blocks
    privateBlocksList.innerHTML = '';

    // Simulate mining progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += 5;
        if (progress <= 100) {
            progressFill.style.width = progress + '%';
            progressText.textContent = progress + '%';
            miningStatus.textContent = `⛏️ Mining private blocks... (${progress}%)`;
        } else {
            clearInterval(interval);

            // Add private blocks to display
            for (let i = 0; i < blocksToMine; i++) {
                const blockElement = document.createElement('div');
                blockElement.className = 'private-block';
                blockElement.textContent = `Private Block ${i + 1}`;
                privateBlocksList.appendChild(blockElement);
            }

            miningStatus.textContent = '✅ Private blocks mined successfully!';
            miningStatus.style.color = '#27ae60';

            // Mark step as completed
            document.getElementById('step3').classList.add('completed');
        }
    }, 200);
}

/**
 * Simulate network race between honest and attacker chains - FIXED FUNCTION NAME
 */
function simulateNetworkRace(attackData) {
    const honestBlocks = document.getElementById('honest-blocks');
    const attackerBlocks = document.getElementById('attacker-blocks');
    const raceResult = document.getElementById('race-result');

    // Clear previous blocks
    honestBlocks.innerHTML = '';
    attackerBlocks.innerHTML = '';
    raceResult.innerHTML = '';

    const blocksToMine = attackData.blocks || 1;
    const isSuccessful = attackData.result?.successful || false;

    // Add existing honest blocks
    for (let i = 0; i < 3; i++) {
        const block = document.createElement('div');
        block.className = 'block honest-block';
        block.textContent = i + 1;
        honestBlocks.appendChild(block);
    }

    // Add attacker blocks with animation
    let attackerBlockCount = 0;
    const attackerInterval = setInterval(() => {
        if (attackerBlockCount < blocksToMine) {
            const block = document.createElement('div');
            block.className = 'block attack-block';
            block.textContent = 3 + attackerBlockCount + 1;
            attackerBlocks.appendChild(block);
            attackerBlockCount++;
        } else {
            clearInterval(attackerInterval);

            // Show race result
            if (isSuccessful) {
                raceResult.className = 'race-result race-success';
                raceResult.innerHTML = '🎯 ATTACK SUCCESSFUL!<br>Attacker chain is longer and wins the race!';
            } else {
                raceResult.className = 'race-result race-failure';
                raceResult.innerHTML = '🛡️ ATTACK FAILED!<br>Honest chain remains the longest!';
            }

            // Mark step as completed
            document.getElementById('step4').classList.add('completed');
        }
    }, 500);

    // Add one more honest block to show the race
    setTimeout(() => {
        if (!isSuccessful) {
            const block = document.createElement('div');
            block.className = 'block honest-block';
            block.textContent = '4';
            honestBlocks.appendChild(block);
        }
    }, 1500);
}

/**
 * Reset attack visualization
 */
function resetAttackVisualization() {
    // Reset all steps
    const steps = document.querySelectorAll('.process-step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed', 'failed');
    });

    // Reset mining progress
    document.getElementById('mining-progress').style.width = '0%';
    document.getElementById('mining-text').textContent = '0%';
    document.getElementById('mining-status').textContent = '⏳ Waiting for attack...';
    document.getElementById('mining-status').style.color = '';

    // Clear blocks
    document.getElementById('private-blocks-list').innerHTML = '';
    document.getElementById('honest-blocks').innerHTML = '';
    document.getElementById('attacker-blocks').innerHTML = '';
    document.getElementById('race-result').innerHTML = '';

    // Reset transaction displays
    const txElements = [
        'attack-sender', 'attack-victim', 'attack-amount-display', 'attack-time',
        'malicious-sender', 'malicious-receiver', 'malicious-amount', 'malicious-time'
    ];

    txElements.forEach(id => {
        document.getElementById(id).textContent = '--';
    });
}

/**
 * Enhanced attack simulation with visualization
 */
async function runAttackWithVisualization() {
    console.log('🎯 Running attack simulation with visualization...');

    // Reset previous visualization
    resetAttackVisualization();

    const attacker = document.getElementById('attack-attacker').value.trim() || 'RedHawk';
    const blocks = parseInt(document.getElementById('attack-blocks').value) || 1;
    const amount = parseFloat(document.getElementById('attack-amount').value) || 10.0;

    if (blocks <= 0 || amount <= 0) {
        showNotification('❌ Please enter valid values for blocks and amount', 'error');
        return;
    }

    try {
        showNotification('🚀 Starting attack simulation with visualization...', 'info');

        const payload = {
            attacker: attacker,
            blocks: blocks,
            amount: amount,
            frontend_config: {
                hash_power: attackConfig.attackerHashPower,
                success_probability: attackConfig.successProbability * 100,
                force_success: attackConfig.forceSuccess,
                force_failure: attackConfig.forceFailure,
                latency: 100
            }
        };

        // Prepare attack data for visualization
        const attackData = {
            attacker: attacker,
            blocks: blocks,
            amount: amount,
            config: payload.frontend_config
        };

        // Start visualization
        updateAttackVisualization(attackData);

        const response = await fetch('/api/attack/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('🎯 Attack response:', data);

        // Update visualization with actual result
        attackData.result = data;
        simulateNetworkRace(attackData); // FIXED: Use correct function name

        const box = document.getElementById('attack-output');
        if (box) {
            box.style.display = 'block';
            box.textContent = formatAttackResponse(data);
        }

        const attackSuccessful = data.successful || false;
        if (attackSuccessful) {
            showNotification('🎯 Attack successful! Double spending achieved!', 'success');
        } else {
            showNotification('🛡️ Attack prevented! Network security maintained.', 'info');
        }

        // Refresh all data and charts after attack
        refreshEnhancedBalances();
        refreshChain();
        setTimeout(refreshAllCharts, 1500);

    } catch (error) {
        console.error('Attack simulation error:', error);
        showNotification('💥 Attack failed: ' + error.message, 'error');

        const box = document.getElementById('attack-output');
        if (box) {
            box.style.display = 'block';
            box.textContent = `❌ ATTACK SIMULATION FAILED\n\n📛 Error: ${error.message}\n\n💡 Please make sure the backend server is running on http://127.0.0.1:5000`;
        }

        // Mark steps as failed
        document.getElementById('step3').classList.add('failed');
        document.getElementById('step4').classList.add('failed');
    }
}

// ================================
// USER-FRIENDLY OUTPUT FORMATTING
// ================================

/**
 * Format transaction response for user-friendly display
 */
function formatTransactionResponse(data) {
    if (!data) return 'No response data received';

    let output = '';

    if (data.status === 'ok') {
        output += '✅ TRANSACTION SUCCESSFUL\n\n';
        output += `📧 Transaction ID: ${data.txid.substring(0, 16)}...\n`;
        output += `📊 Pending Transactions: ${data.mempool_size}\n`;
        output += `⏰ Status: Confirmed and added to mempool\n\n`;
        output += '💡 The transaction is now waiting to be included in the next block.';
    } else {
        output += '❌ TRANSACTION FAILED\n\n';
        output += `📛 Error: ${data.error || 'Unknown error'}\n`;
        output += '💡 Please check the sender balance and try again.';
    }

    return output;
}

/**
 * Format mining response for user-friendly display
 */
function formatMiningResponse(data) {
    if (!data) return 'No response data received';

    let output = '';

    if (data.status === 'ok') {
        output += '⛏️ BLOCK MINED SUCCESSFULLY\n\n';
        output += `📦 Block #${data.block.index} created\n`;
        output += `🔗 Block Hash: ${data.block.hash.substring(0, 16)}...\n`;
        output += `⏰ Timestamp: ${new Date(data.block.timestamp * 1000).toLocaleString()}\n`;
        output += `📊 Transactions in block: ${data.block.transactions.length}\n`;
        output += `⛓️ Total blocks in chain: ${data.chain_length}\n\n`;

        // Show transaction summary
        const userTransactions = data.block.transactions.filter(tx => tx.sender !== 'SYSTEM');
        const rewardTransactions = data.block.transactions.filter(tx => tx.sender === 'SYSTEM');

        if (userTransactions.length > 0) {
            output += '💸 User Transactions:\n';
            userTransactions.forEach(tx => {
                output += `   • ${tx.sender} → ${tx.receiver}: ${tx.amount} coins\n`;
            });
        }

        if (rewardTransactions.length > 0) {
            output += '💰 Mining Rewards:\n';
            rewardTransactions.forEach(tx => {
                output += `   • SYSTEM → ${tx.receiver}: ${tx.amount} coins (mining reward)\n`;
            });
        }

    } else {
        output += '❌ MINING FAILED\n\n';
        output += `📛 Error: ${data.error || 'Unknown error'}\n`;
        output += '💡 Please try again or check for pending transactions.';
    }

    return output;
}

/**
 * Format balances for user-friendly display
 */
function formatBalancesResponse(data) {
    if (!data) return 'No balance data received';

    let output = '';
    output += '💰 WALLET BALANCES OVERVIEW\n\n';

    const { balances, attack_info, total_wallets, active_attacks } = data;

    output += `📊 Total Wallets: ${total_wallets}\n`;
    output += `🛡️ Active Attacks: ${active_attacks}\n\n`;

    // Display balances
    output += '💳 CURRENT BALANCES:\n';
    Object.entries(balances).forEach(([wallet, balance]) => {
        const status = balance >= 0 ? '✅' : '⚠️';
        output += `   ${status} ${wallet}: ${balance.toFixed(2)} coins\n`;
    });

    // Display attack information
    if (Object.keys(attack_info).length > 0) {
        output += '\n🦠 ATTACK ACTIVITY:\n';
        Object.entries(attack_info).forEach(([attacker, info]) => {
            const attackResult = info.success ? 'SUCCESSFUL 🎯' : 'FAILED 🚫';
            const victimInfo = info.victim === 'None (Attack Failed)' ? 'No victim (attack failed)' : info.victim;
            output += `   • ${attacker}: ${attackResult}\n`;
            output += `     Amount: ${info.amount} coins | Victim: ${victimInfo}\n`;
        });
    }

    return output;
}

/**
 * Format blockchain data for user-friendly display
 */
function formatChainResponse(data) {
    if (!data) return 'No blockchain data received';

    let output = '';
    output += '⛓️ BLOCKCHAIN EXPLORER\n\n';

    const { length, lastBlock, mempoolSize, difficulty } = data;

    output += `📊 Blockchain Summary:\n`;
    output += `   • Total Blocks: ${length}\n`;
    output += `   • Pending Transactions: ${mempoolSize}\n`;
    output += `   • Mining Difficulty: ${difficulty}\n\n`;

    if (lastBlock) {
        output += `📦 Latest Block (#${lastBlock.index}):\n`;
        output += `   • Hash: ${lastBlock.hash.substring(0, 20)}...\n`;
        output += `   • Timestamp: ${new Date(lastBlock.timestamp * 1000).toLocaleString()}\n`;
        output += `   • Transactions: ${lastBlock.transactions.length}\n`;

        if (lastBlock.transactions.length > 0) {
            output += `   • Recent Activity:\n`;
            lastBlock.transactions.slice(0, 3).forEach(tx => {
                if (tx.sender === 'SYSTEM') {
                    output += `     💎 ${tx.receiver} received ${tx.amount} coins (mining reward)\n`;
                } else {
                    output += `     💸 ${tx.sender} → ${tx.receiver}: ${tx.amount} coins\n`;
                }
            });
            if (lastBlock.transactions.length > 3) {
                output += `     ... and ${lastBlock.transactions.length - 3} more transactions\n`;
            }
        }
    }

    return output;
}

/**
 * Format attack simulation response for user-friendly display
 */
function formatAttackResponse(data) {
    if (!data) return 'No attack data received';

    let output = '';

    if (data.successful) {
        output += '🎯 DOUBLE SPENDING ATTACK SUCCESSFUL!\n\n';
        output += '💀 Attack Summary:\n';
        output += `   • Status: COMPROMISED 🚨\n`;
        output += `   • Attack Type: Double Spending\n`;
        output += `   • Success Probability: ${(data.success_probability || 0).toFixed(1)}%\n`;
        output += `   • Blocks Mined Privately: ${data.blocks_mined || 0}\n`;
        output += `   • Hash Power Used: ${data.hash_power || 0}%\n\n`;
    } else {
        output += '🛡️ ATTACK PREVENTED!\n\n';
        output += '✅ Defense Summary:\n';
        output += `   • Status: BLOCKED ✅\n`;
        output += `   • Attack Type: Double Spending\n`;
        output += `   • Success Probability: ${(data.success_probability || 0).toFixed(1)}%\n`;
        output += `   • Reason: ${data.message || 'Network consensus rejected private chain'}\n\n`;
    }

    // Add execution steps
    if (data.steps && data.steps.length > 0) {
        output += '🔧 Attack Execution Steps:\n';
        data.steps.forEach((step, index) => {
            const stepNumber = index + 1;
            if (step.action === 'improved_probability') {
                output += `   ${stepNumber}. Probability Calculation: ${step.result ? 'Favorable' : 'Unfavorable'}\n`;
            } else if (step.action === 'mining') {
                output += `   ${stepNumber}. Private Mining: ${step.mining_success ? 'Successful' : 'Failed'}\n`;
            } else if (step.action === 'broadcast') {
                output += `   ${stepNumber}. Network Broadcast: ${step.result ? 'Accepted' : 'Rejected'}\n`;
            } else {
                output += `   ${stepNumber}. ${step.action}: ${step.result || step.mining_success || 'Completed'}\n`;
            }
        });
    }

    output += '\n💡 ' + (data.successful ?
        'The attacker successfully spent the same coins twice!' :
        'The network successfully detected and prevented the double spending attempt.');

    return output;
}

/**
 * Format peer network response for user-friendly display
 */
function formatPeerResponse(data) {
    if (!data) return 'No network data received';

    let output = '';

    if (data.message && data.message.includes('added successfully')) {
        output += '✅ PEER CONNECTION ESTABLISHED\n\n';
        output += `🌐 New peer added to network\n`;
        output += `📡 Connected Peers: ${data.peers ? data.peers.length : 1}\n\n`;

        if (data.peers && data.peers.length > 0) {
            output += '🔗 Active Peer Connections:\n';
            data.peers.forEach(peer => {
                output += `   • ${peer}\n`;
            });
        }
    } else {
        output += '❌ PEER CONNECTION FAILED\n\n';
        output += `📛 Error: ${data.error || 'Unknown connection error'}\n`;
        output += '💡 Please check the peer address and try again.';
    }

    return output;
}

/**
 * Format consensus response for user-friendly display
 */
function formatConsensusResponse(data) {
    if (!data) return 'No consensus data received';

    let output = '';

    if (data.message && data.message.includes('authoritative')) {
        output += '✅ NETWORK CONSENSUS VERIFIED\n\n';
        output += '🔄 Consensus Check Results:\n';
        output += `   • Status: SYNCHRONIZED ✅\n`;
        output += `   • Local Chain: UP-TO-DATE\n`;
        output += `   • Total Blocks: ${data.chain ? data.chain.length : 'Unknown'}\n`;
        output += `   • Result: No conflicts detected\n\n`;
        output += '💡 Your node has the longest and most valid chain.';
    } else if (data.message && data.message.includes('replaced')) {
        output += '🔄 NETWORK CHAIN UPDATED\n\n';
        output += '📥 Consensus Check Results:\n';
        output += `   • Status: UPDATED 🔄\n`;
        output += `   • Action: Chain replaced with longer valid chain\n`;
        output += `   • New Total Blocks: ${data.new_chain ? data.new_chain.length : 'Unknown'}\n`;
        output += `   • Result: Synchronized with network\n\n`;
        output += '💡 Your node accepted a longer valid chain from the network.';
    } else {
        output += '❌ CONSENSUS CHECK FAILED\n\n';
        output += `📛 Error: ${data.error || 'Unknown consensus error'}\n`;
        output += '💡 Network synchronization issue detected.';
    }

    return output;
}

/**
 * Format SimBlock response for user-friendly display
 */
function formatSimBlockResponse(data) {
    if (!data) return 'No simulation data received';

    let output = '';

    if (data.success) {
        output += '🌐 SIMBLOCK NETWORK SIMULATION COMPLETE\n\n';
        output += '📊 Simulation Results:\n';
        output += `   • Status: SUCCESSFUL ✅\n`;
        output += `   • Network: 120+ nodes initialized\n`;
        output += `   • Regions: Global distribution active\n`;
        output += `   • Latency: Realistic network conditions\n`;
        output += `   • Attack Simulation: Ready\n\n`;
        output += '💡 Large-scale P2P network is now active for testing.';
    } else {
        output += '❌ SIMBLOCK SIMULATION FAILED\n\n';
        output += `📛 Error: ${data.error || 'Simulation initialization failed'}\n`;
        output += '💡 Please check the SimBlock configuration.';
    }

    return output;
}

// ================================
// NOTIFICATION SYSTEM
// ================================
function showNotification(message, type = 'info') {
    console.log(`📢 ${type.toUpperCase()}:`, message);

    // Clear existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());

    const notification = document.createElement('div');
    notification.className = 'notification';

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
    `;

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

// ================================
// ENHANCED CHART SYSTEM - SYNCHRONIZED
// ================================

/**
 * Initialize synchronized charts
 */
function initializeNetworkCharts() {
    console.log('📊 Initializing synchronized charts...');

    // Destroy existing charts to prevent duplicates
    Object.values(networkCharts).forEach(chart => {
        if (chart) {
            chart.destroy();
        }
    });

    createNetworkActivityChart();
    createBlockchainDataChart();
    createAttackAnalysisChart();
    createNodeDistributionChart();

    // Load initial data immediately
    setTimeout(updateChartsWithRealData, 500);
    showNotification('📈 Charts initialized! Loading real data...', 'info');
}

/**
 * Create network activity chart
 */
function createNetworkActivityChart() {
    const ctx = document.getElementById('networkActivityChart');
    if (!ctx) {
        console.error('❌ Network Activity Chart canvas not found');
        return;
    }

    networkCharts.activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Loading...',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Network Activity - Loading...',
                    font: { size: 14, weight: 'bold' }
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Transaction Count' }
                },
                x: {
                    title: { display: true, text: 'Block Height' }
                }
            }
        }
    });
}

/**
 * Create blockchain data chart - INDIVIDUAL BLOCKS
 */
function createBlockchainDataChart() {
    const ctx = document.getElementById('blockchainDataChart');
    if (!ctx) {
        console.error('❌ Blockchain Data Chart canvas not found');
        return;
    }

    networkCharts.blockchainDataChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Honest Blocks',
                    data: [],
                    backgroundColor: 'rgba(52, 152, 219, 0.8)',
                    borderColor: '#2980b9',
                    borderWidth: 1
                },
                {
                    label: 'Attack Blocks',
                    data: [],
                    backgroundColor: 'rgba(231, 76, 60, 0.8)',
                    borderColor: '#c0392b',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Blockchain Data - Loading...',
                    font: { size: 14, weight: 'bold' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const datasetIndex = context.datasetIndex;
                            const value = context.parsed.y;
                            const blockIndex = context.dataIndex;
                            const blockLabel = context.chart.data.labels[blockIndex];

                            if (value > 0) {
                                if (datasetIndex === 0) {
                                    return `Honest Block: ${blockLabel}`;
                                } else {
                                    return `Attack Block: ${blockLabel}`;
                                }
                            }
                            return '';
                        }
                    }
                }
            },
            scales: {
                y: {
                    display: false, // Hide Y axis as we're showing individual blocks
                    beginAtZero: true
                },
                x: {
                    title: { display: true, text: 'Block Index' }
                }
            }
        }
    });
}

/**
 * Create enhanced attack analysis chart with ATTACKER NODES metric
 */
function createAttackAnalysisChart() {
    const ctx = document.getElementById('attackAnalysisChart');
    if (!ctx) {
        console.error('❌ Attack Analysis Chart canvas not found');
        return;
    }

    networkCharts.attackAnalysisChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [
                'Success Rate',
                'Hash Power',
                'Blocks Mined',
                'Amount Stolen',
                'Attacker Nodes',
                'Latency Impact',
                'Network Health'
            ],
            datasets: [{
                label: 'Attack Metrics',
                data: [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(46, 204, 113, 0.8)',    // Success Rate - Green
                    'rgba(52, 152, 219, 0.8)',    // Hash Power - Blue
                    'rgba(155, 89, 182, 0.8)',    // Blocks Mined - Purple
                    'rgba(241, 196, 15, 0.8)',    // Amount Stolen - Yellow
                    'rgba(230, 126, 34, 0.8)',    // Attacker Nodes - Orange (NEW)
                    'rgba(231, 76, 60, 0.8)',     // Latency Impact - Red
                    'rgba(149, 165, 166, 0.8)'    // Network Health - Gray
                ],
                borderColor: [
                    '#27ae60',    // Success Rate
                    '#2980b9',    // Hash Power
                    '#8e44ad',    // Blocks Mined
                    '#f39c12',    // Amount Stolen
                    '#d35400',    // Attacker Nodes (NEW)
                    '#c0392b',    // Latency Impact
                    '#7f8c8d'     // Network Health
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Double Spending Attack Analysis',
                    font: { size: 14, weight: 'bold' }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            const metric = context.chart.data.labels[context.dataIndex];

                            switch(metric) {
                                case 'Success Rate':
                                    return `${label}: ${value.toFixed(1)}%`;
                                case 'Hash Power':
                                    return `${label}: ${value.toFixed(1)}%`;
                                case 'Blocks Mined':
                                    return `${label}: ${value} blocks`;
                                case 'Amount Stolen':
                                    return `${label}: ${value} coins`;
                                case 'Attacker Nodes':
                                    return `${label}: ${value} nodes`;
                                case 'Latency Impact':
                                    return `${label}: ${value.toFixed(1)}%`;
                                case 'Network Health':
                                    return `${label}: ${value.toFixed(1)}%`;
                                default:
                                    return `${label}: ${value}`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Percentage/Value' }
                }
            }
        }
    });
}

/**
 * Create node distribution chart as bar chart
 */
function createNodeDistributionChart() {
    const ctx = document.getElementById('nodeDistributionChart');
    if (!ctx) {
        console.error('❌ Node Distribution Chart canvas not found');
        return;
    }

    networkCharts.nodeDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania'],
            datasets: [{
                label: 'Node Count',
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.7)',
                    'rgba(46, 204, 113, 0.7)',
                    'rgba(155, 89, 182, 0.7)',
                    'rgba(241, 196, 15, 0.7)',
                    'rgba(230, 126, 34, 0.7)',
                    'rgba(231, 76, 60, 0.7)'
                ],
                borderColor: [
                    '#3498db',
                    '#2ecc71',
                    '#9b59b6',
                    '#f1c40f',
                    '#e67e22',
                    '#e74c3c'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Global Node Distribution',
                    font: { size: 14, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Number of Nodes' }
                }
            }
        }
    });
}

// ================================
// REAL-TIME DATA UPDATES - SYNCHRONIZED
// ================================

/**
 * Update charts with real blockchain data
 */
async function updateChartsWithRealData() {
    try {
        console.log('🔄 Fetching real data for charts...');

        const [chainResponse, balancesResponse, networkResponse] = await Promise.allSettled([
            fetch('/api/chain').catch(() => ({ ok: false })),
            fetch('/api/balances/detailed').catch(() => ({ ok: false })),
            fetch('/api/simblock/network').catch(() => ({ ok: false }))
        ]);

        let chainData = { chain: [] };
        let balancesData = { balances: {}, attack_info: {} };
        let networkData = {};

        if (chainResponse.status === 'fulfilled' && chainResponse.value.ok) {
            chainData = await chainResponse.value.json();
            console.log('📦 Chain data loaded:', chainData.chain.length, 'blocks');
        }

        if (balancesResponse.status === 'fulfilled' && balancesResponse.value.ok) {
            balancesData = await balancesResponse.value.json();
            console.log('💰 Balance data loaded');
        }

        if (networkResponse.status === 'fulfilled' && networkResponse.value.ok) {
            networkData = await networkResponse.value.json();
            console.log('🌐 Network data loaded');
        }

        updateAllChartsWithData(chainData, balancesData, networkData);
        showNotification('📈 Charts updated with real data!', 'success');

    } catch (error) {
        console.error('Error updating charts:', error);
        showNotification('❌ Failed to update charts with real data', 'error');
        // Fallback to demo data
        updateChartsWithDemoData();
    }
}

/**
 * Update all charts with real data
 */
function updateAllChartsWithData(chainData, balancesData, networkData) {
    console.log('🔄 Updating all charts with real data...');
    updateNetworkActivityChart(chainData);
    updateBlockchainDataChart(chainData, balancesData);
    updateAttackAnalysisChart(chainData, balancesData, networkData);
    updateNodeDistributionChart(networkData);
    updateRealTimeMetrics(networkData, balancesData, chainData);
}

/**
 * Update network activity chart with real data - FIXED to show ALL blocks
 */
function updateNetworkActivityChart(chainData) {
    if (!networkCharts.activityChart) return;

    const blocks = chainData.chain || [];

    if (blocks.length === 0) {
        networkCharts.activityChart.data.labels = ['No blocks yet'];
        networkCharts.activityChart.data.datasets[0].data = [0];
        networkCharts.activityChart.data.datasets[0].label = 'No transactions';
    } else {
        // Show ALL blocks, not just recent ones
        const labels = blocks.map(block => `Block ${block.index}`);
        const txCounts = blocks.map(block => block.transactions ? block.transactions.length : 0);

        networkCharts.activityChart.data.labels = labels;
        networkCharts.activityChart.data.datasets[0].data = txCounts;
        networkCharts.activityChart.data.datasets[0].label = 'Transactions per Block';
    }

    networkCharts.activityChart.options.plugins.title.text = `Network Activity (${blocks.length} blocks)`;
    networkCharts.activityChart.update();
    console.log('✅ Network activity chart updated - Blocks:', blocks.length);
}

/**
 * Update blockchain data chart with INDIVIDUAL BLOCKS - FIXED to show ALL blocks
 */
function updateBlockchainDataChart(chainData, balancesData) {
    if (!networkCharts.blockchainDataChart) return;

    const blocks = chainData.chain || [];
    const attackInfo = balancesData.attack_info || {};

    // Get successful attacks
    const successfulAttacks = Object.values(attackInfo).filter(info => info.success === true);
    const successfulAttackBlocks = successfulAttacks.length;

    // Prepare data for ALL individual blocks
    const blockLabels = blocks.map(block => `Block ${block.index}`);
    const honestBlockData = new Array(blocks.length).fill(0);
    const attackBlockData = new Array(blocks.length).fill(0);

    // All blocks start as honest (1)
    for (let i = 0; i < blocks.length; i++) {
        honestBlockData[i] = 1;
    }

    // Mark attack blocks only if there are successful attacks
    // We'll mark the most recent blocks as attack blocks based on successful attacks
    if (successfulAttackBlocks > 0 && blocks.length > 0) {
        // Start marking from the end backwards for the most recent attacks
        for (let i = 0; i < successfulAttackBlocks && i < blocks.length; i++) {
            const blockIndex = blocks.length - 1 - i;
            honestBlockData[blockIndex] = 0; // Remove from honest
            attackBlockData[blockIndex] = 1; // Mark as attack block
        }
    }

    networkCharts.blockchainDataChart.data.labels = blockLabels;
    networkCharts.blockchainDataChart.data.datasets[0].data = honestBlockData;
    networkCharts.blockchainDataChart.data.datasets[1].data = attackBlockData;

    const totalBlocks = blocks.length;
    const attackBlocks = successfulAttackBlocks;
    const honestBlocks = totalBlocks - attackBlocks;

    networkCharts.blockchainDataChart.options.plugins.title.text = `Blockchain Data (${totalBlocks} blocks, ${attackBlocks} attacks)`;
    networkCharts.blockchainDataChart.update();
    console.log('✅ Blockchain data chart updated - Individual blocks:', {
        totalBlocks: totalBlocks,
        attackBlocks: attackBlocks,
        honestBlocks: honestBlocks,
        labels: blockLabels
    });
}

/**
 * Update enhanced attack analysis with ATTACKER NODES metric
 */
function updateAttackAnalysisChart(chainData, balancesData, networkData) {
    if (!networkCharts.attackAnalysisChart) return;

    const blocks = chainData.chain || [];
    const attackInfo = balancesData.attack_info || {};
    const totalNodes = networkData.node_count || 120;

    // Calculate accurate attack metrics
    const totalAttacks = Object.keys(attackInfo).length;
    const successfulAttacks = Object.values(attackInfo).filter(info => info.success === true).length;
    const failedAttacks = totalAttacks - successfulAttacks;

    // Success rate based on actual attacks
    const successRate = totalAttacks > 0 ? (successfulAttacks / totalAttacks) * 100 : 0;

    // Calculate actual amount stolen only from successful attacks
    const successfulAttackAmount = Object.values(attackInfo)
        .filter(info => info.success === true)
        .reduce((sum, info) => sum + (info.amount || 0), 0);

    // Blocks mined in attacks (only count successful attack blocks)
    const attackBlocks = successfulAttacks;

    // Calculate attacker nodes based on hash power and attack success
    // More hash power and successful attacks indicate more malicious nodes
    const baseMaliciousNodes = Math.floor((attackConfig.attackerHashPower / 100) * totalNodes * 0.3);
    const attackSuccessBonus = successfulAttacks * 2; // More successful attacks = more nodes
    const hashPowerBonus = Math.floor(attackConfig.attackerHashPower / 10);
    const attackerNodes = Math.min(totalNodes * 0.4, baseMaliciousNodes + attackSuccessBonus + hashPowerBonus);

    // Network health (better when fewer successful attacks and malicious nodes)
    const networkHealth = Math.max(0, 100 - (successfulAttacks * 15) - (attackerNodes * 0.5));

    // Latency impact (increases with more attacks and malicious nodes)
    const latencyImpact = Math.min((successfulAttacks * 10) + (attackerNodes * 0.3), 100);

    const metrics = [
        successRate,           // Success Rate (%)
        attackConfig.attackerHashPower, // Hash Power (%)
        attackBlocks,          // Blocks Mined in successful attacks
        successfulAttackAmount, // Amount Stolen (actual amount)
        Math.round(attackerNodes), // Attacker Nodes (NEW METRIC)
        latencyImpact,         // Latency Impact (%)
        networkHealth          // Network Health (%)
    ];

    networkCharts.attackAnalysisChart.data.datasets[0].data = metrics;
    networkCharts.attackAnalysisChart.update();
    console.log('✅ Attack analysis chart updated with attacker nodes:', {
        successRate,
        hashPower: attackConfig.attackerHashPower,
        attackBlocks,
        amountStolen: successfulAttackAmount,
        attackerNodes: Math.round(attackerNodes),
        latencyImpact,
        networkHealth,
        totalNodes
    });
}

/**
 * Update node distribution chart with real data
 */
function updateNodeDistributionChart(networkData) {
    if (!networkCharts.nodeDistributionChart) return;

    const nodeCount = networkData.node_count || 120;
    const distribution = [
        Math.floor(nodeCount * 0.35), // North America
        Math.floor(nodeCount * 0.28), // Europe
        Math.floor(nodeCount * 0.22), // Asia
        Math.floor(nodeCount * 0.08), // South America
        Math.floor(nodeCount * 0.04), // Africa
        Math.floor(nodeCount * 0.03)  // Oceania
    ];

    networkCharts.nodeDistributionChart.data.datasets[0].data = distribution;
    networkCharts.nodeDistributionChart.update();
    console.log('✅ Node distribution chart updated');
}

/**
 * Fallback to demo data if real data fails
 */
function updateChartsWithDemoData() {
    console.log('📊 Using demo data for charts...');

    // Demo network activity
    if (networkCharts.activityChart) {
        networkCharts.activityChart.data.labels = ['Block 1', 'Block 2', 'Block 3'];
        networkCharts.activityChart.data.datasets[0].data = [2, 3, 1];
        networkCharts.activityChart.data.datasets[0].label = 'Transactions (Demo)';
        networkCharts.activityChart.update();
    }

    // Demo blockchain data - individual blocks
    if (networkCharts.blockchainDataChart) {
        networkCharts.blockchainDataChart.data.labels = ['Block 1', 'Block 2', 'Block 3'];
        networkCharts.blockchainDataChart.data.datasets[0].data = [1, 1, 1];
        networkCharts.blockchainDataChart.data.datasets[1].data = [0, 0, 0];
        networkCharts.blockchainDataChart.update();
    }

    // Demo attack analysis - all zeros for fresh start
    if (networkCharts.attackAnalysisChart) {
        networkCharts.attackAnalysisChart.data.datasets[0].data = [0, 0, 0, 0, 0, 0, 100];
        networkCharts.attackAnalysisChart.update();
    }

    // Demo node distribution
    if (networkCharts.nodeDistributionChart) {
        networkCharts.nodeDistributionChart.data.datasets[0].data = [42, 34, 26, 10, 5, 3];
        networkCharts.nodeDistributionChart.update();
    }

    // Demo metrics
    updateRealTimeMetrics(
        { average_latency: 85, node_count: 120 },
        { total_wallets: 0, active_attacks: 0 },
        { chain: Array(3) }
    );
}

/**
 * Update real-time metrics display with actual data
 */
function updateRealTimeMetrics(networkData, balancesData, chainData) {
    const blocks = chainData.chain || [];
    const totalWallets = balancesData.total_wallets || 0;
    const activeAttacks = balancesData.active_attacks || 0;
    const attackInfo = balancesData.attack_info || {};

    // Calculate successful attacks for accurate metrics
    const successfulAttacks = Object.values(attackInfo).filter(info => info.success === true).length;

    // Calculate attacker nodes for real-time metrics
    const totalNodes = networkData.node_count || 120;
    const baseMaliciousNodes = Math.floor((attackConfig.attackerHashPower / 100) * totalNodes * 0.3);
    const attackSuccessBonus = successfulAttacks * 2;
    const hashPowerBonus = Math.floor(attackConfig.attackerHashPower / 10);
    const attackerNodes = Math.min(totalNodes * 0.4, baseMaliciousNodes + attackSuccessBonus + hashPowerBonus);

    const metrics = {
        latency: (networkData.average_latency || 85) + 'ms',
        nodes: (networkData.node_count || 120) + '+',
        throughput: blocks.length > 0 ? Math.floor(blocks.length * 1.5) + '/min' : '0/min',
        blockTime: blocks.length > 1 ? '12.5s' : '--',
        health: Math.max(10, 100 - (successfulAttacks * 15) - (attackerNodes * 0.5)) + '%',
        attack: attackConfig.attackerHashPower + '%'
    };

    // Update metric cards
    Object.keys(metrics).forEach(metric => {
        const element = document.getElementById(metric);
        if (element) {
            element.textContent = metrics[metric];
            element.classList.add('metric-update');
            setTimeout(() => element.classList.remove('metric-update'), 500);
        }
    });

    // Update the specific elements mentioned in HTML
    const specificElements = {
        'current-latency': metrics.latency,
        'active-nodes': metrics.nodes,
        'tx-throughput': metrics.throughput,
        'block-time': metrics.blockTime,
        'network-health': metrics.health,
        'attack-success': metrics.attack
    };

    Object.keys(specificElements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = specificElements[id];
            element.classList.add('metric-update');
            setTimeout(() => element.classList.remove('metric-update'), 500);
        }
    });

    console.log('✅ Real-time metrics updated:', metrics);
}

/**
 * Refresh all charts with latest data
 */
function refreshAllCharts() {
    console.log('🔄 Refreshing all charts with real data...');
    updateChartsWithRealData();
}

/**
 * Export charts as PNG images
 */
function exportCharts() {
    const chartsContainer = document.getElementById('network-charts-dashboard');
    if (!chartsContainer) return;

    const charts = chartsContainer.querySelectorAll('canvas');
    let exported = 0;

    charts.forEach((chart, index) => {
        const link = document.createElement('a');
        link.download = `blockchain-chart-${index + 1}-${new Date().toISOString().split('T')[0]}.png`;
        link.href = chart.toDataURL();
        link.click();
        exported++;
    });

    showNotification(`📸 ${exported} charts exported as PNG!`, 'success');
}

// ================================
// BLOCKCHAIN OPERATIONS - UPDATED WITH USER-FRIENDLY OUTPUTS
// ================================

/**
 * Submit a new transaction
 */
async function submitTransaction() {
    console.log('📝 Submitting transaction...');

    const sender = document.getElementById('tx-sender').value.trim();
    const receiver = document.getElementById('tx-receiver').value.trim();
    const amount = parseFloat(document.getElementById('tx-amount').value);

    if (!sender || !receiver || isNaN(amount) || amount <= 0) {
        showNotification('❌ Please fill all fields with valid values', 'error');
        return;
    }

    try {
        const response = await fetch('/api/tx/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                sender: sender,
                receiver: receiver,
                amount: amount
            })
        });

        const data = await response.json();

        const box = document.getElementById('tx-response');
        if (box) {
            box.style.display = 'block';
            box.textContent = formatTransactionResponse(data);
        }

        if (response.ok) {
            showNotification('✅ Transaction submitted successfully!', 'success');
            // Clear form and refresh data
            document.getElementById('tx-sender').value = '';
            document.getElementById('tx-receiver').value = '';
            document.getElementById('tx-amount').value = '';
            // Refresh charts to show new transaction
            setTimeout(refreshAllCharts, 1000);
        } else {
            showNotification('❌ Transaction failed: ' + (data.error || 'Unknown error'), 'error');
        }

    } catch (error) {
        console.error('Transaction error:', error);
        showNotification('💥 Network error: ' + error.message, 'error');
    }
}

/**
 * Mine a new block
 */
async function mineBlock() {
    console.log('⛏️ Mining block...');

    const miner = document.getElementById('miner-name').value.trim() || 'DefaultMiner';

    try {
        const response = await fetch('/api/mine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                miner: miner
            })
        });

        const data = await response.json();

        const box = document.getElementById('mine-response');
        if (box) {
            box.style.display = 'block';
            box.textContent = formatMiningResponse(data);
        }

        if (response.ok) {
            showNotification('✅ Block mined successfully!', 'success');
            refreshEnhancedBalances();
            refreshChain();
            // Refresh charts to show new block
            setTimeout(refreshAllCharts, 1000);
        } else {
            showNotification('❌ Mining failed: ' + (data.error || 'Unknown error'), 'error');
        }

    } catch (error) {
        console.error('Mining error:', error);
        showNotification('💥 Network error: ' + error.message, 'error');
    }
}

/**
 * Refresh wallet balances
 */
async function refreshEnhancedBalances() {
    console.log('💰 Refreshing balances...');

    try {
        const response = await fetch('/api/balances/detailed');
        const data = await response.json();

        const box = document.getElementById('balances-output');
        if (box) {
            box.textContent = formatBalancesResponse(data);
        }

    } catch (error) {
        console.error('Balance refresh error:', error);
        showNotification('💥 Failed to refresh balances', 'error');
    }
}

/**
 * Refresh blockchain data
 */
async function refreshChain() {
    console.log('⛓️ Refreshing chain...');

    try {
        const response = await fetch('/api/chain');
        const data = await response.json();

        const box = document.getElementById('chain-output');
        if (box) {
            box.textContent = formatChainResponse(data);
        }

    } catch (error) {
        console.error('Chain refresh error:', error);
        showNotification('💥 Failed to refresh chain', 'error');
    }
}

// ================================
// ATTACK SIMULATION - UPDATED WITH USER-FRIENDLY OUTPUTS
// ================================

/**
 * Update success probability
 */
function updateSuccessProbability(value) {
    attackConfig.successProbability = parseFloat(value) / 100;
    document.getElementById('probability-value').textContent = value + '%';
    updateControlStatus();
    // Update attack analysis chart when probability changes
    if (networkCharts.attackAnalysisChart) {
        setTimeout(updateChartsWithRealData, 100);
    }
}

/**
 * Update hash power
 */
function updateHashPower(value) {
    attackConfig.attackerHashPower = parseFloat(value);
    document.getElementById('hashpower-value').textContent = value + '%';
    updateControlStatus();
    // Update attack analysis chart when hash power changes
    if (networkCharts.attackAnalysisChart) {
        setTimeout(updateChartsWithRealData, 100);
    }
}

/**
 * Force attack success
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
 * Force attack failure
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
 * Reset to random mode
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
 * Update control status display
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
// NETWORK OPERATIONS - UPDATED WITH USER-FRIENDLY OUTPUTS
// ================================

/**
 * Add a peer to the network
 */
async function addPeer() {
    const peerAddress = document.getElementById('peer-address').value.trim();

    if (!peerAddress) {
        showNotification('❌ Please enter a valid peer address', 'error');
        return;
    }

    try {
        const response = await fetch('/peers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                address: peerAddress
            })
        });

        const data = await response.json();

        const box = document.getElementById('peer-response');
        if (box) {
            box.style.display = 'block';
            box.textContent = formatPeerResponse(data);
        }

        if (response.ok) {
            showNotification('✅ Peer added successfully!', 'success');
            document.getElementById('peer-address').value = '';
            // Refresh charts to show network changes
            setTimeout(refreshAllCharts, 500);
        } else {
            showNotification('❌ Failed to add peer: ' + (data.error || 'Unknown error'), 'error');
        }

    } catch (error) {
        console.error('Add peer error:', error);
        showNotification('💥 Network error: ' + error.message, 'error');
    }
}

/**
 * Resolve network conflicts
 */
async function resolveConflicts() {
    try {
        const response = await fetch('/consensus');
        const data = await response.json();

        const box = document.getElementById('consensus-response');
        if (box) {
            box.style.display = 'block';
            box.textContent = formatConsensusResponse(data);
        }

        showNotification('🔗 Consensus check completed', 'info');
        refreshChain();
        // Refresh charts after consensus check
        setTimeout(refreshAllCharts, 500);

    } catch (error) {
        console.error('Consensus error:', error);
        showNotification('💥 Network error: ' + error.message, 'error');
    }
}

// ================================
// SIMBLOCK FUNCTIONS - UPDATED WITH USER-FRIENDLY OUTPUTS
// ================================

/**
 * Start SimBlock simulation
 */
async function startSimBlockSimulation() {
    try {
        showNotification('🚀 Starting SimBlock simulation...', 'info');

        const response = await fetch('/api/simblock/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showNotification('✅ SimBlock simulation completed!', 'success');
            // Refresh charts after simulation
            setTimeout(refreshAllCharts, 1000);
        } else {
            showNotification('❌ SimBlock simulation failed', 'error');
        }

    } catch (error) {
        showNotification('💥 SimBlock simulation failed: ' + error.message, 'error');
    }
}

// ================================
// CSV REPORT FUNCTIONS
// ================================

/**
 * Download all CSV reports
 */
async function downloadCSVReports() {
    const spinner = document.getElementById('csv-spinner');

    try {
        if (spinner) spinner.style.display = 'inline';
        showNotification('📊 Generating CSV reports...', 'info');

        const response = await fetch('/api/report/csv');
        if (!response.ok) throw new Error('CSV generation failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'Blockchain-Analysis-Reports.zip';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        showNotification('✅ CSV reports downloaded successfully!', 'success');
    } catch (error) {
        showNotification('💥 CSV generation failed: ' + error.message, 'error');
    } finally {
        if (spinner) spinner.style.display = 'none';
    }
}

/**
 * Download specific CSV report
 */
async function downloadSpecificCSV(reportType) {
    try {
        showNotification(`📄 Generating ${reportType} report...`, 'info');

        const response = await fetch(`/api/report/csv/${reportType}`);
        if (!response.ok) throw new Error(`${reportType} report generation failed`);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');

        const filenames = {
            'blockchain': 'blockchain_analysis',
            'attack': 'attack_analysis',
            'network': 'network_metrics',
            'double-spend': 'double_spend_analysis'
        };

        link.download = `${filenames[reportType] || reportType}_${new Date().toISOString().split('T')[0]}.csv`;
        link.href = url;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        showNotification(`✅ ${reportType} report downloaded!`, 'success');
    } catch (error) {
        showNotification(`💥 ${reportType} report failed: ` + error.message, 'error');
    }
}

// ================================
// INITIALIZATION
// ================================

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('🚀 Initializing blockchain application...');

    // Initialize attack controls
    updateControlStatus();

    // Initialize attack visualization
    resetAttackVisualization();

    // Initialize charts immediately
    setTimeout(initializeNetworkCharts, 500);

    // Load initial data
    setTimeout(() => {
        refreshEnhancedBalances();
        refreshChain();
        showNotification('✅ Blockchain UI Ready! All systems operational.', 'success');
    }, 1000);

    console.log('✅ app.js fully loaded and ready!');
}

// Start the application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM fully loaded!');
    initializeApp();
});

// Global export for HTML onclick handlers
window.submitTransaction = submitTransaction;
window.mineBlock = mineBlock;
window.refreshEnhancedBalances = refreshEnhancedBalances;
window.refreshChain = refreshChain;
window.runAttack = runAttackWithVisualization;
window.addPeer = addPeer;
window.resolveConflicts = resolveConflicts;
window.downloadCSVReports = downloadCSVReports;
window.downloadSpecificCSV = downloadSpecificCSV;
window.updateSuccessProbability = updateSuccessProbability;
window.updateHashPower = updateHashPower;
window.forceAttackSuccess = forceAttackSuccess;
window.forceAttackFailure = forceAttackFailure;
window.resetAttackControl = resetAttackControl;
window.startSimBlockSimulation = startSimBlockSimulation;
window.initializeNetworkCharts = initializeNetworkCharts;
window.refreshAllCharts = refreshAllCharts;
window.exportCharts = exportCharts;
window.resetAttackVisualization = resetAttackVisualization;

console.log('🔧 app.js loaded - all functions are now available globally');