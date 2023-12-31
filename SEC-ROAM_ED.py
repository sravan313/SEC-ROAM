#!/usr/bin/env python3

""" This program sends a response whenever it receives the "INF" """

# Copyright 2018 Rui Silva.
#
# This file is part of rpsreal/pySX127x, fork of mayeranalytics/pySX127x.
#
# pySX127x is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pySX127x is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You can be released from the requirements of the license by obtaining a commercial license. Such a license is
# mandatory as soon as you develop commercial activities involving pySX127x without disclosing the source code of your
# own applications, or shipping pySX127x with a closed source product.
#
# You should have received a copy of the GNU General Public License along with pySX127.  If not, see
# <http://www.gnu.org/licenses/>.

import random
import time, base64, sys
from Crypto.Cipher import AES
from SX127x.constants import add_lookup, MODE, BW, CODING_RATE, GAIN, PA_SELECT, PA_RAMP, MASK, REG
from SX127x.LoRa import set_bit, getter, setter

# Use BOARD 1
from SX127x.LoRa import LoRa
from SX127x.board_config import BOARD
# Use BOARD 2 (you can use BOARD1 and BOARD2 at the same time)
#from SX127x.LoRa import LoRa2 as LoRa
#from SX127x.board_config import BOARD2 as BOARD


BOARD.setup()
BOARD.reset()


class mylora(LoRa):
    def __init__(self, verbose=False):
        super(mylora, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.p = 101111    # p
        self.g = 76543 # g
        self.b = 0
        self.y = 0
        self.counter = 0

    def on_rx_done(self):
        rx_time = time.time()
        decoded = ''
        BOARD.led_on()
        #print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True )
        
        mens=payload[:-1] #to discard \xff\xff\x00\x00 and \x00 at the end
        mens=bytes(mens).decode("utf-8",'ignore')
        '''cipher = AES.new(self.key)
        decodemens=base64.b64decode(mens)
        decoded = cipher.decrypt(decodemens)
        decoded = bytes(decoded).decode("utf-8",'ignore')'''
        print ("\n== RECEIVED: ", mens)
        mens = mens.replace(" ", "")
        a = int(mens)
        key = pow(a,self.b) % self.p
        #print("RX_TIME = ", rx_time)
        #print("Type of Decoded", type(decoded))
        #print("Length of Decoded", len(decoded))
        
        BOARD.led_off()
        #if len(decoded)==16:
        if len(mens)!= 0: 
        #if decoded=="INF             ":
            #print("\nReceived data, going to send ACK\n")
            time.sleep(4)

            msg_text = str(self.y)
            while (len(msg_text)%16 != 0):
                msg_text = msg_text + ' '
            '''cipher = AES.new(self.key)
            encoded = base64.b64encode(cipher.encrypt(msg_text))'''
            #print("TYPE OF DATA RECEIVED ",type(encoded))
            #print("Length OF DATA RECEIVED ",len(encoded))
            res = bytes(msg_text, 'utf-8')
            lista=list(res)
            lista.insert(0,0)
            lista.insert(0,0)
            lista.insert(0,255)
            lista.insert(0,255)
            lista.append(0)
            #print("Length LISTA ",len(lista))
            self.write_payload(lista)
            #self.write_payload([255, 255, 0, 0, 68, 65, 84, 65, 32, 82, 65, 83, 80, 66, 69, 82, 82, 89, 32, 80, 73, 0]) # Send DATA RASPBERRY PI
            self.set_mode(MODE.TX)
            print( "\nNode 2 Sends Over Public Chanel: " , msg_text)
            print( "\n         Node 2 have the Secret: ", key)
            
        time.sleep(3)
        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        print("\nTxDone")
        print(self.get_irq_flags())

    def on_cad_done(self):
        print("\non_CadDone")
        print(self.get_irq_flags())

    def on_rx_timeout(self):
        print("\non_RxTimeout")
        print(self.get_irq_flags())

    def on_valid_header(self):
        print("\non_ValidHeader")
        print(self.get_irq_flags())

    def on_payload_crc_error(self):
        print("\non_PayloadCrcError")
        print(self.get_irq_flags())

    def on_fhss_change_channel(self):
        print("\non_FhssChangeChannel")
        print(self.get_irq_flags())

    def start(self):          
        while True:
            if (self.counter == 0):
                self.b = random.randint(0,self.p-1) # a
                self.y = pow(self.g,self.b) % self.p
                print( "\nPublicly Shared Variables:")
                print( "    Publicly Shared Prime : " , self.p)
                print( "    Publicly Shared Base  : " , self.g)
                print( "    Node 2 Public Key     : " , self.y)
                print( "\nNode 2 Private Key  ------> " , self.b)
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT) # Receiver mode
            while True:
                pass;
            

lora = mylora(verbose=False)

#     Slow+long range  Bw = 125 kHz, Cr = 4/8, Sf = 4096chips/symbol, CRC on. Power 13 dBm
lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
lora.set_bw(BW.BW125)
lora.set_coding_rate(CODING_RATE.CR4_8)
lora.set_spreading_factor(12)
lora.set_rx_crc(True)
#lora.set_lna_gain(GAIN.G1)
#lora.set_implicit_header_mode(False)
lora.set_low_data_rate_optim(True)

#  Medium Range  Defaults after init are 434.0MHz, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on Power 13 dBm
#lora.set_pa_config(pa_select=1)


assert(lora.get_agc_auto_on() == 1)

try:
    print("START")
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("Exit")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("Exit")
    lora.set_mode(MODE.SLEEP)
BOARD.teardown()
