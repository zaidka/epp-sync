# EPP-Sync

EPP-Sync is a power management utility for Linux systems that bridges ACPI power profiles with Energy Performance Preferences (EPP).

## Features

- Dynamically adjusts EPP based on the active ACPI power profile.
- Automatically reacts to changes in power source (AC/battery).
- Can be run as a one-off script or as a continuous background service.
  
## Requirements

- Python 3
- D-Bus
- GLib
- systemd (if running as a service)

## Installation

1. Clone this repository or download the `epp-sync.py` script.

   ```bash
   git clone https://github.com/zaidka/epp-sync.git
   ```

2. Move the `epp-sync.py` script to your desired location.

   ```bash
   mv epp-sync/epp-sync.py /opt/epp-sync/epp-sync.py
   ```

3. Make the script executable.

   ```bash
   chmod +x /opt/epp-sync/epp-sync.py
   ```

## Usage

Before you run this, make sure that you're using a CPU frequency scaling driver that supports Energy Performance Preference (EPP). To check what scaling driver you're using, run:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

And to confirm that it supports EPP, run:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
```

If the file doesn't exist then your scaling driver doesn't support EPP. On my laptop with Ryzen 6800HS using Fedora Silverblue 38, I had to enable the AMD pstate driver (amd-pstate-epp) by passing the kernel argument 'amd_pstate=active'.

Once that's confirmed, check if the EPP profile changes automatically when you change the the ACPI power profile (using the command `powerprofilesctl` or the Power Mode menu in Gnome). If it does change as one would expect, then you don't need to use this script.

You can run the `epp-sync.py` script manually or set it up as a systemd service. Note that this has only been tested on a laptop with Ryzen 6800HS using Fedora Silverblue 38.

### Manual Run

To run the script manually:

```bash
python3 /opt/epp-sync/epp-sync.py
```

The script will run once and exit.

### Run as a Service

To run the script as a systemd service, you need to add a service file:

1. Move the `epp-sync.service` file to the `/etc/systemd/system/` directory.

  ```bash
  mv epp-sync/epp-sync.service /etc/systemd/system/epp-sync.service
  ```

2. Reload the systemd daemon to recognize the new service.

  ```bash
  systemctl daemon-reload
  ```

3. Enable the service to start on boot.

  ```bash
  systemctl enable epp-sync.service
  ```

4. Start the service.

  ```bash
  systemctl start epp-sync.service
  ```

You can check the status of the service with `systemctl status epp-sync.service`.

## License

This project is licensed under the terms of the MIT license.
