import os

if os.environ["TEST"] != "y": # Make sure we are not testing as this will import error
    from sense_hat import SenseHat
    import RPi.GPIO as GPIO
import sqlite3
import time
import datetime
import random

import camera

conn = sqlite3.connect("database.db", check_same_thread=False) #SQLite3 Setup
c = conn.cursor() #SQL Cursor

c.execute("""CREATE TABLE IF NOT EXISTS `data` (
	`id`	        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`timestamp`	    DATE NOT NULL DEFAULT (datetime('now','localtime')),
	`humidity`	    REAL,
	`temperature`	REAL,
	`pressure`	    REAL,
	`soil_humidity` REAL,
    `image`,        TEXT
);""")

conn.commit()

c.execute("""CREATE TABLE IF NOT EXISTS `options` (
    `name`          TEXT,
	`value`	        TEXT
);""")

conn.commit()


if os.environ["TEST"] != "y":
    s = SenseHat() #Sensehat Setup

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN) # Soil Sensor
    GPIO.setup(18, GPIO.OUT) # Pump
else:
    s = None

def get_data(): #Get humidity and temperature
    if os.environ["TEST"] != "y":
        humidity = s.get_humidity()
        temp = s.get_temperature()
        pressure = s.get_pressure()
        soil_humidity = GPIO.input(17)
    else:
        # Generate Fake Data
        humidity = random.uniform(30, 80) # 30% to 80%
        temp = random.uniform(10, 30) # 10degC to 30degC
        pressure = random.uniform(1000, 2000) # 1000mbar to 2000mbar
        soil_humidity = random.uniform(0, 1) # 1 or 0
    log("=========================================")
    log("Current Humidity:      " + str(humidity) + " %")
    log("Current Temperature:   " + str(temp) + " degC")
    log("Current Air Pressure:  " + str(pressure) + " mbar")
    log("-----------------------------------------")
    log("Current Soil Humidity: " + str(soil_humidity))

    ts = time.time()

    st = datetime.datetime.fromtimestamp(ts).strftime('%H-%M-%S-%d')

    filename = st+".jpg"

    camera.Capture(filename)

    insert_data(humidity, temp, pressure, soil_humidity, filename)

def insert_data(humidity, temperature, pressure, soil_humidity, filename): # Put data into the database
    c.execute("INSERT INTO `data` (humidity, temperature, pressure, soil_humidity, image) VALUES (?, ?, ?, ?, ?)", [humidity, temperature, pressure, soil_humidity, filename])
    conn.commit()
    return c.lastrowid

# TODO: Replace this with a CRON Job
def go():
    while True:
        get_data()

        rowid = c.lastrowid
        c.execute("SELECT * FROM data WHERE id=?", [rowid])
        soil_humidity = c.fetchall()
        soil_humidity = soil_humidity[0][5]
        if soil_humidity > 900:
            water()
        else:
            log("Not watering plant because not over threshold")

        time.sleep(10)

if __name__ == "__main__":
    go()

def log(message):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S %d/%m/%Y')
    print("[" + st + "] ", message)

def water():
    log("== Watering for 5s... ==")
    if os.environ["TEST"] != "y":
        GPIO.output(18, GPIO.HIGH)
        time.sleep(5)
        GPIO.output(18, GPIO.LOW)
    log("== Watered Plant ==")
