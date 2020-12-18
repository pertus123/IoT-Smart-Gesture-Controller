import copy
import random
from threading import Thread
from tkinter.ttk import Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as Tk
import paho.mqtt.client as mqtt
import struct
import time
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import collections
import testtt
import graph

callback_state = False
read_mode = False
saved_read = False
mqttmsg = ""
length = 0
switch = 0

Rax = []
Ray = []
Raz = []
scale_x = []
scale_y = []
scale_z = []
flex1 = []
flex2 = []
flex3 = []
flex4 = []


class MqttConnect:
    def __init__(self, broker, plotLength = 300, dataNumBytes=2, numPlots=1):
        self.broker = broker

        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.numPlots = numPlots
        # self.rawData = bytearray(numPlots * dataNumBytes)
        # self.dataType = None
        # if dataNumBytes == 2:
        #     self.dataType = 'h'  # 2 byte integer
        # elif dataNumBytes == 4:
        #     self.dataType = 'f'  # 4 byte float
        self.datay = []
        self.datax = []

        for i in range(numPlots):  # give an array for each type of data and store them in a list
            self.datay.append(collections.deque(maxlen=plotLength))
            self.datax.append(collections.deque(maxlen=plotLength))

        self.isRun = True
        self.isReceiving = False
        self.isGetSenserData = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.counter = 0
        self.Temp = 0
        self.Temp2 = 0

        self.client = mqtt.Client()
        try:
            self.mqttConnect(self.client)
        except Exception as ex:
            print("[Error] Mqtt 연결에 실패했습니다. : " + str(ex))

    def getSenserData(self, frame, lines, lineValueText, lineLabel, timeText, pltInterval, ax):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000) # the first reading will be erroneous
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')

        #privateData = copy.deepcopy(self.rawData[:])
        if self.isGetSenserData is True:
            try:
                for i in range(self.numPlots):
                    # data = privateData[(i * self.dataNumBytes):(self.dataNumBytes + i * self.dataNumBytes)]
                    # value = struct.unpack(self.dataType, data)
                    self.datay[i].append(mqttmsg['Acc'][i])
                    self.datax[i].append(self.counter)
                    # lines[i].set_data(range(self.plotMaxLength), self.data[i])
                    lines[i].set_data(self.datax[i], self.datay[i])

                    if self.counter < self.plotMaxLength:
                        self.Temp = self.counter
                    else:
                        self.Temp = self.plotMaxLength - 1

                    if self.Temp2 < self.datay[i][self.Temp]:
                        ax.set_ylim(-self.Temp2 - 30, self.Temp2 + 30)
                        self.Temp2 = self.datay[i][self.Temp]

                    if self.counter > self.plotMaxLength:
                        ax.set_xlim([self.counter - self.plotMaxLength, self.counter])
                    else:
                        ax.set_xlim([0, self.counter])

                    try:
                        lineValueText[i].set_text('[' + lineLabel[i] + '] = ' + str(self.datay[i][self.Temp]))
                    except Exception as ex:
                        print("lineValueText error : " + str(ex))
                    # if(self.counter == self.plotMaxLength):
                    #     self.isGetSenserData = False
                    #     print("[Info] Graph Data Parse End")

                self.counter += 1
                if self.counter == 100:
                    self.isGetSenserData = False
                    print("[Info] Senser Data Collect Complete")
            except Exception as ex:
                print("[Error] 데이터 불러오는데 에러가 발생했습니다 : " + str(ex))

    def on_connect(self, client, data, flag, rc):
        print("[Info] Mqtt Server Connected with Code : " + str(rc))

    def on_publish(self, client, data, msg):
        print("on_publish")

    def on_message(self, client, userdata, message):
        global length, callback_state, mqttmsg, switch
        x = message.payload.decode("utf-8")

        if read_mode is True:
            print(x)

        # Json 파싱
        mqttmsg = json.loads(x)

        # callback_state가 True이면 값을 저장한다.
        if callback_state is True:
            switch = 1
            Rax.append(mqttmsg['Acc'][0])
            Ray.append(mqttmsg['Acc'][1])
            Raz.append(mqttmsg['Acc'][2])
            scale_x.append(mqttmsg['Gy'][0])
            scale_y.append(mqttmsg['Gy'][1])
            scale_z.append(mqttmsg['Gy'][2])
            flex1.append(mqttmsg['Flex'][0])
            flex2.append(mqttmsg['Flex'][1])
            flex3.append(mqttmsg['Flex'][2])
            flex4.append(mqttmsg['Flex'][3])
            length = len(Rax)
            # print("\r Progress Percent {:4.2f}%...".format(length / self.plotMaxLength * 100))
            print("\r Reading.. ")
            print("\r .")
            if length > 0 and callback_state is False and switch == 1:
                callback_state = False
                switch = 0
                print("[Info] Senser data Save Complete / Check Length : " + str(len(Rax)))

        # print("message received " ,str(message.payload.decode("utf-8")))
        # print("message topic=",message.topic)

    def callback_status(self, client, userdata, message):
        global callback_state
        self.receive = message.payload.decode("utf-8")
        print("[Message - switch/state decoded] : " + self.receive)

        if self.receive == "true":
            print("[Info] Data Input Start")
            callback_state = True
        elif self.receive == "false":
            callback_state = False
            if length < 500:
                print("[Info] Data Input Canceled")

        print("[Message Received] Status_read Switch : " + str(callback_state))

    def callback_print(self, client, userdata, message):
        global read_mode, length, callback_state
        receive = message.payload.decode("utf-8")
        print("[Message - switch/read decoded] : " + receive)

        # 다음과 같은 메세지를 받았을때 세번의 비교과정을 통해서 비교를 한후 각각의 상관계수를 반환한다
        # 첫번째는 그대로 리스트에 넣고 그 다음꺼는 비교후에 상관계수를 뽑아서 일정 이상이면 세번째로 넘어가고 아니면 다시 시도
        # 세개 리스트 다 채워졌으면 그대로 DB에 반영
        if receive == "windowOn":  ###############################
            print("[Info] Mode On 1/3...")
            callback_state = True

        if receive == '0':
            for i in range(0, len(Rax)):
                print(flex1[i], flex2[i], flex3[i], flex4[i])
            read_mode = False
            callback_state = False
            size = len(Rax)
            #print(size)



                #graph.insert(Rax[i], Ray[i], Raz[i], scale_x[i], scale_y[i], scale_z[i], flex1[i], flex2[i], flex3[i], flex4[i])

            for i in range(0, 9):
                fx1 = testtt.dtwtest(flex1[1], fx[i][0])
                fx2 = testtt.dtwtest(flex2[2], fx[i][1])
                fx3 = testtt.dtwtest(flex3[3], fx[i][2])
                fx4 = testtt.dtwtest(flex4[4], fx[i][3])
                result = (fx1 + fx2 + fx3 + fx4) / 4
                if result >= 80:

            result = (fx1 + fx2 + fx3 + fx4) / 4
            print(result)

            '''
            ax = testtt.dtwtest(Rax, "AccX")
            ay = testtt.dtwtest(Ray, "AccY")
            az = testtt.dtwtest(Raz, "AccZ")
            gx = testtt.dtwtest(scale_x, "GyX")
            gy = testtt.dtwtest(scale_y, "GyY")
            gz = testtt.dtwtest(scale_z, "GyZ")
            fx1 = testtt.dtwtest(flex1, "FlexA")
            fx2 = testtt.dtwtest(flex2, "FlexB")
            fx3 = testtt.dtwtest(flex3, "FlexC")
            fx4 = testtt.dtwtest(flex4, "FlexD")
            print(ax)
            print(ay)
            print(az)
            print(gx)
            print(gy)
            print(gz)
            print(fx1)
            print(fx2)
            print(fx3)
            print(fx4)
            result = (abs(ax)+abs(ay)+abs(az)+abs(gx)+abs(gy)+abs(gz)+abs(fx1)+abs(fx2)+abs(fx3)+abs(fx4))/10
            print(result)
            '''
        if receive == 'clear':
            del Rax[:]
            del Ray[:]
            del Raz[:]
            del scale_x[:]
            del scale_y[:]
            del scale_z[:]
            del flex1[:]
            del flex2[:]
            del flex3[:]
            del flex4[:]
            print("[Info] Delete Rax List data : " + str(len(Rax)))

        # 콘솔에서 값 읽는 모드
        if receive == "true":
            read_mode = True
            print("read_mode : " + str(read_mode))
        elif receive == "false":
            read_mode = False
            print("read_mode : " + str(read_mode))

        if receive == "sense_on":
            self.isGetSenserData = True
            print("isGetSenserData : " + str(self.isGetSenserData))
        elif receive == "sense_off":
            self.isGetSenserData = False
            print("isGetSenserData : " + str(self.isGetSenserData))

        # 저장된 데이터를 콘솔에서 읽는 모드
        if receive == "saveload":
            try:
                if len(Rax) > 0:
                    for i in range(len(Rax)):
                        print(f"{Rax[i]}, ", end=' ')
                    print(f"\n[Info] Loaded list length : {length}")
                    print("[Data End]")
                else:
                    print("[Error] 데이터가 존재하지 않습니다.")
            except Exception as ex:
                print("[Error] 데이터를 읽는데 에러가 났습니다 : " + str(ex))

        print("[Message Received] callback_print : " + str(receive))

    def mqttStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()

    def backgroundThread(self):
        while(self.isRun):
            self.client.loop_start()
            self.isReceiving = True

    def mqttConnect(self, broker):
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.client.message_callback_add("switch/state", self.callback_status)
        self.client.message_callback_add("switch/read", self.callback_print)
        self.client.message_callback_add("switch/TouchStatus", self.callback_print)
        self.client.message_callback_add("serve", self.callback_print)

        self.client.connect(self.broker, 1883)  # connect to broker

        self.client.subscribe([("control/value", 0),
                          ("switch/state", 0),
                          ("switch/read", 0),
                          ("switch/end", 0),
                          ("switch/TouchStatus", 0),
                          ("serve", 0)])
        # client.publish("test",data)
        self.mqttStart()

    def close(self):
        self.isRun = False
        self.thread.join()
        print("Disconnected")

