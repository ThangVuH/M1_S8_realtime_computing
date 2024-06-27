import sys
from python_banyan.banyan_base import BanyanBase
from pymata4 import pymata4
from buffers import CircBuff, FIFO
import numpy as np
from keypad import Keypad 
from dc_motor import DC_motor
import time
import random

class Keypad_ser(BanyanBase):
    def __init__(self,keypad):
        super(Keypad_ser, self).__init__(process_name='test_server',
                                            loop_time=0.1)
        
        self.keypad_obj = keypad
        # self.run()

    def run(self):
        try:
            self.saved_keypad(self.keypad_obj)
            # self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def verify(self, entered_code):
        if entered_code == Keypad.correct_code:
            self.publish_payload({'reply':"correct"},'status')
            print(f'code confirmation: {entered_code}')
            self.clean_up()
            sys.exit(0)
        elif entered_code == Keypad.finish_code:
            self.publish_payload({'reply':"stop"},'status')
            print(f'code confirmation: {entered_code}')
            self.clean_up()
            sys.exit(0)
        else:
            self.publish_payload({'reply':"incorrect"},'status')
            entered_code = []

    def saved_keypad(self,obj):
        print('start the keypad')
        entered_code = []
        last_key_time = time.time()
        while True:
            key = obj.scan_keypad()
            if key:
                current_time = time.time()
                if current_time - last_key_time > 5:
                    entered_code = []  # Reset if too long between presses
                    self.publish_payload({'reply':"reset"},'status')
                last_key_time = current_time
                self.publish_payload({'reply':f"Key Pressed: {key}"},'status')
                entered_code.append(key)
            if len(entered_code) == 3:
                self.verify(entered_code)


class DCmotor_ser(BanyanBase):
    def __init__(self,obj):
        super(DCmotor_ser, self).__init__(process_name='ser_DC_motor',
                                            loop_time=0.001,
                                            receive_loop_idle_addition=self.get_data)
        
        self.buffer_size = 5
        self.client_fifo = FIFO(win_len=self.buffer_size)
        self.obj = obj

        self.set_subscriber_topic('request')
        
        self.run()

    def run(self):
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        self.buffer_size = payload['buff_sise']
        self.store_data(self.buffer_size)

    def get_data(self):
        self.obj.control_position()
        t, val_target,val_current = self.obj.time,self.obj.target_position, self.obj.current_position
        self.client_fifo.write((t,val_target,val_current))
        print(f'position in:{val_current},target in:{val_target}  at {t} idle')

    def store_data(self, buffer_size):
        data = self.client_fifo.read()
        if len(data)>=buffer_size:
            data = data[-buffer_size:]
            for targ, curr, t in data:
                self.publish_payload({'time': t, 'val_targ': targ, 'val_curr': curr}, 'status')
        else:
            data = self.client_fifo.read()
            time.sleep(2)
            self.publish_payload({'size': len(data)}, 'less')
        print(data, f'size= {len(data)}')


def run_server1(): #Final keypad 
    board =  pymata4.Pymata4()
    keypad = Keypad(board)
    tmp =Keypad_ser(keypad)
    tmp.run()

def run_server2(): #plot DC motor
    board =  pymata4.Pymata4()
    tmp = DC_motor(board)
    tmp1 =DCmotor_ser(tmp)
    tmp1.run()

if __name__ == '__main__':
    # board =  pymata4.Pymata4()
    # keypad = Keypad(board)
    # motor = DC_motor(board)
    run_server2()