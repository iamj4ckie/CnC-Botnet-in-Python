import json
import logging
import time
import csv
import unicodedata
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from getpass import getpass
from pathlib import Path

from fabric import Connection, task

LOG_FILE = "attack_log.csv"
NUM_THREADS_PER_COWRIE = 3  # Number of threads per Cowrie
logging.basicConfig(
    filename="paramiko.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("paramiko").setLevel(logging.DEBUG)

HOSTS_FILE = "hosts.txt"
STATE_FILE = "hosts_state.json"

if not Path(LOG_FILE).exists():
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "host", "command", "repetition", "response_time"])


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


def clean_text(text):
    """Normalize and remove invalid Unicode characters."""
    if text is None:
        return None
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w@\.\-:]", "", text)  # Allow @ . - : for hostnames/ports
    return text

@task
def add_host(c, host, password=None):
    """Add a new host to the state and append it to hosts.txt."""
    state = load_state()

    # Clean host and password
    host = clean_text(host)
    password = clean_text(password)

    print(f"DEBUG: Cleaned host={repr(host)}, password={repr(password)}")  # Debugging

    # Validate host format (allow colons for ports)
    if not re.match(r"^[\w@\.\-]+(:\d+)?$", host):
        print(f"Invalid host format: {host}")
        return

    if host not in state["env_hosts"]:
        state["env_hosts"].append(host)
        if password:
            state["env_passwords"][host] = password
        save_state(state)

        # Append to hosts.txt
        with open(HOSTS_FILE, "a", encoding="utf-8") as f:
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
        "Enter the indices of hosts to select (comma-separated):"
    ).strip()
    selected_indices = [int(i) for i in selections.split(",") if i.isdigit()]
    selected_hosts = [
        all_hosts[i] for i in selected_indices if i < len(all_hosts)
    ]
    state["selected_hosts"] = selected_hosts
    save_state(state)
    print(f"Selected {len(selected_hosts)} hosts.")


@task
def run_command(c, command, repetitions=1, interval=1):
    """
    Run a command on all selected hosts simultaneously with parallel requests per Cowrie.
    Logs response times to analyze server performance degradation.
    """
    state = load_state()
    hosts = state.get("selected_hosts", [])
    passwords = state.get("env_passwords", {})
    if not hosts:
        print("No hosts selected. Use `select_hosts` to choose hosts.")
        return

    results = {}

    def execute_command(host):
        """Executes the attack command on a single host with multi-threading."""
        password = passwords.get(host)
        if not password:
            password = getpass(f"Password for {host}: ")

        print(f"Connecting to {host}...")

        def run_request(i):
            """Runs a single request and logs the response time."""
            try:
                connection = Connection(host=host, connect_kwargs={"password": password})
                start_time = time.time()
                result = connection.run(command, hide=True)
                response_time = time.time() - start_time

                log_entry = [time.strftime("%Y-%m-%d %H:%M:%S"), host, command, i+1, response_time]
                with open(LOG_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(log_entry)

                print(f"[{host}] Repetition {i+1}: Response Time = {response_time:.4f} sec")
                return response_time
            except Exception as e:
                print(f"Error on {host}: {e}")
                return None

        for i in range(repetitions):
            with ThreadPoolExecutor(max_workers=NUM_THREADS_PER_COWRIE) as executor:
                futures = [executor.submit(run_request, i) for _ in range(NUM_THREADS_PER_COWRIE)]
                for future in as_completed(futures):
                    future.result()  # Wait for all requests to complete

            time.sleep(interval)

        results[host] = f"{repetitions} repetitions completed"

    with ThreadPoolExecutor() as executor:
        executor.map(execute_command, hosts)

    print("\nCommand Execution Results:")
    for host, output in results.items():
        print(f"{host}: {output}")

    print("\nAttack log saved in attack_log.csv.")