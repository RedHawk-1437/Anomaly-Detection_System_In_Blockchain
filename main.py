import os
import json
import time
import sys
import csv
from datetime import datetime
from typing import Dict, Any, Tuple

import requests
import matplotlib
import numpy as np
from flask import Flask, jsonify, render_template, send_file, request, send_from_directory

# Configure matplotlib for server environment
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Blockchain core components
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction

# SimBlock integration for network simulation
from blockchain.simblock_integration import (
    start_simulation,
    get_network_info,
    calculate_probability,
    run_attack as simblock_run_attack
)

# ================================
# FLASK APPLICATION CONFIGURATION
# ================================

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# ================================
# APPLICATION STATE MANAGEMENT
# ================================

# Primary blockchain instance
blockchain_instance = Blockchain(difficulty=3, reward=2.0)

# Network connectivity settings
PEERS = set()
NODE_ADDRESS = os.environ.get("NODE_ADDRESS", "http://127.0.0.1:5000")

# Attack simulation results storage
RECENT_ATTACK_RESULTS = {}

# Real-time chart data containers
NETWORK_ACTIVITY_DATA = {
    'labels': [],
    'data': []
}

# Network performance metrics
SIMBLOCK_METRICS_DATA = {
    'network_latency': 0,
    'node_health': 0,
    'message_delivery': 0,
    'attack_resistance': 0
}


# ================================
# CHART DATA MANAGEMENT FUNCTIONS
# ================================

def update_network_chart_data(attack_successful, hash_power, probability):
    """
    Update network metrics based on attack simulation results.

    Modifies network activity data and SimBlock metrics based on the
    outcome of attack simulations, creating realistic network behavior
    patterns for visualization.

    Args:
        attack_successful: Boolean indicating whether the attack succeeded
        hash_power: Attacker's computational power percentage
        probability: Calculated attack success probability
    """
    try:
        attack_count = len(NETWORK_ACTIVITY_DATA['labels']) + 1
        NETWORK_ACTIVITY_DATA['labels'].append(f"Attack {attack_count}")

        base_activity = hash_power * 2
        if attack_successful:
            activity_level = min(100, base_activity + 30)
        else:
            activity_level = max(10, base_activity - 10)

        activity_level += np.random.randint(-5, 15)
        activity_level = max(5, min(100, activity_level))

        NETWORK_ACTIVITY_DATA['data'].append(activity_level)

        if len(NETWORK_ACTIVITY_DATA['labels']) > 10:
            NETWORK_ACTIVITY_DATA['labels'] = NETWORK_ACTIVITY_DATA['labels'][-10:]
            NETWORK_ACTIVITY_DATA['data'] = NETWORK_ACTIVITY_DATA['data'][-10:]

        SIMBLOCK_METRICS_DATA['network_latency'] = min(100, max(10, hash_power + np.random.randint(5, 25)))

        if attack_successful:
            SIMBLOCK_METRICS_DATA['node_health'] = max(10, SIMBLOCK_METRICS_DATA.get('node_health', 100) - 15)
        else:
            SIMBLOCK_METRICS_DATA['node_health'] = min(100, SIMBLOCK_METRICS_DATA.get('node_health', 50) + 10)

        SIMBLOCK_METRICS_DATA['message_delivery'] = 100 - (hash_power / 2) + np.random.randint(-10, 10)
        SIMBLOCK_METRICS_DATA['message_delivery'] = max(10, min(100, SIMBLOCK_METRICS_DATA['message_delivery']))

        if attack_successful:
            SIMBLOCK_METRICS_DATA['attack_resistance'] = max(10,
                                                             SIMBLOCK_METRICS_DATA.get('attack_resistance', 100) - 20)
        else:
            SIMBLOCK_METRICS_DATA['attack_resistance'] = min(100,
                                                             SIMBLOCK_METRICS_DATA.get('attack_resistance', 50) + 15)

        print(f"📊 Updated network charts - Activity: {activity_level}, Metrics: {SIMBLOCK_METRICS_DATA}")

    except Exception as e:
        print(f"❌ Error updating network chart data: {e}")


def reset_chart_data():
    """Reset all chart data to initial state."""
    global NETWORK_ACTIVITY_DATA, SIMBLOCK_METRICS_DATA
    NETWORK_ACTIVITY_DATA = {'labels': [], 'data': []}
    SIMBLOCK_METRICS_DATA = {
        'network_latency': 0,
        'node_health': 0,
        'message_delivery': 0,
        'attack_resistance': 0
    }
    print("🔄 Chart data reset to initial state")


# ================================
# BALANCE CALCULATION ENGINE
# ================================

def get_balances_with_attackers() -> Tuple[Dict[str, float], Dict[str, Any]]:
    balances = {}
    attack_victims = {}

    # Process all blockchain transactions
    for block in blockchain_instance.chain:
        for tx in block.transactions:
            sender = tx.sender
            receiver = tx.receiver
            amount = tx.amount

            # Initialize new wallets
            if sender not in balances:
                balances[sender] = 0
            if receiver not in balances:
                balances[receiver] = 0

            # Apply transaction amounts (skip deduction for SYSTEM rewards)
            if sender != "SYSTEM":
                balances[sender] -= amount
            balances[receiver] += amount

    # Integrate attack results into balances - ENHANCED SECTION
    if 'last_attack' in RECENT_ATTACK_RESULTS:
        attack_data = RECENT_ATTACK_RESULTS['last_attack']
        attacker = attack_data.get('attacker', 'RedHawk')
        amount = attack_data.get('amount', 0)
        attack_success = attack_data.get('result', {}).get('successful', False)
        transactions = attack_data.get('transactions', {})

        # Ensure attacker wallet exists
        if attacker not in balances:
            balances[attacker] = 0

        # Apply successful attack transfers
        if attack_success:
            # Add the malicious transaction amount to attacker
            if 'malicious' in transactions:
                balances[attacker] += amount

            # Deduct from victim for the legitimate transaction
            victim = transactions.get('legitimate', {}).get('receiver', 'Victim_Wallet')
            if victim in balances:
                balances[victim] -= amount

            attack_victims[attacker] = {
                'victim': victim,
                'amount': amount,
                'success': True,
                'timestamp': attack_data.get('timestamp', time.time()),
                'transactions': transactions  # Include transaction details
            }
        else:
            # Record failed attack attempt with transaction details
            attack_victims[attacker] = {
                'victim': 'None (Attack Failed)',
                'amount': amount,
                'success': False,
                'timestamp': attack_data.get('timestamp', time.time()),
                'transactions': transactions  # Include transaction details even for failed attacks
            }

    # Remove system account from display
    if "SYSTEM" in balances:
        del balances["SYSTEM"]

    return balances, attack_victims


# ================================
# ENHANCED CSV REPORT GENERATION SYSTEM
# ================================

