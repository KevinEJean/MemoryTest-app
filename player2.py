import busio
import board
import time
import random
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bus_device.i2c_device as i2c_device
import paho.mqtt.client as pmc
import json
# --- INITIALIZATION de Raspi Pi---
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
matrix_device = i2c_device.I2CDevice(i2c, 0x70)
x_pin = AnalogIn(ads, 0)
y_pin = AnalogIn(ads, 1)

# MQQT Initialisation 
BROKER = "10.10.21.144"
PORT = 1883
GAME_TOPIC = "map"

# Data a envoyer par MQQT
player2_data = {
    "player2_scores" : None
}
# Scoring and Rounds
rounds = 0
scores = 0
# --- CONFIGURATION ---
MOVE_SPEED = 0.4
CENTER_VAL = 13250
DEAD_ZONE = 8000
NUM_TARGETS = 10  # Set how many dots you want

# Player Setup
dot_x, dot_y = 0.0, 7.0

# --- TARGET SYSTEM ---
# This creates a list of 10 random [x, y] pairs
targets = []
for _ in range(NUM_TARGETS):
    targets.append([random.randint(0, 7), random.randint(0, 7)])

def calculate_step(raw_value):
    diff = raw_value - CENTER_VAL
    if abs(diff) < DEAD_ZONE: return 0
    return (diff / 16000) * MOVE_SPEED

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
        client.subscribe(GAME_TOPIC)
    else:
        print("Erreur code %d\n", code)

def reception_msg(cl,userdata,msg):
    print("Reçu:",msg.payload.decode())

def publication(client, userdata, mid, code, properties):
    print("Envoi confirmé message #" + str(scores))

# Connexion MQQT
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg
# client.on_publish = publication

# Setup Matrix
with matrix_device as mem:
    mem.write(bytes([0x21])) 
    mem.write(bytes([0x81])) 
    mem.write(bytes([0xEF])) 

try:
    client.connect(BROKER, PORT)
    while True:
        # 1. Update Player Position
        dot_x = max(0.0, min(7.0, dot_x + calculate_step(x_pin.value)))
        dot_y = max(0.0, min(7.0, dot_y + calculate_step(y_pin.value)))
        px, py = int(round(dot_x)), int(round(dot_y))

        # 2. COLLISION DETECTION (Capture and Remove)
        # We loop through a copy of the list [:] so we don't crash while removing items
        for t in targets[:]: 
            if px == t[0] and py == t[1]:
                targets.remove(t) # Remove the dot from existence!
                print(f"Captured! {len(targets)} dots remaining.")
                scores += len(targets)
                print(f"Score: {scores}")

        # 3. WIN CONDITION
        if not targets:
            print("Level Cleared! Spawning new wave...")
            time.sleep(1)
            rounds += 1
            # Re-spawn 10 new dots if you want the game to loop
            targets = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(10)]
            if rounds == 1:
                print("Fin du programme")
                player2_data["player2_scores"] = scores
                json_payload = json.dumps(player2_data)
                client.publish(GAME_TOPIC, json_payload)
                with matrix_device as mem:
                    mem.write(bytearray([0x00] * 17))               
                break 

        # 4. RENDER
        buffer = bytearray([0] * 17)
        buffer[0] = 0x00
        
        # Draw remaining targets
        for t in targets:
            row_idx = (t[1] * 2) + 1
            buffer[row_idx] |= (1 << t[0])
            
        # Draw player
        player_row_idx = (py * 2) + 1
        buffer[player_row_idx] |= (1 << px)

        with matrix_device as mem:
            mem.write(buffer)

        time.sleep(0.02)

except KeyboardInterrupt:
    with matrix_device as mem:
        mem.write(bytearray([0x00] * 17))