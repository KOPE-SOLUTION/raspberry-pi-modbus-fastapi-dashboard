# EP5 — Run FastAPI Automatically with systemd

หลังจาก EP4 เรามี FastAPI + HTML Dashboard ที่รันได้ด้วยคำสั่ง `uvicorn` แล้ว แต่ถ้าปิดเครื่อง เปิดเครื่องใหม่ หรือ เครื่อง reboot เราไม่ควรต้อง SSH เข้าไปรัน server เองทุกครั้ง

ใน EP นี้เราจะทำให้ Dashboard เริ่มทำงานอัตโนมัติด้วย `systemd` โดยรันจาก `.venv` โดยตรง วิธีนี้เป็น **วิธีพื้นฐาน** ที่เหมาะกับการเริ่มต้น เรียนรู้ service บน Linux และ debug บนเครื่องจริง

ถ้าต้องการใช้ container deployment ด้วย Podman ให้ข้ามไปใช้ EP6 เป็นอีกทางเลือกหนึ่งได้เลย ไม่จำเป็นต้องเปิด service ของ EP5 และ EP6 พร้อมกัน

---

## เป้าหมายของ EP5

เมื่อ Linux gateway เปิดเครื่องใหม่ ให้ระบบรัน FastAPI Dashboard ให้อัตโนมัติ และเปิดจาก Browser ได้ทันที เช่น

```text
http://192.168.1.125:8000
```

---

## โครงสร้างโปรเจกต์ที่แนะนำ

แนะนำให้จัดโปรเจกต์ไว้แบบนี้:

```text
/home/pi0001/industrial-linux-modbus-fastapi-dashboard/
├── .venv/
├── requirements.txt
├── README.md
├── docs/
├── scripts/
└── src/
    ├── app.py
    ├── modbus_reader.py
    ├── templates/
    └── static/
```

ถ้ายังใช้โครงสร้างเดิมแบบนี้:

```text
/home/pi0001/src/
├── app.py
├── modbus_reader.py
├── templates/
├── static/
├── requirements.txt
└── .venv/
```

ก็ยังใช้ได้ เพียงปรับ `WorkingDirectory`, `Environment` และ `ExecStart` ใน service ให้ตรงกับ path จริง

> หมายเหตุ: ตัวอย่างนี้ใช้ user `pi0001` และ path `/home/pi0001/...` ให้เปลี่ยนเป็น user และตำแหน่งโปรเจกต์จริงของเครื่องคุณ เช่น `pi`, `ubuntu` หรือ user อื่น ตรวจสอบชื่อ user ได้ด้วยคำสั่ง `whoami`
---

## 1. ตรวจสอบตำแหน่งโปรเจกต์

เข้าไปที่โปรเจกต์:

```bash
cd /home/pi0001/industrial-linux-modbus-fastapi-dashboard
```

ตรวจสอบไฟล์หลัก:

```bash
ls -l
ls -l src
```

ควรเห็นไฟล์ประมาณนี้:

```text
.venv/
requirements.txt
src/app.py
src/modbus_reader.py
src/templates/index.html
src/static/style.css
```

---

## 2. ทดสอบรันด้วยตัวเองก่อน

ก่อนทำ service ให้แน่ใจว่า Dashboard รันได้ด้วยมือก่อน:

```bash
cd /home/pi0001/industrial-linux-modbus-fastapi-dashboard/src
source ../.venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```

จากเครื่อง PC เปิด:

```text
http://192.168.1.125:8000
```

ถ้าเปิด Dashboard ได้แล้ว ให้กด `Ctrl + C` เพื่อหยุด server แล้วไปต่อ

---

## 3. สร้าง systemd Service

สร้างไฟล์ service:

```bash
sudo nano /etc/systemd/system/modbus-dashboard.service
```

ใน repo นี้มีไฟล์ตัวอย่างอยู่ที่ `scripts/modbus-dashboard.service.example` ถ้าตำแหน่งโปรเจกต์ตรงกับตัวอย่าง สามารถ copy ไปใช้ได้เลย:

```bash
sudo cp scripts/modbus-dashboard.service.example /etc/systemd/system/modbus-dashboard.service
```

ใส่เนื้อหานี้:

```ini
[Unit]
Description=Modbus FastAPI Dashboard
After=network-online.target
Wants=network-online.target

[Service]
User=pi0001
Group=dialout
WorkingDirectory=/home/pi0001/industrial-linux-modbus-fastapi-dashboard/src
Environment="PATH=/home/pi0001/industrial-linux-modbus-fastapi-dashboard/.venv/bin"
ExecStart=/home/pi0001/industrial-linux-modbus-fastapi-dashboard/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

บันทึกไฟล์:

```text
Ctrl + O
Enter
Ctrl + X
```

---

## หมายเหตุสำหรับโครงสร้างเดิม `/home/pi0001/src`

ถ้าโปรเจกต์ของคุณยังอยู่ที่ `/home/pi0001/src` ให้ใช้ service แบบนี้แทน:

```ini
[Unit]
Description=Modbus FastAPI Dashboard
After=network-online.target
Wants=network-online.target

[Service]
User=pi0001
Group=dialout
WorkingDirectory=/home/pi0001/src
Environment="PATH=/home/pi0001/src/.venv/bin"
ExecStart=/home/pi0001/src/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 4. Reload systemd

หลังสร้างหรือแก้ service ต้อง reload ก่อน:

```bash
sudo systemctl daemon-reload
```

---

## 5. Enable ให้รันตอน Boot

```bash
sudo systemctl enable modbus-dashboard.service
```

