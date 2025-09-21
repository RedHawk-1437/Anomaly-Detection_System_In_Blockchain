// app.js - User-friendly frontend logic for blockchain + simulations

let chainChart = null;
let simblockChart = null;

// ----------------------------
// Helper Functions
// ----------------------------
function formatJSON(data) {
    return JSON.stringify(data, null, 2);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px;
        background: ${type === 'error' ? '#ff4757' : type === 'success' ? '#2ed573' : '#1e90ff'};
        color: white;
        border-radius: 5px;
        z-index: 1000;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 400px;
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 5000);
}

function createUserFriendlyOutput(data, title) {
    return `
        <div class="user-friendly-output">
            <h4>${title}</h4>
            <div class="output-content">${data}</div>
        </div>
    `;
}

// ----------------------------
// Blockchain Playground
// ----------------------------

// Submit transaction
document.getElementById("tx-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const sender = document.getElementById("tx-sender").value;
    const receiver = document.getElementById("tx-receiver").value;
    const amount = parseFloat(document.getElementById("tx-amount").value);

    if (!sender || !receiver || !amount) {
        showNotification('Please fill all transaction fields', 'error');
        return;
    }

    try {
        const res = await fetch("/api/tx/new", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sender, receiver, amount })
        });
        const data = await res.json();

        const box = document.getElementById("tx-response");
        box.style.display = "block";

        if (data.status === "ok") {
            box.innerHTML = createUserFriendlyOutput(`
                <p>✅ <strong>Transaction Successful!</strong></p>
                <p>Transaction ID: <code>${data.txid}</code></p>
                <p>From: <strong>${sender}</strong></p>
                <p>To: <strong>${receiver}</strong></p>
                <p>Amount: <strong>${amount} coins</strong></p>
                <p>Pending transactions: ${data.mempool_size}</p>
            `, "Transaction Details");
            showNotification('Transaction added successfully!', 'success');
        } else {
            box.innerHTML = createUserFriendlyOutput(`
                <p>❌ <strong>Transaction Failed</strong></p>
                <p>Error: ${data.error || 'Unknown error'}</p>
            `, "Transaction Error");
            showNotification('Transaction failed', 'error');
        }
    } catch (err) {
        showNotification('Transaction failed: ' + err.message, 'error');
    }
});

// Mine block
document.getElementById("mine-btn").addEventListener("click", async () => {
    const miner = document.getElementById("miner-name").value || "DefaultMiner";

    try {
        const res = await fetch("/api/mine", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ miner })
        });
        const data = await res.json();
        const box = document.getElementById("mine-response");
        box.style.display = "block";

        if (data.status === "ok") {
            box.innerHTML = createUserFriendlyOutput(`
                <p>✅ <strong>Block Mined Successfully!</strong></p>
                <p>Miner: <strong>${miner}</strong></p>
                <p>Block Index: <strong>${data.block.index}</strong></p>
                <p>Block Hash: <code>${data.block.hash.substring(0, 20)}...</code></p>
                <p>Transactions in block: <strong>${data.block.transactions.length}</strong></p>
                <p>Total chain length: <strong>${data.chain_length} blocks</strong></p>
                <p>Nonce: <strong>${data.block.nonce}</strong></p>
            `, "Mining Results");
            showNotification('Block mined successfully!', 'success');
        } else {
            box.innerHTML = createUserFriendlyOutput(`
                <p>❌ <strong>Mining Failed</strong></p>
                <p>Error: ${data.error || 'Unknown error'}</p>
            `, "Mining Error");
            showNotification('Mining failed', 'error');
        }
    } catch (err) {
        showNotification('Mining failed: ' + err.message, 'error');
    }
});

// Refresh balances
document.getElementById("refresh-balances-btn").addEventListener("click", async () => {
    try {
        const res = await fetch("/api/balances");
        const data = await res.json();

        let balanceHTML = '<div class="balances-table"><h4>💰 Current Balances</h4><table>';
        balanceHTML += '<tr><th>User</th><th>Balance</th></tr>';

        for (const [user, balance] of Object.entries(data)) {
            const balanceClass = balance >= 0 ? 'positive' : 'negative';
            balanceHTML += `<tr><td>${user}</td><td class="${balanceClass}">${balance} coins</td></tr>`;
        }

        balanceHTML += '</table></div>';
        document.getElementById("balances-output").innerHTML = balanceHTML;
        showNotification('Balances refreshed successfully!', 'success');
    } catch (err) {
        document.getElementById("balances-output").innerHTML =
            createUserFriendlyOutput('<p>❌ Failed to load balances</p>', "Error");
        showNotification('Failed to fetch balances', 'error');
    }
});