class Window(Frame):
    def __init__(self, figure, master):
        Frame.__init__(self, master)
        self.entry = None
        self.setPoint = None
        self.master = master        # a reference to the master window
        # keep a reference to our serial connection so that we can use it for bi-directional communicate from this class
        self.initWindow(figure)     # initialize the window with our settings

    def initWindow(self, figure):
        self.master.title("Real Time Plot")
        canvas = FigureCanvasTkAgg(figure, master=self.master)
        toolbar = NavigationToolbar2Tk(canvas, self.master)
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        # create out widgets in the master frame
        lbl1 = Tk.Label(self.master, text="Scaling Factor")
        lbl1.pack(padx=5, pady=5)
        self.entry = Tk.Entry(self.master)
        self.entry.insert(0, '1.0')  # (index, string)
        self.entry.pack(padx=5)
        SendButton = Tk.Button(self.master, text='Send', command=self.sendSerialData)
        SendButton.pack(padx=5)

    def sendSerialData(self):
        print("send~~~~~~~~~~")
        # self.serialConnection.write(data.encode('utf-8'))

def ThreadStart(root):
    root.mainloop()

def main():
    broker = "54.180.101.122"

    maxPlotLength = 100
    dataNumBytes = 4
    numPlots = 3
    s = MqttConnect(broker, maxPlotLength, dataNumBytes, numPlots)

'''
    # plotting starts below
    pltInterval = 50  # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = -(300)
    ymax = 300
    fig = plt.figure(figsize=(10, 8))
    # ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin), float(ymax)))
    ax.set_title('Senser Accelerometer')
    ax.set_xlabel("Time")
    ax.set_ylabel("Accelerometer Output")
    # put our plot onto Tkinter's GUI
    root = Tk.Tk()
    app = Window(fig, root)

    lineLabel = ['X', 'Y', 'Z']
    style = ['r-', 'c-', 'b-']  # linestyles for the different plots
    timeText = ax.text(0.70, 0.95, '', transform=ax.transAxes)
    lines = []
    lineValueText = []

    for i in range(numPlots):
        lines.append(ax.plot([], [], style[i], label=lineLabel[i])[0])
        lineValueText.append(ax.text(0.70, 0.90-i*0.05, '', transform=ax.transAxes))
    anim = animation.FuncAnimation(fig, s.getSenserData, fargs=(lines, lineValueText, lineLabel, timeText, pltInterval, ax), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")

    th = Thread(target=ThreadStart(root)).start
'''
    # go.close()
main()
#if __name__ == '__main__':
#    main()