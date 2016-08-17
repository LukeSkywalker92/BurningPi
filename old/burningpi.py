# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO

from thread import start_new_thread

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.animation as animation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import pylab
from pylab import *
from matplotlib.figure import Figure

import sys
if sys.version_info[0] < 3:
    import Tkinter as Tk
    import ttk
else:
    import tkinter as Tk

import tkFont

'''
Thermometer Importe
'''

from subprocess import Popen, PIPE, call
import re
import numpy

'''
#Style
s=ttk.Style()
print(s.theme_names())
'''

#Hauptfenster root Erstellen
root = Tk.Tk()
root.wm_title("BurningPi")
root.geometry("1920x1080")




####################################################################################################################
'''
Variablen
'''
####################################################################################################################


#Sampling Rate
sample_time = Tk.IntVar()                               #Eingestellte Sampling-Zeit
sample_time.set(5)
sample_time_string=Tk.StringVar()

#Temperaturen Oel
t_oil_soll = Tk.IntVar()                                #Geziehlte Oel-Temperatur
t_oil_ist = Tk.IntVar()                                 #Aktuelle Oel-Temperatur
t_oil_ist_string = Tk.StringVar()
t_oil_delta_heating = Tk.IntVar()                       #Delta T beim Heizen
t_oil_delta_cooling = Tk.IntVar()                       #Delta T beim Kuehlen

#Temperaturen Kuehlwasser
t_water_max = Tk.IntVar()                               #Maximale Kuehlwassertemperatur
t_water_max_string = Tk.StringVar()
t_water_ist = Tk.IntVar()                               #Aktuelle Kuehlwassertemperatur
t_water_ist_string = Tk.StringVar()

#Status der Geraete (True = an, False = aus)
heat_auto = False                                       #Heizautomatik
heat_auto_string = Tk.StringVar()
heat_auto_string.set("Aus")
heating = False                                         #Heizstatus
pump = False                                            #Status der Pumpe
pump_string = Tk.StringVar()
pump_string.set("Aus")

#Startzeit
start_time = time.time()

#Listen fuer Temperatur und Zeit
times=[]
temps_oil=[]
temps_water=[]
temps_oil_soll=[]

#Sensorpfade
sensor_oil = "/sys/bus/w1/devices/28-02155377b2ff/w1_slave"
sensor_water = "/sys/bus/w1/devices/28-02155377b2ff/w1_slave"

#GPIO

########################################################################################################################
'''
Funktionen
'''
########################################################################################################################


'''
Funktionen zum einstellen der Variablen
'''

#Sampling-Zeit einstellen
def set_sample_time(self):
    sample_time.set(int(round(sample_control_scale.get())))
    #print(sample_time.get())

#Geziehlte Oel-Temperatur einstellen
def set_t_oil_soll(self):
    t_oil_soll.set(int(round(oil_soll_scale.get())))

#Delta T beim Heizen einstellen
def set_t_oil_delta_heating(scale):
    t_oil_delta_heating.set(int(round(oil_delta_heating_scale.get())))

#Delta T beim Kuehlen einstellen
def set_t_oil_delta_cooling(scale):
    t_oil_delta_cooling.set(int(round(oil_delta_cooling_scale.get())))

#Maximale Kuehlwassertemperatur einstellen
def set_t_water_max(scale):
    t_water_max.set(int(round(water_max_scale.get())))

#Pumpe an&ausschalten
def change_pump_status():
    global pump
    if pump:
        pump = False
        pump_string.set("Aus")
    else:
        pump = True
        pump_string.set("An")
    #print(pump)

#Heizen an&ausschalten
def change_heating_status():
    global heating
    if heating:
        heating = False
    else:
        heating = True
    #print(heating)

#Heizautomatik an&aus
def change_heat_auto_status():
    global heat_auto
    if heat_auto:
        heat_auto = False
        heat_auto_string.set("Aus")
    else:
        heat_auto = True
        heat_auto_string.set("An")
    #print(heat_auto)

'''
Funktionen zur Kontrolle
'''
#Erste Temperaturmessung
def tempdata1(sensor):
    pipe=Popen(["cat", sensor], stdout=PIPE)
    result=pipe.communicate()[0]
    result_list=result.split("=")
    temp_mC=int(result_list[-1])/1000
    if (re.match(".*YES.*", result)):
        #print(abs(temp_mC-t_oil_ist.get()))
        return temp_mC
    else:
        print(result)
        print("invalid result")
        return tempdata1(sensor)

