"""
This file is used for implementing the k Nearest Neighbour algorithm for predicting final train delay
The function is used in @predictFromLocalFile
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn import neighbors

# Function to find k nearest neighbour using two arrays for training - delay at station and final delay,
# and the delay at the current station
# Input: delay (e.g. 6), delays at station array (e.g. [2, 6, 3]), final delays array (e.g. [4, 7, 3])
def knn_prediction(delay, delay_at_station, final_delay):
    X = np.array(delay_at_station)[:, np.newaxis]
    y = np.array(final_delay)[:, np.newaxis]
    T = np.linspace(0, max(delay_at_station), 100)[:, np.newaxis]

    knn_u = neighbors.KNeighborsRegressor(3, weights='uniform')
    knn = knn_u.fit(X, y)

    y_knn = knn.predict(T)
    # plt.scatter(X, y, color='black', label='training data')
    # plt.plot(T, y_knn, color='g', label='knn_u')
    # plt.show()

    example = np.array([delay])
    example = example.reshape(1, -1)
    prediction = knn.predict(example)
    return prediction
