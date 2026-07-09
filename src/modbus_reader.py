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
        result = client.read_holding_registers(
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