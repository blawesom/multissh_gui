#!/usr/bin/env python

import  os, socket, sys, time, base64, getpass, traceback, subprocess, re
from paramiko.py3compat import input
import paramiko

if sys.platform == 'win32':
    print('- Running on Windows -')
    time.strftime('%A %d %B %Y %H:%M:%S')
if sys.platform == 'linux':
    print('- Running on Linux -')
    
# Connect and use paramiko Client to negotiate SSH2 across the connection
# and exec a terminal command !! ALL PARAMETER ARE STRINGS !! *except port

def gethost():
    hosts_list = []
    with open('hosts.csv', 'r') as file:
        hosts = file.read()
        liste = hosts.split('\n')
        for line in liste:
            if '#' not in line and line is not '':
                hosts_list.append(line.split(';'))
        for host in hosts_list:
            host.append('No')
            host.append('No')
            host.append('N/A')
            host.append('N/A')
            host.append('N/A')
    return hosts_list


def ping(host):
    pingok = 1
    if sys.platform == 'win32':
        cmd = 'ping -n 1 ' + host[1]
    if sys.platform == 'linux':
        cmd = 'ping ' + host[1]
    ##else:
    ##    cmd = 'ping -c 1 ' + host[1]
        
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait() 
    ##print("Command output : {}".format(output))
    status_rep = str(output)
    if 'unreachable' in status_rep:
        pingok = 0
    if 'Unreachable' in status_rep:
        pingok = 0
    if pingok:
        host[5] = 'Yes'


def connect(host, port):
    try:
        client = paramiko.SSHClient()
        hostname, ip, username, password = host[0:4]
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(ip, port, username, password)
        host[6] = 'Yes'
        return client
    except Exception as e:
        print('*** Caught exception: {}:{}'.format(e.__class__, e))
        

def disconnect(client, host):
    try:
        client.close()
        host[6] = 'No'
        host[7] = 'N/A'
        host[8] = 'N/A'
        host[9] = 'N/A'
    except:
        print(' {}@{}({}) >> Error_WTF'.format(host[2], host[0], host[1], command))
        client.close()


def term_exec(command, host, client):
    try:
        stdin, stdout, stderr = client.exec_command(command)
        if command == 'su' or command[0:3] == 'sudo':
            stdin.write(host[5])
            stdin.flush()
        for line in stderr:
            print(line)
        return stdout
    except:
        print(' {}@{}({}) >> Error_WTF'.format(host[2], host[0], host[1], command))

def switch_power(host, client):
    client.exec_command('python set_power.py')


def gethwr(host, client, water_temp):
    try:
        ## CPU infos
        stdin, stdout, stderr = client.exec_command('mpstat') ##  -P ALL pour avoir les infos par core
        cpustat = stdout
        l = 0
        cpu_stat = []
        for line in cpustat:
            if l == 3:
                cpu_stat = line.split('   ')
            l += 1
        host[7] = str('{0:.2f}%'.format(100-float(cpu_stat[-1])))
        
        ## Memory infos
        stdin, stdout, stderr = client.exec_command('free')
        memstat = stdout
        k=0
        mem_stat=[]
        for line in memstat:
            if k == 1:
                mem_stat = line.split('   ')
            k += 1
        host[8] = str('{0:.2f}%'.format(float(mem_stat[3]) / float(mem_stat[2]) * 100))

        ## Temp infos
        if host[0] != 'RasPi':
            stdin, stdout, stderr = client.exec_command('sensors')
            tempstat = stdout
            m=0
            regexp = re.compile("^([.]?[0-9]{2,3}){2}°C$")
            temp_stat=[]
            for line in tempstat:
                if m == 7:
                    temp_stat = line.split('  ')
                m += 1
            host[9] = temp_stat[1]

        ## Lecture data
        if host[0] == 'RasPi':
            stdin, stdout, stderr = client.exec_command('python get_temp.py')
            temp_eau = stdout
            temperatures = []
            for line in temp_eau:
                if ';' in line:
                    temperatures = line.split(';')
            ## modif truquée
            water_temp[0] = float(temperatures[0])
            water_temp[1] = float(temperatures[1])
            if water_temp[1] < water_temp[0]:
                water_temp.reverse()
    except:
        print(' {}@{}({}) >> Error'.format(host[2], host[0], host[1]))
