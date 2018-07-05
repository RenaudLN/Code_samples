# -*- coding: utf-8 -*-
"""
@author: Renaud Laine

This is the user interface to use the Rfoil Thread described in Rfoil_parallel2

"""

from Rfoil_parallel2 import Rfoil
import tkinter as tk
import re
from threading import RLock
import os
import time, datetime

lock = RLock()

class GUI(tk.Frame):

    def __init__(self, window, **kwargs):
        tk.Frame.__init__(self, window, **kwargs)
        self.profiles = []
        self.reynolds = []
        self.mach = tk.DoubleVar()
        self.mach.set(0.1)
        self.angle_max = tk.DoubleVar()
        self.angle_max.set(20)
        self.angle_step = tk.DoubleVar()
        self.angle_step.set(0.5)
        self.tries_max = tk.IntVar()
        self.tries_max.set(5)
        self.root_directory = tk.StringVar()
        self.root_directory.set('Polars')
        self.cmd = tk.StringVar()
        self.cmd.set('C:/rFoil/rfoil01.exe')
        self.max_running = tk.IntVar()
        self.max_running.set(2)
        self.profiles_string = tk.StringVar()
        self.profiles_string.set('Naca0018')
        self.reynolds_string = tk.StringVar()
        self.reynolds_string.set('1e5 5e5 1e6 5e6 1e7 5e7')
        self.button_text = tk.StringVar()
        self.button_text.set('Calculate polars')

        self.grid()

        self.rfoil_path_label = tk.Label(self, text = 'Rfoil path: ', font = ("Times", 10,"bold"))
        self.rfoil_path_label.grid(row = 0, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.rfoil_path_entry = tk.Entry(self, width = 100, textvariable = self.cmd)
        self.rfoil_path_entry.grid(row = 0, column = 1)
        self.rootdir_label = tk.Label(self, text = 'Root directory: ', font = ("Times", 10,"bold"))
        self.rootdir_label.grid(row = 1, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.rootdir_entry = tk.Entry(self, width = 100, textvariable = self.root_directory)
        self.rootdir_entry.grid(row = 1, column = 1)
        self.profiles_label = tk.Label(self, text = 'Profiles: ', font = ("Times", 10,"bold"))
        self.profiles_label.grid(row = 2, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.profiles_entry = tk.Entry(self, width = 100, textvariable = self.profiles_string)
        self.profiles_entry.grid(row = 2, column = 1)
        self.reynolds_label = tk.Label(self, text = 'Reynolds: ', font = ("Times", 10,"bold"))
        self.reynolds_label.grid(row = 3, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.reynolds_entry = tk.Entry(self, width = 100, textvariable = self.reynolds_string)
        self.reynolds_entry.grid(row = 3, column = 1)
        self.mach_label = tk.Label(self, text = 'Mach: ', font = ("Times", 10,"bold"))
        self.mach_label.grid(row = 4, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.mach_entry = tk.Entry(self, width = 100, textvariable = self.mach)
        self.mach_entry.grid(row = 4, column = 1)
        self.angle_max_label = tk.Label(self, text = 'Angle max: ', font = ("Times", 10,"bold"))
        self.angle_max_label.grid(row = 5, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.angle_max_entry = tk.Entry(self, width = 100, textvariable = self.angle_max)
        self.angle_max_entry.grid(row = 5, column = 1)
        self.angle_step_label = tk.Label(self, text = 'Angle step: ', font = ("Times", 10,"bold"))
        self.angle_step_label.grid(row = 6, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.angle_step_entry = tk.Entry(self, width = 100, textvariable = self.angle_step)
        self.angle_step_entry.grid(row = 6, column = 1)
        self.tries_max_label = tk.Label(self, text = 'Tries max: ', font = ("Times", 10,"bold"))
        self.tries_max_label.grid(row = 7, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.tries_max_entry = tk.Entry(self, width = 100, textvariable = self.tries_max)
        self.tries_max_entry.grid(row = 7, column = 1)
        self.max_running_label = tk.Label(self, text = 'Max running: ', font = ("Times", 10,"bold"))
        self.max_running_label.grid(row = 8, column = 0, sticky = tk.W, padx = 10, pady = 5)
        self.max_running_entry = tk.Entry(self, width = 100, textvariable = self.max_running)
        self.max_running_entry.grid(row = 8, column = 1)
        self.run_button = tk.Button(self, textvariable = self.button_text, command = self.launch)
        self.run_button.grid(row = 9, column = 0, columnspan = 2)

    def get_profiles(self):
        self.profiles = re.split('[,; ]+', self.profiles_string.get())

    def get_reynolds(self):
        self.reynolds = re.split('[,; ]+', self.reynolds_string.get())
        
    def launch(self):
        self.get_profiles()
        self.get_reynolds()
        if self.root_directory.get() and not os.path.exists(self.root_directory.get()):
            os.mkdir(self.root_directory.get())
        for profile in self.profiles:
            profile = profile.capitalize()
            ###Make some room for the incoming polars
            polar_directory = os.path.join(self.root_directory.get(), profile)
            if not os.path.exists(polar_directory):
                os.mkdir(polar_directory)
            print('Profile: ' + profile)
            now = datetime.datetime.now()
            log_file = profile + '.log'
            with lock:
                log = open(os.path.join(polar_directory, log_file), 'a')
                log.write(now.strftime("\n----- %Y-%m-%d %H:%M -----\n"))
                log.close()
            threads = [None for i in range(len(self.reynolds))]
            for i, Re in enumerate(self.reynolds):
                threads[i] = Rfoil(cmd = self.cmd.get(), rootdir = self.root_directory.get(),
                                   profile = profile, re = Re, mach = self.mach.get(),
                                   angle_max = self.angle_max.get(), angle_step = self.angle_step.get(),
                                   tries_max = self.tries_max.get())
            running_threads = threads[:self.max_running.get()]
            threads = threads[self.max_running.get():]
            for thread in running_threads:
                thread.start()
            while len(threads) > 0:
                for i, thread in enumerate(running_threads):
                    if not thread.isAlive():
                        running_threads[i] = threads.pop(0)
                        running_threads[i].start()
                time.sleep(0.1)
            for thread in running_threads:
                thread.join()
            delta_t = datetime.datetime.now()-now
            print('Total time: {0} seconds'.format(delta_t.seconds))
            with lock:
                log = open(os.path.join(polar_directory, log_file), 'a')
                log.write('Total time: {0} seconds\n'.format(delta_t.seconds))
                log.close()


if __name__ == '__main__':
    window = tk.Tk()
    window.wm_title("Rfoil GUI")
    gui = GUI(window)
    gui.mainloop()
