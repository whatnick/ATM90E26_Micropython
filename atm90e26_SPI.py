import machine
import time
import struct

SoftReset = 0x00 # Software Reset
SysStatus = 0x01 # System Status
FuncEn = 0x02 # Function Enable
SagTh = 0x03 # Voltage Sag Threshold
SmallPMod = 0x04 # Small-Power Mode
LastData = 0x06 # Last Read/Write SPI/UART Value
LSB = 0x08 # RMS/Power 16-bit LSB
CalStart = 0x20 # Calibration Start Command
PLconstH = 0x21 # High Word of PL_Constant
PLconstL = 0x22 # Low Word of PL_Constant
Lgain = 0x23 # L Line Calibration Gain
Lphi = 0x24 # L Line Calibration Angle
Ngain = 0x25 # N Line Calibration Gain
Nphi = 0x26 # N Line Calibration Angle
PStartTh = 0x27 # Active Startup Power Threshold
PNolTh = 0x28 # Active No-Load Power Threshold
QStartTh = 0x29 # Reactive Startup Power Threshold
QNolTh = 0x2A # Reactive No-Load Power Threshold
MMode = 0x2B # Metering Mode Configuration
CSOne = 0x2C # Checksum 1
AdjStart = 0x30 # Measurement Calibration Start Command
Ugain = 0x31 # Voltage rms Gain
IgainL = 0x32 # L Line Current rms Gain
IgainN = 0x33 # N Line Current rms Gain
Uoffset = 0x34 # Voltage Offset
IoffsetL = 0x35 # L Line Current Offset
IoffsetN = 0x36 # N Line Current Offse
PoffsetL = 0x37 # L Line Active Power Offset
QoffsetL = 0x38 # L Line Reactive Power Offset
PoffsetN = 0x39 # N Line Active Power Offset
QoffsetN = 0x3A # N Line Reactive Power Offset
CSTwo = 0x3B # Checksum 2
APenergy = 0x40 # Forward Active Energy
ANenergy = 0x41 # Reverse Active Energy
ATenergy = 0x42 # Absolute Active Energy
RPenergy = 0x43 # Forward (Inductive) Reactive Energy
Rnenerg = 0x44 # Reverse (Capacitive) Reactive Energy
Rtenergy = 0x45 # Absolute Reactive Energy
EnStatus = 0x46 # Metering Status
Irms = 0x48 # L Line Current rms
Urms = 0x49 # Voltage rms
Pmean = 0x4A # L Line Mean Active Power
Qmean = 0x4B # L Line Mean Reactive Power
Freq = 0x4C # Voltage Frequency
PowerF = 0x4D # L Line Power Factor
Pangle = 0x4E # Phase Angle between Voltage and L Line Current
Smean = 0x4F # L Line Mean Apparent Power
IrmsTwo = 0x68 # N Line Current rms
PmeanTwo = 0x6A # N Line Mean Active Power
QmeanTwo = 0x6B # N Line Mean Reactive Power
PowerFTwo = 0x6D # N Line Power Factor
PangleTwo = 0x6E # Phase Angle between Voltage and N Line Current
SmeanTwo = 0x6F # N Line Mean Apparent Power


