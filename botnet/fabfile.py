import os
import json
import fabric.colors as fab_col
import getpass
import paramiko
from fabric.api import (env, run, sudo, execute, local, settings, hide,
                        open_shell, parallel, serial, put)
from fabric.contrib.console import confirm
from tabulate import tabulate

file_hosts = 'hosts.txt'
state_file = 'hosts_state.json'  # File to persist state
paramiko.util.log_to_file('paramiko.log')
env.colorize_errors = True
selected_hosts = []  # Initialize selected_hosts as an empty list
running_hosts = {}
env.connection_attempts = 2
env.passwords = {}  # Ensure passwords are initialized


# Save the state of env.hosts and selected_hosts to a JSON file
def save_state():
    """Save the state of env.hosts and selected_hosts to a JSON file."""
    state = {
        "env_hosts": env.hosts,
        "selected_hosts": selected_hosts,
        "env_passwords": env.passwords
    }
    with open(state_file, "w") as f:
        json.dump(state, f, indent=4)
    print("Debug: State saved to hosts_state.json")


# Load the state of env.hosts and selected_hosts from a JSON file
def load_state():
    """Load the state of env.hosts and selected_hosts from a JSON file."""
    global selected_hosts
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            state = json.load(f)
            env.hosts = state.get("env_hosts", [])
            selected_hosts = state.get("selected_hosts", [])
            env.passwords = state.get("env_passwords", {})
            print("Debug: State loaded from hosts_state.json")
            print(f"  env.hosts = {env.hosts}")
            print(f"  selected_hosts = {selected_hosts}")
    else:
        print("Debug: No state file found. Starting fresh.")


def load_hosts():
    """Load hosts from `hosts.txt` file."""
    global selected_hosts
    print("Loading hosts from hosts.txt...")
    with open(file_hosts, 'r') as f:
        data = f.readlines()
        for line in data:
            try:
                host, password = line.strip().split()
                print(f"Host: {host}, Password: {password}")
            except ValueError:
                host = line.strip()
                password = None
                print(f"Host: {host}, No password provided.")
            if len(host.split(':')) == 1:
                host = f'{host}:22'
                print(f"No port specified. Defaulting to: {host}")
            env.hosts.append(host)
            if password:
                env.passwords[host] = password.strip()
        env.hosts = list(set(env.hosts))  # Remove duplicates
    selected_hosts = env.hosts.copy()
    debug_state("load_hosts")
    save_state()


def print_hosts():
    """Print selected hosts."""
    global selected_hosts
    load_state()  # Load the state before printing
    debug_state("print_hosts")
    if not selected_hosts:
        print(fab_col.red("No hosts selected or loaded."))
        return
    hosts = map(lambda x: [x, env.passwords.get(x, None)], selected_hosts)
    print(fab_col.green(tabulate(hosts, ['Host', 'Password'])))


def check_hosts():
    """Check if hosts are active or not and print the result."""
    global running_hosts
    load_state()  # Load the state before checking
    running_hosts = {}
    for host in selected_hosts:
        print(fab_col.magenta("\nPinging host: %s" % host))
        response = os.system("ping -c 1 " + host.split("@")[1].split(":")[0])
        running_hosts[host] = response == 0
    mylist = map(lambda x: [x[0], str(x[1])], running_hosts.items())
    print(fab_col.green(tabulate(mylist, ["Host", "Running"])))


def select_running_hosts():
    """Select all active hosts."""
    global selected_hosts
    load_state()  # Load state before filtering
    debug_state("select_running_hosts")
    with hide('stdout'):
        check_hosts()
    selected_hosts = list(filter(lambda x: running_hosts.get(x, False), running_hosts.keys()))
    print(fab_col.green(f"Selected running hosts: {selected_hosts}"))
    save_state()  # Save updated state


def choose_hosts():
    """Select the hosts to be used."""
    global selected_hosts
    load_state()  # Load the state before choosing hosts
    debug_state("choose_hosts")
    if not env.hosts:
        print(fab_col.red("No hosts loaded. Use `load_hosts` first."))
        return
    mylist = [[num, h] for num, h in enumerate(env.hosts)]
    print(fab_col.blue('Select Hosts (space-separated):'))
    print(fab_col.blue(tabulate(mylist, ['Number', 'Host'])))
    choices = input('> ').split()
    choices = [int(c) for c in choices if c.isdigit() and int(c) < len(env.hosts)]
    if not choices:
        print(fab_col.yellow("No valid hosts selected. Keeping current selection."))
        return
    selected_hosts = [env.hosts[i] for i in choices]
    print(fab_col.green(f"Selected hosts: {selected_hosts}"))
    save_state()  # Save updated state


