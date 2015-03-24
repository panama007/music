import pygame
from MyWindow import *

class SynthWindow(MyWindow):
    def __init__(self, root):
        self.signalType = -1 # don't need to load any signals/images
        
        self.sampleRate = 44100
        pygame.mixer.init(self.sampleRate, channels=1)
        
        MyWindow.__init__(self, root)     
        
   
    def makeLeftPane(self):
        #optionsSpecs = [varTitles, varDTypes, varDefaults, varTexts, varVals]
        
        self._makeLeftPane([])#optionsSpecs)
        
        # variable for holding the function
        self.customFunc = StringVar()
        self.customFunc.set('exp(-5*t)*cos(2*pi*f0*t**2+cos(2*pi*f1*t))')
        
        Label(self.leftPane, text='Function').pack(fill=X, pady=(15,0), padx=5)
        # create a frame to hold the function stuff
        funcFrame = Frame(self.leftPane)
        funcFrame.pack(fill=BOTH, padx=5, pady=(0,15))
       
        # custom function radiobutton
        Button(funcFrame, text='Enter Formula:', command=self.updatePlots).grid(row=1,column=1,sticky=W,padx=(5,0))
        # custom function text entry box
        Entry(funcFrame, textvariable=self.customFunc).grid(row=1,column=2,sticky=E,padx=(0,5))
        # button to play sound
        Button(funcFrame, text='Play Sound', command=self.play).grid(row=2,columnspan=2,column=1,padx=5)
    
    def play(self):
        ar = np.array(self.func)                                # make a copy
        ar /= max(abs(ar))                                       # normalize to 1
        ar *= 2**14                                                 # normalize to 15 bits. 16 was making my speakers crackle
        ar = ar.astype(np.int16)
        
        sound = pygame.sndarray.make_sound(ar)   # create sound
        sound.play()                                                # play it
        
    
    ############################################################################  
    # Contains the plots and frequency sliders at the bottom
    #
    ############################################################################    
    def makeRightPane(self):
        varNames = ['f%i'%i for i in range(10)]     # variables to hold 10 possible frequency sliders
        varLimits = [(40, 4000)]*10                       # frequency limits
        varRes = [10]*10                                      # frequency step
        varDTypes = [DoubleVar]*10                     # variable type
        varDefaults = [440]*10                             # defaults, 440 = A4
        varValues = [varNames, varLimits, varRes, varDTypes, varDefaults]
                                                                    
        self._makeRightPane((2,1),varValues)        # create the right pane with 2 plots, and the 10 sliders
        
        self.frequencies = self.vars                       # store the variables so we can use the values
        self.frequencySliders = self.sliders             # store the pointers to sliders so unused ones may be made invisible
      
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
    
        self.freqsUsed = range(10)
    
    ############################################################################  
    # Updates the plots when anything is changed
    #
    ############################################################################       
    def updatePlots(self):
        
        f = [self.frequencies[i].get() for i in range(10)]                  # get all the frequencies from sliders
        oldFreqs = self.freqsUsed                                                  # show sliders if used, hide unused sliders
        newFreqs = []
        for i in range(10):
            if 'f%i'%i in self.customFunc.get(): newFreqs.append(i)
        self.hideShowFreqs(oldFreqs, newFreqs)
        self.freqsUsed = newFreqs
        
        t = np.arange(0,0.5,1./self.sampleRate)                             # 0.5 seconds of sound
        
        localDict = {'f%i'%i : f[i] for i in range(10)}                       # possible variables the input function can access
        localDict['t'] = t
        func = eval(self.customFunc.get(),np.__dict__,localDict)      # evaluate the function using numpy functions if needed
        self.func = func
        N = len(func)                                                                    # number of samples
        
        self.lines[0].set_data(t,func)                                              # plot new data
        self.formatAxes(self.axes[0],t,func,'Time (s)', 'Amplitude',self.customFunc.get()) # format the axes
        
        F = np.abs(np.fft.fft(func))[:N/2]                                         # compute the FFT
        w = np.arange(0.,N/2)*self.sampleRate/float(N)                  # frequencies used in FFT
        self.lines[1].set_data(w,F)                                                  # plot the FFT
        self.formatAxes(self.axes[1],w[:N/10],F[:N/10],'Frequency (Hz)', 'Amplitude', 'FFT of Signal') # formate the axes
        
        
        for axis in self.axes:                                                          # allow plots to update
            axis.get_figure().canvas.draw_idle()
        
if __name__ == "__main__":
    root = Tk()
    SynthWindow(root)
    if os.name == "nt": root.wm_state('zoomed')
    else: root.attributes('-zoomed', True)
    
    root.mainloop()
    exit()
