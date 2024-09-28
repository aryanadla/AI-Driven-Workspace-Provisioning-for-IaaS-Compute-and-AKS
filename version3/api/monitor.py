#monitor.py
from flask import Blueprint, request, jsonify
import logging
import json
import os
import subprocess
import requests
from datetime import datetime, timedelta

# Create a Blueprint for API routes
monitor_bp = Blueprint('monitor', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Global variables for token management
access_token = None
token_expiry = None

# Function to save Terraform outputs
def save_terraform_outputs():
    try:
        output_file_path = os.path.join('terraform', 'terraform_outputs.json')
        
        # Run Terraform output command and save results to file
        subprocess.check_call(
            ["terraform", "output", "-json"],
            cwd="terraform/",
            stdout=open(output_file_path, 'w')
        )
        
        # Load the output from file
        with open(output_file_path, 'r') as file:
            outputs = json.load(file)
        
        logging.info(f"Terraform outputs saved to {output_file_path}")
        return outputs

    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Terraform output: {e}")
        return None

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from Terraform output: {e}")
        return None

    except Exception as ex:
        logging.error(f"An unexpected error occurred: {ex}")
        return None

# Function to get an Azure OAuth2 access token
def get_access_token():
    global access_token, token_expiry

    # Check if token is still valid
    if access_token and token_expiry and datetime.now() < token_expiry:
        return access_token

    # Azure credentials
    tenant_id = '9b415834-803a-4da0-afdc-fe6b1d52d649'
    client_id = '16087f09-1d27-4fe2-8509-7a757712b93d'
    client_secret = 'KRB8Q~q2FYK6nEN1-3KDF~dRIxsOfYwP7e.sNboM'

    # Prepare token request
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://management.azure.com/.default'
    }
    
    try:
        # Make the request for an access token
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        # Extract token and expiration time
        access_token = token_json.get('access_token')
        expires_in = token_json.get('expires_in', 3600)  # Default to 1 hour if not provided
        token_expiry = datetime.now() + timedelta(seconds=int(expires_in))
        
        logging.info(f"Access token retrieved and valid until {token_expiry}")
        return access_token
    
    except requests.RequestException as e:
        logging.error(f"Failed to get access token: {e}")
        return None

# Endpoint to monitor VM metrics
@monitor_bp.route('/monitor', methods=['GET'])
def monitor_metrics():
    logging.info("Monitor endpoint called")
    
    # Save Terraform outputs to ensure they are up-to-date
    terraform_outputs = save_terraform_outputs()
    if terraform_outputs is None:
        return jsonify({"status": "error", "message": "Failed to retrieve Terraform outputs"}), 500

    logging.info(f"Terraform outputs: {json.dumps(terraform_outputs, indent=2)}")

    # Extract VM name from Terraform outputs
    vm_name = terraform_outputs.get('vm_name', {}).get('value')
    if not vm_name:
        logging.error("No VM name found in Terraform outputs.")
        return jsonify({"status": "error", "message": "VM name not found in Terraform outputs"}), 500

    logging.info(f"VM name from Terraform output: {vm_name}")

    # Azure configuration
    subscription_id = 'e38e4eed-8fbd-4713-b27d-0f419989008a'
    resource_group = terraform_outputs.get('resource_group', {}).get('value')
    api_version = '2018-01-01' 

    # Get access token for Azure API
    access_token = get_access_token()
    if not access_token:
        return jsonify({"status": "error", "message": "Failed to obtain access token"}), 500

    # Prepare the URL for Azure metrics API
    metrics_url = (
        f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/'
        f'providers/Microsoft.Compute/virtualMachines/{vm_name}/providers/microsoft.insights/metrics'
        f'?api-version={api_version}&metricnames=Percentage%20CPU,Available%20Memory%20Bytes,Network%20In%20Total,'
        f'Network%20Out%20Total&timespan=PT1H&aggregation=Average&interval=PT1H'
    )
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    logging.info(f"Metrics URL: {metrics_url}")
    logging.info(f"Request headers: {headers}")

    try:
        # Make the request for metrics
        metrics_response = requests.get(metrics_url, headers=headers)
        logging.info(f"Response status code: {metrics_response.status_code}")
        logging.info(f"Response content: {metrics_response.text}")

        metrics_response.raise_for_status()
        metrics_data = metrics_response.json()
        
        logging.info(f"Metrics successfully retrieved for VM: {vm_name}")
        return jsonify({"status": "success", "metrics": metrics_data}), 200
    
    except requests.RequestException as e:
        logging.error(f"Failed to get metrics: {e}")
        if hasattr(e, 'response'):
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
        return jsonify({"status": "error", "message": str(e)}), 500
