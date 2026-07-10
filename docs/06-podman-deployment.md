# EP6 — Podman Deployment for Linux gateway Edge Device

EP6 เป็นอีกหนึ่งทางเลือกสำหรับการ deploy หลังจากทำ Dashboard ใน EP1-EP4 แล้ว โดยเปลี่ยนจากการรันบน `.venv` โดยตรง มาเป็นการรันใน container ด้วย **Podman**

EP5 และ EP6 ไม่ใช่ขั้นตอนที่ต้องเปิดใช้พร้อมกัน ถ้าเลือก EP6 ให้ใช้ Podman + Quadlet เป็นตัวรันระบบ และไม่ต้องเปิด service `.venv` จาก EP5 พร้อมกัน เพราะอาจชน port `8000`

---

## ทำไมเลือก Podman เป็นตัวหลัก

Podman เหมาะกับ Industrial Mini PC / Linux gateway / edge device เพราะ:

* ทำงานแบบ daemonless ไม่ต้องมี container daemon คุม container ตลอดเวลา
* ใช้คำสั่ง container ที่อ่านง่าย เช่น `build`, `run`, `logs`, `ps`
* รองรับ rootless container ได้ดี
* ทำงานร่วมกับ `systemd` ได้เป็นธรรมชาติ โดยเฉพาะผ่าน Quadlet
* เหมาะกับงาน Industrial IoT ที่ต้องการให้ service เริ่มเองหลัง boot และดู log ผ่าน systemd/journal ได้

สำหรับซีรีส์นี้ที่วาง Linux edge gateway ระยะยาว เราจะให้ Podman เป็น default เพื่อให้การ deploy และการผูกกับ systemd ชัดเจนตั้งแต่ต้น

---

## เป้าหมายของ EP6

รัน Modbus FastAPI Dashboard ใน container และเปิดเว็บได้ที่:

```text
http://192.168.1.125:8000
```

โดย container ต้องเข้าถึง USB-RS485 ได้ผ่าน device เช่น:

```text
/dev/ttyUSB0
```

---

## โครงสร้างโปรเจกต์ที่ใช้

ใน EP นี้อ้างอิงโครงสร้างมาตรฐาน และ repo นี้เตรียมไฟล์สำหรับ Podman ไว้ให้แล้ว:

> หมายเหตุ: path `/home/pi0001/...` เป็นตัวอย่างเท่านั้น ถ้าใช้ Raspberry Pi OS อาจเป็น `/home/pi/...` หรือถ้าใช้ Ubuntu อาจเป็น `/home/ubuntu/...` ให้เปลี่ยนคำสั่ง `cd` และ path ให้ตรงกับเครื่องจริงของคุณ

```text
/home/pi0001/industrial-linux-modbus-fastapi-dashboard/
├── requirements.txt
├── Containerfile
├── .containerignore
├── scripts/
│   └── modbus-dashboard.container.example
└── src/
    ├── app.py
    ├── modbus_reader.py
    ├── templates/
    └── static/
```

ใน EP นี้จะใช้ Containerfile เป็นไฟล์หลักสำหรับ build image ด้วย Podman

---

## 1. ติดตั้ง Podman

บน Linux ที่ใช้ Debian/Ubuntu base เช่น Ubuntu Server, Debian หรือ Linux gateway OS:

```bash
sudo apt update
sudo apt install podman -y
```

ตรวจสอบเวอร์ชัน:

```bash
podman --version
```

คำสั่งหลักใน EP นี้ใช้ `sudo podman` เพราะเราวาง Quadlet ไว้ที่ `/etc/containers/systemd/` ซึ่งเป็น rootful systemd path และเหมาะกับงาน hardware gateway ที่ต้องเข้าถึง `/dev/ttyUSB0` โดยตรง

---

## 2. เตรียม requirements.txt

ถ้ายังไม่มี `requirements.txt` ให้สร้างจาก `.venv` เดิมก่อน:

```bash
cd /home/pi0001/industrial-linux-modbus-fastapi-dashboard
source .venv/bin/activate
pip freeze > requirements.txt
```

หรือใช้รายการขั้นต่ำ:

```text
fastapi
uvicorn
pymodbus
pyserial
```

---

## 3. สร้าง Containerfile

