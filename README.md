# Industrial Linux Modbus FastAPI Dashboard

อ่านค่า Sensor Modbus RTU ผ่าน USB-RS485 ด้วยเครื่อง Linux เช่น Industrial Mini PC, Linux SBC หรือ Raspberry Pi แล้วแสดงผลผ่าน FastAPI และหน้าเว็บ HTML แบบง่าย


## Why This Architecture

โปรเจกต์นี้ไม่ได้ทำขึ้นเพื่อบอกว่า Python เร็วกว่า Node-RED หรือ JavaScript แต่ตั้งใจแสดงแนวทางสร้าง Industrial IoT Framework ที่อ่านค่า Modbus RTU แล้วต่อยอดเป็น API, Dashboard, Service และ Deployment ได้เป็นระบบ

จาก datasheet ของเซ็นเซอร์กลุ่มนี้ อุปกรณ์วัดค่า PM1.0, PM2.5 และ PM10 ผ่าน RS485 ได้ และตัว sensor เองมีช่วง warm-up รวมถึง response time ของการวัด ดังนั้นในระบบจริงคอขวดหลักมักอยู่ที่ sensor, serial bus และรอบการอ่าน Modbus มากกว่าความเร็วของภาษา Python

สำหรับงาน Linux Edge Gateway + USB-RS485 + Modbus RTU ที่อ่านค่าทุก 1 วินาที ความต่างระหว่าง Python กับ JavaScript มักไม่ใช่ปัจจัยหลัก เพราะเวลาส่วนใหญ่คือการรออุปกรณ์ตอบกลับผ่าน serial ส่วน Python ใช้เวลาเพียงเล็กน้อยในการจัดรูปข้อมูลเป็น dictionary และส่ง JSON ผ่าน FastAPI

## Python + FastAPI vs Node-RED

| หัวข้อ | Python + FastAPI | Node-RED |
| --- | --- | --- |
| ความเร็วในการทำต้นแบบ | ช้ากว่า ต้องเขียนโค้ดเอง | เร็วมาก ลาก node แล้วต่อ flow ได้ทันที |
| ความเร็ว runtime | เพียงพอสำหรับ Modbus RTU และ dashboard ระดับ 1 วินาที | ดีมาก โดยเฉพาะ event-driven flow และ integration |
| การดูแลระยะยาว | โครงสร้างชัด แยก module ได้ ทดสอบง่าย | flow ใหญ่ ๆ อาจอ่านยากและ merge ยาก |
| Git / Version Control | เป็นมิตรกับ Git, review และ PR | JSON flow review ได้ แต่ไม่สวยเท่า source code |
| Unit Test | ทำได้ตรงไปตรงมา | ทำได้ แต่ไม่ใช่จุดแข็งหลัก |
| Reuse | ทำเป็น library/framework ได้ง่าย | reuse ได้ผ่าน subflow/node แต่เหมาะกับ integration มากกว่า |
| Dashboard / Integration | ต้องเขียนเพิ่มเอง | มี node พร้อมใช้จำนวนมาก เช่น MQTT, dashboard, database |
| เหมาะกับ | สร้าง software framework, API, library, service | ทำ integration, prototype, automation, wiring ระบบเร็ว ๆ |

สรุปคือ Node-RED เหมาะมากถ้าต้องการต่อระบบให้เห็นผลเร็ว เช่น Modbus ไป MQTT, dashboard, database หรือ automation ภายในโรงงาน แต่โปรเจกต์นี้เลือก Python + FastAPI เพราะต้องการสร้างฐานที่ต่อยอดเป็น framework ได้ เช่นแยก reader ของ sensor หลายประเภท แล้วเปิด API แบบเดียวกันให้ Node-RED, Grafana, SCADA, MES หรือระบบอื่นเรียกใช้ต่อ

ตัวอย่างทิศทางระยะยาว:

```text
src/
└── modbus/
    ├── dust.py
    ├── weather.py
    ├── soil.py
    ├── inverter.py
    ├── power_meter.py
    └── plc.py
```

แล้วเปิด API เป็นรูปแบบเดียวกัน:

```text
GET /api/dust
GET /api/weather
GET /api/power-meter
GET /api/inverter
GET /api/plc
```

มุมมองของซีรีส์นี้จึงไม่ใช่แค่ทำ dashboard ให้ดูค่า sensor ได้ แต่เป็นการวางรากฐานสำหรับ Python Industrial IoT Framework ที่สามารถนำไปใช้ซ้ำกับอุปกรณ์ Modbus RTU หลายชนิดได้ในอนาคต

## Adapting to Other Modbus Sensors

ตัวอย่างใน repo นี้ใช้เซ็นเซอร์ที่อ่านค่าได้ 3 พารามิเตอร์ คือ PM1.0, PM2.5 และ PM10 จึงตั้งค่า `REGISTER_COUNT = 3` และ map ค่าเป็น `pm1_0`, `pm2_5`, `pm10`

ถ้าอุปกรณ์ของคุณมีเพียง 1 พารามิเตอร์ หรือมีมากกว่า 3 พารามิเตอร์ ให้ดูจาก Datasheet หรือ Modbus Register Map ของอุปกรณ์นั้นก่อน โดยต้องตรวจสอบอย่างน้อย 4 จุดนี้:

| สิ่งที่ต้องดู | นำไปปรับที่ไหน |
| --- | --- |
| Modbus Address / Slave ID | `SLAVE_ID` ใน `src/modbus_reader.py` |
| Function Code เช่น FC03 หรือ FC04 | ใช้ `read_holding_registers()` หรือ `read_input_registers()` |
| Start Register | `START_REGISTER` ใน `src/modbus_reader.py` |
| จำนวน Register ที่ต้องอ่าน | `REGISTER_COUNT` และการ map `registers[index]` |

