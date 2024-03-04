import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import serial
import queue
import time
import pandas as pd
import numpy as np
COM_PORT1 = "/dev/tty.usbserial-2110" 
COM_PORT2 = "/dev/tty.usbserial-2120"


# Create a command queue for key
cmd_queue = queue.Queue(10)
data_queue = queue.Queue(20)

max_value = 200
columns=["module","count","time","adc","sipmv","deadtime","temp","rate"]
bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130]
bins = np.arange(0,max_value,5)

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
            # calculate count rate
            data.append(1000*(data[0]/(data[1]-data[4])))
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
    
    columns=["module","count","time","adc","sipmv","deadtime","temp","rate"]
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
            
            #print(df_data)
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
    global max_value
    global bins
    global df_data
    #plt.clf()
    ax1.cla()
    ax2.cla()
    ax3.cla()
    ax4.cla()
    ax5.cla()
    ax6.cla()
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)
    ax4.grid(True)
    ax5.grid(True)
    ax6.grid(True)


    title1 = "Raw data (Max: {0} mV, Counts: {1}) ".format(df_data[df_data["module"]==1]["sipmv"].max(),df_data[df_data["module"]==1]["count"].max())
    ax1.set_title(title1)
    ax1.set_xlabel('Voltage [mV]')
    ax1.set_ylabel('#Counts')
    
    title2 = "Coincidence data (Max: {0} mV, Counts: {1}) ".format(df_data[df_data["module"]==2]["sipmv"].max(),df_data[df_data["module"]==2]["count"].max())
   
    ax2.set_title(title2)
    ax2.set_xlabel('Voltage [mV]')
    ax2.set_ylabel('#Counts')

    ax3.set_title('Raw rate')
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Counts/s')
    

    ax4.set_title('Coincidence rate')
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Counts/s')


    ax5.set_title('Temperature')
    ax5.set_xlabel('Time [s]')
    ax5.set_ylabel('°C')

    ax6.set_title('Temperature')
    ax6.set_xlabel('Time [s]')
    ax6.set_ylabel('°C')
    

    
    if df_data[df_data["module"]==1]["sipmv"].max() > max_value:
        max_value = df_data[df_data["module"]==1]["sipmv"].max()
        bins = np.arange(0,max_value,5)
    if df_data[df_data["module"]==2]["sipmv"].max() > max_value:
        max_value = df_data[df_data["module"]==1]["sipmv"].max()
        bins = np.arange(0,max_value,5)




    #if df_data[df_data["module"]==1]["sipmv"] > max_value:
    #    max_value = 


    #print(df_data)

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

    #print(df_data)
    #try:
        #count1 = df_data[df_data["module"]==1 ]["count"].

    # Get the last 10 seconds of data    
    duration = df_data[(df_data["module"]==1)]["time"].max()
    if duration  > 0:
        plot_window_floor = duration - 0
    else:
        plot_window_floor = 0
    filter1 = (df_data["module"]==1) & (df_data[(df_data["module"]==1)]["time"] >= plot_window_floor  )
    filter2 = (df_data["module"]==2) & (df_data[(df_data["module"]==2)]["time"] >= plot_window_floor  )

    #print(df_data[df_data["module"]==1])
    try:
        rate1 = df_data[df_data["module"]==1]["rate"] #/25 # cm2
        time1 = df_data[df_data["module"]==1]["time"]/1000
        temp1 = df_data[df_data["module"]==1]["temp"]
        ax3.plot(time1,rate1,color="blue")
        ax5.plot(time1,temp1,color="blue")

        ax3.set_ylim([0, 6])
        ax5.set_ylim([0, 30])
    except:
        ax3.plot([],[],color="blue")
        ax5.plot([],[],color="blue")
    
    try:
        rate2 = df_data[df_data["module"]==2]["rate"] #/25 # cm2
        time2 = df_data[df_data["module"]==2]["time"]/1000
        temp2 = df_data[df_data["module"]==2]["temp"]
        ax4.plot(time2,rate2,color="blue")
        ax6.plot(time2,temp2,color="blue")
        #print(time2)
        ax4.set_ylim([0, 0.5])
        ax6.set_ylim([0, 30])
    except:
        ax4.plot([],[],color="blue")
        ax6.plot([],[],color="blue")


   

    #time1 = df_data[filter]["time"]
    #deadtime1 = df_data[filter]["time"]
    #count1 =  df_data[filter]["time"]
        #deadtime1 = df_data[df_data["module"]==1]["deadtime"]
        #len1 = len(count1)

        #print(count1[0:])
        #df_data[df_data["module"]==1]["sipmv"].hist(bins=bins,ax=ax2,color="blue")

        


    #except:
    #    ax3.plot([],[])

    #    print(bins)
    #    print(hist_m1)
    #    #ax1.bar(bins[1:],hist_m1)
    #    ax2.bar(bins[1:],hist_m2)
        

        #hist.set_data([0,10,20,30],[2,3,4,2])
       # hist.
    #df_data.hist(bins=bins)
    #return hist,





if __name__ == "__main__":


    fig, [(ax1, ax2), (ax3, ax4),(ax5, ax6)] = plt.subplots(3,2,gridspec_kw={'height_ratios': [4, 2,2]})
    fig.suptitle('Cosmic Watch', fontsize=16)
    fig.set_tight_layout(True) 
    ax1.set_title('Raw data')
    ax1.set_xlabel('Voltage [mV]')
    ax1.set_ylabel('#Counts')
    
    ax2.set_title('Coincidence data')
    ax2.set_xlabel('Voltage [mV]')
    ax2.set_ylabel('#Counts')
    
    ax3.set_title('Rate rate')
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Counts/s')
    

    ax4.set_title('Coincidence rate')
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Counts/s')

    ax5.set_title('Temperature')
    ax5.set_xlabel('Time [s]')
    ax5.set_ylabel('°C')

    ax6.set_title('Temperature')
    ax6.set_xlabel('Time [s]')
    ax6.set_ylabel('°C')
    


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
    time.sleep(0.5)
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