ใน repo นี้มี `Containerfile` ให้แล้ว ถ้าต้องสร้างเอง:

```bash
nano Containerfile
```

ใส่เนื้อหานี้:

```text
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Build Image ด้วย Podman

```bash
cd /home/pi0001/industrial-linux-modbus-fastapi-dashboard
sudo podman build -t modbus-dashboard:latest -f Containerfile .
```

ตรวจสอบ image:

```bash
sudo podman images
```

---

## 5. Run Container ด้วย Podman

รันโดย map port และส่ง device `/dev/ttyUSB0` เข้า container:

```bash
sudo podman run -d \
  --name modbus-dashboard \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  -p 8000:8000 \
  modbus-dashboard:latest
```

เปิดจาก Browser:

```text
http://192.168.1.125:8000
```

---

## 6. ดูสถานะและ Log ของ Podman

ตรวจสอบ container:

```bash
sudo podman ps
```

ดู log:

```bash
sudo podman logs -f modbus-dashboard
```

restart:

```bash
sudo podman restart modbus-dashboard
```

stop:

```bash
sudo podman stop modbus-dashboard
```

ลบ container เดิมก่อน run ใหม่:

```bash
sudo podman rm modbus-dashboard
```

---

## 7. ทำให้ Container เริ่มเองตอน Boot ด้วย Quadlet

Podman รองรับการทำ systemd unit ด้วย Quadlet โดยใช้ไฟล์ `.container` แล้วให้ systemd generator สร้าง service ให้เอง

สร้างไฟล์ Quadlet:

```bash
sudo nano /etc/containers/systemd/modbus-dashboard.container
```

ใน repo นี้มีไฟล์ตัวอย่างอยู่ที่ `scripts/modbus-dashboard.container.example` ถ้าต้องการ copy ไปใช้:

```bash
sudo mkdir -p /etc/containers/systemd
sudo cp scripts/modbus-dashboard.container.example /etc/containers/systemd/modbus-dashboard.container
```

ถ้าเคยทดลองรัน container ด้วย `sudo podman run --name modbus-dashboard` มาก่อน ให้หยุดและลบ container เดิมก่อนเริ่ม Quadlet เพื่อไม่ให้ชื่อชนกัน:

```bash
sudo podman stop modbus-dashboard
sudo podman rm modbus-dashboard
```

เนื้อหาไฟล์:

```ini
[Unit]
Description=Modbus FastAPI Dashboard Container
After=network-online.target
Wants=network-online.target

[Container]
ContainerName=modbus-dashboard
Image=localhost/modbus-dashboard:latest
PublishPort=8000:8000
AddDevice=/dev/ttyUSB0:/dev/ttyUSB0

[Service]
Restart=always
RestartSec=5
TimeoutStartSec=900

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Start service:

```bash
sudo systemctl start modbus-dashboard.service
```

สำหรับ Quadlet ไม่ต้องใช้ `systemctl enable` กับ generated service แบบ unit ปกติ ให้กำหนด `[Install]` ในไฟล์ `.container` แล้วให้ Podman systemd generator จัดการตอน `daemon-reload` และตอน boot

ตรวจสอบ:

```bash
sudo systemctl status modbus-dashboard.service
```

ดู log:

```bash
journalctl -u modbus-dashboard.service -f
```

---

## 8. อัปเดตโค้ดแล้ว Deploy ใหม่

หลังแก้โค้ด ให้ build image ใหม่ แล้ว restart service:

```bash
sudo podman build -t modbus-dashboard:latest -f Containerfile .
sudo systemctl restart modbus-dashboard.service
```

ถ้ารันด้วย `podman run` แบบ manual:

```bash
sudo podman stop modbus-dashboard
sudo podman rm modbus-dashboard
sudo podman build -t modbus-dashboard:latest -f Containerfile .
sudo podman run -d \
  --name modbus-dashboard \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  -p 8000:8000 \
  modbus-dashboard:latest
```

---

## 9. ข้อควรระวังเรื่อง Serial Port

Container ต้องเห็น device เดียวกับ host เช่น:

```bash
ls -l /dev/ttyUSB0
```

ถ้าเสียบ USB-RS485 ใหม่แล้ว path เปลี่ยน อาจต้องแก้ `--device` หรือ `AddDevice`

