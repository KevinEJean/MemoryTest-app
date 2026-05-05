import busio
import board
import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bus_device.i2c_device as i2c_device

# Initialisation
i2c = busio.I2C(board.SCL, board.SDA)
i2cBus = busio.I2C(board.SCL, board.SDA) 
ads = ADS1115(i2c)
matrix_device = i2c_device.I2CDevice(i2cBus, 0x77)

x_pin = AnalogIn(ads, 0)
y_pin = AnalogIn(ads, 1) 

# --- CONFIGURATION ---
GRID_SIZE = 8
# The dead zone prevents the dot from drifting when you aren't touching the stick
DEAD_ZONE = 8000     
# Adjust this to control how fast the dot travels across the screen
# Lower = Slower (e.g., 0.05 is very slow)
MOVE_SPEED = 0.2     
CENTER_VAL = 13250   # This represents the "Resting" state of your joystick

# These variables "remember" where the dot is. 
# They are only updated when the joystick is moved.
dot_x = 0.0
dot_y = 7.0

def calculate_step(raw_value):
    diff = raw_value - CENTER_VAL
    
    # If within the dead zone, change is 0 (stays where it was)
    if abs(diff) < DEAD_ZONE:
        return 0
    
    # Scale the movement. 16000 is approx the distance from center to max tilt.
    step = (diff / 16000) * MOVE_SPEED

    return step

with matrix_device as mem:
    mem.write(bytes([0x81])) # Matrix ON
    mem.write(bytes([0xEF])) # Brightness

try:
    while True:
        # 1. Get the 'tilt' from the joystick
        change_x = calculate_step(x_pin.value)
        change_y = calculate_step(y_pin.value)

        # 2. Add the change to the previous position
        # If change_x is 0, dot_x stays exactly the same.
        dot_x += change_x
        dot_y += change_y 

        # 3. Keep the dot inside the 0-7 boundaries
        dot_x = max(0.0, min(7.0, dot_x))
        dot_y = max(0.0, min(7.0, dot_y))

        # 4. Convert the math (float) to the LED pixel (int)
        display_x = int(round(dot_x))
        display_y = int(round(dot_y))

        # 5. Send data to the 8x8 Matrix
        buffer = bytearray([0] * 17) 
        buffer[0] = 0x00 
        row_index = (display_y * 2) + 1 
        buffer[row_index] = (1 << display_x)

        with matrix_device as mem:
            mem.write(buffer)

        # Small delay for a smooth 50Hz refresh rate
        time.sleep(0.02) 

except KeyboardInterrupt:
    with matrix_device as mem:
        mem.write(bytearray([0x00] * 17))
    print("Programme interrompu.")