
#!/usr/bin/env python3

import platform
import json
import os
import shutil
import subprocess
import time
import argparse


def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except (OSError, ValueError):
        return None

def read_cpu_frequency():
    paths = [
        "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq",
        "/sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq",
        "/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq",
    ]

    for path in paths:
        frequency = read_file(path)

        if frequency:
            try:
                return round(int(frequency) / 1000)
            except ValueError:
                continue

    return None

def read_cpu():

    def counters():
        contents = read_file("/proc/stat")
        if not contents:
            return None

        # Only read the aggregate CPU line, not cpu0, cpu1, etc.
        line = contents.splitlines()[0]
        parts = line.split()

        if not parts or parts[0] != "cpu":
            return None

        return list(map(int, parts[1:]))


    first = counters()
    time.sleep(0.25)
    second = counters()

    if not first or not second:
        return {}

    total1 = sum(first)
    total2 = sum(second)

    idle1 = first[3] + first[4]
    idle2 = second[3] + second[4]

    total_delta = total2 - total1
    idle_delta = idle2 - idle1

    usage = 0
    if total_delta > 0:
        usage = 100 * (total_delta - idle_delta) / total_delta

    frequency = read_cpu_frequency()

    return {
        "usage": round(max(0, min(100, usage)), 1),
        "frequency": frequency
    }


def read_memory():
    values = {}

    for line in (read_file("/proc/meminfo") or "").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            values[parts[0].rstrip(":")] = int(parts[1])

    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", 0)
    swap_total = values.get("SwapTotal", 0)
    swap_free = values.get("SwapFree", 0)

    used = total - available
    swap_used = swap_total - swap_free

    return {
        "total": round(total / 1024, 0),
        "used": round(used / 1024, 0),
        "available": round(available / 1024, 0),
        "usage": round(used / total * 100, 1) if total else 0,
        "swap_usage": round(
            swap_used / swap_total * 100, 1
        ) if swap_total else 0
    }



def read_battery():
    base_path = "/sys/class/power_supply"

    try:
        devices = os.listdir(base_path)
    except OSError:
        return None

    batteries = []

    for device in devices:
        base = os.path.join(base_path, device)

        if read_file(f"{base}/type") != "Battery":
            continue

        capacity = read_file(f"{base}/capacity")

        energy_now = read_file(f"{base}/energy_now")
        energy_full = read_file(f"{base}/energy_full")
        energy_design = read_file(f"{base}/energy_full_design")

        charge_now = read_file(f"{base}/charge_now")
        charge_full = read_file(f"{base}/charge_full")
        charge_design = read_file(f"{base}/charge_full_design")

        # Prefer energy measurements, but fall back to charge.
        now = energy_now or charge_now
        full = energy_full or charge_full
        design = energy_design or charge_design

        try:
            now = int(now) if now else None
            full = int(full) if full else None
            design = int(design) if design else None
        except ValueError:
            now = full = design = None

        try:
            charge = int(capacity) if capacity else None
        except ValueError:
            charge = None

        if charge is None and now is not None and full:
            charge = round(now / full * 100)

        health = None
        if full is not None and design is not None and design > 0:
            health = round(full / design * 100, 1)

        cycles = read_file(f"{base}/cycle_count")

        try:
            cycles = int(cycles) if cycles else None
        except ValueError:
            cycles = None

        # Energy values are reported in microWh by Linux sysfs.
        energy = (
            round(int(energy_now) / 1000000, 2)
            if energy_now else None
        )
        full_energy = (
            round(int(energy_full) / 1000000, 2)
            if energy_full else None
        )

        batteries.append({
            "name": device,
            "charge": charge,
            "health": health,
            "energy": energy,
            "full_energy": full_energy,
            "cycles": cycles,
            "status": read_file(f"{base}/status"),
            "capacity_value": full,
            "design_value": design
        })

    if not batteries:
        return None

    # Combine battery charge using capacity-weighted percentages.
    total_current = sum(
        battery["capacity_value"]
        for battery in batteries
        if battery["capacity_value"] is not None
    )

    total_full = sum(
        battery["capacity_value"]
        for battery in batteries
        if battery["capacity_value"] is not None
    )

    charge = None

    if total_full > 0:
        weighted_charge = sum(
            battery["charge"] * battery["capacity_value"]
            for battery in batteries
            if battery["charge"] is not None
            and battery["capacity_value"] is not None
        )

        charge_capacity = sum(
            battery["capacity_value"]
            for battery in batteries
            if battery["charge"] is not None
            and battery["capacity_value"] is not None
        )

        if charge_capacity:
            charge = round(weighted_charge / charge_capacity)

    # Combine health using design capacity as the weighting factor.
    health_numerator = 0
    health_denominator = 0

    for battery in batteries:
        full = battery["capacity_value"]
        design = battery["design_value"]

        if full is not None and design is not None and design > 0:
            health_numerator += full
            health_denominator += design

    health = (
        round(health_numerator / health_denominator * 100, 1)
        if health_denominator else None
    )

    # Aggregate energy only when every battery provides energy readings.
    energy = None
    full_energy = None

    if all(b["energy"] is not None for b in batteries):
        energy = round(sum(b["energy"] for b in batteries), 2)

    if all(b["full_energy"] is not None for b in batteries):
        full_energy = round(
            sum(b["full_energy"] for b in batteries), 2
        )

    # A single cycle count is meaningful only for one battery.
    cycles = batteries[0]["cycles"] if len(batteries) == 1 else None

    statuses = {
        battery["status"]
        for battery in batteries
        if battery["status"]
    }

    status = (
        next(iter(statuses))
        if len(statuses) == 1
        else "Mixed" if statuses else None
    )

    return {
        "charge": charge,
        "health": health,
        "energy": energy,
        "full_energy": full_energy,
        "cycles": cycles,
        "status": status,
        "batteries": [
            {
                "name": b["name"],
                "charge": b["charge"],
                "health": b["health"],
                "cycles": b["cycles"],
                "status": b["status"]
            }
            for b in batteries
        ]
    }


