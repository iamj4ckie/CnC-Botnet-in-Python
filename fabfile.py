import json
import logging
from pathlib import Path

from fabric import Connection, task
from fabric.group import ThreadingGroup

logging.basicConfig(
    filename="paramiko.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.getLogger("paramiko").setLevel(logging.DEBUG)

HOSTS_FILE = "hosts.txt"
STATE_FILE = "hosts_state.json"


def save_state(state):
    """Save the state of hosts and passwords to a JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)
    print("State saved to hosts_state.json")


def load_state():
    """Load the state of hosts and passwords from a JSON file."""
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            print("State loaded from hosts_state.json")
            return state
    print("No state file found. Starting fresh.")
    return {"env_hosts": [], "selected_hosts": [], "env_passwords": {}}


def load_hosts_from_file():
    """Load hosts and passwords from the `hosts.txt` file."""
    hosts = []
    passwords = {}
    if Path(HOSTS_FILE).exists():
        with open(HOSTS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    host, password = parts
                else:
                    host, password = parts[0], None
                hosts.append(host)
                if password:
                    passwords[host] = password
    else:
        print("No hosts.txt file found.")
    return hosts, passwords


@task
def load_hosts(c):
    """Load hosts and passwords into state from hosts.txt."""
    hosts, passwords = load_hosts_from_file()
    state = load_state()
    state["env_hosts"] = hosts
    state["env_passwords"].update(passwords)
    save_state(state)
    print(f"Loaded {len(hosts)} hosts.")


@task
def list_hosts(c):
    """List all loaded hosts."""
    state = load_state()
    hosts = state.get("selected_hosts", [])
    if not hosts:
        print("No hosts selected.")
        return
    print("Selected hosts:")
    for host in hosts:
        print(f"- {host}")


@task
def add_host(c, host, password=None):
    """Add a new host to the state and append it to hosts.txt."""
    state = load_state()
    if host not in state["env_hosts"]:
        state["env_hosts"].append(host)
        if password:
            state["env_passwords"][host] = password
        save_state(state)

        with open(HOSTS_FILE, "a") as f:
            if password:
                f.write(f"{host} {password}\n")
            else:
                f.write(f"{host}\n")

        print(f"Host {host} added and saved to hosts.txt.")
    else:
        print(f"Host {host} already exists.")


@task
def select_hosts(c):
    """Select specific hosts to execute commands."""
    state = load_state()
    all_hosts = state.get("env_hosts", [])
    if not all_hosts:
        print("No hosts available to select.")
        return
    print("Available hosts:")
    for idx, host in enumerate(all_hosts):
        print(f"{idx}:{host}")
    selections = input(
        "Enter the indices of hosts to select (comma-separated) - \
            Enter to select all:"
    ).strip()
    selected_hosts = all_hosts
    # If none were selected, choose all the hosts
    if selections:
        selected_indices = [
            int(i) for i in selections.split(",") if i.isdigit()
        ]
        selected_hosts = [
            all_hosts[i] for i in selected_indices if i < len(all_hosts)
        ]
    state["selected_hosts"] = selected_hosts
    save_state(state)
    print(f"Selected {len(selected_hosts)} hosts.")


def build_connections():
    """Build Connection objects from selected hosts."""
    state = load_state()
    selected_hosts = state.get("selected_hosts", [])
    passwords = state.get("env_passwords", {})

    connections = []
    for host in selected_hosts:
        password = passwords.get(host)
        connection = Connection(
            host=host,
            connect_kwargs=({"password": password} if password else {}),
        )
        connections.append(connection)
    return connections


@task
def run_command(c, command):
    """
    Execute a custom command on multiple hosts in parallel using
    ThreadingGroup.
    """
    connections = build_connections()
    if not connections:
        print("No hosts selected.")
        return

    group = ThreadingGroup.from_connections(connections)
    try:
        results = group.run(command, hide=False, pty=False)
        for connection, result in results.items():
            print(f"{connection.host}: {result.stdout.strip()}")
    except Exception as e:
        print(f"Error during command execution: {e}")
