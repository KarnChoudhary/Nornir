from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir.core.filter import F
import logging
import csv
import re
from netmiko.exceptions import (
    NetMikoTimeoutException,
    NetMikoAuthenticationException,
)
from paramiko.ssh_exception import SSHException
from nornir.core.exceptions import NornirSubTaskError

# Configure logging
logging.basicConfig(filename='demo_nornir.log', level=logging.DEBUG)
logger = logging.getLogger("nornir")

def parse_diagnostic_values(line):
    """Parse a line of diagnostic values and return a dictionary of readings"""
    values = re.findall(r'-?\d+\.?\d*', line)
    if len(values) >= 5:
        return {
            'temperature': values[0],
            'voltage': values[1],
            'bias': values[2],
            'rx_power': values[3],
            'tx_power': values[4]
        }
    return None

def handle_device_command(task):
    try:
        command = "display transceiver diagnos interface"
        result = task.run(
            task=netmiko_send_command,
            command_string=command,
            use_timing=True
        )
        
        output = result[0].result
        logger.debug(f"Raw output from {task.host.name}:\n{output}")
        
        current_interface = None
        in_current_parameters = False
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            # Check for interface line
            interface_match = re.search(r'(\S+GigabitEthernet\d+/\d+/\d+) transceiver diagnostic information:', line)
            if interface_match:
                current_interface = interface_match.group(1)
                in_current_parameters = False
                continue
            
            # Skip if transceiver is absent
            if current_interface and "The transceiver is absent" in line:
                current_interface = None
                in_current_parameters = False
                continue
            
            # Check for current parameters section
            if current_interface and "Current diagnostic parameters:" in line:
                in_current_parameters = True
                continue
            
            # If we're in current parameters and find the values line
            if in_current_parameters and current_interface:
                # Skip the header line containing "Temp.(C) Voltage(V)..."
                if "Temp.(C)" in line:
                    continue
                    
                # Parse values from the next line
                values = parse_diagnostic_values(line)
                if values:
                    rx_power = values['rx_power']
                    write_to_csv(task.host.name, task.host.hostname, current_interface, rx_power)
                    logger.info(f"Found RX power {rx_power} dBm for {current_interface} on {task.host.name}")
                    current_interface = None
                    in_current_parameters = False
            
    except NetMikoAuthenticationException:
        error_msg = "Login failed"
        logger.error(f"{task.host.name}: Authentication failed")
        write_to_csv(task.host.name, task.host.hostname, "ERROR", error_msg)
    except NetMikoTimeoutException:
        error_msg = "Login failed"
        logger.error(f"{task.host.name}: Connection timed out")
        write_to_csv(task.host.name, task.host.hostname, "ERROR", error_msg)
    except SSHException:
        error_msg = "Login failed"
        logger.error(f"{task.host.name}: SSH connection failed")
        write_to_csv(task.host.name, task.host.hostname, "ERROR", error_msg)
    except NornirSubTaskError:
        error_msg = "Login failed"
        logger.error(f"{task.host.name}: Failed to execute command")
        write_to_csv(task.host.name, task.host.hostname, "ERROR", error_msg)
    except Exception as e:
        error_msg = "Login failed"
        logger.error(f"{task.host.name}: Unexpected error: {str(e)}")
        write_to_csv(task.host.name, task.host.hostname, "ERROR", error_msg)

def write_to_csv(hostname, ip_address, interface, rx_power):
    with open('optical_power.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # If file is empty, write header
            writer.writerow(["Hostname", "IP Address", "Interface", "RX Power (dBm)"])
        writer.writerow([hostname, ip_address, interface, rx_power])

def main():
    try:
        # Initialize Nornir
        nr = InitNornir(config_file="config.yaml")
        
        # Clear existing CSV file
        with open('optical_power.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Hostname", "IP Address", "Interface", "RX Power (dBm)"])
        
        # Filter for HP Comware devices and run the task
        result = nr.filter(F(groups__contains="hp_comware")).run(
            task=handle_device_command
        )
        
        print("Task completed. Check optical_power.csv for results.")
        
    except Exception as e:
        logger.error(f"Failed to initialize Nornir: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()