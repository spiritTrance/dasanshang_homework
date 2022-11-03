'''
决策树算法要求输入和输出都是连续值
'''
import numpy as np

class ClassifyTreeNodeData:
    def __init__(self, feature: np.array, label: np.array, title):
        sampleNum = len(label)
        self.__data = feature
        self.__label = label.reshape(label)
        self.__title = title
        self.__sampleNum, self.__attrNum = feature.data.shape
        
    def getFeature(self):
        return self.__data.copy()
    
    def getLabel(self):
        return self.__label.copy()
    
    def getTitle(self):
        return self.__title
    
    def __bestSplit(self, attridx):
        arr = self.__data[:, attridx].copy()
        tem = arr.copy().sort()
        label = self.__label()
        splitPts = [(tem[i] + tem[i+1]) / 2 for i in range(len(tem) - 1)]
        minMSE = 1e108
        bestPts = 0
        for pts in splitPts:
            lessArr = label[arr <= pts]
            greaterArr = label[arr > pts]
            f = np.var(lessArr) * len(lessArr) + np.var(greaterArr) * len(greaterArr)
            if f < minMSE:
                minMSE = f
                bestPts = pts
        return bestPts, minMSE
            
    def __getBestMSEsplit(self):
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
    
    def split(self):
        bestPts, attrIdx, minMSE = self.__getBestMSEsplit()
        arr = self.__data[:, attrIdx]
        attrSubIdx = [i for i in range(self.__attrNum)].remove(attrIdx)
        data_less = self.__data[arr <= bestPts, attrSubIdx]
        data_greater = self.__data[arr > bestPts, attrSubIdx]
        attrName = self.__title[attrIdx]
        return [data_less.copy(), data_greater.copy()], [attrName+"<="+str(bestPts), attrName+">"+str(bestPts)], attrName, bestPts

class ClassifyTreeNode:
    def __init__(self, data: ClassifyTreeNodeData, height = 0, cmFeature = None, diFeature = None, son = []):
        self.__son = son
        self.__commonFeature = cmFeature     # 该结点下所有节点共有的特征
        self.__divFeature = diFeature    # 子节点分类依据
        self.__data = data          # data格式是{<属性>:[列表]}，且所有列表下标相同的，同属于一个样本
        self.__output = None         # 叶子节点才有的结果
        self.__height = height
        self.__splitPts = None

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
        dataList, criteriaList, attrName, self.__splitPts= self.__data.split()
        self.__divFeature = attrName
        lessSon = ClassifyTreeNode(dataList[0], height = self.__height + 1, cmFeature = criteriaList[0])
        greaterSon = ClassifyTreeNode(dataList[1], height = self.__height + 1, cmFeature = criteriaList[1])
        self.__son = [lessSon, greaterSon]
    
    def setResult(self):
        if self.isLeaf() is True:
            self.__output = np.mean(self.__data.getLabel())
    
    def getResult(self, feature):
        if self.isLeaf() == True:
            return self.__output
        return None
    
    def getSplitPt(self):
        return self.__splitPts
    
    def getDivFeature(self):
        return self.__divFeature
    
class ClassifyTree:
    def __init__(self, data: np.ndarray, label: np.ndarray, title: list, maxDepth = 65536):
        rootNodeData = ClassifyTreeNodeData(data, label, title)
        self.__root = ClassifyTreeNode(data = rootNodeData)
        self.__maxDepth = maxDepth
        
    def __build(self, node: ClassifyTreeNode):    
        if node.getHeight() > self.__maxDepth:
            node.setResult()
            return
        node.split()
        for son in node.getSon():
            self.__build(son)
            
    def build(self):
        self.__build(self.__root)
        
    def pred(self, feature: np.array, titleList: list):
        p = self.__root()
        while p.isLeaf() == False:
            title = p.getDivFeature()
            pts = p.getSplitPts()
            idx = titleList.index(title)
            x = feature[idx]
            p = p.getSon()[0] if x <= pts else p.getSon()[1]
        return p.getResult()