def add_host():
    """Add a new host to the running hosts."""
    global selected_hosts
    load_state()  # Load state before adding hosts
    name = input('Username (default: root): ') or 'root'
    host = input('Host: ')
    port = input('Port (default: 22): ') or '22'
    if not host:
        print(fab_col.red("Error: Hostname cannot be empty."))
        return
    try:
        port = int(port)
    except ValueError:
        print(fab_col.red("Error: Port must be a valid number."))
        return

    new_host = f'{name}@{host}:{port}'
    selected_hosts.append(new_host)
    password = None
    if confirm('Authenticate using a password? '):
        password = getpass.getpass('Password: ').strip()
        env.passwords[new_host] = password

    # Add to hosts.txt
    if confirm('Add the new host to the hosts file? '):
        with open(file_hosts, 'a') as f:
            if password:
                f.write(f'{new_host} {password}\n')
            else:
                f.write(f'{new_host}\n')
    save_state()  # Save updated state


@parallel
def run_command(cmd=None):
    """Execute a command on selected hosts."""
    global selected_hosts
    load_state()  # Load the state before running commands
    debug_state("run_command")
    if not selected_hosts:
        print(fab_col.red("No hosts selected. Use `load_hosts` or `choose_hosts` to select hosts."))
        return
    if not cmd:
        cmd = input('Insert command: ')
    if cmd.strip()[:4] == 'sudo':
        execute(_execute_sudo, cmd, hosts=selected_hosts)
    else:
        execute(_execute_command, cmd, hosts=selected_hosts)


def debug_state(function_name):
    """Debugging helper to print current state."""
    print(f"Debug ({function_name}):")
    print(f"  env.hosts = {env.hosts}")
    print(f"  selected_hosts = {selected_hosts}")
    print(f"  env.passwords = {env.passwords}")


def run_locally(cmd=None):
    """Execute a command locally."""
    if not cmd:
        cmd = input('Insert command: ')
    with settings(warn_only=True):
        local(cmd)

@serial
def _execute_sudo(command):
    """Execute a sudo command on a host."""
    with settings(warn_only=True):
        return sudo(command[4:].strip(), shell=True)


@parallel
def _execute_command(command):
    """Execute a command on a host."""
    with settings(warn_only=True):
        try:
            print(f"Executing command '{command}' on host {env.host}")
            result = run(command)
            print(f"Command executed successfully. Output:\n{result}")
            return result
        except Exception as e:
            print(fab_col.red(f"Error execution in host {env.host}: {e}"))
            return None

@parallel
def run_command(cmd=None):
    """Execute a command on selected hosts."""
    global selected_hosts
    load_state()  # Load state before running the command
    if not selected_hosts:
        print(fab_col.red("No hosts selected. Use `load_hosts` or `choose_hosts` to select hosts."))
        return
    if not cmd:
        cmd = input('Insert command: ')
    if cmd.strip()[:4] == 'sudo':
        execute(_execute_sudo, cmd, hosts=selected_hosts)
    else:
        execute(_execute_command, cmd, hosts=selected_hosts)

@parallel
def execute_script():
    """Execute a script file on selected hosts."""
    global selected_hosts
    load_state()  # Load state before executing the script

    # Check if hosts are available
    if not selected_hosts:
        print(fab_col.red("No hosts selected. Use `load_hosts` or `choose_hosts` to select hosts."))
        return

    # Script input
    script_file = input('Name of the script: ')
    remote_path = '~/'
    if len(script_file) < 4 or '..' in script_file:
        print(fab_col.red('Error. Invalid script name.'))
        return

    # Upload script to hosts
    for h in selected_hosts:
        with settings(host_string=h):
            with hide('running'):
                put(script_file, remote_path, mode=777)

    # Determine script extension
    script_file = script_file.split('/')[-1]
    extension = script_file.split('.')[-1]
    if extension == script_file:
        print(fab_col.red('Invalid script'))
        return

    # Execute script based on extension
    if extension == 'py':
        run_command(f'python {remote_path}{script_file}')
    elif extension in ['sh', 'bash']:
        run_command(f'bash {remote_path}{script_file}')
    else:
        print(fab_col.red('Extension not supported'))

    # Delete the script after execution
    with hide('running', 'stdout'):
        run_command(f'rm -f {remote_path}{script_file}')


def open_sh():
    """Open a shell on a selected host."""
    global selected_hosts
    load_state()  # Load state before opening a shell
    debug_state("open_sh")
    mylist = [[num, h] for num, h in enumerate(selected_hosts)]
    print(fab_col.blue(tabulate(mylist, ['Number', 'Host'])))
    try:
        n = int(input('Open shell in host number: '))
        h = selected_hosts[n]
        execute(open_shell, host=h)
    except (ValueError, IndexError):
        print(fab_col.red('Error: invalid host selection.'))

