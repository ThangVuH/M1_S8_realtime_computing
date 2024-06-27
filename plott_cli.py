import sys
import time
from pymata4 import pymata4
from python_banyan.banyan_base import BanyanBase
from keypad import Keypad
from dc_motor import DC_motor
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from buffers import CircBuff, FIFO

class Keypad_cli(BanyanBase):
    def __init__(self):
        super(Keypad_cli, self).__init__(process_name='client_keypad')
        self.set_subscriber_topic('status')
        self.run()
    
    def run(self):
        try:
            print("Starting digicode system. Please wait...")
            time.sleep(2)  
            print("Ready for code entry.")
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def incoming_message_processing(self, topic, payload):
        reply = payload['reply']
        if reply == 'reset':
            print("Resetting due to timeout...")
        elif reply == 'incorrect':
            print("Incorrect Code. Try again.")
        elif reply == 'stop':
            print("Stop the machine")
            self.clean_up()
            sys.exit(0)
        elif reply == 'correct':
            print("Code Correct. Access Granted.")
            for _ in range(5):  # Display access signal
                            print(".", end=" ", flush=True)
                            time.sleep(1)
            self.clean_up()
            sys.exit(0)
        else:
            print(reply)

from buffers import CircBuff
class DCmotor_cli(BanyanBase):
    def __init__(self,window_duration = 40, refresh_time = 0.5 ):
        super(DCmotor_cli, self).__init__(process_name='client_DC_motor',
                                                   loop_time=refresh_time,
                                                   receive_loop_idle_addition=self.animate)
        self.buffer_size = window_duration
        self.display_time = int(self.buffer_size/2)
        self.refresh_time = refresh_time 
        self.server_cb = CircBuff(size=self.buffer_size)

        self.set_subscriber_topic('status')
        self.set_subscriber_topic('less')
        self.publish_payload({'buff_sise':self.display_time}, 'request')

        plt.ion()
        self.fig, self.ax = plt.subplots()
        self.run()

    def run(self):
        try:
            self.receive_loop()
        except KeyboardInterrupt:
            self.clean_up()
            sys.exit(0)

    def animate(self):
        data = self.server_cb.read()
        if len(data)>=self.display_time:
            # data = data[-self.display_time:] 
            targ_, t_,curr_ = zip(*data)

            start_time = max(t_) - self.display_time
            indices = [i for i, t in enumerate(t_) if t >= start_time]
            t_, targ_, curr_ = [t_[i] for i in indices], [targ_[i] for i in indices], [curr_[i] for i in indices]
            
            print(f'target:{targ_}at {t_}, size={len(data)}')
            self.ax.clear()

            self.ax.plot(t_, targ_,label='target')
            self.ax.scatter(t_, targ_,label='target')

            self.ax.plot(t_, curr_,label='current')
            self.ax.scatter(t_, curr_,label='target')

            self.ax.legend()
            self.ax.set_ylim([-5, 270])
            self.fig.canvas.draw() 
            self.fig.canvas.flush_events()

            time.sleep(self.refresh_time)
            self.publish_payload({'buff_sise':self.display_time}, 'request')

    def incoming_message_processing(self, topic, payload):
        if topic == 'status':
            ard_val_targ,ard_val_curr, ard_time = payload['val_targ'],payload['val_curr'], float(payload['time'])
            self.server_cb.write((ard_time,ard_val_targ,ard_val_curr))
        elif topic == 'less':
            # time.sleep(3)
            self.publish_payload({'buff_sise':self.display_time}, 'request')


def run_client1(): # Final keypad 2
    Keypad_cli()

def run_client2(): #plot DC motor
    DCmotor_cli()

if __name__ == '__main__':
    run_client2()