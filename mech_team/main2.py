import time
import RPi.GPIO as GPIO
import datetime
import csv
#from PiPocketGeiger import RadiationWatch
import ms5837
from startUpBMP180 import *
import os
import board
import adafruit_scd30
import sys

class Bar02:
    def __init__(self,i2cbus=1):
        self.sensor = ms5837.MS5837_30BA(i2cbus)
        self.sensor.init()
    def read(self):
        self.sensor.read()
        _data = [self.sensor.pressure(ms5837.UNITS_psi), self.sensor.temperature(ms5837.UNITS_Centigrade), self.sensor.altitude()]
        return _data    

# class HeatingElement:
#     def __init__(self, pin):
#         self.pin = pin
#         GPIO.setup(pin,GPIO.OUT)
#         self.on = False
#     def setHigh(self):
#         self.on = True
#         GPIO.output(self.pin,1)
#     def setLow(self):
#         self.on = False
#         GPIO.output(self.pin,0)

class Sensor:
    def __init__(self, pins):
        self.pins = pins
        for pin in self.pins:
            GPIO.setup(pin,GPIO.OUT)
        def read(self):
            return [GPIO.input(x) for x in self.pins]

def truncate(x):
    try:
        return round(x, 2)
    except:
        return x

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


    current_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_path)
    csv_path = os.path.join(current_path, 'main.csv')
    with open(csv_path, 'a+', newline='') as SENSORS:
        bar02_spam = csv.writer(SENSORS, delimiter=',') #all readings here bar02 was first
        if not(ran_already):
            bar02_spam.writerow(['Date', 'Time', 'psi', 'temperature', 'altitude', 'CO2level', 'relativeHumidity', 'scdTemperature', 'bmp_temperature','bmp_pressure','bmp_altitude'])
            ran_already = True

        try:

            while not (scd.data_available):
                time.sleep(0.25)

            if scd.data_available:
                print("Data Available!")
                C02level = scd.CO2
                scdTemperature = scd.temperature
                relativeHumidity = scd.relative_humidity

                
        except:
            C02level, scdTemperature, relativeHumidity = 'null', 'null', 'null' #read -1 instead of null

        try: 
            
            bar_data = bar02.read()
            #print('bar_data: ', bar_data)
            psi = bar_data[0]
            temperature = bar_data[1]
            altitude = bar_data[2]
        except:
            psi, temperature, altitude = 'null', 'null', 'null'
                
        try:
            bmp_temperature = bmp.get_temp()
            bmp_pressure = bmp.get_pressure()
            bmp_altitude = bmp.get_altitude()
        except:
            bmp_temperature, bmp_pressure, bmp_altitude = 'null', 'null', 'null'

        total_values = [date_var, time_var, psi, temperature, 
                        altitude, C02level, relativeHumidity, 
                        scdTemperature, bmp_temperature, bmp_pressure, bmp_altitude]

        total_values = [truncate(x) for x in total_values]
        print('total_values: ',total_values)
        bar02_spam.writerow(total_values)
        return total_values

########################End function definitions######################
ran_already = False
bar02 = Bar02()
scd = adafruit_scd30.SCD30(board.I2C())
bmp = bmp180(0x77)
GPIO.setmode(GPIO.BCM)

try:
    while True:

        psi, temperature, altitude = 'null', 'null', 'null'
        CO2level, scdTemperature, relativeHumidity = 'null', 'null', 'null'
        bmp_temperature, bmp_pressure, bmp_altitude = 'null', 'null', 'null'
        data = read_all_sensors()
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting the program.")
    GPIO.cleanup()  # Clean up GPIO pins if you've been using them
    sys.exit(0)


# heating = HeatingElement(37)





# attempt at heating element, suspended for mosfet and buck converter research
    
#     temp_threshold_low = 30 # 17
#     temp_threshold_high = 31 # 25
#     if float(data[3]) < temp_threshold_low:
#         heating.setHigh()
#         print("ksjdfskf")
#     if float(data[3]) > temp_threshold_high:
#         heating.setLow()
#         print("djfslkdfj")
#     print(data[3])
#     print(heating.on)
#     time.sleep(1)