t_oil_ist.set(tempdata1(sensor_oil))
t_oil_ist_string.set(str(t_oil_ist.get())+" °C")
t_water_ist.set(tempdata1(sensor_water))
t_water_ist_string.set(str(t_water_ist.get())+" °C")

#Temperatursensor auslesen
def tempdata(sensor):
    pipe=Popen(["cat", sensor], stdout=PIPE)
    result=pipe.communicate()[0]
    result_list=result.split("=")
    temp_mC=int(result_list[-1])/1000
    if (re.match(".*YES.*", result)) and (abs(temp_mC-t_oil_ist.get())<15):
        #print(abs(temp_mC-t_oil_ist.get()))
        return temp_mC
    else:
        print(result)
        print("invalid result")
        return tempdata(sensor)

#Temperaturkontrolle Oel
def check_oil_temp(temp):
    #print("checking...")
    if heating:
        if temp > (t_oil_soll.get() - t_oil_delta_heating.get()):
            change_heating_status()
    else:
        if temp < (t_oil_soll.get() - t_oil_delta_cooling.get()):
            change_heating_status()


'''
Hauptfunktion
'''

def main_thread(a):
    while True:
        b=a*a
        temp_oil = int(round(tempdata(sensor_oil)))             #Oeltemperatur auslesen
        t_oil_ist.set(temp_oil)                                 #T in variable schreiben
        t_oil_ist_string.set(str(t_oil_ist.get())+" °C")
        temp_water = int(round(tempdata(sensor_water)))         #Wassertemperatur auslesen
        t_water_ist.set(temp_water)                             #T in variable schreiben
        t_water_ist_string.set(str(t_water_ist.get())+" °C")
        times.append(int(round(time.time()-start_time)))        #Zeit in Plot-Array schreiben
        temps_oil.append(temp_oil)                              #T Oel in Plot-Array schreiben
        temps_oil_soll.append(int(round(t_oil_soll.get())))     #T Soll in Plot-Array schreiben
        temps_water.append(temp_water)                          #T Wasser in Plot-Array schreiben
        if heat_auto:                                           #Wenn Heizautomatik an
            check_oil_temp(temp_oil)                            #T Oel checken
        #check_water_temp(temp_water)                           #T Wasser checken
        #print(temps_water)
        #print(temps_oil)                                        
        #print(times)
        
        time.sleep(sample_time.get())                           #Pausieren bis zur nächsten Messung


###########################################################################################################
'''
GUI-Design
'''
###########################################################################################################

'''
Main - Frames
1
2
3
4
'''
main_frame1=ttk.Frame(root, height=200, width=1000, borderwidth=0, relief='groove')
main_frame1.pack()

main_frame2=ttk.Frame(root, height=200, width=1000, borderwidth=0, relief='groove')
main_frame2.pack()

main_frame3=ttk.Frame(root, height=200, width=1000, borderwidth=0, relief='groove')
main_frame3.pack()

main_frame4=ttk.Frame(root, height=200, width=1000, borderwidth=0, relief='groove')
main_frame4.pack()

'''
Titel
'''

title = ttk.Label(main_frame1, font=' -size 70', text="B u r n i n g    P i")
title.pack()


'''
Horizontale Frames (hz_frame)
21 22
31 32
41 42
'''
hz_frame21=ttk.Frame(main_frame2, height=200, width=500 , borderwidth=0, relief='groove')       #An/Aus Schalter
hz_frame21.pack(side=Tk.LEFT)

hz_frame22=ttk.LabelFrame(main_frame2, height=200, width=500 , borderwidth=0, relief='groove', text="Wassertemperatur")       #Oel-Kurve
hz_frame22.pack(side=Tk.RIGHT)

hz_frame31=ttk.Frame(main_frame3, height=200, width=500 , borderwidth=0, relief='groove')       #Regler
hz_frame31.pack(side=Tk.LEFT)

hz_frame32=ttk.LabelFrame(main_frame3, height=200, width=500 , borderwidth=0, relief='groove', text="Oeltemperatur")       #Kuehlwasserkurve
hz_frame32.pack(side=Tk.RIGHT)

