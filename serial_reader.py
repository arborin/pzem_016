import serial
import time
import binascii
import re
import requests
import json


class Pzem:

    read_command = [0xF8,0x04,0x00,0x00,0x00,0x0A,0x64,0x64]
    ser = None
    url = None
    device_response = None
    web_response = None
    device_vals = {
        'voltage': 0,
        'current': 0,
        'power': 0,
        'energy': 0,
        'freq': 0,
        'pf': 0,
    }


    def __init__(self, comport, url):
        self.url = url

        try:
            self.ser = serial.Serial(comport, 9600, timeout=0.5)
        except Exception as e:
            print("Serial communication error: {}".format(str(e)))

    
    def print_vals(self):
        print("="*150)
        print(self.device_response)
        print("="*150)
        print("\nParsed values")
        print("-------------------------")
        for key in self.device_vals.keys():
            print("{}:{}{}".format(key.capitalize(), '\t', self.device_vals[key]))
        print("-------------------------")


    def close_serial(self):
        self.ser.close()


    def read_vals(self):
        if self.ser:
            self.ser.write(self.read_command)
            self.device_response = self.ser.readline().hex()
            
            self.responcse_parser()
            self.print_vals()
            self.send_data()


    def responcse_parser(self):
        if len(str(self.device_response)) == 50:
            self.device_response = re.findall('..', self.device_response)
            voltage = self.device_response[3] + self.device_response[4]
            voltage = int(voltage, 16)
            self.device_vals['voltage'] = voltage/10 
            
            current = self.device_response[5] + self.device_response[6]
            current = int(current, 16)
            self.device_vals['current'] = float(current/1000) 

            power = self.device_response[7] + self.device_response[8] + self.device_response[9] + self.device_response[10]
            power = int(power, 16)
            self.device_vals['power'] = float(power) / 10

            energy = self.device_response[11] + self.device_response[12] + self.device_response[13] + self.device_response[14]
            self.device_vals['energy'] = int(energy, 16)

            freq = self.device_response[15] + self.device_response[16] + self.device_response[17] + self.device_response[18]
            freq = int(freq, 16)
            self.device_vals['freq'] = float(freq/10)

            pf = self.device_response[19] + self.device_response[20]
            pf = int(pf, 16)
            self.device_vals['pf'] = float(pf) / 100

        else:
            print("ERROR IN RESPONSE")
            return False


    def send_data(self):
        
        self.web_response = requests.post(self.url, json=self.device_vals)
        print("\nWeb Request details:")
        print("-------------------------")
        print("Status code: ", self.web_response.status_code)
        print(self.web_response.json())





port = 'COM5'
url = 'example_url.com'

dev = Pzem(port, url)
dev.read_vals()








# ser = serial.Serial('COM5', 9600, timeout=0.5)
# print(ser)
# time.sleep(0.1)

# run = True

# while run:
#     # READ VALUES FROM DEVICE
#     command = "\xf8\x04\x00\x00\x00\x0a\x64\x64"
#     ser.write(serial.to_bytes([0xF8,0x04,0x00,0x00,0x00,0x0A,0x64,0x64]))

#     # GET RESPONSE
#     response = ser.readline().hex()
#     print(type(response))
#     print(response)
    
#     # SPLIT STING INTO LIST
#     response_vals = re.findall('..', response)
#     print(response_vals)
    

#     if len(l)>20:
#         voltage = l[3] + l[4]
#         voltage = int(voltage, 16)
#         print("Voltage:\t{} V".format(float(voltage)/10))

#         current = l[5] + l[6]
#         current = int(current, 16)
#         print("Current:\t{} A".format(float(current)/1000))

#         power = l[7] + l[8] + l[9] + l[10]
#         power = int(power, 16)
#         print("Power:\t{} W".format(float(power)/10))

#         energy = l[11] + l[12] + l[13] + l[14]
#         energy = int(energy, 16)
#         print("Energy:\t{} Wh".format(float(energy)))

#         freq = l[15] + l[16] + l[17] + l[18]
#         freq = int(freq, 16)
#         print("Frequency:\t{} Hz".format(freq/10))

#         pf = l[19] + l[20]
#         pf = int(pf, 16)
#         print("Power Factor:\t{}".format(float(pf)/100))

#         print("\n\n\n")
#         time.sleep(2)

# ser.close()