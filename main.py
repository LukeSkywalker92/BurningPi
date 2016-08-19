# coding: utf8
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
from kivy.config import Config
import time
import json
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.slider import Slider



class BurningPiApp(App):
    #temperature properties
    oil_temp_set = NumericProperty(20)
    oil_temp_is = NumericProperty(0.0)
    water_temp_max = NumericProperty(20)
    water_temp_is = NumericProperty()
    
    #status properties
    heat_auto = BooleanProperty(False)
    heating = BooleanProperty(False)
    pumping = BooleanProperty(False)
    
    #Start Time
    start_time = NumericProperty(1)
    
    #Lists for Temperature and Time
    times = ListProperty()
    oil_temps = ListProperty([])
    oil_temps_set = ListProperty()
    water_temps = ListProperty()
    
    #Sensors
    temp_sensor_oil = StringProperty()
    temp_sensor_water = StringProperty()
    
    
    
    def build(self):
        
        #self.start_time.set(BurningPiApp, time.time())
        self.start_time = time.time()
        
        self.get_config()
        
        layout = self.make_layout()
        
        Clock.schedule_interval(self.refresh_graph_scale, 1)
        
        return layout
    

    def refresh_plot_points(self):
        self.plot_oil.points = [(self.times[x], self.oil_temps[x]) for x in range(0, len(self.times))]
        self.plot_water.points = [(self.times[x], self.water_temps[x]) for x in range(0, len(self.times))]

    def read_sensor(self, *args):
        try:
            f = open(self.temp_sensor_oil)
            oil_temp = float(f.read())
            f.close()
            
            f = open(self.temp_sensor_water)
            water_temp = float(f.read())
            f.close()
            
            self.water_temps.append(water_temp)
            self.water_temp_is = water_temp
            
            self.oil_temps.append(oil_temp)
            self.oil_temp_is = oil_temp
            
            self.times.append(float(time.time()-self.start_time)) 
            
            self.refresh_plot_points()
        except:
            self.read_sensor()

    
    def refresh_graph_scale(self, *args):
        self.read_sensor()
        
        self.graph_oil.xmax = round(max(self.times)+1)
        self.graph_oil.x_ticks_major = int(self.graph_oil.xmax/10)
        self.graph_oil.ymax = max(self.oil_temps)+1
        self.graph_oil.ymin = min(self.oil_temps)-1
        self.graph_oil.y_ticks_major = (self.graph_oil.ymax-self.graph_oil.ymin)/10
        
        self.graph_water.xmax = round(max(self.times)+1)
        self.graph_water.x_ticks_major = int(self.graph_water.xmax/10)
        self.graph_water.ymax = max(self.water_temps)+1
        self.graph_water.ymin = min(self.water_temps)-1
        self.graph_water.y_ticks_major = (self.graph_water.ymax-self.graph_water.ymin)/10
        
    def on_oil_temp_is(self, instance, value):
        self.oil_temp_label.text = str(int(self.oil_temp_is))+" °C"
        
    def on_water_temp_is(self, instance, value):
        self.water_temp_label.text = str(int(self.water_temp_is))+" °C"
        
    def on_start_time(self, instance, value):
        print('My property a changed to', value)
        
    def on_button_heating(self, *args):
        self.button_heating.background_normal = "pic/flame_pressed.png"
        
    def on_button_pump(self, *args):
        self.button_pump.background_normal = "pic/flame_pressed.png"

    def make_layout(self):
        layout = BoxLayout(orientation="vertical")
        
        settingslayout = BoxLayout(orientation="horizontal")
        
        
        on_off_layout = BoxLayout(orientation="vertical")
        
        button_heating = Button(background_normal="pic/flame_normal.png", background_down="pic/flame_pressed.png",allow_stretch=False, size_hint=(None,None))
        button_heating.bind(on_press=self.on_button_heating)
        self.button_heating = button_heating
        
        button_pump = Button(background_normal="pic/flame_normal.jpg", background_down="pic/flame_pressed.jpg",allow_stretch=False, size_hint=(None,None))
        button_pump.bind(on_press=self.on_button_pump)
        self.button_pump = button_pump
        
        
        temperatur_panel = BoxLayout(orientation="vertical")
        
        oil_temp_label = Label(text = "0 Grad", color=[0,0,0,1], font_size = 30, size_hint=(None,None))
        self.oil_temp_label = oil_temp_label
        temperatur_panel.add_widget(oil_temp_label)
        
        water_temp_label = Label(text = "0 Grad", color=[0,0,0,1], font_size = 30, size_hint=(None,None))
        self.water_temp_label = water_temp_label
        temperatur_panel.add_widget(water_temp_label)
        
        set_value_panel = BoxLayout(orientation="vertical")
        set_value_oil_panel = BoxLayout(orientation="horizontal")
        set_value_panel.add_widget(set_value_oil_panel)
        
        set_oil_temp_label = Label(text = "0 °C", color=[0,0,0,1], font_size = 30)
        self.set_oil_temp_label = set_oil_temp_label
        set_value_oil_panel.add_widget(set_oil_temp_label)
        set_oil_temp_slider = Slider(min = 0, max = 150, value = 50)
        self.set_oil_temp_slider = set_oil_temp_slider
        set_value_oil_panel.add_widget(set_oil_temp_slider)
        
        
        
        
        
        settingslayout.add_widget(on_off_layout)
        settingslayout.add_widget(temperatur_panel)
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
            xlabel="X",
            ylabel="Y", 
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
            xlabel="X", 
            ylabel="Y", 
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
        
        plot_oil = SmoothLinePlot(color=rgb('000000'))
        self.plot_oil = plot_oil
        
        plot_water = SmoothLinePlot(color=rgb('000000'))
        self.plot_water = plot_water
        plot_water.points = [(x, x * x) for x in range(0, 11)]
        graph_oil.add_plot(plot_oil)
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
        if bool(config["fullscreen"]):
            Config.set('graphics', 'fullscreen', 'auto')
        self.temp_sensor_oil = config["sensor_oil"]
        self.temp_sensor_water = config["sensor_water"]
        print self.temp_sensor_oil
        print self.temp_sensor_water


    
    
if __name__ == '__main__':
    BurningPiApp().run()