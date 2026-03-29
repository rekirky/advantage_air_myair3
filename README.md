# Advantage Air MyAir3 — Home Assistant Integration

A custom Home Assistant integration for the **Advantage Air MyAir3** ducted air conditioning system.

✅ Fully local control — no cloud dependency  
✅ Simple setup using your device IP or hostname  

---

## 🚀 Version 3.0.0 (MVP Release)

This is the first **working MVP release** of the integration.

You can now:
- Add your MyAir system to Home Assistant
- Turn the **air conditioning system on/off**
- Control **each individual zone**

---

## ✨ Features

- **System switch** — turn the air con on or off  
- **Zone switches** — turn individual zones on/off  
- **Zone naming** — automatically pulled from your device  
- **Manual setup (IP or hostname)** — reliable connection method  
- **Local polling** — updates every 30 seconds  
- **No cloud required** — fully local HTTP API  

---

## ⚠️ Important Change (v3.0.0)

Auto-discovery via UDP has been **removed**.

👉 You must now provide the device IP or hostname during setup  
(e.g. `192.168.1.111` or `home19.local`)

This change improves reliability across different MyAir hardware versions.

---

## 📦 Installation

### HACS (recommended)

1. Go to **HACS → Integrations → Custom repositories**
2. Add: https://github.com/rekirky/advantage_air_myair3 as an **Integration**
3. Install **Advantage Air MyAir3**
4. Restart Home Assistant

---

### Manual

1. Copy:

custom_components/advantage_air_myair3

into:

config/custom_components/

2. Restart Home Assistant

---

## ⚙️ Setup

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Advantage Air MyAir3**
4. Enter your device:
- IP address → `192.168.1.111`


The integration will:
- Validate the connection via the device API
- Store the IP for ongoing use

---

## 📋 Requirements

- Home Assistant **2024.1.0+**
- MyAir3 system on the **same local network**
- Default password:

password


---

## 🔌 Entities

| Entity | Type | Description |
|------|------|-------------|
| Air Con Power | Switch | Main system on/off |
| `<Zone Name>` | Switch | Per-zone on/off |

- Zone names are pulled directly from the device  
- Updates automatically if renamed in the MyAir app  

---

## 🔧 How It Works

- Uses the device's local HTTP API:

http://<ip>/login?password=password

- Authentication is performed before:
- Each poll
- Each control command
- System data and zone data are retrieved via:
- `getSystemData`
- `getZoneData`

---

## 🛣️ Roadmap

- [x] Zone strength control (slider)
- [ ] Scheduling / timers
- [ ] Better error handling / reconnect logic

> **Note:** Temperature, fan speed, and mode look to be controlled directly on the AirCon unit — these cannot be set via the MyAir3 API. This may be limited to my setup and could change depending on your own implementation.

---

## 🧠 Notes

- Runs entirely locally — no internet required  
- Works best with static IP or DHCP reservation  
- Some MyAir firmware versions behave slightly differently — feedback welcome  

---

## 🤝 Contributing

PRs, testing feedback, and device variations are very welcome 👍

---

## 📄 License

MIT License
