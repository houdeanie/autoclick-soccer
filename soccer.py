import pyautogui
from pynput.keyboard import *
import cv2
import numpy as np
from matplotlib import pyplot as plt
import killswitch
import time
import mss
import mss.tools
from PIL import ImageGrab


pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0
# first take a screenshot of the image
scname = 'screenshot.png'
ballname = 'ball.png'
folder1 = 'sc/'
folder2 = 'sc1/'
folder3 = 'sc2/'

##### Screenshot methods #######

def pyautoguisc(left, top, width, height, filename):
    monitor = {'top': top, 'left': left, 'width': width, 'height': height}
    start = time.time()
    pyautogui.screenshot(filename)
    end = time.time()
    print(end - start)

def msssc(left, top, width, height, filename):
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {'top': top, 'left': left, 'width': width, 'height': height}
        # Grab the data
        sct_img = sct.grab(monitor)
        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

def PILgrab(left, top, width, height, filename):
    monitor = {'top': top, 'left': left, 'width': width, 'height': height}
    screen =  np.array(ImageGrab.grab(bbox=(0,40, 800, 850)))

# just a list for future refrence
# methods for opencv
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

METHOD = 'cv2.TM_CCOEFF'

#def (self, parameter_list):
#    pass
# detect where ball is relative to screen
# return centre x and y of ball
def detect(target, source):
    # Load image - work in greyscale as 1/3 as many pixels
    img = cv2.imread(source,cv2.IMREAD_GRAYSCALE)
    #img2 = img.copy()
    template = cv2.imread(target,cv2.IMREAD_GRAYSCALE)
    
    # remove big number center
    img[80:155,122:170] = 255 #- img[117:191,122:162]

    # Negate image so whites become black
    img=255-img

    # get w and h of template
    w, h = template.shape[::-1]

    #img = img2.copy()
    method = eval(METHOD)

    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # find center of rec
    centerX = (top_left[0] + bottom_right[0]) / 2
    centerY = (top_left[1] + bottom_right[1]) / 2

    return centerX, centerY

#  ==========================

def blackball(target, source, i):
    img = cv2.imread(source,cv2.IMREAD_GRAYSCALE)
    #template = cv2.imread(target,cv2.IMREAD_GRAYSCALE)

    # Overwrite "Current Best" with white - these numbers will vary depending on what you capture
    img[80:155,122:170] = 255 #- img[117:191,122:162]

    # Negate image so whites become black
    img=255-img

    nz = cv2.findNonZero(img)
    # Find top, bottom, left and right edge of ball
    a = nz[:,0,0].min()
    b = nz[:,0,0].max()
    c = nz[:,0,1].min()
    d = nz[:,0,1].max()
    print('a:{}, b:{}, c:{}, d:{}'.format(a,b,c,d))

    # Average top and bottom edges, left and right edges, to give centre
    c0 = (a+b)/2
    c1 = (c+d)/2
    print('Ball centre: {},{}'.format(c0,c1))
    cv2.imwrite('gs/greyscale' + str(i) + '.png',img)

    return c0, c1

#  autoclick buttons
resume_key = Key.f1
pause_key = Key.f2
exit_key = Key.f3

pause = True
running = True

def on_press(key):
    global running, pause

    if key == resume_key:
        pause = False
        print("[Resumed]")
    elif key == pause_key:
        pause = True
        print("[Paused]")
    elif key == exit_key:
        running = False
        print("[Exit]")
        quit()

def display_controls():
    print("// AutoClicker by iSayChris")
    print("// - Settings: ")
    print("\t delay = " + str(delay) + ' sec' + '\n')
    print("// - Controls:")
    print("\t F1 = Resume")
    print("\t F2 = Pause")
    print("\t F3 = Exit")
    print("-----------------------------------------------------")
    print('Press F1 to start ...')

# Number of pixels under ball center to click
buffer = 20
suffix = '.png'

fname = 'screenshot'
delay = 0.1 # in seconds

def main():
    desiredscore = 1000
    currentscore = 0
    lis = Listener(on_press=on_press)
    lis.start()
    eloc = {'left': 650, 'top': 95, 'width': 932 - 650, 'height': 534 - 95}
    display_controls()
    i = 0
    
    while currentscore < desiredscore:
        if not pause:
            #takesc()
            print("=========")
            msssc(eloc['left'], eloc['top'], eloc['width'], eloc['height'], folder1 + fname + str(i) + suffix)

            #centreX, centreY = blackball(ballname, folder + fname + str(i) + suffix, i)
            centreX, centreY = detect(ballname, folder1+fname + str(i) + suffix)
            centreX = centreX + eloc['left']
            centreY = centreY + eloc['top']
            print(centreX, centreY)
            if centreY > (eloc['height'])/2 + eloc['top']:
                pyautogui.click(x=centreX, y=centreY+buffer)
                currentscore += 1
                pyautogui.PAUSE = delay
                i +=1 
                #print(currentscore)
        #i = 0

        #
            #width, height = pyautogui.size()
            #for i in range(int(1366/2 -200), int(1366/2 +200)):
            #pyautogui.click(x=1366/2, y=730)
            #print(width, height)
        #    pyautogui.PAUSE = delay
    lis.stop()


if __name__ == "__main__":
    main()