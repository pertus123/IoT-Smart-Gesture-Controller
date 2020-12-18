//합
#include <ArduinoJson.h>
#include <Wire.h>
#include "I2Cdev.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include "MPU6050.h"
#define pi 3.141592
#define RADIANS_TO_DEGREES 180/3.14159
#define fs 131.0;

const size_t capacity = 2*JSON_ARRAY_SIZE(3) + JSON_ARRAY_SIZE(4) + JSON_OBJECT_SIZE(4);
//
  int flexD = 36; //소지
  int flexC = 39; //약지
  int flexB = 34; //중지
  int flexA = 35; //검지
  int push  = 32; //엄지
  int device = 0;
  bool check = false;
//
int test = 0;
int test1 = 1;
int test2 = 2;
int test3 = 3;
int test4 = 4;
int test5 = 5;
int test6 = 6;
int test7 = 7;
//
  int flexValD=0;
  int flexValC=0;
  int flexValB=0;
  int flexValA=0;
  int pushVal;
//Initialize MPU
MPU6050 mpu;
int16_t ax,ay,az;
int16_t gx,gy,gz;
int16_t mx,my,mz;
 
//자이로(각속도)
float gyro_x, gyro_y, gyro_z;
//최종 가속도,자이로 각도
float accel_x, accel_y, accel_z;
float gyro_angle_x=0, gyro_angle_y=0, gyro_angle_z=0;

//상보필터 거친 각도
float angle_x=0,angle_y=0,angle_z=0;

//자이로센서 바이어스값
float base_gx=0, base_gy=0, base_gz=0;
unsigned long pre_msec=0;

char accel[50];
char gyro[50];
double Rax;
double Ray;
double Raz;

//MQTT 기본정보
const char* ssid = "Redmi";
const char* password = "11111111";
const char* mqtt_server = "54.180.101.122";
const char* clientName = "ESP32";
const char* outTopic = "test";
const char* inTopic = "test";
const char* outTopic1 = "test";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;
char sum[1024];

//Json Setup
//const size_t capacity =JSON_OBJECT_SIZE(6);

//const size_t capacity = JSON_ARRAY_SIZE(3) + JSON_OBJECT_SIZE(3);
//DynamicJsonDocument doc(1024);
//JsonArray dt;

void calibrate() { 
  int loop = 10;
  for (int i=0; i < loop; i++)
  {
    mpu.getMotion9(&ax,&ay,&az,&gx,&gy,&gz,&mx,&my,&mz);
    base_gx += gx;
    base_gy += gy;
    base_gz += gz;
    delay(80);
  }
  base_gx /=loop;
  base_gy /=loop;
  base_gz /=loop;
}

void setup() {
  //MPU6050 Setup
  Wire.begin();
  Serial.begin(115200);
  mpu.initialize();
  calibrate();

  //WiFi Setup
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  //dt = doc.to<JsonArray>();
}

//WiFi 설정
void setup_wifi() {
  delay(10); // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void accel_loop() {//단위시간 변화량
  StaticJsonDocument<capacity> doc;
  JsonArray Acc = doc.createNestedArray("Acc");
  JsonArray Gy = doc.createNestedArray("Gy");
  JsonArray Flex = doc.createNestedArray("Flex");
  float dt1 = (millis()-pre_msec)/1000.0;
  pre_msec = millis();
  mpu.getMotion9(&ax,&ay,&az,&gx,&gy,&gz,&mx,&my,&mz);
 
  //가속도값 아크탄젠트->각도변환
  accel_x = atan(ay/sqrt(pow(ax,2) + pow(az,2)))*RADIANS_TO_DEGREES;
  accel_y = atan(-1*ax/sqrt(pow(ay,2) + pow(az,2)))*RADIANS_TO_DEGREES;
  accel_z = atan(sqrt(pow(ax,2) + pow(ay,2))/az)*RADIANS_TO_DEGREES;
  
  //-1*ax/sqrt(pow(ay,2) + pow(az,2))
  //자이로 -32766~+32766을 실제 250degree/s로 변환
  //앞에서 계산한 오차의 평균값을 빼줌 
  gyro_x = (gx-base_gx)/fs;  
  gyro_y = (gy-base_gy)/fs;
  gyro_z = (gz-base_gz)/fs;
  //변화량을 적분 
  gyro_angle_x = angle_x + dt1*gyro_x;
  gyro_angle_y = angle_y + dt1*gyro_y;
  gyro_angle_z = angle_z + dt1*gyro_z;
  //상보필터
  angle_x = 0.95*gyro_angle_x + 0.05*accel_x;
  angle_y = 0.95*gyro_angle_y + 0.05*accel_y;
  angle_z = 0.95*gyro_angle_z + 0.05*accel_z;

  Rax = (double)ax/16383*100;
  Ray = (double)ay/16383*100;
  Raz = (double)az/100;

  flexValD = analogRead(flexD); 
  flexValC = analogRead(flexC); 
  flexValB = analogRead(flexB); 
  flexValA = analogRead(flexA);

  Acc.add(round(Rax*100)/100);
  Acc.add(round(Ray*100)/100);
  Acc.add(round(Raz*100)/100);
  Gy.add(round(angle_x*100)/100);
  Gy.add(round(angle_y*100)/100);
  Gy.add(round(angle_z*100)/100);
  Flex.add(flexValD);
  Flex.add(flexValC);
  Flex.add(flexValB);
  Flex.add(flexValA);
  doc["push"] = pushVal;
  serializeJson(doc, sum);
}

void startSend(){
  accel_loop();
}

void endNotSend(){
}
  
void loop() {
 if(!client.connected()) reconnect();
 client.loop();
 String str;
 str = readSerial();
 Serial.print(str);
 pushVal = analogRead(push);

 if(pushVal >= 2500 && check == true){
 check = false;
   delay(500);
   pushVal = analogRead(push);
  //client.
 //client.publish(outTopic1, sum);// 자이로, 가속도 배열들 MQTT로 전송
 }
 
 if(pushVal >= 2500 && check == false){
  check = true;
  delay(500);
  } 

 if(check == true && pushVal <2500){
    // 자이로, 가속도 배열에 저장
  startSend();
  Serial.println(sum);
  client.publish(outTopic1, sum);// 자이로, 가속도 배열들 MQTT로 전송
 }

Serial. print(check + " ");
Serial. println(pushVal);
  //
 //Serial.println(sum);
 //client.publish(outTopic1, sum);
 delay(100);  
}



String readSerial() {
  String str = "";
  char ch;

  while(Serial.available() > 0) {
    ch = Serial.read();
    str.concat(ch);
    delay(10);
  }
  return str;
}

//Message Queue Callback initialize
void callback(char* topic, byte* payload, unsigned int length) {
  String ledControlString = "";
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    ledControlString += (char)payload[i];
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

//재접속 시도
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(clientName)) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish(outTopic, "hello world");
      // ... and resubscribe
      client.subscribe(inTopic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
