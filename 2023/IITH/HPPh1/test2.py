from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import os
import csv
from datetime import datetime
from netmiko.exceptions import (
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)
from paramiko.ssh_exception import SSHException
from nornir.core.exceptions import NornirSubTaskError

# Configure logging
logging.basicConfig(filename='backup_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

def handle_backup_command(task, backup_dir, results_csv):
    commands = [
        "display current-configuration",
        "display lldp neighbor-information list",
        "display vlan brief"
    ]

    success = True
    error_message = ""

    for command in commands:
        try:
            result = task.run(
                task=netmiko_send_command,
                command_string=command,
                use_timing=True
            )

            output = result[0].result
            logger.debug(f"Raw output from {task.host.name} for command '{command}':\n{output}")

            # Determine the subfolder based on the command
            if command == "display current-configuration":
                subfolder = "configurations"
            elif command == "display lldp neighbor-information list":
                subfolder = "lldp_neighbors"
            elif command == "display vlan brief":
                subfolder = "vlan_brief"

            # Create the subfolder if it doesn't exist
            subfolder_path = os.path.join(backup_dir, subfolder)
            os.makedirs(subfolder_path, exist_ok=True)

            # Save the command output to a file in the appropriate subfolder
            backup_filename = os.path.join(subfolder_path, f"{task.host.name}_{command.replace(' ', '_')}.txt")
            with open(backup_filename, 'w') as file:
                file.write(output)

            logger.info(f"Output for command '{command}' on {task.host.name} saved to {backup_filename}")

        except NetMikoAuthenticationException:
            success = False
            error_message = "Authentication failed"
            logger.error(f"{task.host.name}: Authentication failed")
            break
        except NetMikoTimeoutException:
            success = False
            error_message = "Connection timed out"
            logger.error(f"{task.host.name}: Connection timed out")
            break
        except SSHException:
            success = False
            error_message = "SSH connection failed"
            logger.error(f"{task.host.name}: SSH connection failed")
            break
        except NornirSubTaskError:
            success = False
            error_message = "Failed to execute command"
            logger.error(f"{task.host.name}: Failed to execute command")
            break
        except Exception as e:
            success = False
            error_message = f"Unexpected error: {str(e)}"
            logger.error(f"{task.host.name}: Unexpected error: {str(e)}")
            break

    # Write the result to the CSV file
    with open(results_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        if success:
            writer.writerow([task.host.name, task.host.hostname, "Success"])
        else:
            writer.writerow([task.host.name, task.host.hostname, "Error", error_message])

def main():
    try:
        # Initialize Nornir
        nr = InitNornir(config_file="config.yaml")

        # Create a backup directory named with the current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        backup_dir = f"backups_{current_date}"
        os.makedirs(backup_dir, exist_ok=True)

        # Create a CSV file to log the results
        results_csv = os.path.join(backup_dir, "backup_results.csv")
        with open(results_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Hostname", "IP Address", "Status", "Error Message"])

        # Filter for HP Comware devices and run the task
        result = nr.filter(F(groups__contains="hp_comware")).run(
            task=handle_backup_command, backup_dir=backup_dir, results_csv=results_csv
        )

        print(f"Backup task completed. Check the {backup_dir} folder for results.")

    except Exception as e:
        logger.error(f"Failed to initialize Nornir: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
