import os
import json
import requests
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from langchain_google_genai import ChatGoogleGenerativeAI

vm_metrics_bp = Blueprint('predict', __name__)

def read_terraform_outputs():
    try:
        with open('terraform/terraform_outputs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("terraform_outputs.json not found.")
        return None
    except json.JSONDecodeError:
        print("Error decoding terraform_outputs.json. Please check the file format.")
        return None

# Azure credentials (hardcoded as per request, but this is not recommended for production)
tenant_id = '9b415834-803a-4da0-afdc-fe6b1d52d649'
client_id = '16087f09-1d27-4fe2-8509-7a757712b93d'
client_secret = 'KRB8Q~q2FYK6nEN1-3KDF~dRIxsOfYwP7e.sNboM'
subscription_id = 'e38e4eed-8fbd-4713-b27d-0f419989008a'

access_token = None
token_expiry = None

def get_access_token():
    global access_token, token_expiry

    if access_token and token_expiry and datetime.now() < token_expiry:
        return access_token

    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://management.azure.com/.default'
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        access_token = token_json['access_token']
        expires_in = token_json.get('expires_in', 3600)
        token_expiry = datetime.now() + timedelta(seconds=int(expires_in))
        
        return access_token
    
    except requests.RequestException as e:
        print(f"Failed to get access token: {e}")
        return None

def get_vm_metrics(vm_name):
    access_token = get_access_token()
    if not access_token:
        return None

    metrics_url = (
        f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/Hackathon_Devops5/providers/Microsoft.Compute/virtualMachines/{vm_name}/providers/microsoft.insights/metrics'
        '?api-version=2018-01-01&metricnames=Percentage%20CPU,Available%20Memory%20Bytes,Network%20In%20Total,Network%20Out%20Total&timespan=PT1M&aggregation=Average&interval=PT1M'
    )
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        metrics_response = requests.get(metrics_url, headers=headers)
        metrics_response.raise_for_status()
        return metrics_response.json()
    
    except requests.RequestException as e:
        print(f"Failed to get metrics: {e}")
        return None

# Initialize the AI model
os.environ["GOOGLE_API_KEY"] = "AIzaSyBcG2htILfiVlCOAdYKl3HhkIDAZjxrooI"
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

prompt_template = """
You are an AI assistant designed to analyze system metrics for a virtual machine (VM) and provide alerts. Based on the provided metrics data:

- CPU Usage: {cpu_usage} %
- Available Memory: {available_memory} GB
- Network In: {network_in} bytes
- Network Out: {network_out} bytes

Provide appropriate feedback on performance and any potential risks in 5-6 lines. We are using only Standard_D2s_v3 VM size.
"""

@vm_metrics_bp.route('/predict', methods=['GET'])
def predict():
    terraform_outputs = read_terraform_outputs()
    if not terraform_outputs:
        return jsonify({"error": "Failed to read Terraform outputs"}), 500

    vm_name = terraform_outputs.get('vm_name', {}).get('value')
    if not vm_name:
        return jsonify({"error": "VM name not found in Terraform outputs"}), 500

    metrics_data = get_vm_metrics(vm_name)
    if not metrics_data:
        return jsonify({"error": "Failed to retrieve VM metrics"}), 500

    try:
        cpu_usage = next(metric for metric in metrics_data['value'] if metric['name']['value'] == 'Percentage CPU')['timeseries'][0]['data'][-1]['average']
        available_memory = next(metric for metric in metrics_data['value'] if metric['name']['value'] == 'Available Memory Bytes')['timeseries'][0]['data'][-1]['average']
        network_in = next(metric for metric in metrics_data['value'] if metric['name']['value'] == 'Network In Total')['timeseries'][0]['data'][-1]['average']
        network_out = next(metric for metric in metrics_data['value'] if metric['name']['value'] == 'Network Out Total')['timeseries'][0]['data'][-1]['average']

        available_memory_gb = available_memory / (1024 * 1024 * 1024)

        messages = [
            (
                "system",
                prompt_template.format(
                    cpu_usage=cpu_usage,
                    available_memory=available_memory_gb,
                    network_in=network_in,
                    network_out=network_out
                ),
            ),
            (
                "human",
                "Please analyze the metrics and give suggestions to the user."
            )
        ]

        ai_msg = llm.invoke(messages)

        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_usage": cpu_usage,
                "available_memory_gb": available_memory_gb,
                "network_in": network_in,
                "network_out": network_out
            },
            "analysis": ai_msg.content
        })

    except (KeyError, IndexError, StopIteration) as e:
        return jsonify({"error": f"Error processing metrics data: {str(e)}"}), 500