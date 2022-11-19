'''
1. 理解对率回归算法原理。
2. 编程实现对数几率回归算法。
3. 将算法应用于西瓜数据集、鸢尾花数据集分类问题。
'''
import numpy as np
from logging import warning

class Logistic:
    def __init__(self, feature: np.array, label: np.array) -> None:
        self.__feature = feature.astype('float')
        self.__label = label.astype('float')
        self.__sample_num, self.__input_size = feature.data.shape
        self.__beta = np.random.rand(self.__input_size + 1, 1) * 20 - 10       # 将常数项 b 直接纳入里面
        self.__loss = []
        
    def getPositiveProb(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        expX = self.__beta.T.dot(x_extend)
        if expX > 0:            # 防止数值溢出
            ans = 1 / (1 + np.exp(-expX))
        else:
            ans = np.exp(expX) / (1 + np.exp(expX))
        return ans
            
    def getNegativeProb(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        expX = self.__beta.T.dot(x_extend)
        if expX < 0:            # 防止数值溢出
            ans = 1 / (1 + np.exp(expX))
        else:
            ans = np.exp(-expX) / (1 + np.exp(-expX))
        return ans

    def getLogit(self, x: np.ndarray):
        x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
        ans = self.__beta.T.dot(x_extend)
        return ans
    
    def optimize(self, iter_num = 100, lr = 1, method = "gd"):
        '''
        注意feature是一整批送进来的
        '''
        self.__loss = []
        self.__loss.append(float(self.__getMLEValue()))
        if not method in ["gd","newton"]:
            warn_str = "不存在 "+method+" 迭代算法，默认使用梯度下降法，学习率为: "+str(lr)
            warning(warn_str)
        for epoch in range(1, iter_num + 1):
            self.__step(lr, method)
            self.__loss.append(float(self.__getMLEValue()))
    
    def __step(self, lr = 1, method = "gd"):
        if method == "newton":
            val_2d = self.__getMLEValue_2d()
            try:
                inv_2d = np.linalg.inv(val_2d)
            except np.linalg.LinAlgError:                   # 奇异矩阵无逆矩阵，使用伪逆代替
                inv_2d = np.linalg.pinv(val_2d)
            delta = inv_2d.dot(self.__getMLEValue_1d()) * lr
            self.__beta = self.__beta - delta
        else:
            delta = lr * self.__getMLEValue_1d()
            self.__beta -= delta

    def __getMLEValue(self):          # 极大似然函数
        ans = 0
        for x, y in zip(self.__feature, self.__label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            ans += -y * self.__beta.T.dot(x_extend) + np.log(1 + np.exp(self.__beta.T.dot(x_extend)))
        return ans
    
    def __getMLEValue_1d(self):       # 极大似然函数的一阶导数
        ans = 0
        for x, y in zip(self.__feature, self.__label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            ans += - x_extend * (y - self.getPositiveProb(x))
        return ans
        
    def __getMLEValue_2d(self):       # 极大似然函数的二阶导数
        ans = 0
        for x, y in zip(self.__feature, self.__label):
            x_extend = np.concatenate((x.reshape(self.__input_size, 1), np.ones((1, 1))),axis=0)
            prob_1 = self.getPositiveProb(x)
            ans += - x_extend.dot(x_extend.T) * prob_1 * (1 - prob_1)
        return ans
    
    def eval(self, feature: np.array, label: np.array):
        tot = len(label)
        acc = 0
        for X, y in zip(feature, label):
            pred = 1 if self.getLogit(X) > 0 else 0
            # print(pred, y)
            if int(pred) == int(y):
                acc += 1
        return acc / tot
    
    def getBeta(self):
        return self.__beta
    
    def pred(self, feature: np.array):
        _pred = 1 if self.getLogit(feature) > 0 else 0
        return _pred
    
    def getLossRec(self):
        return self.__loss