# PLAF108 — ESPHome firmware for Petlibro AF108

ESPHome configuration for the **[PETLIBRO Automatic Cat Feeder AIR 2.4G Wi-Fi](https://www.amazon.com/dp/B0CHR8N99Z)** (ESP32-C3). Replaces the stock firmware with local control via Home Assistant, without any cloud dependency.

## Features

- Up to **8 scheduled meal times**, each with individual portion size (1–10)
- Manual **Dispense Meal** button with configurable portion size
- **Skip Next Meal** toggle
- **Out of food** detection via optical sensor
- **Motor stall** detection with automatic retry (reverses direction once before giving up)
- **Dispensing watchdog** — triggers a timeout alarm if dispensing takes too long
- **Alarm LED** driven by any active alarm (out of food / stall / timeout)
- Meal statistics: Meals Today (resets at midnight) and Meals Total
- Full Home Assistant integration (API, time sync, mDNS)
- OTA updates + embedded web server (port 80)

## Hardware

| Component | GPIO |
|---|---|
| Status LED | GPIO3 |
| Alarm LED | GPIO10 |
| Motor Left | GPIO6 |
| Motor Right | GPIO7 |
| Motor Sensor | GPIO8 |
| Food Sensor | GPIO18 |
| Enable Food Sensor | GPIO9 |
| Reset Button | GPIO19 |
| Battery | GPIO0 |
| Battery Plugged In | GPIO4 |
| Mains Connected | GPIO5 |
| UART TX/RX | GPIO21/GPIO20 |

## Reset button

| Press | Action |
|---|---|
| Short press | Restart |
| Double short press | Safe mode |
| Hold 10 s | Factory reset |

## File structure

```
plaf108/
├── .common.plaf108.yaml   # Main config: sensors, motor logic, meal scheduling
├── .base.yaml             # Shared diagnostics (uptime, wifi signal, OTA, buttons)
├── .home.yaml             # Home Assistant specifics (time sync, mDNS, web server)
├── minimal.yaml           # Minimal config for connectivity testing
├── includes/
│   └── std_includes.h     # C++ includes for std::chrono
├── read_boot.py           # Serial monitor for boot logs and flash mode
├── requirements.txt       # Python dependencies (esptool, pyserial)
└── secrets.yaml           # Not committed — see below
```

---

## Getting started

Two paths to get the firmware on your device.

### Option A — Use a pre-built release

Download the latest `plaf108-vX.Y.Z.factory.bin` from the [Releases](../../releases/latest) page, then follow [First flash (USB)](#first-flash-usb) below.

> The pre-built binary starts with no Wi-Fi credentials. On first boot the device creates a fallback AP named `plaf108-XXXXXX` (password: `plaf108setup`, OTA password: `plaf108ota`). Connect to it and use the web UI at `http://192.168.4.1` to verify the device works, then push your own build via OTA to set your Wi-Fi credentials (see [OTA updates](#ota-updates-after-first-flash)).

---

### Option B — Build from source

All commands below are run from the `plaf108/` directory.

#### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- Python 3 with a virtual environment set up (installs `esptool` and `pyserial`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Always activate the venv (`source .venv/bin/activate`) before running `python` or `esptool` commands.

#### secrets.yaml

Create `plaf108/secrets.yaml` (not committed):

```yaml
wifi_ssid: "YourSSID"
wifi_password: "YourPassword"
fallback_wifi_password: "FallbackPassword"
ota_password: "OTAPassword"
```

#### Timezone

Edit `.home.yaml` and set your timezone:

```yaml
time:
  - platform: homeassistant
    timezone: Europe/Paris  # <- change this
```

Full list: [List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

#### Compile

```bash
docker run --rm -v "${PWD}":/config ghcr.io/esphome/esphome compile .common.plaf108.yaml
```

The factory binary is output at:
```
.esphome/build/plaf108/.pioenvs/plaf108/firmware.factory.bin
```

---

## First flash (USB)

The AF108 does not expose UART pins directly — you need to open the device and connect a USB-to-serial adapter (3.3 V) to the UART pads.

> **Assembly note:** make sure the motor mechanism cannot physically press the Reset Button (GPIO19) during dispensing. An accidental press triggers a restart mid-cycle.

**Step 1 — Enter flash mode**

Find your serial port:

```bash
# macOS
ls /dev/cu.usbserial-*
# Linux
ls /dev/ttyUSB*
```

Open a terminal and start `read_boot.py` to monitor the serial output (replace the port with yours):

```bash
python read_boot.py /dev/cu.usbserial-XXX
```

Then power-cycle the device while holding **GPIO9** (BOOT pin) low. You should see:

```
ESP-ROM:esp32c3-api1-20210207
Build:Feb  7 2021
rst:0x1 (POWERON),boot:0x5 (DOWNLOAD(USB/UART0/1))
waiting for download
```

The device is ready to be flashed. Stop `read_boot.py` (`Ctrl+C`) to free the serial port.

**Step 2 — Flash**

Replace the path with the pre-built binary you downloaded (Option A) or the compiled output (Option B):

```bash
esptool --port /dev/cu.usbserial-XXX write-flash 0x0 <firmware.factory.bin>
```

---

## OTA updates (after first flash)

Once the device is on the network, run from the `plaf108/` directory:

```bash
docker run --rm -v "${PWD}":/config ghcr.io/esphome/esphome run .common.plaf108.yaml --device plaf108.local
```

---

## Debugging boot logs

`read_boot.py` is also useful after a normal boot to check that the device starts correctly. Run it, then power-cycle without holding BOOT:

```bash
python read_boot.py /dev/cu.usbserial-XXX
```

---

## Testing connectivity only

`minimal.yaml` is a stripped-down config (no sensors, no motor logic) useful to verify Wi-Fi and OTA work before flashing the full firmware. Run from the `plaf108/` directory:

```bash
docker run --rm -v "${PWD}":/config ghcr.io/esphome/esphome run minimal.yaml
```
