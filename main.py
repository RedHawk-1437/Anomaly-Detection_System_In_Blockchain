# main.py
# This is the main file for the Flask web application.
# It connects all the parts of the project: the blockchain, the attacker simulation,
# peer-to-peer communication, and the web interface for reporting.

import os
import json
import subprocess
import shutil
import requests
from statistics import mean
from flask import Flask, jsonify, render_template, send_file, request
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from blockchain.attacker import run_attack
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Project imports ---
# Importing the main components of our blockchain system
from blockchain.blockchain import Blockchain
from blockchain.block import Block
from blockchain.transaction import Transaction

# Initialize Flask app
app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

# --------------------------------------------------------
# Global Variables for the Blockchain System
# --------------------------------------------------------
# This is our main blockchain instance that will run on this node.
blockchain_instance = Blockchain(difficulty=3, reward=1.0)
# A set to keep track of all other peer nodes in the network.
PEERS = set()
# The address of this node. It's read from an environment variable or defaults to a local address.
NODE_ADDRESS = os.environ.get("NODE_ADDRESS", "http://127.0.0.1:5000")


# --------------------------------------------------------
# SimBlock Runner & Analyzer
# These functions handle running the external SimBlock simulator and analyzing its results.
# --------------------------------------------------------
def run_simblock():
    # This function executes the SimBlock Java simulator.
    # SimBlock is a tool used to simulate blockchain network behavior.
    try:
        # Get the current directory to find the SimBlock simulator files.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        simblock_cwd = os.path.abspath(os.path.join(script_dir, 'simblock', 'simulator'))
        simblock_jar = os.path.join(simblock_cwd, "build", "libs", "simulator.jar")
        conf_dir = os.path.join(simblock_cwd, "conf")
        output_dir = os.path.join(simblock_cwd, "output")
        target_output = os.path.join(script_dir, "blockchain", "simblock_output")

        # Make sure the output directory exists.
        os.makedirs(output_dir, exist_ok=True)
        classpath = f"{simblock_jar}{os.pathsep}{conf_dir}"

        # Run the Java command to start the simulation.
        # This will create simulation data files.
        subprocess.run(
            ["java", "-cp", classpath, "simblock.simulator.Main"],
            cwd=simblock_cwd,
            check=True,
            capture_output=True,
            text=True
        )

        # Clean up previous simulation output and copy the new one.
        if os.path.exists(target_output):
            shutil.rmtree(target_output)
        shutil.copytree(output_dir, target_output)

        # If everything works, return True.
        return True, None
    except Exception as e:
        # If there's an error, return False and the error message.
        return False, str(e)


