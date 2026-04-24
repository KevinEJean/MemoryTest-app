from flask import Flask, jsonify, request
from flask_cors import CORS
import pigpio
import time
import threading
import socket
import board
import busio
from adafruit_ht16k33 import matrix   

# VARIABLE PIGPIO

pi = pigpio.pi()
i2c = busio.I2C(board.SCL, board.SDA)

R,G,B = 0,0,0
BUZZER = 0
MATRIX = matrix.Matrix8x8(i2c)
BTN = 0
JOYSTICK = 0

pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(G, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)
pi.set_mode(BUZZER, pigpio.OUTPUT)
pi.set_mode(MATRIX, pigpio.OUTPUT)
pi.set_mode(BTN, pigpio.INPUT)
pi.set_mode(JOYSTICK, pigpio.INPUT)



app = Flask(__name__)

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    global score
    global game_state
    game_state = 'Not Connected' # pi.read(RGB) => bleue = en_jeux, jaune = restarting/ending, blanc = connected
    return jsonify({'score': score, 'game_state': game_state}),200

@app.route('/api/set_game_state', methods=['POST'])
def set_game_state():
    global led_sequence
    global game_state
    led_sequence = {}
    # ...
    # if 'start' in json:
        # ...
        # clear matrix
        # allumer la led RGB en bleue
        # if game_state = 'Game Started':
            # randomly add led addresses to led_sequence (ex: {'1': f'{col}x{row}', ..., '64': f'{col}x{row}'})
            # turn on led_sequence['1'], sleep, turn off led_sequence['1'], sleep, ... (ex.: MATRIX[led_sequence['1']])
            # return jsonify(led_sequence),200 # return led_sequence for debuging
    # elif 'restart' in json:
        # ...
        # allumer la led RGB en jaune
        # clear matrix & restart services (clean up)
    # elif 'end' in json:
        # ...
        # allumer la led RGB en jaune
        # clear matrix & end game (clean up)

    return jsonify({'game_state': game_state}),200

@app.route('/api/set_matrix', methods=['POST'])
def set_matrix():
    led_position = '' # 0x0
    # ...
    led_state = pi.read(MATRIX[led_position])
    if game_state == 'Connected':
        if led_state == 0:
            MATRIX[led_position] = 1
            led_state = 'ON'
        else:
            MATRIX[led_position] = 0
            led_state = 'ON'
    else:
        return jsonify({'Erreur': 'Requete non autoriser, une partie est en jeux'})

    return jsonify({'led_position': led_position, 'led_state': led_state}),200

# thread 'confirm_btn()' 
def confirm_btn():
    global score
    global led_sequence
    score = 0
    curled_position = '' # 0x0 # from joystick
    # ...
    if curled_position == led_sequence[score]:
        score += 1
        # allumer la led RGB en vert & allumer buzzer (good)
    else:
        pass # allumer la led RGB en rouge & allumer buzzer (bad) & end the game (clean up)

if __name__ == '__main__':
    app.run(host='192.168.4.1', port=5000)