def read_hwmon_devices():
    devices = []

    try:
        hwmon_path = "/sys/class/hwmon"

        for device in os.listdir(hwmon_path):
            base = os.path.join(hwmon_path, device)
            name = read_file(os.path.join(base, "name"))

            if not name:
                continue

            sensors = {
                "temperatures": [],
                "fans": []
            }

            try:
                files = os.listdir(base)
            except OSError:
                continue

            for filename in files:
                path = os.path.join(base, filename)

                if filename.startswith("temp") and filename.endswith("_input"):
                    value = read_file(path)

                    if value is None:
                        continue

                    try:
                        value = int(value)
                    except ValueError:
                        continue

                    if value <= 0:
                        continue

                    prefix = filename[:-6]
                    label = read_file(
                        os.path.join(base, f"{prefix}_label")
                    )

                    sensors["temperatures"].append({
                        "label": label or "",
                        "value": value
                    })

                elif filename.startswith("fan") and filename.endswith("_input"):
                    value = read_file(path)

                    if value is None:
                        continue

                    try:
                        value = int(value)
                    except ValueError:
                        continue

                    if value < 0:
                        continue

                    prefix = filename[:-6]
                    label = read_file(
                        os.path.join(base, f"{prefix}_label")
                    )

                    sensors["fans"].append({
                        "index": prefix,
                        "label": label or "",
                        "rpm": value
                    })

            devices.append({
                "name": name.lower(),
                **sensors
            })

    except OSError:
        pass

    return devices


def read_thermals():
    devices = read_hwmon_devices()

    # Preferred CPU temperature sensors, ordered by confidence.
    # Driver names identify hardware monitoring interfaces;
    # label prefixes identify the desired sensor within each driver.
    cpu_priorities = [
        ("coretemp", "package id"),  # Intel CPU package
        ("k10temp", "tdie"),         # AMD die temperature
        ("k10temp", "tctl"),         # AMD control temperature
        ("zenpower", "tdie"),        # AMD alternative driver
        ("zenpower", "tctl"),
        ("thinkpad", "cpu")          # ThinkPad-specific fallback
    ]

    cpu = None

    for driver, label_prefix in cpu_priorities:
        for device in devices:
            # Fall back to recognizable CPU temperature labels
            # exposed by other hardware monitoring drivers.
            if cpu is None:
                preferred_labels = (
                    "package",
                    "cpu die",
                    "tdie",
                    "tctl"
                )

                for device in devices:
                    for sensor in device["temperatures"]:
                        label = sensor["label"].strip().lower()

                        if any(
                            label.startswith(prefix)
                            for prefix in preferred_labels
                        ):
                            cpu = sensor["value"]
                            break

                    if cpu is not None:
                        break

            # Last resort: a sensor explicitly labelled CPU.
            if cpu is None:
                for device in devices:
                    for sensor in device["temperatures"]:
                        if sensor["label"].strip().lower() == "cpu":
                            cpu = sensor["value"]
                            break

                    if cpu is not None:
                        break

                        if cpu is not None:
                            break

                    if cpu is not None:
                        break

    # Fall back to other recognized CPU sensor drivers.
    if cpu is None:
        for device in devices:
            if device["name"] in ("coretemp", "k10temp", "zenpower"):
                if device["temperatures"]:
                    cpu = device["temperatures"][0]["value"]
                    break

    # Find NVMe composite temperature.
    nvme = None

    for device in devices:
        if device["name"] != "nvme":
            continue

        for sensor in device["temperatures"]:
            if sensor["label"].lower() == "composite":
                nvme = sensor["value"]
                break

        if nvme is None and device["temperatures"]:
            nvme = device["temperatures"][0]["value"]

        if nvme is not None:
            break

    # Discover available fan sensors without assuming a driver.
    fans = [
        {
            "device": device["name"],
            "index": fan["index"],
            "label": fan["label"],
            "rpm": fan["rpm"]
        }
        for device in devices
        for fan in device["fans"]
    ]

    return {
        "cpu": round(cpu / 1000, 1) if cpu is not None else None,
        "nvme": round(nvme / 1000, 1) if nvme is not None else None,
        "fan": max(
            (fan["rpm"] for fan in fans),
            default=None
        ),
        "fans": fans
    }


