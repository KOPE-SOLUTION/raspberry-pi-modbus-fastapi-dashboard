# Raspberry Pi Modbus FastAPI Dashboard

อ่านค่า Sensor Modbus RTU ผ่าน USB-RS485 ด้วย Raspberry Pi แล้วแสดงผลผ่าน FastAPI และหน้าเว็บ HTML แบบง่าย

## Series Content

1. Setup Raspberry Pi + USB-RS485 + Scan Modbus Address
2. Create modbus_reader.py for reading sensor data
3. Create FastAPI app.py for API and web server
4. Create index.html dashboard for browser display

## Hardware

- Raspberry Pi
- USB-RS485 Adapter
- Modbus RTU Sensor
- 12–24VDC Power Supply for sensor

## Quick Start

```bash
sudo apt update
sudo apt install python3-pip python3-serial mbpoll -y
```

## Documentation

- [EP1: Setup and Scan Modbus](docs/01-setup-and-scan-modbus.md)
- [EP2: Modbus Reader Python](docs/02-modbus-reader.md)
- [EP3: FastAPI Web API](docs/03-fastapi-web-api.md)
- [EP4: HTML Dashboard](docs/04-html-dashboard.md)

---

