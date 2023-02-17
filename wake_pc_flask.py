import subprocess
from flask import Flask, render_template, jsonify
from wakeonlan import send_magic_packet
import RPi.GPIO as GPIO
import time
import os


app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
RELAY_PIN = 23
SERVO_PIN = 18
GPIO.setup(RELAY_PIN, GPIO.OUT)  # Relay
GPIO.setup(SERVO_PIN, GPIO.OUT)  # Servo
PWM = GPIO.PWM(SERVO_PIN, 50)  # PWM Frequency
PWM.start(0)

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
    # Move servo arm to button
    PWM.ChangeDutyCycle(angle_to_percent(25))
    # Wait just a little
    time.sleep(0.5)
    # Reset the arm to its default position
    PWM.ChangeDutyCycle(angle_to_percent(90))
    # Wait just a little
    time.sleep(0.5)
    PWM.ChangeDutyCycle(0)
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
    pc_hostname = "192.168.0.208"  # Replace this with the IP address of the target computer
    mac_hostname = "192.168.0.171"
    pc_result = subprocess.run(f"ping -c 1 {pc_hostname}".split(), stdout=subprocess.PIPE)
    mac_result = subprocess.run(f"ping -c 1 {mac_hostname}".split(), stdout=subprocess.PIPE)

    return jsonify({"PC": not(pc_result.returncode), "MAC": not(bool(mac_result.returncode))})


NULL_CHAR = chr(0)
def press_key(char_nr):
    with open("/dev/hidg0", "rb+") as fd:
        fd.write((NULL_CHAR*2+chr(char_nr)+NULL_CHAR*5).encode())
    with open("/dev/hidg0", "rb+") as fd:
        fd.write((NULL_CHAR*8).encode())

# Set function to calculate percent from angle
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 # Calculate ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


def main():
    app.run(debug=True, host="0.0.0.0")


if __name__ == "__main__":
    main()