class ATM90E26_SPI:
	
	'''       
	spi - hardware or software SPI implementation
	cs - Chip Select pin
	'''
	def __init__(self,spi,cs):
		self.spi = spi
		self.cs = cs
		self.init_atm90()
	'''
	rw - True - read, False - write
	address - register to operate
	val - value to write (if any)
	'''
	def comm_atm90(self,RW,address,val):
		#switch MSB and LSB of value
		buf = bytearray(2)
		otw_val = struct.pack('>H',val)
		#Set read write flag
		address|=RW<<7
		self.cs.value(False)
		time.sleep_us(10)
		self.spi.write(bytearray([address]))
		''' Must wait 4 us for data to become valid '''
		time.sleep_us(4)

		#Read data
		#Do for each byte in transfer
		if(RW):
			buf = self.spi.read(2)
		else:
			self.spi.write(otw_val)			 # write all the bytes
		self.cs.value(1)
		return int.from_bytes(buf,'big')

	def init_atm90(self):
		self.comm_atm90(False,SoftReset,0x789A)	#Perform soft reset
		self.comm_atm90(False,FuncEn,0x0030)	#Voltage sag irq=1, report on warnout pin=1, energy dir change irq=0
		self.comm_atm90(False,SagTh,0x1F2F)	#Voltage sag threshhold
		
		#Set metering calibration values
		self.comm_atm90(False,CalStart,0x5678) #Metering calibration startup command. Register 21 to 2B need to be set
		self.comm_atm90(False,PLconstH,0x00B9) #PL Constant MSB
		self.comm_atm90(False,PLconstL,0xC1F3) #PL Constant LSB
		self.comm_atm90(False,Lgain,0x1D39)   #Line calibration gain
		self.comm_atm90(False,Lphi,0x0000) #Line calibration angle
		self.comm_atm90(False,PStartTh,0x08BD) #Active Startup Power Threshold
		self.comm_atm90(False,PNolTh,0x0000) #Active No-Load Power Threshold
		self.comm_atm90(False,QStartTh,0x0AEC) #Reactive Startup Power Threshold
		self.comm_atm90(False,QNolTh,0x0000) #Reactive No-Load Power Threshold
		self.comm_atm90(False,MMode,0x9422) #Metering Mode Configuration. All defaults. See pg 31 of datasheet.
		self.comm_atm90(False,CSOne,0x4A34) #Write CSOne, as self calculated
		
		print("Checksum 1:")
		print(hex(self.comm_atm90(True,CSOne,0x0000))) #Checksum 1. Needs to be calculated based off the above values.
		
		
		#Set measurement calibration values
		self.comm_atm90(False,AdjStart,0x5678) #Measurement calibration startup command, registers 31-3A
		self.comm_atm90(False,Ugain,0xD464)    #Voltage rms gain
		self.comm_atm90(False,IgainL,0x6E49)   #L line current gain
		self.comm_atm90(False,Uoffset,0x0000)  #Voltage offset
		self.comm_atm90(False,IoffsetL,0x0000) #L line current offset
		self.comm_atm90(False,PoffsetL,0x0000) #L line active power offset
		self.comm_atm90(False,QoffsetL,0x0000) #L line reactive power offset
		self.comm_atm90(False,CSTwo,0xD294) #Write CSTwo, as self calculated
		
		print("Checksum 2:")
		print(hex(self.comm_atm90(True,CSTwo,0x0000)))    #Checksum 2. Needs to be calculated based off the above values.
		
		self.comm_atm90(False,CalStart,0x8765) #Checks correctness of 21-2B registers and starts normal metering if ok
		self.comm_atm90(False,AdjStart,0x8765) #Checks correctness of 31-3A registers and starts normal measurement  if ok
		
		systemstatus = self.GetSysStatus()
		
		if (systemstatus&0xC000):
			#checksum 1 error
			print("Checksum 1 Error!!")
		if (systemstatus&0x3000):
			#checksum 2 error
			print("Checksum 2 Error!!")

	def GetSysStatus(self):
		return self.comm_atm90(True,SysStatus,0x0000)
			

	def GetLineVoltage(self):
		voltage = self.comm_atm90(True,Urms,0xFFFF)
		return voltage/100.0


	def GetMeterStatus(self):
	  return self.comm_atm90(True,EnStatus,0xFFFF)


	def GetLineCurrent(self):
		current = self.comm_atm90(True,Irms,0xFFFF)
		return current/1000.0


	def GetActivePower(self):
		apower = self.comm_atm90(True,Pmean,0xFFFF) #Complement, MSB is signed bit
		return double(apower)


	def GetFrequency(self):
		freq = self.comm_atm90(True,Freq,0xFFFF)
		return freq/100.0


	def GetPowerFactor(self):
		pf = self.comm_atm90(True,PowerF,0xFFFF) #MSB is signed bit
		#if negative
		if(pf&0x8000):
			pf=(pf&0x7FFF)*-1
		
		return pf/1000.0


	def GetImportEnergy(self):
		#Register is cleared after reading
		ienergy = self.comm_atm90(True,APenergy,0xFFFF)
		return ienergy*0.0001 #returns kWh if PL constant set to 1000imp/kWh


	def GetExportEnergy(self):
		#Register is cleared after reading
		eenergy = self.comm_atm90(True,ANenergy,0xFFFF)
		return eenergy*0.0001 #returns kWh if PL constant set to 1000imp/kWh
	

sck = machine.Pin(5,machine.Pin.OUT)
mosi = machine.Pin(18,machine.Pin.OUT)
miso = machine.Pin(19,machine.Pin.IN)
cs1 = machine.Pin(15,machine.Pin.OUT)
cs2 = machine.Pin(33,machine.Pin.OUT)

spi = machine.SPI(1,baudrate=200000,bits=8,polarity=1,phase=1,firstbit=machine.SPI.MSB,sck=sck,mosi=mosi,miso=miso)

energy_ic = ATM90E26_SPI(spi,cs2)

while True:
	val = energy_ic.GetSysStatus()
	print(hex(val))
	voltage = energy_ic.GetLineVoltage()
	print(voltage)
	time.sleep_ms(100)