# คู่มือการสแกน Modbus RTU ด้วย Raspberry Pi และ USB-RS485

## วัตถุประสงค์

คู่มือนี้อธิบายการเตรียม Raspberry Pi เพื่อค้นหา (Scan) Modbus Address ของอุปกรณ์ RS485 ผ่าน USB-RS485 Adapter

---

# 1. อัปเดตระบบ

```bash
sudo apt update
```

---

# 2. ติดตั้งโปรแกรมที่จำเป็น

ติดตั้ง Python, PySerial และโปรแกรม `mbpoll`

```bash
sudo apt install python3-pip python3-serial mbpoll -y
```

---

# 3. ตรวจสอบว่า Raspberry Pi พบ USB-RS485 แล้ว

```bash
ls -l /dev/ttyUSB*
```

ตัวอย่างผลลัพธ์

```text
crw-rw---- 1 root dialout 188, 0 Jun 30 12:53 /dev/ttyUSB0
```

หากพบ `/dev/ttyUSB0` แสดงว่า Raspberry Pi มองเห็น USB-RS485 แล้ว

---

# 4. ตรวจสอบสิทธิ์ของผู้ใช้

```bash
groups
```

ควรมี

```text
dialout
```

เช่น

```text
pi0001 adm dialout cdrom sudo audio video plugdev users gpio i2c spi
```

หากไม่มี `dialout`

```bash
sudo usermod -aG dialout $USER
```

จากนั้น Logout และ Login ใหม่

---

# 5. ทดสอบเปิด Serial Port

```bash
python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0',9600,timeout=1); print('OK'); s.close()"
```

ผลลัพธ์ที่ถูกต้อง

```text
OK
```

---

# 6. สแกน Modbus Address

ตัวอย่างนี้ใช้

* Baud Rate : 9600
* Data Bits : 8
* Parity : None
* Stop Bits : 1
* Function Code : 03 (Read Holding Registers)

สแกน Address 1–20

```bash
for id in $(seq 1 20); do
    echo "Scan ID $id"
    mbpoll -m rtu -b 9600 -P none -a $id -t 3 -r 1 -c 1 /dev/ttyUSB0 -1 -q && echo "FOUND $id"
done
```

---

# 7. ตัวอย่างผลลัพธ์

กรณีไม่พบอุปกรณ์

```text
Scan ID 5
Read holding register failed: Connection timed out
```

หมายความว่า

* ไม่มีอุปกรณ์ที่ Address นี้
* หรือ Baud Rate / Function Code ไม่ถูกต้อง

---

กรณีพบอุปกรณ์

```text
Scan ID 1
-- Polling slave 1...
[1]: 4

FOUND 1
```

หมายความว่า

* พบ Modbus Device
* Modbus Address = 1
* อ่าน Register สำเร็จ

---

# 8. หากไม่พบอุปกรณ์

ตรวจสอบตามลำดับ

* ตรวจสอบไฟเลี้ยง Sensor
* ตรวจสอบสาย RS485 A/B ไม่สลับ
* ตรวจสอบ Baud Rate
* ตรวจสอบ Modbus Address
* ทดลอง Function Code 04
* ทดลอง Register Address อื่น

---

# 9. ทดลอง Function Code 04

อุปกรณ์บางรุ่นเก็บค่าที่วัดได้ไว้ใน Input Register

ตัวอย่าง

```bash
for id in $(seq 1 20); do
    echo "Scan ID $id"
    mbpoll -m rtu -b 9600 -P none -a $id -t 4 -r 1 -c 1 /dev/ttyUSB0 -1 -q && echo "FOUND $id"
done
```

หาก FC03 ไม่พบ แต่ FC04 พบ แสดงว่าอุปกรณ์ใช้ **Input Register**

---

# 10. ความหมายของ Function Code

| Function Code | รายละเอียด               |
| ------------: | ------------------------ |
|            01 | Read Coils               |
|            02 | Read Discrete Inputs     |
|            03 | Read Holding Registers   |
|            04 | Read Input Registers     |
|            05 | Write Single Coil        |
|            06 | Write Single Register    |
|            15 | Write Multiple Coils     |
|            16 | Write Multiple Registers |

โดยทั่วไป

* **FC03** ใช้อ่านค่าที่สามารถเขียนได้ เช่น การตั้งค่า (Configuration)
* **FC04** ใช้อ่านค่าที่วัดได้จากเซนเซอร์ เช่น ความเร็วลม อุณหภูมิ ความชื้น ความดัน และค่าจากเซนเซอร์ต่าง ๆ

---

# 11. ขั้นตอนถัดไป

เมื่อทราบแล้วว่า

* Serial Port คือ `/dev/ttyUSB0`
* Baud Rate เท่าใด
* Modbus Address เท่าใด
* ใช้ Function Code 03 หรือ 04

ก็สามารถนำข้อมูลไปพัฒนาโปรแกรม Python หรือ FastAPI เพื่ออ่านค่าและแสดงผลผ่านหน้าเว็บได้ต่อไป
