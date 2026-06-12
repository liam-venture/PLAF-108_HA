import serial
import sys

if len(sys.argv) < 2:
    print("Usage: python read_boot.py <port>")
    print("  macOS: /dev/cu.usbserial-XXX")
    print("  Linux: /dev/ttyUSB0")
    sys.exit(1)

PORT = sys.argv[1]

print(f"Listening on {PORT} — power cycle the PLAF108 now")
print("-" * 60)

with serial.Serial(PORT, 115200, timeout=10) as ser:
    while True:
        data = ser.read(1)
        if data:
            try:
                print(data.decode('utf-8'), end='', flush=True)
            except:
                print(f'[{hex(data[0])}]', end='', flush=True)
