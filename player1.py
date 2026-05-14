import busio
import board
import time
import random
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_bus_device.i2c_device as i2c_device
import paho.mqtt.client as pmc
import json
import threading
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
global targets
targets = 0
game_running = False

# Data a envoyer par MQQT
player1_data = {
    "player1_scores" : None
}
# Scoring and Rounds
rounds = 0
scores = 0
# --- CONFIGURATION ---
MOVE_SPEED = 0.4
CENTER_VAL = 13250
DEAD_ZONE = 9000
NUM_TARGETS = 10  # Set how many dots you want

# Player Setup
dot_x, dot_y = 0.0, 7.0

# --- TARGET SYSTEM ---
# This creates a list of 10 random [x, y] pairs
global targets_list
global targets_list2
global targets_list3
targets_list = []
targets_list2 = []
targets_list3 = []

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
    global targets_list
    global targets_list2
    global targets_list3
    global game_running
    global rounds
    try:
        data = json.loads(msg.payload.decode())

        # Check if the message contains the map
        if data.get("type") == "MAP_DATA":
                game_running = True
                rounds = 0
                targets_list = data.get("targets", [])
            
                targets_list2 = data.get("targets1", [])
            
                targets_list3 = data.get("targets2",[])
                
            
                print(f"Map Loaded: {targets_list}")

        # elif data.get("type") == "GAME_STATE" and data.get("game_state") == "end":
        #     game_running = False
        #     targets = []
        #     print("Timer hit zero! Game stopped.")
        #     clearMatrix()
    except: # works but any exception will trigger this
        data = msg.payload.decode()
        game_running = False
        targets = []
        clearMatrix()
        print(data)
        return

    print("Reçu:",msg.payload.decode())

def publication(client, userdata, mid, code, properties):
    print("Envoi confirmé message #" + str(scores))

def clearMatrix():
    with matrix_device as mem:
        mem.write(bytearray([0x00] * 17))
    
    time.sleep(0.5)

# Connexion MQQT
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg
threading.Thread(target=client.loop_forever, daemon=True).start()

# Setup Matrix
with matrix_device as mem:
    mem.write(bytes([0x21])) 
    mem.write(bytes([0x81])) 
    mem.write(bytes([0xEF])) 

try:
    client.connect(BROKER, PORT)
    while True:
        print(game_running)
        while game_running:
            # 1. Update Player Position
            dot_x = max(0.0, min(7.0, dot_x + calculate_step(x_pin.value)))
            dot_y = max(0.0, min(7.0, dot_y + calculate_step(y_pin.value)))
            px, py = int(round(dot_x)), int(round(dot_y))

            # 2. COLLISION DETECTION (Capture and Remove)
            # We loop through a copy of the list [:] so we don't crash while removing items
            for t in targets_list[:]: 
                if px == t[0] and py == t[1]:
                    targets_list.remove(t) # Remove the dot from existence!
                    print(f"Captured! {len(targets_list)} dots remaining.")
                    scores += len(targets_list)
                    print(f"Score: {scores}")

            # 3. WIN CONDITION
            if not targets_list:

               dot_x, dot_y = 0.0, 7.0 # Reset player
     
               if rounds == 0:
                    print("Map 1 Cleared! Loading Map 2...")
                    targets_list = list(targets_list2)
                    rounds = 1
                    dot_x, dot_y = 0.0, 7.0 # Reset player
                    time.sleep(0.5)
               elif rounds == 2:
                    print("Map 1 Cleared! Loading Map 2...")
                    targets_list = list(targets_list3)
                    rounds = 2
                    dot_x, dot_y = 0.0, 7.0 # Reset player
                    time.sleep(0.5)
     
               else:
                    print("Fin du programme")
                    player1_data["player1_scores"] = scores
                    json_payload = json.dumps(player1_data)
                    client.publish(GAME_TOPIC, json_payload)
                    clearMatrix()
                    dot_x, dot_y = 0.0, 7.0 # Reset player
                    game_running = False
                    rounds = 0
                    scores = 0            

            # 4. RENDER
            buffer = bytearray([0] * 17)
            buffer[0] = 0x00
            
            # Draw remaining targets
            for t in targets_list:
                row_idx = (t[1] * 2) + 1
                buffer[row_idx] |= (1 << t[0])
                
            # Draw player
            player_row_idx = (py * 2) + 1
            buffer[player_row_idx] |= (1 << px)

            with matrix_device as mem:
                mem.write(buffer)

            time.sleep(0.02)

except KeyboardInterrupt:
    clearMatrix()