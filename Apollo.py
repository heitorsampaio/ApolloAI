#!/usr/bin python3


#importing stuffs
import speech_recognition as sr
import os
import sys
import re
import webbrowser
import smtplib
import requests
import subprocess
from pyowm import OWM
import youtube_dl
import vlc
import urllib
import urllib3
import json
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
import wikipedia
import random
from time import strftime
from gtts import gTTS
import pyttsx3
import lxml
from yeelight import Bulb
from yeelight import *
from matplotlib import colors
from tempfile import TemporaryFile
import facebook
import tweepy
import snowboydecoder
import signal
import pyaudio
from ibm_watson import TextToSpeechV1
from ibm_watson.websocket import SynthesizeCallback
from pygame import mixer



bulb = Bulb('192.168.15.2')
interrupted = False
text_to_speech = TextToSpeechV1(
    iam_apikey='9mDYXRnjmXZS5grZPaBVleJarFajeVEn-Mjp9m_sWFSm',
    url='https://stream.watsonplatform.net/text-to-speech/api'
)

class Play(object):
    """
    Wrapper to play the audio in a blocking mode
    """
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 22050
        self.chunk = 1024
        self.pyaudio = None
        self.stream = None

    def start_streaming(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self._open_stream()
        self._start_stream()

    def _open_stream(self):
        stream = self.pyaudio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True,
            frames_per_buffer=self.chunk,
            start=False
        )
        return stream

    def _start_stream(self):
        self.stream.start_stream()

    def write_stream(self, audio_stream):
        self.stream.write(audio_stream)

    def complete_playing(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

class MySynthesizeCallback(SynthesizeCallback):
    def __init__(self):
        SynthesizeCallback.__init__(self)
        self.play = Play()

    def on_connected(self):
        print('Opening stream to play')
        self.play.start_streaming()

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_timing_information(self, timing_information):
        print(timing_information)

    def on_audio_stream(self, audio_stream):
        self.play.write_stream(audio_stream)

    def on_close(self):
        print('Completed synthesizing')
        self.play.complete_playing()

test_callback = MySynthesizeCallback()

def apolloRes(audio):
    text_to_speech.synthesize_using_websocket(audio,
                                                test_callback,
                                                accept='audio/wav',
                                                voice="en-US_MichaelV3Voice",)

def mic():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Tell me something... ')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language='en-US').lower()
        print('You said: ' + command)
    except sr.UnknownValueError:
        print('...')
        command = mic()
    return command


def assistant(command):
    
    if 'tell me about' in command:
        reg_ex = re.search('tell me about(.*)', command)
        try:
            if reg_ex:
                topic = reg_ex.group(1)
                wikipedia.set_lang('en')
                ny = wikipedia.summary(topic, sentences=1)
                print(ny)
                apolloRes(ny)
                apolloRes('Thats what i know about %s' %(topic))
        except Exception as e:
                apolloRes(e)

    elif 'open the website' in command:
        reg_ex = re.search('open the website (.*)', command)
        if reg_ex:
            domain = reg_ex.group(1)
            print(domain)
            url = 'https://www.' + domain
            webbrowser.open(url)
            apolloRes('I have opened the desired website.')
        else:
            pass

            bulb.turn_off()
    elif 'hey apollo' in command:
        day_time = int(strftime('%H'))
        if day_time < 12:
            apolloRes('Hey. Good Morning')
        elif 12 <= day_time < 18:
            apolloRes('Hey. Good Afternoon')
        else:
            apolloRes('Hey. Good Night')

    elif 'tell me a joke' in command:
        res = requests.get(
            'https://icanhazdadjoke.com/',
            headers={'Accept':'application/json'})
        if res.status_code == requests.codes.ok:
            apolloRes(str(res.json()['joke']))
        else:
            apolloRes('oops! Im running out of jokes right now and im not in the mood for jokes.')

    elif 'tell me todays news' in command:
        try:
            news_url = 'https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419'
            Client = urlopen(news_url)
            xml_page = Client.read()
            Client.close()
            soup_page = soup(xml_page,'lxml')
            news_list = soup_page.findAll('item')
            for news in news_list[:15]:
                apolloRes(news.title.text)
        except Exception as e:
            print(e)
    
    elif '''how's the weather in ''' in command:
        reg_ex = re.search('''how's the weather in (.*)''', command)
        if reg_ex:
            city = reg_ex.group(1)
            owm = OWM(API_key='247eed961dfdbff4a65c25d27834eaea')
            obs = owm.weather_at_place(city)
            w = obs.get_weather()
            k = w.get_status()
            x = w.get_temperature(unit='celsius')
            apolloRes('O clima em %s é %s. Com máxima temperature de %0.2f e a minima temperatura de %0.2f celsius' % (city, k, x['temp_max'], x['temp_min']))
    elif 'what time is it' in command:
        import datetime
        now = datetime.datetime.now()
        apolloRes('It is %d hours and %d minutes' %(now.hour, now.minute))

    elif 'turn on the room light' in command:
        bulb.turn_on()
        bulb.set_brightness(100)
        apolloRes('Feito.')
    elif 'turn off the room light' in command:
        bulb.turn_off()
        apolloRes('Pronto.')
    elif 'change the room light color to' in command:
        reg_ex = re.search('mude a luz do quarto para (.*)', command)
        if reg_ex:
            color = reg_ex.group(1)
            if color == 'azul':
                bulb.set_rgb(0,0,255)
                apolloRes('Feito.')
            elif color == 'vermelho':
                bulb.set_rgb(255,0,0)
                apolloRes('Feito.')
            elif color == 'cyano':
                bulb.set_rgb(0,255,255)
                apolloRes('Feito.')
            elif color == 'verde limão':
                bulb.set_rgb(0,255,0)
                apolloRes('Feito.')
            elif color == 'amarelo':
                bulb.set_rgb(255,255,0)
                apolloRes('Feito.')
            elif color == 'rosa':
                bulb.set_rgb(255,0,255)
                apolloRes('Feito.')
            elif color == 'verde':
                bulb.set_rgb(128,128,0)
                apolloRes('Feito.')
            elif color == 'azul marinho':
                bulb.set_rgb(0,0,128)
                apolloRes('Feito.')
            elif color == 'roxo':
                bulb.set_rgb(128,0,128)
                apolloRes('Feito.')
            elif color == 'branco':
                bulb.set_rgb(255,255,255)
                apolloRes('Feito.')
    elif 'mude o brilho da luz do quarto para' in command:
        reg_ex = re.search('mude o brilho da luz do quarto para (.*)', command)
        if reg_ex:
            bri = reg_ex.group(1)
            bulb.set_brightness(int(bri))
            apolloRes('O brilho da luz do quarto agora está em %d porcento' %(int(bri)))
    elif 'start light flow' in command:
        transitions = [
            RGBTransition(255,0,255, duration=1000)
        ]
        flow = Flow(
            count=0,
            transitions=transitions
        )
        bulb.start_flow(flow)

    elif 'who are you' in command:
        apolloRes('''Olá, eu sou Apollo, uma inteligencia artificial criada por Heitor Sampaio,
        basta você pedir que eu posso fazer qualquer coisa, todos os dias estou aprendendo mais,
        caso queira saber minhas habilidades, diga "Me ajuda", até mais!
        ''')

    elif 'open the application' in command:
        reg_ex = re.search('abra o (.*)', command)
        if reg_ex:
            appname = reg_ex.group(1)
            appname1 = appname+'.app'
            subprocess.Popen(['open', '-n', '/Applications/' + appname1], stdout=subprocess.PIPE)
            apolloRes('I have opened the desired application')

    elif 'post on twitter' in command:
        reg_ex = re.search('post on twitter (.*)', command)
        if reg_ex:
            post = reg_ex.group(1)
            consumer_key = ''
            consumer_secret = ''
            access_token = ''
            access_token_secret = ''
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            api.update_status(status = post)

    elif 'send a e-mail' in command:
            apolloRes('Para quem você gostaria de enviar o e-mail?')
            #recipient = mic()
    elif 'play the next song' in command:
        subprocess.Popen(['atvremote', '-a', 'next'])
        apolloRes('Ok, i have changed the song on AppleTV')

    elif 'comece uma dinâmica molecular' in  command:
        reg_ex = re.search('comece uma dinâmica molecular (.*)', command)
        if reg_ex:
            din = reg_ex.group(1)
        if din == 'sem gpu':
            process = subprocess.Popen(['python3 /Users/heitorsampaio/GMXSMDF/run.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            process.stdin.write(b'2')
            process.stdin.close()
        elif din == 'com gpu':
            process = subprocess.Popen(['python3', '/Users/heitorsampaio/GMXSMDF/run.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            process.stdin.write(b'1')
            process.stdin.close()
    

while True:
    assistant(mic())

    
