import mss
import numpy as np
import threading
import winsound
import PySimpleGUI as sg
import time

import cv2

def is_similar(image1, image2):
    return image1.shape == image2.shape and not(np.bitwise_xor(image1,image2).any())

def Grabber (monitor_number, height , width):

    with mss.mss() as sct:
        mon = sct.monitors[monitor_number]

        

        # The screen part to capture
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"] // width,
            "height": mon["height"] // height,
            "mon": monitor_number,
        }
        output = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)

        # Grab the data
        img = np.array(sct.grab(monitor)) # BGR Image
        
        return img


def time_as_int():
    return int(round(time.time() * 100))


def validInputs(monitor_number, height, width, interval):
    test = True
    if(monitor_number == ''):
        test = False
    elif(height == ''):
        test = False
    elif(width == ''):
        test = False
    elif(interval == ''):
        test = False
    return test




def main():
    # ----------------  Create Form  ----------------
    sg.theme('Black')

    layout = [[sg.Text('Time passed', size=(16, 1), font=('Helvetica', 20),
                    justification='center')],
            [sg.Text('', size=(8, 2), font=('Helvetica', 18),
                    justification='center', key='text')],
            [sg.Text('Please enter monitor number, dimensions [1/x] and alarm interval [sec]')],
            [sg.Text('Monitor:', size =(12, 1)), sg.InputText(size= (6,1))],
            [sg.Text('Height: 1/', size =(12, 1)), sg.InputText(size= (6,1))],
            [sg.Text('Width:  1/', size =(12, 1)), sg.InputText(size= (6,1))],
            [sg.Text('Alarm intervals:', size =(12, 1)), sg.InputText(size= (6,1))],
            [sg.Button('Start', key='-RUN-PAUSE-', button_color=('white', '#001480')),
            sg.Button('Reset', button_color=('white', '#007339'), key='-RESET-'),
            sg.Button('Show', button_color=('white', '#007339'), key='-SHOW-'),
            sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]]

    window = sg.Window('Running Timer', layout,
                    no_titlebar=False,
                    auto_size_buttons=False,
                    keep_on_top=False,
                    grab_anywhere=True,
                    element_padding=(0, 0),
                    finalize=True,
                    element_justification='c')

    current_time, paused_time, paused = 0, 0, True
    
    # init with monitor 1 (whole screen)
    old_img = Grabber(1, 1, 1)

    
    # for debugging
    ##cv2.namedWindow("area")
    ##cv2.imshow("area",old_img)
    ##cv2.waitKey(0)
    
    paused_time = start_time = time_as_int()
    current_time = 0
    
    wating = False
    wait_time = 0
    img = old_img

    monitor_number = 1
    height = 1
    width = 1
    while True:
         # --------- Read and update window --------
        event, values = window.read(timeout=10)
        if event in (sg.WIN_CLOSED, 'Exit'):        # EXIT
            break
        
        monitor_number = values[0]
        height = values[1]
        width = values[2]
        interval = values[3]

        # Check inputs
        if validInputs(monitor_number, height, width, interval):
            
            # cast as integers
            monitor_number = int(monitor_number)
            height = int(height)
            width = int(width)
            interval = float(values[3])
       
            if not paused:
                
                current_time = time_as_int() - start_time
                

                img = Grabber(monitor_number, height, width)
                ##cv2.imshow("test", img)
                if not is_similar(img, old_img):
                    
                    if not wating:
                        ##winsound.Beep(400,100)
                        winsound.MessageBeep()
                        wait_time =  (current_time // 100) % 60 
                        wating = True
                    
                    
                    
                    if wait_time + interval< (current_time // 100) % 60:
                        wating = False


                

            
            # --------- Do Button Operations --------
            
            if event == '-RESET-':
                paused_time = start_time = time_as_int()
                current_time = 0
                old_img = Grabber(monitor_number, height, width)
                wating = False
                sg.theme('Black')
            elif event == '-RUN-PAUSE-':
                old_img = Grabber(monitor_number, height, width)
                paused = not paused
                if paused:
                    paused_time = time_as_int()
                else:
                    start_time = start_time + time_as_int() - paused_time
                # Change button's text
                window['-RUN-PAUSE-'].update('Start' if paused else 'Pause')
            elif event == '-SHOW-':
                cv2.imshow("Area", Grabber(monitor_number, height, width))
                cv2.waitKey(100)
            
            elif event == 'Edit Me':
                sg.execute_editor(__file__)
        
        # --------- Display timer in window -------- 
        window['text'].update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
                                                            (current_time // 100) % 60,
                                                            current_time % 100))

        
        # show image for debugging
        ##cv2.imshow("area", img - old_img)
        ##cv2.waitKey(1)
        

    window.close()







main_thread = threading.Thread(name='main program',
                               target=main, daemon=True, args=[])



main_thread.start()

main_thread.join()
