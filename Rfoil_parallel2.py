# -*- coding: utf-8 -*-
"""
@author: Renaud Laine

This is a program I wrote to take control of a computer's process and write
text lines in a background task. The purpose was to automate the process of
using a software that behaves like a command line (writing commands line after
line) but that could not be used in a batch. Therefore this opens said process
(rfoil) in the background, feeds it the required lines, waits for the
computation to finish and outputs the data from the software as a file. Also
this offers the option of parallel computing using the Thread class. A user
interface calling the object Rfoil was also created.

"""

import time, datetime
try:
    import win32api, win32gui, win32process, win32con
except:
    from win32 import win32api, win32gui, win32process
    import win32.lib.win32con as win32con
import os
import shutil
import psutil
from threading import Thread, RLock

class Rfoil(Thread):
    
    def __init__(self, cmd = '', rootdir = '', profile = '', re = '', mach = 0,
                 angle_max = 0, angle_step = 0, tries_max = 5):
        Thread.__init__(self)
        self.cmd = cmd
        self.profile = profile.capitalize()
        self.re = re
        self.root_directory = rootdir
        self.polar_directory = os.path.join(self.root_directory, self.profile)
        self.profile_file = self.profile + '.dat'
        self.log_file = self.profile + '.log'
        self.polar_file = 'RE' + re + '.dat'
        self.tries = 1
        self.tries_max = tries_max
        self.mach = mach
        self.angle_max = angle_max
        self.angle_step = angle_step
        self.success = False
        self.handle = {}
        self.setDaemon(True)

    def openwindow(self):
        """
        Opens rfoil in the background and remembers its process id
        """
        self.startupinfo = win32process.STARTUPINFO()
        self.startupinfo.dwFlags = win32process.STARTF_USESHOWWINDOW
        self.startupinfo.wShowWindow = win32con.SW_MINIMIZE
        self.hp, self.ht, self.pid, self.tid = win32process.CreateProcess(
                None,    # name
                self.cmd,     # command line
                None,    # process attributes
                None,    # thread attributes
                0,       # inheritance flag
                0,       # creation flag
                None,    # new environment
                self.polar_directory,    # current directory
                self.startupinfo)
        self.process = psutil.Process(self.pid)
        self.getwindow()

    def wcallb(self, hwnd, handle):
        '''wcallb is callback for EnumThreadWindows and 
        EnumChildWindows. It populates the dict 'handle' with 
        references by class name for each window and child 
        window of the given thread ID.
        '''
        handle[win32gui.GetClassName(hwnd)] = hwnd
        win32gui.EnumChildWindows(hwnd, self.wcallb, handle)
        return True

    def getwindow(self):
        """
        Gets the window handle for the window named 'rfoil01Graphic' in the
        given process.
        """
        while 'rfoil01Graphic' not in self.handle:   
            time.sleep(0.1)
            try:
                win32gui.EnumThreadWindows(self.tid, self.wcallb, self.handle)
            except:
                pass
        
    def write(self, msg):
        """
        write sends a message to the rfoil window and
        then waits for rfoil to be idle (cpu usage = 0) for
        a certain amount of time.
        """
        msg = str(msg) + '\n'
        for c in msg:
            win32api.PostMessage(
                self.handle['rfoil01Graphic'], 
                win32con.WM_CHAR, 
                ord(c), 
                0)
        self.waitready()

    def waitready(self):
        """
        Wait until process cpu usage is 0
        """
        timer = 50#milliseconds
        count_max = int(timer/10)
        #cpu usage over the last count_max*0.01 seconds
        cpu = [1 for i in range(count_max)]
        while sum(cpu) > 0:
            cpu_now = self.process.cpu_percent()
            cpu = cpu[1:] + [cpu_now]
            #print(cpu)
            time.sleep(0.01)

    def close(self):
        """
        Kill process
        """
        self.handle = {}
        try:
            self.process.kill()
        except:
            pass

    def run(self):
        """
        The run method for the Thread, plays all the desired actions in the
        order. Creates a data file and a log file.
        """
        while (not self.success) and (self.tries <= tries_max):
            if self.tries == 1:
                old_lines=[]
            file_fullpath = os.path.join(self.polar_directory, self.polar_file)
            log_fullpath = os.path.join(self.polar_directory, self.log_file)
            ###Check whether the profile is custom or Naca
            naca = False
            if self.profile[0:4] == 'Naca' and len(self.profile) in [8, 9]:
                naca = True
                naca_number = self.profile[4:]
                naca_type = 'nac' + str(len(naca_number))
            else:
                naca_type = ''
                naca_number = ''
            if not naca and not os.path.exists(os.path.join(self.polar_directory, self.profile_file)):
                try:
                    with lock:
                        shutil.copyfile(self.profile_file, os.path.join(self.polar_directory, self.profile_file))
                except:
                    print('No data for profile: {0}'.format(self.profile))
                    self.success = True
                    continue
            if os.path.exists(file_fullpath):
                #Remember what was in the file and delete it
                with lock:
                    file = open(file_fullpath)
                    old_lines = file.readlines()
                    file.close()
                    os.remove(file_fullpath)
            self.openwindow()
            try:
                self.waitready() #Initial wait for everything to be written in the window
                with lock:
                    if naca:
                        self.write(naca_type)
                        self.write(naca_number)
                    else:
                        self.write('load')
                        self.write(self.profile_file)
                        self.write(self.profile)
                self.write('oper')
                self.write('visc')
                self.write(self.re)
                self.write('mach')
                self.write(self.mach)
                self.write('pacc')
                self.write(self.polar_file)
                self.write('')
                self.write('aseq')
                self.write('0')
                self.write(self.angle_max)
                self.write(self.angle_step)
                self.waitready() #Security wait between the two halves
                self.write('vpar')
                self.write('init')
                self.write('')
                self.write('aseq')
                self.write(-self.angle_step)
                self.write(-self.angle_max)
                self.write(-self.angle_step)
                self.waitready()
            except:
                pass
            finally:
                self.close()
                if os.path.exists(file_fullpath):
                    file = open(file_fullpath)
                    lines = file.readlines()
                    file.close()
                    #There are 13 header lines
                    lines = lines[13:]
                    min_amount_data = self.angle_max / self.angle_step + 2
                    #If data is same as before allow less data as minimum
                    #This is to reduce calculation time as Rfoil takes lots
                    #of cpu time on computation converging badly.
                    if len(old_lines) == len(lines):
                        min_amount_data = int(min_amount_data * (self.tries_max - self.tries + 1) / self.tries_max)
                    #If we have less data than before, rewrite previous file
                    elif len(old_lines) > len(lines):
                        lines = old_lines
                    #Check there is enough data or too many tries
                    if len(lines) >= min_amount_data or self.tries >= self.tries_max: 
                        if len(lines) >= min_amount_data:
                            print('    Reynolds = {0}, success on try {1}'.format(self.re, self.tries))
                            log = open(log_fullpath, 'a')
                            log.write('Reynolds = {0}, success on try {1}\n'.format(self.re, self.tries))
                            log.close()
                        else:
                            print('    Reynolds = {0}, failed {1} times'.format(self.re, self.tries_max))
                            log = open(log_fullpath, 'a')
                            log.write('Reynolds = {0}, failed {1} times\n'.format(self.re, self.tries_max))
                            log.close()
                        lines = [(float(item[:8]), item) for item in lines]
                        lines = [line for angle, line in sorted(lines)]
                        file = open(file_fullpath, 'w')
                        file.writelines(lines)
                        file.close()
                        self.success = True
                    else:
                        self.tries += 1
                        os.remove(file_fullpath)
                else:
                    if self.tries >= tries_max:
                        open(file_fullpath, 'w').writelines(old_lines)
                        print('    Reynolds = {0}, failed {1} times'.format(self.re, self.tries_max))
                        open(log_fullpath, 'a').write('Reynolds = {0}, failed {1} times\n'.format(self.re, self.tries_max))
                    self.tries += 1

        
