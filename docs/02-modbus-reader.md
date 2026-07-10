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

## Step 1 — ติดตั้ง Python Library ใน Virtual Environment

เปิดใช้งาน `.venv` ที่สร้างไว้จาก EP1 แล้วติดตั้ง `pymodbus` ด้วย `pip`

```sh
source .venv/bin/activate
pip install pymodbus
```

<br>

ทดสอบว่า import ได้:

```sh
python -c "import pymodbus; print('pymodbus OK')"
```

---

## Step 2 — สร้างไฟล์ modbus_reader.py

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
START_REGISTER = 0
REGISTER_COUNT = 3
```

> หมายเหตุ: ใน `mbpoll` เราทดสอบด้วย `-r 1` แต่ใน `pymodbus` มักอ้าง register แบบ zero-based ดังนั้น Register 1 จึงใช้ `address=0`

---

## Step 4 — เขียนโค้ดอ่าน Input Register

> ใน EP นี้ใช้งาน Function Code 04
> ใน pymodbus จะใช้คำสั่ง read_input_registers()

```py
from pymodbus.client import ModbusSerialClient

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SLAVE_ID = 1
START_REGISTER = 0
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
        try:
            result = client.read_input_registers(
                address=START_REGISTER,
                count=REGISTER_COUNT,
                device_id=SLAVE_ID
            )
        except TypeError:
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
python src/modbus_reader.py
```

<br>

ตัวอย่างผลลัพธ์:

```python
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
|        1 | pm1_0 | ug/m3 |
|        2 | pm2_5 | ug/m3 |
|        3 | pm10  | ug/m3 |

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

## ถ้า Sensor มีจำนวน Parameter ไม่เท่ากับตัวอย่าง

ตัวอย่างใน EP นี้อ่าน 3 Register เพราะอุปกรณ์ตัวอย่างมี 3 ค่า คือ PM1.0, PM2.5 และ PM10

```py
REGISTER_COUNT = 3
```

และนำค่าจาก `registers` มา map แบบนี้:

```py
return {
    "status": "ok",
    "pm1_0": registers[0],
    "pm2_5": registers[1],
    "pm10": registers[2],
    "timestamp": int(time.time())
}
```

ถ้า Sensor ของคุณมีเพียง 1 ค่า เช่น temperature ให้ปรับเป็น:

```py
REGISTER_COUNT = 1
```

แล้ว map ค่าเดียว:

```py
return {
    "status": "ok",
    "temperature": registers[0],
    "timestamp": int(time.time())
}
```

ถ้า Sensor มี 2 ค่า เช่น temperature และ humidity ให้ใช้:

```py
REGISTER_COUNT = 2
```

แล้ว map ตามลำดับ Register:

```py
return {
    "status": "ok",
    "temperature": registers[0],
    "humidity": registers[1],
    "timestamp": int(time.time())
}
```

จุดสำคัญคือต้องดู Datasheet หรือ Modbus Register Map ของอุปกรณ์จริงก่อนเสมอ โดยดูว่าแต่ละค่าถูกเก็บอยู่ที่ Register ใด ใช้ Function Code 03 หรือ 04 และค่าที่อ่านได้ต้องหาร scale หรือไม่ เช่น บางอุปกรณ์เก็บ `253` เพื่อแทน `25.3` องศา แบบนี้ต้องแปลงค่าก่อนส่งออกเป็น JSON

ตัวอย่างการแปลง scale:

```py
temperature = registers[0] / 10
```

ถ้าเปลี่ยนชื่อ field ใน `modbus_reader.py` แล้ว ใน EP4 ต้องเปลี่ยน HTML และ JavaScript ให้ตรงกันด้วย เช่น ถ้า API ส่ง `temperature` หน้า Dashboard ก็ต้องใช้ `data.temperature` แทน `data.pm2_5`
### ตัวอย่าง: เพิ่ม Solar Radiation Sensor

สมมติว่าเราต้องการเปลี่ยนจากเซ็นเซอร์ฝุ่น มาอ่าน Solar Radiation Sensor ผ่าน Modbus RTU ขั้นตอนที่ควรทำคือ:

1. เปิด Datasheet หรือ Modbus Register Map ของ Solar Radiation Sensor
2. ดูว่าอุปกรณ์ใช้ Slave ID เท่าไร เช่น `1`
3. ดูว่าใช้ Function Code ใด เช่น FC04 หรือ FC03
4. ดูว่า Solar Radiation อยู่ที่ Register ใด เช่น Register 1
5. ดูว่าต้องอ่านกี่ Register เช่น 1 Register
6. ดูว่าค่าที่อ่านได้ต้องหาร scale หรือไม่ เช่น หาร 10

ถ้า Register Map ระบุประมาณนี้:

| Parameter | Function Code | Register | Count | Scale | Unit |
| --- | --- | ---: | ---: | ---: | --- |
| Solar Radiation | FC04 | 1 | 1 | 1 | W/m2 |

ให้ทดสอบด้วย `mbpoll` ก่อน:

```bash
mbpoll -m rtu -b 9600 -P none -a 1 -t 4 -r 1 -c 1 /dev/ttyUSB0
```

ถ้าอ่านได้ เช่น:

```text
[1]: 756
```

แปลว่าเราสามารถปรับ `modbus_reader.py` ได้ประมาณนี้:

```py
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SLAVE_ID = 1
START_REGISTER = 0
REGISTER_COUNT = 1
```

แล้วเปลี่ยนส่วน return เป็น:

```py
return {
    "status": "ok",
    "solar_radiation": registers[0],
    "timestamp": int(time.time())
}
```

ถ้า Datasheet ระบุ scale เป็น 0.1 หรือบอกว่าค่าจริง = register / 10 ให้เขียนแบบนี้:

```py
solar_radiation = registers[0] / 10

return {
    "status": "ok",
    "solar_radiation": solar_radiation,
    "timestamp": int(time.time())
}
```

หลังจากเปลี่ยน `modbus_reader.py` แล้ว ให้ทดสอบก่อน:

```bash
python src/modbus_reader.py
```

ควรได้ผลลัพธ์ประมาณนี้:

```python
{'status': 'ok', 'solar_radiation': 756, 'timestamp': 1783650000}
```

จากนั้นใน EP4 ให้แก้หน้า Dashboard จาก `pm1_0`, `pm2_5`, `pm10` เป็น field ใหม่ เช่น `solar_radiation` และแก้ JavaScript จาก:

```js
document.getElementById("pm2_5").textContent = data.pm2_5;
```

เป็น:

```js
document.getElementById("solar_radiation").textContent = data.solar_radiation;
```
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
START_REGISTER = 0
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
        try:
            result = client.read_input_registers(
                address=START_REGISTER,
                count=REGISTER_COUNT,
                device_id=SLAVE_ID
            )
        except TypeError:
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

รันแบบวนทุก 1 วินาที:

```bash
watch -n 1 python src/modbus_reader.py
```

<br>

ตัวอย่าง:

```bash
Every 1.0s: python src/modbus_reader.py

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

เปิดใช้งาน `.venv` แล้วติดตั้งใหม่:

```bash
source .venv/bin/activate
pip install pymodbus
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
