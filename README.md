# 🚀 Blockchain Anomaly Detection System - Double Spending Attack Simulation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-brightgreen)
![SimBlock](https://img.shields.io/badge/SimBlock-Integrated-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A comprehensive blockchain prototype with double-spending attack detection and 100+ node network simulation**

*Developed under the supervision of Virtual University of Pakistan*

</div>

## 📖 Overview

This project implements a complete blockchain ecosystem with advanced anomaly detection capabilities. It features a custom blockchain implementation, double-spending attack simulation, P2P network functionality, and integration with SimBlock for large-scale network analysis with 100+ nodes.

## ✨ Key Features

### 🔗 Core Blockchain
- **Custom Blockchain Implementation** with Proof-of-Work consensus
- **Transaction Management** with mempool and mining rewards
- **P2P Network** with peer discovery and chain synchronization
- **Balance Management** with real-time wallet tracking

### ⚡ Attack Simulation
- **Double-Spending Attack** simulation with configurable parameters
- **100+ Node Network** with global regional distribution
- **Private Chain Mining** with 6+ attacker nodes
- **Dual Transaction Demonstration** - legitimate + malicious transactions with same timestamp
- **Attack Analytics** with success rate tracking

### 📊 Visualization & Analytics
- **Interactive Charts** for blockchain growth and transaction patterns
- **Balance Distribution** visualization with pie charts
- **Mining Analysis** with time-series data
- **Network Activity** monitoring and simulation
- **Private vs Public Network** visualization

### 🔬 SimBlock Integration
- **Large-scale Network Simulation** with 100+ customizable nodes
- **Global Node Distribution** across multiple regions
- **Attack Probability Analysis** across large networks
- **Performance Metrics** including block times and fork detection
- **Comparative Analysis** between honest and attacker blocks

### 📈 Advanced Reporting System
- **Comprehensive CSV Reports** replacing PDF for deep analysis
- **Blockchain Analysis CSV** - Complete chain data and metrics
- **Attack Analysis CSV** - Detailed attack forensics and results
- **Network Metrics CSV** - Performance and health monitoring
- **Double Spend Analysis CSV** - Transaction conflict detection

## 🏗️ Project Structure
blockchain-anomaly-detection/  
│         
├── 📁 blockchain/ # Core blockchain modules  
│ ├── blockchain.py # Main blockchain class    
│ ├── block.py # Block structure implementation    
│ ├── transaction.py # Transaction handling with double spend detection      
│ ├── attacker.py # Attack simulation logic       
│ └── simblock_integration.py # 100+ node network simulation      
│       
├── 📁 web/ # Frontend application       
│ ├── templates/       
│ │ └── index.html # Main web interface      
│ └── static/       
│ ├── styles.css # Comprehensive styling      
│ ├── app.js # Interactive functionality     
│ └── images/ # Logos and assets      
│        
├── 📁 simblock/ # Network simulation       
│ └── simulator/ # SimBlock with 100+ node configuration       
│     
├── 📁 reports/ # Generated CSV analysis reports      
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

1. **Clone the repository**
```bash
git clone https://github.com/your-username/blockchain-anomaly-detection.git
cd blockchain-anomaly-detection
Install Python dependencies

bash
pip install -r requirements.txt
Install SimBlock (Required for 100+ node simulation)

bash
# Clone SimBlock into the project directory
git clone https://github.com/simblock/simblock.git simblock
cd simblock/simulator
./gradlew build
Running the Application
Start the Flask server

bash
python main.py
Access the web interface

text
Open http://localhost:5000 in your browser
💻 Usage Guide
Basic Blockchain Operations
Create Transactions

Enter sender, receiver, and amount

Submit to add to mempool

Mine Blocks

Specify miner name

Mine pending transactions into new blocks

Manage Network

Add peer nodes for P2P communication

Resolve conflicts with consensus algorithm

Advanced Attack Simulation
Configure 100+ Node Network

Automatic setup of global node distribution

Regional latency simulation

Network health monitoring

Execute Double-Spending Attack

Legitimate Transaction: Attacker → Victim wallet

Malicious Transaction: Attacker → Shadow wallet (same timestamp)

Private Mining: 6+ node attacker network

Chain Broadcast: Attempt to override main chain

Monitor Attack Progress

Real-time private vs public chain visualization

Network acceptance metrics

Success probability calculations

Analytics & Simulation
View Real-time Charts

Blockchain growth analysis

Balance distribution

Mining time patterns

Network activity with 100+ nodes

Private mining progress

Run Large-scale Simulations

100+ node network status

Global attack probability analysis

Performance metrics across regions

Generate Comprehensive CSV Reports

Download multiple CSV files for deep analysis

Blockchain technical specifications

Attack forensics and timeline

Network performance metrics

Double spend detection analysis

🔧 API Endpoints
Blockchain Operations
GET /api/chain - Get complete blockchain

POST /api/tx/new - Create new transaction

POST /api/mine - Mine new block

GET /api/balances/detailed - Get wallet balances with attack info

Attack Simulation
POST /api/attack/run - Execute double-spending attack with 6+ private nodes

GET /api/simblock/network - Get 100+ node network status

POST /api/simblock/start - Start large-scale simulation

Analytics & Visualization
GET /api/charts/blockchain-growth - Blockchain growth data

GET /api/charts/balance-distribution - Balance chart data

GET /api/charts/network-activity - 100+ node network activity

GET /api/charts/simblock-analysis - Network performance metrics

Advanced CSV Reporting
GET /api/report/csv - Generate all CSV reports (ZIP)

GET /api/report/csv/blockchain - Blockchain analysis CSV

GET /api/report/csv/attack - Attack analysis CSV

GET /api/report/csv/network - Network metrics CSV

GET /api/report/csv/double-spend - Double spend analysis CSV

🎯 Educational Value
This project serves as an excellent learning tool for:

Blockchain Fundamentals - Understanding core concepts

Cryptocurrency Security - Double-spending vulnerability analysis

Large-scale Networks - 100+ node simulation and management

Attack Vectors - Private mining and chain reorganization

Data Analysis - CSV-based deep analytics and reporting

Academic Research - Anomaly detection in distributed systems

📊 Sample Outputs
Attack Simulation Results
text
🎯 Double-Spending Attack Results
✅ Attack SUCCESSFUL with 6 private nodes!
• Network Size: 100+ nodes globally distributed
• Private Mining: 6 attacker nodes mining alternative chain
• Dual Transactions: 
  - Legitimate: RedHawk → Victim_Wallet (10.0 coins)
  - Malicious: RedHawk → Shadow_Wallet (10.0 coins) - SAME TIMESTAMP
• Success Probability: 75.0%
CSV Report System
text
📈 Comprehensive CSV Analysis Generated
✅ blockchain_analysis_20241205_143022.csv - Full chain data
✅ attack_analysis_20241205_143022.csv - Attack forensics  
✅ network_metrics_20241205_143022.csv - 100+ node performance
✅ double_spend_analysis_20241205_143022.csv - Transaction conflicts
🆕 Instructor Requirements Implementation
✅ Completed Enhancements
100+ Node Network

SimBlock configuration for large-scale simulation

Global node distribution across regions

Realistic network latency simulation

Private Block Mining with 6+ Nodes

Visual separation of public and private networks

Attacker-controlled mining pool

Alternative chain development

Proper Double Spending Demonstration

Simultaneous transaction creation

Identical timestamps for legitimacy proof

Clear malicious intent demonstration

Shadow wallet implementation

CSV Reporting System

Replaced PDF with comprehensive CSV analysis

Multiple specialized report types

Deep data analytics capabilities

Educational forensic analysis

🤝 Contributing
We welcome contributions to enhance this project:

Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📝 License
This project is developed under the academic supervision of Virtual University of Pakistan and is available for educational and research purposes.

👨‍💻 Project Team
Project Instructor
Fouzia Jumani

Skype: fouziajumani

Email: fouziajumani@vu.edu.pk

Project Author
Eng. Muhammad Imtiaz Shaffi

VU ID: BC220200917

Email: bc220200917mis@vu.edu.pk

🔗 Related Resources
SimBlock GitHub Repository

Virtual University of Pakistan

Blockchain Basics Guide

📞 Support
For technical support or questions about this project:

Create an issue on GitHub

Contact the project author via email

Refer to the comprehensive documentation

<div align="center">
⭐ If you find this project useful, please give it a star on GitHub!

*"Advancing blockchain security through 100+ node simulations and comprehensive analytics"*

</div> ```