###The main action of the script
###Loops over profiles and Reynolds to create the polars.
if __name__ == "__main__":
    ###PATH to Rfoil
    cmd = 'C:/Program Files (x86)/rFoil/rfoil01.exe' #Use / or \\ in the path
    ###Write each profile between apostrophes separated by a comma.
    ###If a Naca profile is specified, the airfoil will be generated by Rfoil.
    profiles = ['Profile']
    ###Write the range of Reynolds you want to generate a polar for.
    Reynolds = ['1e5', '5e5', '1e6', '5e6', '1e7', '5e7']
    ###Other Rfoil settings
    Mach = 0.1
    angle_max = 20
    angle_step = 0.5
    ###The number of tries you want to do for a polar in case of failure.
    ###Failure can happen for various reason, from convergence failing to Rfoil crashing.
    ###If you absolutely want all polars to be created set a high (>= 5) tries_max.
    tries_max = 5
    ###Polars will be saved to root_directory/Name_of_profile/ (relative to where you started this script)
    root_directory = 'Polars'
    lock = RLock()
    max_running = 1
    for profile in profiles:
        profile = profile.capitalize()
        ###Make some room for the incoming polars
        polar_directory = os.path.join(root_directory, profile)
        if not os.path.exists(polar_directory):
            os.mkdir(polar_directory)
        print('Profile: ' + profile)
        now = datetime.datetime.now()
        log_file = profile + '.log'
        with lock:
            log = open(os.path.join(polar_directory, log_file), 'a')
            log.write(now.strftime("\n----- %Y-%m-%d %H:%M -----\n"))
            log.close()
        ###re is the Reynolds index
        ###tries is to try again as many times as tries_max if something goes wrong
        threads = [None for i in range(len(Reynolds))]
        for i, re in enumerate(Reynolds):
            threads[i] = Rfoil(cmd = cmd, rootdir = root_directory, profile = profile, re = re, mach = Mach,
                   angle_max = angle_max, angle_step = angle_step, tries_max = tries_max)
        running_threads = threads[:max_running]
        threads = threads[max_running:]
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