def generate_blockchain_csv_report() -> str:
    """
    Generate comprehensive blockchain data CSV report with enhanced formatting.
    """
    try:
        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(reports_dir, f"blockchain_analysis_{timestamp}.csv")

        chain_data = blockchain_instance.to_dict()
        balances, attack_victims = get_balances_with_attackers()
        network_info = get_network_info()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # ===== ENHANCED HEADER SECTION =====
            writer.writerow(['BLOCKCHAIN ANOMALY DETECTION SYSTEM - COMPREHENSIVE ANALYSIS REPORT'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['System', 'Double Spending Attack Simulation & Detection'])
            writer.writerow(['Version', '1.0 - Educational Prototype'])
            writer.writerow([])
            writer.writerow([])

            # ===== EXECUTIVE SUMMARY =====
            writer.writerow(['EXECUTIVE SUMMARY'])
            writer.writerow(['Metric', 'Value', 'Status'])
            writer.writerow(['Total Blocks', len(chain_data.get("chain", [])), 'Active'])
            writer.writerow(
                ['Total Transactions', sum(len(b["transactions"]) for b in chain_data.get("chain", [])), 'Processed'])
            writer.writerow(['Pending Transactions', len(chain_data.get("mempool", [])), 'Queued'])
            writer.writerow(['Active Wallets', len(balances), 'Monitored'])
            writer.writerow(['Network Nodes', network_info.get('nodes', 120), 'Simulated'])
            writer.writerow(['Attack Simulations', len(attack_victims), 'Performed'])
            writer.writerow(
                ['Successful Attacks', sum(1 for info in attack_victims.values() if info['success']), 'Detected'])
            writer.writerow([])
            writer.writerow([])

            # ===== BLOCKCHAIN OVERVIEW =====
            writer.writerow(['BLOCKCHAIN TECHNICAL OVERVIEW'])
            writer.writerow(['Parameter', 'Specification', 'Details'])
            writer.writerow(['Consensus Algorithm', 'Proof of Work (PoW)', 'SHA-256 Hashing'])
            writer.writerow(['Mining Difficulty', chain_data.get("difficulty", "N/A"), 'Adjustable'])
            writer.writerow(['Block Time', 'Variable', 'Based on network conditions'])
            writer.writerow(['Mining Reward', f"{chain_data.get('miner_reward', 'N/A')} coins", 'Per block'])
            writer.writerow(['Network Protocol', 'REST API + SimBlock', 'Hybrid implementation'])
            writer.writerow(['Connected Peers', len(PEERS), 'Active connections'])
            writer.writerow([])

            # ===== BLOCK DETAILS - ENHANCED =====
            writer.writerow(['BLOCKCHAIN DATA - DETAILED ANALYSIS'])
            writer.writerow(
                ['Block Index', 'Timestamp', 'Transaction Count', 'Block Hash (Short)', 'Previous Hash (Short)',
                 'Status'])

            for block in chain_data.get("chain", []):
                block_index = block.get('index', '')
                timestamp = datetime.fromtimestamp(block.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')
                tx_count = len(block.get('transactions', []))
                block_hash = block.get('hash', '')[:16] + '...' if block.get('hash') else 'N/A'
                prev_hash = block.get('previous_hash', '')[:16] + '...' if block.get('previous_hash') else 'GENESIS'

                # Determine block status
                if block_index == 0:
                    status = 'GENESIS BLOCK'
                elif any('RedHawk' in str(tx.get('sender', '')) for tx in block.get('transactions', [])):
                    status = 'ATTACK RELATED'
                else:
                    status = 'NORMAL'

                writer.writerow([block_index, timestamp, tx_count, block_hash, prev_hash, status])
            writer.writerow([])

            # ===== TRANSACTION ANALYSIS - ENHANCED =====
            writer.writerow(['TRANSACTION ANALYSIS - COMPREHENSIVE'])
            writer.writerow(['Block', 'Transaction ID', 'Sender', 'Receiver', 'Amount', 'Type', 'Timestamp'])

            total_transactions = 0
            user_transactions = 0
            system_transactions = 0

            for block in chain_data.get("chain", []):
                for tx in block.get("transactions", []):
                    total_transactions += 1
                    sender = tx.get('sender', '')
                    receiver = tx.get('receiver', '')
                    amount = tx.get('amount', 0)

                    if sender == 'SYSTEM':
                        tx_type = 'MINING REWARD'
                        system_transactions += 1
                    else:
                        tx_type = 'USER TRANSACTION'
                        user_transactions += 1

                    tx_timestamp = datetime.fromtimestamp(tx.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')

                    writer.writerow([
                        block.get('index', ''),
                        tx.get('id', '')[:20] + '...',
                        sender,
                        receiver,
                        f"{amount:.2f}",
                        tx_type,
                        tx_timestamp
                    ])

            writer.writerow([])
            writer.writerow(['TRANSACTION SUMMARY', '', '', '', '', '', ''])
            writer.writerow(['Total Transactions', total_transactions, '', '', '', '', ''])
            writer.writerow(['User Transactions', user_transactions, '', '', '', '', ''])
            writer.writerow(['System Transactions', system_transactions, '', '', '', '', ''])
            writer.writerow([])

            # ===== WALLET BALANCES - ENHANCED =====
            writer.writerow(['WALLET PORTFOLIO ANALYSIS'])
            writer.writerow(['Wallet Address', 'Balance (coins)', 'Status', 'Transaction Count'])

            # Calculate transaction counts per wallet
            wallet_tx_counts = {}
            for block in chain_data.get("chain", []):
                for tx in block.get("transactions", []):
                    sender = tx.get('sender', '')
                    receiver = tx.get('receiver', '')

                    if sender != 'SYSTEM':
                        wallet_tx_counts[sender] = wallet_tx_counts.get(sender, 0) + 1
                    wallet_tx_counts[receiver] = wallet_tx_counts.get(receiver, 0) + 1

            # Sort wallets by balance (highest first)
            sorted_wallets = sorted(balances.items(), key=lambda x: x[1], reverse=True)

            for wallet, balance in sorted_wallets:
                tx_count = wallet_tx_counts.get(wallet, 0)
                if balance > 0:
                    status = 'ACTIVE - POSITIVE'
                elif balance == 0:
                    status = 'INACTIVE'
                else:
                    status = 'ACTIVE - NEGATIVE'

                writer.writerow([wallet, f"{balance:.2f}", status, tx_count])

            writer.writerow([])

            # ===== SECURITY ANALYSIS =====
            writer.writerow(['SECURITY & ATTACK ANALYSIS'])
            writer.writerow(['Metric', 'Value', 'Risk Level', 'Recommendation'])

            total_attacks = len(attack_victims)
            successful_attacks = sum(1 for info in attack_victims.values() if info['success'])
            success_rate = (successful_attacks / total_attacks * 100) if total_attacks > 0 else 0

            # Risk assessment
            if success_rate == 0:
                risk_level = 'LOW'
                recommendation = 'Network security is strong'
            elif success_rate < 30:
                risk_level = 'MEDIUM'
                recommendation = 'Monitor network activity closely'
            else:
                risk_level = 'HIGH'
                recommendation = 'Implement additional security measures'

            writer.writerow(['Total Attack Simulations', total_attacks, risk_level, recommendation])
            writer.writerow(['Successful Attacks', successful_attacks, risk_level, ''])
            writer.writerow(['Attack Success Rate', f"{success_rate:.1f}%", risk_level, ''])
            writer.writerow(['Double Spending Risk', risk_level, risk_level, recommendation])
            writer.writerow([])

            # ===== NETWORK PERFORMANCE =====
            writer.writerow(['NETWORK PERFORMANCE METRICS'])
            writer.writerow(['Metric', 'Current Value', 'Target Range', 'Status'])
            writer.writerow(['Network Latency', f"{SIMBLOCK_METRICS_DATA['network_latency']}%", '0-40%',
                             'GOOD' if SIMBLOCK_METRICS_DATA['network_latency'] < 40 else 'HIGH'])
            writer.writerow(['Node Health', f"{SIMBLOCK_METRICS_DATA['node_health']}%", '80-100%',
                             'GOOD' if SIMBLOCK_METRICS_DATA['node_health'] > 80 else 'LOW'])
            writer.writerow(['Message Delivery', f"{SIMBLOCK_METRICS_DATA['message_delivery']}%", '90-100%',
                             'GOOD' if SIMBLOCK_METRICS_DATA['message_delivery'] > 90 else 'LOW'])
            writer.writerow(['Attack Resistance', f"{SIMBLOCK_METRICS_DATA['attack_resistance']}%", '80-100%',
                             'GOOD' if SIMBLOCK_METRICS_DATA['attack_resistance'] > 80 else 'LOW'])
            writer.writerow([])

            # ===== TECHNICAL SPECIFICATIONS =====
            writer.writerow(['TECHNICAL SPECIFICATIONS'])
            writer.writerow(['Component', 'Implementation', 'Version', 'Status'])
            writer.writerow(['Blockchain Core', 'Custom Python Implementation', '1.0', 'ACTIVE'])
            writer.writerow(['Consensus Mechanism', 'Proof of Work (PoW)', '1.0', 'ACTIVE'])
            writer.writerow(['Network Simulation', 'SimBlock Integration', '1.0', 'ACTIVE'])
            writer.writerow(['Web Interface', 'Flask + JavaScript', '1.0', 'ACTIVE'])
            writer.writerow(['Data Analytics', 'Real-time Charts & Metrics', '1.0', 'ACTIVE'])
            writer.writerow(['Attack Detection', 'Double Spending Algorithm', '1.0', 'ACTIVE'])
            writer.writerow([])

            # ===== FOOTER =====
            writer.writerow(['REPORT GENERATED BY: Blockchain Anomaly Detection System'])
            writer.writerow(['EDUCATIONAL PURPOSE: Virtual University of Pakistan'])
            writer.writerow(['TIMESTAMP:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['REPORT ID:', f"BLOCKCHAIN_REPORT_{timestamp}"])

        print(f"✅ Enhanced Blockchain CSV report generated: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Enhanced Blockchain CSV generation error: {e}")
        raise


def generate_attack_analysis_csv() -> str:
    """
    Generate detailed attack analysis CSV report with enhanced formatting.
    """
    try:
        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(reports_dir, f"attack_analysis_{timestamp}.csv")

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # ===== ENHANCED HEADER =====
            writer.writerow(['DOUBLE SPENDING ATTACK ANALYSIS - COMPREHENSIVE REPORT'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Report Type', 'Security Analysis & Attack Forensics'])
            writer.writerow([])
            writer.writerow([])

            if 'last_attack' in RECENT_ATTACK_RESULTS:
                attack_data = RECENT_ATTACK_RESULTS['last_attack']
                attack_result = attack_data.get('result', {})
                config = attack_data.get('config', {})
                transactions = attack_data.get('transactions', {})

                # ===== ATTACK EXECUTIVE SUMMARY =====
                writer.writerow(['ATTACK EXECUTIVE SUMMARY'])
                writer.writerow(['Metric', 'Value', 'Impact Level'])

                attack_successful = attack_result.get('successful', False)
                impact_level = 'HIGH' if attack_successful else 'LOW'

                writer.writerow(['Attack Status', 'SUCCESSFUL' if attack_successful else 'FAILED', impact_level])
                writer.writerow(['Attacker Identity', attack_data.get('attacker', 'Unknown'), impact_level])
                writer.writerow(['Attack Amount', f"{attack_data.get('amount', 0)} coins", impact_level])
                writer.writerow(['Private Blocks Mined', attack_data.get('blocks', 0), impact_level])
                writer.writerow(['Success Probability', f"{config.get('success_probability', 0)}%", impact_level])
                writer.writerow(['Hash Power Used', f"{config.get('hash_power', 0)}%", impact_level])
                writer.writerow([])

                # ===== ATTACK CONFIGURATION DETAILS =====
                writer.writerow(['ATTACK CONFIGURATION DETAILS'])
                writer.writerow(['Parameter', 'Setting', 'Description'])
                writer.writerow(
                    ['Attacker Name', attack_data.get('attacker', 'Unknown'), 'Primary attacker identifier'])
                writer.writerow(['Target Blocks', attack_data.get('blocks', 0), 'Private blocks to mine'])
                writer.writerow(['Attack Amount', f"{attack_data.get('amount', 0)} coins", 'Double spending amount'])
                writer.writerow(['Hash Power', f"{config.get('hash_power', 0)}%", 'Computational resources'])
                writer.writerow(
                    ['Success Probability', f"{config.get('success_probability', 0)}%", 'Base success chance'])
                writer.writerow(
                    ['Force Success', 'ENABLED' if config.get('force_success') else 'DISABLED', 'Override mode'])
                writer.writerow(
                    ['Force Failure', 'ENABLED' if config.get('force_failure') else 'DISABLED', 'Override mode'])
                writer.writerow(['Network Latency', f"{config.get('latency', 100)}ms", 'Simulated conditions'])
                writer.writerow([])

                # ===== TRANSACTION FORENSICS - ENHANCED =====
                writer.writerow(['TRANSACTION FORENSICS ANALYSIS'])
                writer.writerow(['Transaction Type', 'Sender', 'Receiver', 'Amount', 'Timestamp', 'Purpose', 'Status'])

                legitimate_tx = transactions.get('legitimate', {})
                malicious_tx = transactions.get('malicious', {})

                # Legitimate transaction
                writer.writerow([
                    'LEGITIMATE TRANSACTION',
                    transactions.get('transaction_1', {}).get('type', ''),
                    transactions.get('transaction_1', {}).get('purpose', ''),
                    legitimate_tx.get('sender', ''),
                    legitimate_tx.get('receiver', ''),
                    legitimate_tx.get('amount', 0),
                    datetime.fromtimestamp(legitimate_tx.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'VALID'
                ])

                # Malicious transaction
                writer.writerow([
                    'MALICIOUS TRANSACTION',
                    transactions.get('transaction_2', {}).get('type', ''),
                    transactions.get('transaction_2', {}).get('purpose', ''),
                    malicious_tx.get('sender', ''),
                    malicious_tx.get('receiver', ''),
                    malicious_tx.get('amount', 0),
                    datetime.fromtimestamp(malicious_tx.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                    'FRAUDULENT'
                ])
                writer.writerow([])

                # ===== DOUBLE SPENDING INDICATORS =====
                writer.writerow(['DOUBLE SPENDING DETECTION INDICATORS'])
                writer.writerow(['Indicator', 'Present', 'Confidence Level', 'Description'])

                indicators = [
                    ('Same Sender', True, 'HIGH', 'Both transactions from same wallet'),
                    ('Same Amount', True, 'HIGH', 'Identical transaction amounts'),
                    ('Same Timestamp', True, 'MEDIUM', 'Transactions created simultaneously'),
                    ('Different Receivers', True, 'HIGH', 'Funds sent to different destinations'),
                    ('Private Mining', attack_data.get('blocks', 0) > 0, 'HIGH', 'Attempt to create alternative chain')
                ]

                for indicator, present, confidence, description in indicators:
                    status = 'DETECTED' if present else 'NOT DETECTED'
                    writer.writerow([indicator, status, confidence, description])
                writer.writerow([])

                # ===== ATTACK EXECUTION TIMELINE =====
                writer.writerow(['ATTACK EXECUTION TIMELINE'])
                writer.writerow(['Step', 'Action', 'Result', 'Timestamp', 'Status'])

                steps = attack_result.get('steps', [])
                attack_start_time = attack_data.get('timestamp', time.time())

                for i, step in enumerate(steps, 1):
                    step_time = attack_start_time + (i * 2)  # Simulated timing
                    step_timestamp = datetime.fromtimestamp(step_time).strftime('%H:%M:%S')

                    action = step.get('action', '').replace('_', ' ').title()
                    result = step.get('result', '') or step.get('mining_success', '') or 'Completed'
                    status = 'SUCCESS' if result else 'FAILED'

                    writer.writerow([i, action, result, step_timestamp, status])
                writer.writerow([])

                # ===== NETWORK IMPACT ANALYSIS =====
                writer.writerow(['NETWORK IMPACT ANALYSIS'])
                writer.writerow(['Metric', 'Before Attack', 'After Attack', 'Change', 'Impact Level'])

                if len(NETWORK_ACTIVITY_DATA['data']) > 1:
                    before_activity = NETWORK_ACTIVITY_DATA['data'][-2]
                    after_activity = NETWORK_ACTIVITY_DATA['data'][-1]
                    change = after_activity - before_activity
                    impact = 'HIGH' if abs(change) > 30 else 'MEDIUM' if abs(change) > 15 else 'LOW'

                    writer.writerow([
                        'Network Activity',
                        f"{before_activity}%",
                        f"{after_activity}%",
                        f"{change:+.1f}%",
                        impact
                    ])

                # Add other metrics
                metrics_impact = [
                    ('Network Latency', SIMBLOCK_METRICS_DATA['network_latency'], 'Higher indicates congestion'),
                    ('Node Health', SIMBLOCK_METRICS_DATA['node_health'], 'Lower indicates node issues'),
                    ('Message Delivery', SIMBLOCK_METRICS_DATA['message_delivery'], 'Lower indicates delivery problems'),
                    ('Attack Resistance', SIMBLOCK_METRICS_DATA['attack_resistance'], 'Lower indicates vulnerability')
                ]

                for metric, value, description in metrics_impact:
                    status = 'CONCERN' if (('Latency' in metric and value > 50) or
                                          (value < 50 and 'Latency' not in metric)) else 'NORMAL'
                    writer.writerow([metric, f"{value}%", 'Current', '', status])

                writer.writerow([])

                # ===== SECURITY RECOMMENDATIONS =====
                writer.writerow(['SECURITY RECOMMENDATIONS & MITIGATIONS'])
                writer.writerow(['Priority', 'Recommendation', 'Implementation', 'Expected Impact'])

                security_recommendations = [
                    ('HIGH', 'Wait for multiple confirmations', 'Transaction validation', 'Prevents double spending'),
                    ('HIGH', 'Monitor transaction patterns', 'Real-time analytics', 'Early detection'),
                    ('MEDIUM', 'Implement network monitoring', 'Node surveillance', 'Attack prevention'),
                    ('MEDIUM', 'Use longer block times', 'Consensus parameters', 'Increases security'),
                    ('LOW', 'Regular security audits', 'Periodic reviews', 'Continuous improvement')
                ]

                for priority, recommendation, implementation, expected_impact in security_recommendations:
                    writer.writerow([priority, recommendation, implementation, expected_impact])

                writer.writerow([])

                # ===== RISK ASSESSMENT =====
                writer.writerow(['COMPREHENSIVE RISK ASSESSMENT'])
                writer.writerow(['Risk Factor', 'Level', 'Probability', 'Impact', 'Mitigation Strategy'])

                risk_factors = [
                    ('Double Spending Success', 'HIGH' if attack_successful else 'LOW',
                     f"{config.get('success_probability', 0)}%", 'HIGH' if attack_successful else 'LOW',
                     'Multiple confirmations, monitoring'),
                    ('Network Vulnerability', 'MEDIUM', '60%', 'MEDIUM', 'Enhanced node security'),
                    ('Consensus Weakness', 'LOW', '30%', 'HIGH', 'Algorithm improvements'),
                    ('User Awareness', 'MEDIUM', '70%', 'MEDIUM', 'Education & training')
                ]

                for factor, level, probability, impact, mitigation in risk_factors:
                    writer.writerow([factor, level, probability, impact, mitigation])

                writer.writerow([])

            else:
                # ===== NO ATTACK DATA SECTION =====
                writer.writerow(['NO ATTACK DATA AVAILABLE'])
                writer.writerow(['Status', 'No recent attack simulations found'])
                writer.writerow(['Action Required', 'Run attack simulation to generate analysis data'])
                writer.writerow(['Recommendation', 'Use the attack simulation interface to test scenarios'])
                writer.writerow([])

            # ===== REPORT FOOTER =====
            writer.writerow([])
            writer.writerow(['ATTACK ANALYSIS REPORT GENERATED BY: Blockchain Security System'])
            writer.writerow(['EDUCATIONAL USE: Virtual University Blockchain Research'])
            writer.writerow(['REPORT TIMESTAMP:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['REPORT ID:', f"ATTACK_ANALYSIS_{timestamp}"])

        print(f"✅ Enhanced Attack analysis CSV generated: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Enhanced Attack analysis CSV generation error: {e}")
        raise


def generate_network_metrics_csv() -> str:
    """
    Generate network metrics and performance CSV report with enhanced formatting.
    """
    try:
        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(reports_dir, f"network_metrics_{timestamp}.csv")

        network_info = get_network_info()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # ===== ENHANCED HEADER =====
            writer.writerow(['NETWORK PERFORMANCE METRICS - COMPREHENSIVE REPORT'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Network Type', 'SimBlock P2P Blockchain Simulation'])
            writer.writerow(['Node Count', f"{network_info.get('nodes', 120)} nodes"])
            writer.writerow([])
            writer.writerow([])

            # ===== NETWORK OVERVIEW =====
            writer.writerow(['NETWORK OVERVIEW & STATUS'])
            writer.writerow(['Metric', 'Value', 'Status', 'Details'])
            writer.writerow(['Network Status', network_info.get('status', 'default').title(),
                             'ACTIVE', 'Primary network status'])
            writer.writerow(['Average Latency', network_info.get('latency', '100ms'),
                             'OPTIMAL' if 'ms' in str(network_info.get('latency', '')) and int(
                                 network_info.get('latency', '100').replace('ms', '')) < 150 else 'HIGH',
                             'Network communication delay'])
            writer.writerow(['Active Nodes', network_info.get('nodes', 4),
                             'HEALTHY', 'Participating network nodes'])
            writer.writerow(['Attacker Present', 'Yes' if network_info.get('attacker_present') else 'No',
                             'MONITORED', 'Malicious node detection'])
            writer.writerow(['Simulation Ready', 'Yes' if network_info.get('simulation_ready') else 'No',
                             'READY', 'Simulation capabilities'])
            writer.writerow([])

            # ===== PERFORMANCE METRICS - ENHANCED =====
            writer.writerow(['REAL-TIME PERFORMANCE METRICS'])
            writer.writerow(['Metric', 'Current Score', 'Target Range', 'Status', 'Trend', 'Impact'])

            metrics_data = [
                ('Network Latency', SIMBLOCK_METRICS_DATA['network_latency'], '0-40%', 'Lower is better',
                 'UP' if SIMBLOCK_METRICS_DATA['network_latency'] > 50 else 'STABLE', 'High impact'),
                ('Node Health', SIMBLOCK_METRICS_DATA['node_health'], '80-100%', 'Higher is better',
                 'UP' if SIMBLOCK_METRICS_DATA['node_health'] > 70 else 'DOWN', 'Critical'),
                ('Message Delivery', SIMBLOCK_METRICS_DATA['message_delivery'], '90-100%', 'Higher is better',
                 'STABLE', 'High impact'),
                ('Attack Resistance', SIMBLOCK_METRICS_DATA['attack_resistance'], '80-100%', 'Higher is better',
                 'DOWN' if SIMBLOCK_METRICS_DATA['attack_resistance'] < 60 else 'STABLE', 'Critical')
            ]

            for metric, score, target, status, trend, impact in metrics_data:
                current_status = 'GOOD' if (
                        (metric == 'Network Latency' and score < 40) or
                        (metric != 'Network Latency' and score > 80)
                ) else 'POOR' if (
                        (metric == 'Network Latency' and score > 70) or
                        (metric != 'Network Latency' and score < 50)
                ) else 'FAIR'

                writer.writerow([metric, f"{score}%", target, current_status, trend, impact])
            writer.writerow([])

            # ===== NETWORK ACTIVITY TIMELINE - ENHANCED =====
            writer.writerow(['NETWORK ACTIVITY TIMELINE - LAST 10 EVENTS'])
            writer.writerow(['Sequence', 'Event Type', 'Activity Level', 'Timestamp', 'Duration', 'Impact'])

            for i, (label, activity) in enumerate(
                    zip(NETWORK_ACTIVITY_DATA['labels'][-10:], NETWORK_ACTIVITY_DATA['data'][-10:])):
                event_type = 'ATTACK' if 'Attack' in label else 'NORMAL'
                timestamp = datetime.now().strftime('%H:%M:%S')
                duration = '2-5min' if event_type == 'ATTACK' else 'Continuous'
                impact = 'HIGH' if event_type == 'ATTACK' and activity > 70 else 'LOW'

                writer.writerow([i + 1, event_type, f"{activity}%", timestamp, duration, impact])
            writer.writerow([])

            # ===== PEER NETWORK ANALYSIS =====
            writer.writerow(['PEER NETWORK ANALYSIS'])
            writer.writerow(['Peer Type', 'Count', 'Status', 'Distribution'])
            writer.writerow(['SimBlock Nodes', '120+', 'SIMULATED', 'Global distribution'])
            writer.writerow(['Traditional Peers', len(PEERS), 'ACTIVE' if PEERS else 'INACTIVE', 'Direct connections'])
            writer.writerow(['Total Network Size', f"{120 + len(PEERS)}+", 'HEALTHY', 'Hybrid network'])
            writer.writerow([])

            if PEERS:
                writer.writerow(['ACTIVE PEER CONNECTIONS'])
                writer.writerow(['Peer Address', 'Connection Time', 'Status'])
                for peer in PEERS:
                    writer.writerow([peer, datetime.now().strftime('%H:%M:%S'), 'ACTIVE'])
                writer.writerow([])

            # ===== NETWORK HEALTH ASSESSMENT =====
            writer.writerow(['COMPREHENSIVE NETWORK HEALTH ASSESSMENT'])
            writer.writerow(['Assessment Area', 'Score', 'Status', 'Recommendation'])

            avg_health = (SIMBLOCK_METRICS_DATA['node_health'] + SIMBLOCK_METRICS_DATA['message_delivery']) / 2
            health_status = 'EXCELLENT' if avg_health > 80 else 'GOOD' if avg_health > 60 else 'FAIR' if avg_health > 40 else 'POOR'

            assessment_areas = [
                ('Overall Health', f"{avg_health:.1f}%", health_status,
                 'Continue monitoring' if avg_health > 60 else 'Investigate network issues'),
                ('Performance', f"{(100 - SIMBLOCK_METRICS_DATA['network_latency']):.1f}%",
                 'GOOD' if SIMBLOCK_METRICS_DATA['network_latency'] < 40 else 'POOR',
                 'Optimize network routes' if SIMBLOCK_METRICS_DATA[
                                                  'network_latency'] > 60 else 'Maintain current setup'),
                ('Security', f"{SIMBLOCK_METRICS_DATA['attack_resistance']:.1f}%",
                 'STRONG' if SIMBLOCK_METRICS_DATA['attack_resistance'] > 70 else 'WEAK',
                 'Enhance security protocols' if SIMBLOCK_METRICS_DATA[
                                                     'attack_resistance'] < 50 else 'Security adequate'),
                ('Reliability', f"{SIMBLOCK_METRICS_DATA['message_delivery']:.1f}%",
                 'HIGH' if SIMBLOCK_METRICS_DATA['message_delivery'] > 85 else 'LOW',
                 'Improve node connectivity' if SIMBLOCK_METRICS_DATA['message_delivery'] < 70 else 'Reliability good')
            ]

            for area, score, status, recommendation in assessment_areas:
                writer.writerow([area, score, status, recommendation])
            writer.writerow([])

            # ===== TECHNICAL SPECIFICATIONS =====
            writer.writerow(['NETWORK TECHNICAL SPECIFICATIONS'])
            writer.writerow(['Parameter', 'Value', 'Configuration', 'Notes'])
            writer.writerow(['Network Type', 'P2P Blockchain', 'Decentralized', 'No central authority'])
            writer.writerow(['Consensus', 'Proof of Work', 'SHA-256', 'Mining required'])
            writer.writerow(['Block Time', 'Variable', 'Dynamic adjustment', 'Based on difficulty'])
            writer.writerow(['Node Distribution', 'Global', '120+ nodes', 'Simulated regions'])
            writer.writerow(['Latency Simulation', 'Enabled', 'Realistic conditions', 'Network realism'])
            writer.writerow([])

            # ===== REPORT FOOTER =====
            writer.writerow(['NETWORK METRICS REPORT GENERATED BY: Blockchain Monitoring System'])
            writer.writerow(['EDUCATIONAL PURPOSE: Virtual University Research Project'])
            writer.writerow(['REPORT TIMESTAMP:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['REPORT ID:', f"NETWORK_METRICS_{timestamp}"])

        print(f"✅ Enhanced Network metrics CSV generated: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Enhanced Network metrics CSV generation error: {e}")
        raise


def generate_double_spend_analysis_csv() -> str:
    """
    Generate double spending transaction analysis CSV report.

    Returns:
        str: File path to the generated CSV report
    """
    try:
        from blockchain.transaction import generate_double_spend_report

        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_path = os.path.join(reports_dir, f"double_spend_analysis_{timestamp}.csv")

        # Get attack data for demonstration
        attacker = 'RedHawk'
        victim = 'Victim_Wallet'
        amount = 10.0

        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attacker = attack_data.get('attacker', 'RedHawk')
            amount = attack_data.get('amount', 10.0)

        report = generate_double_spend_report(attacker, victim, amount)

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Double Spending Analysis Header
            writer.writerow(['DOUBLE SPENDING TRANSACTION ANALYSIS'])
            writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])

            # Demonstration Overview
            demo = report.get('demonstration', {})
            writer.writerow(['DEMONSTRATION OVERVIEW'])
            writer.writerow(['Type', demo.get('demonstration_type', '')])
            writer.writerow(['Scenario', demo.get('attack_scenario', '')])
            writer.writerow(['Timestamp', demo.get('timestamp', '')])
            writer.writerow([])

            # Participants
            participants = demo.get('participants', {})
            writer.writerow(['PARTICIPANTS'])
            writer.writerow(['Role', 'Address'])
            writer.writerow(['Attacker', participants.get('attacker', '')])
            writer.writerow(['Victim', participants.get('victim', '')])
            writer.writerow(['Shadow Wallet', participants.get('shadow_wallet', '')])
            writer.writerow([])

            # Transaction Details
            transactions = demo.get('transactions', {})
            writer.writerow(['TRANSACTION DETAILS'])
            writer.writerow(['Transaction', 'Type', 'Purpose', 'Sender', 'Receiver', 'Amount', 'Timestamp', 'TX ID'])

            honest_tx = transactions.get('transaction_1', {}).get('transaction', {})
            malicious_tx = transactions.get('transaction_2', {}).get('transaction', {})

            writer.writerow([
                'Honest Transaction',
                transactions.get('transaction_1', {}).get('type', ''),
                transactions.get('transaction_1', {}).get('purpose', ''),
                honest_tx.get('sender', ''),
                honest_tx.get('receiver', ''),
                honest_tx.get('amount', 0),
                honest_tx.get('timestamp', ''),
                honest_tx.get('id', '')[:16] + '...'
            ])

            writer.writerow([
                'Malicious Transaction',
                transactions.get('transaction_2', {}).get('type', ''),
                transactions.get('transaction_2', {}).get('purpose', ''),
                malicious_tx.get('sender', ''),
                malicious_tx.get('receiver', ''),
                malicious_tx.get('amount', 0),
                malicious_tx.get('timestamp', ''),
                malicious_tx.get('id', '')[:16] + '...'
            ])
            writer.writerow([])

            # Double Spend Indicators
            indicators = demo.get('double_spend_indicators', {})
            writer.writerow(['DOUBLE SPEND INDICATORS'])
            writer.writerow(['Indicator', 'Present'])
            for indicator, present in indicators.items():
                writer.writerow([indicator.replace('_', ' ').title(), 'Yes' if present else 'No'])
            writer.writerow([])

            # Validation Results
            validation = report.get('validation_results', {})
            writer.writerow(['VALIDATION RESULTS'])
            writer.writerow(['Is Double Spend', 'Yes' if validation.get('is_double_spend') else 'No'])
            writer.writerow(['Reasons'])
            for reason in validation.get('reasons', []):
                writer.writerow(['', reason])
            writer.writerow([])

            # Risk Assessment
            risk = report.get('risk_assessment', {})
            writer.writerow(['RISK ASSESSMENT'])
            writer.writerow(['Risk Level', risk.get('risk_level', '')])
            writer.writerow(['Vulnerability', risk.get('vulnerability', '')])
            writer.writerow(['Recommendations'])
            for recommendation in risk.get('recommendations', []):
                writer.writerow(['', recommendation])
            writer.writerow([])

            # Transaction Analysis Summary
            analysis = report.get('transaction_analysis', {})
            writer.writerow(['ANALYSIS SUMMARY'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Transactions', analysis.get('total_transactions', 0)])
            writer.writerow(['Conflicting Pairs', analysis.get('conflicting_pairs', 0)])
            writer.writerow(['Double Spend Detected', 'Yes' if analysis.get('double_spend_detected') else 'No'])
            writer.writerow(['Detection Confidence', analysis.get('detection_confidence', '')])

        print(f"✅ Double spend analysis CSV generated: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Double spend analysis CSV generation error: {e}")
        raise


def generate_all_csv_reports() -> Dict[str, str]:
    """
    Generate all CSV reports for comprehensive analysis.

    Returns:
        Dict[str, str]: Dictionary mapping report types to file paths
    """
    try:
        print("🚀 Generating comprehensive CSV reports...")

        reports = {}

        # Generate all report types
        reports['blockchain'] = generate_blockchain_csv_report()
        reports['attack_analysis'] = generate_attack_analysis_csv()
        reports['network_metrics'] = generate_network_metrics_csv()
        reports['double_spend_analysis'] = generate_double_spend_analysis_csv()

        print(f"✅ Generated {len(reports)} CSV reports for deep analysis")
        return reports

    except Exception as e:
        print(f"❌ CSV report generation error: {e}")
        raise


# ================================
# CHART DATA API ENDPOINTS
# ================================

@app.route('/api/charts/blockchain-growth', methods=['GET'])
def get_blockchain_growth_chart():
    """API endpoint for blockchain growth chart data"""
    try:
        chain_data = blockchain_instance.to_dict()

        if not chain_data.get("chain"):
            return jsonify({
                "labels": [],
                "datasets": [{
                    "label": "Transactions per Block",
                    "data": [],
                    "backgroundColor": "#2a5298",
                    "borderColor": "#1e3c72",
                    "borderWidth": 1
                }]
            })

        labels = [f"Block {b['index']}" for b in chain_data["chain"]]
        tx_counts = [len(b["transactions"]) for b in chain_data["chain"]]

        return jsonify({
            "labels": labels,
            "datasets": [{
                "label": "Transactions per Block",
                "data": tx_counts,
                "backgroundColor": "#2a5298",
                "borderColor": "#1e3c72",
                "borderWidth": 1
            }]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/balance-distribution', methods=['GET'])
def get_balance_distribution_chart():
    """API endpoint for balance distribution chart data"""
    try:
        balances, _ = get_balances_with_attackers()

        active_wallets = {k: v for k, v in balances.items() if v != 0}

        if not active_wallets:
            return jsonify({
                "labels": ["No Data"],
                "datasets": [{
                    "data": [1],
                    "backgroundColor": ['#C9CBCF']
                }]
            })

        return jsonify({
            "labels": list(active_wallets.keys()),
            "datasets": [{
                "data": list(active_wallets.values()),
                "backgroundColor": [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#9b59b6', '#34495e'
                ]
            }]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/mining-analysis', methods=['GET'])
def get_mining_analysis_chart():
    """API endpoint for mining analysis chart data"""
    try:
        chain_data = blockchain_instance.to_dict()

        if len(chain_data.get("chain", [])) < 2:
            return jsonify({
                "labels": [],
                "datasets": [{
                    "label": "Mining Time (seconds)",
                    "data": [],
                    "borderColor": "#e74c3c",
                    "backgroundColor": "rgba(231, 76, 60, 0.1)",
                    "fill": True,
                    "tension": 0.4
                }]
            })

        blocks = chain_data["chain"]
        block_indices = [b['index'] for b in blocks]
        mining_times = [i * 2.5 for i in range(len(blocks))]

        return jsonify({
            "labels": block_indices,
            "datasets": [{
                "label": "Mining Time (seconds)",
                "data": mining_times,
                "borderColor": "#e74c3c",
                "backgroundColor": "rgba(231, 76, 60, 0.1)",
                "fill": True,
                "tension": 0.4
            }]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/network-activity', methods=['GET'])
def get_network_activity_chart():
    """API endpoint for network activity chart data"""
    try:
        return jsonify({
            "labels": NETWORK_ACTIVITY_DATA['labels'],
            "datasets": [{
                "label": "Network Activity Level",
                "data": NETWORK_ACTIVITY_DATA['data'],
                "borderColor": "#3498db",
                "backgroundColor": "rgba(52, 152, 219, 0.3)",
                "fill": True
            }]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/simblock-analysis', methods=['GET'])
def get_simblock_analysis_chart():
    """API endpoint for SimBlock network analysis chart"""
    try:
        chart_data = {
            "labels": ["Network Latency", "Node Health", "Message Delivery", "Attack Resistance"],
            "datasets": [{
                "label": "Network Performance",
                "data": [
                    SIMBLOCK_METRICS_DATA['network_latency'],
                    SIMBLOCK_METRICS_DATA['node_health'],
                    SIMBLOCK_METRICS_DATA['message_delivery'],
                    SIMBLOCK_METRICS_DATA['attack_resistance']
                ],
                "backgroundColor": ['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                "borderColor": ['#2980b9', '#27ae60', '#d35400', '#c0392b'],
                "borderWidth": 2
            }]
        }
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/charts/reset', methods=['POST'])
def reset_chart_data_endpoint():
    """Reset all chart data to initial state"""
    try:
        reset_chart_data()
        return jsonify({
            "status": "success",
            "message": "Chart data reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
# CORE BLOCKCHAIN API ENDPOINTS
# ================================

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/chain', methods=['GET'])
def get_chain():
    """Get complete blockchain data with chart information."""
    chain_dict = blockchain_instance.to_dict()
    chain_summary = {
        "labels": [f"Block {b['index']}" for b in chain_dict["chain"]],
        "tx_counts": [len(b["transactions"]) for b in chain_dict["chain"]],
    }
    return jsonify({
        "chain": chain_dict["chain"],
        "mempool": chain_dict["mempool"],
        "difficulty": chain_dict["difficulty"],
        "chart_data": chain_summary
    })


@app.route('/api/balances', methods=['GET'])
def get_balances():
    """Get current wallet balances."""
    return jsonify(blockchain_instance.get_balances())


@app.route('/api/balances/detailed', methods=['GET'])
def get_detailed_balances():
    """Get current wallet balances with attack information"""
    try:
        balances, attack_victims = get_balances_with_attackers()

        # Include transaction details in the response
        attack_details = {}
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attack_details = {
                'transactions': attack_data.get('transactions', {}),
                'timestamp': attack_data.get('timestamp'),
                'config': attack_data.get('config', {})
            }

        return jsonify({
            "balances": balances,
            "attack_info": attack_victims,
            "total_wallets": len(balances),
            "active_attacks": len(attack_victims),
            "attack_details": attack_details  # ADD THIS LINE
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tx/new', methods=['POST'])
def new_transaction():
    """Create a new transaction."""
    try:
        tx_data = request.get_json()
        sender = tx_data.get("sender")
        receiver = tx_data.get("receiver")
        amount = float(tx_data.get("amount"))

        txid = blockchain_instance.new_transaction(sender, receiver, amount)

        tx_to_broadcast = {
            "id": txid,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": int(time.time())
        }

        for peer in PEERS:
            try:
                requests.post(f"{peer}/tx/broadcast", json=tx_to_broadcast, timeout=5)
            except Exception as e:
                print(f"Failed to broadcast to {peer}: {e}")

        return jsonify({
            "status": "ok",
            "txid": txid,
            "mempool_size": len(blockchain_instance.mempool)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/mine', methods=['POST'])
def mine_block():
    """Mine a new block with pending transactions."""
    try:
        data = request.json or {}
        miner = data.get("miner", "DefaultMiner")

        block = blockchain_instance.mine_pending_transactions(miner)

        for peer in PEERS:
            try:
                requests.post(f"{peer}/blocks/receive", json=block.to_dict(), timeout=5)
            except Exception as e:
                print(f"Failed to broadcast block to {peer}: {e}")

        return jsonify({
            "status": "ok",
            "block": block.to_dict(),
            "chain_length": len(blockchain_instance.chain)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/attack/run', methods=['POST'])
def api_run_attack():
    """Execute double-spending attack simulation"""
    try:
        data = request.get_json() or {}
        print(f"🎯 Attack Request: {data}")

        attacker = data.get("attacker", "RedHawk")
        blocks = int(data.get("blocks", 1))
        amount = float(data.get("amount", 10.0))
        frontend_config = data.get("frontend_config", {})

        hash_power = frontend_config.get('hash_power', 30)
        success_probability = frontend_config.get('success_probability', 50)
        force_success = frontend_config.get('force_success', False)
        force_failure = frontend_config.get('force_failure', False)

        # FIXED: Respect force success/failure settings
        if force_success:
            attack_successful = True
        elif force_failure:
            attack_successful = False
        else:
            # Use probability-based success
            attack_successful = success_probability > 50  # Simple success condition

        # Create transaction details for visualization
        current_timestamp = int(time.time())
        transaction_details = {
            "legitimate": {
                "sender": attacker,
                "receiver": "Victim_Wallet",
                "amount": amount,
                "timestamp": current_timestamp,
                "purpose": "Initial legitimate transaction to victim"
            },
            "malicious": {
                "sender": attacker,
                "receiver": attacker,
                "amount": amount,
                "timestamp": current_timestamp,
                "purpose": "Secret double spending transaction to own wallet"
            }
        }

        # Simulate attack result
        result = {
            "successful": attack_successful,
            "success_probability": success_probability,
            "blocks_mined": blocks if attack_successful else 0,
            "hash_power": hash_power,
            "message": "Attack successful!" if attack_successful else "Attack failed!",
            "steps": [
                {"action": "probability_calculation", "result": True},
                {"action": "private_mining", "mining_success": attack_successful},
                {"action": "network_broadcast", "result": attack_successful}
            ]
        }

        RECENT_ATTACK_RESULTS['last_attack'] = {
            'config': frontend_config,
            'timestamp': time.time(),
            'attacker': attacker,
            'blocks': blocks,
            'amount': amount,
            'transactions': transaction_details,
            'result': result
        }

        update_network_chart_data(attack_successful, hash_power, success_probability)

        # Enhanced response with transaction details
        enhanced_result = {
            **result,
            "transactions": transaction_details,
            "private_blocks_mined": blocks,
            "attack_timestamp": current_timestamp,
            "victim_wallet": "Victim_Wallet"
        }

        print(f"✅ Attack simulation completed: {'SUCCESS' if attack_successful else 'FAILED'}")

        return jsonify(enhanced_result), 200

    except Exception as e:
        print(f"💥 Attack API error: {e}")
        return jsonify({
            "error": f"Attack simulation failed: {str(e)}",
            "successful": False,
            "success_rate": 0
        }), 500


@app.route('/api/report/csv', methods=['GET'])
def generate_csv_reports_route():
    """Generate comprehensive CSV reports for deep analysis."""
    try:
        reports = generate_all_csv_reports()

        # Create a zip file containing all reports
        import zipfile
        import tempfile

        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_path = os.path.join(reports_dir, f"blockchain_analysis_reports_{timestamp}.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for report_type, report_path in reports.items():
                zipf.write(report_path, os.path.basename(report_path))

        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=f"Blockchain-Analysis-Reports-{timestamp}.zip"
        )

    except Exception as e:
        return jsonify({"error": f"CSV report generation failed: {str(e)}"}), 500


@app.route('/api/report/csv/<report_type>', methods=['GET'])
def generate_specific_csv_report(report_type):
    """Generate specific CSV report type."""
    try:
        report_paths = {
            'blockchain': generate_blockchain_csv_report,
            'attack': generate_attack_analysis_csv,
            'network': generate_network_metrics_csv,
            'double-spend': generate_double_spend_analysis_csv
        }

        if report_type not in report_paths:
            return jsonify({"error": f"Invalid report type: {report_type}"}), 400

        csv_path = report_paths[report_type]()

        return send_file(
            csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=os.path.basename(csv_path)
        )

    except Exception as e:
        return jsonify({"error": f"CSV report generation failed: {str(e)}"}), 500


# ================================
# NETWORK MANAGEMENT ENDPOINTS
# ================================

@app.route('/peers', methods=['POST'])
def add_peer():
    """Add a new peer to the network"""
    try:
        data = request.get_json()
        peer_address = data.get('address')
        if not peer_address:
            return jsonify({"error": "Invalid peer address"}), 400

        PEERS.add(peer_address)
        return jsonify({
            "message": "Peer added successfully",
            "peers": list(PEERS)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/consensus', methods=['GET'])
def resolve_conflicts():
    """Resolve blockchain conflicts with peers"""
    try:
        replaced = blockchain_instance.resolve_conflicts()
        if replaced:
            return jsonify({
                "message": "Our chain was replaced by a longer one.",
                "new_chain": [block.to_dict() for block in blockchain_instance.chain]
            }), 200
        else:
            return jsonify({
                "message": "Our chain is authoritative.",
                "chain": [block.to_dict() for block in blockchain_instance.chain]
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/blocks', methods=['GET'])
def get_blocks():
    """Get all blocks in the blockchain"""
    try:
        chain_data = [block.to_dict() for block in blockchain_instance.chain]
        return jsonify({
            "chain": chain_data,
            "length": len(chain_data)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tx/broadcast', methods=['POST'])
def broadcast_transaction_endpoint():
    """Broadcast a transaction to the network"""
    try:
        tx_data = request.get_json()
        new_tx = Transaction(
            sender=tx_data['sender'],
            receiver=tx_data['receiver'],
            amount=tx_data['amount'],
            txid=tx_data['id'],
            timestamp=tx_data['timestamp']
        )
        result = blockchain_instance.new_transaction_from_dict(new_tx.to_dict())
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/blocks/receive', methods=['POST'])
def receive_block():
    """Receive blocks from peers"""
    try:
        block_data = request.get_json()
        block = Block.from_dict(block_data)

        if blockchain_instance.add_new_block(block):
            return jsonify({"message": "Block received and added to chain"}), 200
        else:
            return jsonify({"error": "Block rejected, not a valid PoW"}), 400
    except Exception as e:
        return jsonify({"error": f"Invalid block data: {e}"}), 400


# ================================
# SIMBLOCK INTEGRATION ENDPOINTS
# ================================

@app.route('/api/simblock/network', methods=['GET'])
def get_simblock_network():
    """Get current SimBlock network conditions."""
    try:
        network_info = get_network_info()
        return jsonify(network_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simblock/start', methods=['POST'])
def start_simblock_simulation():
    """Start a new SimBlock simulation."""
    try:
        success = start_simulation()
        return jsonify({
            "status": "started",
            "success": success,
            "message": "SimBlock simulation started successfully" if success else "SimBlock simulation failed"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/simblock/attack-probability', methods=['POST'])
def calculate_attack_probability():
    """Calculate attack probability using SimBlock."""
    try:
        data = request.get_json() or {}
        base_prob = data.get('base_probability', 70.0)
        hash_power = data.get('hash_power', 50.0)
        latency = data.get('latency', 100)

        enhanced_prob = calculate_probability(base_prob, hash_power, latency)

        return jsonify({
            "base_probability": base_prob,
            "enhanced_probability": enhanced_prob,
            "hash_power": hash_power,
            "latency": latency,
            "message": "Probability calculated with SimBlock integration"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
# APPLICATION STARTUP
# ================================

if __name__ == '__main__':
    """Main entry point for the Flask application."""
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        port = int(sys.argv[2])

    if len(blockchain_instance.chain) == 0:
        blockchain_instance.create_genesis_block()
        print("✅ Genesis block created")

    import pathlib

    pathlib.Path("reports").mkdir(exist_ok=True)
    pathlib.Path("blockchain/simblock_output").mkdir(parents=True, exist_ok=True)

    print("🚀 Starting Anomaly Detection System in Blockchain...")
    print("📊 Prototype: Double Spending Attack Simulation")
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("🔧 Debug mode: ON")
    print("🛠️ SimBlock Integration: ACTIVE")
    print("📈 CSV Reports: ENABLED")

    app.run(host='0.0.0.0', port=port, debug=True)