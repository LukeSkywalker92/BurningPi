# coding: utf8
from kivy.config import Config
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'height', 512)
Config.set('graphics','width', 256)
Config.set('graphics', 'resizable', '0')
Config.write()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
import time
from kivy import args




class SimulateSensorApp(App):
    
    def build(self):
        main_layout = BoxLayout(orientation='horizontal')
        oil_layout = BoxLayout(orientation='vertical')
        water_layout = BoxLayout(orientation='vertical')
        
        oil_label = Label(text='Öl', size_hint = (1, None), font_size = 30)
        oil_temp_label = Label(text='20 °C', size_hint = (1, None), font_size = 30)
        self.oil_temp_label = oil_temp_label
        oil_slider = Slider(min = 0, max = 150, value = 20, orientation = 'vertical')
        self.oil_slider = oil_slider
        oil_slider.bind(value=self.on_oil_slider)
        
        oil_layout.add_widget(oil_label)
        oil_layout.add_widget(oil_slider)
        oil_layout.add_widget(oil_temp_label)
        
        
        water_label = Label(text='Wasser', size_hint = (1, None), font_size = 30)
        water_temp_label = Label(text='10 °C', size_hint = (1, None), font_size = 30)
        self.water_temp_label = water_temp_label
        water_slider = Slider(min = 0, max = 40, value = 10, orientation = 'vertical')
        self.water_slider = water_slider
        water_slider.bind(value=self.on_water_slider)
        
        water_layout.add_widget(water_label)
        water_layout.add_widget(water_slider)
        water_layout.add_widget(water_temp_label)
        
        
        main_layout.add_widget(oil_layout)
        main_layout.add_widget(water_layout)
        
        
        
        return main_layout
    
    def on_oil_slider(self, *args):
        self.oil_temp_label.text = str(int(args[1]))+" °C"
        f = open("testdata/sensor1","w+")
        f.write(str(1000*int(args[1])))
        f.close()
        
    def on_water_slider(self, *args):
        self.water_temp_label.text = str(int(args[1]))+" °C"
        f = open("testdata/sensor2","w+")
        f.write(str(1000*int(args[1])))
        f.close()
    
SimulateSensorApp().run()