// Refresh chain
document.getElementById("refresh-chain-btn").addEventListener("click", async () => {
    try {
        const res = await fetch("/api/chain");
        const data = await res.json();

        let chainHTML = '<div class="chain-view"><h4>⛓️ Blockchain Overview</h4>';
        chainHTML += `<p>Total blocks: <strong>${data.chain.length}</strong></p>`;
        chainHTML += `<p>Pending transactions: <strong>${data.mempool.length}</strong></p>`;
        chainHTML += `<p>Difficulty: <strong>${data.difficulty}</strong></p>`;

        chainHTML += '<div class="blocks-container">';
        data.chain.forEach(block => {
            chainHTML += `
                <div class="block-card">
                    <h5>Block #${block.index}</h5>
                    <p>Hash: <code>${block.hash.substring(0, 15)}...</code></p>
                    <p>Previous: <code>${block.previous_hash.substring(0, 15)}...</code></p>
                    <p>Transactions: ${block.transactions.length}</p>
                    <p>Nonce: ${block.nonce}</p>
                    <button onclick="viewBlockDetails(${block.index})">View Details</button>
                </div>
            `;
        });
        chainHTML += '</div></div>';

        document.getElementById("chain-output").innerHTML = chainHTML;
        updateChainChart(data.chart_data);
        showNotification('Blockchain refreshed successfully!', 'success');
    } catch (err) {
        document.getElementById("chain-output").innerHTML =
            createUserFriendlyOutput('<p>❌ Failed to load blockchain</p>', "Error");
        showNotification('Failed to fetch blockchain', 'error');
    }
});

// View block details function
window.viewBlockDetails = function(blockIndex) {
    fetch("/api/chain")
        .then(res => res.json())
        .then(data => {
            const block = data.chain.find(b => b.index === blockIndex);
            if (block) {
                const modal = document.createElement('div');
                modal.className = 'modal';
                modal.innerHTML = `
                    <div class="modal-content">
                        <h3>Block #${block.index} Details</h3>
                        <pre>${formatJSON(block)}</pre>
                        <button onclick="this.parentElement.parentElement.remove()">Close</button>
                    </div>
                `;
                document.body.appendChild(modal);
            }
        });
};

