#!/usr/bin/env python3
import dbus
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop
import os
import glob
import argparse

DBusGMainLoop(set_as_default=True)
system_bus = dbus.SystemBus()

parser = argparse.ArgumentParser(description="EPP-Sync: A dynamic power management utility for Linux systems, bridging ACPI power profiles with Energy Performance Preferences (EPP) for optimal power usage and system performance.")
parser.add_argument('-d', '--daemon', help="Run the script as a daemon", action="store_true")
args = parser.parse_args()


with open('/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_available_preferences', 'r') as f:
    epp_profiles = f.read().strip().split()
print("Available EPP Profiles:", epp_profiles)

profile_mapping = {
    'performance': {
        True: 'balance_performance',  # On Battery
        False: 'performance'  # On AC
    },
    'balanced': {
        True: 'balance_power',  # On Battery
        False: 'balance_performance'  # On AC
    },
    'power-saver': {
        True: 'power',  # On Battery
        False: 'balance_power'  # On AC
    }
}

def is_battery_powered():
    upower = dbus.Interface(system_bus.get_object("org.freedesktop.UPower", "/org/freedesktop/UPower/devices/battery_BAT0"), "org.freedesktop.DBus.Properties")
    if upower.Get("org.freedesktop.UPower.Device", 'Type') == 2:  # Battery
        state = upower.Get("org.freedesktop.UPower.Device", 'State')
        return state == 2
    return False


def get_active_power_profile():
    power_profiles = dbus.Interface(system_bus.get_object("net.hadess.PowerProfiles", "/net/hadess/PowerProfiles"), "org.freedesktop.DBus.Properties")
    active_profile = power_profiles.Get("net.hadess.PowerProfiles", "ActiveProfile")
    return active_profile


def set_epp_profile(profile):
    for path in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference"):
        with open(path, 'w') as f:
            f.write(profile)


def update_epp_profile():
    power_profile = get_active_power_profile()
    battery_powered = is_battery_powered()
    epp_profile = profile_mapping.get(power_profile, {}).get(battery_powered)
    if epp_profile in epp_profiles:
        set_epp_profile(epp_profile)
    else:
        print(f"Profile '{epp_profile}' not found in available profiles.")


def signal_handler(*args, **kwargs):
    update_epp_profile()


system_bus.add_signal_receiver(
    signal_handler,
    signal_name="PropertiesChanged",
    dbus_interface="org.freedesktop.DBus.Properties",
    bus_name="net.hadess.PowerProfiles",
    path="/net/hadess/PowerProfiles",
)

system_bus.add_signal_receiver(
    signal_handler,
    dbus_interface="org.freedesktop.DBus.Properties",
    signal_name="PropertiesChanged",
    arg0="org.freedesktop.UPower.Device"
)

update_epp_profile()

if args.daemon:
  try:
      loop = GLib.MainLoop()
      loop.run()
  except KeyboardInterrupt:
      loop.quit()
