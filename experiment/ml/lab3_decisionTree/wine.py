from decisionTree import DecisionTree
from utils.Data import DataClass, DataSet, DataSpliter
from sklearn.datasets import load_wine

dataset_wine = load_wine()
feature_wine = dataset_wine.data
label_wine = dataset_wine.target
labelName_wine = dataset_wine.target_names
title_wine = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]
dataset_wine = DataSet(feature_wine, label_wine)
feature_wine, label_wine = dataset_wine.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, validFeatureSet, validLabelSet, testFeatureSet, testLabelSet = DataSpliter.train_valid_testSetSplit_baredata(feature_wine, label_wine, trainRatio = 0.6, validRatio = 0.2)

model = DecisionTree(trainFeatureSet, trainLabelSet, validFeatureSet, validLabelSet)
model.buildTree(pre_prun = False, criteria = "gini")
model.post_prun()

# model.printTree()
print(model.getTrainAccAndValidAcc())

tot = len(testLabelSet)
acc = 0
for X, y in zip(testFeatureSet, testLabelSet):
    y_hat = model.pred(X)
    if y == y_hat:
        acc += 1
print(acc / tot)
