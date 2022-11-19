from regressionTree import RegressionTree
from utils.Data import DataClass, DataSet, DataSpliter
import pandas as pd
import numpy as np
import logging
logging.disable(logging.WARNING)    # 禁用 DataSet 定义的 Logging
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
import pandas as pd

df = pd.read_excel("icecream_data.xlsx")
label_ice = df['Revenue'].to_numpy()
feature_ice = df['Temperature'].to_numpy().reshape(len(label_ice), 1)

dataset_ice = DataSet(feature_ice, label_ice)
title = dataset_ice.getTitle(is_converted = False)
feature_ice, label_ice = dataset_ice.getFeatureAndLabel()
trainFeatureSet, testFeatureSet, trainLabelSet, testLabelSet = train_test_split(feature_ice, label_ice)

model = RegressionTree(trainFeatureSet, trainLabelSet, title, 10)
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
    