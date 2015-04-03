import numpy as np
import matplotlib.pyplot as plt
import pygame
from MyWindow import *

class KarplusStrongWindow(MyWindow):
    def __init__(self, root):
        self.signalType = -1 # don't need to load any signals/images
        
        self.sampleRate = 44100
        pygame.mixer.init(self.sampleRate, channels=1)
        
        MyWindow.__init__(self, root)     
        
   
    def makeLeftPane(self):
        varTitles = ['Random Excitation Type']
        varDTypes = [IntVar]
        varDefaults = [0]
        varTexts = [['Uniform', 'Gaussian', 'Exponential']]
        varVals = [range(3)]
        
        optionsSpecs = [varTitles, varDTypes, varDefaults, varTexts, varVals]
        
        self._makeLeftPane(optionsSpecs)
        
        self.randType = self.options[0]
        
        
        self.delay = StringVar()
        self.delay.set('100')
        self.prob = StringVar()
        self.prob.set('1')
        
        Label(self.leftPane, text='Karplus-Strong Factors').pack(fill=X, pady=(15,0), padx=5)
        funcFrame = Frame(self.leftPane)
        funcFrame.pack(fill=BOTH, padx=5, pady=(0,15))
       
        Button(funcFrame, text='Enter Delay:', command=self.updatePlots).grid(row=1,column=1,sticky=W,padx=(5,0))
        Entry(funcFrame, textvariable=self.delay).grid(row=1,column=2,sticky=E,padx=(0,5))
        Button(funcFrame, text='Enter Probability:', command=self.updatePlots).grid(row=2,column=1,sticky=W,padx=(5,0))
        Entry(funcFrame, textvariable=self.prob).grid(row=2,column=2,sticky=E,padx=(0,5))
        
        
    ############################################################################  
    # Contains the plots and frequency sliders at the bottom
    #
    ############################################################################    
    def makeRightPane(self):
    
        self._makeRightPane((2,1))        # create the right pane with 2 plots, and the 10 sliders
      
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
    
    def play(self):
        ar = np.array(self.func)                                # make a copy
        ar /= max(abs(ar))                                       # normalize to 1
        ar *= 2**14                                                 # normalize to 15 bits. 16 was making my speakers crackle
        ar = ar.astype(np.int16)
        
        sound = pygame.sndarray.make_sound(ar)   # create sound
        sound.play()                                                # play it
        
        
    ############################################################################  
    # Updates the plots when anything is changed
    #
    ############################################################################       
    def updatePlots(self):
        
        dt = 1./self.sampleRate
        t = np.arange(0,1,dt)
        N = len(t)

        p = int(self.delay.get())
        b = float(self.prob.get())
        
        if self.randType.get() == 0:
            y = np.random.uniform(0.,1., p+1)
        elif self.randType.get() == 1:
            y = np.random.standard_normal(p+1)
        elif self.randType.get() == 2:
            y = np.random.exponential(3,p+1)

        for i in range(p+1, len(t)):
            newval = (2*np.random.binomial(1, b)-1) * 0.5*( y[i-p] + y[i-p-1] )
            y = np.append(y, newval)

        F = np.abs(np.fft.fft(y))[:N/2]                              # compute the FFT
        w = np.arange(0.,N/2)*self.sampleRate/float(N)                  # frequencies used in FFT
            
        self.lines[0].set_data(t,y)
        self.lines[1].set_data(w,F)
        
        self.func = y
        self.play()
        
        self.formatAxes(self.axes[0],t,y,'Time (s)', 'Amplitude','KS String') # format the axes
        self.formatAxes(self.axes[1],w[:N],F[:N],'Frequency (Hz)', 'Amplitude', 'FFT of Signal') # formate the axes
        
        for axis in self.axes:                                                          # allow plots to update
            axis.get_figure().canvas.draw_idle()
        
if __name__ == "__main__":
    root = Tk()
    KarplusStrongWindow(root)
    if os.name == "nt": root.wm_state('zoomed')
    else: root.attributes('-zoomed', True)
    
    root.mainloop()
    exit()

        

print len(t), len(y)

plt.plot(t,y)

play(y)

plt.show()
