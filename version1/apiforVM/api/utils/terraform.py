import subprocess

def run_terraform(command, track_success=True):
    try:
        # Run Terraform init command to initialize the configuration directory
        subprocess.check_call(
            ["terraform", "init"],
            cwd="terraform/"
        )

        # Determine whether the command should include the -auto-approve flag
        if command in ["apply", "destroy"]:
            terraform_command = ["terraform", command, "-auto-approve", "-var-file=terraform.tfvars"]
        else:
            terraform_command = ["terraform", command, "-var-file=terraform.tfvars"]

        # Run the specified Terraform command (e.g., 'apply', 'destroy', etc.)
        subprocess.check_call(
            terraform_command,
            cwd="terraform/"
        )

        return True, "Terraform command executed successfully."

    except subprocess.CalledProcessError as e:
        # Capture and return the error message if an error occurs
        if command == "apply":
            # If an error occurs during apply, attempt to destroy the resources
            print("Error occurred during apply. Initiating destroy to clean up resources...")
            try:
                subprocess.check_call(
                    ["terraform", "destroy", "-auto-approve", "-var-file=terraform.tfvars"],
                    cwd="terraform/"
                )
                return False, "Terraform apply failed, and rollback (destroy) was successful."
            except subprocess.CalledProcessError as destroy_error:
                return False, f"Terraform apply failed and rollback (destroy) also failed: {destroy_error.output}"
        
        return False, f"Terraform execution failed with exit code {e.returncode}: {e.output}"

    except Exception as ex:
        return False, f"An unexpected error occurred: {str(ex)}"
