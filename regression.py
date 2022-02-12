"""
This file is used for implementing the linear regression algorithm for predicting final train delay
The function is used in @predictFromLocalFile
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Function to find the values of a & b that can be used in the formula
# estimated delay = a * delay + b
# Input: delay (e.g. 6), delays at station array (e.g. [2, 6, 3]), final delays array (e.g. [4, 7, 3])
def regression_prediction(delay, delay_at_station, final_delay):
    X = np.array(delay_at_station)[:, np.newaxis]
    y = np.array(final_delay)[:, np.newaxis]
    T = np.linspace(0, max(delay_at_station), 100)[:, np.newaxis]

    # Fit a linear regression model
    lr = LinearRegression().fit(X, y)
    y_lr = lr.predict(T)
    a = lr.coef_
    b = lr.intercept_

    # plt.scatter(X, y, color='black', label='training data')
    # plt.plot(T, y_lr, color='b', label='Linear Regression')
    # plt.show()

    return a * delay + b

