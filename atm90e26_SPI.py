import machine
import time

SysStatus = 0x01 #System Status

sck = machine.Pin(5,machine.Pin.OUT)
mosi = machine.Pin(18,machine.Pin.OUT)
miso = machine.Pin(19,machine.Pin.IN)
cs1 = machine.Pin(15,machine.Pin.OUT)
cs2 = machine.Pin(33,machine.Pin.OUT)

spi = machine.SPI(1,baudrate=200000,bits=8,polarity=1,phase=1,firstbit=machine.SPI.MSB,sck=sck,mosi=mosi,miso=miso)

while True:
	cs2.value(0)
	spi.write(bytearray([172]))
	time.sleep_us(4)
	val = spi.read(2)
	print(val)
	cs2.value(1)
	time.sleep_ms(100)