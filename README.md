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

- Use `select-hosts` if you want to select specific hosts to run commands or scripts.

- The current selected hosts are saved to `hosts_state.json`.

- Use `run-command` to execute a command on the hosts in `hosts_state.json`
```sh
# Example
fab run-command "wget example.com"
```
- Use `execute-script` to execute a script:
**Warning**:  This does not work and it is commented out at the moment!
```sh
fab execute-script dummy.py
```

## Docker

```sh
# Building the container
docker build -t fab-botnet .   
# Running the container
# Connecting the container to the network
docker run -d --name fab-botnet --network chn-network fab-botnet
# Confirm network
docker network inspect chn-network
```
