from flask import Flask, render_template, jsonify
from wakeonlan import send_magic_packet
import RPi.GPIO as GPIO
import time
import os


app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

def wake_pc():
    GPIO.output(23, 1)
    # Sleep for 500 milliseconds
    time.sleep(0.5)
    GPIO.output(23, 0)

def kill_pc():
    GPIO.output(23, 1)
    # Sleep for mutliple seconds
    time.sleep(20)
    GPIO.ouput(23, 0)


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/kill")
def kill():
    kill_pc()
    return {"STATUS": "SUCCESS"}


@app.get("/linux")
def launch_linux():
    wake_pc()
    return {"STATUS": "SUCCESS"}


@app.get("/mac")
def launch_macos():
    send_magic_packet("14:98:77:43:2b:97")
    return {"STATUS": "SUCCESS"}


@app.get("/windows")
def launch_windows():
    wake_pc()
    start_time = time.time()
    while time.time() - start_time < 120:
        try:
            press_key(68)  # 68 = F11
        except BrokenPipeError:
            continue
    # press_key(81) # 81 = Down Arrow
    press_key(40) # 40 = Enter
    return {"STATUS": "SUCCESS"}


@app.route("/awake")
def awake():
    hostname = "192.168.0.208"  # Replace this with the IP address of the target computer
    response = os.system("ping -c 1 " + hostname)

    if response == 0:
        return jsonify(True)
    else:
        return jsonify(False)


NULL_CHAR = chr(0)
def press_key(char_nr):
    with open("/dev/hidg0", "rb+") as fd:
        fd.write((NULL_CHAR*2+chr(char_nr)+NULL_CHAR*5).encode())
    with open("/dev/hidg0", "rb+") as fd:
        fd.write((NULL_CHAR*8).encode())


def main():
    app.run(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
