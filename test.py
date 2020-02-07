import snowboydecoder
from Apollo import *
 

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

st = assistant(mic())

detector = snowboydecoder.HotwordDetector("/home/pho3nix/Tools/ApolloAI/hotword/Apollo.pmdl", 
                       sensitivity = 0.5, audio_gain = 1) 
detector.start(detected_callback=assistant(mic()),
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()