# -*- coding: utf-8 -*-
import pifacedigitalio
import time

def main(*args):
    power = int()
    ## Cycle de démarrage de PC
    try:
        with open('state.txt','r') as state:
            power = int(state.read())
    except:
        print 'ERREUR STATE READ'
        
    if power == 0:
        pifacedigitalio.init()
        pifacedigitalio.digital_write(1,1)
        time.sleep(0.3)
        pifacedigitalio.digital_write(0,1)
        time.sleep(0.2)
        pifacedigitalio.digital_write(1,0)
        with open ('state.txt','w') as state:
            state.write('1')
    if power == 1:
        pifacedigitalio.init()
        with open ('state.txt','w') as state:
            state.write('0')       

if __name__ == "__main__":
    main()
