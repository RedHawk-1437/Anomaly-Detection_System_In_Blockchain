# 🚀 Blockchain Anomaly Detection System - Double Spending Attack Simulation

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-brightgreen)
![SimBlock](https://img.shields.io/badge/SimBlock-Integrated-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A comprehensive blockchain prototype with double-spending attack detection and network simulation capabilities**

*Developed under the supervision of Virtual University of Pakistan*

</div>

## 📖 Overview

This project implements a complete blockchain ecosystem with advanced anomaly detection capabilities. It features a custom blockchain implementation, double-spending attack simulation, P2P network functionality, and integration with SimBlock for large-scale network analysis.

## ✨ Key Features

### 🔗 Core Blockchain
- **Custom Blockchain Implementation** with Proof-of-Work consensus
- **Transaction Management** with mempool and mining rewards
- **P2P Network** with peer discovery and chain synchronization
- **Balance Management** with real-time wallet tracking

### ⚡ Attack Simulation
- **Double-Spending Attack** simulation with configurable parameters
- **Attack Success Probability** controls with real-time adjustment
- **Private Chain Mining** with broadcast capabilities
- **Attack Analytics** with success rate tracking

### 📊 Visualization & Analytics
- **Interactive Charts** for blockchain growth and transaction patterns
- **Balance Distribution** visualization with pie charts
- **Mining Analysis** with time-series data
- **Network Activity** monitoring and simulation

### 🔬 SimBlock Integration
- **Large-scale Network Simulation** with customizable parameters
- **Attack Probability Analysis** across multiple nodes
- **Performance Metrics** including block times and fork detection
- **Comparative Analysis** between honest and attacker blocks

### 📄 Reporting
- **Comprehensive PDF Reports** with charts and analytics
- **Simulation Summaries** with detailed metrics
- **Attack Results Documentation** with configuration details

## 🏗️ Project Structure

```
blockchain-anomaly-detection/
│
├── 📁 blockchain/                 # Core blockchain modules
│   ├── blockchain.py             # Main blockchain class
│   ├── block.py                  # Block structure implementation
│   ├── transaction.py            # Transaction handling
│   └── attacker.py               # Attack simulation logic
│
├── 📁 web/                       # Frontend application
│   ├── templates/
│   │   └── index.html            # Main web interface
│   └── static/
│       ├── styles.css            # Comprehensive styling
│       ├── app.js                # Interactive functionality
│       └── images/               # Logos and assets
│
├── 📁 simblock/                  # Network simulation (optional)
│   └── simulator/                # SimBlock installation
│
├── 📁 reports/                   # Generated PDF reports
├── main.py                       # Flask application entry point
└── README.md                     # This file
```

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
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install SimBlock (Optional - for network simulation)**
```bash
# Clone SimBlock into the project directory
git clone https://github.com/simblock/simblock.git simblock
cd simblock/simulator
./gradlew build
```

### Running the Application

1. **Start the Flask server**
```bash
python main.py
```

2. **Access the web interface**
```
Open http://localhost:5000 in your browser
```

## 💻 Usage Guide

### Basic Blockchain Operations

1. **Create Transactions**
   - Enter sender, receiver, and amount
   - Submit to add to mempool

2. **Mine Blocks**
   - Specify miner name
   - Mine pending transactions into new blocks

3. **Manage Network**
   - Add peer nodes for P2P communication
   - Resolve conflicts with consensus algorithm

### Attack Simulation

1. **Configure Attack Parameters**
   - Set success probability (1-100%)
   - Adjust attacker hash power
   - Choose forced outcomes (success/failure/random)

2. **Run Double-Spending Attack**
   - Specify attacker name and blocks to mine
   - Execute attack and monitor results
   - View detailed attack steps and outcomes

### Analytics & Simulation

1. **View Real-time Charts**
   - Blockchain growth analysis
   - Balance distribution
   - Mining time patterns
   - Network activity

2. **Run SimBlock Simulations**
   - Check SimBlock status
   - Configure simulation parameters
   - Analyze network-wide attack probabilities

3. **Generate Reports**
   - Download comprehensive PDF reports
   - Include charts and simulation results

## 🔧 API Endpoints

### Blockchain Operations
- `GET /api/chain` - Get complete blockchain
- `POST /api/tx/new` - Create new transaction
- `POST /api/mine` - Mine new block
- `GET /api/balances` - Get wallet balances

### Attack Simulation
- `POST /api/attack/run` - Execute double-spending attack
- `POST /peers` - Add network peers
- `GET /consensus` - Resolve network conflicts

### Analytics & Visualization
- `GET /api/charts/blockchain-growth` - Blockchain growth data
- `GET /api/charts/balance-distribution` - Balance chart data
- `GET /api/analyze` - Run SimBlock analysis
- `GET /api/report/pdf` - Generate PDF report

## 🎯 Educational Value

This project serves as an excellent learning tool for:

- **Blockchain Fundamentals** - Understanding core concepts
- **Cryptocurrency Security** - Double-spending vulnerability analysis
- **Network Protocols** - P2P communication and consensus
- **Data Visualization** - Real-time analytics and charting
- **Academic Research** - Anomaly detection in distributed systems

## 📊 Sample Outputs

### Attack Simulation Results
```
🎯 Double-Spending Attack Results
✅ Attack SUCCESSFUL!
• Success Rate: 75.0%
• Blocks Mined: 3
• Network Acceptance: 4/5 peers
```

### Simulation Analytics
```
📈 SimBlock Simulation Summary
• Attack Probability: 32.5%
• Total Blocks: 1,247
• Average Block Time: 12.3ms
• Forks Detected: 18
• Total Miners: 156
```

## 🤝 Contributing

We welcome contributions to enhance this project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is developed under the academic supervision of **Virtual University of Pakistan** and is available for educational and research purposes.

## 👨‍💻 Project Team

### Project Instructor
- **Fouzia Jumani**
- Skype: fouziajumani
- Email: fouziajumani@vu.edu.pk

### Project Author
- **Eng. Muhammad Imtiaz Shaffi**
- VU ID: BC220200917
- Email: bc220200917mis@vu.edu.pk

## 🔗 Related Resources

- [SimBlock GitHub Repository](https://github.com/simblock/simblock)
- [Virtual University of Pakistan](https://www.vu.edu.pk)
- [Blockchain Basics Guide](https://github.com/bitcoinbook/bitcoinbook)

## 📞 Support

For technical support or questions about this project:
- Create an issue on GitHub
- Contact the project author via email
- Refer to the comprehensive documentation

---

<div align="center">

**⭐ If you find this project useful, please give it a star on GitHub!**

*"Advancing blockchain security through education and innovation"*

</div>


