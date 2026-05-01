import busio
import board
import time
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
 
# Initialisation de l'interface i2c
i2c = busio.I2C(board.SCL, board.SDA)
 
# Créer une instance de la classe ADS1115 
# et l'associer à l'interface i2c
ads = ADS1115(i2c)
 
# Créer une instance d'entrée analogique
# et l'associer à la broche 0 du module ADC
x = AnalogIn(ads, 0)
y = AnalogIn(ads, 1) 

# Grid size for matrix
GRID_SIZE = 8
MAXIMUM_VALUE_FOR_8BIT = 32767
# Dead zone threshold (optional, depending on joystick behavior)
DEAD_ZONE = 1000

# Number of readings to average
NUM_SAMPLES = 10

def read_average(channel):
    """Take multiple samples and return the average"""
    readings = [channel.value for _ in range(NUM_SAMPLES)]
    return sum(readings) // len(readings)

def scale_value(value, max_val=65535,  grid_size=GRID_SIZE):
    # Scales avec la matrix
    return int((value / max_val) * (grid_size - 1))

try:
    while True:
        raw_x = read_average(x)
        raw_y = read_average(y)

        if abs(raw_x - MAXIMUM_VALUE_FOR_8BIT) < DEAD_ZONE:  
            raw_x = MAXIMUM_VALUE_FOR_8BIT
        if abs(raw_y - MAXIMUM_VALUE_FOR_8BIT) < DEAD_ZONE:
            raw_y = MAXIMUM_VALUE_FOR_8BIT
        
        # Apply scaling to convert ADC values to a usable range (-1 to 1)
        grid_x = scale_value(raw_x)
        grid_y = scale_value(raw_y)

        print(f"Joystick Position -> X: {grid_x}, Y: {grid_y}")

except KeyboardInterrupt:
    print("Programme interrompu.")