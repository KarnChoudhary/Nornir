from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_utils.plugins.functions import print_result
import logging

# Configure logging with less verbose output
logging.basicConfig(
    filename='nornir_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

def configure_console_line(task):
    """Configure the console line with login local"""
    try:
        commands = [
            "line con 0",
            "login local"
        ]
        result = task.run(
            task=netmiko_send_config,
            config_commands=commands,
            read_timeout=30
        )

        if result[0].failed:
            logging.error(f"Failed to configure console line on {task.host.name}: {result[0].exception}")
        else:
            logging.info(f"Successfully configured console line on {task.host.name}")

        return result
    except Exception as e:
        logging.error(f"Exception while configuring console line on {task.host.name}: {str(e)}")
        raise

def save_config(task):
    """Save the running configuration"""
    try:
        result = task.run(
            task=netmiko_send_command,
            command_string="write memory",
            read_timeout=30
        )

        if result[0].failed:
            logging.error(f"Failed to save configuration on {task.host.name}")
        else:
            logging.info(f"Successfully saved configuration on {task.host.name}")

        return result
    except Exception as e:
        logging.error(f"Exception while saving configuration on {task.host.name}: {str(e)}")
        raise

def main():
    try:
        # Configure the console line
        print("Configuring console line...")
        result = nr.run(task=configure_console_line)
        print_result(result)

        # Save the configuration
        print("Saving configuration...")
        result = nr.run(task=save_config)
        print_result(result)

        print("Operations completed successfully")

    except Exception as e:
        print(f"Error during execution: {str(e)}")
        logging.error(f"Script failed: {str(e)}")

if __name__ == "__main__":
    main()
