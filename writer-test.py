import fifo
import time

for i in range(5):
    fifo.writer("10,10,10,100,100,100,100")
    time.sleep(1)