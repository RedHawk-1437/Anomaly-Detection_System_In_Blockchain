# Enhanced Flask application with working charts, attacker balance tracking, and auto-refresh

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

# Set matplotlib to non-interactive backend for server use
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import blockchain components
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction

# Import SimBlock integration
from blockchain.simblock_integration import (
    start_simulation,
    get_network_info,
    calculate_probability,
    run_attack as simblock_run_attack
)

# ================================
# FLASK APPLICATION SETUP
# ================================

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# ================================
# GLOBAL VARIABLES
# ================================

# Core blockchain instance
blockchain_instance = Blockchain(difficulty=3, reward=1.0)

# Network peers and node configuration
PEERS = set()
NODE_ADDRESS = os.environ.get("NODE_ADDRESS", "http://127.0.0.1:5000")

# Analytics and attack tracking
RECENT_ATTACK_RESULTS = {}

# ✅ ADDED: Dynamic chart data storage
NETWORK_ACTIVITY_DATA = {
    'labels': [],
    'data': []
}

SIMBLOCK_METRICS_DATA = {
    'network_latency': 0,
    'node_health': 0,
    'message_delivery': 0,
    'attack_resistance': 0
}


# ================================
# ENHANCED BALANCE CALCULATION WITH ATTACKER TRACKING
# ================================

