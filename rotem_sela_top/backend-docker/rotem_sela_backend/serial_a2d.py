import queue
import serial
import struct
from time import sleep
    

class SerialA2D():
    def __init__(self):
        self.ser = serial.Serial ("/dev/ttyS0", 115200)    #Open port with baud rate
        self.values = [0,0,0,0,0,0,0,0,0,0]

    def listen(self):    
        while True:
                if(self.ser.in_waiting):
                    calc_checksum = 0
                    received_checksum = 0
                    received_data = self.ser.read(1)              #read serial port
                    # print("Received data !!", received_data)
                    if received_data[0] == 0xaa:
                        received_data = self.ser.read(1)
                           
                        if received_data[0] == 0xde:
                            received_data = self.ser.read(1)    
                            if received_data[0] == 21:
                                received_data = self.ser.read(21)
                                self.values = list(struct.unpack('10h', received_data[0:20]))
                                calc_checksum = self.CalcChecksum(received_data)
                                received_checksum = received_data[20]
                            
                                if(calc_checksum != received_checksum):
                                    continue
                                # else:
                                #     print(self.values) 
                            else:
                                continue
                        else:
                            continue
                    else:
                        continue
    
    def CalcChecksum(self, values):
        ret_val = 0xaa + 0xde + 21
        for i in range(20):
            ret_val += values[i]
        ret_val = (~ret_val)&0xFF
        return ret_val            

if __name__ == "__main__":
    x = SerialA2D()
    x.listen()