เช่น ถ้าอุปกรณ์มีค่าเดียว อาจใช้ `REGISTER_COUNT = 1` และส่ง JSON แค่ field เดียว เช่น `value` หรือ `temperature` จากนั้นค่อยปรับ API response และหน้า Dashboard ให้แสดง field นั้นแทนตัวอย่าง PM1.0/PM2.5/PM10
ตัวอย่างเช่น ถ้าต้องเพิ่ม Solar Radiation Sensor ให้เริ่มจากดู Datasheet ว่าค่ารังสีแสงอาทิตย์อยู่ที่ Register ใด ใช้หน่วยอะไร เช่น W/m2 ต้องอ่านกี่ Register และมี scale factor หรือไม่ จากนั้นปรับ `modbus_reader.py` ให้ map ค่าออกมาเป็น field ใหม่ เช่น `solar_radiation`

```py
REGISTER_COUNT = 1

return {
    "status": "ok",
    "solar_radiation": registers[0],
    "timestamp": int(time.time())
}
```

ถ้า Datasheet ระบุว่าค่าที่อ่านได้ต้องหาร 10 ให้แปลงก่อนส่งออก:

```py
solar_radiation = registers[0] / 10
```

หลังจากนั้นจึงปรับหน้า Dashboard ให้แสดง `data.solar_radiation` แทน field ของเซ็นเซอร์ตัวอย่างเดิม
## How to Use This Series

ซีรีส์นี้เป็น project-based series ที่เน้นทำระบบให้รันได้จริงก่อน โดยในบางช่วงจะใช้วิธีคัดลอกโค้ดตัวอย่างไปวาง เพื่อให้เห็น workflow ของระบบตั้งแต่ Modbus Reader, FastAPI API, HTML Dashboard, systemd และ Podman ได้ต่อเนื่องตั้งแต่ต้นจนจบ

ดังนั้นในซีรีส์นี้จะไม่ได้อธิบายโค้ดทุกบรรทัดแบบคอร์ส syntax แต่จะอธิบายภาพรวมว่าแต่ละไฟล์ทำหน้าที่อะไร ข้อมูลไหลจาก sensor ไปถึง browser อย่างไร และต้องตรวจสอบจุดไหนเมื่อระบบไม่ทำงาน

หลังจากซีรีส์นี้ ผมจะทยอยแยกทำซีรีส์พื้นฐานเพิ่มเติม มานำเสนอภายหลัง เช่น HTML, CSS, JavaScript, Python, FastAPI, systemd และ Podman เพื่ออธิบายรายละเอียดของแต่ละเทคโนโลยีให้ลึกขึ้นทีละส่วน

## Series Content

1. Setup Linux Edge Gateway + USB-RS485 + Scan Modbus Address
2. Create modbus_reader.py for reading sensor data
3. Create FastAPI app.py for API and web server
4. Create index.html dashboard for browser display
5. Basic deployment: Run FastAPI automatically with systemd + .venv
6. Container deployment: Deploy with Podman + Quadlet

## Deployment Options

หลังจากทำ EP1-EP4 แล้ว คุณไม่จำเป็นต้องทำ EP5 และ EP6 พร้อมกัน ให้เลือกวิธี deploy ตามรูปแบบงานจริง:

| วิธี | เหมาะกับ | ใช้อะไรเป็นหลัก |
| --- | --- | --- |
| EP5: Basic deployment | เริ่มต้นง่าย, debug ง่าย, แก้โค้ดบนเครื่องบ่อย | `systemd` + `.venv` + `uvicorn` |
| EP6: Container deployment | ต้องการแยก environment, build image, deploy ซ้ำได้เป็นระบบ | `Podman` + `Containerfile` + `Quadlet` |

ถ้าเลือก EP5 ให้รัน service จาก `.venv` โดยตรง และยังไม่ต้องใช้ Podman

ถ้าเลือก EP6 ให้รันระบบผ่าน container และใช้ Quadlet ให้ `systemd` เปิด container ตอน boot แทน service `.venv` ของ EP5

## Hardware

- Industrial Mini PC, Linux SBC, Raspberry Pi, Orange Pi, or any Linux machine with USB support
- Linux OS such as Ubuntu Server, Debian, Raspberry Pi OS, or another Debian/Ubuntu-based distribution
- USB-RS485 Adapter
- Modbus RTU Sensor
- 12-24VDC Power Supply for sensor

## Quick Start

```bash
sudo apt update
sudo apt install python3-venv mbpoll -y
python3 -m venv .venv
source .venv/bin/activate
pip install pyserial pymodbus fastapi uvicorn
```

## Documentation

- [EP1: Setup and Scan Modbus](docs/01-setup-and-scan-modbus.md)
- [EP2: Modbus Reader Python](docs/02-modbus-reader.md)
- [EP3: FastAPI Web API](docs/03-fastapi-web-api.md)
- [EP4: HTML Dashboard](docs/04-html-dashboard.md)
- [EP5: Run with systemd](docs/05-run-with-systemd.md)
- [EP6: Podman Deployment](docs/06-podman-deployment.md)

## Deployment Files

- `requirements.txt` — Python packages for `.venv` or container build
- `Containerfile` — Podman-first container image for FastAPI Dashboard
- `scripts/modbus-dashboard.service.example` — systemd service example for `.venv`
- `scripts/modbus-dashboard.container.example` — Podman Quadlet example
