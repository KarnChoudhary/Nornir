from netmiko import ConnectHandler

# Replace with your device details
DEVICE_IP = "10.5.48.88"
USERNAME = "iith"
PASSWORD = "HSTLQ@IITH2022"
TFTP_SERVER = "192.168.74.109"
TFTP_FILENAME = "my_switch_config.cfg"

# Connect to the switch
device_params = {
    "device_type": "cisco_ios",
    "ip": DEVICE_IP,
    "username": USERNAME,
    "password": PASSWORD,
}

try:
  # Create connection
  net_connect = ConnectHandler(**device_params)

  # Enter privileged mode
  net_connect.enable()

  # Build the copy command
  copy_command = f"copy running-config tftp://{TFTP_SERVER}/{TFTP_FILENAME}"

  # Send the copy command and handle prompts (optional)
  # This section is commented out as directly including arguments avoids prompts
  # result = net_connect.send_command_timing(copy_command)
  # if "Address or name of remote host" in result:
  #     result += net_connect.send_command_timing(TFTP_SERVER + "\n")
  # if "Destination filename" in result:
  #     result += net_connect.send_command_timing(TFTP_FILENAME + "\n")

  # Execute the copy command with arguments (recommended)
  result = net_connect.send_command(copy_command)

  print(result)

except Exception as e:
  print(f"Error connecting to device: {e}")

finally:
  # Disconnect from the switch
  net_connect.disconnect()
