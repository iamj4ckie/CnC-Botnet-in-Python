from simple_term_menu import TerminalMenu
import sys


def choice_error():
    print("Choice does not exist")


def end():
    sys.exit(0)


def menu():
    descriptions = [
        "Load host from external file",
        "Add a new host",
        "Print selected hosts",
        "Check active hosts",
        "Select only active hosts",
        "Select bots",
        "Execute command locally",
        "Execute command on bots",
        "Run external script",
        "Open shell in a host",
        "Exit",
    ]

    terminal_menu = TerminalMenu(descriptions, title="Menu")
    choice_index = terminal_menu.show()

    if choice_index is not None:
        return choice_index  
    else:
        choice_error()
        return None

