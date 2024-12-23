import csv

# Open the CSV file
with open('csv.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)

    # Open the DOT file for writing
    with open('network_topology.dot', 'w') as dotfile:
        dotfile.write('graph Network {\n')

        # Dictionary to keep track of defined nodes
        defined_nodes = {}

        # Write nodes and edges
        for row in reader:
            device = row['Device Name'].replace('-', '_')
            neighbor = row['Neighbor Device Name'].replace('-', '_')
            link_type = row['Link Type']
            interface_device = row['Interface Device Side']
            interface_neighbor = row['Interface Neighbor Side']
            cores = row['Number of Cores']
            switch_model = row['Switch Model']
            ip_address = row['IP address of switch']

            # Write node attributes if not already defined or update if already defined
            if device not in defined_nodes:
                dotfile.write(f'    {device} [label="{device}\\n{ip_address}\\n{switch_model}"];\n')
                defined_nodes[device] = (ip_address, switch_model)
            else:
                # Update the node label if the IP address or model number is different
                existing_ip, existing_model = defined_nodes[device]
                if ip_address != existing_ip or switch_model != existing_model:
                    dotfile.write(f'    {device} [label="{device}\\n{ip_address}\\n{switch_model}"];\n')
                    defined_nodes[device] = (ip_address, switch_model)

            if neighbor not in defined_nodes:
                dotfile.write(f'    {neighbor} [label="{neighbor}"];\n')
                defined_nodes[neighbor] = ('', '')  # Neighbor might not have an IP address or switch model
            else:
                # Update the neighbor label if the IP address or model number is different
                existing_ip, existing_model = defined_nodes[neighbor]
                if ip_address != existing_ip or switch_model != existing_model:
                    dotfile.write(f'    {neighbor} [label="{neighbor}\\n{ip_address}\\n{switch_model}"];\n')
                    defined_nodes[neighbor] = (ip_address, switch_model)

            # Write edge attributes
            edge_label = f'{link_type}\\n{interface_device} - {interface_neighbor}'
            if link_type == 'Fiber':
                edge_label += f'\\nCores: {cores}'
            dotfile.write(f'    {device} -- {neighbor} [label="{edge_label}"];\n')

        dotfile.write('}\n')
