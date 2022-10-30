'''
?
'''
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from time import time
from MLP import MLP
from matplotlib import pyplot as plt

data = pd.read_excel('winequality_data.xlsx')
data = data.to_numpy()
X, y_ = data[:, 0:-1], data[:, -1]
y=[]
for i in y_:
    if i=="Bad":
        y.append(0)
    if i=="Normal":
        y.append(1)
    if i=="Good":
        y.append(2)
y=np.array(y)
# X=preprocessing.scale(X)#将数据标准化
# 归一化

def preprocess(data):
    '''
    ???
    '''
    mean = np.array([np.mean(data[:,i]) for i in range(data.shape[1])])
    scale = np.array([np.std(data[:,i]) for i in range(data.shape[1])])
    ans_data = np.empty(shape=data.shape,dtype=float)
    for j in range(data.shape[1]):
            ans_data[:,j] = (data[:,j] - mean[j]) / (scale[j])
    return ans_data

def trainResultPrint(dataSetName: str, trainingTime: int, trainacc: float, testacc: float, lr: float, epochNum: int):
    print(" * {:s} 数据集的训练结果：".format(dataSetName))
    print("    - 训练时长为:          {:.2f} s".format(trainingTime))
    print("    - 迭代总次数为:        {:d} ".format(epochNum))
    print("    - 学习率为:            {:.6f} ".format(lr))
    print("    - 训练集上的准确率为:  {:.2%} ".format(trainacc))
    print("    - 测试集上的准确率为:  {:.2%} ".format(testacc))
    print()

X=preprocess(X)
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

st = time()
md = MLP(11, 50, 3)
lr = 0.0001
epochNum = 5000
md.optimize(x_train, y_train, epochNum = epochNum, lr = 0.0001, decay = "none", printMsg = True)
acc = md.eval(x_test, y_test)
ed = time()
trainacc = md.eval(x_train, y_train)
testacc = md.eval(x_test, y_test)
trainResultPrint("红酒(UCI)", ed - st, trainacc, testacc, lr, epochNum)
y = md.getTrainLoss()
plt.plot(y)
plt.rcParams['figure.figsize'] = (20.0, 12.0)
plt.show()