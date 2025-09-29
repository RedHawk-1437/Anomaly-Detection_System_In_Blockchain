# 🚀 Anomaly Detection System in Blockchain - Double Spending Attack Simulation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-brightgreen)
![SimBlock](https://img.shields.io/badge/SimBlock-Integrated-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A comprehensive blockchain prototype with double-spending attack detection and network simulation capabilities**

*BSCS Final Year Project - Virtual University of Pakistan*

</div>

## 📖 Overview

This project implements a complete blockchain ecosystem with advanced anomaly detection capabilities for simulating and analyzing double-spending attacks. It features a custom blockchain implementation, interactive web interface, real-time analytics, and integration with SimBlock for large-scale network analysis.

## ✨ Key Features

### 🔗 Core Blockchain Implementation
- **Custom Blockchain** with Proof-of-Work consensus mechanism
- **Block Management** with index, timestamp, transactions, and cryptographic hashing
- **Transaction System** with validation, mempool management, and digital signatures
- **Mining Operations** with adjustable difficulty and miner rewards

### ⚡ Double-Spending Attack Simulation
- **Configurable Attack Parameters** with success probability controls (1-100%)
- **Hash Power Simulation** with attacker dominance settings
- **Force Controls** for manual success/failure override
- **Private Chain Mining** with secret fork creation and broadcasting
- **Real-time Attack Analytics** with detailed step-by-step logging

### 🌐 P2P Network Simulation
- **Peer-to-Peer Communication** using Flask HTTP endpoints
- **Dynamic Peer Management** with add/remove functionality
- **Consensus Mechanism** implementing longest-chain rule
- **Conflict Resolution** with automatic fork detection and resolution

### 📊 Advanced Visualization & Analytics
- **Interactive Dashboard** with multiple chart types
- **Blockchain Growth Analysis** showing transactions per block
- **Balance Distribution** with interactive pie charts
- **Mining Performance** with time-series analysis
- **Network Activity** monitoring with real-time updates

### 🔬 SimBlock Integration
- **Large-scale Network Simulation** with configurable parameters
- **Attack Probability Analysis** across distributed nodes
- **Performance Metrics** including block propagation times
- **Fork Detection** and chain comparison analytics

### 📄 Comprehensive Reporting
- **PDF Report Generation** with embedded charts and analytics
- **Simulation Summaries** with detailed performance metrics
- **Attack Documentation** with configuration and outcome analysis
- **Academic Documentation** for research and educational purposes

## 🏗️ Project Structure
Anomaly-Detection_System_In_Blockchain/  
│   
├── 📁 blockchain/ # Core blockchain modules  
│ ├── init.py # Package initialization  
│ ├── blockchain.py # Main Blockchain class implementation  
│ ├── block.py # Block structure and operations  
│ ├── transaction.py # Transaction handling and validation  
│ └── attacker.py # Double-spending attack simulation  
│  
├── 📁 web/ # Frontend web application  
│ ├── templates/  
│ │ └── index.html # Main web interface  
│ └── static/  
│ ├── styles.css # Comprehensive CSS styling  
│ ├── app.js # Interactive JavaScript functionality  
│ ├── vu_logo.png # University logo  
│ └── student_pic.png # Author photograph   
│  
├── 📁 simblock/ # Network simulation integration  
│ └── simulator/ # SimBlock installation and configuration  
│  
├── 📁 reports/ # Generated PDF reports and analytics  
├── main.py # Flask application entry point  
├── test_suite.py # Comprehensive testing framework  
├── requirements.txt # Python dependencies  
└── README.md # Project documentation  

text

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Java JDK 8+** (for SimBlock integration)
- **Git** (for SimBlock installation)

### Installation

1. **Clone or Download the Project**
```bash
# If using git
git clone <repository-url>
cd Anomaly-Detection_System_In_Blockchain

# Or extract the project zip file
Install Python Dependencies

bash
pip install -r requirements.txt
Install SimBlock (Optional - for advanced network simulation)

bash
# Clone SimBlock into the project directory
git clone https://github.com/simblock/simblock.git simblock
cd simblock/simulator
./gradlew build
Running the Application
Start the Flask Development Server

bash
python main.py
Access the Web Interface

text
Open http://localhost:5000 in your web browser
For Custom Port (if needed)

bash
python main.py --port 5001
💻 Usage Guide
Basic Blockchain Operations
Create Transactions

Navigate to "Create New Transaction" section

Enter sender address, receiver address, and amount

Click "Submit Transaction" to add to mempool

View transaction ID and mempool status

Mine Blocks

Go to "Mine Pending Transactions" section

Enter miner name (optional)

Click "Mine Block" to create new block

View block details including hash and transaction count

View Blockchain State

Check "Current Balances" for wallet status

Examine "Blockchain Chain" for complete block history

Monitor pending transactions in mempool

Double-Spending Attack Simulation
Configure Attack Parameters

Adjust "Success Probability" slider (1-100%)

Set "Attacker Hash Power" percentage

Use "Force Outcome" buttons for controlled testing:

✅ Force Success: Always succeeds

❌ Force Failure: Always fails

🔄 Random: Uses probability settings

Execute Attack

Enter attacker name and number of blocks to mine

Specify double-spending amount

Click "Run Attack" to start simulation

Monitor real-time attack steps and results

Analyze Results

View attack success/failure status

Examine success rate percentage

Review detailed attack steps and network responses

Network Management
Add Network Peers

Enter peer address (e.g., http://127.0.0.1:5001)

Click "Add Peer" to expand network

View connected peers list

Resolve Conflicts

Click "Run Consensus" to synchronize with network

Monitor chain replacement if longer chain exists

Ensure network-wide consistency

Analytics & Visualization
Access Analytics Dashboard

Click "Show Analytics Dashboard" button

View multiple chart types:

Blockchain Growth Chart

Balance Distribution Pie Chart

Mining Analysis Line Chart

Network Activity Area Chart

Run SimBlock Simulation

Click "Run Simulation" for advanced analysis

View simulation metrics and statistics

Analyze attack probabilities and network behavior

Generate Reports

Click "Download Comprehensive PDF Report"

Receive detailed report with charts and analytics

Use for documentation and academic purposes

🔧 API Endpoints
Core Blockchain Operations
GET /api/chain - Retrieve complete blockchain data

POST /api/tx/new - Create and broadcast new transaction

POST /api/mine - Mine new block with pending transactions

GET /api/balances - Get current wallet balances

Attack Simulation
POST /api/attack/run - Execute double-spending attack simulation

POST /peers - Add new peer to P2P network

GET /consensus - Resolve network conflicts and synchronize chains

Analytics & Visualization
GET /api/charts/blockchain-growth - Blockchain growth chart data

GET /api/charts/balance-distribution - Balance distribution data

GET /api/charts/mining-analysis - Mining performance data

GET /api/charts/network-activity - Network activity data

GET /api/analyze - Run SimBlock simulation analysis

GET /api/report/pdf - Generate comprehensive PDF report

🧪 Testing Framework
The project includes a comprehensive test suite:

bash
python test_suite.py
Test Options:

Quick VIVA Demo - Essential functionality tests

Full Comprehensive Test - All system components

Attack Simulation Demo - Security-focused testing

All Tests - Complete test suite execution

🎯 Educational Value
This project serves as an excellent educational tool for:

Blockchain Fundamentals - Core concepts and implementation

Cryptocurrency Security - Double-spending vulnerability analysis

Distributed Systems - P2P networking and consensus algorithms

Cryptographic Principles - SHA-256 hashing and digital signatures

Data Visualization - Real-time analytics and interactive charts

Software Engineering - Complete project lifecycle implementation

📊 Sample Outputs
Successful Attack Simulation
text
🎯 Double-Spending Attack Results
✅ ATTACK SUCCESSFUL!
• Success Rate: 75.0%
• Blocks Mined: 3
• Network Acceptance: 4/5 peers
• Double-spending achieved!
Simulation Analytics
text
📈 SimBlock Simulation Summary
• Attack Probability: 32.5%
• Total Blocks: 1,247
• Average Block Time: 12.3ms
• Forks Detected: 18
• Total Miners: 156
🤝 Contributing
This project was developed as a BSCS Final Year Project. For academic collaborations or improvements:

Fork the repository

Create a feature branch (git checkout -b feature/improvement)

Commit your changes (git commit -m 'Add improvement')

Push to the branch (git push origin feature/improvement)

Open a Pull Request

📝 License
This project is developed under the academic supervision of Virtual University of Pakistan and is available for educational and research purposes.

👨‍💻 Project Team
Project Supervisor
Dr. Fouzia Jumani

Skype: fouziajumani

Email: fouziajumani@vu.edu.pk

Project Author
Eng. Muhammad Imtiaz Shaffi

VU ID: BC220200917

Email: bc220200917mis@vu.edu.pk

📞 Support
For technical support or questions about this project:

Contact the project author via email

Refer to the comprehensive documentation

Check the testing suite for functionality verification

<div align="center">
Developed as BSCS Final Year Project - Virtual University of Pakistan

"Advancing blockchain security through education and practical implementation"

</div> ```