คำสั่งนี้ทำให้ service เริ่มเองทุกครั้งหลังเปิดเครื่อง

---

## 6. Start Service

```bash
sudo systemctl start modbus-dashboard.service
```

---

## 7. ตรวจสอบสถานะ

```bash
sudo systemctl status modbus-dashboard.service
```

ถ้าทำงานปกติ ควรเห็นประมาณนี้:

```text
Active: active (running)
```

กด `q` เพื่อออกจากหน้าสถานะ

---

## 8. ดู Log แบบสด

ถ้า Dashboard เปิดไม่ได้ หรืออ่าน Sensor ไม่ได้ ให้ดู log:

```bash
journalctl -u modbus-dashboard.service -f
```

ถ้าต้องการดู log ล่าสุดแบบไม่ตามต่อ:

```bash
journalctl -u modbus-dashboard.service -n 100
```

---

## 9. Restart หลังแก้โค้ด

เวลาแก้ `app.py`, `modbus_reader.py`, HTML หรือ CSS แล้วต้องการให้ service โหลดใหม่:

```bash
sudo systemctl restart modbus-dashboard.service
```

---

## 10. Stop Service

ถ้าต้องการหยุด server:

```bash
sudo systemctl stop modbus-dashboard.service
```

ถ้าต้องการปิดไม่ให้รันตอน boot:

```bash
sudo systemctl disable modbus-dashboard.service
```

---

## 11. ทดสอบ Boot จริง

สั่ง reboot:

```bash
sudo reboot
```

รอเครื่องเปิดกลับมา แล้วเปิด Browser จาก PC:

```text
http://192.168.1.125:8000
```

ถ้าเข้า Dashboard ได้ทันที แปลว่า `systemd` ทำงานถูกต้องแล้ว

---

## Troubleshooting

### 1. Service ขึ้น Permission denied: /dev/ttyUSB0

ตรวจสอบว่า user อยู่ในกลุ่ม `dialout`:

```bash
groups pi0001
```

ถ้ายังไม่มี `dialout`:

```bash
sudo usermod -aG dialout pi0001
sudo reboot
```

---

### 2. Service หา module ไม่เจอ

เช่น:

```text
ModuleNotFoundError: No module named 'fastapi'
```

ให้ตรวจสอบว่า `.venv` ถูกต้อง และติดตั้ง package แล้ว:

```bash
cd /home/pi0001/industrial-linux-modbus-fastapi-dashboard
source .venv/bin/activate
pip install -r requirements.txt
```

ถ้ายังไม่มี `requirements.txt`:

```bash
pip install fastapi uvicorn pymodbus pyserial
pip freeze > requirements.txt
```

---

### 3. Service หา `app.py` ไม่เจอ

ตรวจสอบ `WorkingDirectory` ใน service ว่าชี้ไปยังโฟลเดอร์ที่มี `app.py`

กรณีโครงสร้างมาตรฐาน:

```ini
WorkingDirectory=/home/pi0001/industrial-linux-modbus-fastapi-dashboard/src
```

กรณีโครงสร้างเดิม:

```ini
WorkingDirectory=/home/pi0001/src
```

---

### 4. แก้ service แล้วไม่เปลี่ยน

หลังแก้ไฟล์ `/etc/systemd/system/modbus-dashboard.service` ต้องรัน:

```bash
sudo systemctl daemon-reload
sudo systemctl restart modbus-dashboard.service
```

---

## Uninstall / Cleanup

ถ้าต้องการถอด service แบบ `systemd + .venv` ออกจากเครื่อง ให้หยุด service และปิดการรันตอน boot ก่อน:

```bash
sudo systemctl stop modbus-dashboard.service
sudo systemctl disable modbus-dashboard.service
```

จากนั้นลบไฟล์ service และ reload systemd:

```bash
sudo rm /etc/systemd/system/modbus-dashboard.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

ตรวจสอบว่า service ไม่อยู่แล้ว:

```bash
sudo systemctl status modbus-dashboard.service
```

ถ้าต้องการลบโฟลเดอร์โปรเจกต์และ `.venv` ด้วย ให้ตรวจสอบตำแหน่งก่อน:

```bash
pwd
ls -l /home/pi0001
```

เมื่อตรวจสอบแน่ใจแล้วว่า path ถูกต้อง จึงค่อยลบ:

```bash
cd /home/pi0001
rm -rf industrial-linux-modbus-fastapi-dashboard
```

> หมายเหตุ: ถ้าเครื่องของคุณใช้ user อื่น เช่น `pi` หรือ `ubuntu` ให้เปลี่ยน `/home/pi0001` ให้ตรงกับเครื่องจริงก่อนรันคำสั่งลบ

---
## สรุป EP5

ใน EP นี้เราเปลี่ยนจากการรัน `uvicorn` ด้วยมือ มาเป็นให้ `systemd` จัดการแทน โดยยังรันจาก `.venv` บนเครื่อง Linux โดยตรง

คำสั่งที่ใช้บ่อย:

```bash
sudo systemctl status modbus-dashboard.service
sudo systemctl restart modbus-dashboard.service
journalctl -u modbus-dashboard.service -f
```

หลังจากนี้ Dashboard จะเริ่มทำงานเองทุกครั้งเมื่อ Linux gateway boot

ถ้าวันหลังเปลี่ยนไปใช้ EP6 แบบ Podman + Quadlet ให้ `disable` หรือ `stop` service ของ EP5 ก่อน เพื่อไม่ให้ทั้งสองวิธีแย่ง port `8000` กัน