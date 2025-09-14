import os
from flask import Flask, request, jsonify, render_template_string
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables from a.env file
load_dotenv()

app = Flask(__name__)

# --- Blockchain Configuration ---
# IMPORTANT: Set these in your Vercel Environment Variables
INFURA_URL = os.getenv("INFURA_URL")
WALLET_PRIVATE_KEY = os.getenv("WALLET_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Connect to the Ethereum network
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
account = w3.eth.account.from_key(WALLET_PRIVATE_KEY)

# The ABI (Application Binary Interface) you copied from Remix
# This is a simplified version for the functions we need
CONTRACT_ABI = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "projectId",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "projectName",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "implementingBody",
				"type": "string"
			}
		],
		"name": "ProjectRegistered",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_projectName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_location",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_implementingBody",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_areaHectares",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_startDate",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_projectType",
				"type": "string"
			}
		],
		"name": "registerProject",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "projectId",
				"type": "uint256"
			}
		],
		"name": "getProject",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "projectId",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "projectName",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "location",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "implementingBody",
						"type": "string"
					},
					{
						"internalType": "uint256",
						"name": "areaHectares",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "startDate",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "projectType",
						"type": "string"
					},
					{
						"internalType": "bool",
						"name": "isInitialized",
						"type": "bool"
					}
				],
				"internalType": "struct AquaCredRegistry.Project",
				"name": "",
				"type": "tuple"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getProjectCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "projectCounter",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "projects",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "projectId",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "projectName",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "location",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "implementingBody",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "areaHectares",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "startDate",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "projectType",
				"type": "string"
			},
			{
				"internalType": "bool",
				"name": "isInitialized",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# Create a contract object
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# --- HTML Template for the Mobile App ---
# This is kept inside the python file for simplicity
MOBILE_APP_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AquaCred - New Report</title>
    <style>
        body { font-family: 'Poppins', sans-serif; background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
       .container { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 500px; margin: auto; }
        h1 { color: #005f73; text-align: center; }
        label { display: block; margin-top: 15px; font-weight: 600; }
        input[type="text"], input[type="number"], input[type="date"] { width: 95%; padding: 10px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; }
       .submit-btn { display: block; width: 100%; padding: 15px; margin-top: 20px; background-color: #0a9396; color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; }
       .submit-btn:hover { background-color: #005f73; }
       .status { text-align: center; margin-top: 20px; font-weight: bold; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>New Project Report</h1>
        <form action="/api/submit_project" method="post">
            <label for="projectName">Project Name:</label>
            <input type="text" id="projectName" name="projectName" required>

            <label for="location">Location (State):</label>
            <input type="text" id="location" name="location" required>

            <label for="implementingBody">Implementing Body:</label>
            <input type="text" id="implementingBody" name="implementingBody" required>

            <label for="areaHectares">Area (Hectares):</label>
            <input type="number" id="areaHectares" name="areaHectares" required>

            <label for="startDate">Start Date:</label>
            <input type="date" id="startDate" name="startDate" required>

            <label for="projectType">Project Type:</label>
            <input type="text" id="projectType" name="projectType" value="Mangrove Afforestation" required>

            <button type="submit" class="submit-btn">Submit to Ledger</button>
        </form>
        <div class="status" id="status-message"></div>
    </div>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def mobile_app():
    """Serves the mobile app's data entry form."""
    return render_template_string(MOBILE_APP_TEMPLATE)

@app.route('/api/submit_project', methods=)
def submit_project():
    """
    Receives form data and writes it to the blockchain.
    This is the core "write" functionality.
    """
    try:
        # Get data from the form
        data = request.form
        project_name = data['projectName']
        location = data['location']
        implementing_body = data
        area_hectares = int(data['areaHectares'])
        
        # Convert date to Unix timestamp
        from datetime import datetime
        start_date_dt = datetime.strptime(data, '%Y-%m-%d')
        start_date_timestamp = int(start_date_dt.timestamp())

        project_type = data

        # Build the transaction
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

        # Sign and send the transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=WALLET_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for the transaction to be mined
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "status": "success",
            "message": "Project registered successfully on the blockchain!",
            "transactionHash": tx_hash.hex()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# This route is needed for Vercel to find the main application
@app.route('/index')
def index():
    return mobile_app()