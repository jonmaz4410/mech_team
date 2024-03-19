import time
import RPi.GPIO as GPIO
import datetime
import csv
#from PiPocketGeiger import RadiationWatch
from scd30_i2c import SCD30
#sleep(30)

#open('/home/james/Desktop/test1.txt','w+')
import ms5837
#from time import sleep

from startUpBMP180 import *


#bar02 class
class Bar02:
    def __init__(self,i2cbus=1):
        self.sensor = ms5837.MS5837_30BA(i2cbus)
        self.sensor.init()
    def read(self):
        self.sensor.read()
        _data = [self.sensor.pressure(ms5837.UNITS_psi), self.sensor.temperature(ms5837.UNITS_Centigrade), self.sensor.altitude()]
        return _data
    
#scd30 class
#timeout error here
GPIO.setmode(GPIO.BCM)

class HeatingElement:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin,GPIO.OUT)
        self.on = False
    def setHigh(self):
        self.on = True
        GPIO.output(self.pin,1)
    def setLow(self):
        self.on = False
        GPIO.output(self.pin,0)


class Sensor:
    def __init__(self, pins):
        self.pins = pins
        for pin in self.pins:
            GPIO.setup(pin,GPIO.OUT)
        def read(self):
            return [GPIO.input(x) for x in self.pins]

#scd30 = Sensor([3,5]) #Grove hookup with i2c at 3(SDA) and 5(SCL)
scd30 = SCD30()
scd30.set_measurement_interval(2)
scd30.start_periodic_measurement()
bmp = bmp180(0x77)
#cause of timeout error must be above

def truncate(x):
    try:
        return round(x, 2)
    except:
        return x
#geieger class

#bmp180 class
ran_already = False
#all sensors
def read_all_sensors():
    global ran_already
    date_var, time_var, psi, temperature, altitude, C02level, relativeHumidity, scdTemperature = 'null', 'null', 'null', 'null', 'null', 'null', 'null', 'null'
    timeStart = datetime.datetime.now()
    #print(timeStart)
    #print(type(timeStart))
    date_and_time = str(timeStart)

    dt_split = date_and_time.split(' ')
    date_var = dt_split[0]
    time_var = dt_split[1]
    
    with open('/home/james/Desktop/sensor_test/main.csv', 'a+', newline='') as SENSORS:
        bar02_spam = csv.writer(SENSORS, delimiter=',') #all readings here bar02 was first
        if not(ran_already):
            bar02_spam.writerow(['Date', 'Time', 'psi', 'temperature', 'altitude', 'CO2level', 'relativeHumidity', 'scdTemperature', 'bmp_temperature','bmp_pressure','bmp_altitude'])
            ran_already = True
        #ran_already = True
        # Grab timestamp
        #scdTemperature, C02level, relativeHumidity = scd_function() # return scdTemperature, C02level, relativeHumidity

        #bar02 read then write to csv
        try: 
            bar02 = Bar02()
            bar_data = bar02.read()
            #print('bar_data: ', bar_data)
            psi = bar_data[0]
            temperature = bar_data[1]
            altitude = bar_data[2]
        except:
            psi, temperature, altitude = 'null', 'null', 'null'

        #grove scd30 read then write to csv
        
        # Grab timestamp
        #scdTemperature, C02level, relativeHumidity = scd_function() # return scdTemperature, C02level, relativeHumidity
        try: 
            scd30 = SCD30()
            scd30_data = scd30.read_measurement()
            #print('scd30_data: ', scd30_data)
            C02level = scd30_data[0]
            scdTemperature = scd30_data[1]
            relativeHumidity = scd30_data[2]


        except:
            C02level, scdTemperature, relativeHumidity = 'null', 'null', 'null' #read -1 instead of null

        try:
            bmp_temperature = bmp.get_temp()
            bmp_pressure = bmp.get_pressure()
            bmp_altitude = bmp.get_altitude()
        except:
            bmp_temperature, bmp_pressure, bmp_altitude = 'null', 'null', 'null'

#ground station on campus talk to EE

        #psi, temperature, altitude = bar02_function()
        # can add alert after except from fail kindfa like the null read
        
        total_values = [date_var, time_var, psi, temperature, altitude, C02level, relativeHumidity, scdTemperature, bmp_temperature, bmp_pressure, bmp_altitude]
        #our_team(total_values)
        total_values = [truncate(x) for x in total_values]
        print('total_values: ',total_values)
        bar02_spam.writerow(total_values)
        return total_values


heating = HeatingElement(37)


run_flag = True
while run_flag:

    '''
attempt at heating element, suspended for mosfet and buck converter research
    data = read_all_sensors()
    temp_threshold_low = 30 # 17
    temp_threshold_high = 31 # 25
    if float(data[3]) < temp_threshold_low:
        heating.setHigh()
        print("ksjdfskf")
    if float(data[3]) > temp_threshold_high:
        heating.setLow()
        print("djfslkdfj")
    print(data[3])
    print(heating.on)
    time.sleep(1)
    '''