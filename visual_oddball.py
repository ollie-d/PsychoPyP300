# Triangle-based P300 Speller
# Written in PsychoPy (use conda environment)
# Paradigm inspired by Li et al., 2019
#   https://www.frontiersin.org/articles/10.3389/fnhum.2018.00520/full
#
# Wrote this in a couple of hours, but should suffice
# Photosensor circle in lower-right corner turns on for
# duration of task-relevant stimuli.
# An LSL marker is sent on the first frame of stimulus onset.
# Currently triangle point down is standard and point up is target
# '0' marker is standard and '1' marker is oddball/target
# Size of triangle roughly calculated to be 4 visual degrees like paper
# (took some rough measurements for my setup)
# Make sure you check out the link for that.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! MAKE SURE refresh_rate IS SET TO YOUR MONITOR'S REFRESH RATE !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
# Created........: 13Apr2021 [ollie-d]
# Last Modified..: 13Apr2021 [ollie-d]

from math import atan2, degrees
import psychopy.visual
import psychopy.event
import time
import numpy as np
import pylsl
import random

# Global variables
win = None # Global variable for window (Initialized in main)
mrkstream = None # Global variable for LSL marker stream (Initialized in main)
photosensor = None # Global variable for photosensor (Initialized in main)
triangle = None # Global variable for stimulus (Initialized in main)
fixation = None # Global variable for fixation cross (Initialized in main)
bg_color = [-1, -1, -1]
win_w = 1920
win_h = 1080
refresh_rate = 144. # Monitor refresh rate (CRITICAL FOR TIMING)


#========================================================
# High Level Functions
#========================================================
def Paradigm():
    global refresh_rate
    global win
    global photosensor
    global fixation
    global triangle
    global mrkstream
    global bg_color
    
    # Compute sequence of stimuli
    sequence = CreateSequence(120, 30)
    
    # Iterate through sequence and perform:
    # 250ms  bold fixation
    # 500ms  normal fixation
    # 500ms  stimulus presentation
    # 1000ms black screen
    
    
    for i, s in enumerate(sequence):
        # 250ms Bold fixation cross
        fixation.lineWidth = 1
        fixation.lineColor = [1, 1, 1]
        SetStimulus(fixation, 'on')
        for frame in range(MsToFrames(250, refresh_rate)):
            fixation.draw()
            win.flip()
            
        # 500ms Normal fixation cross
        fixation.lineColor = bg_color
        for frame in range(MsToFrames(500, refresh_rate)):
            fixation.draw()
            win.flip()
    
        # 500ms Stimulus presentation (w/ fixation)
        RotateTriangle(triangle, 180)   # <-- Standard (S)
        mrk = pylsl.vectorstr(['0'])
        if s == 'T':
            RotateTriangle(triangle, 0) # <-- Target (T)
            mrk = pylsl.vectorstr(['1'])
        SetStimulus(photosensor, 'on')
        for frame in range(MsToFrames(500, refresh_rate)):
            # Send LSL marker on first frame
            if frame == 0:
                mrkstream.push_sample(mrk);
            photosensor.draw()
            triangle.draw()
            fixation.draw()
            win.flip()
        
        # 1000ms darkness
        for frame in range(MsToFrames(1000, refresh_rate)):
            win.flip()

#========================================================
# Low Level Functions
#========================================================
def CreateSequence(s, t):
    # s is num standards
    # t is num targets
    # Sequence will be created of len(s+t)
    # TT trials are possible (need to add code to prevent them)
    seq = []
    seq.append(['S' for x in range(s)])
    seq.append(['T' for x in range(t)])
    seq = listFlatten(seq)
    random.seed()
    random.shuffle(seq) # shuffles in-place
    return seq

def InitTriangle(size=50):
    return psychopy.visual.Polygon(
                win=win,
                edges=3,
                units='pix',
                radius=size,
                lineWidth=3,
                lineColor=[1, 1, 1],
                fillColor=bg_color,
                pos=[0, 0],
                ori=0,
                name='off'
            )

def InitFixation(size=50):
    return psychopy.visual.ShapeStim(
                win=win,
                units='pix',
                size = size,
                fillColor=[1, 1, 1],
                lineColor=[1, 1, 1],
                lineWidth = 1,
                vertices = 'cross',
                name = 'off', # Used to determine state
                pos = [0, 0]
            )

def InitPhotosensor(size=50):
    # Create a circle in the lower right-hand corner
    # Will be size pixels large
    # Initiate as color of bg (off)
    return psychopy.visual.Circle(
            win=win,
            units="pix",
            radius=size,
            fillColor=bg_color,
            lineColor=bg_color,
            lineWidth = 1,
            edges = 32,
            name = 'off', # Used to determine state
            pos = ((win_w / 2) - size, -((win_h / 2) - size))
        )

def SetStimulus(stim, c):
    # c is state
    # Make sure it's either on or off
    c = c.lower(); 
    if c != 'on' and c != 'off':
        print('Invalid setting'); sys.stdout.flush()
        return
        
    if c == 'on':
        stim.name = 'on';
        stim.color = (1, 1, 1);
    if c == 'off':
        stim.name = 'off';
        stim.color = bg_color;

def RotateTriangle(tri, a):
    # Sets rotation to a, does not rotate by a
    tri.ori = a

def MsToFrames(ms, fs):
    dt = 1000 / fs;
    return np.round(ms / dt).astype(int);

def DegToPix(h, d, r, deg):
    # Source: https://osdoc.cogsci.nl/3.2/visualangle/
    deg_per_px = degrees(atan2(.5*h, d)) / (.5*r)
    size_in_px = deg / deg_per_px
    return size_in_px

def listFlatten(df):
    t = []
    for i in range(len(df)):
        for j in range(len(df[i])):
            t.append(df[i][j])
    return t

def CreateMrkStream():
    info = pylsl.stream_info('P300_Markers', 'Markers', 1, 0, pylsl.cf_string, 'unsampledStream');
    outlet = pylsl.stream_outlet(info, 1, 1)
    return outlet;

if __name__ == "__main__":
    # Create PsychoPy window
    win = psychopy.visual.Window(
        screen = 0,
        size=[win_w, win_h],
        units="pix",
        fullscr=True,
        color=bg_color,
        gammaErrorPolicy = "ignore"
    );
    
    # Initialize LSL marker stream
    mrkstream = CreateMrkStream();
    
    time.sleep(5)
    
    # Initialize photosensor
    photosensor = InitPhotosensor(50)
    fixation = InitFixation(30)
    triangle = InitTriangle(np.round(DegToPix(20.3, 48.26, 1080, 4))) # ~181

    # Run through paradigm
    Paradigm()
    