import json
from fabric import Connection, Group, task
from pathlib import Path
from getpass import getpass
import logging

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
    """Add a new host to the state."""
    state = load_state()
    if host not in state["env_hosts"]:
        state["env_hosts"].append(host)
        if password:
            state["env_passwords"][host] = password
        save_state(state)
        print(f"Host {host} added.")
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
        "Enter the indices of hosts to select (comma-separated):"
    ).strip()
    selected_indices = [int(i) for i in selections.split(",") if i.isdigit()]
    selected_hosts = [all_hosts[i] for i in selected_indices if i < len(all_hosts)]
    state["selected_hosts"] = selected_hosts
    save_state(state)
    print(f"Selected {len(selected_hosts)} hosts.")


@task
def run_command(c, command):
    """Run a command on all selected hosts."""
    state = load_state()
    hosts = state.get("selected_hosts", [])
    passwords = state.get("env_passwords", {})
    if not hosts:
        print("No hosts selected. Use `select_hosts` to choose hosts.")
        return

    results = {}
    for host in hosts:
        password = passwords.get(host)
        if not password:
            password = getpass(f"Password for {host}: ")

        print(f"Connecting to {host}...")
        try:
            connection = Connection(host=host, connect_kwargs={"password": password})
            result = connection.run(command, hide=True)
            print(f"Success on {host}: {result.stdout.strip()}")
            results[host] = result.stdout.strip()
        except Exception as e:
            print(f"Error on {host}: {e}")
            results[host] = str(e)

    print("\nCommand Execution Results:")
    for host, output in results.items():
        print(f"{host}: {output}")


# This doesn't work
# @task
# This is only with python so far
# def execute_script(c, script_file):
#     """Execute a script file on all selected hosts."""
#     state = load_state()
#     hosts = state.get("selected_hosts", [])
#     passwords = state.get("env_passwords", {})
#     if not hosts:
#         print("No hosts selected. Use `select_hosts` to choose hosts.")
#         return

#     script_name = Path(script_file).name
#     remote_path = f"/tmp/{script_name}"

#     for host in hosts:
#         password = passwords.get(host)
#         if not password:
#             password = getpass(f"Password for {host}: ")

#         print(f"Uploading and executing script {script_file} on {host}...")
#         try:
#             connection = Connection(host=host, connect_kwargs={"password": password})

#             connection.put(script_file, remote=remote_path)

#             result = connection.run(f"python3 {remote_path}", hide=False)
#             print(f"Success on {host}: {result.stdout.strip()}")

#         except Exception as e:
#             print(f"Error on {host}: {e}")
#         finally:
#             try:
#                 connection.run(f"rm -f {remote_path}/{script_name}", hide=True)
#             except Exception as cleanup_error:
#                 print(f"Cleanup failed on {host}: {cleanup_error}")
