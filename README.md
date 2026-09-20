# NetworkMonitor

A Python-based network monitoring project that tracks device status changes and detects connectivity problems.

The project starts with simulated monitoring and is designed to later expand into real network monitoring using ping, latency, packet loss, and service checks.

## Features

- Device information loaded from JSON
  - Routers
  - Switches
  - Clients
  - Servers

- Device IP management

- Simulated network monitoring
  - UP
  - WARNING
  - DOWN
  - RECOVERED

- Latency monitoring

- Packet loss monitoring

- Consecutive failure detection
  - A device is marked as DOWN after repeated failures

- Recovery detection
  - Detects when a previously DOWN device becomes reachable again

- Downtime measurement

- Event logging
  - DOWN events
  - RECOVERED events
  - Device name
  - Device IP
  - Recovery time

- Current device status tracking

- Status export to `status.json`

- Simulation mode for development and testing

## Monitoring Logic

NetworkMonitor periodically checks each configured device.

A single failed check does not immediately mark the device as DOWN.

Repeated failures increase the consecutive failure count, and the device is marked as DOWN after the configured threshold is reached.

When a DOWN device becomes available again, NetworkMonitor detects the recovery and records the downtime.

Devices that are reachable but have high latency or packet loss are displayed as WARNING.

## Project Files

```text
NetworkMonitor/
├── main.py
├── devices.json
├── status.json
├── README.md
└── .gitignore