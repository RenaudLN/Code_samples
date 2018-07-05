# -*-coding:Latin-1 -*
"""
@author: Renaud Laine

This is a script I wrote to make a UserIterface for an optimization tool using
Computer Fluid Dynamics calculations. The goal was to write the proper batch
file to launch the desired optimization study. Many options are available as to
what variables should be studied and with what type of algorithm.

"""


from subprocess import Popen
import os
import tkinter as tk

class Interface(tk.Frame):

        
    def __init__(self,window,**kwargs):
        tk.Frame.__init__(self,window,width=768,height=576,**kwargs)
        self.variables = ['tsr','x_offset','angle_timestep','pitch_blade','y_offset','wind_speed']
        self.default = [3, 0.5, 1, 0, 17.5, 10]
        self.defaultMetSettings = [1, 100,0.001,0.001]
        self.selectedVar=[]
        self.method='optimStudy'
        self.methodType='local'
        self.varSettings=["loBound","upBound","partitions","initPoint","finPoint","stepVect","stepPerVar"]
        self.metSettings=["numSteps","maxIter","minBoxSize","convTol"]
        self.usedVarSettings=["loBound","upBound","initPoint"]
        self.usedMetSettings=["convTol","maxIter"]
        self.grid()
        padding=20

        # Variables
        self.variablesTitle = tk.Label(self,text='Variables',font=("Times",10,"bold")).grid(row=0,pady=10, padx=padding)

        self.varLabel = tk.Label(self,text='Choose the variables you want to work on\n').grid(row=1,column=0)
        
        self.varList = tk.Listbox(self,selectmode='multiple')
        self.varList.insert(tk.END,'TSR')
        self.varList.insert(tk.END,'Attach point offset')
        self.varList.insert(tk.END,'Angle per time step')
        self.varList.insert(tk.END,'Pitch')
        self.varList.insert(tk.END,'Turbine radius')
        self.varList.insert(tk.END,'Wind speed')
        self.varList.bind('<<ListboxSelect>>',self.changeSelectedVar)
        self.varList.grid(row=2,sticky=tk.W+tk.N+tk.E+tk.S,rowspan=6, padx=padding)

        self.separator = tk.Label(self,text='|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|\n|').grid(rowspan=8,row=0,column=1)
        
        # Methods Frame
        self.methodsTitle = tk.Label(self,text='Methods',font=("Times",10,"bold")).grid(row=0,column=2,pady=10)
        
        self.methodLabel = tk.Label(self,text='Which type of study are you carrying out\n').grid(row=1,column=2,sticky=tk.W, padx=padding)
        
        self.radio1=tk.StringVar()
        self.radio1.set('optimStudy')
        self.radio1.trace('w',self.setMethod)
        self.method1 = tk.Radiobutton(self,text='Optimization',variable=self.radio1,value='optimStudy')
        self.method1.grid(row=2,column=2,sticky=tk.W, padx=padding)
        self.method2 = tk.Radiobutton(self,text='Parameter study',variable=self.radio1,value='paramStudy')
        self.method2.grid(row=3,column=2,sticky=tk.W, padx=padding)

        self.optimTypeLabel = tk.Label(self,text='\nWhich type of optimization\n')
        self.optimTypeLabel.grid(row=4,column=2,sticky=tk.W, padx=padding)
        
        self.radio2=tk.StringVar()
        self.radio2.set('local')
        self.radio2.trace('w',self.setMethodType)
        self.optimType1 = tk.Radiobutton(self,text='Local (gradient descent)',variable=self.radio2,value='local')
        self.optimType1.grid(row=5,column=2,sticky=tk.W, padx=padding)
        self.optimType2 = tk.Radiobutton(self,text='Global (DIRECT algorithm)',variable=self.radio2,value='global')
        self.optimType2.grid(row=6,column=2,sticky=tk.W, padx=padding)
        self.optimType3 = tk.Radiobutton(self,text='Hybrid (DIRECT then gradient descent)',variable=self.radio2,value='hybrid')
        self.optimType3.grid(row=7,column=2,sticky=tk.W, padx=padding)

        self.paramTypeLabel = tk.Label(self,text='\nWhich type of parameter study\n')
        self.paramTypeLabel.grid(row=4,column=2,sticky=tk.W, padx=padding)
        self.paramTypeLabel.grid_remove()
        
        self.radio3=tk.StringVar()
        self.radio3.set('multidim')
        self.radio3.trace('w',self.setMethodType)
        self.paramType1 = tk.Radiobutton(self,text='Multidimensional study',variable=self.radio3,value='multidim')
        self.paramType1.grid(row=5,column=2,sticky=tk.W, padx=padding)
        self.paramType2 = tk.Radiobutton(self,text='Vector study',variable=self.radio3,value='vector')
        self.paramType2.grid(row=6,column=2,sticky=tk.W, padx=padding)
        self.paramType3 = tk.Radiobutton(self,text='Centered study',variable=self.radio3,value='centered')
        self.paramType3.grid(row=7,column=2,sticky=tk.W, padx=padding)
        self.paramType1.grid_remove()
        self.paramType2.grid_remove()
        self.paramType3.grid_remove()       

        self.separator2=tk.Label(self,text='__________________________________________________________________________________________________________________\n')
        self.separator2.grid(row=8,columnspan=3)
        
        # Settings
        self.settingsTitle = tk.Label(self,text='Settings',font=("Times",10,"bold"))
        self.settingsTitle.grid(row=9,columnspan=3)
        self.settingsFrame = tk.Frame(self)
        self.settingsFrame.grid(row=10,columnspan=3,sticky=tk.W+tk.E)
        self.label={}
        for i,item in enumerate(self.variables):
            self.label[item]=tk.Label(self,text=item).grid(row=0,column=i+1,in_=self.settingsFrame,padx=1)
            
        self.varSettingInput={}
        self.varInputTitle={}
        self.val={}
        for i,setting in enumerate(self.varSettings):
            self.varSettingInput[setting]={}
            self.val[setting]={}
            self.varInputTitle[setting]=tk.Label(self.settingsFrame,text=setting)
            self.varInputTitle[setting].grid(row=i+1,padx=10,sticky=tk.W)
            for j,variable in enumerate(self.variables):
                self.val[setting][variable]=tk.StringVar()
                self.val[setting][variable].set(str(self.default[j]))
                self.varSettingInput[setting][variable]=tk.Entry(self.settingsFrame,width=10,textvariable=self.val[setting][variable])
                self.varSettingInput[setting][variable].grid(row=i+1,column=j+1)
                if setting not in self.usedVarSettings:
                    self.varSettingInput[setting][variable].grid_remove()
                    self.varInputTitle[setting].grid_remove()
                if setting in ['partitions','stepVect','stepPerVar']:
                    self.val[setting][variable].set(str(0))
                if variable not in self.selectedVar:
                    self.varSettingInput[setting][variable]['state']='disabled'
                else:
                    self.varSettingInput[setting][variable]['state']='normal'
        self.separator3=tk.Label(self.settingsFrame,text='_______________________________________________________\n')
        self.separator3.grid(row=1+len(self.varSettings),columnspan=7)
        self.metSettingInput={}
        self.metInputTitle={}
        self.valMet={}
        for i,setting in enumerate(self.metSettings):
            self.metInputTitle[setting]=tk.Label(self.settingsFrame,text=setting)
            self.metInputTitle[setting].grid(row=i+2+len(self.varSettings),padx=10,sticky=tk.W)
            self.valMet[setting]=tk.StringVar()
            self.valMet[setting].set(str(self.defaultMetSettings[i]))
            self.metSettingInput[setting]=tk.Entry(self.settingsFrame,width=10,textvariable=self.valMet[setting])
            self.metSettingInput[setting].grid(row=i+2+len(self.varSettings),column=1)
            if setting not in self.usedMetSettings:
                self.metSettingInput[setting].grid_remove()
                self.metInputTitle[setting].grid_remove()
            else:
                self.metSettingInput[setting].grid()
                self.metInputTitle[setting].grid()

        self.separator4=tk.Label(self,text='__________________________________________________________________________________________________________________\n')
        self.separator4.grid(row=11,columnspan=3)

        # Responses
        self.responsesTitle = tk.Label(self,text='Responses\n',font=("Times",10,"bold"))
        self.responsesTitle.grid(row=12,columnspan=3)

        self.responseNumberLabel = tk.Label(self,text='Number of response or objective function:')
        self.responseNumberLabel.grid(row=13,sticky=tk.W)

        self.responseVar=tk.StringVar()
        self.responseVar.set('1')
        self.responseNumber = tk.Entry(self,width=10,textvariable=self.responseVar)
        self.responseNumber.grid(row=13,columnspan=2,column=1,sticky=tk.W)
        
        # Write file button        
        self.writeFileButton = tk.Button(self, text="Launch!!",command=self.launch)
        self.writeFileButton.grid(row=100,columnspan=3,pady=padding)
        

    # Methods
    def changeSelectedVar(self,*args,**kwargs):
        """
        Choose the variables for the study
        """
        self.selectedVar = [v for i,v in enumerate(self.variables) if i in self.varList.curselection()]
        self.updateInputs()

    def updateInputs(self):
        """
        Update which inputs can be written in
        """
        for setting in self.varSettings:
            for variable in self.variables:
                if variable not in self.selectedVar:
                    self.varSettingInput[setting][variable]['state']='disabled'
                else:
                    self.varSettingInput[setting][variable]['state']='normal'
        
    def launch(self):
        """
        Write the batch file with all the desired preferences
        """
        file='environment\n\ttabular_data\n\t\ttabular_data_file = \'DesignPoints.dat\''
        if self.methodType=='local':
            file+='\n\nmethod'
            file+='\n\tmax_iterations = '+self.valMet['maxIter'].get()
            file+='\n\tconvergence_tolerance = '+self.valMet['convTol'].get()
            file+='\n\tconmin_frcg'
            file+='\n\nvariables'
            file+='\n\tcontinuous_design = '+str(len(self.selectedVar))
            file+='\n\t\tinitial_point ='
            for var in self.selectedVar:
                file+=' '+self.val['initPoint'][var].get()
            file+='\n\t\tlower_bounds ='
            for var in self.selectedVar:
                file+=' '+self.val['loBound'][var].get()
            file+='\n\t\tupper_bounds ='
            for var in self.selectedVar:
                file+=' '+self.val['upBound'][var].get()
            file+='\n\t\tdescriptors ='
            for var in self.selectedVar:
                file+=' \''+var+'\''
            file+='\n\ninterface'
            file+='\n\t.............'
            file+='\n\t.............'
            file+='\n\t.............'
            file+='\n\t.............'
            file+='\n\nresponses'
            file+='\n\tobjective_functions = '+self.responseVar.get()
            file+='\n\tnumerical_gradients'
            file+='\n\t\tmethod_source dakota'
            file+='\n\t\tfd_gradient_step_size = 1.e-5'
            file+='\n\tno_hessians'
        writeTo=open('dakota.in','w')
        writeTo.write(file)
        writeTo.close()
        print(file)
        window.quit()

    def setMethod(self,*args,**kwargs):
        """
        Choose the study method
        """
        method = self.radio1.get()
        self.method = method
        self.updateMethodType()
        self.setMethodType()

    def updateMethodType(self, ):
        """
        Update the display according to study method
        """
        if self.method=='optimStudy':
            self.optimTypeLabel.grid()
            self.optimType1.grid()
            self.optimType2.grid()
            self.optimType3.grid()
            self.paramTypeLabel.grid_remove()
            self.paramType1.grid_remove()
            self.paramType2.grid_remove()
            self.paramType3.grid_remove()
        else:
            self.paramTypeLabel.grid()
            self.paramType1.grid()
            self.paramType2.grid()
            self.paramType3.grid()
            self.optimTypeLabel.grid_remove()
            self.optimType1.grid_remove()
            self.optimType2.grid_remove()
            self.optimType3.grid_remove()

    def setMethodType(self,*args,**kwargs):
        """
        Set study method type
        """
        if self.method=='optimStudy':
            self.methodType = self.radio2.get()
        else:
            self.methodType = self.radio3.get()
        self.setUsedSettings()

    def setUsedSettings(self):
        """
        Update display according to study method type
        """
        if self.methodType=='local':
            self.usedVarSettings=["loBound","upBound","initPoint","convTol","maxIter"]
            self.usedMetSettings=["maxIter","convTol"]
        elif self.methodType=='global':
            self.usedVarSettings=["loBound","upBound","maxIter"]
            self.usedMetSettings=["maxIter","minBoxSize"]
        elif self.methodType=='hybrid':
            self.usedVarSettings=["loBound","upBound","convTol","maxIter"]
            self.usedMetSettings=["maxIter","minBoxSize","convTol"]
        elif self.methodType=='multidim':
            self.usedVarSettings=["loBound","upBound","partitions"]
            self.usedMetSettings=[]
        elif self.methodType=='vector':
            self.usedVarSettings=["initPoint","finPoint","stepVect"]
            self.usedMetSettings=["numSteps"]
        else:
            self.usedVarSettings=["initPoint","stepPerVar","stepVect"]
            self.usedMetSettings=[]
        self.updateSettings()

    def updateSettings(self):
        """
        Update available settings acording to study method and method type
        """
        for setting in self.varSettings:
            for variable in self.variables:
                if setting not in self.usedVarSettings:
                    self.varSettingInput[setting][variable].grid_remove()
                    self.varInputTitle[setting].grid_remove()
                else:
                    self.varSettingInput[setting][variable].grid()
                    self.varInputTitle[setting].grid()
        for setting in self.metSettings:
            if setting not in self.usedMetSettings:
                self.metSettingInput[setting].grid_remove()
                self.metInputTitle[setting].grid_remove()
            else:
                self.metSettingInput[setting].grid()
                self.metInputTitle[setting].grid()
        

window = tk.Tk()
window.resizable(width=tk.FALSE, height=tk.TRUE)
window.geometry('540x650')
interface=Interface(window)
interface.mainloop()
window.destroy()


#Launch dakota
p = Popen("launch.bat", cwd=os.getcwd())
stdout, stderr = p.communicate()
