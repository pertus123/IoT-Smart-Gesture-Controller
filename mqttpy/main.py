import paho.mqtt.client as mqtt
import time
import json

# MQTT Environment Initialize
# 기본 포트는 1883이니 임의 지정은 안해도 될거임
broker_address = "54.180.101.122"

# 전역 변수는 여기서
callback_state = False
read_mode = False
saved_read = False
length = 0

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


def on_connect(client, data, flag, rc):
    print("Connected", str(rc))


def on_publish(client, data, msg):
    print("on_publish")


def on_message(client, userdata, message):
    global length
    x = message.payload.decode("utf-8")

    if read_mode is True:
        print(x)

    # Json 파싱
    cvt_x = json.loads(x)
    #print(cvt_x['Acc'][0])

    # callback_state가 True이면 값을 저장한다.
    if callback_state is True:
        Rax.append(cvt_x['Acc'][0])
        Ray.append(cvt_x['Acc'][1])
        Raz.append(cvt_x['Acc'][2])
        scale_x.append(cvt_x['Gy'][0])
        scale_y.append(cvt_x['Gy'][1])
        scale_z.append(cvt_x['Gy'][2])
        flex1.append(cvt_x['Flex'][0])
        flex2.append(cvt_x['Flex'][1])
        flex3.append(cvt_x['Flex'][2])
        flex4.append(cvt_x['Flex'][3])

    length = len(Rax)
    print("\r Progress Percent {:4.2f}%...".format(length / 300 * 100))
    #print("\r Progress Percent {:4.2f}%...".format(length / self.plotMaxLength * 100))
    if length == 300:
        callback_state = False
        print("[Info] Senser data Save Complete / Check Length : " + str(len(Rax)))


def callback_status(client, userdata, message):
    global callback_state
    receive = message.payload.decode("utf-8")
    print("[Message - switch/state decoded] : " + receive)
    if receive == "true":
        callback_state = True
    else:
        callback_state = False
    print("[Message Received] Status_read Switch : " + str(callback_state))


def callback_print(client, userdata, message):
    global read_mode, length
    receive = message.payload.decode("utf-8")
    print("[Message - switch/read decoded] : " + receive)

    # 콘솔에서 값 읽는 모드
    if receive == "true":
        read_mode = True
    elif receive == "false":
        read_mode = False

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

    print("[Message Received] Read Mode Switch : " + str(read_mode))


client = mqtt.Client()

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.message_callback_add("switch/state", callback_status)
client.message_callback_add("switch/read", callback_print)


client.connect(broker_address, 1883)  # connect to broker

client.subscribe([("test", 0),
                  ("switch/state", 0),
                  ("switch/read", 0),
                  ("control/value", 0)])
# client.publish("test",data)

client.loop_forever()
# time.sleep(4) # wait
# client.loop_stop() #stop the loop
