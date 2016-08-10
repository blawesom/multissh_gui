#!/usr/bin/env python

from tkinter import *
import multiexec
## import statplot
import time


def update():
    global hosts_list
    global water_temp
    if len(water_temp) < 2:
        water_temp = [0, 0]
    for host in hosts_list:  ## Affichage des hotes et listing des états
        liste_Label[hosts_list.index(host)]['text'] = str('{}] Host: {}  \tIP: {} \tAvailable: {} \tConnected: {}  \tCPU: {} \tMem: {} \t Temp: {}'\
            .format(hosts_list.index(host) +1 ,host[0],host[1],host[5],host[6],host[7],host[8], host[9]))
    temp_Lab['text'] = str(' IN : {}°C \t OUT: {}°C'.format(water_temp[0],water_temp[1]))

def check():
    global hosts_list
    for host in hosts_list:
        outputPanel.insert(END,'ping '+ host[1] +'...\n')
        outputPanel.yview(END)
        multiexec.ping(host)
    update()

def connect():
    global hosts_list
    global clients_list
    for host in hosts_list:
        if host[5]=='Yes':
            outputPanel.insert(END, '*** Connecting to '+host[0]+'('+host[1]+')...\n')
            clients_list.append(multiexec.connect(host, 22))
            if host[6]== 'Yes':
                outputPanel.insert(END, '*** OK\n')
            else:
                outputPanel.insert(END, '*** Echec\n')
            outputPanel.yview(END)
    update()

def disconnect():
    global hosts_list
    global clients_list
    for host in hosts_list:
        if host[6]=='Yes':
            multiexec.disconnect(clients_list[0], host)
            outputPanel.insert(END, '*** Closing Connection to '+host[0]+'('+host[1]+')...\n')
            clients_list.remove(clients_list[0])
            outputPanel.yview(END)
    update()

def phelp():
    outputPanel.insert(END,'\n-- Listes des commandes spéciales disponibles:\n')
    outputPanel.insert(END,'   check : Vérifie la liste des hotes disponibles\n')
    outputPanel.insert(END,'   connect : Se connecte aux hotes disponibles \n')
    outputPanel.insert(END,'   disconnect : Ferme les connexions actives\n')
    outputPanel.yview(END)

def checkhw():
    global hosts_list
    global clients_list
    global water_temp
    j=0
    for host in hosts_list:
        if host[6]=='Yes':
            multiexec.gethwr(host, clients_list[j], water_temp)
            outputPanel.insert(END, host[2]+'@'+host[0]+'('+host[1]+'): '+host[7]+' CPU used - '+host[8]+' RAM used - CPU Temp: '+host[9]+'\n')
            outputPanel.yview(END)
            j += 1
    update()

def set_power():
    global hosts_list
    global clients_list
    j=0
    for host in hosts_list:
        if host[6]=='Yes':
            if host[0]=='RasPi':
                multiexec.switch_power(host, clients_list[j])
                outputPanel.insert(END, 'New PSU state in progress...\n')
                outputPanel.yview(END)
            j+=1
    update()

def plotnew():
    global hosts_list
    global clients_list
    ## statplot.statplot(hosts_list, clients_list)
    
def exect(*args):
    global hosts_list
    global clients_list
    j=0
    if cmd_t.get() != '':
        for host in hosts_list:
            if host[6]=='Yes':
                outline = multiexec.term_exec(cmd_t.get(), host, clients_list[j])
                j += 1
                outputPanel.insert(END, host[2]+'@'+host[0]+'('+host[1]+') >> '+ cmd_t.get()+'\n')
                if outline is not None:
                    for line in outline:
                        outputPanel.insert(END, '  ' + str(line[:-1]) + '\n')
                        outputPanel.yview(END)
                outputPanel.insert(END, '--------------------------------\n')
                outputPanel.yview(END)
    else:
        outputPanel.insert(END, '*** Entrez une commande valide ***\n')
    cmd_t.set('')

hosts_list = [] ## hotes potentiels
clients_list = [] ## connexions ouvertes
liste_Label = []
water_temp = []

hosts_list = multiexec.gethost() ## infos de connexions

fenetre = Tk()
fenetre.resizable(0,0)
fenetre.title('deFAB monitoring tool')

## Framing
frame_list = Frame(fenetre, width = 100)
temp_list = Frame(fenetre, width = 100)
button_frame = Frame(fenetre, width = 100)
cmd_frame=Frame(fenetre, width = 100)
txt_frame= Frame(fenetre, width=100, height=80)

## Labels
for host in hosts_list:  ## Affichage des hotes et listing des états
    liste_Label.append(Label(frame_list, text=''))
temp_Lab = Label(temp_list, text = '', font = "Arial 30 bold")
update()

## Output
scrollbar = Scrollbar(txt_frame)
outputPanel = Text(txt_frame, wrap='word', yscrollcommand = scrollbar.set,  height=25, width=80)

## Ligne de commande
newLab = Label(cmd_frame, text='Commande:')
cmd_t = StringVar()
ligne_cmd = Entry(cmd_frame, textvariable=cmd_t, width=40)

## Boutons
bouton_help = Button(button_frame, text="Help",command=phelp)
bouton_disconnect = Button(button_frame, text="Disconnect",command=disconnect)
bouton_connect = Button(button_frame, text="Connect", command=connect)
bouton_stathw = Button(button_frame, text="HW Stat", command=checkhw)
bouton_check = Button(button_frame, text="Check",command=check)
bouton_ok = Button(cmd_frame, text="OK", command=exect)
fenetre.bind("<Return>", exect)

bouton_pwr = Button(frame_list, text="PWR", command=set_power)

## Frame grid
frame_list.grid(row=0, pady=10)
temp_list.grid(row=1, pady=10)
button_frame.grid(row=2, sticky = 'e')
cmd_frame.grid(row=2, sticky = 'w')
txt_frame.grid(row=3, padx=5, pady=10)

## Gridding
for label in liste_Label:
    i=liste_Label.index(label)
    label.grid(row=i, sticky='w', padx=5, pady=5)
rowN = len(liste_Label)    
bouton_pwr.grid(row=0, column = 1, rowspan=rowN, sticky='nsew', padx=10, pady=20)

temp_Lab.grid(row=0)

bouton_check.grid(row=0, column = 0, padx=3)
bouton_connect.grid(row=0, column = 1, padx=3)
bouton_stathw.grid(row=0, column = 2, padx=4)
bouton_disconnect.grid(row=0, column = 3, padx=3)
bouton_help.grid(row=0, column = 4, padx=3)

newLab.grid(row=0, column=0, padx=5, pady=5)
ligne_cmd.grid(row=0, column=1)
bouton_ok.grid(row=0, column=2, padx=5, pady=5)

outputPanel.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
scrollbar.grid(row=0, column=1, sticky='nsew')

fenetre.mainloop()
    
