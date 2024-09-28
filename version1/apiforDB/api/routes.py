from flask import Blueprint, request, jsonify
import logging
from api.utils.terraform import run_terraform

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@api_bp.route('/provision', methods=['POST'])
def provision_resources():
    # Get the JSON data from the request
    data = request.json
    if not data:
        logging.error("No JSON data provided in the request.")
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Extract Databricks data
    databricks_data = data.get('databricks')
    if not databricks_data:
        logging.error("No Databricks configuration data provided.")
        return jsonify({"status": "error", "message": "No Databricks configuration data provided"}), 400

    # Generate content for terraform.tfvars
    tfvars_content = generate_tfvars_content(databricks_data)
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

@api_bp.route('/decommission', methods=['POST'])
def provision_decommission():
    success, message = run_terraform('destroy')
    if not success:
        logging.error(f"Terraform destroy failed: {message}")
        return jsonify({"status": "error", "message": message}), 500

def generate_tfvars_content(databricks_data):
    # Initialize tfvars content
    content = ""

    # Resource Group and Location
    content += f"""
# Resource Group and Location
resource_group_name = "{databricks_data.get('resource_group_name', 'default-resource-group')}"
location = "{databricks_data.get('location', 'East US')}"
"""

    # Databricks Workspace
    content += f"""
# Databricks Workspace
databricks_workspace_name = "{databricks_data.get('databricks_workspace_name', 'default-workspace')}"
databricks_sku = "{databricks_data.get('databricks_sku', 'standard')}"
"""

    # Databricks Clusters
    clusters = databricks_data.get('databricks_clusters', {})
    if clusters:
        content += "# Databricks Clusters\n"
        content += "databricks_clusters = {\n"
        for cluster_key, cluster in clusters.items():
            content += f"  {cluster_key} = {{\n"
            content += f"    cluster_name  = \"{cluster.get('cluster_name', 'default-cluster-name')}\"\n"
            content += f"    spark_version = \"{cluster.get('spark_version', '9.1.x-scala2.12')}\"\n"
            content += f"    node_type     = \"{cluster.get('node_type', 'Standard_DS3_v2')}\"\n"
            content += f"    min_workers   = {cluster.get('min_workers', 1)}\n"
            content += f"    max_workers   = {cluster.get('max_workers', 2)}\n"
            content += "  }\n"
        content += "}\n"
    else:
        content += "databricks_clusters = {}\n"

    # Optional configurations
    content += f"""
# Optional Configurations
enable_secure_cluster_connectivity = {str(databricks_data.get('enable_secure_cluster_connectivity', False)).lower()}
enable_vnet_deployment = {str(databricks_data.get('enable_vnet_deployment', False)).lower()}
vnet_id = "{databricks_data.get('vnet_id', '')}"
enable_customer_managed_key = {str(databricks_data.get('enable_customer_managed_key', False)).lower()}
"""

    return content
