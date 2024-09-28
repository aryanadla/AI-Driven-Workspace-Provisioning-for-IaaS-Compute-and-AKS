from flask import Blueprint, request, jsonify
import logging
from api.utils.terraform import run_terraform

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@api_bp.route('/provision/aks', methods=['POST'])
def provision_resources():
    data = request.json
    if not data:
        logging.error("No JSON data provided in the request.")
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Extract vm data
    aks_data = data.get('aks')
    if not aks_data:
        logging.error("No vm configuration data provided.")
        return jsonify({"status": "error", "message": "No aks configuration data provided"}), 400

    # Generate content for terraform.tfvars
    tfvars_content = generate_aks_tfvars_content(aks_data)
    tfvars_path = 'terraform/terraform.tfvars'

    # Write data to terraform.tfvars
    try:
        with open(tfvars_path, 'w') as tfvars_file:
            tfvars_file.write(tfvars_content)
    except IOError as e:
        logging.error(f"Error writing to terraform.tfvars: {e}")
        return jsonify({"status": "error", "message": "Failed to write to tfvars file"}), 500

    # Run Terraform commands
    success, message = run_terraform('init')
    if not success:
        logging.error(f"Terraform init failed: {message}")
        return jsonify({"status": "error", "message": message}), 500

    success, message = run_terraform('apply')
    if not success:
        logging.error(f"Terraform apply failed: {message}")
        return jsonify({"status": "error", "message": message}), 500

    # Read and return the updated terraform.tfvars content
    try:
        with open(tfvars_path, 'r') as tfvars_file:
            updated_tfvars_content = tfvars_file.read()
            logging.debug("Updated terraform.tfvars content:\n%s", updated_tfvars_content)
    except IOError as e:
        logging.error(f"Error reading terraform.tfvars: {e}")
        return jsonify({"status": "error", "message": "Failed to read tfvars file"}), 500

    return jsonify({
        "status": "success",
        "message": "Terraform commands executed successfully.",
        "tfvars_content": updated_tfvars_content
    }), 200

@api_bp.route('/decommission/aks', methods=['POST'])
def provision_decommission():
    success, message = run_terraform('destroy')
    if not success:
        logging.error(f"Terraform destroy failed: {message}")
        return jsonify({"status": "error", "message": message}), 500

def generate_aks_tfvars_content(aks_data):
    # Initialize tfvars content
    content = ""

    # Resource Group Name
    content += f'resource_group_name = "{aks_data.get("resource_group_name", "default-rg")}"\n'

    # ACR Name and SKU
    content += f'acr_name = "{aks_data.get("acr_name", "default-acr")}"\n'
    content += f'acr_sku  = "{aks_data.get("acr_sku", "Basic")}"\n'

    # AKS Cluster Name and Version
    content += f'cluster_name = "{aks_data.get("cluster_name", "default-aks-cluster")}"\n'
    content += f'kubernetes_version = "{aks_data.get("kubernetes_version", "1.29.2")}"\n'

    # DNS Prefix
    content += f'dns_prefix = "{aks_data.get("dns_prefix", "default-dns")}"\n'

    # Node Resource Group
    content += f'node_resource_group = "{aks_data.get("node_resource_group", "default-node-rg")}"\n'

    # Node Pools
    node_pools = aks_data.get('node_pools', [])
    content += "# Node Pools\n"
    content += "node_pools = [\n"
    for pool in node_pools:
        content += f"""  {{
    name                = "{pool.get('name', 'default')}",
    os_sku              = "{pool.get('os_sku', 'Ubuntu')}",
    node_count          = {pool.get('node_count', 2)},
    vm_size             = "{pool.get('vm_size', 'Standard_DS2_v2')}"
  }},
"""
    content += "]\n"

    # Network Plugin and Policy
    content += f'network_plugin = "{aks_data.get("network_plugin", "azure")}"\n'
    content += f'network_policy = "{aks_data.get("network_policy", "azure")}"\n'

    # Service CIDR and DNS Service IP
    content += f'service_cidr = "{aks_data.get("service_cidr", "10.0.0.0/16")}"\n'
    content += f'dns_service_ip = "{aks_data.get("dns_service_ip", "10.0.0.10")}"\n'

    return content
