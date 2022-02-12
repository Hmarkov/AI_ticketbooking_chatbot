from asyncio.windows_events import NULL
from timestamps import Timestamp
from concurrent.futures import process
import timestamps
import queue
import kivy
from datetime import datetime
from datetime import date 
import threading
import json
import time
import socket
import random
import calendar
import time
from kivy.config import Config
import pyowm
Config.set('graphics', 'resizable', False)
import threading
from threading import Thread
import socket
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color,RoundedRectangle
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen

"""
READ THIS BEFORE EXECUTING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Please run server.py before running this file.
If the server file returns an error after sending a message run server.py in debug mode  
The purpose of server.py is to process the user messages. 
"""

#Window configuration
Window.size=(1200,1000)
Window.clearcolor = (0/255,0/255,0/255,1)

#Global elelemnts necessary to spawn widgets
text_dict={}
dply=0
turn=0

day_abr=list(calendar.day_name)

#Image show function as a message
def show_r_im(sr):
    b=BoxLayout(orientation="vertical", spacing=5,size_hint=(1,None),size=(450,215),pos_hint={'left':1, 'top':1})
    b.add_widget(Label(text="", font_size=11,size_hint=(None,None),size=("30dp","10dp"),pos_hint={'left':1, 'top':1} ))
    b.add_widget(Image(source=sr,size_hint=(None,None),size=("300dp","200dp"),pos_hint={'left':1, 'top':1}))
    dply.add_widget(b)

#Display function for client messages
def sonly(tx,*f):
    global turn
    global text_dict
    global dply
    
    if tx=="":
        return
    if tx!="!im":
        ssize=len(tx)*0.0080+0.10
        text_dict[str(datetime.now())[:-7]]=tx
        b=BoxLayout(orientation="vertical",spacing=2,padding=2,size_hint=(1,None),pos_hint={'right':1, 'top':1})
        while turn!=1:
            turn=1
            b.add_widget(Label(text="You", font_size=35,size_hint=(None,None),size=("80dp","40dp"),pos_hint={'right':1, 'top':1} ))
            b.add_widget(text_your(tx,ssize))
            dply.add_widget(b)

#Display function for server messages
def process_message(tx):
    global turn
    global text_dict
    global dply
    if tx=="":
        return
    elif tx!="qrcode1.png":
        if len(tx)>100:
            ssize=len(tx)*0.004+0.10
            hsize=50
        else:
            ssize=len(tx)*0.0080+0.10
            hsize=len(tx)*0.001
        text_dict[str(datetime.now())[:-7]]=tx
        b=BoxLayout(orientation="vertical",spacing=2,padding=2,size_hint=(1,None),pos_hint={'right':1, 'top':1})
        if turn==1:
            b.add_widget(Label(text="", font_size=35,size_hint=(None,None),size=("80dp","40dp"),pos_hint={'left':1, 'top':1} ))
        b.add_widget(text_their(tx,ssize,hsize))
        dply.add_widget(b)  
        turn=0
    else:
        show_r_im(tx)

#Function that gets already processed messages from the server 
def feedback_send(tx):
    global turn
    global text_dict
    global dply
    turn=1
    if len(tx)>100:
        ssize=len(tx)*0.004+0.10
        hsize=0.001
    else:
        ssize=len(tx)*0.0080+0.10
        hsize=len(tx)*0.001
    text_dict[str(datetime.now())[:-7]]=tx
    b=BoxLayout(orientation="vertical",spacing=2,padding=2,size_hint=(1,None),pos_hint={'right':1, 'top':1})
    if turn==1:
        b.add_widget(Label(text="", font_size=35,size_hint=(None,None),size=("80dp","40dp"),pos_hint={'left':1, 'top':1} ))
        turn=0
    b.add_widget(text_their(tx,ssize,hsize))
    dply.add_widget(b)  

#Message box configurations
class text_their(Button):
    def __init__(self,tx,ssize,hsize,**kwargs):
        super(text_their,self).__init__(**kwargs)
        self.text=tx
        self.background_normal='Icons/ch2.png'
        self.background_down='Icons/ch2.png'
        self.font_size=20
        self.size_hint=(ssize,hsize)
        self.size=(ssize,"90dp")
        self.pos_hint={'left':1, 'top':1}

class text_your(Button):
    def __init__(self,tx,ssize,**kwargs):
        super(text_your,self).__init__(**kwargs)
        self.text=tx
        self.background_normal='Icons/ch1.png'
        self.background_down='Icons/ch1.png'
        self.font_size=20
        self.size_hint=(ssize,None)
        self.size=(ssize,"90dp")
        self.pos_hint={'right':1, 'top':1}

#Chatbot class configuration
class ChatBot(App):
    #exit function
    def exit(self):
        Window.close()

    #Initial display initialization 
    def initialize(self,d):
        global dply
        dply=d

    #clear widgets on display function
    def clear_chat(self):
        dply.clear_widgets()

    #get current date and weekday as a string function
    def date(self,wd):
        while True:
            today=date.today()
            d=str(today.strftime("%d-%m-%Y"))
            weekd=calendar.day_name[date.today().weekday()]
            dwd=str(d+"\n"+weekd)
            wd.text=dwd
            time.sleep(3600)

    #initialize current city
    def getcity():
        currentcity='Norwich'
        return currentcity

    def city(self,wd):
        wd.text=ChatBot.getcity()

    #Weather API configuration
    def Apidata():
        APIKEY='b6b80fdccb01e3b2ec74c540330c5e41'
        OpenWMap=pyowm.OWM(APIKEY)
        mng = OpenWMap.weather_manager()
        Weather=mng.weather_at_place(ChatBot.getcity()) 
        Data=Weather.weather
        return Data

    def city(self,wd):
        city='Norwich'
        wd.text=city
        return city
        
    #get current temperature function from pyOWM
    def temperature(self,wd):
        while True:
            temp = ChatBot.Apidata().temperature()
            temp=round(temp['temp']-273.15)
            temperature=str(temp)+"\N{DEGREE SIGN}"
            wd.text=str(temperature)
            time.sleep(600)
            
    #get current humidity function from pyOWM        
    def humidity(self,wd):
        while True:
            hum = str(ChatBot.Apidata().humidity)
            humidity=hum+"%"
            wd.text=str(humidity)
            time.sleep(600)

    #get current windspeed function from pyOWM
    def windspeed(self,wd):
        while True:
            wind = ChatBot.Apidata().wind()
            wd.text=str(wind['speed'])
            time.sleep(600)

    #get current time function
    def clock(self,wd):
        while True:
            now = time.localtime()
            wd.text=str(time.strftime("%H:%M",now))
            time.sleep(1)
    
    #client based send function after the message from the GUI is displayed
    #this function sends the message to the server and waits for the server to process it and send it back
    def send(self,t):
        sonly(t.text)
        host='127.0.0.1' #client ip
        port = 4005
        
        server = ('127.0.0.1', 4000)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((host,port))
        
        message = t.text
        if message !='q':
            s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            print("Received from server: " + data)
            process_message(data)
            if data[-1]!="?":
                data, addr = s.recvfrom(1024)
                data = data.decode('utf-8')
                print("Received from server: " + data)
                process_message(data)
            if data[-1]!="?":
                data, addr = s.recvfrom(1024)
                data = data.decode('utf-8')
                print("Received from server: " + data)
                process_message(data)
            message = t.text
        s.close()
        t.text=""
        
    #kivy design file
    def build(self):
        return Builder.load_file("design.kv")

if __name__ == '__main__':
    ChatBot().run()
    print("Exitted!")
