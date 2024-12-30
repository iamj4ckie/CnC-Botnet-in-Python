## Containirised Botnet

This approach was created due to dependencies and build erros on macOS. In a realistic scenario, the botnet would not be on the same network as the honeypots since in this context the cowrie instances are used as a mean to attack victims.

## Setup Instructions

1. Build the botnet image
    ```bash
    docker build -t fab-botnet .
    ```

2. Run the container:
    ```bash
    docker run -d --name fab-botnet fab-botnet
    ```

3. Connect the botnet container to the network used by the honeypots:   
    ```bash
    docker network connect chn-network fab-botnet
    ```

4. Access the container 
```bash
docker exec -it fab-botnet fab -l
```

Once you are inside the container you can execute the the botnet commands as on the README.md

The run-command is enhanced with positional (optional) arguments to make the attacks repititive in intervals for DDoS simulation. 

---

### Dynamic Victim

To attack the dynamic victim behind the reverse proxy, you can use the following:

**Using `curl`:**
```bash
fab run-command "curl http://reverse-proxy/dynamic" --repetitions 100 --interval 1
```

**Using `wget`:**
```bash
fab run-command "wget http://reverse-proxy/dynamic" --repetitions 100 --interval 1
```

The above commands will repeatedly request the `/dynamic` endpoint of the reverse proxy at the specified interval (1 second in this case), simulating repeated load or a basic DDoS scenario.

---

### Static Victim

To attack the static victim behind the reverse proxy, use:

**Using `curl`:**
```bash
fab run-command "curl http://reverse-proxy/static" --repetitions 100 --interval 1
```

**Using `wget`:**
```bash
fab run-command "wget http://reverse-proxy/static" --repetitions 100 --interval 1
```

Similar to the dynamic victim, this will repeatedly target the `/static` endpoint of the reverse proxy.

---

## Using `ping`

**Example Command:**
```bash
fab run-command "ping -c 10 reverse-proxy" --repetitions 5 --interval 1
```

The `ping` command tests the reachability of the reverse proxy by sending ICMP packets. It provides metrics such as round-trip time and packet loss.

### Why `ping` Cannot Reach the Victims via the Proxy
- The reverse proxy (NGINX) handles requests at the **HTTP layer** and forwards them to the victims based on the configured paths (`/dynamic` and `/static`).
- `ping` uses the **ICMP protocol**, which operates at a lower network layer. Since NGINX does not process or forward ICMP packets, the `ping` requests stop at the reverse proxy and do not reach the victims.
- As a result, `ping` can only verify the connectivity to the reverse proxy itself but cannot interact with the dynamic or static victims.

---




