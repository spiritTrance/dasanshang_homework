from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import load_iris
from utils.Data import DataClass, DataSet, DataSpliter

dataset_iris = load_iris()
feature_iris = dataset_iris.data
label_iris = dataset_iris.target

trainFeatureSet, trainLabelSet, validFeatureSet, validLabelSet, testFeatureSet, testLabelSet = DataSpliter.train_valid_testSetSplit_baredata(feature_iris, label_iris, trainRatio = 0.6, validRatio = 0.2)

model = DecisionTreeClassifier(criterion = "entropy")
model.fit(trainFeatureSet, trainLabelSet)

tot = len(testLabelSet)
acc = 0
y_hat = model.predict(testFeatureSet)
print(y_hat)
for a,b in zip(y_hat, testLabelSet):
    print(a, b)
    if a == b:
        acc += 1
print(acc / tot)