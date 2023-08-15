import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import serial
import queue
import time
import pandas as pd
import numpy as np
COM_PORT1 = "/dev/tty.usbserial-120" 
COM_PORT2 = "/dev/tty.usbserial-110"


# Create a command queue for key
cmd_queue = queue.Queue(10)
data_queue = queue.Queue(20)

columns=["module","count","time","adc","sipmv","deadtime","temp"]
bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130]
bins = np.arange(0,200,5)

#values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#df_data = pd.DataFrame(columns=columns)
#plt.bar(bins,values)
df_data = pd.DataFrame(columns=columns)
#print(df_data)
hist_m1 = [0,0,0,0,0,0,0,0,0,0,0,0,0]
hist_m2 = [0,0,0,0,0,0,0,0,0,0,0,0,0]
bin_edges1 = []

bin_edges2 = []

# Keep program running as long as True. Terminate by writing "quit" in terminal window
run_app = True


# Keyboard thread to detect input commands and put them in the command queue
def keyboard(run_app):
    while run_app():
        cmd = input("\r\n> ")
        cmd_queue.put(cmd)
        time.sleep(0.5)


def decode_data(data):
    data = data.decode(errors='ignore').strip("\r\n")
    #print(data)
    if len(data) > 0:
        if data[0] != "#":
            data = data.split(" ")
            data = [float(x) for x in data]
        else:       
            data = ""
    return data
    #print(type(data))
    

# Thread for reading serial data
def serial_data1(run_app):
    # Open serial port
    ser = serial.Serial(COM_PORT1, 9600,timeout = 1)
    while run_app():
        #no_bytes = ser.inWaiting()
        data = ser.readline()
        data = decode_data(data)
        
        
        if len(data) > 0:
            
            data.insert(0,1)
            data_queue.put(data)    
            #print(data_queue.qsize())        
        time.sleep(0.001)


    ser.close()

# Thread for reading serial data
def serial_data2(run_app):
    # Open serial port
    ser = serial.Serial(COM_PORT2, 9600,timeout = 1)
    while run_app():
        #no_bytes = ser.inWaiting()
        data = ser.readline()
        data = decode_data(data)
    
        if len(data) > 0:
            data.insert(0,2)
            data_queue.put(data)    
            #print(data_queue.qsize())        
        time.sleep(0.001)

    ser.close()

def detector(run_app):

    #global df_data
    #global columns
    #global bins
    global hist_m1
    global bin_edges1
    global hist_m2
    global bin_edges2
    global bins
    global df_data
    print("starting detector")
    
    columns=["module","count","time","adc","sipmv","deadtime","temp"]
    #bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130]
#values = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #df_data = pd.DataFrame(columns=columns)

    while run_app():
        if not data_queue.empty():
            data = data_queue.get()
            
            #print(data)
            df_temp = pd.DataFrame([data],columns=columns)
            #print(df_temp["count"])
            if (df_temp["count"].values == 1.0) & (df_temp["module"].values == 1):
                print("first")
                df_data = pd.DataFrame(columns=columns)
            #if (True & True):

            #if ( df_temp[ (df_temp["module"]==1) & (df_temp["count"] == 1.0) ] ):
            #    print("first")
            #print(df_temp)
            #print(df_data)
            df_data = pd.concat([df_data,df_temp],ignore_index=True)
    
             
            sipmv1 = df_data[df_data["module"]==1]["sipmv"].values
            sipmv2 = df_data[df_data["module"]==2]["sipmv"].values
            
            if len(sipmv1) > 0:
                hist_m1, bin_edges1 = np.histogram(sipmv1,bins=bins)
            if len(sipmv2) > 0:
                hist_m2, bin_edges2 = np.histogram(sipmv2,bins=bins)

            

            #hist_m1 = df_data[df_data["module"]==1]["sipmv"].hist()
            #print(hist_m1)
            #print(bin_edges1)
    
    
    
        time.sleep(0.001)



def animate(oFrame):
    #plt.cla()
    global hist_m1
    global bin_edges1
    global hist_m2
    global bin_edges2
    
    global bins
    global df_data
    #plt.clf()
    ax1.cla()
    ax2.cla()

    ax1.set_title('Cosmic Watch 1')
    ax1.set_xlabel('Voltage')
    ax1.set_ylabel('[V]')
    
    ax2.set_title('Cosmic Watch 2')
    ax2.set_xlabel('Voltage')
    ax2.set_ylabel('[V]')

    try:
        df_data[df_data["module"]==1]["sipmv"].hist(bins=bins,ax=ax1,color="blue")
    except:
        #ax1.cla()
        ax1.plot([],[])

    try:
        df_data[df_data["module"]==2]["sipmv"].hist(bins=bins,ax=ax2,color="blue")
    except:
        #ax2.cla()
        ax2.plot([],[])

    #    print(bins)
    #    print(hist_m1)
    #    #ax1.bar(bins[1:],hist_m1)
    #    ax2.bar(bins[1:],hist_m2)
        

        #hist.set_data([0,10,20,30],[2,3,4,2])
       # hist.
    #df_data.hist(bins=bins)
    #return hist,





if __name__ == "__main__":


    fig, [ax1,ax2] = plt.subplots(1,2)
    #fig.set_tight_layout()
    ax1.set_title('Cosmic Watch 1')
    ax1.set_xlabel('Voltage')
    ax1.set_ylabel('[V]')
    
    ax1.set_title('Cosmic Watch 2')
    ax1.set_xlabel('Voltage')
    ax1.set_ylabel('[V]')
    
    #ax.set_xlim( 0, 130)
    #ax.set_ylim( 0, 10)
    ax1.plot([],[])
    ax2.plot([],[])
   
    
    #hist, = ax.plot([],[])
   
    # Create threads
    #keyboard_thread = threading.Thread(target=keyboard, args=(lambda: run_app,))fig, ax = plt.subplots()
    serial_thread1 = threading.Thread(target=serial_data1, args=(lambda: run_app,))
    serial_thread2 = threading.Thread(target=serial_data2, args=(lambda: run_app,))
    detector_thread = threading.Thread(target=detector, args=(lambda: run_app,))
    # Set threads as deamon -- threads are automatically killed if program is killed
    #keyboard_thread.daemon = True
    serial_thread1.daemon = True
    serial_thread2.daemon = True
    
    detector_thread.daemon = True

    # Start threads
    #keyboard_thread.start()
    serial_thread1.start()
    serial_thread2.start()
    
    detector_thread.start()
    #serial_thread2.start()

   

    #df_data = plt.hist([])
    #hist = plt.hist([])
   


    #while run_app:

    animation = animation.FuncAnimation(fig, animate, interval=500 )
    plt.show()
    #serial_thread1.join()
    #serial_thread1.join()
    #detector_thread.join()
    #keyboard_thread.join()
    
    
        #while not cmd_queue.empty():
        #    cmd = cmd_queue.get()
        #    if "quit" == cmd.lower():
        #        run_app = False
        #    if "q" == cmd.lower():
        #        run_app = False
        #time.sleep(0.1)