def read_storage():
    try:
        stats = os.statvfs("/")
        total = stats.f_blocks * stats.f_frsize
        free = stats.f_bavail * stats.f_frsize
        used = total - free

        return {
            "total": round(total / 1024**3, 1),
            "used": round(used / 1024**3, 1),
            "free": round(free / 1024**3, 1),
            "usage": round(used / total * 100, 1) if total else 0
        }
    except OSError:
        return {}


def read_amd_gpu():
    """Read the first amdgpu device exposed through Linux sysfs."""
    try:
        cards = sorted(os.listdir("/sys/class/drm"))
    except OSError:
        return None

    for card in cards:
        if not card.startswith("card") or "-" in card:
            continue
        device = f"/sys/class/drm/{card}/device"
        vendor = read_file(os.path.join(device, "vendor"))
        if vendor and vendor.lower() != "0x1002":
            continue

        hwmon_root = os.path.join(device, "hwmon")
        try:
            hwmons = [os.path.join(hwmon_root, item) for item in os.listdir(hwmon_root)]
        except OSError:
            hwmons = []

        gpu = {"vendor": "AMD", "name": None, "temperature": None,
               "utilization": None, "memory_used": None, "memory_total": None,
               "fan_speed": None}
        for hwmon in hwmons:
            if (read_file(os.path.join(hwmon, "name")) or "").lower() != "amdgpu":
                continue
            gpu["name"] = read_file(os.path.join(hwmon, "device", "product_name"))
            for filename in os.listdir(hwmon):
                if filename.startswith("temp") and filename.endswith("_input"):
                    value = read_file(os.path.join(hwmon, filename))
                    label = read_file(os.path.join(hwmon, filename[:-6] + "_label")) or ""
                    try:
                        temp = round(int(value) / 1000, 1)
                    except (ValueError, TypeError):
                        continue
                    if gpu["temperature"] is None or "edge" in label.lower():
                        gpu["temperature"] = temp
                    if "junction" in label.lower():
                        gpu["hotspot"] = temp
                if filename.startswith("fan") and filename.endswith("_input") and gpu["fan_speed"] is None:
                    try:
                        gpu["fan_speed"] = int(read_file(os.path.join(hwmon, filename)))
                    except (ValueError, TypeError):
                        pass

        try:
            busy = read_file(os.path.join(device, "gpu_busy_percent"))
            gpu["utilization"] = int(busy) if busy is not None else None
        except ValueError:
            pass
        for key, filename in (("memory_used", "mem_info_vram_used"),
                              ("memory_total", "mem_info_vram_total")):
            try:
                value = read_file(os.path.join(device, filename))
                gpu[key] = round(int(value) / 1024**2) if value is not None else None
            except ValueError:
                pass
        if gpu["temperature"] is not None or gpu["utilization"] is not None or gpu["name"]:
            return gpu
    return None


def read_nvidia_gpu():
    """Read the first NVIDIA GPU using the optional nvidia-smi utility."""
    if not shutil.which("nvidia-smi"):
        return None
    query = "name,temperature.gpu,utilization.gpu,memory.used,memory.total,fan.speed"
    try:
        result = subprocess.run(
            ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2, check=True
        )
        fields = [field.strip() for field in result.stdout.splitlines()[0].split(",")]

        if len(fields) < 6 or not fields[0]:
            return None

        def number(value):
            try:
                result = float(value)
                return result if result >= 0 else None
            except (ValueError, TypeError):
                return None

        return {
            "vendor": "NVIDIA", "name": fields[0],
            "temperature": number(fields[1]), "utilization": number(fields[2]),
            "memory_used": number(fields[3]), "memory_total": number(fields[4]),
            "fan_speed": number(fields[5])
        }
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


def read_gpu(backend):
    if backend == "disabled":
        return None
    if backend == "amd":
        return read_amd_gpu()
    if backend == "nvidia":
        return read_nvidia_gpu()
    return read_nvidia_gpu() or read_amd_gpu()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu-backend", choices=("auto", "amd", "nvidia", "disabled"), default="auto")
    args = parser.parse_args()
    data = {
        "system": {
            "hostname": platform.node() or "Linux System"
        },
        "cpu": read_cpu(),
        "memory": read_memory(),
        "battery": read_battery(),
        "thermals": read_thermals(),
        "storage": read_storage(),
        "gpu": read_gpu(args.gpu_backend),
        "timestamp": time.time()
    }

    print(json.dumps(data), flush=True)


if __name__ == "__main__":
    main()
