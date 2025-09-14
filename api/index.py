import os
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from a.env file
load_dotenv()

app = Flask(__name__)

# --- Blockchain Configuration ---
# IMPORTANT: These are read from your Vercel Environment Variables
INFURA_URL = os.getenv("INFURA_URL")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Connect to the Ethereum network
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(WALLET_PRIVATE_KEY)

# The ABI (Application Binary Interface) for your Solidity contract
# This tells our Python code how to talk to the smart contract
CONTRACT_ABI = ',"stateMutability":"view","type":"function"},{"inputs":,"name":"getProjectCount","outputs":,"stateMutability":"view","type":"function"},{"inputs":,"name":"projects","outputs":,"stateMutability":"view","type":"function"},{"inputs":,"name":"projectCounter","outputs":,"stateMutability":"view","type":"function"},{"inputs":,"name":"registerProject","outputs":,"stateMutability":"nonpayable","type":"function"}]'


# Create a contract object
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# --- Flask Routes (The different pages of our website) ---

@app.route('/')
def mobile_app():
    """Serves the mobile app's data entry form."""
    return render_template('mobile_form.html')

@app.route('/dashboard')
def dashboard():
    """Serves the dashboard page."""
    return render_template('dashboard.html')

# ####################################################################
# THIS IS THE LINE THAT HAS BEEN FIXED
# ####################################################################
@app.route('/api/submit_project', methods=['GET', 'POST'])
def submit_project():
    """Receives form data and writes it to the blockchain."""
    try:
        data = request.form
        start_date_dt = datetime.strptime(data, '%Y-%m-%d')
        start_date_timestamp = int(start_date_dt.timestamp())

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.registerProject(
            data['projectName'],
            data['location'],
            data,
            int(data['areaHectares']),
            start_date_timestamp,
            data
        ).build_transaction({
            'chainId': 11155111,  # Sepolia testnet chain ID
            'gas': 300000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': nonce,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=WALLET_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "message": "Project registered successfully!",
            "transactionHash": tx_hash.hex()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# This is a catch-all for Vercel to find the app
@app.route('/index')
def index():
    return mobile_app()