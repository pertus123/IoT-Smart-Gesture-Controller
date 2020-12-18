'''
import numpy as np
from dtw import dtw

ts1 = [1, 5, 3, 4, 7, 6]
ts2 = [0, 2, 6, 3, 5, 6, 8, 5]

x = np.array(ts1).reshape(-1,1) # 열 차원으로 값이 하나씩 들어감.
y = np.array(ts2).reshape(-1,1) # 열으로 하나씩

#d = 삽입비용만 유지(7), cost_matrix m*n 합치기전 절대값 뺀 것만, acc_cost_matrix 최종 매트릭스, path 늘려진 값이 뭔지(배열
d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=lambda x, y: np.abs(x - y)) #
ts1_dtw = [ts1[p] for p in path[0]] # 값에 맞게 삽입

print(ts1_dtw)
result = np.corrcoef(ts1_dtw, ts2)
## correlation coefficent 상관계수
print(result)
print(result[0][1])
'''

'''
import numpy as np
from dtw import dtw

#if __name__ == '__main__':
def dtwtest(accel, gyro):
    ts1 = accel
    ts2 = gyro

    if len(ts1) > len(ts2):
        ts1, ts2 = ts2, ts1 # 교환

    x = np.array(ts1).reshape(-1,1) # 열 차원으로 값이 하나씩 들어감.
    y = np.array(ts2).reshape(-1,1) # 열으로 하나씩

        #d = 삽입비용만 유지(7), cost_matrix m*n 합치기전 절대값 뺀 것만, acc_cost_matrix 최종 매트릭스, path 늘려진 값이 뭔지(배열
    d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=lambda x, y: np.abs(x - y)) #
    ts1_dtw = [ts1[p] for p in path[0]] # 값에 맞게 삽입

    #print(path[0])
    result = np.corrcoef(ts1_dtw, ts2)    ## correlation coefficent 상관계수

    #print(result)
    return result
'''
import numpy as np
from dtw import dtw
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import subscriber as sb
import publisher as pb
import matplotlib.pyplot as mat
from time import time, sleep
5
# if __name__ == '__main__':
ts1 = np.array([1,6,2,3,9,3]);
ts2 = np.array([2,7,4,5,8,4,1]);
x = np.array(ts1).reshape(-1, 1)  # 열 차원으로 값이 하나씩
y = np.array(ts2).reshape(-1, 1)  # 열으로 하나씩
    # d = 삽입비용만 유지(7), cost_matrix m*n 합치기전 절대값 뺀 것만, acc_cost_matrix 최종 매트릭스, path 늘려진 값이 뭔지(배열
d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=lambda x, y: np.abs(x - y))  #
ts1_dtw = [ts1[p] for p in path[0]]  # 값에 맞게 삽입

result = np.corrcoef(ts1_dtw, ts2)  ## correlation coefficent 상관계수

len_ts1 = len(ts1)
len_ts2 = len(ts2)
interval = len_ts2 / float(len_ts1)
interp_ind = np.arange(0, len_ts2, interval)
ts1_interp = np.interp(np.arange(0,len_ts2, 1), interp_ind, ts1)
plt.figure(figsize=(15,5))
plt.subplot(121)
plt.title('Time series 1')
plt.plot(ts1)
plt.grid(True)
plt.subplot(122)
plt.title('Comparison : ts1_interp vs. ts2')
plt.plot(ts1_interp)
plt.plot(ts2)
plt.legend(['Time series 1 - interpolation', 'Time series 2'])
plt.grid(True)
plt.show()

print(ts1_dtw)


print(result[0][1])