// Run Attack UI
document.getElementById("run-attack-btn").addEventListener("click", async () => {
    const attacker = document.getElementById("attack-attacker").value || "Attacker";
    const blocks = parseInt(document.getElementById("attack-blocks").value || "1");
    const amount = parseFloat(document.getElementById("attack-amount").value || "5");
    const payload = { attacker, blocks, amount };

    const box = document.getElementById("attack-output");
    box.style.display = "block";
    box.innerHTML = createUserFriendlyOutput(`
        <p>⚡ <strong>Starting Double-Spending Attack Simulation...</strong></p>
        <p>Attacker: ${attacker}</p>
        <p>Private blocks to mine: ${blocks}</p>
        <p>Amount: ${amount} coins</p>
        <div class="loading">Processing... ⏳</div>
    `, "Attack Simulation");

    try {
        const res = await fetch("/api/attack/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        let attackHTML = `
            <p>🎯 <strong>Double-Spending Attack Results</strong></p>
            <div class="attack-steps">
        `;

        data.steps.forEach((step, index) => {
            attackHTML += `<div class="attack-step"><strong>Step ${index + 1}:</strong> `;

            switch(step.action) {
                case 'broadcast_honest_tx':
                    attackHTML += `Broadcast honest transaction to merchant`;
                    if (step.result) {
                        attackHTML += ` ✅ (TX ID: ${step.result.txid.substring(0, 8)}...)`;
                    }
                    break;
                case 'private_mined_blocks':
                    attackHTML += `Mined ${step.count} private blocks with conflicting transaction`;
                    break;
                case 'broadcast_private_blocks':
                    attackHTML += `Broadcast private chain to network`;
                    const success = step.results.some(r => r.ok);
                    attackHTML += success ? ' ✅' : ' ❌ (Rejected by network)';
                    break;
                case 'consensus_results':
                    attackHTML += `Network consensus check`;
                    break;
                default:
                    attackHTML += step.action;
            }

            attackHTML += `</div>`;
        });

        // Check if attack was successful
        const broadcastStep = data.steps.find(s => s.action === 'broadcast_private_blocks');
        const attackSuccessful = broadcastStep && broadcastStep.results.some(r => r.ok);

        attackHTML += `
            <div class="attack-result ${attackSuccessful ? 'success' : 'failure'}">
                <h4>${attackSuccessful ? '✅ ATTACK SUCCESSFUL!' : '❌ ATTACK FAILED'}</h4>
                <p>${attackSuccessful ?
                    'The double-spending attack was successful! The fraudulent transaction was accepted.' :
                    'The attack was detected and prevented by the network. The honest chain was maintained.'
                }</p>
            </div>
        `;

        box.innerHTML = createUserFriendlyOutput(attackHTML, "Attack Simulation Complete");
        showNotification(`Attack ${attackSuccessful ? 'successful' : 'failed'}`,
                        attackSuccessful ? 'success' : 'error');

    } catch (err) {
        box.innerHTML = createUserFriendlyOutput(`
            <p>❌ <strong>Attack Simulation Failed</strong></p>
            <p>Error: ${err.message}</p>
        `, "Attack Error");
        showNotification('Attack request failed', 'error');
    }
});

function updateChainChart(chartData) {
    const ctx = document.getElementById('chainChart').getContext('2d');
    document.getElementById('chain-chart-container').style.display = 'block';
    if (chainChart) {
        chainChart.destroy();
    }
    chainChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '# of Transactions',
                data: chartData.tx_counts,
                backgroundColor: 'rgba(42, 82, 152, 0.6)',
                borderColor: 'rgba(42, 82, 152, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

// ----------------------------
// P2P Network
// ----------------------------

// Add Peer
document.getElementById("add-peer-btn").addEventListener("click", async () => {
    const peerAddress = document.getElementById("peer-address").value;
    if (!peerAddress) {
        showNotification('Please enter a valid peer address', 'error');
        return;
    }

    try {
        const res = await fetch("/peers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ address: peerAddress })
        });
        const data = await res.json();
        const box = document.getElementById("peer-response");
        box.style.display = "block";

        if (data.message) {
            box.innerHTML = createUserFriendlyOutput(`
                <p>✅ <strong>Peer Added Successfully!</strong></p>
                <p>${data.message}</p>
                <p>Total peers: ${data.peers.length}</p>
                <ul>${data.peers.map(peer => `<li>${peer}</li>`).join('')}</ul>
            `, "Network Update");
            showNotification('Peer added successfully!', 'success');
        } else {
            box.innerHTML = createUserFriendlyOutput(`
                <p>❌ <strong>Failed to Add Peer</strong></p>
                <p>Error: ${data.error || 'Unknown error'}</p>
            `, "Network Error");
            showNotification('Failed to add peer', 'error');
        }
    } catch (err) {
        showNotification('Failed to add peer: ' + err.message, 'error');
    }
});

// Run Consensus
document.getElementById("resolve-conflicts-btn").addEventListener("click", async () => {
    const box = document.getElementById("consensus-response");
    box.style.display = "block";
    box.innerHTML = createUserFriendlyOutput(`
        <p>🔍 <strong>Checking Network Consensus...</strong></p>
        <div class="loading">Querying all peers... ⏳</div>
    `, "Consensus Check");

    try {
        const res = await fetch("/consensus");
        const data = await res.json();

        if (data.message.includes('replaced')) {
            box.innerHTML = createUserFriendlyOutput(`
                <p>🔄 <strong>Chain Replaced!</strong></p>
                <p>Our chain was replaced by a longer chain from the network.</p>
                <p>New chain length: ${data.new_chain.length} blocks</p>
                <p><em>The network consensus mechanism worked correctly!</em></p>
            `, "Consensus Results");
            showNotification('Chain replaced with longer chain', 'success');
        } else {
            box.innerHTML = createUserFriendlyOutput(`
                <p>✅ <strong>Chain is Authoritative</strong></p>
                <p>Our chain is the longest and most valid chain in the network.</p>
                <p>Current chain length: ${data.chain.length} blocks</p>
                <p><em>No consensus change needed.</em></p>
            `, "Consensus Results");
            showNotification('Our chain is authoritative', 'success');
        }
    } catch (err) {
        box.innerHTML = createUserFriendlyOutput(`
            <p>❌ <strong>Consensus Check Failed</strong></p>
            <p>Error: ${err.message}</p>
        `, "Consensus Error");
        showNotification('Failed to run consensus', 'error');
    }
});

// ----------------------------
// SimBlock Simulation
// ----------------------------
document.getElementById("run-analysis-btn").addEventListener("click", async () => {
    const spinner = document.getElementById("loading-spinner");
    const summaryBox = document.getElementById("simulation-summary");
    spinner.style.display = "inline";
    summaryBox.style.display = "none";

    try {
        const res = await fetch("/api/analyze");
        if (!res.ok) {
            const err = await res.json().catch(() => ({error: "unknown"}));
            throw new Error(err.error || "Simulation failed");
        }
        const data = await res.json();
        spinner.style.display = "none";
        summaryBox.style.display = "block";

        const tableBody = document.getElementById("summary-table").getElementsByTagName("tbody")[0];
        tableBody.innerHTML = "";

        // Add user-friendly analysis
        let analysisHTML = `
            <div class="simblock-analysis">
                <h3>📊 SimBlock Simulation Results</h3>
                <div class="result-card ${data.attack_successful ? 'attack-success' : 'attack-fail'}">
                    <h4>${data.attack_successful ? '✅ ATTACK SUCCESSFUL' : '❌ ATTACK FAILED'}</h4>
                    <p>${data.attack_conclusion || (data.attack_successful ?
                        'The double-spending attack was successful in the simulation.' :
                        'The attack was prevented in the simulation.')}
                    </p>
                </div>
        `;

        // Create summary table
        const metrics = {
            'Attack Probability': `${(data.attack_probability * 100).toFixed(1)}%`,
            'Total Blocks': data.total_blocks,
            'Average Block Time': data.avg_block_time ? `${data.avg_block_time.toFixed(2)} ms` : 'N/A',
            'Forks Detected': data.forks_detected,
            'Total Miners': data.total_miners
        };

        for (const [key, value] of Object.entries(metrics)) {
            const row = tableBody.insertRow();
            row.innerHTML = `<td><strong>${key}</strong></td><td>${value}</td>`;
        }

        if (data.detailed_analysis) {
            analysisHTML += `
                <div class="detailed-analysis">
                    <h4>Detailed Analysis:</h4>
                    <p>Attacker blocks: ${data.detailed_analysis.attacker_blocks_added_count || 0}</p>
                    <p>Honest blocks: ${data.detailed_analysis.honest_blocks_added_count || 0}</p>
                </div>
            `;

            // Chart container ko visible karein
            const chartContainer = document.getElementById('simblock-chart-container');
            if (chartContainer) {
                chartContainer.style.display = 'block';

                // Chart ko update karne se pehle thoda wait karein
                setTimeout(() => {
                    updateSimblockChart(data.detailed_analysis);
                }, 100);
            }
        }

        analysisHTML += `</div>`;
        summaryBox.innerHTML = analysisHTML + summaryBox.innerHTML;
        showNotification('Simulation completed successfully!', 'success');

    } catch (err) {
        spinner.style.display = "none";
        showNotification('Simulation failed: ' + err.message, 'error');
    }
});

function updateSimblockChart(detailedData) {
    const canvas = document.getElementById('simblockChart');
    if (!canvas) {
        console.error('Chart canvas not found');
        return;
    }

    // Purana chart destroy karein agar exists karta hai
    if (simblockChart) {
        simblockChart.destroy();
    }

    const attacker = detailedData.attacker_blocks_added_count || 0;
    const honest = detailedData.honest_blocks_added_count || 0;

    // Agar dono zero hain to chart show na karein
    if (attacker === 0 && honest === 0) {
        console.warn('No data available for chart');
        return;
    }

    try {
        simblockChart = new Chart(canvas, {
            type: 'pie',
            data: {
                labels: ["Attacker Blocks", "Honest Blocks"],
                datasets: [{
                    data: [attacker, honest],
                    backgroundColor: ["#e74c3c", "#2ecc71"],
                    borderColor: "#fff",
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                layout: {
                    padding: {
                        left: 10,
                        right: 10,
                        top: 10,
                        bottom: 10
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                size: 12 // Legend text size chota karein
                            },
                            padding: 15 // Legend spacing kam karein
                        }
                    },
                    title: {
                        display: true,
                        text: 'Block Distribution',
                        font: {
                            size: 14 // Title size chota karein
                        },
                        padding: {
                            top: 5,
                            bottom: 10
                        }
                    }
                }
            }
        });

        // Canvas size directly control karein
        canvas.style.width = '100px';
        canvas.style.height = '50px';

    } catch (error) {
        console.error('Error creating chart:', error);
        // Fallback: Text representation show karein
        canvas.parentElement.innerHTML += `
            <div class="chart-fallback">
                <h4>Block Distribution:</h4>
                <p>Attacker Blocks: ${attacker} (${((attacker/(attacker+honest))*100).toFixed(1)}%)</p>
                <p>Honest Blocks: ${honest} (${((honest/(attacker+honest))*100).toFixed(1)}%)</p>
            </div>
        `;
    }
}

// ----------------------------
// Download PDF
// ----------------------------
document.getElementById("download-report-btn").addEventListener("click", async () => {
    const spinner = document.getElementById("pdf-spinner");
    spinner.style.display = "inline";

    try {
        const res = await fetch("/api/report/pdf");
        if (!res.ok) {
            const err = await res.json().catch(() => ({error: "unknown"}));
            throw new Error(err.error || "PDF generation failed");
        }
        const blob = await res.blob();
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = "Double-Spending-Report.pdf";
        document.body.appendChild(link);
        link.click();
        link.remove();
        showNotification('PDF report downloaded successfully!', 'success');
    } catch (err) {
        showNotification('PDF generation failed: ' + err.message, 'error');
    } finally {
        spinner.style.display = "none";
    }
});

// Add CSS for the new styles
const style = document.createElement('style');
style.textContent = `
    /* Style for a user-friendly output box */
    .user-friendly-output {
        background: #f8f9fa; /* Light grey background */
        border: 1px solid #e9ecef; /* Light grey border */
        border-radius: 8px; /* Rounded corners */
        padding: 15px; /* Spacing inside the box */
        margin: 10px 0; /* Vertical margin outside the box */
    }

    /* Style for the heading inside the output box */
    .user-friendly-output h4 {
        color: #2a5298; /* A shade of blue for the text color */
        margin-bottom: 10px; /* Space below the heading */
        border-bottom: 2px solid #2a5298; /* A blue line below the heading */
        padding-bottom: 5px; /* Spacing between the heading and the line */
    }

    /* Style for the content area inside the output box */
    .output-content {
        line-height: 1.6; /* Increases line spacing for better readability */
    }

    /* Style for the container of the balances table */
    .balances-table {
        margin: 10px 0; /* Adds vertical spacing */
    }

    /* General table styling */
    .balances-table table {
        width: 100%; /* Makes the table fill the container width */
        border-collapse: collapse; /* Merges table borders into a single line */
    }

    /* Styles for table headers and data cells */
    .balances-table th, .balances-table td {
        padding: 8px; /* Spacing inside the cells */
        text-align: left; /* Aligns text to the left */
        border: 1px solid #ddd; /* A light grey border for each cell */
    }

    /* Style for positive balance values */
    .balances-table .positive {
        color: #2ed573; /* Green text color */
        font-weight: bold; /* Makes the text bold */
    }

    /* Style for negative balance values */
    .balances-table .negative {
        color: #ff4757; /* Red text color */
        font-weight: bold; /* Makes the text bold */
    }

    /* Style for the blockchain overview section */
    .chain-view {
        margin: 10px 0; /* Vertical spacing */
    }

    /* Style for the container that holds all the block cards */
    .blocks-container {
        display: flex; /* Uses Flexbox for layout */
        flex-wrap: wrap; /* Allows cards to wrap to the next line */
        gap: 10px; /* Creates space between the block cards */
        margin: 10px 0; /* Vertical spacing */
    }

    /* Style for each individual block card */
    .block-card {
        background: white; /* White background */
        border: 1px solid #ddd; /* Light grey border */
        border-radius: 5px; /* Slightly rounded corners */
        padding: 10px; /* Spacing inside the card */
        width: 200px; /* Fixed width for each card */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); /* Subtle shadow for a "lifted" effect */
    }

    /* Style for the heading inside a block card */
    .block-card h5 {
        margin: 0 0 10px 0; /* Removes default margin and adds space at the bottom */
        color: #2a5298; /* Blue text color */
    }

    /* Style for the container of attack steps */
    .attack-steps {
        margin: 10px 0; /* Vertical spacing */
    }

    /* Style for each individual attack step list item */
    .attack-step {
        padding: 5px; /* Spacing inside the step item */
        border-left: 3px solid #2a5298; /* A blue line on the left side */
        margin: 5px 0; /* Vertical spacing between steps */
        background: #f8f9fa; /* Light grey background */
    }

    /* Style for the container that holds the final attack result */
    .attack-result {
        padding: 15px; /* Spacing inside the result box */
        border-radius: 5px; /* Rounded corners */
        margin: 10px 0; /* Vertical spacing */
    }

    /* Specific style for a successful attack result */
    .attack-result.success {
        background: #d4edda; /* Light green background */
        border: 1px solid #c3e6cb; /* Light green border */
        color: #155724; /* Dark green text color */
    }

    /* Specific style for a failed attack result */
    .attack-result.failure {
        background: #f8d7da; /* Light red background */
        border: 1px solid #f5c6cb; /* Light red border */
        color: #721c24; /* Dark red text color */
    }

    /* Style for a loading message */
    .loading {
        text-align: center; /* Centers the text horizontally */
        padding: 20px; /* Spacing around the text */
        color: #6c757d; /* Grey text color */
    }

    /* Style for the notification pop-up */
    .notification {
        position: fixed; /* Positions the element relative to the browser window */
        top: 20px; /* 20px from the top of the window */
        right: 20px; /* 20px from the right of the window */
        padding: 15px; /* Spacing inside the notification */
        border-radius: 5px; /* Rounded corners */
        z-index: 1000; /* Ensures the notification is on top of other elements */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Adds a shadow */
        display: flex; /* Uses Flexbox for internal layout */
        justify-content: space-between; /* Pushes child elements to the ends of the container */
        align-items: center; /* Centers child elements vertically */
        max-width: 400px; /* Limits the maximum width */
    }

    /* Style for the modal (pop-up window) background overlay */
    .modal {
        position: fixed; /* Fixed position */
        top: 0; /* Aligns to the top edge */
        left: 0; /* Aligns to the left edge */
        width: 100%; /* Full width */
        height: 100%; /* Full height */
        background: rgba(0,0,0,0.5); /* Semi-transparent black background */
        display: flex; /* Uses Flexbox */
        justify-content: center; /* Centers content horizontally */
        align-items: center; /* Centers content vertically */
        z-index: 1000; /* On top of everything */
    }

    /* Style for the content box inside the modal */
    .modal-content {
        background: white; /* White background */
        padding: 20px; /* Spacing inside the box */
        border-radius: 8px; /* Rounded corners */
        max-width: 80%; /* Limits the maximum width */
        max-height: 80%; /* Limits the maximum height */
        overflow: auto; /* Adds a scrollbar if the content overflows */
    }

    /* Style for the SimBlock analysis section */
    .simblock-analysis {
        margin-bottom: 20px; /* Adds space below the section */
    }

    /* General style for result cards in the SimBlock section */
    .result-card {
        padding: 15px; /* Spacing inside the card */
        border-radius: 5px; /* Rounded corners */
        margin: 10px 0; /* Vertical spacing */
    }

    /* Specific style for a successful attack result card */
    .attack-success {
        background: #d4edda; /* Light green background */
        border: 1px solid #c3e6cb; /* Light green border */
    }

    /* Specific style for a failed attack result card */
    .attack-fail {
        background: #f8d7da; /* Light red background */
        border: 1px solid #f5c6cb; /* Light red border */
    }

    /* Style for the SimBlock chart container */
    #simblock-chart-container {
        max-width: 350px; /* Limits the maximum width of the chart */
        margin: 20px auto; /* Centers the chart horizontally with vertical spacing */
    }
`;
document.head.appendChild(style);