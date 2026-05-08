from flask import Flask, jsonify, request
from flask_cors import CORS
import pigpio
import time
import threading
import socket
import board
import busio
import adafruit_bus_device.i2c_device as i2c_device
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn
import random
import paho.mqtt.client as pmc

# VARIABLE PIGPIO
pi = pigpio.pi()
i2c = busio.I2C(board.SCL, board.SDA)
matrix = i2c_device.I2CDevice(i2c, 0x70)
R,G,B = 21,20,16
BUZZER = 19
ads = ADS1115(i2c)
BTN = 19

# Flask
app = Flask(__name__)
CORS(app)

# MQQT Variables
# Broker = 10.10.41.134
# GAME_TOPIC = "map"
# PORT = 1883

# Donne des joueurs
player1_data = {
    "player1_scores" : None
}
player2_data = {
    "player2_scores" : None
}

# Initialisation de la matrix 8x8
matrix.write(bytes([0x21]))
matrix.write(bytes([0x81]))
matrix.write(bytes([0xEF]))

# les déclarations de pi
pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(G, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)
pi.set_mode(BUZZER, pigpio.OUTPUT)
pi.set_mode(BTN, pigpio.INPUT)
x = AnalogIn(ads, 0)
y = AnalogIn(ads, 1)

# --- CONFIGURATION ---
global NUM_TARGETS
MOVE_SPEED = 0.4
CENTER_VAL = 13250
DEAD_ZONE = 8000
NUM_TARGETS = 10  # Set how many dots you want
buzzer_triggered = False

# Initial for the dot
global dot_x
dot_x = 0.0
global dot_y
dot_y = 7.0
# Function to return color of rgb with r,g,b = 1 or 0
def led_state(r,g,b):
    pi.write(R,r)
    pi.write(G,g)
    pi.write(B,b)

# Function to clear the matrix board
def clearMatrix():
    with matrix as mem:
        mem.write(bytearray([0x00] * 17))
    
    time.sleep(0.5)

# Fonction to calculate the movement of the joystick
def calculate_step(raw_value):
    diff = raw_value - CENTER_VAL
    if abs(diff) < DEAD_ZONE: return 0
    return (diff / 16000) * MOVE_SPEED
    
def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

def reception_msg(cl,userdata,msg):
    print("Reçu:",msg.payload.decode())

def map_display():
    targets = []
    NUM_TARGETS = 10
    for _ in range(NUM_TARGETS):
        targets.append([random.randint(0, 7), random.randint(0, 7)])
        targets = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(NUM_TARGETS)]
        return f"[SERVER] Map ({NUM_TARGETS} dots) : {targets}"
        
def timer():
    timer = 10
    for i in range(timer):
        timer -= 1
        client.publish(TOPIC, f"[SERVER] Timer : {timer}s")
        time.sleep(1)
    client.publish(TOPIC, f"[SERVER] Timer : Game Over!")
# mqtt_client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
# mqtt_client.on_connect = connexion
# mqtt_client.on_message = reception_msg
# mqtt_client.on_publish = publication
# mqtt_client.connect(BROKER, PORT)
 
# threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

game_state = 'Connected'

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    global score
    global game_state
    global buzzer_triggered
    score = 0
    # bleue = en_jeux, jaune = restarting, blanc = connected
    if game_state == "Connected":
        led_state(0,0,0)
    if game_state == "Game Started" and not buzzer_triggered:
        led_state(1,1,0)
        pi.write(BUZZER,1)
        time.sleep(1)
        pi.write(BUZZER,0)

        buzzer_triggered = True
    else:
        led_state(1,1,1)
        pi.write(BUZZER,0)
    return jsonify({'game_state': game_state, 'score': score}),200

