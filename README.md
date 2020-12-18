IoT Smart Gesture Controller
=============

주의사항
-------------

- databases
  - 테이블명 : blindDown, blindStop, blindUp, doorOff, doorOn, ledOff, ledOn, windowsOff, windowOn
  - 각 테이블의 필드 명 : AccX1, AccY1, .... GyX2, GyY2.... FlexA3, FlexB3 로 30개 필드. 1,2,3 숫자로 구분.


- testtt.py   // dtw 알고리즘. 
	- dtwtest(comparison, fieldName, tableName) // comparison은 비교 값, fieldName 필드명, tableName 테이블명
	- ts2 // db에서 필드명과 테이블명을 가지고 db에서 정보 조회

- graph.py // db
	- insert // tableName 테이블이름, fieldNumber AccX1,2,3 의 숫자
	- deleteAll  // table 전 삭제 - 등록 전 수행
	- select // 필드이름으로 select문을 조회, 리스트 형태로 반환.

- main에서 호출
	- 비교가 끝나고, 등록할 때,  graph.deleteAll(tble_Name)으로 원래테이블 초기화 

<br>

### 등록모드
```
 if len(receive) > 4: # 등록모드
            callback_state = True
            checkSum = 1
            enCoff(receive, cnt)
def enCoff(controlName, cnt): # 등록모드 수행 controlName = 테이블이름.
        print(1)
        if(cnt == 0):
            graph.deleteAll(tble_Name)
            print("[Info] Mode On 1/3...")
            graph.deleteAll(controlName) # 첫 수행시, 관련 테이블안에 있는 데이터 전부 제거
            checkSum = 1
            # 상관 계수 값을 확인하여 다시 호출 if result >= 0.85 enCoff(contorlName, cnt+1) 아니면 enCoff(cnotrolName, cnt)
        if(cnt == 1):
            print("[Info] Mode On 2/3...")

        if(cnt == 2):
            print("[Info] Mode On 3/3...")

        if(cnt == 3):
            print("complete!")
```

<br>

### 비교 모드
```
            for i in tableName:
                for j in range(1,4):
                    ax = testtt.dtwtest(Rax, "AccX"+j, i)  #첫 번째 인자는 비교값, 두번째는 db 필드, 세번째는 테이블 이름(9가지).
                    ay = testtt.dtwtest(Ray, "AccY"+j, i)
                    az = testtt.dtwtest(Raz, "AccZ"+j, i)
                    gx = testtt.dtwtest(scale_x, "GyX"+j, i)
                    gy = testtt.dtwtest(scale_y, "GyY"+j, i)
                    gz = testtt.dtwtest(scale_z, "GyZ"+j, i)
                    fx1 = testtt.dtwtest(flex1, "FlexA"+j, i)
                    fx2 = testtt.dtwtest(flex2, "FlexB"+j, i)
                    fx3 = testtt.dtwtest(flex3, "FlexC"+j, i)
                    fx4 = testtt.dtwtest(flex4, "FlexD"+j, i)
                    print(ax, ay, az, gx, gy, gz, fx1, fx2, fx3, fx4)
                    #음의 상관계수를
                    result = (abs(ax)+abs(ay)+abs(az)+abs(gx)+abs(gy)+abs(gz)+abs(fx1)+abs(fx2)+abs(fx3)+abs(fx4))/10
                    # 소수점 4자리
                    result = round(result, 4)
                    print(result)
                    #if result >= 0.85: # 예시, 이거 수행
                    self.client.publish("serve", result)
                #break
```
<br>
<br>

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
  
![Alt text](/img/DTW_math.JPG)
* 템플릿 2차원 배열을 생성하여 각 데이터를 로우와 컬럼으로 입력.
  
* 데이터 요소간의 차이의 절대값에 이전 값을 더해 나머지 매트릭스를 채움.

* 행렬의 마지막에서 시작하여 가장 작은 숫자의 칸으로 이동하여 warping path 생성. 대각선 변화량에 따라 유사도를 구함.

![Alt text](/img/DTW_graph.JPG)

<br>

3.Smart Gesture Controller Testing
-------------

### -  Sensor Graph

![Alt text](/img/Sensor_visualization.JPG)
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