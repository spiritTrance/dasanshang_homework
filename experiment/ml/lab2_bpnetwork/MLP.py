from logging import warning
import numpy as np
from scipy.special import expit
from math import exp

class MLP(object):
    def __init__(self, n_input: int, n_hidden: int, n_output: int, loss_func = "MSELoss"):
        self.__n_input = n_input
        self.__n_hidden = n_hidden
        self.__n_output = n_output
        self.__layer_1 = np.random.uniform(-1, 1, size=(n_input, n_hidden))       # weights between hidden layer and output layer
        self.__layer_2 = np.random.uniform(-1, 1, size=(n_hidden, n_output))      # weights between input layer and hidden layer
        self.__bias_1 = np.random.uniform(-1, 1, size=(n_hidden))                 # bias in hidden layer
        self.__bias_2 = np.random.uniform(-1, 1, size=(n_output))                 # bias in output layer
        self.__hidden_output = np.zeros(shape = (1, n_hidden))                      # record middle output for backward propagation
        self.__loss_func = loss_func
        self.__loss_train_rec = []
    
    def __sigmoid(self, x):
        return expit(x)     # sigmoid function, import scipy to avoid the annoying numerical precision problem which is not the focus of this experiement.

    def __onehotConvert(self, label_set):
        sampleNum = label_set.data.shape
        s = set()
        for i in label_set:
            s.add(i)
        classNum = len(s)
        newSet = np.zeros(shape = (0, classNum))        
        for i in label_set:
            l = np.zeros(shape = (1, classNum))
            l[0][i] = 1
            newSet = np.concatenate((newSet, l), axis = 0)
        return newSet
    
    def __lrDecay(self, lr_0, epoch, maxEpoch, decay = "None"):
        if decay == "none":
            return lr_0
        elif decay == "linear":
            return lr_0 * (maxEpoch - epoch) / maxEpoch
        else:
            warning("No such decay method: {:s}, use default method.".format(decay))
            return lr_0
    
    def optimize(self, feature_set, label_set, epochNum = 100, lr = 0.01, decay = "none", printMsg = False):
        self.__loss_train_rec = []
        label_set = self.__onehotConvert(label_set)
        for epoch in range(1, epochNum + 1):
            loss = 0
            if epoch % 1000 == 0 and printMsg == True:
                print(" + 当前是第 {:d} 次迭代".format(epoch))
            lr_e = self.__lrDecay(lr, epoch, epochNum, decay)
            for X, y in zip(feature_set, label_set):
                loss += self.__step(X, y, lr_e)
            self.__loss_train_rec.append(loss)
        loss = 0
        for X, y in zip(feature_set, label_set):
            loss += self.MSELoss(X, y)
        self.__loss_train_rec.append(loss)
        
    def __step(self, feature: np.array, label: np.array, lr = 0.01):
        output = self.__forward(feature)
        loss = self.MSELoss(feature, label, output)
        self.__backPropagate(feature, label, output, lr)
        return loss
    
    def __forward(self, feature: np.ndarray):
        # note that feature is a single feature
        feature = feature.reshape(1, self.__n_input)
        output = feature.dot(self.__layer_1)
        output += self.__bias_1
        output = self.__sigmoid(output)
        self.__hidden_output += output
        output = output.dot(self.__layer_2)
        output += self.__bias_2
        output = self.__sigmoid(output)
        return output.reshape(self.__n_output)
    
    def __backPropagate(self, feature: np.ndarray, label: np.ndarray, output: np.ndarray, lr = 0.01):
        # note that feature is a single feature, label is the same.
        # the param need update: bias_1, bias_2, layer_1, layer_2
        # note that label here should be one-hot vector, which shall be processed in DataSet class
        
        # adjust the shape of input
        output = output.reshape(1, self.__n_output)
        feature = feature.reshape(self.__n_input, 1)    # shape: n_input * 1
        label = label.reshape(1, self.__n_output)
        # backward propagantion!
        d_g = output * (1 - output) * (label - output)                                              # gradient for middle varaible: shape: 1 * n_output
        d_e = self.__hidden_output * (1 - self.__hidden_output) * d_g.dot(self.__layer_2.T)         # gradient for middle varaible: shape: 1 * n_hidden
        d_b2 = - d_g.reshape(self.__n_output)                                                       # gradient for bias_2: shape: n_output
        d_w2 = self.__hidden_output.T.dot(d_g)                                                      # gradient for weight in layer_2: shape: n_hidden * n_output
        d_b1 = - d_e.reshape(self.__n_hidden)                                                       # gradient for bias_1: shape: n_hidden
        d_w1 = feature.dot(d_e)                                                                     # gradient for weight in layer_1: shape: n_input * n_hidden
        # update parameters
        self.__bias_1 += lr * d_b1
        self.__bias_2 += lr * d_b2
        self.__layer_1 += lr * d_w1
        self.__layer_2 += lr * d_w2
        # clear accumulate
        self.__hidden_output = np.zeros(shape=(1, self.__n_hidden))
        
    def MSELoss(self, feature, label, y_hat = None):
        # note that feature is a single feature
        if y_hat is None:
            return np.sum((label - self.__forward(feature)) ** 2)
        else:
            return np.sum((label - y_hat) ** 2)
    
    def pred(self, feature):
        return np.argmax(self.__forward(feature))
    
    def eval(self, feature_set, label_set):
        # evaluation function, return the accuracy
        acc = 0
        tot = len(label_set)
        for X, y in zip(feature_set, label_set):
            y_hat = self.pred(X)
            acc = acc + 1 if y_hat == y else acc
        return acc / tot

    def getTrainLoss(self):
        return self.__loss_train_rec