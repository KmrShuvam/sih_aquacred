import os
import json
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure Flask app with template folder for Vercel serverless environment
# When running in api/, templates are at ../templates
app = Flask(__name__, template_folder='../templates')

def validate_env_vars():
    """Validate that all required environment variables are present."""
    required_vars = ['INFURA_URL', 'WALLET_PRIVATE_KEY', 'CONTRACT_ADDRESS', 'CONTRACT_ABI_JSON']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def get_contract():
    """Get a Web3 contract instance with proper configuration."""
    validate_env_vars()
    
    # Get environment variables
    INFURA_URL = os.getenv("INFURA_URL")
    WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
    CONTRACT_ABI_JSON = os.getenv("CONTRACT_ABI_JSON")
    
    # Parse ABI from JSON
    try:
        CONTRACT_ABI = json.loads(CONTRACT_ABI_JSON)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid CONTRACT_ABI_JSON format: {e}")
    
    # Connect to Web3
    w3 = Web3(Web3.HTTPProvider(INFURA_URL))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ethereum network")
    
    # Create account from private key
    account = w3.eth.account.from_key(WALLET_PRIVATE_KEY)
    
    # Create contract instance with checksummed address
    contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    
    return w3, account, contract

# --- Flask Routes ---

@app.route('/')
def mobile_app():
    """Serves the mobile app's data entry form."""
    return render_template('mobile_form.html')

@app.route('/dashboard')
def dashboard():
    """Serves the dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    try:
        validate_env_vars()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/submit_project', methods=['POST'])
def submit_project():
    """Receives form data and writes it to the blockchain."""
    try:
        # Validate environment variables
        validate_env_vars()
        
        # Get Web3 and contract instances
        w3, account, contract = get_contract()
        
        # Parse form data
        data = request.form
        required_fields = ['projectName', 'location', 'implementingBody', 'areaHectares', 'startDate', 'projectType']
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
        
        # Parse and validate data
        project_name = data['projectName']
        location = data['location']
        implementing_body = data['implementingBody']
        area_hectares = int(data['areaHectares'])
        project_type = data['projectType']
        
        # Parse start date
        start_date_str = data['startDate']
        start_date_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        start_date_timestamp = int(start_date_dt.timestamp())

        # Get nonce and build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.registerProject(
            project_name,
            location,
            implementing_body,
            area_hectares,
            start_date_timestamp,
            project_type
        ).build_transaction({
            'chainId': 11155111,  # Sepolia testnet chain ID
            'gas': 300000,
            'gasPrice': w3.to_wei('10', 'gwei'),
            'nonce': nonce,
        })

        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("WALLET_PRIVATE_KEY"))
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Return immediately without waiting for receipt (for serverless timeout prevention)
        return jsonify({
            "status": "success",
            "transactionHash": tx_hash.hex()
        })
        
    except ValueError as e:
        return jsonify({"status": "error", "message": f"Configuration error: {str(e)}"}), 500
    except ConnectionError as e:
        return jsonify({"status": "error", "message": f"Network error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Vercel compatibility route
@app.route('/index')
def index():
    """Vercel compatibility route."""
    return mobile_app()