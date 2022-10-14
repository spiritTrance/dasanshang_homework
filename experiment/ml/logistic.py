'''
1. 理解对率回归算法原理。
2. 编程实现对数几率回归算法。
3. 将算法应用于西瓜数据集、鸢尾花数据集分类问题。
'''
import numpy as np

class DataSet:
    def __init__(self, feature, label, title):
        self.__feature = feature
        self.__label = label
        self.__title = title
        self.__sample_num = len(label)
        self.__convertedFeature = None
        self.__convertedTitle = None
        
    def getFeature(self):
        return self.__feature
    
    def getLabel(self):
        return self.__label
    
    def getTitle(self):
        return self.__title
    
    def getSampleNum(self):
        return self.__sample_num
    
    def str2Onehot():
        pass
    
    def Onehot2str():
        pass
        

class Logistic:
    def __init__(self, input_size: int) -> None:
        self.__beta = np.random.rand(input_size + 1, 1)       # 将常数项 b 直接纳入里面
        self.__input_size = input_size
        
    def getPositiveProb(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        ans = np.exp(self.__beta.T.dot(x_extend)) / 1 + np.exp(self.__beta.T.dot(x_extend))
        return ans
            
    def getNegativeProb(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        ans = 1 / 1 + np.exp(self.__beta.T.dot(x_extend))
        return ans

    def getLogit(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        ans = self.__beta.T.dot(x_extend)
        return ans
    
    def optimize(self, feature: np.ndarray, label: np.ndarray, iter_num = 100):
        for epoch in range(1, iter_num + 1):
            self.__step(feature, label)
            print(self.__beta)
    
    def __step(self, feature: np.ndarray, label: np.ndarray, lr = 1):
        val_2d = self.__getMLEValue_2d(feature, label)
        try:
            inv_2d = np.linalg.inv(val_2d)
        except np.linalg.LinAlgError:                   # 奇异矩阵无逆矩阵，使用伪逆代替
            inv_2d = np.linalg.pinv(val_2d)
        delta = inv_2d * self.__getMLEValue_1d(feature, label) * lr
        self.__beta = self.__beta - delta

    def __getMLEValue(self, feature: np.ndarray, label: np.ndarray):          # 极大似然函数
        ans = 0
        for x, y in zip(feature, label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            ans += -y * self.__beta.T * x_extend + np.log(1 + np.exp(self.__beta.T * x_extend))
        return ans
    
    def __getMLEValue_1d(self, feature: np.ndarray, label: np.ndarray):       # 极大似然函数的一阶导数
        ans = 0
        for x, y in zip(feature, label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            ans += - x_extend * (y - self.getPositiveProb(x))
        return ans
        
    def __getMLEValue_2d(self, feature: np.ndarray, label: np.ndarray):       # 极大似然函数的二阶导数
        ans = 0
        for x, y in zip(feature, label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            prob_1 = self.getPositiveProb(x)
            ans += - x_extend.dot(x_extend.T) * prob_1 * (1 - prob_1)
        return ans