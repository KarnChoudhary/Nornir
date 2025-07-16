import csv
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command

# Initialize Nornir
nr = InitNornir(config_file="config.yaml")

def check_device_reachability(task):
    try:
        # Attempt to run a simple command to check if the device is reachable
        task.run(task=netmiko_send_command, command_string="show version", enable=True)
        return {"status": "reachable"}
    except Exception as e:
        # If any exception occurs, the device is not reachable
        return {"status": f"unreachable: {str(e)}"}

# Execute the task on all devices
results = nr.run(task=check_device_reachability)

# Prepare data for CSV
data = [["Hostname", "Status"]]  # Header for the CSV file
unreachable_devices = []
reachable_devices = []

for host, result in results.items():
    status = result[0].result["status"]
    if "unreachable" in status:
        unreachable_devices.append([host, status])
    else:
        reachable_devices.append([host, status])

# Combine unreachable and reachable devices
data += unreachable_devices + reachable_devices

# Write data to CSV file
csv_filename = "switch_reachability_report_sorted.csv"
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)

print(f"Done. Check {csv_filename} for the reachability report.")
