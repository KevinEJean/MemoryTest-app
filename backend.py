from flask import Flask, jsonify, request
from flask_cors import CORS
import pigpio
import time
import threading
import socket
import board
import busio
import adafruit_bus_device.i2c_device as i2c_device

# VARIABLE PIGPIO

pi = pigpio.pi()

R,G,B = 21,20,16
BUZZER = 19
# ads = ADS1115(i2c)
BTN = 19

i2cBus = busio.I2C(board.SCL, board.SDA)
matrix = i2c_device.I2CDevice(i2cBus, 0x70)
matrix.write(bytes([0x21])) # Initialiser l'oscillateur du contrôleur
matrix.write(bytes([0x81])) # Initialiser la matrice de LED 
matrix.write(bytes([0xEF])) # Initialiser la luminosité

pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(G, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)
pi.set_mode(BUZZER, pigpio.OUTPUT)
pi.set_mode(BTN, pigpio.INPUT)
# x = AnalogIn(ads, 0)
# y = AnalogIn(ads, 1) 

def led_state(r,g,b):
    pi.write(R,r)
    pi.write(G,g)
    pi.write(B,b)

app = Flask(__name__)
CORS(app)

game_state = 'Connected'

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    global score
    global game_state
    score = 0
    # bleue = en_jeux, jaune = restarting/ending, blanc = connected
    if game_state == "Connected":
        led_state(0,0,0)
    if game_state == "Game Started":
        pi.write(BUZZER,1)
        time.sleep(1)
        pi.write(BUZZER,0)
        led_state(1,1,0)
    else:
        led_state(1,1,1)
        pi.write(BUZZER,0)
    return jsonify({'game_state': game_state, 'score': score}),200

@app.route('/api/set_game_state', methods=['POST'])
def set_game_state():
    global led_sequence
    global game_state
    led_sequence = {}
    if request.method == "POST":
        json = request.get_json()
        if 'game_state' in json and 'difficulty' in json:
            if json['game_state'] == 'start':
                game_state = 'Game Started'
                # clear matrix
                # allumer la led RGB en bleue
                # if game_state = 'Game Started':
                    # randomly add led addresses to led_sequence (ex: {'1': f'{col}x{row}', ..., '64': f'{col}x{row}'})
                    # turn on led_sequence['1'], sleep, turn off led_sequence['1'], sleep, ... (ex.: MATRIX[led_sequence['1']])
                    # return jsonify(led_sequence),200 # return led_sequence for debuging
                pass
            elif json['game_state'] == 'restart':
                game_state = 'Connected'
                # allumer la led RGB en jaune
                # clear matrix & restart services (clean up)
                pass
            elif json['game_state'] == 'end':
                game_state = 'Connected'
                # allumer la led RGB en jaune
                # clear matrix & end game (clean up)
                pass
            else:
                return jsonify({'Erreur': 'Mauvaise valeur'}),500
        else:
            return jsonify({'Erreur': 'Requete invalide'}),500
    else:
      return jsonify({'Erreur': 'Requetes POST seulement'}),500


    return jsonify({'game_state': game_state}),200

@app.route('/api/set_matrix', methods=['POST'])
def set_matrix(): # only turns on 1 led in each column
    led_position = ''
    led_state = ''
    # sum = 0
    if request.method == "POST":
        json = request.get_json()
        if game_state == 'Connected':
            if 'led_position' in json and 'led_state' in json:
                led_position = json['led_position'].split('x')
                led_state = json['led_state']
                values = converter(led_position[0], led_position[1])
                if led_state == 'off':
                    # sum -= values[1]
                    matrix.write(bytes([values[0], 0]))
                elif led_state == 'on':
                    matrix.write(bytes([values[0], values[1]]))
                    # sum += values[1]
                    # matrix.write(bytes([values[0], sum))
                else:
                    return jsonify({'Erreur': 'Mauvaise valeur'}),500
            else:
                return jsonify({'Erreur': 'Requete invalide'}),500
        else:
            return jsonify({'Erreur': 'Requete non autoriser, une partie est en jeux'}),500
    else:
        return jsonify({'Erreur': 'Requetes POST seulement'}),500

    return jsonify({'led_position': json['led_position'], 'led_state': json['led_state']}),200

def converter(col, row):
    col_byte, row_num = 0x00,0
    match col:
        case '0':
            col_byte = 0x00
        case '1':
            col_byte = 0x02
        case '2':
            col_byte = 0x04
        case '3':
            col_byte = 0x06
        case '4':
            col_byte = 0x08
        case '5':
            col_byte = 0x0A
        case '6':
            col_byte = 0x0C
        case '7':
            col_byte = 0x0E
    
    match row:
        case '0':
            row_num = 1
        case '1':
            row_num = 2
        case '2':
            row_num = 4
        case '3':
            row_num = 8
        case '4':
            row_num = 16
        case '5':
            row_num = 32
        case '6':
            row_num = 64
        case '7':
            row_num = 128

    return [col_byte, row_num]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # host='192.168.17.1'