def get_balances_with_attackers() -> Tuple[Dict[str, float], Dict[str, Any]]:
    """
    Calculate current wallet balances including attackers and victims
    Returns: (balances, attack_victims)
    """
    balances = {}
    attack_victims = {}

    # Process all transactions in the blockchain
    for block in blockchain_instance.chain:
        for tx in block.transactions:
            sender = tx.sender
            receiver = tx.receiver
            amount = tx.amount

            # Initialize wallets if not present
            if sender not in balances:
                balances[sender] = 0
            if receiver not in balances:
                balances[receiver] = 0

            # Only deduct from sender if not SYSTEM (mining reward)
            if sender != "SYSTEM":
                balances[sender] -= amount
            balances[receiver] += amount

    # ✅ ENHANCED: Include attacker balances and track victims
    if 'last_attack' in RECENT_ATTACK_RESULTS:
        attack_data = RECENT_ATTACK_RESULTS['last_attack']
        attacker = attack_data.get('attacker', 'RedHawk')
        amount = attack_data.get('amount', 0)
        attack_success = attack_data.get('result', {}).get('successful', False)

        # Initialize attacker wallet if not present
        if attacker not in balances:
            balances[attacker] = 0

        # If attack successful, attacker gains the amount and victim loses
        if attack_success:
            balances[attacker] += amount

            # ✅ Find the victim from recent transactions
            victim_found = False
            if blockchain_instance.chain:
                # Look in recent blocks for the transaction
                for block in reversed(blockchain_instance.chain[-3:]):  # Check last 3 blocks
                    for tx in block.transactions:
                        if (tx.sender != "SYSTEM" and
                                abs(tx.amount - amount) < 0.01 and  # Allow small floating point differences
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

            # If no victim found in transactions, create a generic one
            if not victim_found:
                generic_victim = "Victim_Wallet"
                if generic_victim not in balances:
                    balances[generic_victim] = 100  # Start with some balance
                balances[generic_victim] -= amount
                attack_victims[attacker] = {
                    'victim': generic_victim,
                    'amount': amount,
                    'success': True,
                    'timestamp': attack_data.get('timestamp', time.time())
                }
        else:
            # Track failed attacks too
            attack_victims[attacker] = {
                'victim': 'None (Attack Failed)',
                'amount': amount,
                'success': False,
                'timestamp': attack_data.get('timestamp', time.time())
            }

    # Remove SYSTEM from balances for display
    if "SYSTEM" in balances:
        del balances["SYSTEM"]

    return balances, attack_victims


# ================================
# CHART GENERATION FUNCTIONS - FIXED TO RETURN FIGURE OBJECTS
# ================================

def generate_blockchain_growth_chart(chain_data: Dict[str, Any]):
    """
    Generate blockchain growth chart for PDF report.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        if not chain_data.get("chain"):
            # Return empty chart
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

        # Fix for tick labels warning
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, count in zip(bars, tx_counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating blockchain growth chart: {e}")
        # Return empty chart on error
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Blockchain Growth Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_balance_distribution_chart(balances: Dict[str, float]):
    """
    Generate balance distribution chart for PDF report.
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 8))

        if not balances:
            ax.text(0.5, 0.5, 'No wallet balance data\navailable for chart',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_title('Wallet Balance Distribution', fontsize=14, fontweight='bold')
            return fig

        # ✅ FIXED: Include ALL balances (positive and negative) but exclude zero balances
        non_zero_balances = {k: v for k, v in balances.items() if v != 0}

        if not non_zero_balances:
            ax.text(0.5, 0.5, 'No wallet activity\navailable for chart',
                    ha='center', va='center', fontsize=12, fontweight='bold')
            ax.set_title('Wallet Balance Distribution', fontsize=14, fontweight='bold')
            return fig

        labels = list(non_zero_balances.keys())
        values = list(non_zero_balances.values())

        # ✅ Use different colors for positive and negative balances
        colors = []
        for balance in values:
            if balance > 0:
                colors.append('#2ecc71')  # Green for positive
            else:
                colors.append('#e74c3c')  # Red for negative

        wedges, texts, autotexts = ax.pie([abs(v) for v in values], labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90, shadow=True)

        ax.set_title('Wallet Balance Distribution (All Active Wallets)', fontsize=14, fontweight='bold')

        # Improve text appearance
        for text in texts + autotexts:
            text.set_fontsize(10)
            text.set_fontweight('bold')

        # ✅ Add legend for balance types
        ax.legend(wedges, [f'{label}: {value:.2f} coins' for label, value in zip(labels, values)],
                  title="Wallet Balances", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        return fig

    except Exception as e:
        print(f"❌ Error creating balance distribution chart: {e}")
        # Return empty chart on error
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Balance Distribution Chart', fontsize=14, fontweight='bold')
        return fig


def generate_mining_analysis_chart(chain_data: Dict[str, Any]):
    """
    Generate mining analysis chart for PDF report.
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
        mining_times = [i * 2.5 for i in range(len(blocks))]  # Simulated times

        ax.plot(range(len(blocks)), mining_times, marker='o', linewidth=2, markersize=8,
                color='#e74c3c', markerfacecolor='#c0392b')

        ax.set_xlabel('Block Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('Mining Time (seconds)', fontsize=12, fontweight='bold')
        ax.set_title('Block Mining Time Analysis', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Add trend line
        z = np.polyfit(range(len(blocks)), mining_times, 1)
        p = np.poly1d(z)
        ax.plot(range(len(blocks)), p(range(len(blocks))), "r--", alpha=0.7)

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating mining analysis chart: {e}")
        # Return empty chart on error
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Mining Analysis Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_network_activity_chart():
    """
    Generate network activity chart for PDF report - UPDATED to use dynamic data
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        # ✅ UPDATED: Use dynamic network activity data
        if not NETWORK_ACTIVITY_DATA['labels']:
            # Show empty chart with message
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

        # Set x-axis labels
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating network activity chart: {e}")
        # Return empty chart on error
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('Network Activity Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


def generate_simblock_analysis_chart():
    """
    Generate SimBlock network analysis chart for PDF - UPDATED to use dynamic data
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics = ['Network Latency', 'Node Health', 'Message Delivery', 'Attack Resistance']

        # ✅ UPDATED: Use dynamic SimBlock metrics
        values = [
            SIMBLOCK_METRICS_DATA['network_latency'],
            SIMBLOCK_METRICS_DATA['node_health'],
            SIMBLOCK_METRICS_DATA['message_delivery'],
            SIMBLOCK_METRICS_DATA['attack_resistance']
        ]

        # If all values are zero, show empty chart
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

        # Add value labels
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f'{value}%', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        return fig

    except Exception as e:
        print(f"❌ Error creating SimBlock chart: {e}")
        # Return empty chart on error
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f'Error generating chart:\n{str(e)}',
                ha='center', va='center', fontsize=10, color='red')
        ax.set_title('SimBlock Analysis Chart', fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig


# ✅ ADDED: Function to update network data after attacks
def update_network_chart_data(attack_successful, hash_power, probability):
    """
    Update network activity and SimBlock metrics based on attack results
    """
    try:
        # Update network activity data
        attack_count = len(NETWORK_ACTIVITY_DATA['labels']) + 1
        NETWORK_ACTIVITY_DATA['labels'].append(f"Attack {attack_count}")

        # Calculate activity level based on attack parameters
        base_activity = hash_power * 2  # Higher hash power = more activity
        if attack_successful:
            activity_level = min(100, base_activity + 30)  # Successful attacks create more activity
        else:
            activity_level = max(10, base_activity - 10)  # Failed attacks create less activity

        # Add some randomness to make it realistic
        activity_level += np.random.randint(-5, 15)
        activity_level = max(5, min(100, activity_level))

        NETWORK_ACTIVITY_DATA['data'].append(activity_level)

        # Keep only last 10 attacks for chart clarity
        if len(NETWORK_ACTIVITY_DATA['labels']) > 10:
            NETWORK_ACTIVITY_DATA['labels'] = NETWORK_ACTIVITY_DATA['labels'][-10:]
            NETWORK_ACTIVITY_DATA['data'] = NETWORK_ACTIVITY_DATA['data'][-10:]

        # Update SimBlock metrics
        SIMBLOCK_METRICS_DATA['network_latency'] = min(100, max(10, hash_power + np.random.randint(5, 25)))

        # Node health decreases with successful attacks, increases with failures
        if attack_successful:
            SIMBLOCK_METRICS_DATA['node_health'] = max(10, SIMBLOCK_METRICS_DATA.get('node_health', 100) - 15)
        else:
            SIMBLOCK_METRICS_DATA['node_health'] = min(100, SIMBLOCK_METRICS_DATA.get('node_health', 50) + 10)

        # Message delivery affected by attack success and hash power
        SIMBLOCK_METRICS_DATA['message_delivery'] = 100 - (hash_power / 2) + np.random.randint(-10, 10)
        SIMBLOCK_METRICS_DATA['message_delivery'] = max(10, min(100, SIMBLOCK_METRICS_DATA['message_delivery']))

        # Attack resistance based on failure rate
        if attack_successful:
            SIMBLOCK_METRICS_DATA['attack_resistance'] = max(10,
                                                             SIMBLOCK_METRICS_DATA.get('attack_resistance', 100) - 20)
        else:
            SIMBLOCK_METRICS_DATA['attack_resistance'] = min(100,
                                                             SIMBLOCK_METRICS_DATA.get('attack_resistance', 50) + 15)

        print(f"📊 Updated network charts - Activity: {activity_level}, Metrics: {SIMBLOCK_METRICS_DATA}")

    except Exception as e:
        print(f"❌ Error updating network chart data: {e}")


# ✅ ADDED: Function to reset chart data
def reset_chart_data():
    """Reset all chart data to initial empty state"""
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
# PDF REPORT GENERATION - FIXED WITH BETTER CHART HANDLING
# ================================

class BlockchainPDF(FPDF):
    """
    Custom PDF class for blockchain reports using standard fonts.
    """

    def header(self):
        """Create custom header with logos and project information."""
        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "web", "static", "vu_logo.png")
        author_pic = os.path.join(script_dir, "web", "static", "student_pic.png")

        # Add university logo
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 20)

        # Add author photo
        if os.path.exists(author_pic):
            self.image(author_pic, self.w - 30, 8, 20)

        # Title and project information
        self.set_font("helvetica", "B", 16)
        self.set_xy(0, 10)
        self.cell(0, 8, "Blockchain Anomaly Detection System", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "B", 14)
        self.cell(0, 6, "Comprehensive Analysis Report", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("helvetica", "", 10)
        self.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                  align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Instructor and author information
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

        # Separator line
        self.set_line_width(0.5)
        self.line(10, 55, self.w - 10, 55)
        self.set_y(65)

    def footer(self):
        """Create custom footer with page numbers and copyright."""
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128)

        # Page number
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

        # Copyright line
        self.set_y(-12)
        self.cell(0, 10, "© 2025 Virtual University of Pakistan - Blockchain Anomaly Detection Research",
                  align="C")

    def add_section_title(self, title: str):
        """Add a section title with consistent formatting."""
        self.set_font("helvetica", "B", 14)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_table(self, title: str, data: Dict[str, Any], col_widths: tuple = (60, 120)):
        """
        Add a formatted table to the PDF.
        """
        self.set_font("helvetica", "B", 12)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Table headers
        self.set_font("helvetica", "B", 10)
        self.set_fill_color(200, 200, 200)
        self.cell(col_widths[0], 8, "Metric", border=1, fill=True, align="C")
        self.cell(col_widths[1], 8, "Value", border=1, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Table rows
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
    Generate chart images for inclusion in the PDF report.

    Args:
        chain_data: Blockchain data
        balances: Wallet balances
        charts_dir: Directory to save chart images

    Returns:
        Dictionary of chart file paths
    """
    chart_paths = {}

    try:
        print("🔄 Generating charts for PDF report...")

        # Generate Blockchain Growth Chart
        print("  📊 Generating blockchain growth chart...")
        growth_fig = generate_blockchain_growth_chart(chain_data)
        if growth_fig:
            chart_path = os.path.join(charts_dir, "blockchain_growth.png")
            growth_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(growth_fig)  # Close the figure properly
            chart_paths['blockchain_growth'] = chart_path
            print(f"    ✅ Blockchain growth chart saved: {chart_path}")

        # Generate Balance Distribution Chart
        print("  📊 Generating balance distribution chart...")
        balance_fig = generate_balance_distribution_chart(balances)
        if balance_fig:
            chart_path = os.path.join(charts_dir, "balance_distribution.png")
            balance_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(balance_fig)
            chart_paths['balance_distribution'] = chart_path
            print(f"    ✅ Balance distribution chart saved: {chart_path}")

        # Generate Mining Analysis Chart
        print("  📊 Generating mining analysis chart...")
        mining_fig = generate_mining_analysis_chart(chain_data)
        if mining_fig:
            chart_path = os.path.join(charts_dir, "mining_analysis.png")
            mining_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(mining_fig)
            chart_paths['mining_analysis'] = chart_path
            print(f"    ✅ Mining analysis chart saved: {chart_path}")

        # Generate Network Activity Chart
        print("  📊 Generating network activity chart...")
        network_fig = generate_network_activity_chart()
        if network_fig:
            chart_path = os.path.join(charts_dir, "network_activity.png")
            network_fig.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close(network_fig)
            chart_paths['network_activity'] = chart_path
            print(f"    ✅ Network activity chart saved: {chart_path}")

        # Generate SimBlock Analysis Chart
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
    Generate a comprehensive PDF report with all blockchain analytics and charts.
    """
    try:
        print("🚀 Starting comprehensive PDF report generation...")

        # Create reports directory
        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        charts_dir = os.path.join(reports_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)

        # Collect all data for the report
        chain_data = blockchain_instance.to_dict()
        balances, attack_victims = get_balances_with_attackers()
        network_info = get_network_info()

        print(f"📊 Collected data: {len(chain_data.get('chain', []))} blocks, {len(balances)} wallets")

        # Generate charts for PDF
        chart_paths = generate_charts_for_pdf(chain_data, balances, charts_dir)

        # Initialize PDF
        pdf = BlockchainPDF()
        pdf.add_page()

        # ===== EXECUTIVE SUMMARY =====
        pdf.add_section_title("1. Executive Summary")
        pdf.set_font("helvetica", "", 11)
        pdf.multi_cell(0, 6,
                       "This comprehensive report provides detailed analytics of the blockchain network, "
                       "including transaction patterns, mining statistics, double-spending attack simulations, "
                       "and SimBlock P2P network integration analysis. The report is generated automatically "
                       "from the live blockchain data and includes visual charts for better analysis.")
        pdf.ln(10)

        # ===== BLOCKCHAIN OVERVIEW =====
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

        # Add Blockchain Growth Chart if available
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

        # ===== TRANSACTION ANALYSIS =====
        pdf.add_section_title("3. Transaction Analysis")

        if chain_data.get("chain"):
            # Recent transactions
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

        # ===== WALLET BALANCES =====
        pdf.add_section_title("4. Wallet Balances")

        if balances:
            balance_data = {}
            for wallet, balance in balances.items():
                balance_data[wallet] = f"{balance:.2f} coins"
            pdf.add_table("Current Wallet Balances", balance_data)

            # Add Balance Distribution Chart if available
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

        # ===== MINING ANALYSIS =====
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

            # Add mining statistics if available
            if chain_data.get("chain"):
                mining_stats = {
                    "Total Blocks Mined": len(chain_data["chain"]),
                    "Average Transactions per Block": f"{sum(len(b['transactions']) for b in chain_data['chain']) / len(chain_data['chain']):.1f}",
                    "Genesis Block": chain_data["chain"][0]["hash"][:20] + "...",
                    "Latest Block": chain_data["chain"][-1]["hash"][:20] + "..."
                }
                pdf.add_table("Mining Statistics", mining_stats)

        # ===== SIMBLOCK NETWORK ANALYSIS =====
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

        # Add Network Activity Chart if available
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

        # Add SimBlock Analysis Chart if available
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

        # ===== ATTACK SIMULATION RESULTS =====
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            pdf.add_page()
            pdf.add_section_title("7. Double-Spending Attack Simulation")

            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attack_result = attack_data.get('result', {})

            # Debug information
            print(f"🔍 PDF Debug - Attack Data: {attack_data}")
            print(f"🔍 PDF Debug - Frontend Config: {attack_data.get('config', {})}")

            # Get hash power and probability from frontend config or use defaults
            frontend_config = attack_data.get('config', {})
            hash_power = frontend_config.get('hash_power', 0)
            success_probability = frontend_config.get('success_probability', 0)

            # If not in frontend config, try to get from attack result
            if hash_power == 0 and attack_result.get('hash_power'):
                hash_power = attack_result.get('hash_power', 0)
            if success_probability == 0 and attack_result.get('success_probability'):
                success_probability = attack_result.get('success_probability', 0)

            # Attack configuration
            attack_config = {
                "Attacker": attack_data.get('attacker', 'Unknown'),
                "Private Blocks Mined": attack_data.get('blocks', 0),
                "Attack Amount": f"{attack_data.get('amount', 0)} coins",
                "Hash Power": f"{hash_power}%",
                "Success Probability": f"{success_probability}%"
            }
            pdf.add_table("Attack Configuration", attack_config)

            # Attack results
            attack_successful = attack_result.get('success', False)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 8, "Attack Outcome:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_font("helvetica", "B", 14)
            if attack_successful:
                pdf.set_text_color(0, 128, 0)  # Green for success
                pdf.cell(0, 10, "SUCCESS - Attack Successful", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                pdf.set_text_color(255, 0, 0)  # Red for failure
                pdf.cell(0, 10, "FAILED - Attack Prevented", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.set_text_color(0, 0, 0)  # Reset to black

            if attack_result.get('message'):
                pdf.set_font("helvetica", "", 10)
                pdf.multi_cell(0, 6, f"Details: {attack_result.get('message')}")

            # ✅ ADDED: Show victim information
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

        # ===== NETWORK PERFORMANCE =====
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

        # ===== SECURITY ANALYSIS =====
        pdf.add_section_title("9. Security Analysis")

        # Calculate security metrics based on recent attacks
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

        # ===== RECOMMENDATIONS =====
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

        # ===== CONCLUSION =====
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 8, "Conclusion", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_font("helvetica", "", 10)

        # Dynamic conclusion based on attack results
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

        # ===== TECHNICAL DETAILS =====
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

        # Clean up chart files
        try:
            for chart_path in chart_paths.values():
                if os.path.exists(chart_path):
                    os.remove(chart_path)
                    print(f"🧹 Cleaned up chart file: {chart_path}")
            # Only remove directory if it's empty
            if os.path.exists(charts_dir) and not os.listdir(charts_dir):
                os.rmdir(charts_dir)
                print(f"🧹 Cleaned up charts directory: {charts_dir}")
        except Exception as e:
            print(f"Note: Could not clean up chart files: {e}")

        # Save PDF
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
# CHART API ENDPOINTS - UPDATED FOR DYNAMIC DATA
# ================================

@app.route('/api/charts/blockchain-growth', methods=['GET'])
def get_blockchain_growth_chart():
    """API endpoint for blockchain growth chart data"""
    try:
        chain_data = blockchain_instance.to_dict()

        if not chain_data.get("chain"):
            # Return empty dataset for initial load
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

        # ✅ FIXED: Include ALL wallets (positive and negative balances)
        active_wallets = {k: v for k, v in balances.items() if v != 0}

        if not active_wallets:
            # Return empty dataset for initial load
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
            # Return empty dataset for initial load
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
        # Simulate mining times
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
    """API endpoint for network activity chart data - UPDATED for dynamic data"""
    try:
        # ✅ UPDATED: Return dynamic network activity data
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
    """API endpoint for SimBlock network analysis chart - UPDATED for dynamic data"""
    try:
        # ✅ UPDATED: Return dynamic SimBlock metrics
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


# ✅ ADDED: Endpoint to reset chart data
@app.route('/api/charts/reset', methods=['POST'])
def reset_chart_data_endpoint():
    """Reset all chart data to initial empty state"""
    try:
        reset_chart_data()
        return jsonify({
            "status": "success",
            "message": "Chart data reset successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
# CORE API ENDPOINTS (Keep all existing endpoints)
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

        # Broadcast to peers
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

        # Broadcast to peers
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
    """Run a double-spending attack simulation - UPDATED to update network charts"""
    try:
        data = request.get_json() or {}
        print(f"🎯 RAW REQUEST DATA: {data}")

        attacker = data.get("attacker", "RedHawk")
        blocks = int(data.get("blocks", 1))
        amount = float(data.get("amount", 10.0))
        frontend_config = data.get("frontend_config", {})

        print(f"🎯 Attack Request: {attacker}, {blocks} blocks, {amount} coins")
        print(f"🔧 Frontend Config: {frontend_config}")

        # ✅ DEBUG: Print ALL possible parameter names
        all_possible_keys = []
        for key in frontend_config.keys():
            all_possible_keys.append(key)
            if 'hash' in key.lower():
                print(f"   🔍 Found hash-related key: {key} = {frontend_config[key]}")
            if 'success' in key.lower():
                print(f"   🔍 Found success-related key: {key} = {frontend_config[key]}")
            if 'force' in key.lower():
                print(f"   🔍 Found force-related key: {key} = {frontend_config[key]}")

        # ✅ FIXED: Try multiple possible parameter names from frontend
        hash_power = (
                frontend_config.get('attackerHashPower') or
                frontend_config.get('hash_power') or
                frontend_config.get('hashPower') or
                frontend_config.get('attacker_hash_power') or
                30  # default fallback
        )

        success_probability = (
                frontend_config.get('successProbability') or
                frontend_config.get('success_probability') or
                frontend_config.get('probability') or
                50  # default fallback
        )

        force_success = (
                frontend_config.get('forceSuccess') or
                frontend_config.get('force_success') or
                frontend_config.get('forceSuccess') or
                False  # default fallback
        )

        force_failure = (
                frontend_config.get('forceFailure') or
                frontend_config.get('force_failure') or
                frontend_config.get('forceFail') or
                False  # default fallback
        )

        # ✅ ADDED: Extract hash power for chart updates
        hash_power = (
                frontend_config.get('attackerHashPower') or
                frontend_config.get('hash_power') or
                frontend_config.get('hashPower') or
                frontend_config.get('attacker_hash_power') or
                30  # default fallback
        )

        corrected_config = {
            'hash_power': hash_power,
            'success_probability': success_probability,
            'force_success': force_success,
            'force_failure': force_failure,
            'latency': frontend_config.get('latency', 100)
        }

        print(f"✅ FINAL Corrected Config: {corrected_config}")

        # Store attack configuration with corrected data
        RECENT_ATTACK_RESULTS['last_attack'] = {
            'config': corrected_config,
            'timestamp': time.time(),
            'attacker': attacker,
            'blocks': blocks,
            'amount': amount
        }

        # Import and run attack
        from blockchain.attacker import run_attack

        result = run_attack(
            node_url=NODE_ADDRESS,
            peers=list(PEERS) or [NODE_ADDRESS],
            attacker_addr=attacker,
            blocks=blocks,
            amount=amount,
            frontend_config=corrected_config
        )

        # ✅ ADDED: Update network charts with attack results
        attack_successful = result.get('successful', False)
        success_probability_value = result.get('success_probability', 0)

        update_network_chart_data(attack_successful, hash_power, success_probability_value)

        # Store results with enhanced data
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
# NETWORK MANAGEMENT ENDPOINTS (Keep all existing endpoints)
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
# SIMBLOCK INTEGRATION ENDPOINTS (Keep all existing endpoints)
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
    # Get port from command line or use default
    port = 5000
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        port = int(sys.argv[2])

    # Initialize blockchain with genesis block if empty
    if len(blockchain_instance.chain) == 0:
        blockchain_instance.create_genesis_block()
        print("✅ Genesis block created")

    # Create necessary directories
    import pathlib

    pathlib.Path("reports").mkdir(exist_ok=True)
    pathlib.Path("blockchain/simblock_output").mkdir(parents=True, exist_ok=True)

    # Startup information
    print("🚀 Starting Anomaly Detection System in Blockchain...")
    print("📊 Prototype: Double Spending Attack Simulation")
    print("🌐 Server running on: http://127.0.0.1:5000")
    print("🔧 Debug mode: ON")
    print("🛠️ SimBlock Integration: ACTIVE")

    # Start Flask application
    app.run(host='0.0.0.0', port=port, debug=True)