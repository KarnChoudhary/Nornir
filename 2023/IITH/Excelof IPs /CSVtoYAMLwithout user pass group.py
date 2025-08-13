import csv
import yaml
from datetime import datetime

# Path to the CSV file
csv_file = "hosts.csv"

# Reading data from CSV file
with open(csv_file, mode='r') as file:
    csv_reader = csv.DictReader(file)
    yaml_data = {}

    # Converting CSV data to YAML format
    for row in csv_reader:
        host_data = {
            'hostname': row['Hostname'],
            
        }
        yaml_data[row['Host']] = {
            'hostname': host_data['hostname'],
            
        }

# Converting to YAML format
yaml_output = yaml.dump(yaml_data, default_flow_style=False)

# Generating timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Writing YAML output to a text file with timestamp in the file name
output_file = f"hosts_yaml_output_{timestamp}.yaml"
with open(output_file, 'w') as file:
    file.write(yaml_output)

print(f"YAML output saved to {output_file}")