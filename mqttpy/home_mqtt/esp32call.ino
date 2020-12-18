//real 집
#include <ArduinoJson.h>
#include <Wire.h>
#include "I2Cdev.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include "MPU6050.h"
//#include <Servo.h>
#include <ESP32Servo.h>
#define pi 3.141592
#define RADIANS_TO_DEGREES 180/3.14159
#define fs 131.0;
#include <Stepper.h>

const int stepsPerRevolution = 700; // change this to fit the number of steps per revolution
Stepper myStepper(stepsPerRevolution, 15,2,0,4);

const size_t capacity = 2*JSON_ARRAY_SIZE(3) + JSON_ARRAY_SIZE(4) + JSON_OBJECT_SIZE(4);
WiFiClient espClient;
PubSubClient client(espClient);

Servo Window;
Servo Door; 
int led = 16;
int winservo = 18;
int doorservo = 5;
int a;
int b;
int blindCheck = 0;
int blindControl = 10;

const char* ssid = "ForGraduate";
const char* password = "11111111";
const char* mqtt_server = "54.180.101.122";
const char* clientName = "ESP32";
const char* outTopic = "test";
const char* inTopic = "module";
const char* inTopic2 = "module/mobile";
const char* outTopic1 = "test";

//String ledControlString = "";
bool check = false;

void setup() {
  myStepper.setSpeed(30);  // 스피드
  pinMode(led, OUTPUT);   
  Window.attach(winservo);
  Door.attach(doorservo);
  
  //MPU6050 Setup
  Wire.begin();
  Serial.begin(115200);
  //WiFi Setup
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}


void windowOn(){
  Window.write(0);  //  Serial.println("1");
}
void windowOff(){
  Window.write(90);// Serial.println("2");
}

void doorOn(){
  Door.write(90); //Serial.println("3");
}

void doorOff(){
  Door.write(0); //  Serial.println("4");
}

void ledOn(){
  digitalWrite(led, HIGH);//  Serial.println("5");
}
void ledOff(){
  digitalWrite(led, LOW);//  Serial.println("6");
}

void blindUp(){

  if(blindCheck < 9){
     myStepper.step(stepsPerRevolution);
     blindCheck++;
  }
  
}
void blindStop(){
   myStepper.step(0);
}
void blindDown(){
   if(blindCheck > 0){
      myStepper.step(-stepsPerRevolution);
      blindCheck--;
}
}



void loop() {
 if(!client.connected()) reconnect();
 client.loop();

 if(blindControl==0){
    blindUp();
 }else if(blindControl==1){
    blindDown();
 }else if(blindControl==2){
    blindStop();
 }
  
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
  //String topicName(topic);
  //Serial.print("Message arrived [");
  //Serial.print(topic);
  //Serial.print("] ");
  for (int i = 0; i < length; i++) {
    ledControlString += (char)payload[i];
    //Serial.print((char)payload[i]);
  }
  
  execute(ledControlString);
 // Serial.println();
 
}

void execute(String control) {
  if(control == "windowOn") windowOn(); //어차피 둘 중 하나,
  if(control == "windowOff") windowOff();
  if(control == "doorOn") doorOn();
  if(control == "doorOff") doorOff();
  if(control == "ledOn") ledOn();
  if(control == "ledOff") ledOff();
  if(control == "blindUp") blindControl=0;
  if(control == "blindStop") blindControl=2;
  if(control == "blindDown") blindControl=1;
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
      //client.subscribe(inTopic2);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
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

/*
void accel_loop() {//단위시간 변화량
  StaticJsonDocument<capacity> doc;
  JsonArray Acc = doc.createNestedArray("Acc");
  JsonArray Gy = doc.createNestedArray("Gy");
  JsonArray Flex = doc.createNestedArray("Flex");
  float dt1 = (millis()-pre_msec)/1000.0;
  pre_msec = millis();
  mpu.getMotion9(&ax,&ay,&az,&gx,&gy,&gz,&mx,&my,&mz);
  //doc["push"] = pushVal;
 // serializeJson(doc, sum);
}
*/
