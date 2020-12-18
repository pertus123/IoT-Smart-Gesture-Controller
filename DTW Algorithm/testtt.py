
import numpy as np
from dtw import dtw

# if __name__ == '__main__':
def dtwtest(accel, gyro):
    ts1 = [1,2,3,4,5,6,7,8,9,10,1,1,11,1] #14
    ts2 = [1,2,3,4,5,6,7,71,9,3,1,1,1,1,1,2,1] #17

    if len(ts1) > len(ts2):
        ts1, ts2 = ts2, ts1  # 교환

    x = np.array(ts1).reshape(-1, 1)  # 열 차원으로 값이 하나씩 들어감.
    y = np.array(ts2).reshape(-1, 1)  # 열으로 하나씩

    # d = 삽입비용만 유지(7), cost_matrix m*n 합치기전 절대값 뺀 것만, acc_cost_matrix 최종 매트릭스, path 늘려진 값이 뭔지(배열
    d, cost_matrix, acc_cost_matrix, path = dtw(x, y, dist=(lambda x, y: np.abs(x - y)))  #
    ts1_dtw = [ts1[p] for p in path[0]]  # 값에 맞게 삽입
    ts2_dtw = [ts2[p] for p in path[1]]
    print(path)
    print(ts2_dtw)
    print(d)
    print(ts1_dtw)
    print(len(ts1_dtw))
    print(len(ts2))
    print(path[0])
    print(path[1])
    result = np.corrcoef(ts1_dtw, ts2_dtw)  ## correlation coefficent 상관계수

    return result[0][1]

print(dtwtest(1,2))