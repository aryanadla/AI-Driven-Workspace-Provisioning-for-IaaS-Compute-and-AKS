from flask import Blueprint, request, jsonify, send_file
import logging
import os
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

    # Extract vm data
    vm_data = data.get('virtual_machine')
    if not vm_data:
        logging.error("No vm configuration data provided.")
        return jsonify({"status": "error", "message": "No vm configuration data provided"}), 400

    # Generate content for terraform.tfvars
    tfvars_content = generate_vm_tfvars_content(vm_data)
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
    try:
        success, message = run_terraform('destroy')
        if not success:
            logging.error(f"Terraform destroy failed: {message}")
            return jsonify({"status": "error", "message": message}), 500
        
        return jsonify({"status": "success", "message": "Resources destroyed successfully."}), 200
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({"status": "error", "message": "An unexpected error occurred."}), 500

def generate_vm_tfvars_content(vm_data):
    # Extract virtual machine data
    rgname = vm_data.get('rgname', 'default-rgname')
    vm_name = vm_data.get('vm', 'default-vm')
    vm_size = vm_data.get('vmsize', 'Standard_D2s_v3')
    admin_username = vm_data.get('admin_username', 'adminuser')

    # Initialize tfvars content
    content = f"""
    rgname = "{rgname}"
    vm = "{vm_name}"
    vmsize = "{vm_size}"
    admin_username = "{admin_username}"
    """

    return content
