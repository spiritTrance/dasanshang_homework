from turtle import forward
import numpy as np
from scipy.special import expit

class MLP(object):
    def __init__(self, n_input: int, n_hidden: int, n_output: int):
        self.__n_input = n_input
        self.__n_hidden = n_hidden
        self.__n_output = n_output
        self.__layer_1 = np.random.uniform(-10, 10, size=(n_input, n_hidden))
        self.__layer_2 = np.random.uniform(-10, 10, size=(n_hidden, n_output))
        self.__bias_1 = np.random.uniform(-10, 10, size=(n_hidden))
        self.__bias_2 = np.random.uniform(-10, 10, size=(n_output))
    
    def __sigmoid(self, x):
        return expit(x)     # 调用scipy的sigmoid函数
    
    def forward(self, feature: np.ndarray):
        feature = feature.reshape(1, self.__n_input)
        output = feature.dot(self.__layer_1)
        output += self.__bias_1
        output = self.__sigmoid(output)
        output = output.dot(self.__layer_2)
        output += self.__bias_2
        output = self.__sigmoid(output)
        return output
    
    def backward(self):
        pass
    
    def MSELoss(self):
        pass
    
a = np.random.uniform(-10,10,size=(9,))
md = MLP(9, 5, 3)
print(md.forward(a))