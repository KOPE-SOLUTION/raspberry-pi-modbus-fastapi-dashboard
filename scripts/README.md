# Scripts

โฟลเดอร์นี้เก็บ Utility Script สำหรับใช้งานกับ Raspberry Pi และ Modbus RTU

## Requirements

ติดตั้งโปรแกรมที่จำเป็นก่อน

```bash
sudo apt update
sudo apt install python3-pip python3-serial mbpoll -y
```

ตรวจสอบว่า Raspberry Pi พบ USB-RS485

```bash
ls -l /dev/ttyUSB*
```

ตัวอย่าง

```text
/dev/ttyUSB0
```

---

## scan_modbus.sh

ใช้สแกนหา Modbus Slave Address ของอุปกรณ์ที่เชื่อมต่อผ่าน USB-RS485

### ให้สิทธิ์ในการรัน

```bash
chmod +x scan_modbus.sh
```

### เริ่มสแกน

```bash
./scan_modbus.sh
```

### ตัวอย่างผลลัพธ์

```text
Scan ID 1
-- Polling slave 1...
[1]:    4

FOUND 1

Scan ID 2
Read input register failed: Connection timed out
```

หมายความว่า

* พบอุปกรณ์ที่ Modbus Address 1
* Address 2 ไม่มีอุปกรณ์ตอบกลับ

---

## แก้ไขค่า Baud Rate

ภายใน `scan_modbus.sh`

```bash
-b 9600
```

สามารถเปลี่ยนเป็น

```text
4800
9600
19200
38400
115200
```

ตามการตั้งค่าของอุปกรณ์

---

## เปลี่ยน Function Code

สำหรับ Modbus RTU

| Function Code | ความหมาย               |
| ------------: | ---------------------- |
|            03 | Read Holding Registers |
|            04 | Read Input Registers   |

ตัวอย่าง

```bash
-t 3
```

หรือ

```bash
-t 4
```

---

## เปลี่ยนช่วง Address

ค้นหาเฉพาะ Address 1–20

```bash
seq 1 20
```

หากต้องการค้นหาทั้งหมด

```bash
seq 1 247
```

---

## เปลี่ยน Register Address

ตัวอย่างอ่าน Register 1

```bash
-r 1
```

หากคู่มือระบุ Register 0

```bash
-r 0
```

---

## หมายเหตุ

หากไม่พบอุปกรณ์ ให้ตรวจสอบ

* USB-RS485 Adapter
* สาย RS485 A/B
* ไฟเลี้ยง Sensor
* Baud Rate
* Modbus Address
* Function Code
* Register Address
