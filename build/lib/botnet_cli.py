#!/usr/bin/env python3

import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import argparse
from botnet.fabfile import *
from botnet.utilities import *

commands = {
    'load_hosts': load_hosts,
    'add_host': add_host,
    'print_hosts': print_hosts,
    'check_hosts': check_hosts,
    'select_running_hosts': select_running_hosts,
    'choose_hosts': choose_hosts,
    'run_locally': run_locally,
    'run_command': run_command,
    'execute_script': execute_script,
    'open_shell': open_sh,
    'exit': end,
}

command_descriptions = {
    'load_hosts': "Load host information from an external file.",
    'add_host': "Add a new host to the system.",
    'print_hosts': "Print the list of currently selected hosts.",
    'check_hosts': "Check which hosts are active.",
    'select_running_hosts': "Select only hosts that are currently running.",
    'choose_hosts': "Choose specific hosts.",
    'run_locally': "Execute a command locally on your machine.",
    'run_command': "Execute a command on selected bots.",
    'execute_script': "Run an external script on selected bots.",
    'open_shell': "Open a shell on a selected host.",
    'exit': "Exit the CLI.",
}

def main():

    parser = argparse.ArgumentParser(
        prog = "botnet-cli",
        description = "CLI for botnet management",
    )

    subparsers = parser.add_subparsers(
        title="Commands",
        dest="command", 
        required=True,  
    )

    for cmd, func in commands.items():
        subparsers.add_parser(
            cmd,
            help=command_descriptions.get(cmd, "No description available."),
        )

    args = parser.parse_args()

    command = commands.get(args.command)
    if command:
        command()
    else:
        print(f"Invalid command: {args.command}")

if __name__ == "__main__":
    main()
