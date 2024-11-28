# CnC-Botnet-in-Python
C&#38;C Botnet written in Python

## Description
Simple botnet written in Python using fabric. 
<p>
The author is not responsible for the use of this code.

## Hosts
It is possible to load hosts from a file _hosts.txt_ included in the main directory of the project.
The default format for this file is:
```bash
username@host:port password
```

If the port number is not declared, port 22 is used:
```bash
username@host password
```
SSH connection is the default authentication way, so if the host knows the public key of the user, it is not necessary to indicate the password:
```bash
username@host
```

## Usage
To start the application, simply download the repository
```bash
git clone https://github.com/marcorosa/CnC-Botnet-in-Python
cd CnC-Botnet-in-Python
```

Install the dependencies
```bash
pip install -r requirements.txt
```

Install the Package 
```bash
pip install .
```

Create the _hosts.txt_ file (optional, see above).

Run the CLI
```bash
botnet-cli <command>
```

## Command List

The following commands are available in the CLI:

- **`load_hosts`**: Load hosts from the `_hosts.txt` file.
- **`add_host`**: Add a new host to the system.
- **`print_hosts`**: Print the list of currently selected hosts.
- **`check_hosts`**: Check which hosts are active.
- **`select_running_hosts`**: Select only hosts that are currently running.
- **`choose_hosts`**: Manually choose specific hosts.
- **`run_locally`**: Execute a command locally.
- **`run_command`**: Execute a command on selected bots.
- **`execute_script`**: Run an external script on selected bots.
- **`open_shell`**: Open a shell on a selected host.
- **`exit`**: Exit the CLI.
