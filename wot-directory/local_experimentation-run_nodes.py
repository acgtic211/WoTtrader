import os
import subprocess
import time
import psutil

# Define the ports and database names
ports = [3021, 3022, 3023, 3024, 3025, 3026, 3027, 3028]
databases = ["node1-database", "node2-database", "node3-database", "node4-database", "node5-database", "node6-database", "node7-database", "node8-database"]

# Function to update the .env file
def update_env_file(port, database):
    with open('.env', 'r') as file:
        lines = file.readlines()

    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith('WEB_APP_PORT='):
                file.write(f'WEB_APP_PORT={port}\n')
            elif line.startswith('MONGODB_DATABASE='):
                file.write(f'MONGODB_DATABASE={database}\n')
            elif line.startswith('FUSEKI_URI_DEVELOPMENT='):
                file.write(f'FUSEKI_URI_DEVELOPMENT=http://localhost:{port+100}/wottrader\n')
            else:
                file.write(line)

# Function to kill processes running on specified ports
def kill_processes_on_ports(ports):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            connections = proc.connections()
            for conn in connections:
                if conn.laddr.port in ports:
                    print(f"Killing process {proc.info['pid']} on port {conn.laddr.port}")
                    proc.kill()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

# Function to close terminal windows
def close_terminal_windows():
    subprocess.call(['taskkill', '/F', '/IM', 'cmd.exe'])

# Kill existing processes on specified ports and close Visual Studio Code terminals
kill_processes_on_ports(ports)
#close_terminal_windows()

# Loop through the ports and databases
for port, database in zip(ports, databases):
    # Update the .env file
    update_env_file(port, database)
    
    # Run the application in a new terminal
    subprocess.Popen(['cmd', '/k', 'npm run dev'], creationflags=subprocess.CREATE_NEW_CONSOLE)

    # Introduce a delay to ensure the previous instance starts before the next one
    time.sleep(4)