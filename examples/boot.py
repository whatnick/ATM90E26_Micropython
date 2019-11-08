import socket
from atm90e26_SPI import *

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('HOT_SPOT', 'HOT_PASS')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

def http_get(url):
    _, _, host, path = url.split('/', 3)
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    while True:
        data = s.recv(100)
        if data:
            print(str(data, 'utf8'), end='')
        else:
            break
    s.close()
	
sck = machine.Pin(5,machine.Pin.OUT)
mosi = machine.Pin(18,machine.Pin.OUT)
miso = machine.Pin(19,machine.Pin.IN)
cs1 = machine.Pin(15,machine.Pin.OUT)
cs2 = machine.Pin(33,machine.Pin.OUT)

do_connect()

spi = machine.SPI(1,baudrate=200000,bits=8,polarity=1,phase=1,firstbit=machine.SPI.MSB,sck=sck,mosi=mosi,miso=miso)

all_ics = [ATM90E26_SPI(spi,cs1),ATM90E26_SPI(spi,cs2)]



while True:
	ic_id = 0
	for energy_ic in all_ics:
		sys_val = energy_ic.GetSysStatus()
		print("Sys Status:",hex(sys_val))
		met_val = energy_ic.GetMeterStatus()
		print("Met Status:",hex(met_val))
		voltage = energy_ic.GetLineVoltage()
		print("Voltage:",voltage)
		current = energy_ic.GetLineCurrent()
		print("Current:",current)
		time.sleep_ms(100)
		power = energy_ic.GetActivePower()
		print("Power:",power)
		url = 
'https://emoncms.local:8080/input/post?json={power'+str(ic_id)+':'+str(power)+'}&apikey=API_KEY'
		http_get(url)
		ic_id += 1
	time.sleep(15)

