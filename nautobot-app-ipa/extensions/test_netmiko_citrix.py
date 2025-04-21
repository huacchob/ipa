from netmiko import BaseConnection, ConnectHandler

netscaler = {
    "device_type": "netscaler",  # Use terminal_server for raw session handling
    "host": "192.168.100.10",
    "username": "nsroot",  # placeholder, may be required
    "password": "nsroot",  # placeholder
    "port": 22,
}

# Establish raw connection
net_connect: BaseConnection = ConnectHandler(**netscaler)

# Step 1: Issue `login` command
output = net_connect.send_command_timing(command_string="nscli")
output = net_connect.send_command_timing(command_string="login")
print(output)

# Step 2: Respond to Username prompt
if "userName" in output:
    # output += net_connect.send_command_timing(command_string="nsroot")
    net_connect.send_command_timing(command_string="nsroot")
    net_connect.send_command_timing(command_string="nsroot")
    print(output)

# Step 5: Now issue actual CLI commands
commands: list[str] = [
    "set ns hostname NS1",
    "enable feature lb",
    "save ns config",
]

for cmd in commands:
    response = net_connect.send_command_timing(command_string=cmd)
    print(f"Output of `{cmd}`:\n{response}\n")

# Step 6: Disconnect
net_connect.disconnect()
