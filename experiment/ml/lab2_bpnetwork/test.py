from MLP import MLP
import sklearn
from utils.Data import DataClass, DataSet, DataSpliter
import numpy as np
from sklearn.datasets import load_iris, load_wine   # 注意是导入的数据集
import logging
from matplotlib import pyplot as plt
logging.disable(logging.WARNING)    # 禁用 DataSet 定义的 Logging
from time import time

def trainResultPrint(dataSetName: str, trainingTime: int, trainacc: float, testacc: float, lr: float, epochNum: int):
    print(" * {:s} 数据集的训练结果：".format(dataSetName))
    print("    - 训练时长为:          {:.2f} s".format(trainingTime))
    print("    - 迭代总次数为:        {:d} ".format(epochNum))
    print("    - 学习率为:            {:.6f} ".format(lr))
    print("    - 训练集上的准确率为:  {:.2%} ".format(trainacc))
    print("    - 测试集上的准确率为:  {:.2%} ".format(testacc))
    print()
    
    
dataset_iris = load_iris()
feature_iris = dataset_iris.data
label_iris = dataset_iris.target
labelName_iris = dataset_iris.target_names
title_iris = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]

dataset_iris = DataSet(feature_iris, label_iris, title_iris)
feature_iris, label_iris = dataset_iris.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_iris, label_iris)

st = time()
md = MLP(4, 15, 3)
lr = 0.001
epochNum = 5000
md.optimize(trainFeatureSet, trainLabelSet, epochNum = epochNum, lr = lr, decay = "none", printMsg = True)
acc_train = md.eval(trainFeatureSet, trainLabelSet)
acc_test = md.eval(testFeatureSet, testLabelSet)
ed = time()
trainResultPrint("鸢尾花", ed - st, acc_train, acc_test, lr, epochNum)

y = md.getTrainLoss()
plt.plot(y)
plt.title("MSELoss curve")
plt.rcParams['figure.figsize'] = (20.0, 12.0)
plt.show()

dataset_wine = load_wine()
feature_wine = dataset_wine.data
label_wine = dataset_wine.target
labelName_wine = dataset_wine.target_names
title_wine = ["Alcohol", "Malic acid", "Ash", "Alcalinity of ash", "Magnesium", "Total phenols", "Flavanoids", "Nonflavanoid phenols", "Proanthocyanins", "Color intensity", "Hue", "OD280/OD315 of diluted wines", "Proline"]

dataset_wine = DataSet(feature_wine, label_wine, title_wine)
dataset_wine.rescaling()
feature_wine, label_wine = dataset_wine.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_wine, label_wine, trainRatio = 0.7)

st = time()
md = MLP(13, 50, 3)
lr = 0.0001
epochNum = 5000
md.optimize(trainFeatureSet, trainLabelSet, epochNum = 5000, lr = 0.0001, decay = "none", printMsg = True)
acc = md.eval(testFeatureSet, testLabelSet)
ed = time()
trainacc = md.eval(trainFeatureSet, trainLabelSet)
testacc = md.eval(testFeatureSet, testLabelSet)
trainResultPrint("红酒(UCI)", ed - st, trainacc, testacc, lr, epochNum)

y = md.getTrainLoss()
plt.plot(y)
plt.rcParams['figure.figsize'] = (20.0, 12.0)
plt.show()