hz_frame41=ttk.Frame(main_frame4, height=200, width=500 , borderwidth=0, relief='groove')       #Oel-Temperatur
hz_frame41.pack(side=Tk.LEFT)

hz_frame42=ttk.Frame(main_frame4, height=200, width=500 , borderwidth=0, relief='groove')       #Kuehlwassertemperatur
hz_frame42.pack(side=Tk.RIGHT)

'''
An/Aus-Schalter
'''
#Titel
status_label=ttk.Label(hz_frame21, font=' -size 30', text="Steuerung", width = 20, anchor='center')
status_label.pack(pady = 5)

#Heizen
heating_status_frame=ttk.Frame(hz_frame21, height=100, width=500 )
heating_status_frame.pack()

heating_status_label=ttk.Label(heating_status_frame, font =' -size 30', text="Heizen")
heating_status_label.pack(side=Tk.LEFT, padx = 20)

heating_status_button=ttk.Button(heating_status_frame, textvariable=heat_auto_string, command=change_heat_auto_status)
heating_status_button.pack(side=Tk.LEFT)

#Kuehlwasser
pump_status_frame=ttk.Frame(hz_frame21, height=100, width=500)
pump_status_frame.pack()

pump_status_label=ttk.Label(pump_status_frame, font=' -size 30', text="Pumpe")
pump_status_label.pack(side=Tk.LEFT, padx = 20)

pump_status_button=ttk.Button(pump_status_frame, textvariable=pump_string, command=change_pump_status)
pump_status_button.pack(side=Tk.LEFT)


'''
Parameter
'''

#Sampling Zeit
sample_param_frame=ttk.Frame(hz_frame31, height=100, width=500, borderwidth=0, relief='groove')
sample_param_frame.pack()

sample_param_label=ttk.Label(sample_param_frame, font=' -size 30', text="Sampling Zeit", width = 20, anchor='center')
sample_param_label.pack(pady = 20)

sample_control_frame=ttk.Frame(sample_param_frame)
sample_control_frame.pack()

sample_control_label=ttk.Label(sample_control_frame, text = "Sampling Zeit in s", width = 20)
sample_control_label.pack(side=Tk.LEFT, padx=10)
   
sample_control_scale=ttk.Scale(sample_control_frame, from_=1, to=10, command=set_sample_time)
sample_control_scale.pack(side=Tk.LEFT, padx=10)
sample_control_scale.set(sample_time.get())

sample_value_label=ttk.Label(sample_control_frame, textvariable=sample_time, width = 20)
sample_value_label.pack(side=Tk.LEFT, padx=10)


#Oel Temperaturen
oil_param_frame=ttk.Frame(hz_frame31, height=100, width=500, borderwidth=0, relief='groove')
oil_param_frame.pack()

oil_param_label=ttk.Label(oil_param_frame, font=' -size 30', text="Oel", width = 20, anchor='center')
oil_param_label.pack(pady = 20)

#Soll Temperatur
oil_soll_frame=ttk.Frame(oil_param_frame)
oil_soll_frame.pack()

oil_soll_label=ttk.Label(oil_soll_frame, text = "Solltemperatur in °C", width = 20)
oil_soll_label.pack(side=Tk.LEFT, padx=10)
   
oil_soll_scale=ttk.Scale(oil_soll_frame, from_=1, to=125, command=set_t_oil_soll)
oil_soll_scale.pack(side=Tk.LEFT, padx=10)
oil_soll_scale.set(30)

oil_soll_value_label=ttk.Label(oil_soll_frame, textvariable=t_oil_soll, width = 20)
oil_soll_value_label.pack(side=Tk.LEFT, padx=10)

#Delta Heizen
oil_delta_heating_frame=ttk.Frame(oil_param_frame)
oil_delta_heating_frame.pack()

oil_delta_heating_label=ttk.Label(oil_delta_heating_frame, text = "Delta T Heizen in °C", width = 20)
oil_delta_heating_label.pack(side=Tk.LEFT, padx=10)
   
oil_delta_heating_scale=ttk.Scale(oil_delta_heating_frame, from_=1, to=30, command=set_t_oil_delta_heating)
oil_delta_heating_scale.pack(side=Tk.LEFT, padx=10)
oil_delta_heating_scale.set(5)

