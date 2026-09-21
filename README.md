# NetworkMonitor

> **Live monitoring companion project for NetFaultLab**
>
> Observes real Containerlab state and connectivity to detect `WARNING`, `DOWN`, and `RECOVERED` events.

> 🚧 **This project is currently under active development.**
>
> Live NetFaultLab monitoring, dynamic device refresh, and status-change detection are implemented, while monitoring coverage, UI, testing, and documentation are still being improved.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Docker](https://img.shields.io/badge/Docker-Monitoring-blue)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Output](https://img.shields.io/badge/Output-JSON%20%7C%20Logs-lightgrey)

## Project at a Glance

| Item | Details |
|---|---|
| Goal | Live monitoring of NetFaultLab |
| Data Source | `lab_state.json` + direct Docker/Containerlab checks |
| Client Check | Real ping to server |
| Server Check | Ping to default gateway |
| Router/Switch Check | Container and lab-facing interface state |
| States | `UP`, `WARNING`, `DOWN`, `RECOVERED` |

## Example Output

```text
[00:42:24] PC2       CLIENT   WARNING   | Failure 1/3
[00:42:26] PC2       CLIENT   WARNING   | Failure 2/3
[00:42:28] PC2       CLIENT   DOWN
[00:42:41] PC2       CLIENT   RECOVERED | Downtime: 13.02 seconds
```

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Device Checks](#device-checks)
- [Status Logic](#status-logic)
- [Dynamic Topology Refresh](#dynamic-topology-refresh)
- [Usage](#usage)
- [Current Limitations](#current-limitations)

NetworkMonitor is a companion monitoring project for NetFaultLab. It reads the currently active NetFaultLab topology, checks the real Containerlab environment, and reports device and connectivity state changes.

Unlike the original simulation-only prototype, the current version monitors the live lab created by NetFaultLab.

[한국어 README](README_KR.md)

## Features

- Reads live topology data from NetFaultLab `lab_state.json`
- Automatically refreshes the device list when the NetFaultLab topology changes
- Removes devices that no longer exist
- Adds newly created devices automatically
- Checks real Docker/Containerlab state
- Client-to-server ping monitoring
- Server-to-gateway ping monitoring
- Router/switch interface-state monitoring
- Consecutive-failure based `WARNING` and `DOWN`
- `RECOVERED` detection with downtime calculation
- Event logging to `logs.txt`
- Current status output to `status.json`
- State-change-only console output to reduce noise

## How It Works

```text
NetFaultLab
    |
    | lab_state.json
    v
NetworkMonitor
    |
    +-- Docker container state
    +-- Client -> Server ping
    +-- Server -> Gateway ping
    +-- Router/Switch interface state
```

NetworkMonitor does not receive the answer to the injected fault. It reads topology information and independently checks the real lab.

## Device Checks

### Clients

Clients are checked with real end-to-end ping tests to the current server.

This can reveal the effects of:

- Wrong IP
- Wrong Default Gateway
- Wrong Static Route
- Interface Down
- ACL Block

### Servers

Servers are checked against their configured default gateway.

### Routers and Switches

Router and switch containers are checked for:

- running container state
- Lab-facing interface state

The Containerlab management interface `eth0` is excluded from Lab link checks.

## Status Logic

A failed check does not immediately mark a device as down.

Default behavior:

```text
Failure 1 -> WARNING
Failure 2 -> WARNING
Failure 3 -> DOWN
```

The threshold can be changed with:

```python
down_threshold = 3
```

When connectivity returns after a confirmed outage:

```text
RECOVERED
```

is reported together with downtime.

## Dynamic Topology Refresh

NetworkMonitor reloads `lab_state.json` during monitoring.

If NetFaultLab changes from:

```text
R1 R2 R3 SW1 PC1 PC2 Server1
```

to:

```text
R1 SW1 SW2 PC1 PC2 PC3 Server1
```

NetworkMonitor automatically:

- removes R2/R3 monitoring state
- adds SW2/PC3
- clears stale failure counters
- saves only currently active devices to `status.json`

## Console Output

By default:

```python
show_all_checks = False
```

Only state changes are printed, which keeps the console readable.

Example:

```text
NetworkMonitor Started
Topology: Branch Network
Devices: 8
Mode: STATE CHANGES

[00:42:10] R1        ROUTER   UP
[00:42:10] PC1       CLIENT   UP
[00:42:24] PC2       CLIENT   WARNING   | Failure 1/3
[00:42:26] PC2       CLIENT   WARNING   | Failure 2/3
[00:42:28] PC2       CLIENT   DOWN
[00:42:41] PC2       CLIENT   RECOVERED | Downtime: 13.02 seconds
```

For verbose output:

```python
show_all_checks = True
```

## Files

### `lab_state.json`

Created by NetFaultLab and read by NetworkMonitor.

### `status.json`

Stores the latest status of currently active devices.

Example:

```json
{
    "R1": "UP",
    "SW1": "UP",
    "PC1": "UP",
    "PC2": "DOWN",
    "Server1": "UP"
}
```

### `logs.txt`

Records meaningful events such as:

```text
PC2 192.168.10.11 DOWN | 00:42:28
PC2 192.168.10.11 RECOVERED | 00:42:41 | Downtime: 13.02 seconds
```

## Requirements

- Python 3
- Docker Engine
- A running NetFaultLab topology
- `../NetFaultLab/lab_state.json`

## Usage

Start NetFaultLab first:

```bash
cd ~/NetFaultLab
python3 main.py
```

Then start NetworkMonitor in another terminal:

```bash
cd ~/NetworkMonitor
python3 main.py
```

Keep NetworkMonitor running while using NetFaultLab commands such as:

```text
inject
configure
verify
```

NetworkMonitor should detect state changes while the lab remains active.

Stop monitoring with:

```text
Ctrl + C
```

## Current Limitations

- Monitoring logic is designed specifically around the current NetFaultLab topology model.
- Router and switch health is currently based mainly on container and interface state rather than full protocol-level health.
- Only the current first server is used as the main client end-to-end ping target.
- SNMP, streaming telemetry, and external alert integrations are not implemented.
- The project is intended for lab and portfolio use, not production monitoring.

## Related Project

NetFaultLab creates the network, injects faults, and provides the troubleshooting CLI. NetworkMonitor observes the running lab independently and reports operational state changes.
