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
import json as json_player
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
Broker = "10.10.21.144"
GAME_TOPIC = "map"
PORT = 1883

# Donne des joueurs
player1_data = {
    "player1_scores" : None,
    # "isReady" : False
}
player2_data = {
    "player2_scores" : None,
    # "isReady" : False
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

global game_timer
game_timer = 15

# --- CONFIGURATION ---
global NUM_TARGETS
MOVE_SPEED = 0.4
CENTER_VAL = 13250
DEAD_ZONE = 8000
NUM_TARGETS = 10  # Set how many dots you want
buzzer_triggered = False

# list for the map
global targets
targets = []

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
        mqtt_client.subscribe("map")
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

def reception_msg(cl,userdata,msg):
    message = msg.payload.decode()

    if "player1_score" in message:
        player1_score = message.split(":").pop().replace("}", "")
        player1_data['player1_scores'] = player1_score

    elif "player2_score" in message:
        player2_score = message.split(":").pop().replace("}", "")
        player2_data['player2_scores'] = player2_score
        print(player2_score)
        

    # elif "player1 is ready" in message:
    #     player1_data['isReady'] = True

    # elif "player2 is ready" in message:
    #     player2_data['isReady'] = True

    # if player1_data['isReady'] and player2_data['isReady']:
    #     game_state = 'Game Started'

    # elif "Game Over" in message:
    #     game_state = "Connected"

    else:
        print("Reçu:", message)

def map_display(num_targets):
    global targets
    targets = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(num_targets)]
    targets1 = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(num_targets)]
    targets2 = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(num_targets)]

    payload = {
        "type": "MAP_DATA",
        "targets": targets,
        "targets1": targets1,
        "targets2": targets2,
    }
    return json_player.dumps(payload)
        
def timer():
    global game_state
    global game_timer
    game_timer = 15
    for i in range(game_timer):
        game_timer -= 1
        mqtt_client.publish(GAME_TOPIC, f"[SERVER] Timer : {game_timer}s")
        time.sleep(1)
    game_state = "Connected"
    clearMatrix()
    mqtt_client.publish(GAME_TOPIC, f"[SERVER] Timer : Game Over!")

mqtt_client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = connexion
mqtt_client.on_message = reception_msg
mqtt_client.connect(Broker, PORT)
 
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

game_state = 'Connected'

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    global score
    global game_state
    global buzzer_triggered
    global player2_score
    global game_timer
    mqtt_client.on_message = reception_msg
    player1_score = player1_data['player1_scores']
    player2_score = player2_data['player2_scores']
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
    # return jsonify({'game_state': game_state, 'player1_score': player1_score, 'player2_score': player2_score, 'timer': game_timer}),200
    return jsonify({'game_state': game_state, 'player1_score': player1_score, 'player2_score': player2_score}),200

@app.route('/api/set_game_state', methods=['POST'])
def set_game_state():
    global game_state
    global dot_x
    global dot_y
    global score
    global targets
    scores = 0
    rounds = 0
    if request.method == "POST":
        json = request.get_json()
        if 'game_state' in json and 'difficulty' in json:
            # if json['game_state'] == 'start' and player1_data['isReady'] == True and player2_data['isReady'] == True:
            if json['game_state'] == 'start':
                game_state = 'Game Started'
                clearMatrix()
                if json['difficulty'] == 'Easy':
                    NUM_TARGETS = 5
                elif json['difficulty'] == 'Normal':
                    NUM_TARGETS = 7
                elif json['difficulty'] == 'Hard':
                    NUM_TARGETS = 10

                mqtt_client.publish(GAME_TOPIC, map_display(NUM_TARGETS))

                # Setup Matrix
                with matrix as mem:
                    mem.write(bytes([0x21])) 
                    mem.write(bytes([0x81])) 
                    mem.write(bytes([0xEF])) 

 
                    # timer_thread = threading.Thread(target=timer, daemon=True).start()
                    try:
                        mqtt_client.connect(Broker, PORT)             
                            # 3. WIN CONDITION
                        if not targets:
                                print("Level Cleared! Spawning new wave...")
                                time.sleep(1)
                                rounds += 1
                                # Re-spawn 10 new dots if you want the game to loop
                                # targets = [[random.randint(0, 7), random.randint(0, 7)] for _ in range(10)]
                                mqtt_client.publish(GAME_TOPIC, map_display(NUM_TARGETS))

                                print(f"Rounds : {rounds}")
                                if rounds == 3:
                                    print("Fin du programme")
                                    player1_data["player1_scores"] = scores # pi@rasp11 would be player2_scores ?
                                    json_payload = str(player1_data)
                                    mqtt_client.publish(GAME_TOPIC, json_payload)
                                    with matrix as mem:
                                        mem.write(bytearray([0x00] * 17))
                                    # stop timer
                                    game_state = "Connected"
                              

                            # # 4. RENDER
                            # buffer = bytearray([0] * 17)
                            # buffer[0] = 0x00
                            
                            # # Draw remaining targets
                            # for t in targets:
                            #     row_idx = (t[1] * 2) + 1
                            #     buffer[row_idx] |= (1 << t[0])
                                
                            # # Draw player
                            # player_row_idx = (py * 2) + 1
                            # buffer[player_row_idx] |= (1 << px)

                            # with matrix as mem:
                            #     mem.write(buffer)

                        time.sleep(0.02)

                    except KeyboardInterrupt:
                        # timer_thread.join()
                        clearMatrix()
                        game_state = "Connected"

            # elif json['game_state'] == 'player1_ready':
            #     mqtt_client.publish(GAME_TOPIC, "player1 is ready")
            
            # elif json['game_state'] == 'player2_ready':
            #     mqtt_client.publish(GAME_TOPIC, "player2 is ready")

            elif json['game_state'] == 'restart' or json['game_state'] == 'end':
                # timer_thread.join()
                end_payload = {
                    "type" : "GAME_STATE",
                    "game_state" : "end"
                }
                json_player.dumps(end_payload)
                game_state = 'Connected'
                clearMatrix()

            else:
                return jsonify({'Erreur': 'Mauvaise valeur'}),500
        else:
            return jsonify({'Erreur': 'Requete invalide'}),500
    else:
      return jsonify({'Erreur': 'Requetes POST seulement'}),500

    # print(player1_data['isReady'], player2_data['isReady'])
    return jsonify({'game_state': game_state}),200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # host='192.168.17.1'
