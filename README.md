Blockchain Double-Spending & Anomaly Detection System
This project is a Flask-based web application that provides a user-friendly interface to a simplified blockchain. It serves as an educational tool to demonstrate core blockchain concepts, including transactions, mining (Proof-of-Work), peer-to-peer (P2P) networking, and a classic double-spending attack simulation.

The system integrates a custom blockchain implementation with a simulation framework to analyze the probability of a double-spending attack succeeding under various conditions.

🌟 Features
Blockchain Playground: Create and broadcast new transactions, mine new blocks, and view the current state of the blockchain and user balances.

P2P Network: Add multiple nodes (peers) and run a consensus algorithm to ensure all nodes have the longest, most valid chain.

Double-Spending Attack Simulation: A dedicated section to simulate a classic double-spending attack, visualizing the attacker's actions and the outcome.

Visualizations: Interactive charts to track blockchain growth and visualize the results of the attack simulation.

PDF Report Generation: Generate a comprehensive PDF report summarizing the blockchain state and simulation results for analysis.

🚀 Getting Started
Follow these steps to set up and run the project locally.

Prerequisites
Python 3.7+

pip (Python package installer)

Installation
Clone the repository to your local machine:

Bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
Create and activate a virtual environment (recommended):

Bash

python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
Install the required Python packages:

Bash

pip install Flask requests jinja2 python-simblock reportlab
💻 How to Run
Start the Flask server from the command line:

Bash

python main.py
The server will start on http://127.0.0.1:5000 by default.

Open your web browser and navigate to http://127.0.0.1:5000 to access the application.

For P2P Network Simulation:
To demonstrate the P2P features, you can open multiple terminal windows and run the application on different ports.

For example, to start a second node on port 5001:

Bash

set FLASK_RUN_PORT=5001  # On Windows
export FLASK_RUN_PORT=5001 # On macOS/Linux

python main.py
You can then use the Add Peer functionality in the web interface to connect the nodes (e.g., connect http://127.0.0.1:5000 to http://127.0.0.1:5001).

📁 Project Structure
.
├── main.py                     # The main Flask application file
├── templates/
│   └── index.html              # The main front-end HTML file
├── static/
│   └── app.js                  # Frontend JavaScript for interactivity
│   └── (your CSS files)
├── blockchain/                 # The core blockchain logic
│   ├── __init__.py
│   ├── block.py
│   ├── blockchain.py
│   ├── transaction.py
│   └── attacker.py
└── .venv/                      # Python virtual environment