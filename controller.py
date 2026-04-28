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
# Lire la valeur numérique et le voltage
try:
    while True:
        print(x.value, y.value)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Programme interrompu.")