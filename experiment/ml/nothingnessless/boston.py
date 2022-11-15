from regressionTree import RegressionTree
from utils.Data import DataClass, DataSet, DataSpliter
import pandas as pd
import numpy as np
import logging
logging.disable(logging.WARNING)    # 禁用 DataSet 定义的 Logging
from sklearn.tree import DecisionTreeRegressor

data_url = "http://lib.stat.cmu.edu/datasets/boston"
raw_df = pd.read_csv(data_url, sep="\s+", skiprows=22, header=None)
feature_boston = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
label_boston = raw_df.values[1::2, 2]

dataset_boston = DataSet(feature_boston, label_boston)
title = dataset_boston.getTitle(is_converted = False)
feature_boston, label_boston = dataset_boston.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_boston, label_boston, trainRatio = 0.7)

model = RegressionTree(trainFeatureSet, trainLabelSet, title, 17)
model.build()
print(model.getRSquare(testFeatureSet, testLabelSet, title))

model2 = DecisionTreeRegressor()
model2.fit(trainFeatureSet, trainLabelSet)
X = testFeatureSet
Y = testLabelSet
y_mean = np.mean(Y)
fenzi, fenmu = 0, 0
for x, y in zip(X, Y):
    y_pred = model2.predict(x.reshape(1, -1))
    fenzi += (y_pred - y) ** 2
    fenmu += (y - y_mean) ** 2
print(float(1 - fenzi / fenmu))
    