# coding: utf8
from kivy.config import Config
import json
with open('config.json') as config_file:
            config = json.load(config_file)
if config["fullscreen"]:
    Config.set('graphics', 'fullscreen', 'auto')
else:
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'height', config["height"])
    Config.set('graphics', 'width', config["width"])
Config.set('graphics', 'resizable', '0')
Config.write()
from kivy.uix.image import Image
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy import args
from kivy.clock import Clock
from libs.gardengraph.graph import Graph, SmoothLinePlot
from kivy.utils import get_color_from_hex as rgb
from kivy.properties import NumericProperty, BooleanProperty,\
    BoundedNumericProperty, StringProperty, ListProperty, ObjectProperty,\
    DictProperty, AliasProperty
import time
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.slider import Slider
from subprocess import Popen, PIPE, call
import re
import csv
import sys
import os
try:
    import RPi.GPIO as GPIO
except:
    print("No GPIO")


class BurningPiApp(App):
    #temperature properties
    oil_temp_set = NumericProperty(20)
    oil_temp_is = NumericProperty(0.0)
    water_temp_max = NumericProperty(20)
    water_temp_is = NumericProperty()
    time_is = NumericProperty(0)
    delta_heating = NumericProperty(5)
    delta_cooling = NumericProperty(5)
    
    #status properties
    heat_auto = BooleanProperty(False)
    heating = BooleanProperty(False)
    pumping = BooleanProperty(False)
    water_alarm = BooleanProperty(False)
    water_alarm_counter = NumericProperty(0)
    web_counter = NumericProperty(0)

    #Start Time
    start_time = NumericProperty()
    
    #Lists for Temperature and Time
    times = ListProperty()
    oil_temps = ListProperty([])
    oil_temps_set = ListProperty()
    water_temps = ListProperty()
    
    #Sensors
    temp_sensor_oil = StringProperty()
    temp_sensor_water = StringProperty()
    #GPIO
    gpio_oil = NumericProperty()
    gpio_water = NumericProperty()
    
    
    def build(self):
        self.icon = "pic/icon.png"
        self.title = "Burning Pi"
        try:
            GPIO.setmode(GPIO.BCM)
        except:
            pass
        self.start_time = time.time()
        self.get_config()
        
        try:
            GPIO.setup(self.gpio_oil, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.gpio_water, GPIO.OUT, initial=GPIO.LOW)
        except:
            pass

        #f = open('www/oil.csv', 'wb')
#         try:
#             writer = csv.writer(f)
#             writer.writerow( ('country',"visits") )
#         finally:
#             f.close()
        #f.write('')
        #f.close()
        
        
        layout = self.make_layout()
        
        #if not self.config["debug"]:
        self.oil_temp_is = self.tempdata1(self.temp_sensor_oil)
        self.water_temp_is = self.tempdata1(self.temp_sensor_water)
        
        my_dict = {'oil_is': self.oil_temp_is, 'oil_set': self.set_oil_temp_slider.value, 'time': 0, 'water': self.water_temp_is}
        
        with open('www/tempdata.json', 'w') as f:
            f.write('[')
            f.write(os.linesep)
            json.dump(my_dict, f)
            f.write(os.linesep)
            f.write(']')
        
        Clock.schedule_interval(self.refresh_graph_scale, 1)
        Clock.schedule_interval(self.check_water_temp, 1)
        Clock.schedule_interval(self.check_oil_temp, 1)
        
        
        
        return layout
    

    def post_build(self):
        pass

    def refresh_plot_points(self):
        self.plot_oil.points = [(self.times[x], self.oil_temps[x]) for x in range(0, len(self.times))]
        self.plot_oil_set.points = [(self.times[x], self.oil_temps_set[x]) for x in range(0, len(self.times))]
        self.plot_water.points = [(self.times[x], self.water_temps[x]) for x in range(0, len(self.times))]

    def read_sensor(self, *args):
        try:
            if self.config["debug"]:
                oil_temp = self.tempdata(self.temp_sensor_oil)
                water_temp = self.tempdata(self.temp_sensor_water)