oil_delta_heating_value_label=ttk.Label(oil_delta_heating_frame, textvariable=t_oil_delta_heating, width = 20)
oil_delta_heating_value_label.pack(side=Tk.LEFT, padx=10)

#Delta Kuehlen
oil_delta_cooling_frame=ttk.Frame(oil_param_frame)
oil_delta_cooling_frame.pack()

oil_delta_cooling_label=ttk.Label(oil_delta_cooling_frame, text = "Delta T Kuehlen in °C", width = 20)
oil_delta_cooling_label.pack(side=Tk.LEFT, padx=10)
   
oil_delta_cooling_scale=ttk.Scale(oil_delta_cooling_frame, from_=1, to=30, command=set_t_oil_delta_cooling)
oil_delta_cooling_scale.pack(side=Tk.LEFT, padx=10)
oil_delta_cooling_scale.set(5)

oil_delta_cooling_value_label=ttk.Label(oil_delta_cooling_frame, textvariable=t_oil_delta_cooling, width = 20)
oil_delta_cooling_value_label.pack(side=Tk.LEFT, padx=10)



#Wasser Temperaturen
water_param_frame=ttk.Frame(hz_frame31, height=100, width=500, borderwidth=0, relief='groove')
water_param_frame.pack()

water_param_label=ttk.Label(water_param_frame, font=' -size 30', text="Wassertemperatur", width = 20, anchor='center')
water_param_label.pack(pady = 20)

#Soll Temperatur
water_max_frame=ttk.Frame(water_param_frame)
water_max_frame.pack()

water_max_label=ttk.Label(water_max_frame, text = "Maximaltenperatur in °C", width = 20)
water_max_label.pack(side=Tk.LEFT, padx=10)
   
water_max_scale=ttk.Scale(water_max_frame, from_=1, to=30, command=set_t_water_max)
water_max_scale.pack(side=Tk.LEFT, padx=10)
water_max_scale.set(30)

water_max_value_label=ttk.Label(water_max_frame, textvariable=t_water_max, width = 20)
water_max_value_label.pack(side=Tk.LEFT, padx=10)


'''
Temperatur Anzeigen
'''

oil_temp_title_label=ttk.Label(hz_frame41, font=' -size 30', text="Oeltemperatur", width = 20, anchor='center')
oil_temp_title_label.pack(pady = 5)

oil_temp_label=ttk.Label(hz_frame41, font=' -size 40', textvariable=t_oil_ist_string)
oil_temp_label.pack(pady = 5)

water_temp_title_label=ttk.Label(hz_frame42, font=' -size 30', text="Wassertemperatur", width = 20, anchor='center')
water_temp_title_label.pack(pady = 5)

water_temp_label=ttk.Label(hz_frame42, font=' -size 40', textvariable=t_water_ist_string)
water_temp_label.pack(pady = 5)

####################################################################################################################
'''
Plot
'''
####################################################################################################################

#Oel
fig=Figure(figsize=(10,4), dpi=100)
ax=fig.add_subplot(111)
ax.axis([0,1000,10,40])
ax.set_title("Oeltemperatur")


def animate_oil(i):
    try:
        ax.clear()
        ax.plot(times, temps_oil)
        ax.plot(times, temps_oil_soll)
    except:
        pass

canvas = FigureCanvasTkAgg(fig, master=hz_frame32)
canvas.show()
canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

#toolbar = NavigationToolbar2TkAgg(canvas)
#toolbar.update()
#canvas.tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

ani = animation.FuncAnimation(fig, animate_oil, interval=2000)


#Wasser
fig_water=Figure(figsize=(10,2.5), dpi=100)
bx=fig_water.add_subplot(111)
bx.axis([0,1000,10,40])
bx.set_title("Oeltemperatur")


def animate_water(i):
    try:
        bx.clear()
        bx.plot(times, temps_water)
    except:
        pass


canvas_water = FigureCanvasTkAgg(fig_water, master=hz_frame22)
canvas_water.show()
canvas_water.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

#toolbar = NavigationToolbar2TkAgg(canvas)
#toolbar.update()
#canvas.tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

ani_water = animation.FuncAnimation(fig_water, animate_water, interval=2000)


#######################################################################################
'''
Starten der Hauptfunktion in Thread
'''
#######################################################################################
start_new_thread(main_thread,(1,))


root.mainloop()