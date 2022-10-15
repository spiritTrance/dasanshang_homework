'''
考虑到后面实验都要进行非常麻烦的数据预处理，原则上又不允许调库，所以需要实现一个DataSet类用于数据预处理。
'''
import numpy as np
from enum import Enum

class DataClass(Enum):  # 枚举类，定义数据类型
    value = 1   # 数值数据
    order = 2   # 定序数据
    tag = 3     # 分类数据

class DataSet(object):
    def __init__(self, feature: np.ndarray, label: np.ndarray, title: list, dataClassList: list = None):
        self.__feature = feature
        self.__label = label.reshape((len(label),1))
        self.__title = title
        self.__sample_num = len(label)
        self.__isConverted = False
        self.__convertedFeature = None
        self.__convertedTitle = None
        if dataClassList is None:
            self.__dataClassList = []
            sample = feature[0]
            for i in sample:
                if type(i) == type(1):
                    self.__dataClassList.append(DataClass.order)
                elif type(i) == type(1.0):
                    self.__dataClassList.append(DataClass.value)
                else:
                    self.__dataClassList.append(DataClass.tag)
        else:
            self.__dataClassList = dataClassList
    
    def __createTempOrderMappingList(self):
        mapping = dict()
        for idx, dataType in enumerate(self.__dataClassList):
            if dataType != DataClass.order:
                continue
            s = set()
            for attrVal in self.__feature[:,idx]:
                s.add(attrVal)
            subMapping = dict()
            for orderVal, attrName in enumerate(s):
                subMapping[attrName] = orderVal
            attr = self.__title[idx]
            mapping[attr] = subMapping
        return mapping
                
    def convertFeature(self, orderMappingDict: dict = None):     # mappingList是字典的字典，外层字典的键为属性值，内层字典的键为属性取值，值为定序的大小。要求传入定序类数据的映射
        if orderMappingDict is None:
            orderMappingDict = self.__createTempOrderMappingList()
        # TODO: finish it!
    
    def getFeature(self, isConverted = False):
        if isConverted == False:
            return self.__feature
        elif self.__isConverted == False:
            self.convertFeature()
        return self.__convertedFeature
            
    def getLabel(self):
        return self.__label
    
    def getTitle(self, isConverted = False):
        if isConverted == False:
            return self.__title
        elif self.__isConverted == False:
            self.convertFeature()
        return self.__convertedTitle
    
    def getSampleNum(self):
        return self.__sample_num
    
    def shuffleSample(self, is_converted = False):
        pass
    
    def getDataIterWithBatch(self, batchsize = 1, is_shuffle = True, is_converted = True):
        return zip(self.__feature,self.__label)
    # 组装的时候，第一维是批次数，第二维是样本索引，注意了
    
    def getDataIterWithoutBatch(self, is_shuffle = True, is_converted = True):
        pass
    # 组装的时候，第一维就是样本索引，注意了
        