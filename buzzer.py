import pigpio
import time

BUZZER = 19
pi = pigpio.pi()
R,G,B = 21,20,16
pi.set_mode(BUZZER, pigpio.OUTPUT)
pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(G, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)

def led_state(r,g,b):
    pi.write(R,r)
    pi.write(G,g)
    pi.write(B,b)


pi.write(BUZZER,1)
time.sleep(1)
pi.write(BUZZER,0)


led_state(1,1,0)

