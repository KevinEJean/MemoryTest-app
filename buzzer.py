import pigpio
import time

BUZZER = 19
pi = pigpio.pi()

pi.set_mode(BUZZER, pigpio.OUTPUT)


pi.write(BUZZER,1)
time.sleep(1)
pi.write(BUZZER,0)