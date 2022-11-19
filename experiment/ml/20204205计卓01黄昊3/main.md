# 导入必要的库


```python
from decisionTree import DecisionTree
from regressionTree import RegressionTree
from utils.Data import DataClass, DataSet, DataSpliter
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import logging
logging.disable(logging.WARNING)    # 禁用 DataSet 定义的 Logging
```


```python
def printResult(s: str, acc, accStd, opt):
    print("[{:s}] 数据集的结果为：".format(s))
    if opt == 0:
        print("\t自行编写的分类决策树在测试集上的准确率为：{:.4%}".format(acc))
        print("\tsklearn的分类决策树在测试集上的准确率为：{:.4%}".format(accStd))
    else:
        print("\t自行编写的回归决策树在测试集上的r-square为：{:.4f}".format(acc))
        print("\tsklearn的回归决策树在测试集上的r-square为：{:.4f}".format(accStd))
```

# Wine数据集（分类）


```python
dataset_wine = load_wine()
feature_wine = dataset_wine.data
label_wine = dataset_wine.target
labelName_wine = dataset_wine.target_names
dataset_wine = DataSet(feature_wine, label_wine)
feature_wine, label_wine = dataset_wine.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_wine, label_wine, trainRatio = 0.8)
# 实验手写的模型
model = DecisionTree(trainFeatureSet, trainLabelSet, trainFeatureSet, trainLabelSet)
model.buildTree(pre_prun = False, criteria = "gini")
model.post_prun()

tot = len(testLabelSet)
acc = 0
for X, y in zip(testFeatureSet, testLabelSet):
    y_hat = model.pred(X)
    if y == y_hat:
        acc += 1
accRate_experiement = acc / tot

# sklearn库的模型
model = DecisionTreeClassifier(criterion = "gini")
model.fit(trainFeatureSet, trainLabelSet)
# 评估
tot = len(testLabelSet)
acc = 0
y_hat = model.predict(testFeatureSet)
idx = (y_hat == testLabelSet)
acc = len(testLabelSet[idx])
accRate_std = acc / tot

printResult("红酒", accRate_experiement, accRate_std, opt = 0)
```

    [红酒] 数据集的结果为：
    	自行编写的分类决策树在测试集上的准确率为：86.4865%
    	sklearn的分类决策树在测试集上的准确率为：81.0811%
    

# Breast_Cancer数据集（分类）


```python
dataset_breast_cancer = load_breast_cancer()
feature_breast_cancer = dataset_breast_cancer.data
label_breast_cancer = dataset_breast_cancer.target
labelName_breast_cancer = dataset_breast_cancer.target_names
title_breast_cancer = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]
dataset_breast_cancer = DataSet(feature_breast_cancer, label_breast_cancer)
feature_breast_cancer, label_breast_cancer = dataset_breast_cancer.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_breast_cancer, label_breast_cancer, trainRatio = 0.8)
# 训练模型
model = DecisionTree(trainFeatureSet, trainLabelSet, trainFeatureSet, trainLabelSet)
model.buildTree(pre_prun = False, criteria = "gini")
model.post_prun()
# 评估
tot = len(testLabelSet)
acc = 0
for X, y in zip(testFeatureSet, testLabelSet):
    y_hat = model.pred(X)
    if y == y_hat:
        acc += 1
accRate_experiement = acc / tot

# sklearn库的模型
model = DecisionTreeClassifier(criterion = "gini")
model.fit(trainFeatureSet, trainLabelSet)
# 评估
tot = len(testLabelSet)
acc = 0
y_hat = model.predict(testFeatureSet)
idx = (y_hat == testLabelSet)
acc = len(testLabelSet[idx])
accRate_std = acc / tot

printResult("癌症", accRate_experiement, accRate_std, opt = 0)
```

    [癌症] 数据集的结果为：
    	自行编写的分类决策树在测试集上的准确率为：93.0435%
    	sklearn的分类决策树在测试集上的准确率为：90.4348%
    

# 波士顿房价预测（回归）


```python
df = pd.read_csv("boston_housing_data.csv")
df_num = df.to_numpy()
idx = ~np.isnan(df_num).any(axis = 1)
df_num = df_num[idx]
feature_boston = df_num[:, :-1]
label_boston = df_num[:, -1]
label_boston = label_boston.reshape(len(label_boston))

dataset_boston = DataSet(feature_boston, label_boston)
title = dataset_boston.getTitle(is_converted = False)
feature_boston, label_boston = dataset_boston.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_boston, label_boston, trainRatio = 0.7)
# 训练自建模型
model = RegressionTree(trainFeatureSet, trainLabelSet, title, 13)
model.build()
R_ex = (model.getRSquare(testFeatureSet, testLabelSet, title))
# sklearn库模型
model2 = DecisionTreeRegressor()
model2.fit(trainFeatureSet, trainLabelSet)
# 评估模型
X = testFeatureSet
Y = testLabelSet
y_mean = np.mean(Y)
fenzi, fenmu = 0, 0
for x, y in zip(X, Y):
    y_pred = model2.predict(x.reshape(1, -1))
    fenzi += (y_pred - y) ** 2
    fenmu += (y - y_mean) ** 2
R_std = (float(1 - fenzi / fenmu))

printResult("波士顿", R_ex, R_std, opt = 1)
```

    [波士顿] 数据集的结果为：
    	自行编写的回归决策树在测试集上的r-square为：0.5875
    	sklearn的回归决策树在测试集上的r-square为：0.5321
    

# 冰激凌数据集（回归）


```python
df = pd.read_csv("icecream_data.csv")
label_ice = df['Revenue'].to_numpy()
feature_ice = df['Temperature'].to_numpy().reshape(len(label_ice), 1)

dataset_ice = DataSet(feature_ice, label_ice)
title = dataset_ice.getTitle(is_converted = False)
feature_ice, label_ice = dataset_ice.getFeatureAndLabel()
trainFeatureSet, testFeatureSet, trainLabelSet, testLabelSet = train_test_split(feature_ice, label_ice)
# 训练自建模型
model = RegressionTree(trainFeatureSet, trainLabelSet, title, 10)
model.build()
# 评估自建模型
R_ex = (model.getRSquare(testFeatureSet, testLabelSet, title))
# sklearn库的模型
model2 = DecisionTreeRegressor()
model2.fit(trainFeatureSet, trainLabelSet)
# 评估模型
X = testFeatureSet
Y = testLabelSet
y_mean = np.mean(Y)
fenzi, fenmu = 0, 0
for x, y in zip(X, Y):
    y_pred = model2.predict(x.reshape(1, -1))
    fenzi += (y_pred - y) ** 2
    fenmu += (y - y_mean) ** 2
R_std = (float(1 - fenzi / fenmu))
printResult("冰激凌", R_ex, R_std, opt = 1)
```

    [冰激凌] 数据集的结果为：
    	自行编写的回归决策树在测试集上的r-square为：0.9631
    	sklearn的回归决策树在测试集上的r-square为：0.9602
    
