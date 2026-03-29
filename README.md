# Advantage Air MyAir3 — Home Assistant Integration

A custom Home Assistant integration for the **Advantage Air MyAir3** ducted air conditioning system. Uses the device's local HTTP API — no cloud dependency.

## Features

- **System switch** — turn the air con on or off
- **Zone switches** — turn individual zones on or off, labelled with the zone name from the device
- **Auto-discovery** — finds the device on your network via UDP broadcast
- **Manual IP fallback** — if discovery fails, enter the IP (or hostname) through the Home Assistant UI
- **Local polling** — polls the device every 30 seconds

## Installation

### HACS (recommended)

1. In Home Assistant, go to **HACS → Integrations → Custom repositories**
2. Add `https://github.com/rekirky/advantage_air_myair3` as an **Integration**
3. Install **Advantage Air MyAir3** from the list
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/advantage_air_myair3` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Advantage Air MyAir3**
3. The integration will attempt to auto-discover your device via UDP broadcast
   - If found, it will configure automatically
   - If not found, you will be prompted to enter the device IP address or hostname (e.g. `home19.local`)

## Requirements

- Home Assistant 2024.1.0 or newer
- Advantage Air MyAir3 system on the same local network
- Default device password (`password`) — this is the factory default

## Entities

| Entity | Type | Description |
|--------|------|-------------|
| Air Con Power | Switch | Main system on/off |
| `<Zone Name>` (×8) | Switch | Per-zone on/off, named from the device |

## Roadmap

- [ ] Zone damper percentage control (slider)
- [ ] Temperature sensors (per zone and central)
- [ ] Central temperature set point
- [ ] Fan speed control
- [ ] AC mode selection (cool / heat / fan only / dry)
- [ ] Timer / schedule support

## Notes

- The device is queried at `http://<ip>:80/`
- A login call is made before each poll and before each control command
- Zone names are read from the device — they update automatically if you rename zones in the MyAir app