ตัวอย่างปัญหา:

```text
/dev/ttyUSB0 เปลี่ยนเป็น /dev/ttyUSB1
```

ให้ตรวจสอบด้วย:

```bash
ls -l /dev/ttyUSB*
```

---

## 10. ข้อควรระวังเรื่องสิทธิ์

ถ้า container อ่าน serial ไม่ได้ ให้ลองตรวจสอบ permission บน host:

```bash
ls -l /dev/ttyUSB0
```

สำหรับ Podman rootful การใช้ `--device /dev/ttyUSB0:/dev/ttyUSB0` หรือ `AddDevice=/dev/ttyUSB0:/dev/ttyUSB0` มักเพียงพอแล้ว

ถ้าใช้ rootless Podman แล้วติด permission อาจต้องปรับสิทธิ์ device, udev rule หรือเลือกใช้ rootful Quadlet สำหรับงาน hardware gateway

---

## Uninstall / Cleanup

ถ้าใช้ Podman + Quadlet ให้หยุด service ก่อน:

```bash
sudo systemctl stop modbus-dashboard.service
```

ลบไฟล์ Quadlet แล้ว reload systemd:

```bash
sudo rm /etc/containers/systemd/modbus-dashboard.container
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

ลบ container และ image ที่สร้างไว้:

```bash
sudo podman rm -f modbus-dashboard
sudo podman rmi localhost/modbus-dashboard:latest
```

ถ้าเคยรันด้วย `podman run` แบบ manual และไม่ได้ใช้ Quadlet ให้ใช้ชุดนี้แทน:

```bash
sudo podman stop modbus-dashboard
sudo podman rm modbus-dashboard
sudo podman rmi modbus-dashboard:latest
```

ตรวจสอบว่าลบออกแล้ว:

```bash
sudo podman ps -a
sudo podman images
sudo systemctl status modbus-dashboard.service
```

ถ้าต้องการลบโฟลเดอร์โปรเจกต์ด้วย ให้ตรวจสอบ path ก่อนเสมอ:

```bash
pwd
ls -l /home/pi0001
```

เมื่อตรวจสอบแน่ใจแล้วว่า path ถูกต้อง จึงค่อยลบ:

```bash
cd /home/pi0001
rm -rf industrial-linux-modbus-fastapi-dashboard
```

> หมายเหตุ: ถ้าใช้ Raspberry Pi OS หรือ Ubuntu path อาจเป็น `/home/pi/...` หรือ `/home/ubuntu/...` ให้เปลี่ยน path ให้ตรงกับเครื่องจริงก่อนรันคำสั่งลบ

---
## EP5 หรือ EP6 ควรเลือกอะไร

ไม่จำเป็นต้องใช้ทั้งสองแบบพร้อมกัน ให้เลือกวิธีใดวิธีหนึ่งตามเป้าหมายของงาน

ใช้ `systemd + .venv` จาก EP5 ถ้า:

* ต้องการความเรียบง่าย
* debug บนเครื่อง Linux gateway บ่อย
* ยังไม่ต้องการจัดการ image/container

ใช้ `Podman + Quadlet` จาก EP6 ถ้า:

* ต้องการแยก environment ชัดเจน
* ต้องการ deploy ซ้ำได้เป็นระบบ
* ต้องการให้ container เป็น service ของ systemd
* ต้องการแนวทางที่เหมาะกับ Linux edge gateway ระยะยาว


---

## สรุป EP6

ใน EP นี้เราเลือกแนว container deployment โดยให้ Podman เป็นตัวหลัก ใช้ `Containerfile` สำหรับ build image และใช้ Quadlet เพื่อให้ container เริ่มเองตอน boot ผ่าน systemd

ถ้าเลือกใช้ EP6 แล้ว ให้หยุดหรือปิด service แบบ `.venv` จาก EP5 ก่อน เพื่อให้เหลือวิธี deploy เพียงทางเดียวในเครื่องจริง

คำสั่งที่ใช้บ่อย:

```bash
sudo podman build -t modbus-dashboard:latest -f Containerfile .
sudo podman logs -f modbus-dashboard
sudo systemctl restart modbus-dashboard.service
journalctl -u modbus-dashboard.service -f
```

