# JVM Monitoring Script for Nagios

This Python script monitors a remote Java Virtual Machine (JVM) (e.g., Tomcat/Catalina or any other JVM) via SSH and is designed to integrate with Nagios. It connects to a remote host using an SSH key and retrieves several metrics including CPU, RAM, Garbage Collector status, Heap usage, number of loaded classes, and active threads.

## Features

- **SSH Connection:** Connects to a remote host using an SSH key.
- **Java Process Detection:** Searches for a running Java process using `pgrep -f java` and retrieves its PID.
- **Metrics Monitored:**
  - **CPU Usage:** Monitors the CPU usage of the Java process.
  - **RAM Usage:** Monitors memory usage.
  - **Garbage Collector:** Checks the Garbage Collector status using `jstat -gc`.
  - **Heap:** Displays heap size and usage using `jstat -gccapacity`.
  - **Classes:** Shows the number of loaded classes using `jstat -class`.
  - **Threads:** Displays the number of active threads using `ps -L`.

## Requirements

- **Python 3**
- **Paramiko Library:**  
  Install with:
  ```bash
  pip install paramiko

Remote Host Tools:
Ensure the remote host has the following installed:

pgrep

ps

jstat

Usage
Run the script with the required arguments:
Usage
Run the script with the required arguments:

bash
Copier
./script.py -H <host> -i <ssh_key_path> -m <mode> [options]
Main Arguments
-H, --host: (Required) Remote host to connect to.

-i, --identity: (Required) Path to the SSH key.

-m, --mode: (Required) Monitoring mode. Options:

cpu : Check CPU usage.

ram : Check memory usage.

gc : Check Garbage Collector status.

heap : Display heap size and usage.

classes : Display the number of loaded classes.

threads : Display the number of active threads.

Additional Options
-w, --warning: Warning threshold for metrics (default: 80.0).

-c, --critical: Critical threshold for metrics (default: 90.0).

-u, --user: SSH user (default: root).

--debug: Enable debug mode for verbose output.

--output: Output format: short for concise results or long for detailed output (default: short).

Example
To check CPU usage on host 192.168.1.100 with user admin, using the SSH key at /home/user/.ssh/id_rsa, with a warning threshold of 75% and a critical threshold of 90%, in debug mode with detailed output:

bash
Copier
./script.py -H 192.168.1.100 -i /home/user/.ssh/id_rsa -m cpu -w 75 -c 90 -u admin --output long --debug
Exit Codes (Nagios Convention)
0: OK

1: WARNING

2: CRITICAL

3: UNKNOWN (e.g., SSH connection failure or no Java process found)

Contributing
Contributions, bug fixes, and improvements are welcome. Please open an issue or submit a pull request if you wish to contribute.

License
This script is provided "as is" without any warranty. You are free to use, modify, and redistribute it according to your needs.

© Julien Charbonnel, Conseil départemental de Haute-Loire 2025, assisted by CHATGPT.
