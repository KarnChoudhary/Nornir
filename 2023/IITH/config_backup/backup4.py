import os
from datetime import datetime
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command

# Initialize Nornir with the inventory
nr = InitNornir(config_file="config.yaml")

# Create folders with the current date and time
backup_dir = datetime.now().strftime("%Y-%m-%d")
os.makedirs(backup_dir, exist_ok=True)
arp_inspection_dir = os.path.join(backup_dir, "arp_inspection")
cdp_neighbors_dir = os.path.join(backup_dir, "cdp_neighbors")
vlan_dir = os.path.join(backup_dir, "vlan")
os.makedirs(arp_inspection_dir, exist_ok=True)
os.makedirs(cdp_neighbors_dir, exist_ok=True)
os.makedirs(vlan_dir, exist_ok=True)

# Define a task to get the running configuration
def get_running_config(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command,
        command_string="show running-config"
    )
    return Result(host=task.host, result=result.result)

# Define a task to get ARP inspection details
def get_arp_inspection(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command,
        command_string="show ip arp inspection"
    )
    return Result(host=task.host, result=result.result)

# Define a task to get CDP neighbors details
def get_cdp_neighbors(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command,
        command_string="show cdp neighbors detail | i Device ID:| Port | Platform: | IP address:"
    )
    return Result(host=task.host, result=result.result)

# Define a task to get VLAN details
def get_vlan(task: Task) -> Result:
    result = task.run(
        task=netmiko_send_command,
        command_string="show vlan"
    )
    return Result(host=task.host, result=result.result)

# Define a task to save the running configuration to a file
def save_running_config(task: Task) -> Result:
    config = task.host.data["running_config"]
    hostname = task.host.name
    filename = os.path.join(backup_dir, f"{hostname}.cfg")
    with open(filename, "w") as f:
        f.write(config)
    return Result(host=task.host, result=f"Saved configuration to {filename}")

# Define a task to save the ARP inspection details to a file
def save_arp_inspection(task: Task) -> Result:
    arp_inspection = task.host.data["arp_inspection"]
    hostname = task.host.name
    filename = os.path.join(arp_inspection_dir, f"{hostname}_arp_inspection.txt")
    with open(filename, "w") as f:
        f.write(arp_inspection)
    return Result(host=task.host, result=f"Saved ARP inspection details to {filename}")

# Define a task to save the CDP neighbors details to a file
def save_cdp_neighbors(task: Task) -> Result:
    cdp_neighbors = task.host.data["cdp_neighbors"]
    hostname = task.host.name
    filename = os.path.join(cdp_neighbors_dir, f"{hostname}_cdp_neighbors.txt")
    with open(filename, "w") as f:
        f.write(cdp_neighbors)
    return Result(host=task.host, result=f"Saved CDP neighbors details to {filename}")

# Define a task to save the VLAN details to a file
def save_vlan(task: Task) -> Result:
    vlan = task.host.data["vlan"]
    hostname = task.host.name
    filename = os.path.join(vlan_dir, f"{hostname}_vlan.txt")
    with open(filename, "w") as f:
        f.write(vlan)
    return Result(host=task.host, result=f"Saved VLAN details to {filename}")

# Execute the tasks on all devices in the inventory
results = nr.run(task=get_running_config)
arp_inspection_results = nr.run(task=get_arp_inspection)
cdp_neighbors_results = nr.run(task=get_cdp_neighbors)
vlan_results = nr.run(task=get_vlan)

# Save the results to the backup directory
for host, result in results.items():
    nr.inventory.hosts[host].data["running_config"] = result.result

for host, result in arp_inspection_results.items():
    nr.inventory.hosts[host].data["arp_inspection"] = result.result

for host, result in cdp_neighbors_results.items():
    nr.inventory.hosts[host].data["cdp_neighbors"] = result.result

for host, result in vlan_results.items():
    nr.inventory.hosts[host].data["vlan"] = result.result

nr.run(task=save_running_config)
nr.run(task=save_arp_inspection)
nr.run(task=save_cdp_neighbors)
nr.run(task=save_vlan)

print(f"Backups saved to {backup_dir}")
