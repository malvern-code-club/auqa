from time import sleep
import os

if os.environ["TEST"] != "y":
    from picamera import PiCamera

def log(message):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S %d/%m/%Y')
    print("[" + st + "] ", message)

def Capture(name):
    if os.environ["TEST"] != "y":
        camera.capture("assets/img/" + name)
    else:
        log("== TAKE PICTURE ==")

if os.environ["TEST"] != "y":
    camera = PiCamera()
    camera.resolution = (1024, 786)
else:
    camera = None