def analyze_simblock_results(simblock_output_path):
    # This function reads the files created by SimBlock and analyzes the results
    # to determine if the double-spending attack was successful.
    results = {}
    try:
        # Define paths to the different output files.
        output_json_file = os.path.join(simblock_output_path, 'output.json')
        block_list_file = os.path.join(simblock_output_path, 'blockList.txt')
        script_dir = os.path.dirname(os.path.abspath(__file__))
        nodes_json_file = os.path.join(script_dir, 'simblock', 'simulator', 'conf', 'nodes.json')

        # Check if all required files exist.
        if not all(os.path.exists(f) for f in [output_json_file, block_list_file, nodes_json_file]):
            return {"error": "Required simulation files missing."}

        # Read the nodes configuration to find the attacker's ID.
        with open(nodes_json_file) as f:
            nodes_config = json.load(f)
        attacker_id = next((n['id'] for n in nodes_config['nodes'] if n.get('type') == 'attacker'), -1)
        if attacker_id == -1:
            return {"error": "No attacker node found."}

        all_blocks = {}
        attacker_blocks = set()
        timestamps = []

        # Read the simulation events to track all mined blocks and who mined them.
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
                # Keep track of blocks mined by the attacker.
                if miner == attacker_id:
                    attacker_blocks.add(block)

        on_chain_blocks = set()
        # Read the block list to find which blocks made it onto the main chain.
        with open(block_list_file) as f:
            for line in f:
                if "OnChain" in line:
                    try:
                        on_chain_blocks.add(int(line.split(':')[1].strip()))
                    except Exception:
                        continue

        # Determine if the attack was successful by checking if any attacker blocks are on the main chain.
        success_blocks = attacker_blocks.intersection(on_chain_blocks)
        results['attack_successful'] = bool(success_blocks)
        results['attack_conclusion'] = "Attack Successful!" if success_blocks else "Attack Failed."

        # Calculate other metrics like total blocks, block time, and forks.
        results['total_blocks'] = len(all_blocks)
        if len(timestamps) > 1:
            intervals = [t2 - t1 for t1, t2 in zip(timestamps[:-1], timestamps[1:]) if 0 < (t2 - t1) < 50000]
            if intervals:
                results['avg_block_time'] = mean(intervals)
        results['forks_detected'] = max(0, len(all_blocks) - len(on_chain_blocks))

        # Count honest vs. attacker blocks.
        attacker_count = len(attacker_blocks)
        honest_count = max(0, len(all_blocks) - attacker_count)
        results['detailed_analysis'] = {
            "attacker_blocks_added_count": attacker_count,
            "honest_blocks_added_count": honest_count
        }

        # Calculate the probability of the attack succeeding.
        total_for_prob = attacker_count + honest_count
        results['attack_probability'] = attacker_count / total_for_prob if total_for_prob > 0 else 0.0

        # Count the total number of unique miners.
        results['total_miners'] = len(set(all_blocks.values()))
    except Exception as e:
        # Return an error if something goes wrong during analysis.
        results['error'] = str(e)
    return results


