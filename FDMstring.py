import numpy as np
import matplotlib.pyplot as plt
import pygame, math
from MyWindow import *

class FDMStringWindow(MyWindow):
    def __init__(self, root):
        self.signalType = -1 # don't need to load any signals/images
        
        self.sampleRate = 44100
        pygame.mixer.init(self.sampleRate, channels=1)
        
        
        MyWindow.__init__(self, root)     
        
   
    def makeLeftPane(self):  
        varTitles = ['Excitation Type']
        varDTypes = [IntVar]
        varDefaults = [0]
        varTexts = [['Kronecker Delta', 'Triangle']]
        varVals = [range(2)]
        
        optionsSpecs = [varTitles, varDTypes, varDefaults, varTexts, varVals]
        
        self._makeLeftPane(optionsSpecs)
        
        self.excitationType = self.options[0]
        
        varNames = ['numElems','deltaX','deltaT','secs','tension','density', 'dampening']
        varTypes = [IntVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar, DoubleVar]
        varInit = [100, 1./100, 1./self.sampleRate, 1, 50000., 1., 5]
        varLabel = ['Number of Elements:', 'Delta x:', 'Delta t:', 'Simulation Time:', 'Tension:', 'Density:', 'Dampening Factor:']
        
        Label(self.leftPane, text='String Simulation Factors').pack(fill=X, pady=(15,0), padx=5)
        funcFrame = Frame(self.leftPane)
        funcFrame.pack(fill=BOTH, padx=5, pady=(0,15))
       
       
        for i in range(len(varNames)):
            var = varTypes[i]()
            var.set(varInit[i])
            print var.get()
            #eval('print var.get()')
            exec('self.%s = var'%(varNames[i]))
            
            Button(funcFrame, text=varLabel[i], command=self.runSimulation).grid(row=i+1,column=1,sticky=W,padx=(5,0))
            Entry(funcFrame, textvariable=var).grid(row=i+1,column=2,sticky=E,padx=(0,5))
            
        controlsFrame = Frame(self.leftPane)
        controlsFrame.pack(fill=BOTH, padx=5, pady=(0,15))
        self.step = IntVar()
        self.step.set(1)
        
        Entry(controlsFrame, textvariable=self.step, width=10).pack(side=LEFT,padx=(5,5))
        Button(controlsFrame, text='Back', command=self.backT).pack(side=LEFT,padx=(5,5))
        Button(controlsFrame, text='Forward', command=self.forwardT).pack(side=LEFT,padx=(5,5))
        Button(controlsFrame, text='Play Sound', command=self.play).pack(side=LEFT,padx=(15,5))
        #Button(controlsFrame, text='Forward', command=lambda : self.changeT(1)).pack(side=LEFT,padx=(5,5))
        

    def backT(self):
        self.time -= self.step.get()
        self.updatePlots()
    def forwardT(self):
        self.time += self.step.get()
        self.updatePlots()
        
    ############################################################################  
    # Contains the plots and frequency sliders at the bottom
    #
    ############################################################################    
    def makeRightPane(self):
    
        self._makeRightPane((3,1))        # create the right pane with 2 plots, and the 10 sliders
      
    ############################################################################  
    # Initializes the signals in the plots
    #
    ############################################################################    
    def initSignals(self):                  # plots dummy data on the plots
        axes = self.axes
        lines = []
        dummy = [0]
        for axis in axes:
            l,=axis.plot(dummy)
            lines.append(l)
        
        self.lines = lines
        self.time = 1

    
    def play(self):
        ar = np.array(self.sound)                                # make a copy
        ar /= max(abs(ar))                                       # normalize to 1
        ar *= 2**14                                                 # normalize to 15 bits. 16 was making my speakers crackle
        ar = ar.astype(np.int16)
        
        sound = pygame.sndarray.make_sound(ar)   # create sound
        sound.play()                                                # play it
        
    
    def runSimulation(self):
        N = self.numElems.get()
        N = N - N%2 + 1
        dt = self.deltaT.get()
        dx = self.deltaX.get()
        length = self.secs.get()
        tension = self.tension.get()
        density = self.density.get()
        damp = self.dampening.get()
        
        if self.excitationType.get():
            excitation = 2./N * np.array(range((N-1)/2) + range((N-1)/2, -1, -1))
        else:
            excitation = np.zeros(N)
            excitation[(N-1)/2] = 1
        self.func = [excitation]
        
        
        timeSteps = int(math.ceil(length/dt))
        v = np.zeros(N)
        for n in range(timeSteps):
            #print '%0.05f%% done'%(100.*n/timeSteps)
            pos = self.func[-1]
            next_pos = list(self.func[-1])
            for i in range(1, N-1):
                a = tension/density*(pos[i-1] + pos[i+1] - 2*pos[i])/(dx**2) - damp * v[i]
                v[i] += a * dt
                next_pos[i] += v[i] * dt
            self.func.append(next_pos)
        self.genSound()
        self.updatePlots()
   
    
    def genSound(self):
        sound = []
        for i in range(len(self.func)):
            sample = np.mean(self.func[i])
            print sample
            sound.append(sample)
        
        self.sound = sound
        #print self.sound
        
    
    ############################################################################  
    # Updates the plots when anything is changed
    #
    ############################################################################       
    def updatePlots(self):
        N = self.numElems.get()
        N = N - N%2 + 1
        dt = self.deltaT.get()
        dx = self.deltaX.get()
        length = self.secs.get()
        timeSteps = math.ceil(length/dt)
    
        wave = self.func[self.time]
        sound = self.sound/max(self.sound)
        
        t = np.linspace(0,self.secs.get(),timeSteps+1)
        x = np.linspace(0,N*dx,N)
        
        print len(t), len(sound), len(x), len(wave)
        self.lines[0].set_data(x,wave)
        self.lines[1].set_data(1000*t,sound)
        
        self.axes[2].cla()
        self.axes[2].specgram(sound, Fs=self.sampleRate)
        
        #self.play()
        f = np.array(self.func)
        m = f.max(axis=1).max()
        self.formatAxes(self.axes[0],x,[-m,m],'Position', 'Amplitude','String Shape at n = %i'%self.time) # format the axes
        self.formatAxes(self.axes[1],1000*t,sound,'Time (ms)', 'Amplitude', 'Sound') # formate the axes
        self.formatAxes(self.axes[2],1000*t,[0,self.sampleRate/2.],'Time (ms)','Frequency (kHz)','Spectrogram, Fs = %0.01f kHz'%(self.sampleRate/1000.),spec=True)
        
        
        for axis in self.axes:                                                          # allow plots to update
            axis.get_figure().canvas.draw_idle()
        
if __name__ == "__main__":
    root = Tk()
    FDMStringWindow(root)
    if os.name == "nt": root.wm_state('zoomed')
    else: root.attributes('-zoomed', True)
    
    root.mainloop()
    exit()
