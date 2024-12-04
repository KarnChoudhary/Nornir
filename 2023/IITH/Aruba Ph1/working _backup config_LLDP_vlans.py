from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='nornir.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("nornir")

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

# Get the current date for the backup folder name
backup_date = datetime.now().strftime("%Y-%m-%d")
backup_folder = f"backups/{backup_date}"

# Create the backup folder if it doesn't exist
os.makedirs(backup_folder, exist_ok=True)

# Create subfolders for each command
commands = ["show running-config", "show lldp info remote-device", "show vlan"]
for command in commands:
    command_folder = os.path.join(backup_folder, command.replace(" ", "_"))
    os.makedirs(command_folder, exist_ok=True)

# Define the task to take a backup of the configuration and additional commands
def backup_configuration(task):
    try:
        # Connect to the device
        net_connect = task.host.get_connection("netmiko", task.nornir.config)

        for command in commands:
            # Run the command
            result = net_connect.send_command(command)
            logger.info(f"Command '{command}' executed successfully on {task.host.name}")

            # Define the backup file path
            command_folder = os.path.join(backup_folder, command.replace(" ", "_"))
            backup_file = os.path.join(command_folder, f"{task.host.name}_{command.replace(' ', '_')}.txt")

            # Write the command output to the backup file
            with open(backup_file, "w") as file:
                file.write(result)

            logger.info(f"Output of command '{command}' for {task.host.name} saved to {backup_file}")

    except Exception as e:
        error_message = str(e)
        if "Authentication failure" in error_message:
            logger.error(f"Authentication failed for {task.host.name}: Incorrect username or password")
        elif "timed out" in error_message:
            logger.error(f"Connection timed out for {task.host.name}")
        else:
            logger.error(f"Failed to run command on {task.host.name}: {e}")

# Run the backup task on all devices
result = nr.run(task=backup_configuration)

print("Backup task completed")
