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
import dtwlogic

isInputGesture = False
callback_state = False
read_mode = False
saved_read = False
mqttmsg = ""
progressText = ""
length = 0
savePhase = 0
valEvaluateMeter = 0


# List 선언
Rax, Ray, Raz = [], [], []
Rax1, Rax2, Rax3, Ray1, Ray2, Ray3, Raz1, Raz2, Raz3 = [], [], [], [], [], [], [], [], []
scale_x, scale_y, scale_z = [], [], []
scale_x1, scale_y1, scale_z1, scale_x2, scale_y2, scale_z2, scale_x3, scale_y3, scale_z3 = [], [], [], [], [], [], [], [], []
flex1, flex2, flex3, flex4 = [], [], [], []
flex1_1, flex1_2, flex1_3, flex1_4, flex2_1, flex2_2, flex2_3, flex2_4, flex3_1, flex3_2, flex3_3, flex3_4 = [], [], [], [], [], [], [], [], [], [], [], []


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
        self.isComplete = False
        self.isComplete2 = False
        self.isComplete3 = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        self.counter = 0
        self.Temp = 0
        self.Temp2 = 0

        # self.saveGestureList(mqttmsg)
        # self.checkValEvaluateMeter()

        self.evaluateMeterLimit = 0.80

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
                # if self.counter == 100:
                #     self.isGetSenserData = False
                #     print("[Info] Senser Data Collect Complete")
            except Exception as ex:
                print("[Error] 데이터 불러오는데 에러가 발생했습니다 : " + str(ex))

    def on_connect(self, client, data, flag, rc):
        print("[Info] Mqtt Server Connected with Code : " + str(rc))

    def on_publish(self, client, data, msg):
        print("on_publish")

    def on_message(self, client, userdata, message):
        global length, callback_state, isInputGesture
        x = message.payload.decode("utf-8")

        if read_mode is True:
            print(x)

        # Json 파싱
        mqttmsg = json.loads(x)

        # 데이터 세이브 하는 과정
        if isInputGesture is True:
            self.saveGestureList(mqttmsg)

        # callback_state가 True이면 값을 저장한다.
        if callback_state is True:
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
            if (len(Rax1) == 1):
                print("\r [Info] Data Saving..", end='')
            if (len(Rax1) % 5 == 0):
                print("\r .")
            if length == self.plotMaxLength:
                callback_state = False
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
        global read_mode, length
        receive = message.payload.decode("utf-8")
        print("[Message - switch/read decoded] : " + receive)

        if receive == 'clear':
            del Rax[:], Ray[:], Raz[:]
            del scale_x[:], scale_y[:], scale_z[:]
            del flex1[:], flex2[:], flex3[:], flex4[:]
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
                if len(Rax1) > 0:
                    for i in range(len(Rax1)):
                        print(f"{Rax1[i]}, ", end=' ')
                    print(f"\n[Info] Loaded list length : {length}")
                    print("[Data End]")
                else:
                    print("[Error] 데이터가 존재하지 않습니다.")
            except Exception as ex:
                print("[Error] 데이터를 읽는데 에러가 났습니다 : " + str(ex))

        print("[Message Received] callback_print : " + str(receive))

    def callback_mod1(self, client, userdata, message):
        global isInputGesture, savePhase
        self.receive = message.payload.decode("utf-8")
        if self.receive == "data_on":
            isInputGesture = True
            print("isInputGesture : " + str(isInputGesture))
        elif self.receive == "data_off":
            isInputGesture = False
            print("isInputGesture : " + str(isInputGesture))

        if self.receive == "complete":
            if(savePhase == 0):
                self.isComplete = True
            elif(savePhase == 1):
                self.isComplete2 = True
            elif(savePhase == 2):
                self.isComplete3 = True
            print("isComplete : " + str(self.isComplete))

        if self.receive == "complete_cancel":
            self.isComplete = False
            self.isComplete2 = False
            self.isComplete3 = False
            print("isComplete : " + str(self.isComplete))

        if self.receive == "all_del":
            print("[System] Delete All List!!")
            del Rax[:], Ray[:], Raz[:], scale_x[:], scale_y[:], scale_z[:], flex1[:], flex2[:], flex3[:], flex4[:]
            del Rax1[:], Ray1[:], Raz1[:], scale_x1[:], scale_y1[:], scale_z1[:], flex1_1[:], flex1_2[:], flex1_3[:], flex1_4[:]
            del Rax2[:], Ray2[:], Raz2[:], scale_x2[:], scale_y2[:], scale_z2[:], flex2_1[:], flex2_2[:], flex2_3[:], flex2_4[:]
            del Rax3[:], Ray3[:], Ray3[:], scale_x3[:], scale_y3[:], scale_z3[:], flex3_1[:], flex3_2[:], flex3_3[:], flex3_4[:]
            print("[Info] Deleted List of Rax : " + str(len(Rax)))

        if self.receive == "show_rax":
            print("[Info]" + str(Rax))

    def saveGestureList(self, message):
        global savePhase, isInputGesture, progressText, mqttmsg
        mqttmsg = message
        self.isCompleteIn = False

        if(savePhase == 0):
            if(len(Rax1) == 0) :
                print("[Info] Event Listened, 첫번째 데이터를 저장합니다.. // savePhase = " + str((savePhase + 1)))
                progressText = "\r [Info] 1st Data Saving.."
            Rax1.append(mqttmsg['Acc'][0]), Ray1.append(mqttmsg['Acc'][1]), Raz1.append(mqttmsg['Acc'][2])
            scale_x1.append(mqttmsg['Gy'][0]), scale_y1.append(mqttmsg['Gy'][1]), scale_z1.append(mqttmsg['Gy'][2])
            flex1_1.append(mqttmsg['Flex'][0]), flex1_2.append(mqttmsg['Flex'][1]), flex1_3.append(mqttmsg['Flex'][2]), flex1_4.append(mqttmsg['Flex'][3])
            length = len(Rax1)
            if len(Rax1) % 5 == 0:
                progressText += '.'
                print(progressText, end='')
            if self.isComplete is True:
                self.isCompleteIn = True
                Rax.append(Rax1), Ray.append(Ray1), Raz.append(Raz1)
                scale_x.append(scale_x1), scale_y.append(scale_y1), scale_z.append(scale_z1)
                flex1.append(flex1_1), flex2.append(flex1_2), flex3.append(flex1_3), flex4.append(flex1_4)
                print("[Info] First Senser data Save Complete / Check Length : " + str(len(Rax)))
                savePhase += 1
                print("[Save Phase] : " + str(savePhase))
                isInputGesture = False

        if(savePhase == 1 and isInputGesture is True):
            if(len(Rax2) == 0) :
                print("[Info] Event Listened, 두번째 데이터를 저장합니다.. // savePhase = " + str((savePhase + 1)))
                progressText = "\r [Info] 2nd Data Saving.."
            Rax2.append(mqttmsg['Acc'][0]), Ray2.append(mqttmsg['Acc'][1]), Raz3.append(mqttmsg['Acc'][2])
            scale_x2.append(mqttmsg['Gy'][0]), scale_y2.append(mqttmsg['Gy'][1]), scale_z2.append(mqttmsg['Gy'][2])
            flex2_1.append(mqttmsg['Flex'][0]), flex2_2.append(mqttmsg['Flex'][1]), flex2_3.append(mqttmsg['Flex'][2]), flex2_4.append(mqttmsg['Flex'][3])
            length = len(Rax2)
            if len(Rax2) % 5 == 0:
                progressText += '.'
                print(progressText, end='')
            if self.isComplete2 is True:
                isInputGesture = False
                Rax.append(Rax2), Ray.append(Ray2), Raz.append(Raz2)
                scale_x.append(scale_x2), scale_y.append(scale_y2), scale_z.append(scale_z2)
                flex2.append(flex2_1), flex2.append(flex2_2), flex3.append(flex2_3), flex4.append(flex2_4)

                print("[Info] Second Senser data Save Complete / Check Length : " + str(len(Rax)))
                print("[Info] Evaluate List...")
                self.checkValEvaluateMeter(Rax, Ray, Raz, scale_x, scale_y, scale_z, flex1, flex2, flex3, flex4)
                print("[Info] Result of valEvaluateMeter [Phase " + str(savePhase) +"] : " + str(valEvaluateMeter))
                if valEvaluateMeter >= self.evaluateMeterLimit:
                    print("[Info] Evaluate Complete. If you want to go Next Phase, plz Recall Message >> data_on <<")
                    savePhase += 1
                    print("[Save Phase] : " + savePhase)
                else:
                    print("[Error] Evaluate Failed. Please Retry 2nd Evaluate Process.")
                    del Rax[1:], Ray[1:], Raz[1:], scale_x[1:], scale_y[1:], scale_z[1:], flex1[1:], flex2[1:], flex3[1:], flex4[1:]
                    print("[Info] Rax~ list length : " + str(len(Rax)))
                    del Rax2[:], Ray2[:], Raz2[:], scale_x2[:], scale_y2[:], scale_z2[:], flex2_1[:], flex2_2[:], flex2_3[:], flex2_4[:]
                    print("[Info] Rax2~ list length : " + str(len(Rax2)))
                isInputGesture = False


        if(savePhase == 2 and isInputGesture is True):
            if(len(Rax3) == 0):
                print("[Info] Event Listened, 세번째 데이터를 저장합니다.. // savePhase = " + str((savePhase + 1)))
                progressText = "\r [Info] 3rd Data Saving.."
            Rax3.append(mqttmsg['Acc'][0]), Ray3.append(mqttmsg['Acc'][1]), Raz3.append(mqttmsg['Acc'][2])
            scale_x3.append(mqttmsg['Gy'][0]), scale_y3.append(mqttmsg['Gy'][1]), scale_z3.append(mqttmsg['Gy'][2])
            flex3_1.append(mqttmsg['Flex'][0]), flex3_2.append(mqttmsg['Flex'][1]), flex3_3.append(mqttmsg['Flex'][2]), flex3_4.append(mqttmsg['Flex'][3])
            length = len(Rax3)
            if len(Rax3) % 5 == 0:
                progressText += '.'
                print(progressText, end='')
            if self.isComplete3 is True:
                Rax.append(Rax3), Ray.append(Ray3), Raz.append(Raz3)
                scale_x.append(scale_x3), scale_y.append(scale_y3), scale_z.append(scale_z3)
                flex3.append(flex3_1), flex2.append(flex3_2), flex3.append(flex3_3), flex4.append(flex3_4)

                print("[Info] Third Senser data Save Complete / Check Length : " + str(len(Rax)))
                print("[Info] Evaluate List...")
                self.checkValEvaluateMeter(Rax, Ray, Raz, scale_x, scale_y, scale_z, flex1, flex2, flex3, flex4)
                print("[Info] Result of valEvaluateMeter [Phase " + str(savePhase) + "] : " + str(valEvaluateMeter))
                if valEvaluateMeter >= self.evaluateMeterLimit:
                    print("[Info] Evaluate All Complete. Save into DB all lists")
                    savePhase = 0
                    print("[Save Phase] : " + str(savePhase))
                else:
                    print("[Error] Evaluate Failed. Please Retry 3rd Evaluate Process.")
                    del Rax[2:], Ray[2:], Raz[2:], scale_x[2:], scale_y[2:], scale_z[2:], flex1[2:], flex2[2:], flex3[2:], flex4[2:]
                    print("[Info] Rax~ list length : " + str(len(Rax)))
                    del Rax3[:], Ray3[:], Ray3[:], scale_x3[:], scale_y3[:], scale_z3[:], flex3_1[:], flex3_2[:], flex3_3[:], flex3_4[:]
                    print("[Info] Rax3~ list length : " + str(len(Rax3)))
                isInputGesture = False

    def checkValEvaluateMeter(self, Rax, Ray, Raz, scale_x, scale_y, scale_z, flex1, flex2, flex3, flex4):
        global valEvaluateMeter
        if savePhase == 1:
            ax = dtwlogic.dtwtest(Rax[0], Rax[1])
            print("ax" + str(ax))
            ay = dtwlogic.dtwtest(Ray[0], Ray[1])
            print("ay" + str(ay))
            az = dtwlogic.dtwtest(Raz[0], Raz[1])
            print("az" + str(az))
            Gyx = dtwlogic.dtwtest(scale_x[0], scale_x[1])
            print(Gyx)
            Gyy = dtwlogic.dtwtest(scale_y[0], scale_y[1])
            Gyz = dtwlogic.dtwtest(scale_z[0], scale_z[1])
            Flex1 = dtwlogic.dtwtest(flex1[0], flex1[1])
            Flex2 = dtwlogic.dtwtest(flex2[0], flex2[1])
            Flex3 = dtwlogic.dtwtest(flex3[0], flex3[1])
            Flex4 = dtwlogic.dtwtest(flex4[0], flex4[1])
        if savePhase == 2:
            ax = dtwlogic.dtwtest(Rax[1], Rax[2])
            ay = dtwlogic.dtwtest(Ray[1], Ray[2])
            az = dtwlogic.dtwtest(Raz[1], Raz[2])
            Gyx = dtwlogic.dtwtest(scale_x[1], scale_x[2])
            Gyy = dtwlogic.dtwtest(scale_y[1], scale_y[2])
            Gyz = dtwlogic.dtwtest(scale_z[1], scale_z[1])
            Flex1 = dtwlogic.dtwtest(flex1[1], flex1[2])
            Flex2 = dtwlogic.dtwtest(flex2[1], flex2[2])
            Flex3 = dtwlogic.dtwtest(flex3[1], flex3[2])
            Flex4 = dtwlogic.dtwtest(flex4[1], flex4[2])

        print(ax, ay, az, Gyx, Gyy, Gyz, Flex1, Flex2, Flex3, Flex4)

        result = (abs(ax) + abs(ay) + abs(az) +
                 abs(Gyx) + abs(Gyy) + abs(Gyz) +
                 abs(Flex1) + abs(Flex2) + abs(Flex3) + abs(Flex4)) / 10
        result = round(result, 4)
        valEvaluateMeter = result
        print(valEvaluateMeter)
        self.client.publish("serve", result)

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
        self.client.message_callback_add("switch/mod1", self.callback_mod1)

        self.client.connect(self.broker, 1883)  # connect to broker

        self.client.subscribe([("control/value", 0),
                          ("switch/state", 0),
                          ("switch/read", 0),
                               ("switch/mod1", 0)])
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

    maxPlotLength = 50
    dataNumBytes = 4
    numPlots = 3
    s = MqttConnect(broker, maxPlotLength, dataNumBytes, numPlots)

    # plotting starts below
    pltInterval = 50  # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = maxPlotLength
    ymin = -(300)
    ymax = 300
    fig = plt.figure(figsize=(7, 6))
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

    # go.close()

if __name__ == '__main__':
    main()