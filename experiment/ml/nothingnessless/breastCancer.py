from decisionTree import DecisionTree
from utils.Data import DataClass, DataSet, DataSpliter
from sklearn.datasets import load_breast_cancer

dataset_breast_cancer = load_breast_cancer()
feature_breast_cancer = dataset_breast_cancer.data
label_breast_cancer = dataset_breast_cancer.target
labelName_breast_cancer = dataset_breast_cancer.target_names
title_breast_cancer = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]
dataset_breast_cancer = DataSet(feature_breast_cancer, label_breast_cancer)
feature_breast_cancer, label_breast_cancer = dataset_breast_cancer.getFeatureAndLabel()
trainFeatureSet, trainLabelSet, validFeatureSet, validLabelSet, testFeatureSet, testLabelSet = DataSpliter.train_valid_testSetSplit_baredata(feature_breast_cancer, label_breast_cancer, trainRatio = 0.6, validRatio = 0.2)

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
