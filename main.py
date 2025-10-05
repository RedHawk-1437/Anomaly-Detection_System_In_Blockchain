"""
main.py - Blockchain Anomaly Detection System Main Application

This module serves as the main Flask web server for the blockchain anomaly detection system.
It provides a comprehensive web interface for blockchain simulation, attack detection,
analytics visualization, and report generation.

Key Features:
- Flask web server with RESTful API endpoints
- Real-time blockchain simulation and visualization
- Double-spending attack simulation and detection
- Interactive chart generation and analytics
- PDF report generation with comprehensive analysis
- SimBlock network integration for realistic simulations
- Peer-to-peer network management
- Balance calculation with attack impact tracking

The application combines blockchain technology, network simulation, and security analysis
to provide a complete platform for studying blockchain anomalies and attack vectors.
"""

import os
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Tuple

import requests
import matplotlib
import numpy as np
from flask import Flask, jsonify, render_template, send_file, request
from fpdf import FPDF
from fpdf.enums import XPos, YPos

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
# BALANCE CALCULATION ENGINE
# ================================

def get_balances_with_attackers() -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Compute wallet balances with attack impact integration.

    Processes all transactions in the blockchain and applies attack results
    to modify balances, tracking both successful and failed attack attempts.
    Handles special cases like mining rewards and double-spending impacts.

    Returns:
        Tuple containing:
        - balances: Dictionary mapping wallet addresses to their current balances
        - attack_victims: Dictionary containing attack impact details including
                         victim information, amounts, and success status
    """
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

    # Integrate attack results into balances
    if 'last_attack' in RECENT_ATTACK_RESULTS:
        attack_data = RECENT_ATTACK_RESULTS['last_attack']
        attacker = attack_data.get('attacker', 'RedHawk')
        amount = attack_data.get('amount', 0)
        attack_success = attack_data.get('result', {}).get('successful', False)

        # Ensure attacker wallet exists
        if attacker not in balances:
            balances[attacker] = 0

        # Apply successful attack transfers
        if attack_success:
            balances[attacker] += amount

            # Locate victim transaction in recent blocks
            victim_found = False
            if blockchain_instance.chain:
                for block in reversed(blockchain_instance.chain[-3:]):
                    for tx in block.transactions:
                        if (tx.sender != "SYSTEM" and
                                abs(tx.amount - amount) < 0.01 and
                                tx.receiver != attacker):
                            victim = tx.receiver
                            if victim in balances:
                                balances[victim] -= amount
                                attack_victims[attacker] = {
                                    'victim': victim,
                                    'amount': amount,
                                    'success': True,
                                    'timestamp': attack_data.get('timestamp', time.time())
                                }
                                victim_found = True
                                break
                    if victim_found:
                        break

            # Create generic victim if none found
            if not victim_found:
                generic_victim = "Victim_Wallet"
                if generic_victim not in balances:
                    balances[generic_victim] = 100
                balances[generic_victim] -= amount
                attack_victims[attacker] = {
                    'victim': generic_victim,
                    'amount': amount,
                    'success': True,
                    'timestamp': attack_data.get('timestamp', time.time())
                }
        else:
            # Record failed attack attempt
            attack_victims[attacker] = {
                'victim': 'None (Attack Failed)',
                'amount': amount,
                'success': False,
                'timestamp': attack_data.get('timestamp', time.time())
            }

    # Remove system account from display
    if "SYSTEM" in balances:
        del balances["SYSTEM"]

    return balances, attack_victims


# ================================
# CHART GENERATION SYSTEM
# ================================

def generate_blockchain_growth_chart(chain_data: Dict[str, Any]):
    """
    Create blockchain growth visualization showing transactions per block.

    Generates a bar chart displaying the number of transactions in each block
    to visualize blockchain growth and transaction patterns over time.

    Args:
        chain_data: Blockchain data dictionary containing chain information

    Returns:
        matplotlib.figure.Figure: Configured matplotlib figure object
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        if not chain_data.get("chain"):
            ax.text(0.5, 0.5, 'No blockchain data available\nfor growth chart',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_title('Blockchain Growth - Transactions per Block', fontsize=14, fontweight='bold')
            ax.set_xlabel('Block Number', fontsize=12, fontweight='bold')
            ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            return fig

        labels = [f"Block {b['index']}" for b in chain_data["chain"]]
        tx_counts = [len(b["transactions"]) for b in chain_data["chain"]]

        bars = ax.bar(labels, tx_counts, color='#2a5298', alpha=0.8)

        ax.set_xlabel('Block Number', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Transactions', fontsize=12, fontweight='bold')
        ax.set_title('Blockchain Growth - Transactions per Block', fontsize=14, fontweight='bold')

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        ax.grid(axis='y', alpha=0.3)

        for bar, count in zip(bars, tx_counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating blockchain growth chart: {e}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Blockchain Growth Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_balance_distribution_chart(balances: Dict[str, float]):
    """
    Generate wallet balance distribution pie chart.

    Creates a pie chart visualization of wallet balances, showing the
    distribution of coins across different wallet addresses with color
    coding for positive and negative balances.

    Args:
        balances: Dictionary mapping wallet addresses to their balances

    Returns:
        matplotlib.figure.Figure: Configured matplotlib figure object
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 8))

        if not balances:
            ax.text(0.5, 0.5, 'No wallet balance data\navailable for chart',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_title('Wallet Balance Distribution', fontsize=14, fontweight='bold')
            return fig

        non_zero_balances = {k: v for k, v in balances.items() if v != 0}

        if not non_zero_balances:
            ax.text(0.5, 0.5, 'No wallet activity\navailable for chart',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_title('Wallet Balance Distribution', fontsize=14, fontweight='bold')
            return fig

        labels = list(non_zero_balances.keys())
        values = list(non_zero_balances.values())

        colors = []
        for balance in values:
            if balance > 0:
                colors.append('#2ecc71')
            else:
                colors.append('#e74c3c')

        wedges, texts, autotexts = ax.pie([abs(v) for v in values], labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90, shadow=True)

        ax.set_title('Wallet Balance Distribution (All Active Wallets)', fontsize=14, fontweight='bold')

        for text in texts + autotexts:
            text.set_fontsize(10)
            text.set_fontweight('bold')

        ax.legend(wedges, [f'{label}: {value:.2f} coins' for label, value in zip(labels, values)],
                  title="Wallet Balances", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        return fig

    except Exception as e:
        print(f"❌ Error creating balance distribution chart: {e}")
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Balance Distribution Chart', fontsize=14, fontweight='bold')
        return fig


def generate_mining_analysis_chart(chain_data: Dict[str, Any]):
    """
    Create mining performance analysis chart.

    Generates a line chart showing simulated mining times across blocks
    with trend analysis to visualize mining difficulty and performance.

    Args:
        chain_data: Blockchain data dictionary containing chain information

    Returns:
        matplotlib.figure.Figure: Configured matplotlib figure object
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        if not chain_data.get("chain") or len(chain_data["chain"]) < 2:
            ax.text(0.5, 0.5, 'Insufficient blockchain data\nfor mining analysis',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_xlabel('Block Index', fontsize=12, fontweight='bold')
            ax.set_ylabel('Mining Time (seconds)', fontsize=12, fontweight='bold')
            ax.set_title('Block Mining Time Analysis', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            return fig

        blocks = chain_data["chain"]
        mining_times = [i * 2.5 for i in range(len(blocks))]

        ax.plot(range(len(blocks)), mining_times, marker='o', linewidth=2, markersize=8,
                color='#e74c3c', markerfacecolor='#c0392b')

        ax.set_xlabel('Block Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('Mining Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Block Mining Time Analysis', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        z = np.polyfit(range(len(blocks)), mining_times, 1)
        p = np.poly1d(z)
        ax.plot(range(len(blocks)), p(range(len(blocks))), "r--", alpha=0.7)

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating mining analysis chart: {e}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Mining Analysis Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_network_activity_chart():
    """
    Generate network activity timeline chart.

    Creates a line chart showing network activity levels over time based on
    attack simulations and network conditions. Visualizes the impact of
    attacks on network behavior.

    Returns:
        matplotlib.figure.Figure: Configured matplotlib figure object
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        if not NETWORK_ACTIVITY_DATA['labels']:
            ax.text(0.5, 0.5, 'No network activity data available\nRun attacks to see network activity',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_xlabel('Time', fontsize=12, fontweight='bold')
            ax.set_ylabel('Network Activity Level', fontsize=12, fontweight='bold')
            ax.set_title('P2P Network Activity Over Time', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            return fig

        labels = NETWORK_ACTIVITY_DATA['labels']
        activity_levels = NETWORK_ACTIVITY_DATA['data']

        ax.fill_between(range(len(labels)), activity_levels, alpha=0.4, color='#3498db')
        ax.plot(range(len(labels)), activity_levels, linewidth=2, color='#2980b9', marker='o')

        ax.set_xlabel('Attack Sequence', fontsize=12, fontweight='bold')
        ax.set_ylabel('Network Activity Level', fontsize=12, fontweight='bold')
        ax.set_title('Network Activity During Attacks', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating network activity chart: {e}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Network Activity Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_simblock_analysis_chart():
    """
    Create SimBlock network performance radar chart.

    Generates a bar chart showing various network performance metrics
    including latency, node health, message delivery, and attack resistance
    based on SimBlock simulation data.

    Returns:
        matplotlib.figure.Figure: Configured matplotlib figure object
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['Network Latency', 'Node Health', 'Message Delivery', 'Attack Resistance']

        values = [
            SIMBLOCK_METRICS_DATA['network_latency'],
            SIMBLOCK_METRICS_DATA['node_health'],
            SIMBLOCK_METRICS_DATA['message_delivery'],
            SIMBLOCK_METRICS_DATA['attack_resistance']
        ]

        if all(v == 0 for v in values):
            ax.text(0.5, 0.5, 'No SimBlock metrics available\nRun attacks to see network performance',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_xlabel('Network Metrics', fontsize=12, fontweight='bold')
            ax.set_ylabel('Performance Score', fontsize=12, fontweight='bold')
            ax.set_title('SimBlock P2P Network Analysis', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            return fig

        bars = ax.bar(metrics, values, color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'])

        ax.set_xlabel('Network Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Performance Score', fontsize=12, fontweight='bold')
        ax.set_title('SimBlock P2P Network Analysis', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)

        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'{value}%', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating SimBlock chart: {e}")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('SimBlock Analysis Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


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
# PDF REPORT GENERATION SYSTEM
# ================================

class BlockchainPDF(FPDF):
    """
    Custom PDF generator for blockchain analysis reports.

    Extends FPDF to provide specialized formatting for blockchain analytics
    with custom headers, footers, and section layouts. Includes institutional
    branding and comprehensive data presentation.

    Features:
    - Custom header with institutional logos
    - Professional section formatting
    - Data table generation
    - Image embedding for charts
    - Automated pagination
    """

    def header(self):
        """Generate PDF header with institutional branding."""
        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "web", "static", "vu_logo.png")
        author_pic = os.path.join(script_dir, "web", "static", "student_pic.png")

        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 20)

        if os.path.exists(author_pic):
            self.image(author_pic, self.w - 30, 8, 20)

        self.set_font("helvetica", "B", 16)
        self.set_xy(0, 10)
        self.cell(0, 8, "Blockchain Anomaly Detection System", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "B", 14)
        self.cell(0, 6, "Comprehensive Analysis Report", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "", 10)
        self.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "", 9)
        self.set_xy(10, 35)
        self.multi_cell(80, 4,
                        "Project Instructor: Fouzia Jumani\n"
                        "Email: fouziajumani@vu.edu.pk\n"
                        "Virtual University of Pakistan")

        self.set_xy(self.w - 85, 35)
        self.multi_cell(75, 4,
                        "Project Author: Eng. Muhammad Imtiaz Shaffi\n"
                        "VU ID: BC220200917\n"
                        "Email: bc220200917mis@vu.edu.pk")

        self.set_line_width(0.5)
        self.line(10, 55, self.w - 10, 55)
        self.set_y(65)

    def footer(self):
        """Generate PDF footer with pagination and copyright."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)

        self.cell(0, 10, f"Page {self.page_no()}", align="L")

        self.set_y(-12)
        self.cell(0, 10, "© 2025 Virtual University of Pakistan - Blockchain Anomaly Detection Research",
                  align="C")

    def add_section_title(self, title: str):
        """Add formatted section title to PDF.

        Args:
            title: Section title text to display
        """
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_table(self, title: str, data: Dict[str, Any], col_widths: tuple = (60, 120)):
        """
        Add formatted data table to PDF.

        Args:
            title: Table title to display above the table
            data: Dictionary of key-value pairs to display in the table
            col_widths: Tuple specifying column widths (metric_col, value_col)
        """
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "B", 10)
        self.set_fill_color(200, 200, 200)
        self.cell(col_widths[0], 8, "Metric", border=1, fill=True, align="C")
        self.cell(col_widths[1], 8, "Value", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "", 9)
        for key, value in data.items():
            if self.get_y() > self.h - 30:
                self.add_page()

            display_value = str(value)
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."

            self.cell(col_widths[0], 7, str(key), border=1, align="L")
            self.cell(col_widths[1], 7, display_value, border=1, align="L",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(5)


def generate_charts_for_pdf(chain_data: Dict[str, Any], balances: Dict[str, float], charts_dir: str) -> Dict[str, str]:
    """
    Generate all chart images for PDF report inclusion.

    Creates and saves all visualization charts to temporary files for
    embedding in the PDF report. Handles error cases gracefully.

    Args:
        chain_data: Blockchain data dictionary
        balances: Wallet balances dictionary
        charts_dir: Output directory for chart images

    Returns:
        Dict[str, str]: Dictionary mapping chart types to their file paths
    """
    chart_paths = {}

    try:
        print("🔄 Generating charts for PDF report...")

        print("  📊 Generating blockchain growth chart...")
        growth_fig = generate_blockchain_growth_chart(chain_data)
        if growth_fig:
            chart_path = os.path.join(charts_dir, "blockchain_growth.png")
            growth_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(growth_fig)
            chart_paths['blockchain_growth'] = chart_path
            print(f"    ✅ Blockchain growth chart saved: {chart_path}")

        print("  📊 Generating balance distribution chart...")
        balance_fig = generate_balance_distribution_chart(balances)
        if balance_fig:
            chart_path = os.path.join(charts_dir, "balance_distribution.png")
            balance_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(balance_fig)
            chart_paths['balance_distribution'] = chart_path
            print(f"    ✅ Balance distribution chart saved: {chart_path}")

        print("  📊 Generating mining analysis chart...")
        mining_fig = generate_mining_analysis_chart(chain_data)
        if mining_fig:
            chart_path = os.path.join(charts_dir, "mining_analysis.png")
            mining_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(mining_fig)
            chart_paths['mining_analysis'] = chart_path
            print(f"    ✅ Mining analysis chart saved: {chart_path}")

        print("  📊 Generating network activity chart...")
        network_fig = generate_network_activity_chart()
        if network_fig:
            chart_path = os.path.join(charts_dir, "network_activity.png")
            network_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(network_fig)
            chart_paths['network_activity'] = chart_path
            print(f"    ✅ Network activity chart saved: {chart_path}")

        print("  📊 Generating SimBlock analysis chart...")
        simblock_fig = generate_simblock_analysis_chart()
        if simblock_fig:
            chart_path = os.path.join(charts_dir, "simblock_analysis.png")
            simblock_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(simblock_fig)
            chart_paths['simblock_analysis'] = chart_path
            print(f"    ✅ SimBlock analysis chart saved: {chart_path}")

        print(f"✅ Generated {len(chart_paths)} charts for PDF report")

    except Exception as e:
        print(f"❌ Chart generation error: {e}")
        import traceback
        traceback.print_exc()

    return chart_paths


def generate_comprehensive_pdf_report() -> str:
    """
    Generate complete PDF analysis report with charts and analytics.

    Creates a comprehensive PDF report containing blockchain statistics,
    transaction analysis, wallet balances, attack simulations, network
    performance metrics, and security recommendations.

    Returns:
        str: File path to the generated PDF report

    Raises:
        Exception: If PDF generation fails
    """
    try:
        print("🚀 Starting comprehensive PDF report generation...")

        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        charts_dir = os.path.join(reports_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        chain_data = blockchain_instance.to_dict()
        balances, attack_victims = get_balances_with_attackers()
        network_info = get_network_info()

        print(f"📊 Collected data: {len(chain_data.get('chain', []))} blocks, {len(balances)} wallets")

        chart_paths = generate_charts_for_pdf(chain_data, balances, charts_dir)

        pdf = BlockchainPDF()
        pdf.add_page()

        pdf.add_section_title("1. Executive Summary")
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 6,
                       "This comprehensive report provides detailed analytics of the blockchain network, "
                       "including transaction patterns, mining statistics, double-spending attack simulations, "
                       "and SimBlock P2P network integration analysis. The report is generated automatically "
                       "from the live blockchain data and includes visual charts for better analysis.")
        pdf.ln(10)

        pdf.add_section_title("2. Blockchain Overview")

        blockchain_stats = {
            "Total Blocks": len(chain_data.get("chain", [])),
            "Total Transactions": sum(len(b["transactions"]) for b in chain_data.get("chain", [])),
            "Pending Transactions": len(chain_data.get("mempool", [])),
            "Current Difficulty": chain_data.get("difficulty", "N/A"),
            "Mining Reward": f"{chain_data.get('miner_reward', 'N/A')} coins",
            "Connected Peers": len(PEERS)
        }
        pdf.add_table("Blockchain Statistics", blockchain_stats)

        if chart_paths.get('blockchain_growth'):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Blockchain Growth Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            try:
                if os.path.exists(chart_paths['blockchain_growth']):
                    pdf.image(chart_paths['blockchain_growth'], x=10, w=pdf.w - 20)
                    pdf.ln(5)
                    print("✅ Added blockchain growth chart to PDF")
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 8, "Chart file not found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 8, f"Chart not available: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                print(f"❌ Error adding blockchain growth chart: {e}")

        pdf.add_section_title("3. Transaction Analysis")

        if chain_data.get("chain"):
            recent_txs = []
            for block in chain_data["chain"][-5:]:
                for tx in block["transactions"][-3:]:
                    if tx.get("sender") != "SYSTEM":
                        recent_txs.append(
                            f"{tx.get('sender', 'Unknown')} -> {tx.get('receiver', 'Unknown')}: {tx.get('amount', 0)} coins")

            if recent_txs:
                pdf.set_font("helvetica", "B", 11)
                pdf.cell(0, 8, "Recent Transactions:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 9)
                for tx in recent_txs[-10:]:
                    pdf.cell(0, 6, f"- {tx}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.ln(5)

        pdf.add_section_title("4. Wallet Balances")

        if balances:
            balance_data = {}
            for wallet, balance in balances.items():
                balance_data[wallet] = f"{balance:.2f} coins"
            pdf.add_table("Current Wallet Balances", balance_data)

            if chart_paths.get('balance_distribution'):
                pdf.ln(5)
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "Balance Distribution Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                try:
                    if os.path.exists(chart_paths['balance_distribution']):
                        pdf.image(chart_paths['balance_distribution'], x=10, w=pdf.w - 20)
                        pdf.ln(5)
                        print("✅ Added balance distribution chart to PDF")
                    else:
                        pdf.set_font("helvetica", "", 10)
                        pdf.cell(0, 8, "Chart file not found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                except Exception as e:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 8, f"Chart not available: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    print(f"❌ Error adding balance distribution chart: {e}")
        else:
            pdf.set_font("helvetica", "", 10)
            pdf.cell(0, 8, "No wallet balance data available.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        if chart_paths.get('mining_analysis'):
            pdf.add_page()
            pdf.add_section_title("5. Mining Analysis")
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Mining Time Analysis Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            try:
                if os.path.exists(chart_paths['mining_analysis']):
                    pdf.image(chart_paths['mining_analysis'], x=10, w=pdf.w - 20)
                    pdf.ln(5)
                    print("✅ Added mining analysis chart to PDF")
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 8, "Chart file not found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 8, f"Chart not available: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                print(f"❌ Error adding mining analysis chart: {e}")

            if chain_data.get("chain"):
                mining_stats = {
                    "Total Blocks Mined": len(chain_data["chain"]),
                    "Average Transactions per Block": f"{sum(len(b['transactions']) for b in chain_data['chain']) / len(chain_data['chain']):.1f}",
                    "Genesis Block": chain_data["chain"][0]["hash"][:20] + "...",
                    "Latest Block": chain_data["chain"][-1]["hash"][:20] + "..."
                }
                pdf.add_table("Mining Statistics", mining_stats)

        pdf.add_page()
        pdf.add_section_title("6. SimBlock P2P Network Analysis")

        simblock_stats = {
            "Network Status": network_info.get('status', 'default').title(),
            "Average Latency": network_info.get('latency', '100ms'),
            "Active Nodes": network_info.get('nodes', 4),
            "Attacker Present": "Yes" if network_info.get('attacker_present') else "No",
            "Simulation Ready": "Yes" if network_info.get('simulation_ready') else "No",
            "Network Health": network_info.get('status', 'unknown').title()
        }
        pdf.add_table("Network Conditions", simblock_stats)

        if chart_paths.get('network_activity'):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Network Activity Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            try:
                if os.path.exists(chart_paths['network_activity']):
                    pdf.image(chart_paths['network_activity'], x=10, w=pdf.w - 20)
                    pdf.ln(5)
                    print("✅ Added network activity chart to PDF")
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 8, "Chart file not found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 8, f"Chart not available: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                print(f"❌ Error adding network activity chart: {e}")

        if chart_paths.get('simblock_analysis'):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "SimBlock Network Performance", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            try:
                if os.path.exists(chart_paths['simblock_analysis']):
                    pdf.image(chart_paths['simblock_analysis'], x=10, w=pdf.w - 20)
                    pdf.ln(5)
                    print("✅ Added SimBlock analysis chart to PDF")
                else:
                    pdf.set_font("helvetica", "", 10)
                    pdf.cell(0, 8, "Chart file not found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            except Exception as e:
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 8, f"Chart not available: {str(e)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                print(f"❌ Error adding SimBlock analysis chart: {e}")

        if 'last_attack' in RECENT_ATTACK_RESULTS:
            pdf.add_page()
            pdf.add_section_title("7. Double-Spending Attack Simulation")

            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attack_result = attack_data.get('result', {})

            print(f"🔍 PDF Debug - Attack Data: {attack_data}")
            print(f"🔍 PDF Debug - Frontend Config: {attack_data.get('config', {})}")

            frontend_config = attack_data.get('config', {})
            hash_power = frontend_config.get('hash_power', 0)
            success_probability = frontend_config.get('success_probability', 0)

            if hash_power == 0 and attack_result.get('hash_power'):
                hash_power = attack_result.get('hash_power', 0)
            if success_probability == 0 and attack_result.get('success_probability'):
                success_probability = attack_result.get('success_probability', 0)

            attack_config = {
                "Attacker": attack_data.get('attacker', 'Unknown'),
                "Private Blocks Mined": attack_data.get('blocks', 0),
                "Attack Amount": f"{attack_data.get('amount', 0)} coins",
                "Hash Power": f"{hash_power}%",
                "Success Probability": f"{success_probability}%"
            }
            pdf.add_table("Attack Configuration", attack_config)

            attack_successful = attack_result.get('success', False)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Attack Outcome:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("helvetica", "B", 14)
            if attack_successful:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(0, 10, "SUCCESS - Attack Successful", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(0, 10, "FAILED - Attack Prevented", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_text_color(0, 0, 0)

            if attack_result.get('message'):
                pdf.set_font("helvetica", "", 10)
                pdf.multi_cell(0, 6, f"Details: {attack_result.get('message')}")

            if attack_victims:
                pdf.ln(5)
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 8, "Attack Impact:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("helvetica", "", 10)
                for attacker, info in attack_victims.items():
                    if info['success']:
                        pdf.multi_cell(0, 6,
                                       f"Attacker '{attacker}' stole {info['amount']} coins from victim '{info['victim']}'")
                    else:
                        pdf.multi_cell(0, 6,
                                       f"Attacker '{attacker}'s attack failed - no coins stolen")

        pdf.add_page()
        pdf.add_section_title("8. Network Performance Metrics")

        performance_data = {
            "Blockchain Synchronization": "Optimal",
            "Transaction Throughput": f"{len(chain_data.get('mempool', []))} pending",
            "Network Latency": network_info.get('latency', '100ms'),
            "Node Connectivity": f"{len(PEERS)} direct peers",
            "Consensus Efficiency": "Active",
            "Attack Detection": "Enabled"
        }
        pdf.add_table("Performance Metrics", performance_data)

        pdf.add_section_title("9. Security Analysis")

        total_attacks = 0
        successful_attacks = 0

        if 'last_attack' in RECENT_ATTACK_RESULTS:
            total_attacks = 1
            attack_result = RECENT_ATTACK_RESULTS['last_attack'].get('result', {})
            if attack_result.get('success'):
                successful_attacks = 1

        security_metrics = {
            "Total Attack Simulations": total_attacks,
            "Successful Attacks": successful_attacks,
            "Attack Success Rate": f"{(successful_attacks / total_attacks) * 100 if total_attacks > 0 else 0:.1f}%",
            "Network Resilience": "High" if successful_attacks == 0 else "Medium",
            "Double-Spending Risk": "Low" if successful_attacks == 0 else "Medium"
        }
        pdf.add_table("Security Metrics", security_metrics)

        pdf.add_section_title("10. Security Recommendations")

        recommendations = [
            "Monitor for unusual transaction patterns regularly",
            "Maintain network node diversity for better security",
            "Implement additional validation for high-value transactions",
            "Regularly update consensus algorithm parameters",
            "Conduct periodic security audits and attack simulations",
            "Monitor hash power distribution among network participants"
        ]

        pdf.set_font("helvetica", "", 10)
        for i, recommendation in enumerate(recommendations, 1):
            pdf.cell(0, 6, f"{i}. {recommendation}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "Conclusion", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("helvetica", "", 10)

        if 'last_attack' in RECENT_ATTACK_RESULTS:
            attack_result = RECENT_ATTACK_RESULTS['last_attack'].get('result', {})
            if attack_result.get('success'):
                conclusion_text = (
                    "The blockchain network successfully defended against double-spending attacks "
                    "in most scenarios. However, recent simulations show that under certain conditions "
                    "(high hash power, favorable network conditions), attacks can succeed. "
                    "Continued monitoring and security enhancements are recommended."
                )
            else:
                conclusion_text = (
                    "The blockchain network demonstrated strong resilience against double-spending attacks "
                    "in all simulated scenarios. The current security measures are effective, but "
                    "continuous monitoring and periodic security assessments should be maintained."
                )
        else:
            conclusion_text = (
                "The blockchain network is operating within expected parameters. "
                "Regular monitoring and continued security assessments are recommended "
                "to maintain network integrity and detect potential anomalies."
            )

        pdf.multi_cell(0, 6, conclusion_text)

        pdf.add_page()
        pdf.add_section_title("11. Technical Details")

        technical_details = {
            "Blockchain Implementation": "Custom Python Blockchain",
            "Consensus Algorithm": "Proof of Work (PoW)",
            "Mining Difficulty": chain_data.get("difficulty", "N/A"),
            "Block Time": "Variable (Based on difficulty)",
            "Transaction Format": "JSON-based",
            "Hash Algorithm": "SHA-256",
            "Network Protocol": "REST API + SimBlock P2P",
            "Report Generation": f"Automated - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }
        pdf.add_table("System Configuration", technical_details)

        try:
            for chart_path in chart_paths.values():
                if os.path.exists(chart_path):
                    os.remove(chart_path)
                    print(f"🧹 Cleaned up chart file: {chart_path}")
            if os.path.exists(charts_dir) and not os.listdir(charts_dir):
                os.rmdir(charts_dir)
                print(f"🧹 Cleaned up charts directory: {charts_dir}")
        except Exception as e:
            print(f"Note: Could not clean up chart files: {e}")

        report_path = os.path.join(reports_dir, f"Blockchain-Report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf")
        pdf.output(report_path)

        print(f"✅ Comprehensive PDF report with charts generated: {report_path}")
        return report_path

    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
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

        return jsonify({
            "balances": balances,
            "attack_info": attack_victims,
            "total_wallets": len(balances),
            "active_attacks": len(attack_victims)
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
        print(f"🎯 RAW REQUEST DATA: {data}")

        attacker = data.get("attacker", "RedHawk")
        blocks = int(data.get("blocks", 1))
        amount = float(data.get("amount", 10.0))
        frontend_config = data.get("frontend_config", {})

        print(f"🎯 Attack Request: {attacker}, {blocks} blocks, {amount} coins")
        print(f"🔧 Frontend Config: {frontend_config}")

        all_possible_keys = []
        for key in frontend_config.keys():
            all_possible_keys.append(key)
            if 'hash' in key.lower():
                print(f"   🔍 Found hash-related key: {key} = {frontend_config[key]}")
            if 'success' in key.lower():
                print(f"   🔍 Found success-related key: {key} = {frontend_config[key]}")
            if 'force' in key.lower():
                print(f"   🔍 Found force-related key: {key} = {frontend_config[key]}")

        hash_power = (
                frontend_config.get('attackerHashPower') or
                frontend_config.get('hash_power') or
                frontend_config.get('hashPower') or
                frontend_config.get('attacker_hash_power') or
                30
        )

        success_probability = (
                frontend_config.get('successProbability') or
                frontend_config.get('success_probability') or
                frontend_config.get('probability') or
                50
        )

        force_success = (
                frontend_config.get('forceSuccess') or
                frontend_config.get('force_success') or
                frontend_config.get('forceSuccess') or
                False
        )

        force_failure = (
                frontend_config.get('forceFailure') or
                frontend_config.get('force_failure') or
                frontend_config.get('forceFail') or
                False
        )

        hash_power = (
                frontend_config.get('attackerHashPower') or
                frontend_config.get('hash_power') or
                frontend_config.get('hashPower') or
                frontend_config.get('attacker_hash_power') or
                30
        )

        corrected_config = {
            'hash_power': hash_power,
            'success_probability': success_probability,
            'force_success': force_success,
            'force_failure': force_failure,
            'latency': frontend_config.get('latency', 100)
        }

        print(f"✅ FINAL Corrected Config: {corrected_config}")

        RECENT_ATTACK_RESULTS['last_attack'] = {
            'config': corrected_config,
            'timestamp': time.time(),
            'attacker': attacker,
            'blocks': blocks,
            'amount': amount
        }

        from blockchain.attacker import run_attack

        result = run_attack(
            node_url=NODE_ADDRESS,
            peers=list(PEERS) or [NODE_ADDRESS],
            attacker_addr=attacker,
            blocks=blocks,
            amount=amount,
            frontend_config=corrected_config
        )

        attack_successful = result.get('successful', False)
        success_probability_value = result.get('success_probability', 0)

        update_network_chart_data(attack_successful, hash_power, success_probability_value)

        RECENT_ATTACK_RESULTS['last_attack']['result'] = result

        print(f"✅ Attack completed: {'SUCCESS' if result.get('successful') else 'FAILED'}")
        print(
            f"📊 Final Stats - Hash Power: {corrected_config['hash_power']}%, Probability: {result.get('success_probability', 0):.1f}%")

        return jsonify(result), 200

    except Exception as e:
        print(f"💥 Attack API error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Attack simulation failed: {str(e)}",
            "successful": False,
            "success_rate": 0
        }), 500


@app.route('/api/report/pdf', methods=['GET'])
def generate_pdf_report_route():
    """Generate comprehensive PDF report."""
    try:
        report_path = generate_comprehensive_pdf_report()

        return send_file(
            report_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"Blockchain-Analysis-Report-{datetime.now().strftime('%Y%m%d')}.pdf"
        )

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


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

    app.run(host='0.0.0.0', port=port, debug=True)