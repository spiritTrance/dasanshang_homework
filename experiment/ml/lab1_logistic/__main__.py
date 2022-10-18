'''
代码在src的上级目录，在命令行输入：
    python -m lab1_logistic
即可运行
'''

from lab1_logistic.logistic import Logistic
from lab1_logistic.utils.Data import DataClass, DataSet, DataSpliter
import numpy as np
from sklearn.datasets import load_iris
import logging
from sklearn.model_selection import train_test_split

if __name__ == "__main__":
    logging.disable(logging.WARNING)    # 禁用 DataSet 定义的 Logging
    
    # 西瓜数据集
    ITER_NUM = 2000
    feature=[["青绿","蜷缩","浊响","清晰","凹陷","硬滑",0.697,0.46],
            ["乌黑","蜷缩","沉闷","清晰","凹陷","硬滑",0.774,0.376],
            ["乌黑","蜷缩","浊响","清晰","凹陷","硬滑",0.634,0.264],
            ["青绿","蜷缩","沉闷","清晰","凹陷","硬滑",0.608,0.318],
            ["浅白","蜷缩","浊响","清晰","凹陷","硬滑",0.556,0.215],
            ["青绿","稍蜷","浊响","清晰","稍凹","软粘",0.403,0.237],
            ["乌黑","稍蜷","浊响","稍糊","稍凹","软粘",0.481,0.149],
            ["乌黑","稍蜷","浊响","清晰","稍凹","硬滑",0.437,0.211],
            ["乌黑","稍蜷","沉闷","稍糊","稍凹","硬滑",0.666,0.091],
            ["青绿","硬挺","清脆","清晰","平坦","软粘",0.243,0.267],
            ["浅白","硬挺","清脆","模糊","平坦","硬滑",0.245,0.057],
            ["浅白","蜷缩","浊响","模糊","平坦","软粘",0.343,0.099],
            ["青绿","稍蜷","浊响","稍糊","凹陷","硬滑",0.639,0.161],
            ["浅白","稍蜷","沉闷","稍糊","凹陷","硬滑",0.657,0.198],
            ["乌黑","稍蜷","浊响","清晰","稍凹","软粘",0.36,0.37],
            ["浅白","蜷缩","浊响","模糊","平坦","硬滑",0.593,0.042],
            ["青绿","蜷缩","沉闷","稍糊","稍凹","硬滑",0.719,0.103]]
    label=[1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0]
    feature_title=["色泽","根蒂","敲声","纹理","脐部","触感","密度","含糖率"]
    
    feature = np.array(feature, dtype=object)
    label = np.array(label, dtype=object)
    dataset_watermelon = DataSet(feature,label,feature_title,labelConvert=False)
    feature_watermelon, label_watermelon = dataset_watermelon.getFeatureAndLabel(is_converted = True)
    title_watermelon = dataset_watermelon.getTitle(is_converted=True)
    attrNum = len(title_watermelon)
    model_watermelon = Logistic(feature_watermelon, label_watermelon)
    model_watermelon.optimize(lr = 0.3, iter_num = ITER_NUM, method="gd")
    acc = model_watermelon.eval(feature_watermelon, label_watermelon)
    print("西瓜数据集上的训练轮数为：{:d}，分类正确率为：{:.2%}".format(ITER_NUM, acc))
    
    # 鸢尾花数据集
    ITER_NUM = 1000
    dataset_iris = load_iris()
    feature_iris = dataset_iris.data
    label_iris = dataset_iris.target
    labelName_iris = dataset_iris.target_names
    title_iris = ["sepal length in cm", "sepal width in cm", "petal length in cm", "petal width in cm"]
    dataset_iris = DataSet(feature_iris, label_iris, title_iris)
    feature_iris, label_iris = dataset_iris.getFeatureAndLabel()
    trainFeatureSet, testFeatureSet, trainLabelSet, testLabelSet = train_test_split(feature_iris, label_iris, train_size = 0.66, random_state = 0)
    # trainFeatureSet, trainLabelSet, testFeatureSet, testLabelSet = DataSpliter.trainAndTestSetSpliter_bareData(feature_iris, label_iris, is_shuffle = True, trainRatio = 0.7)
    mapping_0 = {0:1, 1:0, 2:0} # 0 作为正例
    mapping_1 = {0:0, 1:1, 2:0} # 1 作为正例
    mapping_2 = {0:0, 1:0, 2:1} # 2 作为正例
    label_iris_0 = np.zeros((len(trainLabelSet), 1))
    label_iris_1 = np.zeros((len(trainLabelSet), 1))
    label_iris_2 = np.zeros((len(trainLabelSet), 1))
    for idx, val in enumerate(trainLabelSet):
        val = val[0]
        label_iris_0[idx] = mapping_0[val]
        label_iris_1[idx] = mapping_1[val]
        label_iris_2[idx] = mapping_2[val]
    # OvR多分类策略
    model_iris_0 = Logistic(trainFeatureSet, label_iris_0)
    model_iris_1 = Logistic(trainFeatureSet, label_iris_1)
    model_iris_2 = Logistic(trainFeatureSet, label_iris_2)
    # 模型训练
    OvR_LR = 0.005
    model_iris_0.optimize(iter_num = ITER_NUM, lr = OvR_LR)
    model_iris_1.optimize(iter_num = ITER_NUM, lr = OvR_LR)
    model_iris_2.optimize(iter_num = ITER_NUM, lr = OvR_LR)
    # 获取训练集准确率
    acc_0 = model_iris_0.eval(trainFeatureSet, label_iris_0)
    acc_1 = model_iris_1.eval(trainFeatureSet, label_iris_1)
    acc_2 = model_iris_2.eval(trainFeatureSet, label_iris_2)
    acc_search = [(acc_0, 0), (acc_1, 1), (acc_2, 2)]
    acc_search.sort(key = lambda x: x[0], reverse = True)   # 按照准确率从大到小排列，后续扫描从准确率大的开始比对
    # 开始进行预测
    acc = 0
    tot = len(testLabelSet)
    for X, y in zip(testFeatureSet, testLabelSet):
        pred_0 = model_iris_0.pred(X)
        pred_1 = model_iris_1.pred(X)
        pred_2 = model_iris_2.pred(X)
        pred = [pred_0, pred_1, pred_2]
        for _ , l in acc_search:
            if pred[l] == 1:
                if l == y:
                    acc += 1
                break
    print("鸢尾花数据集上的训练轮数为：{:d}，训练集上的分类正确率为：{:.2%}".format(ITER_NUM, acc / tot))