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
            
            # Parse device responce and send it 
            parse_result = self.responcse_parser()
            if parse_result:
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

            return True
        else:
            print("ERROR IN RESPONSE")
            return False


    def send_data(self):
        
        self.web_response = requests.get(self.url, json=self.device_vals)
        print("\nWeb Request details:")
        print("-------------------------")
        print("Status code: ", self.web_response.status_code)
        print(self.web_response.json())
        print("-------------------------")





port = 'COM5'
url = 'https://httpbin.org/ip'

dev = Pzem(port, url)
dev.read_vals()