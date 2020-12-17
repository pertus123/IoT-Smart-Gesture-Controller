IoT Smart Gesture Controller
=============

1.Introduction
-------------
- 사물인터넷, IoT 등 인터넷과 연결된 모듈이나 환경을 사용자의 제스처로 컨트롤
- 등록된 제스처를 통해 원하는 명령을 내리는 것이 가능
- 제스처를 만드는 것으로 남들이 알지 못하는 방식으로 제어와 접근

<br>

### System Diagram
![Alt text](/img/system_diagram.JPG)

### Hardware Design
* WiFi 통신을 위한 ESP32
* 팔 동작 제스쳐 인식을 위한 MPU6050
* 손가락 제스쳐 인식을 위한 Flex sensor
* 제어 시연을 하기 위해 스마트 홈 제작
    > 창문, 문(서보모터), 커튼(스텝모터), LED 

### Software Design
* 각 센서의 데이터를 받아 전처리 작업 수행.
* 칼라 필터를 이용하여 가속도 값 보정.
* MQTT 프로토콜을 이용한 서버 통신.
* 안드로이드 - DB 제스쳐 등록 및 해제.
* DTW 알고리즘 데이터 패턴 매칭 진행.

<br>

2.DTW(Dynamic Time Warping) 알고리즘
-------------

<br>

* 두 시계열 간의 거리를 최소화하는 하는 방향으로 움직이면서 매칭시켜 각 템플릿과의 누적 거리를 계산하여 최소화 보간.
  
![Alt text](/img/DTW_math.jpg)
* 템플릿 2차원 배열을 생성하여 각 데이터를 로우와 컬럼으로 입력.
  
* 데이터 요소간의 차이의 절대값에 이전 값을 더해 나머지 매트릭스를 채움.

* 행렬의 마지막에서 시작하여 가장 작은 숫자의 칸으로 이동하여 warping path 생성. 대각선 변화량에 따라 유사도를 구함.

![Alt text](/img/DTW_graph.jpg)

<br>

3.Smart Gesture Controller Testing
-------------

<br>

### -  Sensor Graph

![Alt text](/img/Sensor_visualization.jpg)
[Accelerometer, Gyro, Flex data sensor graph] 

<br>

### - Testing.
![Alt text](/img/Gesture1.gif)

![Alt text](/img/Gesture2.gif)

<br>
<br>

참고 문헌
-------------

***

[1] 최동식, 고재일, 김영호, 신민철, 양종섭, 박기홍. (2019). IoT 제어의 편의 향상을 위한 Smart Gesture Controller 플랫폼. 한국정보기술학회 종합학술발표논문집, (), 383-384.