# main.py - Enhanced with comprehensive chart visualization
# This is the main Flask application that serves the blockchain web interface
# and provides API endpoints for blockchain operations, analytics, and attack simulations.

import os
import json
import subprocess
import shutil
import sys

import requests
from statistics import mean
from flask import Flask, jsonify, render_template, send_file, request
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from blockchain.attacker import run_attack
import matplotlib
import numpy as np
from datetime import datetime
import time

# Set matplotlib to use non-interactive backend (for server use)
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import blockchain components from our package
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction

# Create Flask application with custom template and static folders
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# Global Variables
# Initialize the main blockchain instance with difficulty 3 and reward 1.0
blockchain_instance = Blockchain(difficulty=3, reward=1.0)

# Set to store peer node addresses
PEERS = set()

# Current node's address (default: localhost:5000)
NODE_ADDRESS = os.environ.get("NODE_ADDRESS", "http://127.0.0.1:5000")

# Store recent attack results for reporting
RECENT_ATTACK_RESULTS = {}

# Enhanced data storage for charts and analytics
BLOCKCHAIN_ANALYTICS = {
    'transaction_history': [],  # History of all transactions
    'mining_times': [],  # Time taken to mine each block
    'block_sizes': [],  # Size of each block (number of transactions)
    'attack_results': [],  # Results of attack simulations
    'network_activity': []  # Network activity over time
}


# --------------------------------------------------------
# Chart Generation Functions (FIXED)
# --------------------------------------------------------

