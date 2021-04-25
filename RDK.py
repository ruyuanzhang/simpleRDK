'''
A simple random dot kinematogram (RDK) experiment for perceptual decision making

History:
    2021/04/25 RYZ create it
'''

from psychopy import core, monitors, clock, visual, event, data
from psychopy.tools import monitorunittools
from psychopy.hardware import keyboard
from psychopy.visual import circle
import numpy as np
import csv
from time import localtime, strftime

# ======= parameter you want to change ========
subjID = 'RYZ' # initials of the subject, to save data
wantSave = True # save data or not
# =============================================


# ================ exp setting ==================
cohs=[0, 0.02, 0.05, 0.08, 0.1, 0.2, 0.5] # coherence level
#cohs=[0, 0.02, 0.5] # coherence level
stimDir = [-1, 1]  # -1, left;1, right
fieldRadius = 5  # in deg
nTrialsPerCond = 1 # how many trials per condition
stimDur = 5  # sec, stim duration or a key press comes first
delayDur = 1  # sec, delay of stim onset after fixation
speedDeg = 10.0  # deg/sec, shall convert to deg/frame
dotDensity = 0.6  # dots/deg^2
dotSize = 0.125  # deg, diameter

# ======= setup hardwares =======
# you may want to change your monitor settings
mon = monitors.Monitor('hospital6')
mon.setDistance(57)  # View distance cm
mon.setSizePix([1920, 1080])
mon.setWidth(52.71)  # cm
myWin = visual.Window([1000, 1000], units='deg', monitor=mon, color=(-1, -1, -1), checkTiming=True)
fps = myWin.getActualFrameRate()

event.globalKeys.clear()
event.globalKeys.add(key='q', func=core.quit)  # global quit key
kb = keyboard.Keyboard()  # create kb object

# let's do some calculation before going further
speedFrame = speedDeg / fps  # how many deg/frame
dotSizePix = monitorunittools.deg2pix(dotSize, mon)  # calculate dotSizePix for DotStim object
nDots = round(np.pi * fieldRadius ** 2 * dotDensity)  # calcuate nDots
maxFrames = round(stimDur / myWin.monitorFramePeriod)

nTrials = nTrialsPerCond * len(cohs) * len(stimDir)
stimList = []
for dire in stimDir:
    for coh in cohs:
        stimList.append({'direction':dire, 'coherence':coh})
trials=data.TrialHandler(stimList, nTrialsPerCond)

#  ====== define stimulus components =======
# define fixation
fixation = circle.Circle(win=myWin, units='deg', radius=0.25, lineColor=0, fillColor=0)
# define dots 
dots = visual.DotStim(win=myWin, nDots=nDots, units='deg', fieldSize=[fieldRadius * 2, fieldRadius * 2],
                         fieldShape='circle', speed=speedFrame, dotSize=dotSizePix, dotLife=-1) 
                         # note here dotSize is in pixels, speed is in deg/frame


# define welcome instruction interface
instrText = \
    '欢迎参加这个实验!\n \
    您将在屏幕上看到一系列运动的点\n \
    一旦这些点开始运动您需要按方向键(左/右)来判断整体的运动方向。\n \
    您可以不等运动点消失直接按键, \n \
    每次您必须要按键反应，实验才能继续。\n \
    请您又快又准确的反应! \n \
    如果您理解了以上的话，请按空格键继续'
tex = visual.TextStim(win=myWin, text=instrText, font='SimHei')
tex.draw()
myWin.flip()
kb.start()
kb.waitKeys(keyList=['space'], waitRelease=True)
kb.stop()
myWin.flip()


# do it!!!
#  =========== main experiment loop ========
for trial in trials: # use trialHandler

    # draw fixation
    fixation.draw()
    myWin.flip()
    
    # add 1s delay while do some calculation
    ISI=clock.StaticPeriod(screenHz=fps)
    ISI.start(delayDur)

    dots.dir = 180 if trial['direction']==-1 else 0 # set direction
    dots.coherence = trial['coherence']
    ISI.complete()
    
    # show moving stim
    kb.clock.reset()  # reset the keyboard clock
    kb.start()  # keyboard start recoding
    for i in range(maxFrames):  #
        fixation.draw()
        dots.draw()
        myWin.flip()
        keys = kb.getKeys(keyList=['left', 'right'])
        if keys:
            break
    if not keys:
        keys = kb.waitKeys(keyList=['left', 'right'])  # still waiting after stimulus
    kb.stop()
    myWin.flip()

    # save data in this trial
    trials.addData('RT', keys[0].rt)
    trials.addData('choice', -1 if keys[0].name == 'left' else 1)
    trials.addData('correct', 1 if trials.data['choice'][trials.thisIndex] == trial['direction'] else 0)

# ====cleanup and save data to csv======
if wantSave: # save data
    # we want to save direction, stimType, RT, choice into a CSV file
    fileName = strftime('%Y%m%d%H%M%S', localtime())
    fileName = f'{fileName}_{subjID}'
    # Save more information into a numpy file 
    dataInfo = '''
        direction: -1,left; 1, right \n
        cohs: coherence levels \n
        choice: -1, left; 1, right \n
        RT in secs related to onset of the motion stimulus \n
        correct: 1, choice correct; 0, wrong
    '''
    # create a result dict
    trials.extraInfo={
        'subjID': subjID,
        'dataInfo': dataInfo,
        'time': strftime('%Y-%m-%d-%H-%M-%S', localtime()),
    }
    trials.saveAsExcel(fileName=fileName, sheetName='rawData') # save as excel
    trials.saveAsPickle(fileName=fileName) # # save as pickle
    

