from random import random
import  time

starttemp1 = 20
starttemp2 = 50

while True:
    temp1 = starttemp1+5*random()
    temp2 = starttemp2+5*random()
    f = open("testdata/sensor1","w+")
    f.write(str(temp1))
    f.close()
    f = open("testdata/sensor2","w+")
    f.write(str(temp2))
    f.close()
    time.sleep(2)