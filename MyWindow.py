import numpy as np

import os

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.axes3d import Axes3D

import Tkinter as tk
import tkFileDialog
from Tkinter import *


class MyWindow(Frame):    
    
    def __init__(self, root):
    
        Frame.__init__(self, root)
        
        master = PanedWindow(root, orient=HORIZONTAL)
        self.master = master
        master.pack(fill=BOTH, expand=1)

        self.makeLeftPane()
        self.makeRightPane()
            
        self.initSignals()
        
           
    def _makeLeftPane(self, optionsSpecs=[]):
        leftPane = Frame(self.master, bg='grey')
        
        if optionsSpecs:
            [varTitles, varDTypes, varDefaults, varTexts, varVals] = optionsSpecs
            numOptions = len(optionsSpecs[0])

            self.options = []
            self.radioButtons = []

            for i in range(numOptions):
                self.options.append(varDTypes[i]())
                self.options[i].set(varDefaults[i])
            
            for i in range(numOptions):
                self.radioButtons.append([])
            
                l = Label(leftPane, text=varTitles[i])
                l.pack(fill=X, pady=(5,0), padx=5)

                frame = Frame(leftPane)
                frame.pack(fill=BOTH,pady=(0,5),padx=5)
                

                for j in range(len(varTexts[i])):
                    rb = Radiobutton(frame, text=varTexts[i][j], variable=self.options[i], value=varVals[i][j], command=self.updatePlots)
                    rb.grid(row=j+1,sticky=W,padx=(5,0))
                    
                    self.radioButtons[i].append(rb)

        self.leftPane = leftPane    
        self.master.add(leftPane)    
        
    def _makeRightPane(self, plots, varValues=[]):
        rightPane = Frame(self.master)

        numPlots = plots[0]*plots[1]
        plotFrame = Frame(rightPane)
        plotFrame.pack(fill=BOTH, expand=1)
        plotFrames = [Frame(plotFrame) for i in range(numPlots)] 
        figs = [Figure(figsize=(1,1)) for i in range(numPlots)]
        axes = [fig.add_subplot(111) for fig in figs]
        self.figs = figs
        self.axes = axes
        
        #  creates the matplotlib canvasses for the plots 
        for i in range(numPlots):
            canvas = FigureCanvasTkAgg(figs[i], master=plotFrames[i])
            canvas.show()
            canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
            
        for c in range(plots[1]):
            plotFrame.columnconfigure(c, weight=1)
            for r in range(plots[0]):
                plotFrame.rowconfigure(r, weight=1)
                p = plotFrames[c*plots[1]+r]
                p.grid(row=r, column=c, sticky=N+S+E+W)

        
        # This part below takes care of the sliders. It stores the pointers at
        #   self.sliders and self.vars
        if varValues:
            varsFrame = Frame(rightPane)   
            [varNames, varLimits, varRes, varDTypes, varDefaults] = varValues
            numVars = len(varValues[0])
            
            self.sliders = []
            self.vars = []

            for i in range(numVars):
                self.vars.append(varDTypes[i]()) 
                self.vars[i].set(varDefaults[i])
            
            for i in range(numVars):

                l = Label(varsFrame, text=varNames[i]+': ')
                l.grid(row=i,column=0) 
                w = Scale(varsFrame,from_=varLimits[i][0], to=varLimits[i][1], resolution=varRes[i], 
                    orient=HORIZONTAL, command=(lambda x: self.updatePlots()), variable=self.vars[i])
                w.grid(row=i,column=1, sticky=N+S+E+W)

                self.sliders.append([l,w])
            # only let the sliders expand, labels same size
            varsFrame.columnconfigure(1, weight=1)                       
            varsFrame.pack(fill=X)
               
        self.rightPane = rightPane
        self.master.add(rightPane)
         
    def initSignals(self): pass
    def updatePlots(self): pass

    def formatAxes(self, ax, x, y, xlabel, ylabel, title, spec=False):
        if not spec:
            ax.axis([min(x), max(x), min(y), max(y)])
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        #ax.spines['bottom'].set_position('zero')
        #ax.spines['bottom'].label='zero'
        #ax.xaxis.set_label_coords(0.5,-0.01)
        #ax.yaxis.set_label_coords(-0.05,0.5)
         
    def hideShowFreqs(self, oldFreqs, newFreqs):
        for i in oldFreqs:
            if i not in newFreqs:
                self.frequencySliders[i][0].grid_remove()
                self.frequencySliders[i][1].grid_remove()
        for i in newFreqs:
            if i not in oldFreqs:
                self.frequencySliders[i][0].grid()
                self.frequencySliders[i][1].grid() 
                
    def file_save(self):
        f = tkFileDialog.asksaveasfilename(defaultextension='.dat', initialdir='signals/', filetypes=[('Data File','.dat')])
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        np.savetxt(f,self.y)
        f.close() # `()` was missing.
    