#                 f = open(self.temp_sensor_oil)
#                 oil_temp = float(f.read())
#                 f.close()
#                 
#                 f = open(self.temp_sensor_water)
#                 water_temp = float(f.read())
#                 f.close()
                
            else:
                oil_temp = self.tempdata(self.temp_sensor_oil)
                water_temp = self.tempdata(self.temp_sensor_water)
                
            
            self.water_temp_is = water_temp
            
            
            self.oil_temp_is = oil_temp
            
            time_is = float(time.time()-self.start_time)
            
            self.time_is = time_is
            self.oil_temps_set.append(self.set_oil_temp_slider.value)
            
            self.water_temps.append(water_temp)
            self.oil_temps.append(oil_temp)
            self.times.append(time_is) 
            self.refresh_plot_points()
            
            if self.web_counter == 5:
                my_dict = {'oil_is': oil_temp, 'oil_set': self.set_oil_temp_slider.value, 'time': int(time_is), 'water': water_temp}
                
                with open('www/tempdata.json', 'rb+') as f:
                    f.seek(-1, os.SEEK_END)
                    f.truncate()
                with open('www/tempdata.json', 'a') as f:
                    f.write(',')
                    f.write(os.linesep)
                    json.dump(my_dict, f)
                    f.write(']')
                self.web_counter = 0
            else:
                self.web_counter += 1
            
           # f = open('www/oil.csv', 'ab')
           # try:
           #     writer = csv.writer(f)
           #     writer.writerow( (str(time_is), str(oil_temp)) )
           # finally:
           #     f.close()
            
            
        except:
            self.read_sensor()

    def tempdata1(self, sensor):
      
        # 1-wire Slave Datei lesen
        tempfile = open(sensor)
        filecontent = tempfile.read()
        tempfile.close()
     
        # Temperaturwerte auslesen und konvertieren
        #stringvalue = filecontent.split("\n")[1].split(" ")[9]
        temp_mC = float(filecontent) / 1000
        return temp_mC

    def tempdata10(self, sensor):
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
            return self.tempdata1(sensor)
        
        
    def tempdata(self, sensor):
      
        # 1-wire Slave Datei lesen
        tempfile = open(sensor)
        filecontent = tempfile.read()
        tempfile.close()
     
        # Temperaturwerte auslesen und konvertieren
        #stringvalue = filecontent.split("\n")[1].split(" ")[9]
        temp_mC = float(filecontent) / 1000
        
        if sensor == self.temp_sensor_oil:
            if (abs(temp_mC-self.oil_temp_is<30)):
                return temp_mC
            else:
                print("invalid result")
                return self.oil_temp_is
        if sensor == self.temp_sensor_water:
            if (abs(temp_mC-self.water_temp_is<30)):
                return temp_mC
            else:
                print("invalid result")
                return self.water_temp_is

    def tempdata0(self, sensor):
        pipe=Popen(["cat", sensor], stdout=PIPE)
        result=pipe.communicate()[0]
        result_list=result.split("=")
        temp_mC=float(result_list[-1])/1000
        if sensor == self.temp_sensor_oil:
            if (re.match(".*YES.*", result)) and (abs(temp_mC-self.oil_temp_is<15)):
                return temp_mC
            else:
                print(result)
                print("invalid result")
                return self.tempdata(sensor)
        if sensor == self.temp_sensor_water:
            if (re.match(".*YES.*", result)) and (abs(temp_mC-self.water_temp_is<15)):
                return temp_mC
            else:
                print(result)
                print("invalid result")
                return self.tempdata(sensor)

    def check_oil_temp(self, *args):
        if self.heat_auto:
            if self.heating:
                if self.oil_temp_is > (self.oil_temp_set - self.delta_heating):
                    self.change_heating_status()
            else:
                if int(self.oil_temp_is) <= int(self.oil_temp_set - self.delta_cooling):
                    self.change_heating_status()
            
    def check_water_temp(self, *args):
        if self.water_temp_is >= self.water_temp_max:
            if self.water_alarm_counter == 5:
                self.water_alarm_counter = 0
                if self.water_alarm:
                    self.graph_water.background_color = rgb('ffffff')
                    self.water_alarm = False
                else:
                    self.graph_water.background_color = rgb('ff0000')
                    self.water_alarm = True
            self.water_alarm_counter += 1
        else:
            self.graph_water.background_color = rgb('ffffff')
    
    def change_heating_status(self):
        if self.heating:
            self.heating_image.source = 'pic/heating_off.png'
            #GPIO
            try:
                GPIO.output(self.gpio_oil, GPIO.HIGH)
            except:
                pass
            self.heating = False  
        else:
            self.heating_image.source = 'pic/heating_on.png'
            #GPIO
            try:
                GPIO.output(self.gpio_oil, GPIO.LOW)
            except:
                pass
            self.heating = True
            
    def refresh_graph_scale(self, *args):
        self.read_sensor()
        
        self.graph_oil.xmax = round(max(self.times)+1)
        self.graph_oil.x_ticks_major = int(self.graph_oil.xmax/10)
        self.graph_oil.ymax = round(max(max(self.oil_temps),max(self.oil_temps_set))+1)
        self.graph_oil.ymin = round(min(min(self.oil_temps),min(self.oil_temps_set)))
        self.graph_oil.y_ticks_major = int(round((self.graph_oil.ymax-self.graph_oil.ymin)/5))
        
        self.graph_water.xmax = round(max(self.times)+1)
        self.graph_water.x_ticks_major = int(self.graph_water.xmax/10)
        self.graph_water.ymax = round(max(self.water_temps)+1)
        self.graph_water.ymin = round(min(self.water_temps)-1)
        self.graph_water.y_ticks_major = int(round((self.graph_water.ymax-self.graph_water.ymin)/5))
        
    def on_time_is(self, instance, value):
        self.time_label.text = str(int(self.time_is/60))+" min"
              
    def on_oil_temp_is(self, instance, value):
        self.oil_temp_label.text = str(int(self.oil_temp_is))+" °C"
        
    def on_water_temp_is(self, instance, value):
        self.water_temp_label.text = str(int(self.water_temp_is))+" °C"
              
    def on_button_heating(self, *args):
        if self.heat_auto:
            self.heat_auto = False
            self.button_heating.background_normal = "pic/flame_off.png"
            if self.heating:
                self.change_heating_status()
        else:
            self.heat_auto = True
            self.button_heating.background_normal = "pic/flame_on.png"
        
    def on_button_pump(self, *args):
        if self.pumping:
            self.pumping = False
            try:
                GPIO.output(self.gpio_water, GPIO.HIGH)
            except:
                pass
            self.button_pump.background_normal = "pic/pump_off.png"
        else:
            self.pumping = True
            try:
                GPIO.output(self.gpio_water, GPIO.LOW)
            except:
                pass
            self.button_pump.background_normal = "pic/pump_on.png"
        
    def on_set_oil_temp_slider(self, *args):
        self.oil_temp_set = int(args[1])
        self.set_oil_temp_label.text = str(int(args[1]))+" °C"
        
    def on_set_water_temp_slider(self, *args):
        self.set_water_temp_label.text = str(int(args[1]))+" °C"
        self.water_temp_max = int(args[1])
        
    def on_set_delta_heating_slider(self, *args):
        self.delta_heating = int(args[1])
        self.set_delta_heating_label.text = str(int(args[1]))+" °C"
        
    def on_set_delta_cooling_slider(self, *args):
        self.delta_cooling = int(args[1])
        self.set_delta_cooling_label.text = str(int(args[1]))+" °C"

    def make_layout(self):
        layout = BoxLayout(orientation="vertical")
        
        settingslayout = BoxLayout(orientation="horizontal")
        left_settings = BoxLayout(orientation="horizontal")
        settingslayout.add_widget(left_settings)
        
        
        on_off_layout = BoxLayout(orientation="vertical")
        self.on_off_layout = on_off_layout
        
        button_heating = Button(background_normal="pic/flame_off.png", background_down="pic/flame_pressed.png",allow_stretch=False, size_hint=(0.7, 1), border=[0,0,0,0])
        button_heating.bind(on_press=self.on_button_heating)
        self.button_heating = button_heating
        
        
        
        button_pump = Button(background_normal="pic/pump_off.png", background_down="pic/pump_pressed.png",allow_stretch=False, size_hint=(0.7, 1), border=[0,0,0,0])
        button_pump.bind(on_press=self.on_button_pump)
        self.button_pump = button_pump
        
        
        temperatur_panel = BoxLayout(orientation="vertical")
        
        oil_temp_label = Label(text = "0 Grad", color=[0,0,0,1], font_size = 30)
        self.oil_temp_label = oil_temp_label
        temperatur_panel.add_widget(oil_temp_label)
        
        water_temp_label = Label(text = "0 Grad", color=[0,0,0,1], font_size = 30)
        self.water_temp_label = water_temp_label
        temperatur_panel.add_widget(water_temp_label)
        
        time_label = Label(text = "0 min", color=[0,0,0,1], font_size = 30)
        self.time_label = time_label
        temperatur_panel.add_widget(time_label)
        
        heating_image = Image(source = 'pic/heating_off.png')
        self.heating_image = heating_image
        temperatur_panel.add_widget(heating_image)
        
        
        names_panel = BoxLayout(orientation="vertical")
        name_oil = Label(text = "Öl:", color=[0,0,0,1], font_size = 30)
        names_panel.add_widget(name_oil)
        name_water = Label(text = "Wasser:", color=[0,0,0,1], font_size = 30)
        names_panel.add_widget(name_water)
        name_time = Label(text = "Zeit:", color=[0,0,0,1], font_size = 30)
        names_panel.add_widget(name_time)
        name_heating = Label(text = "Heizen:", color=[0,0,0,1], font_size = 30)
        names_panel.add_widget(name_heating)
        
        
        
        set_value_panel = BoxLayout(orientation="vertical")
        set_value_oil_panel = BoxLayout(orientation="horizontal")
        set_value_water_panel = BoxLayout(orientation="horizontal")
        set_delta_heating_panel = BoxLayout(orientation="horizontal")
        set_delta_cooling_panel = BoxLayout(orientation="horizontal")
        set_value_panel.add_widget(set_value_oil_panel)
        set_value_panel.add_widget(set_value_water_panel)
        set_value_panel.add_widget(set_delta_heating_panel)
        set_value_panel.add_widget(set_delta_cooling_panel)
        
        
        set_oil_temp_slider = Slider(min = 0, max = 150, value = 50)
        self.set_oil_temp_slider = set_oil_temp_slider
        set_oil_temp_slider.bind(value=self.on_set_oil_temp_slider)
        set_value_oil_panel.add_widget(set_oil_temp_slider)
        set_oil_temp_label = Label(text = "50 °C", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        self.set_oil_temp_label = set_oil_temp_label
        set_value_oil_panel.add_widget(set_oil_temp_label)
        
        set_water_temp_slider = Slider(min = 0, max = 50, value = 10)
        self.set_water_temp_slider = set_water_temp_slider
        set_water_temp_slider.bind(value=self.on_set_water_temp_slider)
        set_value_water_panel.add_widget(set_water_temp_slider)
        set_water_temp_label = Label(text = "10 °C", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        self.set_water_temp_label = set_water_temp_label
        set_value_water_panel.add_widget(set_water_temp_label)
        
        name_delta_heating_label = Label(text = u"\u0394"+"Th", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        set_delta_heating_panel.add_widget(name_delta_heating_label)
        set_delta_heating_slider = Slider(min = 0, max = 10, value = 5)
        self.set_delta_heating_slider = set_delta_heating_slider
        set_delta_heating_slider.bind(value=self.on_set_delta_heating_slider)
        set_delta_heating_panel.add_widget(set_delta_heating_slider)
        set_delta_heating_label = Label(text = "5 °C", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        self.set_delta_heating_label = set_delta_heating_label
        set_delta_heating_panel.add_widget(set_delta_heating_label)
        
        name_delta_cooling_label = Label(text = u"\u0394"+"Tk", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        set_delta_cooling_panel.add_widget(name_delta_cooling_label)
        set_delta_cooling_slider = Slider(min = 0, max = 10, value = 5)
        self.set_delta_cooling_slider = set_delta_cooling_slider
        set_delta_cooling_slider.bind(value=self.on_set_delta_cooling_slider)
        set_delta_cooling_panel.add_widget(set_delta_cooling_slider)
        set_delta_cooling_label = Label(text = "5 °C", color=[0,0,0,1], font_size = 30, size_hint=(None,1))
        self.set_delta_cooling_label = set_delta_cooling_label
        set_delta_cooling_panel.add_widget(set_delta_cooling_label)
        
        
        
        
        left_settings.add_widget(on_off_layout)
        left_settings.add_widget(names_panel)
        left_settings.add_widget(temperatur_panel)
        settingslayout.add_widget(set_value_panel)
        on_off_layout.add_widget(button_heating)
        on_off_layout.add_widget(button_pump)
        layout.add_widget(settingslayout)
        
        
        
        with layout.canvas.before:
            Color(1, 1, 1, 1) 
            layout.rect = Rectangle(size=layout.size,
                           pos=layout.pos)
            
        layout.bind(pos=self.update_rect, size=self.update_rect)
        
        graph_theme = {
            'label_options':{
                'color':rgb('444444'), # color of tick labels and titles
                'bold':True}, 
            'background_color':rgb('ffffff'), # back ground color of canvas
            'tick_color':rgb('808080'), # ticks and grid
            'border_color':rgb('808080')}
        graph_oil = Graph( 
            xlabel="Zeit [s]",
            ylabel="Öltemperatur [°C]", 
            x_ticks_major=1, 
            y_ticks_major=1, 
            y_grid_label=True, 
            x_grid_label=True, 
            padding=5, 
            xlog=False, 
            ylog=False, 
            x_grid=True, 
            y_grid=True, 
            xmin=0, 
            xmax=10, 
            **graph_theme)
        self.graph_oil = graph_oil
        
        graph_water = Graph(
            xlabel="Zeit [s]", 
            ylabel="Wassertemperatur [°C]", 
            x_ticks_major=1, 
            y_ticks_major=10, 
            y_grid_label=True, 
            x_grid_label=True, 
            padding=5, 
            xlog=False, 
            ylog=False, 
            x_grid=True, 
            y_grid=True, 
            xmin=0, 
            xmax=10, 
            **graph_theme)
        self.graph_water = graph_water
        
        plot_oil = SmoothLinePlot(color=rgb('ff0000'))
        self.plot_oil = plot_oil
        
        plot_oil_set = SmoothLinePlot(color=rgb('00ff00'))
        self.plot_oil_set = plot_oil_set
        
        plot_water = SmoothLinePlot(color=rgb('0000ff'))
        self.plot_water = plot_water
        plot_water.points = [(x, x * x) for x in range(0, 11)]
        graph_oil.add_plot(plot_oil)
        graph_oil.add_plot(plot_oil_set)
        graph_water.add_plot(plot_water)
        layout.add_widget(graph_oil)
        layout.add_widget(graph_water)
        
        

        
        
        
        
        return layout
    
    def update_rect(self, instance, value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size

    def get_config(self):
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.config = config
        if self.config["debug"]:
            self.temp_sensor_oil = 'tests/testdata/sensor1'
            self.temp_sensor_water = 'tests/testdata/sensor2'
        else:
            self.temp_sensor_oil = self.config["sensor_oil"]
            self.temp_sensor_water = self.config["sensor_water"]
        self.gpio_oil = self.config["gpio_oil"]
        self.gpio_water = self.config["gpio_water"]
        print self.temp_sensor_oil
        print self.temp_sensor_water
        
    def on_stop(self):
        #GPIO Cleanup
        try:
            GPIO.cleanup(self.gpio_oil)
            GPIO.cleanup(self.gpio_water)
        except:
            pass
        print("Gestoppt")
        
        


    
    
if __name__ == '__main__':
    BurningPiApp().run()
    
    
