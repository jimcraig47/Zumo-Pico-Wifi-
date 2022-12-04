"""
Zumo Tracked Robot
Raspberry Pi Pico W
TB6612FNG motor driver
wifi_creds on board
"""


import network
import socket
from time import sleep
import machine
import wifi_creds
from machine import Pin, PWM

ipConnect_led = Pin(16, Pin.OUT)
          
AIN1 = Pin(12, Pin.OUT)
AIN2 = Pin(13, Pin.OUT)
PWMA = PWM(Pin(15))

BIN1 = Pin(10, Pin.OUT)
BIN2 = Pin(9, Pin.OUT)
PWMB = PWM(Pin(14))

STBY = Pin(11 , Pin.OUT)

PWMA.freq(1000)
PWMB.freq(1000)

def move_forward():
    PWMA.duty_u16(65025)
    PWMB.duty_u16(65025)
    STBY.value(1)
    AIN1.value(1)
    AIN2.value(0)
    BIN1.value(1)
    BIN2.value(0)
   
def move_backward():
    PWMA.duty_u16(65025)
    PWMB.duty_u16(65025)
    STBY.value(1)
    AIN1.value(0)
    AIN2.value(1)
    BIN1.value(0)
    BIN2.value(1)
        
def move_left():
    PWMA.duty_u16(32512)
    PWMB.duty_u16(32512)
    STBY.value(1)
    AIN1.value(0)
    AIN2.value(1)
    BIN1.value(1)
    BIN2.value(0)
    sleep(0.4)
    move_stop()
        
def move_right():
    PWMA.duty_u16(32512)
    PWMB.duty_u16(32512)
    STBY.value(1)
    AIN1.value(1)
    AIN2.value(0)
    BIN1.value(0)
    BIN2.value(1)
    sleep(0.4)
    move_stop()
        
def move_stop():
    STBY.value(0)
    
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(wifi_creds.ssid, wifi_creds.password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    
    #led on indicates ip connection good(I used a blue led)
    if wlan.isconnected() == True:
        ipConnect_led.value(1)
    else:
        ipConnect_led.value(0)
    return ip
 
    
def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage():
    #Template HTML
    html = f"""
   <!DOCTYPE html>
<html>

<head>
    <title>WiFi Robot Control</title>
</head>

<body bgcolor="black">
    <center><b>
            <h4 style="color:red;"><b>WiFi Robot Control</b></h4>
            <h5 style="color:aqua"><i><b>motor control</b></i></h5>

            <form action="./forward">
                <input type="submit" value="Forward" style= "height:120px; width:120px; background-color: grey; color: chartreuse;  font-size: 20px; border-radius: 8px;" />
            </form>
            <table>
                <tr>
                    <td>
                        <form action="./left">
                            <input type="submit" value="Left" style= "height:120px; width:120px; background-color: grey; color: chartreuse;  font-size: 20px; border-radius: 8px;" />
                        </form>
                    </td>
                    <td>
                        <form action="./stop">
                            <input type="submit" value="Stop" style= "height:120px; width:120px; background-color: grey; color: red;  font-size: 20px; border-radius: 8px;" />
                        </form>
                    </td>
                    <td>
                        <form action="./right">
                            <input type="submit" value="Right" style= "height:120px; width:120px; background-color: grey; color: chartreuse;  font-size: 20px; border-radius: 8px;" />
                        </form>
                    </td>
                </tr>
            </table>
            <form action="./back">
                <input type="submit" value="Back" style= "height:120px; width:120px; background-color: grey; color: chartreuse;  font-size: 20px; border-radius: 8px;" />
            </form>
            <br />
            <h5 style="color:aqua"><i><b>lights</b></i></h5>
            <table>
                <tr>
                    <td>
                        <form action="./lightson">
                            <input type="submit" value="On" style= "height:120px; width:120px; background-color: grey; color: chartreuse;  font-size: 20px; border-radius: 8px;" />
                        </form>
                    </td>
                    <td>
                        <form action="./lightsoff">
                            <input type="submit" value="Off" style= "height:120px; width:120px; background-color: grey; color: red;  font-size: 20px; border-radius: 8px;" />
                        </form>
                    </td>
                </tr>
            </table>
</body>
<h5 style="color:red;"><b><i>Old Monkey Robotix</i></b></h5>
</html>
            """
    return str(html)

def serve(connection):
    #Start web server
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/forward?':
            move_forward()
        elif request =='/left?':
            move_left()
        elif request =='/stop?':
            move_stop()
        elif request =='/right?':
            move_right()
        elif request =='/back?':
            move_backward()
        html = webpage()
        client.send(html)
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()

    