def generate_blockchain_growth_chart(chain_data):
    """
    Generate blockchain growth chart showing transactions per block.

    Args:
        chain_data (dict): Blockchain data containing chain information

    Returns:
        matplotlib.pyplot: Plot object with blockchain growth chart
    """
    # Check if we have chain data
    if not chain_data.get("chain"):
        return None

    # Create labels for x-axis (Block numbers)
    labels = [f"Block {b['index']}" for b in chain_data["chain"]]
    # Count transactions in each block for y-axis
    tx_counts = [len(b["transactions"]) for b in chain_data["chain"]]

    # Create the plot figure
    plt.figure(figsize=(10, 6))
    # Create bar chart
    bars = plt.bar(labels, tx_counts, color='#2a5298', alpha=0.8)

    # Configure chart labels and title
    plt.xlabel('Block Number', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Transactions', fontsize=12, fontweight='bold')
    plt.title('Blockchain Growth - Transactions per Block', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for readability
    plt.grid(axis='y', alpha=0.3)  # Add grid lines

    # Add value labels on top of each bar
    for bar, count in zip(bars, tx_counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 str(count), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return plt


def generate_balance_distribution_chart(balances):
    """
    Generate pie chart for wallet balance distribution - FIXED FOR NEGATIVE VALUES.

    Args:
        balances (dict): Dictionary of wallet addresses and their balances

    Returns:
        matplotlib.pyplot: Plot object with balance distribution chart
    """
    # Check if we have balance data
    if not balances:
        return None

    # Filter out zero and negative balances for pie chart (only positive values make sense for pie)
    positive_balances = {k: v for k, v in balances.items() if v > 0}

    # If no positive balances, create a placeholder message
    if not positive_balances:
        plt.figure(figsize=(8, 8))
        plt.text(0.5, 0.5, 'No positive balances\navailable for chart',
                 ha='center', va='center', fontsize=12, fontweight='bold')
        plt.title('Wallet Balance Distribution', fontsize=14, fontweight='bold')
        return plt

    # Extract labels and values for the pie chart
    labels = list(positive_balances.keys())
    values = list(positive_balances.values())
    # Generate distinct colors for each slice
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

    # Create pie chart
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(values, labels=labels, colors=colors, autopct='%1.1f%%',
                                       startangle=90, shadow=True)

    plt.title('Wallet Balance Distribution (Positive Balances Only)', fontsize=14, fontweight='bold')

    # Improve text appearance for better readability
    for text in texts + autotexts:
        text.set_fontsize(10)
        text.set_fontweight('bold')

    return plt


def generate_mining_analysis_chart(chain_data):
    """
    Generate mining analysis chart showing block mining patterns.

    Args:
        chain_data (dict): Blockchain data containing chain information

    Returns:
        matplotlib.pyplot: Plot object with mining analysis chart
    """
    # Check if we have sufficient chain data
    if not chain_data.get("chain"):
        return None

    blocks = chain_data["chain"]
    # Need at least 2 blocks for meaningful analysis
    if len(blocks) < 2:
        return None

    # Calculate mining times (simulated - in real system this would be actual times)
    mining_times = [i * 2.5 for i in range(len(blocks))]  # Simulated times

    # Create line plot
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(blocks)), mining_times, marker='o', linewidth=2, markersize=8,
             color='#e74c3c', markerfacecolor='#c0392b')

    # Configure chart
    plt.xlabel('Block Index', fontsize=12, fontweight='bold')
    plt.ylabel('Mining Time (seconds)', fontsize=12, fontweight='bold')
    plt.title('Block Mining Time Analysis', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    # Add trend line to show overall pattern
    z = np.polyfit(range(len(blocks)), mining_times, 1)  # Linear fit
    p = np.poly1d(z)  # Create polynomial function
    plt.plot(range(len(blocks)), p(range(len(blocks))), "r--", alpha=0.7)  # Dashed trend line

    plt.tight_layout()
    return plt


def generate_attack_success_chart(attack_history):
    """
    Generate chart showing attack success rates over time.

    Args:
        attack_history (list): List of attack result dictionaries

    Returns:
        matplotlib.pyplot: Plot object with attack success chart
    """
    # Check if we have attack history data
    if not attack_history:
        return None

    # Extract success flags from attack history
    successes = [1 if attack.get('successful') else 0 for attack in attack_history]
    attempts = range(1, len(successes) + 1)

    # Calculate cumulative success rate over time
    success_rate = [sum(successes[:i + 1]) / (i + 1) * 100 for i in range(len(successes))]

    # Create line plot
    plt.figure(figsize=(10, 6))
    plt.plot(attempts, success_rate, marker='s', linewidth=2, markersize=6,
             color='#27ae60', markerfacecolor='#2ecc71')

    # Configure chart
    plt.xlabel('Attack Attempt Number', fontsize=12, fontweight='bold')
    plt.ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Double-Spending Attack Success Rate Over Time', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)  # Set y-axis limits from 0% to 100%

    plt.tight_layout()
    return plt


def generate_network_activity_chart(network_data):
    """
    Generate network activity chart showing simulated network usage.

    Args:
        network_data: Network activity data (not used in current implementation)

    Returns:
        matplotlib.pyplot: Plot object with network activity chart
    """
    # Simulate 24 hours of network activity
    timestamps = [i for i in range(24)]  # 24 hours simulation
    # Simulate activity levels with some variation
    activity_levels = [max(5, 20 + 10 * np.sin(i / 3)) for i in timestamps]

    # Create area chart
    plt.figure(figsize=(10, 6))
    plt.fill_between(timestamps, activity_levels, alpha=0.4, color='#3498db')  # Filled area
    plt.plot(timestamps, activity_levels, linewidth=2, color='#2980b9')  # Line on top

    # Configure chart
    plt.xlabel('Time (Hours)', fontsize=12, fontweight='bold')
    plt.ylabel('Network Activity Level', fontsize=12, fontweight='bold')
    plt.title('P2P Network Activity Over Time', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    return plt


def generate_comparison_chart(analysis_data):
    """
    Generate comparison chart between honest and attacker blocks.

    Args:
        analysis_data (dict): Analysis data from SimBlock simulation

    Returns:
        matplotlib.pyplot: Plot object with comparison chart
    """
    # Check if we have detailed analysis data
    if not analysis_data.get('detailed_analysis'):
        return None

    detailed = analysis_data['detailed_analysis']
    # Get counts of attacker and honest blocks
    attacker_blocks = detailed.get('attacker_blocks_added_count', 0)
    honest_blocks = detailed.get('honest_blocks_added_count', 0)

    # Prepare data for bar chart
    labels = ['Honest Blocks', 'Attacker Blocks']
    values = [honest_blocks, attacker_blocks]
    colors = ['#2ecc71', '#e74c3c']  # Green for honest, red for attacker

    # Create bar chart
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values, color=colors, alpha=0.8)

    # Configure chart
    plt.ylabel('Number of Blocks', fontsize=12, fontweight='bold')
    plt.title('Honest vs Attacker Block Distribution', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 str(value), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return plt


def generate_simblock_metrics_chart(analysis_data):
    """
    Generate bar chart for SimBlock simulation metrics.

    Args:
        analysis_data (dict): Analysis data from SimBlock simulation

    Returns:
        matplotlib.pyplot: Plot object with SimBlock metrics chart
    """
    # Check if we have analysis data
    if not analysis_data:
        return None

    # Define metrics to display
    metrics = [
        ('Attack Probability', analysis_data.get('attack_probability', 0) * 100, '%'),
        ('Total Blocks', analysis_data.get('total_blocks', 0), ''),
        ('Avg Block Time', analysis_data.get('avg_block_time', 0), 'ms'),
        ('Forks Detected', analysis_data.get('forks_detected', 0), ''),
        ('Total Miners', analysis_data.get('total_miners', 0), '')
    ]

    # Filter out invalid metrics (None values or zeros where inappropriate)
    valid_metrics = [m for m in metrics if m[1] is not None and not (
            isinstance(m[1], float) and m[1] == 0 and m[0] != 'Attack Probability')]

    # If no valid metrics, return None
    if not valid_metrics:
        return None

    # Extract data for chart
    labels = [m[0] for m in valid_metrics]
    values = [m[1] for m in valid_metrics]
    units = [m[2] for m in valid_metrics]
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    # Create bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, values, color=colors[:len(valid_metrics)])

    # Configure chart
    plt.xlabel('Simulation Metrics', fontsize=12, fontweight='bold')
    plt.ylabel('Values', fontsize=12, fontweight='bold')
    plt.title('SimBlock Simulation Metrics', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels
    plt.grid(axis='y', alpha=0.3)

    # Add value labels on bars with appropriate formatting
    for i, (bar, value, unit) in enumerate(zip(bars, values, units)):
        if labels[i] == 'Attack Probability':
            label_text = f'{value:.1f}{unit}'
        elif labels[i] == 'Avg Block Time':
            label_text = f'{value:.2f}{unit}'
        else:
            label_text = f'{value}{unit}'

        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                 label_text, ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return plt


# --------------------------------------------------------
# SimBlock Functions
# --------------------------------------------------------

def run_simblock():
    """
    Run the SimBlock simulation to analyze blockchain behavior.

    Returns:
        tuple: (success_status, error_message)
    """
    try:
        # Set up file paths for SimBlock execution
        script_dir = os.path.dirname(os.path.abspath(__file__))
        simblock_cwd = os.path.abspath(os.path.join(script_dir, 'simblock', 'simulator'))
        simblock_jar = os.path.join(simblock_cwd, "build", "libs", "simulator.jar")
        conf_dir = os.path.join(simblock_cwd, "conf")
        output_dir = os.path.join(simblock_cwd, "output")
        target_output = os.path.join(script_dir, "blockchain", "simblock_output")

        # Create necessary directories
        os.makedirs(output_dir, exist_ok=True)

        # Set up Java classpath
        classpath = f"{simblock_jar}{os.pathsep}{conf_dir}"

        # Run SimBlock Java simulation
        subprocess.run(
            ["java", "-cp", classpath, "simblock.simulator.Main"],
            cwd=simblock_cwd,
            check=True,
            capture_output=True,
            text=True
        )

        # Copy simulation results to our application directory
        if os.path.exists(target_output):
            shutil.rmtree(target_output)
        shutil.copytree(output_dir, target_output)

        return True, None

    except Exception as e:
        return False, str(e)


def analyze_simblock_results(simblock_output_path):
    """
    Analyze results from SimBlock simulation.

    Args:
        simblock_output_path (str): Path to SimBlock output directory

    Returns:
        dict: Analysis results including attack success, block statistics, etc.
    """
    results = {}
    try:
        # Define required file paths
        output_json_file = os.path.join(simblock_output_path, 'output.json')
        block_list_file = os.path.join(simblock_output_path, 'blockList.txt')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        nodes_json_file = os.path.join(script_dir, 'simblock', 'simulator', 'conf', 'nodes.json')

        # Check if all required files exist
        if not all(os.path.exists(f) for f in [output_json_file, block_list_file, nodes_json_file]):
            return {"error": "Required simulation files missing."}

        # Load node configuration to identify attacker
        with open(nodes_json_file) as f:
            nodes_config = json.load(f)

        # Find attacker node ID
        attacker_id = next((n['id'] for n in nodes_config['nodes'] if n.get('type') == 'attacker'), -1)
        if attacker_id == -1:
            return {"error": "No attacker node found."}

        # Track all blocks and identify attacker blocks
        all_blocks = {}
        attacker_blocks = set()
        timestamps = []

        # Parse simulation events from JSON
        with open(output_json_file) as f:
            events = json.load(f)

        for e in events:
            if e.get('kind') == 'add-block':
                try:
                    miner = int(e['content']['node-id'])
                    block = int(e['content']['block-id'])
                    ts = int(e['content']['timestamp'])
                except Exception:
                    continue

                all_blocks[block] = miner
                timestamps.append(ts)
                if miner == attacker_id:
                    attacker_blocks.add(block)

        # Identify blocks that made it to the main chain
        on_chain_blocks = set()
        with open(block_list_file) as f:
            for line in f:
                if "OnChain" in line:
                    try:
                        on_chain_blocks.add(int(line.split(':')[1].strip()))
                    except Exception:
                        continue

        # Calculate attack success (attacker blocks that are on main chain)
        success_blocks = attacker_blocks.intersection(on_chain_blocks)
        results['attack_successful'] = bool(success_blocks)
        results['attack_conclusion'] = "Attack Successful!" if success_blocks else "Attack Failed."

        # Calculate various statistics
        results['total_blocks'] = len(all_blocks)

        # Calculate average block time from timestamps
        if len(timestamps) > 1:
            intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:]) if 0 < (t2 - t1) < 50000]
            if intervals:
                results['avg_block_time'] = mean(intervals)

        # Calculate forks (blocks not on main chain)
        results['forks_detected'] = max(0, len(all_blocks) - len(on_chain_blocks))

        # Count blocks by type (attacker vs honest)
        attacker_count = len(attacker_blocks)
        honest_count = max(0, len(all_blocks) - attacker_count)
        results['detailed_analysis'] = {
            "attacker_blocks_added_count": attacker_count,
            "honest_blocks_added_count": honest_count
        }

        # Calculate attack probability
        total_for_prob = attacker_count + honest_count
        results['attack_probability'] = attacker_count / total_for_prob if total_for_prob > 0 else 0.0

        # Count unique miners
        results['total_miners'] = len(set(all_blocks.values()))

        # Prepare chart data for frontend visualization
        results['chart_data'] = {
            'labels': ['Attack Probability', 'Total Blocks', 'Avg Block Time', 'Forks Detected', 'Total Miners'],
            'values': [
                results.get('attack_probability', 0) * 100,
                results.get('total_blocks', 0),
                results.get('avg_block_time', 0),
                results.get('forks_detected', 0),
                results.get('total_miners', 0)
            ],
            'colors': ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        }

    except Exception as e:
        results['error'] = str(e)

    return results


# --------------------------------------------------------
# PDF Helper Functions
# --------------------------------------------------------

def add_table(pdf, title, data_dict):
    """
    Add a table to PDF report.

    Args:
        pdf (FPDF): PDF object
        title (str): Table title
        data_dict (dict): Data to display in table
    """
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("helvetica", "", 10)

    # Calculate column widths
    col_width_key = pdf.w / 3.5
    col_width_val = pdf.w / 2.2

    # Add table headers
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(col_width_key, 8, "Key", border=1, align="C")
    pdf.cell(col_width_val, 8, "Value", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Add table rows
    pdf.set_font("helvetica", "", 9)
    for key, value in data_dict.items():
        # Add new page if we're near the bottom
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()

        display_value = str(value)
        # Truncate long values
        if len(display_value) > 40:
            display_value = display_value[:37] + "..."

        pdf.cell(col_width_key, 7, str(key), border=1, align="L")
        pdf.cell(col_width_val, 7, display_value, border=1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


class MyFPDF(FPDF):
    """
    Custom PDF class with custom header and footer for blockchain reports.
    """

    def header(self):
        """Create custom header with logos and project information."""
        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "web", "static", "vu_logo.png")
        author_pic = os.path.join(script_dir, "web", "static", "student_pic.png")

        # Add university logo
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 10, 20)

        # Add author photo
        if os.path.exists(author_pic):
            self.image(author_pic, self.w - 35, 5, 25)

        # Add title and project information
        self.set_font("helvetica", "B", 14)
        self.set_xy(0, 10)
        self.cell(0, 6, "Anomaly Detection System in Blockchain", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("helvetica", "", 12)
        self.cell(0, 6, "Prototype: Double Spending Attack Simulation", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("helvetica", "", 9)

        # Add instructor and author information
        self.set_xy(10, 35)
        self.multi_cell(80, 5, "Project Instructor: Fouzia Jumani\nSkype: fouziajumani\nEmail: fouziajumani@vu.edu.pk")
        self.set_xy(self.w - 75, 35)
        self.multi_cell(70, 5,
                        "Project Author: Eng. Muhammad Imtiaz Shaffi\nVU ID: BC220200917\nEmail: bc220200917mis@vu.edu.pk")

        # Add separator line
        self.set_line_width(0.4)
        self.line(10, 60, self.w - 10, 60)
        self.set_y(70)

    def footer(self):
        """Create custom footer with copyright information."""
        self.set_line_width(0.4)
        self.line(10, self.h - 15, self.w - 10, self.h - 15)
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, "© 2025 This project is developed under the supervision of Virtual University of Pakistan",
                  align="C")


# --------------------------------------------------------
# API Endpoints for Chart Data
# --------------------------------------------------------

@app.route('/api/charts/blockchain-growth', methods=['GET'])
def get_blockchain_growth_chart():
    """
    API endpoint to get blockchain growth chart data.

    Returns:
        JSON: Chart data for blockchain growth visualization
    """
    # Get current blockchain data
    chain_data = blockchain_instance.to_dict()

    # Check if we have chain data
    if not chain_data.get("chain"):
        return jsonify({"error": "No blockchain data available"}), 400

    # Prepare data for chart
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


@app.route('/api/charts/balance-distribution', methods=['GET'])
def get_balance_distribution_chart():
    """
    API endpoint to get balance distribution chart data.

    Returns:
        JSON: Chart data for balance distribution visualization
    """
    # Get current wallet balances
    balances = blockchain_instance.get_balances()

    # Only include positive balances for pie chart
    positive_balances = {k: v for k, v in balances.items() if v > 0}
    if not positive_balances:
        return jsonify({"error": "No positive balance data available"}), 400

    return jsonify({
        "labels": list(positive_balances.keys()),
        "datasets": [{
            "data": list(positive_balances.values()),
            "backgroundColor": [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
            ]
        }]
    })


@app.route('/api/charts/mining-analysis', methods=['GET'])
def get_mining_analysis_chart():
    """
    API endpoint to get mining analysis chart data.

    Returns:
        JSON: Chart data for mining analysis visualization
    """
    # Get current blockchain data
    chain_data = blockchain_instance.to_dict()

    # Check if we have sufficient data
    if len(chain_data.get("chain", [])) < 2:
        return jsonify({"error": "Insufficient blockchain data"}), 400

    blocks = chain_data["chain"]
    block_indices = [b['index'] for b in blocks]
    # Simulate mining times (in real system this would be actual times)
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


@app.route('/api/charts/network-activity', methods=['GET'])
def get_network_activity_chart():
    """
    API endpoint to get network activity chart data.

    Returns:
        JSON: Chart data for network activity visualization
    """
    # Simulate 24 hours of network activity
    timestamps = [f"Hour {i}" for i in range(24)]
    activity_levels = [max(5, 20 + 10 * np.sin(i / 3)) for i in range(24)]

    return jsonify({
        "labels": timestamps,
        "datasets": [{
            "label": "Network Activity Level",
            "data": activity_levels,
            "borderColor": "#3498db",
            "backgroundColor": "rgba(52, 152, 219, 0.3)",
            "fill": True
        }]
    })


# --------------------------------------------------------
# Enhanced PDF Report Generation (FIXED)
# --------------------------------------------------------

@app.route('/api/report/pdf', methods=['GET'])
def generate_pdf_report_route():
    """
    Generate comprehensive PDF report with multiple charts and analytics.

    Returns:
        PDF file: Comprehensive blockchain report as PDF download
    """
    try:
        # Set up reports directory
        script_dir = os.path.dirname(__file__)
        reports_dir = os.path.join(script_dir, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        # Get all required data for the report
        simblock_output_path = os.path.join(script_dir, "blockchain", "simblock_output")
        analysis = analyze_simblock_results(simblock_output_path)
        chain_data = blockchain_instance.to_dict()
        balances = blockchain_instance.get_balances()

        # Initialize PDF with custom class
        pdf = MyFPDF()
        pdf.add_page()

        # 1. Title Page
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 12, "Comprehensive Blockchain Analytics Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        pdf.set_font("helvetica", "", 12)
        pdf.multi_cell(0, 8,
                       "This report contains detailed analytics and visualizations of the blockchain network, including transaction patterns, mining statistics, and double-spending attack simulations.")
        pdf.ln(15)

        # 2. Blockchain Growth Chart
        growth_chart = generate_blockchain_growth_chart(chain_data)
        if growth_chart:
            chart_path = os.path.join(reports_dir, "blockchain_growth.png")
            growth_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "1. Blockchain Growth Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 3. Balance Distribution Chart (FIXED)
        pdf.add_page()
        balance_chart = generate_balance_distribution_chart(balances)
        if balance_chart:
            chart_path = os.path.join(reports_dir, "balance_distribution.png")
            balance_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "2. Wallet Balance Distribution", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 4. Mining Analysis Chart
        mining_chart = generate_mining_analysis_chart(chain_data)
        if mining_chart:
            chart_path = os.path.join(reports_dir, "mining_analysis.png")
            mining_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "3. Mining Time Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 5. SimBlock Metrics Chart
        pdf.add_page()
        simblock_chart = generate_simblock_metrics_chart(analysis)
        if simblock_chart:
            chart_path = os.path.join(reports_dir, "simblock_metrics.png")
            simblock_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "4. SimBlock Simulation Metrics", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 6. Comparison Chart
        comparison_chart = generate_comparison_chart(analysis)
        if comparison_chart:
            chart_path = os.path.join(reports_dir, "comparison_analysis.png")
            comparison_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "5. Honest vs Attacker Blocks", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 7. Network Activity Chart
        pdf.add_page()
        network_chart = generate_network_activity_chart(None)
        if network_chart:
            chart_path = os.path.join(reports_dir, "network_activity.png")
            network_chart.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()

            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "6. Network Activity Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.image(chart_path, x=10, w=pdf.w - 20)
            pdf.ln(10)

        # 8. Double Spending Attack Results
        if 'last_attack' in RECENT_ATTACK_RESULTS:
            pdf.add_page()
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 12, "Double Spending Attack Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(5)

            attack_data = RECENT_ATTACK_RESULTS['last_attack']
            attack_result = attack_data['result']

            # Attack Configuration
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Attack Configuration", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "", 10)

            config_info = {
                "Attacker": attack_data.get('attacker', 'Unknown'),
                "Private Blocks Mined": attack_data.get('blocks', 0),
                "Amount": f"{attack_data.get('amount', 0)} coins",
                "Hash Power": f"{attack_data.get('config', {}).get('attackerHashPower', 0)}%",
                "Success Probability": f"{attack_data.get('config', {}).get('successProbability', 0) * 100}%"
            }

            for key, value in config_info.items():
                pdf.cell(60, 8, f"{key}:", border=0, align="L")
                pdf.cell(0, 8, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Attack Results
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 12)
            pdf.cell(0, 10, "Attack Results", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("helvetica", "", 10)

            # Determine attack success from results
            attack_successful = False
            for step in attack_result.get('steps', []):
                if step.get('action') == 'broadcast_private_blocks':
                    if any(r.get('ok') for r in step.get('results', [])):
                        attack_successful = True
                        break

            pdf.cell(0, 8, f"Attack Outcome: {'SUCCESSFUL' if attack_successful else 'FAILED'}",
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # 9. Detailed Statistics
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 12, "Detailed Statistics", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        # Blockchain statistics
        blockchain_stats = {
            "Total Blocks": len(chain_data.get("chain", [])),
            "Total Transactions": sum(len(b["transactions"]) for b in chain_data.get("chain", [])),
            "Pending Transactions": len(chain_data.get("mempool", [])),
            "Current Difficulty": chain_data.get("difficulty", "N/A"),
            "Connected Peers": len(PEERS)
        }
        add_table(pdf, "Blockchain Statistics", blockchain_stats)

        # SimBlock statistics
        if "error" not in analysis:
            simblock_stats = {
                "Attack Conclusion": analysis.get("attack_conclusion", "N/A"),
                "Attack Successful": "Yes" if analysis.get("attack_successful") else "No",
                "Attack Probability": f"{analysis.get('attack_probability', 0.0) * 100:.2f}%",
                "Total Blocks": analysis.get("total_blocks", "N/A"),
                "Avg Block Time": f"{analysis.get('avg_block_time', 0):.2f} ms" if analysis.get(
                    'avg_block_time') else "N/A",
                "Forks Detected": analysis.get("forks_detected", "N/A"),
                "Total Miners": analysis.get("total_miners", "N/A")
            }
            add_table(pdf, "SimBlock Simulation Summary", simblock_stats)

        # Save and return PDF
        report_path = os.path.join(reports_dir, "Comprehensive-Blockchain-Report.pdf")
        pdf.output(report_path)

        return send_file(report_path, mimetype="application/pdf", as_attachment=True,
                         download_name="Comprehensive-Blockchain-Report.pdf")

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


# --------------------------------------------------------
# Existing Routes (unchanged)
# --------------------------------------------------------

@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/attack/run', methods=['POST'])
def api_run_attack():
    """
    API endpoint to run a double-spending attack simulation.

    Returns:
        JSON: Detailed attack results
    """
    data = request.get_json() or {}
    node = data.get("node", NODE_ADDRESS)
    peers = data.get("peers", list(PEERS) or [node])
    attacker = data.get("attacker", "Attacker")
    blocks = int(data.get("blocks", 1))
    amount = float(data.get("amount", 5.0))

    frontend_config = data.get("frontend_config", {})

    # Store attack results for PDF reporting
    RECENT_ATTACK_RESULTS['last_attack'] = {
        'result': {},
        'config': frontend_config,
        'timestamp': time.time(),
        'attacker': attacker,
        'blocks': blocks,
        'amount': amount
    }

    # Pass frontend_config properly to the attack function
    result = run_attack(
        node_url=node,
        peers=peers,
        attacker_addr=attacker,
        blocks=blocks,
        amount=amount,
        frontend_config=frontend_config  # This is important
    )

    # Update with actual result
    RECENT_ATTACK_RESULTS['last_attack']['result'] = result

    return jsonify(result), 200


@app.route('/peers', methods=['POST'])
def add_peer():
    """
    API endpoint to add a new peer to the network.

    Returns:
        JSON: Result of peer addition
    """
    data = request.get_json()
    peer_address = data.get('address')
    if not peer_address:
        return jsonify({"error": "Invalid peer address"}), 400
    PEERS.add(peer_address)
    return jsonify({
        "message": "Peer added successfully",
        "peers": list(PEERS)
    })


@app.route('/blocks', methods=['GET'])
def get_blocks():
    """
    API endpoint to get all blocks in the blockchain.

    Returns:
        JSON: Complete blockchain data
    """
    chain_data = [block.to_dict() for block in blockchain_instance.chain]
    return jsonify({
        "chain": chain_data,
        "length": len(chain_data)
    })


@app.route('/tx/broadcast', methods=['POST'])
def broadcast_transaction_endpoint():
    """
    API endpoint to broadcast a transaction to the network.

    Returns:
        JSON: Transaction broadcast result
    """
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


@app.route('/blocks/receive', methods=['POST'])
def receive_block():
    """
    API endpoint to receive blocks from peers.

    Returns:
        JSON: Block reception result
    """
    block_data = request.get_json()
    try:
        block = Block.from_dict(block_data)
    except Exception as e:
        return jsonify({"error": f"Invalid block data: {e}"}), 400

    if blockchain_instance.add_new_block(block):
        return jsonify({"message": "Block received and added to chain"}), 200

    return jsonify({"error": "Block rejected, not a valid PoW"}), 400


@app.route('/consensus', methods=['GET'])
def resolve_conflicts():
    """
    API endpoint to resolve blockchain conflicts with peers.

    Returns:
        JSON: Consensus resolution result
    """
    replaced = blockchain_instance.resolve_conflicts()
    if replaced:
        return jsonify({
            "message": "Our chain was replaced by a longer one.",
            "new_chain": blockchain_instance.to_dict()['chain']
        }), 200
    else:
        return jsonify({
            "message": "Our chain is authoritative.",
            "chain": blockchain_instance.to_dict()['chain']
        }), 200


@app.route("/api/mine", methods=["POST"])
def mine_block():
    """
    API endpoint to mine a new block.

    Returns:
        JSON: Mining result with new block information
    """
    try:
        data = request.json or {}
        miner = data.get("miner", "DefaultMiner")

        # Mine the block with pending transactions
        block = blockchain_instance.mine_pending_transactions(miner)

        # Broadcast the new block to all peers
        for peer in PEERS:
            try:
                requests.post(f"{peer}/blocks/receive", json=block.to_dict())
            except Exception as e:
                print(f"Failed to broadcast block to {peer}: {e}")

        return jsonify({"status": "ok", "block": block.to_dict(), "chain_length": len(blockchain_instance.chain)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/tx/new", methods=["POST"])
def new_transaction():
    """
    API endpoint to create a new transaction.

    Returns:
        JSON: Transaction creation result
    """
    try:
        tx_data = request.get_json()
        sender = tx_data.get("sender")
        receiver = tx_data.get("receiver")
        amount = float(tx_data.get("amount"))

        # Create new transaction
        txid = blockchain_instance.new_transaction(sender, receiver, amount)

        # Prepare transaction for broadcasting
        tx_to_broadcast = {
            "id": txid,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": int(time.time())
        }

        # Broadcast transaction to all peers
        for peer in PEERS:
            try:
                requests.post(f"{peer}/tx/broadcast", json=tx_to_broadcast)
            except Exception as e:
                print(f"Failed to broadcast transaction to {peer}: {e}")

        return jsonify({"status": "ok", "txid": txid, "mempool_size": len(blockchain_instance.mempool)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/chain", methods=["GET"])
def get_chain():
    """
    API endpoint to get the complete blockchain data.

    Returns:
        JSON: Complete blockchain information
    """
    chain_dict = blockchain_instance.to_dict()
    # Prepare data for charts
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


@app.route("/api/balances", methods=["GET"])
def get_balances():
    """
    API endpoint to get current wallet balances.

    Returns:
        JSON: Wallet balances
    """
    return jsonify(blockchain_instance.get_balances())


@app.route('/api/analyze', methods=['GET'])
def get_analysis():
    """
    API endpoint to run SimBlock analysis.

    Returns:
        JSON: SimBlock analysis results
    """
    success, error = run_simblock()
    if not success:
        return jsonify({"error": error}), 500
    analysis = analyze_simblock_results(os.path.join(os.path.dirname(__file__), "blockchain", "simblock_output"))
    return jsonify(analysis)


if __name__ == '__main__':
    """
    Main entry point for the Flask application.

    Supports custom port specification via command line arguments.
    """
    # Command line se port lelo (Get port from command line)
    if len(sys.argv) > 1 and sys.argv[1] == '--port':
        port = int(sys.argv[2])
    else:
        port = 5000

    # Start the Flask application
    app.run(host='0.0.0.0', port=port, debug=True)