import paho.mqtt.client as pmc
import random
import time

BROKER = "10.10.21.144"
PORT = 1883
TOPIC = "meteo"


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

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)

client.connect(BROKER, PORT)

client.publish(TOPIC, map_display())
client.publish(TOPIC, timer())

client.loop_forever()