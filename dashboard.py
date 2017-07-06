from flask import Flask, render_template, send_from_directory, jsonify
import sqlite3
import time
import datetime
import sense

# Setup SQLite Database
conn = sqlite3.connect("database.db", check_same_thread=False)
c = conn.cursor()

app = Flask(__name__)

@app.route("/")
def dashboard():
    # get latest result from database to display on dashboard
    c.execute("SELECT temperature, pressure, humidity, timestamp, soil_humidity, image FROM `data` ORDER BY timestamp DESC LIMIT 1")
    current = c.fetchone()
    # get all results from the last day to put in the charts
    c.execute("SELECT temperature, pressure, humidity, timestamp, soil_humidity FROM `data` WHERE timestamp >= datetime('now', '-1 day') ORDER BY timestamp ASC")
    history = c.fetchall()
    #log(current)
    # give the html to the browser
    return render_template("dashboard.html.j2", current=current, history=history)

@app.route("/api/manualwater", methods=["POST"])
def manual_water(): # this page is triggered when someone clicks on the manual water button on the dashboard
    sense.water() # this calls the water function in sense.py
    return jsonify({
        "status": "ok"
    }) # this tells the dashboard we have received the message

@app.route("/assets/js/<path:path>") # serve files from the js folder
def send_js(path):
    return send_from_directory("assets/js", path)

@app.route("/assets/css/<path:path>") # serve files from the css folder
def send_css(path):
    return send_from_directory("assets/css", path)

@app.route("/assets/fonts/<path:path>") # serve files from the fonts folder
def send_fonts(path):
    return send_from_directory("assets/fonts", path)

@app.route("/assets/img/<path:path>") # serve files from the images folder
def send_images(path):
    return send_from_directory("assets/img", path)

def log(message):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S %d/%m/%Y')
    print("[" + st + "] ", message)

if __name__ == "__main__":
    app.run()
