# -*- coding: utf-8 -*-
import sys
import serial
import numpy

def main(*args):
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    with open('temp.txt', 'r') as datatemp:
        listemp = datatemp.read()
        listetemp = listemp.split('\n')
        temp_list=[]
        for line in listetemp:
            temp_list.append(line.split(';'))
               
    temp=[]
    resist=[]
    for item, value in temp_list:
        temp.append(float(item))
        resist.append(float(value))
    resist.reverse()
    temp.reverse()
    check = False
    while check != True:
        try:
            rin = float(ser.readline())
            R0  = rin*9.78/(4.8-rin)
            rout = float(ser.readline())
            R1  = rout*9.78/(4.8-rout)
            check = True
        except:
            check = False
    T0 = numpy.interp(R0, resist, temp)
    T1 = numpy.interp(R1, resist, temp)
    sys.stdout.flush()
    sys.stdout.write(str(T0)[:5]+';'+str(T1)[:5])

if __name__ == "__main__":
    main()
