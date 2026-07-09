# EP2 — Python Modbus Reader

ใน EP นี้ เราจะต่อยอดจาก EP1 ที่สแกนเจออุปกรณ์ Modbus RTU แล้ว โดยนำค่าที่ได้จาก `mbpoll` มาเขียนเป็น Python Script สำหรับอ่านค่าจาก Sensor ผ่าน USB-RS485

---

## เป้าหมายของ EP2

สร้างไฟล์ `modbus_reader.py` เพื่ออ่านค่า Sensor ผ่าน Modbus RTU และแสดงผลเป็นข้อมูลแบบ Dictionary

ตัวอย่างผลลัพธ์ที่ต้องการ:

```python
{
    "pm1_0": 8,
    "pm2_5": 14,
    "pm10": 18
}
```

---

## ค่าที่ได้จาก EP1

จากการทดสอบด้วย mbpoll เราได้ค่าที่ใช้งานจริงดังนี้:

```sh
Serial Port   : /dev/ttyUSB0
Baudrate      : 9600
Data Bits     : 8
Parity        : None
Stop Bit      : 1
Slave Address : 1
Function Code : 04
Start Register: 1
Register Count: 3
```

<br>

คำสั่ง `mbpoll` ที่ทดสอบผ่าน:

```sh
mbpoll -m rtu -b 9600 -P none -a 1 -t 4 -r 1 -c 3 /dev/ttyUSB0
```

<br>

ตัวอย่างผลลัพธ์:

```sh
[1]:    8
[2]:    14
[3]:    18
```

---

## โครงสร้างไฟล์ใน EP2

```sh
src/
└── modbus_reader.py
```

---

## Step 1 — ติดตั้ง Python Library

ติดตั้ง `pymodbus`

```sh
sudo apt update
sudo apt install python3-pip -y
pip3 install pymodbus
```

<br>

ทดสอบว่า import ได้:

```sh
python3 -c "import pymodbus; print('pymodbus OK')"
```

---

Step 2 — สร้างไฟล์ modbus_reader.py

สร้างโฟลเดอร์และไฟล์:

```sh
mkdir -p src
nano src/modbus_reader.py
```

---

## Step 3 — กำหนดค่า Serial / Modbus

```py
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SLAVE_ID = 1
START_REGISTER = 1
REGISTER_COUNT = 3
```

---

## Step 4 — เขียนโค้ดอ่าน Input Register

> ใน EP นี้ใช้งาน Function Code 04
> ใน pymodbus จะใช้คำสั่ง read_input_registers()

```py
from pymodbus.client import ModbusSerialClient

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SLAVE_ID = 1
START_REGISTER = 1
REGISTER_COUNT = 3


def read_sensor():
    client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    if not client.connect():
        return {
            "status": "error",
            "message": "Cannot connect to serial port"
        }

    try:
        result = client.read_input_registers(
            address=START_REGISTER,
            count=REGISTER_COUNT,
            slave=SLAVE_ID
        )

        if result.isError():
            return {
                "status": "error",
                "message": str(result)
            }

        registers = result.registers

        data = {
            "status": "ok",
            "pm1_0": registers[0],
            "pm2_5": registers[1],
            "pm10": registers[2]
        }

        return data

    finally:
        client.close()


if __name__ == "__main__":
    data = read_sensor()
    print(data)
```

---

## Step 5 — รันโปรแกรม

```sh
python3 src/modbus_reader.py
```

<br>

ตัวอย่างผลลัพธ์:

```json
{'status': 'ok', 'pm1_0': 8, 'pm2_5': 14, 'pm10': 18}
```

---

## Step 6 — อธิบาย Mapping ของ Register

จากคำสั่ง `mbpoll`:

```sh
[1]: 8
[2]: 14
[3]: 18
```

<br>

เรานำมา Mapping เป็น:

| Register | Field | Unit  |
| -------: | ----- | ----- |
|        1 | pm1_0 | µg/m³ |
|        2 | pm2_5 | µg/m³ |
|        3 | pm10  | µg/m³ |

<br>

ดังนั้นใน Python:

```py
data = {
    "pm1_0": registers[0],
    "pm2_5": registers[1],
    "pm10": registers[2]
}
```

---

## Step 7 — เพิ่ม Timestamp

แก้ไขโค้ดโดยเพิ่ม `time`

```py
import time
```

<br>

แล้วเพิ่มใน Dictionary:

```py
"timestamp": int(time.time())
```

<br>

ตัวอย่าง:

```py
data = {
    "status": "ok",
    "pm1_0": registers[0],
    "pm2_5": registers[1],
    "pm10": registers[2],
    "timestamp": int(time.time())
}
```

---

## Step 8 — โค้ดฉบับสมบูรณ์

```py
import time
from pymodbus.client import ModbusSerialClient

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SLAVE_ID = 1
START_REGISTER = 1
REGISTER_COUNT = 3


def read_sensor():
    client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
        parity="N",
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    if not client.connect():
        return {
            "status": "error",
            "message": "Cannot connect to serial port",
            "timestamp": int(time.time())
        }

    try:
        result = client.read_input_registers(
            address=START_REGISTER,
            count=REGISTER_COUNT,
            slave=SLAVE_ID
        )

        if result.isError():
            return {
                "status": "error",
                "message": str(result),
                "timestamp": int(time.time())
            }

        registers = result.registers

        return {
            "status": "ok",
            "pm1_0": registers[0],
            "pm2_5": registers[1],
            "pm10": registers[2],
            "timestamp": int(time.time())
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": int(time.time())
        }

    finally:
        client.close()


if __name__ == "__main__":
    data = read_sensor()
    print(data)
```

---

## Step 9 — ทดสอบอ่านค่าหลายครั้ง

รันแบบวนทุก 2 วินาที:

```bash
watch -n 2 python3 src/modbus_reader.py
```

<br>

ตัวอย่าง:

```bash
Every 2.0s: python3 src/modbus_reader.py

{'status': 'ok', 'pm1_0': 8, 'pm2_5': 14, 'pm10': 18, 'timestamp': 1783650000}
```

---

## Troubleshooting

1. Permission denied: /dev/ttyUSB0

ตรวจสอบสิทธิ์:

```bash
groups
```
ควรมี `dialout`

ถ้าไม่มี:

```bash
sudo usermod -aG dialout $USER
```

จากนั้น Logout แล้ว Login ใหม่

<br>

2. Cannot connect to serial port

ตรวจสอบว่าเจอ USB-RS485 หรือไม่:

```bash
ls -l /dev/ttyUSB*
```

<br>

3. Modbus timeout

ตรวจสอบ:
- Sensor มีไฟเลี้ยงหรือไม่
- สาย A/B ต่อถูกหรือไม่
- Baudrate ถูกต้องหรือไม่
- Slave Address ถูกต้องหรือไม่
- Function Code ถูกต้องหรือไม่
- Register Address ถูกต้องหรือไม่

<br>

4. pymodbus import ไม่ได้

ติดตั้งใหม่:

```bash
pip3 install pymodbus
```

---

## สรุป

ใน EP นี้ เราได้สร้าง `modbus_reader.py` สำหรับอ่านค่าจาก Sensor ผ่าน Modbus RTU โดยใช้ข้อมูลที่ค้นพบจาก EP1

ผลลัพธ์สุดท้ายคือ Python Dictionary:

```json
{
    "status": "ok",
    "pm1_0": 8,
    "pm2_5": 14,
    "pm10": 18,
    "timestamp": 1783650000
}
```

ข้อมูลนี้จะถูกนำไปใช้ต่อใน EP3 เพื่อสร้าง FastAPI Endpoint