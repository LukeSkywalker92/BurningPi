from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy import args
from kivy.clock import Clock

class BurningPiApp(App):
    
    def build(self):
        layout = BoxLayout(orientation="horizontal")
        button1 = Button(text="Knopf1")
        button1.bind(on_press=self.klick)
        button2 = Button(text="Knopf2")
        layout.add_widget(button1)
        layout.add_widget(button2)
        Clock.schedule_interval(self.read_senor, 1)
        return layout
    
    def read_senor(self, *args):
        f = open("tests/testdata/sensor1")
        print(f.read())
        f.close()
    
    def klick(self, *args):
        print(args)
        
    
    
if __name__ == '__main__':
    BurningPiApp().run()