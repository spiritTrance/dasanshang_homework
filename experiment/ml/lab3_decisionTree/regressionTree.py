'''
决策树算法要求输入和输出都是连续值
'''
import numpy as np

class RegressionTreeNodeData:               # 每个节点的data进行定义
    def __init__(self, feature: np.array, label: np.array, title):
        sampleNum = len(label)
        self.__data = feature
        self.__label = label.reshape(sampleNum)
        self.__title = title
        self.__sampleNum, self.__attrNum = feature.data.shape
        
    def getFeature(self):                   # getter
        return self.__data.copy()
    
    def getLabel(self):
        return self.__label.copy()
    
    def getTitle(self):
        return self.__title
    
    def getSize(self):
        return len(self.__label)
    
    def __bestSplit(self, attridx):         # 对于指定的属性，返回最佳切分点和最小均方误差
        arr = self.__data[:, attridx].copy()
        tem = arr.copy()
        tem.sort()
        label = self.__label
        splitPts = [(tem[i] + tem[i+1]) / 2 for i in range(len(tem) - 1)]
        minMSE = 1e108
        bestPts = 0
        for pts in splitPts:
            lessArr = label[arr <= pts]
            greaterArr = label[arr > pts]
            if len(lessArr) == 0:
                a = 0
            else:
                a = np.var(lessArr) * len(lessArr)
            if len(greaterArr) == 0:
                b = 0
            else:
                b = np.var(greaterArr) * len(greaterArr)
            f = a + b
            if f < minMSE:
                minMSE = f
                bestPts = pts
        return bestPts, minMSE
            
    def __getBestMSEsplit(self):            # 对于整个数据，按照最小二乘准则找到最佳切分点，返回最佳切分点，对应的属性下标和对应的均方误差
        attrIdx = 0
        minMSE = 1e108
        bestPts = 0
        for idx, attr in enumerate(self.__title):
            pts, mse = self.__bestSplit(idx)
            if mse < minMSE:
                minMSE = mse
                attrIdx = idx
                bestPts = pts
        return bestPts, attrIdx, minMSE
    
    def split(self):                        # 对于数据进行切分，但保留原有下标
        bestPts, attrIdx, minMSE = self.__getBestMSEsplit()
        arr = self.__data[:, attrIdx]
        data_less = self.__data[arr <= bestPts]
        data_greater = self.__data[arr > bestPts]
        label_less = self.__label[arr <= bestPts]
        label_greater = self.__label[arr > bestPts]
        data_l = RegressionTreeNodeData(data_less, label_less, self.__title)
        data_r = RegressionTreeNodeData(data_greater, label_greater, self.__title)
        attrName = self.__title[attrIdx]
        return [data_l, data_r], [attrName+"<="+str(bestPts), attrName+">"+str(bestPts)], attrName, bestPts

class RegressionTreeNode:
    def __init__(self, data: RegressionTreeNodeData, height = 0, cmFeature = None, diFeature = None, son = []):
        self.__son = son
        self.__commonFeature = cmFeature     # 该结点下所有节点共有的特征
        self.__divFeature = diFeature    # 子节点分类依据
        self.__data = data          
        self.__output = None         # 叶子节点才有的结果
        self.__height = height
        self.__splitPts = None      # 分割点位置

    def isLeaf(self):
        return len(self.__son) == 0 
    
    def setSon(self, son: list):
        self.__son = son
        
    def getSon(self):
        return self.__son
        
    def setCommomFeature(self, featureName: str):
        self.__commonFeature = featureName
        
    def setDivFeature(self, divFeature: str):
        self.__divFeature = divFeature
        
    def setData(self, data: dict):
        self.__data = data
        
    def getHeight(self):
        return self.__height
        
    def split(self):
        dataList, criteriaList, attrName, self.__splitPts = self.__data.split()
        self.__divFeature = attrName
        lessSon = RegressionTreeNode(dataList[0], height = self.__height + 1, cmFeature = criteriaList[0])
        if dataList[0].getSize() == 0:
            lessSon = None
        greaterSon = RegressionTreeNode(dataList[1], height = self.__height + 1, cmFeature = criteriaList[1])
        if dataList[1].getSize() == 1:
            greaterSon = None
        self.__son = [lessSon, greaterSon]
        if (lessSon is None) and (greaterSon is None):
            self.__son = []
    
    def setResult(self):
        if len(self.__data.getLabel()) == 0:
            self.__output = 0
        else:
            self.__output = np.mean(self.__data.getLabel())
    
    def getResult(self):
        return self.__output
    
    def getSplitPt(self):
        return self.__splitPts
    
    def getDivFeature(self):
        return self.__divFeature
    
class RegressionTree:
    def __init__(self, data: np.ndarray, label: np.ndarray, title: list, maxDepth = 65536):
        self.__rootNodeData = RegressionTreeNodeData(data, label, title)
        self.__root = RegressionTreeNode(data = self.__rootNodeData)
        self.__maxDepth = maxDepth
        
    def __build(self, node: RegressionTreeNode):    
        if node.getHeight() > self.__maxDepth:
            node.setResult()
            return
        node.split()
        node.setResult()
        for son in node.getSon():
            if not son is None:
                self.__build(son)
            
    def build(self):
        self.__build(self.__root)
        
    def pred(self, feature: np.array, titleList: list):
        p = self.__root
        while p.isLeaf() == False:
            title = p.getDivFeature()
            pts = p.getSplitPt()
            idx = titleList.index(title)
            val = feature[idx]
            if p.getSon()[0] is None:
                p = p.getSon()[1]
            elif p.getSon()[1] is None:
                p = p.getSon()[0]
            else:
                p = p.getSon()[0] if val <= pts else p.getSon()[1]
        return p.getResult()
    
    def getRSquare(self, feature: np.array, label: np.array, titleList: list):   # 越接近于1效果越好
        X = feature
        Y = label
        y_mean = np.mean(Y)
        fenzi, fenmu = 0, 0
        for x, y in zip(X, Y):
            y_pred = self.pred(x, titleList)
            fenzi += (y_pred - y) ** 2
            fenmu += (y - y_mean) ** 2
        return 1 - fenzi / fenmu
    
