from nornir import InitNornir

from napalm import get_network_driver


def copy_config(host):
    driver = get_network_driver(host.get_connection_platform())
    device = driver(hostname=host.hostname, username=host.username, password=host.password)
    device.open()

    # Build copy command
    tftp_server = "192.168.74.109"
    tftp_filename = "my_switch_config.cfg"
    copy_command = f"copy running-config tftp://{tftp_server}/{tftp_filename}"

    # Execute copy command
    device.cli(commands=[copy_command])

    # Close connection
    device.close()


# Initialize Nornir with the inventory file (assuming hosts.yaml)
nr = InitNornir(config_file="hosts.yaml")

# Loop through each host in Nornir inventory
for host, _data in nr.inventory.hosts.items():
    copy_config(host)