@app.route('/api/set_game_state', methods=['POST'])
def set_game_state():
    global led_sequence
    global game_state
    global dot_x
    global dot_y
    global score
    targets = []
    col = 0x00
    row = 0
    if request.method == "POST":
        json = request.get_json()
        if 'game_state' in json and 'difficulty' in json:
            if json['game_state'] == 'start':
                game_state = 'Game Started'
                clearMatrix()
                if json['difficulty'] == 'Easy':
                    NUM_TARGETS = 10
                elif json['difficulty'] == 'Normal':
                    NUM_TARGETS = 7
                elif json['difficulty'] == 'Hard':
                    NUM_TARGETS = 5

                for _ in range(NUM_TARGETS):
                    targets.append([random.randint(0, 7), random.randint(0, 7)])

                # Setup Matrix
                with matrix as mem:
                    mem.write(bytes([0x21])) 
                    mem.write(bytes([0x81])) 
                    mem.write(bytes([0xEF])) 

                try:
                    while game_state == 'Game Started':
                        # 1. Update Player Position
                        dot_x = max(0.0, min(7.0, dot_x + calculate_step(x.value)))
                        dot_y = max(0.0, min(7.0, dot_y + calculate_step(y.value)))
                        px, py = int(round(dot_x)), int(round(dot_y))

                        # 2. COLLISION DETECTION (Capture and Remove)
                        # We loop through a copy of the list [:] so we don't crash while removing items
                        for t in targets[:]: 
                            if px == t[0] and py == t[1]:
                                targets.remove(t) # Remove the dot from existence!
                                score += 1
                                # clien.publish("SCORE", "{score}")
                                print(f"Captured! {len(targets)} dots remaining.") # send to pi B (ex.: "Player01 : Captured! {len(targets)} dots remaining.")

                        # 3. WIN CONDITION
                        if not targets:
                            print("Level Cleared! Spawning new wave...") # send to pi B (ex.: "Player01 : Level Cleared! Spawning new wave...")
                            time.sleep(1)
                            # Re-spawn 10 new dots if you want the game to loop
                            targets = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(NUM_TARGETS)]

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

                        with matrix as mem:
                            mem.write(buffer)

                        time.sleep(0.02)

                except:
                    clearMatrix()
                    pass

            elif json['game_state'] == 'restart':
                game_state = 'Connected'
                clearMatrix()

            elif json['game_state'] == 'end':
                game_state = 'Connected'
                clearMatrix()
            else:
                return jsonify({'Erreur': 'Mauvaise valeur'}),500
        else:
            return jsonify({'Erreur': 'Requete invalide'}),500
    else:
      return jsonify({'Erreur': 'Requetes POST seulement'}),500


    return jsonify({'game_state': game_state, 'led_sequence': targets}),200

# @app.route('/api/set_matrix', methods=['POST'])
# def set_matrix(): # only turns on 1 led in each column
#     led_position = ''
#     led_state = ''
#     # sum = 0
#     if request.method == "POST":
#         json = request.get_json()
#         if game_state == 'Connected':
#             if 'led_position' in json and 'led_state' in json:
#                 led_position = json['led_position'].split('x')
#                 led_state = json['led_state']
#                 values = converter(led_position[0], led_position[1])
#                 if led_state == 'off':
#                     # sum -= values[1]
#                     matrix.write(bytes([values[0], 0]))
#                 elif led_state == 'on':
#                     matrix.write(bytes([values[0], values[1]]))
#                     # sum += values[1]
#                     # matrix.write(bytes([values[0], sum))
#                 else:
#                     return jsonify({'Erreur': 'Mauvaise valeur'}),500
#             else:
#                 return jsonify({'Erreur': 'Requete invalide'}),500
#         else:
#             return jsonify({'Erreur': 'Requete non autoriser, une partie est en jeux'}),500
#     else:
#         return jsonify({'Erreur': 'Requetes POST seulement'}),500

#     return jsonify({'led_position': json['led_position'], 'led_state': json['led_state']}),200


# def converter(col, row):
#     col_byte, row_num = 0x00,0
#     match col:
#         case '0':
#             col_byte = 0x00
#         case '1':
#             col_byte = 0x02
#         case '2':
#             col_byte = 0x04
#         case '3':
#             col_byte = 0x06
#         case '4':
#             col_byte = 0x08
#         case '5':
#             col_byte = 0x0A
#         case '6':
#             col_byte = 0x0C
#         case '7':
#             col_byte = 0x0E
    
#     match row:
#         case '0':
#             row_num = 1
#         case '1':
#             row_num = 2
#         case '2':
#             row_num = 4
#         case '3':
#             row_num = 8
#         case '4':
#             row_num = 16
#         case '5':
#             row_num = 32
#         case '6':
#             row_num = 64
#         case '7':
#             row_num = 128

#     return [col_byte, row_num]

if __name__ == '__main__':
    app.run(host='192.168.17.1', port=5000) # host='192.168.17.1'