# --------------------------------------------------------
# FPDF & Table helper functions
# These functions help in generating a PDF report.
# --------------------------------------------------------
def add_table(pdf, title, data_dict):
    # This function adds a formatted table to the PDF document.
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.set_font("helvetica", "", 10)

    # Set up column widths for the table.
    col_width_key = pdf.w / 3.5
    col_width_val = pdf.w / 2.2

    # Add the table header.
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(col_width_key, 8, "Key", border=1, align="C")
    pdf.cell(col_width_val, 8, "Value", border=1, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Add the data rows to the table.
    pdf.set_font("helvetica", "", 9)
    for key, value in data_dict.items():
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()
        display_value = str(value)
        if len(display_value) > 40:
            display_value = display_value[:37] + "..."
        pdf.cell(col_width_key, 7, str(key), border=1, align="L")
        pdf.cell(col_width_val, 7, display_value, border=1, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)


class MyFPDF(FPDF):
    # This class extends the FPDF library to create a custom PDF layout.
    def header(self):
        # This function defines the header for each page of the PDF.
        script_dir = os.path.dirname(__file__)
        logo_path = os.path.join(script_dir, "web", "static", "vu_logo.png")
        author_pic = os.path.join(script_dir, "web", "static", "student_pic.png")

        # Add a logo and an author picture if they exist.
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 10, 20)
        if os.path.exists(author_pic):
            self.image(author_pic, self.w - 35, 5, 25)

        # Add the main title and subtitles.
        self.set_font("helvetica", "B", 14)
        self.set_xy(0, 10)
        self.cell(0, 6, "Anomaly Detection System in Blockchain", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("helvetica", "", 12)
        self.cell(0, 6, "Prototype: Double Spending Attack Simulation", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("helvetica", "", 9)

        # Add project and author details.
        self.set_xy(10, 35)
        self.multi_cell(80, 5, "Project Instructor: Fouzia Jumani\nSkype: fouziajumani\nEmail: fouziajumani@vu.edu.pk")
        self.set_xy(self.w - 75, 35)
        self.multi_cell(70, 5,
                        "Project Author: Eng. Muhammad Imtiaz Shaffi\nVU ID: BC220200917\nEmail: bc220200917mis@vu.edu.pk")

        # Draw a line and set the starting position for the content.
        self.set_line_width(0.4)
        self.line(10, 60, self.w - 10, 60)
        self.set_y(70)

    def footer(self):
        # This function defines the footer for each page, including copyright information.
        self.set_line_width(0.4)
        self.line(10, self.h - 15, self.w - 10, self.h - 15)
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, "© 2025 This project is developed under the supervision of Virtual University of Pakistan",
                  align="C")


# --------------------------------------------------------
# Web Routes
# These are the URLs (endpoints) that the Flask app will respond to.
# --------------------------------------------------------
@app.route('/')
def index():
    # This route serves the main homepage of the web application.
    return render_template('index.html')


# --------------------------------------------------------
# Attacker Routes
# --------------------------------------------------------
@app.route('/api/attack/run', methods=['POST'])
def api_run_attack():
    # This endpoint is used to trigger a double-spending attack simulation.
    data = request.get_json() or {}
    node = data.get("node", NODE_ADDRESS)
    peers = data.get("peers", list(PEERS) or [node])
    attacker = data.get("attacker", "Attacker")
    blocks = int(data.get("blocks", 1))
    amount = float(data.get("amount", 5.0))
    # Call the `run_attack` function from the attacker module to start the simulation.
    result = run_attack(node_url=node, peers=peers, attacker_addr=attacker, blocks=blocks, amount=amount)
    return jsonify(result), 200


# --------------------------------------------------------
# P2P Endpoints
# These endpoints handle communication between different nodes in the network.
# --------------------------------------------------------
@app.route('/peers', methods=['POST'])
def add_peer():
    # This endpoint allows a node to add a new peer to its list of connected nodes.
    data = request.get_json()
    peer_address = data.get('address')
    if not peer_address:
        return jsonify({"error": "Invalid peer address"}), 400
    PEERS.add(peer_address)  # Add the new peer to the set.
    return jsonify({
        "message": "Peer added successfully",
        "peers": list(PEERS)
    })


@app.route('/blocks', methods=['GET'])
def get_blocks():
    # This endpoint returns the entire blockchain of this node.
    chain_data = [block.to_dict() for block in blockchain_instance.chain]
    return jsonify({
        "chain": chain_data,
        "length": len(chain_data)
    })


@app.route('/tx/broadcast', methods=['POST'])
def broadcast_transaction_endpoint():
    # This endpoint is used to receive a transaction broadcast from another node.
    tx_data = request.get_json()
    new_tx = Transaction(
        sender=tx_data['sender'],
        receiver=tx_data['receiver'],
        amount=tx_data['amount'],
        txid=tx_data['id'],
        timestamp=tx_data['timestamp']
    )
    # Add the received transaction to the local mempool.
    result = blockchain_instance.new_transaction_from_dict(new_tx.to_dict())
    return jsonify(result), 201


@app.route('/blocks/receive', methods=['POST'])
def receive_block():
    # This endpoint is used to receive a new block from another node.
    block_data = request.get_json()
    try:
        # Create a Block object from the received data.
        block = Block.from_dict(block_data)
    except Exception as e:
        return jsonify({"error": f"Invalid block data: {e}"}), 400

    # Try to add the new block to the local chain.
    if blockchain_instance.add_new_block(block):
        return jsonify({"message": "Block received and added to chain"}), 200

    # If the block is not valid, reject it.
    return jsonify({"error": "Block rejected, not a valid PoW"}), 400


@app.route('/consensus', methods=['GET'])
def resolve_conflicts():
    # This endpoint is used to resolve conflicts with other nodes
    # by checking if a longer chain exists in the network.
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


# --------------------------------------------------------
# API Endpoints
# These endpoints are for interacting with the blockchain from a web client.
# --------------------------------------------------------
@app.route("/api/mine", methods=["POST"])
def mine_block():
    # This endpoint triggers the mining process to create a new block.
    try:
        data = request.json or {}
        miner = data.get("miner", "DefaultMiner")

        # Mine a new block with the pending transactions.
        block = blockchain_instance.mine_pending_transactions(miner)

        # After mining, broadcast the new block to all connected peers.
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
    # This endpoint creates a new transaction and adds it to the mempool.
    try:
        tx_data = request.get_json()
        sender = tx_data.get("sender")
        receiver = tx_data.get("receiver")
        amount = float(tx_data.get("amount"))

        # Add the new transaction to the local mempool.
        txid = blockchain_instance.new_transaction(sender, receiver, amount)

        # Prepare the transaction data to be broadcast to other peers.
        tx_to_broadcast = {
            "id": txid,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "timestamp": int(__import__("time").time())
        }

        # Broadcast the new transaction to all known peers.
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
    # This endpoint returns the full blockchain data and some summary information for charting.
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


@app.route("/api/balances", methods=["GET"])
def get_balances():
    # This endpoint calculates and returns the current balance of all wallets.
    return jsonify(blockchain_instance.get_balances())


@app.route('/api/analyze', methods=['GET'])
def get_analysis():
    # This endpoint runs the SimBlock simulation and returns the analysis results.
    success, error = run_simblock()
    if not success:
        return jsonify({"error": error}), 500
    analysis = analyze_simblock_results(os.path.join(os.path.dirname(__file__), "blockchain", "simblock_output"))
    return jsonify(analysis)


@app.route('/api/report/pdf', methods=['GET'])
def generate_pdf_report_route():
    # This endpoint generates a comprehensive PDF report based on the blockchain data and simulation results.

    # 1. Get simulation analysis and blockchain data.
    script_dir = os.path.dirname(__file__)
    simblock_output_path = os.path.join(script_dir, "blockchain", "simblock_output")
    analysis = analyze_simblock_results(simblock_output_path)
    if "error" in analysis:
        return jsonify({"error": analysis["error"]}), 400
    chain_data = blockchain_instance.to_dict()
    balances = blockchain_instance.get_balances()

    # 2. Initialize the PDF document.
    pdf = MyFPDF()
    pdf.add_page()

    # 3. Add sections to the PDF using helper functions.
    # BALANCES SECTION
    add_table(pdf, "Blockchain Playground - Balances", balances)

    # BLOCKCHAIN SNAPSHOT
    if "chain" in chain_data and chain_data["chain"]:
        chain_info = {}
        max_blocks_to_show = min(3, len(chain_data["chain"]))
        for i, b in enumerate(chain_data["chain"][:max_blocks_to_show]):
            chain_info[f"Block {b['index']} - Hash"] = b["hash"][:20] + "..."
            chain_info[f"Block {b['index']} - PrevHash"] = b["previous_hash"][:20] + "..." if b[
                                                                                                  "previous_hash"] != "0" else "0"
            chain_info[f"Block {b['index']} - Nonce"] = b["nonce"]
            chain_info[f"Block {b['index']} - Transactions"] = len(b["transactions"])
        add_table(pdf, "Blockchain Chain Snapshot (First 3 Blocks)", chain_info)

    # BLOCKCHAIN GROWTH CHART
    if chain_data["chain"]:
        labels = [f"Block {b['index']}" for b in chain_data["chain"]]
        tx_counts = [len(b["transactions"]) for b in chain_data["chain"]]

        if labels and tx_counts:
            plt.figure(figsize=(8, 5))
            bars = plt.bar(labels, tx_counts, color="#2a5298")
            plt.xlabel('Block Numbers', fontsize=12)
            plt.ylabel('Number of Transactions', fontsize=12)
            plt.title('Blockchain Growth - Transactions per Block', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            for bar, count in zip(bars, tx_counts):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                         str(count), ha='center', va='bottom')
            plt.tight_layout()
            chart_path = os.path.join(script_dir, "reports", "chain_chart.png")
            os.makedirs(os.path.join(script_dir, "reports"), exist_ok=True)
            plt.savefig(chart_path, dpi=100, bbox_inches='tight')
            plt.close()
            if os.path.exists(chart_path):
                pdf.ln(10)
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 10, "Blockchain Growth Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.image(chart_path, x=10, w=pdf.w - 20)
                pdf.ln(10)

    # RECENT TRANSACTIONS
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Recent Transactions", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 11)
    if chain_data["chain"]:
        recent_txs = []
        for block in chain_data["chain"]:
            for tx in block["transactions"]:
                if tx["sender"] != "SYSTEM":
                    recent_txs.append(f"{tx['sender']} -> {tx['receiver']}: {tx['amount']} coins")
        if recent_txs:
            for tx in recent_txs[-10:]:
                pdf.cell(0, 8, f"- {tx}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.cell(0, 8, "No recent transactions", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(0, 8, "No transactions found", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # MINING INFORMATION
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Mining Information", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 11)
    mining_info = {
        "Total Blocks": len(chain_data["chain"]),
        "Pending Transactions": len(chain_data["mempool"]),
        "Current Difficulty": chain_data["difficulty"],
        "Miner Reward": "1.0 coins"
    }
    for key, value in mining_info.items():
        pdf.cell(90, 8, f"{key}:", border=0, align="L")
        pdf.cell(0, 8, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # P2P NETWORK INFORMATION
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "P2P Network Status", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 11)
    network_info = {
        "Connected Peers": len(PEERS),
        "Node Address": NODE_ADDRESS,
        "Network Status": "Active" if len(PEERS) > 0 else "Standalone"
    }
    for key, value in network_info.items():
        pdf.cell(90, 8, f"{key}:", border=0, align="L")
        pdf.cell(0, 8, str(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # SIMBLOCK SIMULATION SUMMARY
    pdf.add_page()
    simblock_summary = {
        "Attack Conclusion": analysis.get("attack_conclusion", "N/A"),
        "Attack Successful": "Yes" if analysis.get("attack_successful") else "No",
        "Attack Probability": f"{analysis.get('attack_probability', 0.0) * 100:.2f}%",
        "Total Blocks": analysis.get("total_blocks", "N/A"),
        "Avg Block Time": f"{analysis.get('avg_block_time', 0):.2f} ms" if analysis.get('avg_block_time') else "N/A",
        "Forks Detected": analysis.get("forks_detected", "N/A"),
        "Total Miners": analysis.get("total_miners", "N/A")
    }
    add_table(pdf, "SimBlock Simulation Summary", simblock_summary)

    # ATTACK SIMULATION RESULTS
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Attack Simulation Analysis", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 11)
    attack_result = "Successful" if analysis.get("attack_successful") else "Failed"
    pdf.cell(0, 8, f"Double-Spending Attack: {attack_result}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if analysis.get("attack_successful"):
        pdf.cell(0, 8, "The attacker successfully executed a double-spending attack.", new_x=XPos.LMARGIN,
                 new_y=YPos.NEXT)
    else:
        pdf.cell(0, 8, "The attack was detected and prevented by the network.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Add a pie chart to visualize the results.
    if "detailed_analysis" in analysis:
        attacker = analysis['detailed_analysis'].get("attacker_blocks_added_count", 0)
        honest = analysis['detailed_analysis'].get("honest_blocks_added_count", 0)
        if attacker + honest > 0:
            plt.figure(figsize=(5, 5))
            plt.pie([attacker, honest], labels=["Attacker Blocks", "Honest Blocks"],
                    colors=["#e74c3c", "#2ecc71"], autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.tight_layout()
            pie_path = os.path.join(script_dir, "reports", "simblock_pie.png")
            plt.savefig(pie_path, dpi=100, bbox_inches='tight')
            plt.close()
            if os.path.exists(pie_path):
                pdf.ln(10)
                pdf.image(pie_path, x=pdf.w / 4, w=pdf.w / 2.5)
                pdf.ln(5)
                pdf.set_font("helvetica", "", 10)
                pdf.cell(0, 8, f"Attacker Blocks: {attacker} ({attacker / (attacker + honest) * 100:.1f}%)",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(0, 8, f"Honest Blocks: {honest} ({honest / (attacker + honest) * 100:.1f}%)",
                         new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 4. Save and return the PDF file.
    report_path = os.path.join(script_dir, "reports", "Double-Spending-Report.pdf")
    pdf.output(report_path)
    return send_file(report_path, mimetype="application/pdf", as_attachment=True,
                     download_name="Double-Spending-Report.pdf")


if __name__ == '__main__':
    # This block runs the Flask application when the script is executed directly.
    # It starts a local web server that listens for requests.
    app.run(host='0.0.0.0', port=5000, debug=True)