from decisionTree import DecisionTree
from utils.Data import DataClass, DataSet, DataSpliter
from sklearn.datasets import load_iris, load_wine

dataset_iris = load_iris()
feature_iris = dataset_iris.data
label_iris = dataset_iris.target
labelName_iris = dataset_iris.target_names
title_iris = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]
dataset_iris = DataSet(feature_iris, label_iris)
feature_iris, label_iris = dataset_iris.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, validFeatureSet, validLabelSet, testFeatureSet, testLabelSet = DataSpliter.train_valid_testSetSplit_baredata(feature_iris, label_iris, trainRatio = 0.4, validRatio = 0.3)
# trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_iris, label_iris, trainRatio = 0.5)

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
