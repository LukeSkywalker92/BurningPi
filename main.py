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
from random import random

class BurningPiApp(App):
    #temperature properties
    oil_temp_set = NumericProperty()
    oil_temp_is = NumericProperty()
    water_temp_max = NumericProperty()
    water_temp_is = NumericProperty()
    
    #status properties
    heat_auto = BooleanProperty(False)
    heating = BooleanProperty(False)
    pumping = BooleanProperty(False)
    
    #Start Time
    start_time = NumericProperty(1)
    
    #Lists for Temperature and Time
    times = ListProperty()
    oil_temps = ListProperty()
    oil_temps_set = ListProperty()
    water_temps = ListProperty()
    
    #Sensors
    temp_sensor_oil = StringProperty()
    temp_sensor_water = StringProperty()
    
    
    
    def build(self):
        
        #self.start_time.set(BurningPiApp, time.time())
        self.start_time = time.time()
        
        layout = self.make_layout()
        
        
        return layout
    
    def read_senor(self, *args):
        f = open("tests/testdata/sensor1")
        print(f.read())
        f.close()
    
    def klick(self, *args):
        self.start_time = time.time()
        
    def on_start_time(self, instance, value):
        print('My property a changed to', value)

    def make_layout(self):
        layout = BoxLayout(orientation="vertical")
        settingslayout = BoxLayout(orientation="horizontal")
        button1 = Button(background_normal="pic/pump.jpg", background_down="pic/pump.jpg")
        button1.bind(on_press=self.klick)
        button2 = Button(text="Knopf2")
        settingslayout.add_widget(button1)
        settingslayout.add_widget(button2)
        layout.add_widget(settingslayout) #Clock.schedule_interval(self.read_senor, 1)
        graph_theme = {
            'label_options':{
                'color':rgb('444444'), # color of tick labels and titles
                'bold':True}, 
            'background_color':rgb('f8f8f2'), # back ground color of canvas
            'tick_color':rgb('808080'), # ticks and grid
            'border_color':rgb('808080')}
        graph = Graph(
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
            ymin=0, 
            ymax=100, **
            graph_theme)
        plot = SmoothLinePlot(color=rgb('000000'))
        plot.points = [(x, x * x) for x in range(0, 11)]
        graph.add_plot(plot)
        layout.add_widget(graph)
        return layout

    
    
if __name__ == '__main__':
    BurningPiApp().run()